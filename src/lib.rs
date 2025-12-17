use radixtarget::{RadixTarget, ScopeMode};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::Arc;
use std::time::{Duration, SystemTime};
use tokio::sync::{Mutex, RwLock};

#[cfg(feature = "py")]
mod python;

const CLOUDCHECK_SIGNATURE_URL: &str = "https://raw.githubusercontent.com/blacklanternsecurity/cloudcheck/refs/heads/stable/cloud_providers_v2.json";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CloudProvider {
    pub name: String,
    pub tags: Vec<String>,
}

#[derive(Debug, Deserialize)]
struct ProviderData {
    name: String,
    tags: Vec<String>,
    cidrs: Vec<String>,
    domains: Vec<String>,
}

type ProvidersMap = HashMap<String, Vec<CloudProvider>>;
type Error = Box<dyn std::error::Error + Send + Sync>;

#[derive(Clone)]
pub struct CloudCheck {
    radix: Arc<RwLock<Option<RadixTarget>>>,
    providers: Arc<RwLock<Option<ProvidersMap>>>,
    last_fetch: Arc<Mutex<Option<SystemTime>>>,
}

impl Default for CloudCheck {
    fn default() -> Self {
        Self::new()
    }
}

impl CloudCheck {
    pub fn new() -> Self {
        CloudCheck {
            radix: Arc::new(RwLock::new(None)),
            providers: Arc::new(RwLock::new(None)),
            last_fetch: Arc::new(Mutex::new(None)),
        }
    }

    fn get_signature_url() -> String {
        std::env::var("CLOUDCHECK_SIGNATURE_URL")
            .unwrap_or_else(|_| CLOUDCHECK_SIGNATURE_URL.to_string())
    }

    fn get_cache_path() -> Result<PathBuf, Error> {
        let home = std::env::var("HOME")?;
        let mut path = PathBuf::from(home);
        path.push(".cache");
        path.push("cloudcheck");
        path.push("cloud_providers_v2.json");
        Ok(path)
    }

    async fn fetch_and_cache(
        cache_path: &PathBuf,
    ) -> Result<String, Error> {
        let url = Self::get_signature_url();
        let response = reqwest::get(&url).await?;
        let json_data = response.text().await?;

        if let Some(parent) = cache_path.parent() {
            tokio::fs::create_dir_all(parent).await?;
        }
        tokio::fs::write(cache_path, &json_data).await?;

        Ok(json_data)
    }

    /// Gets the last fetch time, checking in-memory timestamp first.
    /// If no in-memory timestamp exists (first run), falls back to checking
    /// the cache file's modification time. Returns None if file doesn't exist.
    async fn get_last_fetch_time(
        &self,
        cache_path: &PathBuf,
    ) -> Result<Option<SystemTime>, Error> {
        let last_fetch = self.last_fetch.lock().await;
        match *last_fetch {
            Some(time) => Ok(Some(time)),
            None => {
                // No in-memory timestamp - check file modification time
                drop(last_fetch);
                match tokio::fs::metadata(cache_path).await {
                    Ok(metadata) => Ok(metadata.modified().ok()),
                    Err(_) => Ok(None),
                }
            }
        }
    }

    /// Loads JSON data either from network (if refresh needed) or from cache file.
    /// Returns (json_data, fetched_fresh) where fetched_fresh indicates if we
    /// fetched from network. Sets last_fetch timestamp on first cache load to
    /// track process runtime. Falls back to network fetch if cache read fails.
    async fn load_json_data(
        &self,
        cache_path: &PathBuf,
        needs_refresh: bool,
    ) -> Result<(String, bool), Error> {
        if needs_refresh {
            let data = Self::fetch_and_cache(cache_path).await?;
            Ok((data, true))
        } else {
            match tokio::fs::read_to_string(cache_path).await {
                Ok(data) => {
                    // First load from cache - set timestamp to track process runtime
                    let now = SystemTime::now();
                    let mut last_fetch = self.last_fetch.lock().await;
                    if last_fetch.is_none() {
                        *last_fetch = Some(now);
                    }
                    Ok((data, false))
                }
                Err(_) => {
                    // Cache file was deleted between stat and read, fetch fresh
                    let data = Self::fetch_and_cache(cache_path).await?;
                    Ok((data, true))
                }
            }
        }
    }

    /// Parses JSON and builds the radix tree and providers map.
    /// For each provider, inserts all CIDRs and domains into the radix tree,
    /// normalizing them in the process. Maps normalized values to provider lists.
    fn build_data_structures(
        json_data: &str,
    ) -> Result<(RadixTarget, ProvidersMap), Error> {
        let providers_data: HashMap<String, ProviderData> = serde_json::from_str(json_data)?;

        let mut radix = RadixTarget::new(&[], ScopeMode::Normal)?;
        let mut providers_map: ProvidersMap = HashMap::new();

        for (_, provider) in providers_data {
            let cloud_provider = CloudProvider {
                name: provider.name.clone(),
                tags: provider.tags.clone(),
            };

            // Insert all CIDRs for this provider
            for cidr in provider.cidrs {
                let normalized = match radix.get(&cidr) {
                    Some(n) => n,
                    None => match radix.insert(&cidr) {
                        Ok(Some(n)) => n,
                        Ok(None) => continue,
                        Err(e) => {
                            eprintln!("Error inserting CIDR '{}': {}", cidr, e);
                            continue;
                        }
                    },
                };
                providers_map
                    .entry(normalized.clone())
                    .or_default()
                    .push(cloud_provider.clone());
            }

            // Insert all domains for this provider
            for domain in provider.domains {
                let normalized = match radix.get(&domain) {
                    Some(n) => n,
                    None => match radix.insert(&domain) {
                        Ok(Some(n)) => n,
                        Ok(None) => continue,
                        Err(e) => {
                            eprintln!("Error inserting domain '{}': {}", domain, e);
                            continue;
                        }
                    },
                };
                providers_map
                    .entry(normalized.clone())
                    .or_default()
                    .push(cloud_provider.clone());
            }
        }

        Ok((radix, providers_map))
    }

    /// Ensures data is loaded and fresh. Checks if refresh is needed based on
    /// 24-hour process runtime. Returns early if data is already loaded and fresh.
    /// Otherwise loads data (from network or cache), builds structures, and updates
    /// the in-memory timestamp if we fetched fresh data.
    async fn ensure_loaded(&self) -> Result<(), Error> {
        let cache_valid_duration = Duration::from_secs(24 * 60 * 60);
        let now = SystemTime::now();
        let cache_path = Self::get_cache_path()?;

        // Check if we need refresh (uses in-memory timestamp, falls back to file stat)
        let last_fetch_time = self.get_last_fetch_time(&cache_path).await?;
        let needs_refresh = match last_fetch_time {
            Some(fetch_time) => now
                .duration_since(fetch_time)
                .map(|elapsed| elapsed >= cache_valid_duration)
                .unwrap_or(true),
            None => true,
        };

        // Early return if data is already loaded and fresh
        {
            let radix_guard = self.radix.read().await;
            if radix_guard.is_some() && !needs_refresh {
                return Ok(());
            }
        }

        // Load JSON data and build structures
        let (json_data, fetched_fresh) = self.load_json_data(&cache_path, needs_refresh).await?;
        let (radix, providers_map) = Self::build_data_structures(&json_data)?;

        // Update in-memory data structures
        {
            let mut radix_guard = self.radix.write().await;
            *radix_guard = Some(radix);
        }
        {
            let mut providers_guard = self.providers.write().await;
            *providers_guard = Some(providers_map);
        }

        // Update timestamp if we fetched fresh data
        if fetched_fresh {
            let mut last_fetch = self.last_fetch.lock().await;
            *last_fetch = Some(now);
        }

        Ok(())
    }

    pub async fn lookup(
        &self,
        target: &str,
    ) -> Result<Vec<CloudProvider>, Error> {
        self.ensure_loaded().await?;

        let radix_guard = self.radix.read().await;
        let providers_guard = self.providers.read().await;

        let radix = radix_guard.as_ref().unwrap();
        let providers = providers_guard.as_ref().unwrap();

        if let Some(normalized) = radix.get(target) {
            Ok(providers.get(&normalized).cloned().unwrap_or_default())
        } else {
            Ok(Vec::new())
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_lookup_google_dns() {
        let cloudcheck = CloudCheck::new();
        let results = cloudcheck.lookup("8.8.8.8").await.unwrap();
        let names: Vec<String> = results.iter().map(|p| p.name.clone()).collect();
        assert!(
            names.contains(&"Google".to_string()),
            "Expected Google in results: {:?}",
            names
        );
    }

    #[tokio::test]
    async fn test_lookup_amazon_domain() {
        let cloudcheck = CloudCheck::new();
        let results = cloudcheck.lookup("asdf.amazon.com").await.unwrap();
        let names: Vec<String> = results.iter().map(|p| p.name.clone()).collect();
        assert!(
            names.contains(&"Amazon".to_string()),
            "Expected Amazon in results: {:?}",
            names
        );
    }
}
