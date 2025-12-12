use radixtarget::{RadixTarget, ScopeMode};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::Arc;
use std::time::{Duration, SystemTime};
use tokio::sync::OnceCell;

#[cfg(feature = "pyo3")]
mod python;

const CLOUDCHECK_SIGNATURE_URL: &str = "https://raw.githubusercontent.com/blacklanternsecurity/cloudcheck/refs/heads/cloudcheck-v8/cloud_providers_v2.json";

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

#[derive(Clone)]
pub struct CloudCheck {
    radix: Arc<OnceCell<RadixTarget>>,
    providers: Arc<OnceCell<HashMap<String, Vec<CloudProvider>>>>,
}

impl Default for CloudCheck {
    fn default() -> Self {
        Self::new()
    }
}

impl CloudCheck {
    pub fn new() -> Self {
        CloudCheck {
            radix: Arc::new(OnceCell::new()),
            providers: Arc::new(OnceCell::new()),
        }
    }

    fn get_signature_url() -> String {
        std::env::var("CLOUDCHECK_SIGNATURE_URL")
            .unwrap_or_else(|_| CLOUDCHECK_SIGNATURE_URL.to_string())
    }

    fn get_cache_path() -> Result<PathBuf, Box<dyn std::error::Error + Send + Sync>> {
        let home = std::env::var("HOME")?;
        let mut path = PathBuf::from(home);
        path.push(".cache");
        path.push("cloudcheck");
        path.push("cloud_providers_v2.json");
        Ok(path)
    }

    async fn fetch_and_cache(
        cache_path: &PathBuf,
    ) -> Result<String, Box<dyn std::error::Error + Send + Sync>> {
        let url = Self::get_signature_url();
        let response = reqwest::get(&url).await?;
        let json_data = response.text().await?;

        if let Some(parent) = cache_path.parent() {
            tokio::fs::create_dir_all(parent).await?;
        }
        tokio::fs::write(cache_path, &json_data).await?;

        Ok(json_data)
    }

    async fn ensure_loaded(&self) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
        let radix_cell = Arc::clone(&self.radix);
        let providers_cell = Arc::clone(&self.providers);

        radix_cell
            .get_or_try_init(|| async {
                let cache_path = Self::get_cache_path()?;
                let cache_valid_duration = Duration::from_secs(24 * 60 * 60);

                let json_data = match tokio::fs::metadata(&cache_path).await {
                    Ok(metadata) => {
                        let modified = metadata.modified()?;
                        let now = SystemTime::now();

                        if let Ok(elapsed) = now.duration_since(modified) {
                            if elapsed < cache_valid_duration {
                                tokio::fs::read_to_string(&cache_path).await?
                            } else {
                                Self::fetch_and_cache(&cache_path).await?
                            }
                        } else {
                            Self::fetch_and_cache(&cache_path).await?
                        }
                    }
                    Err(_) => Self::fetch_and_cache(&cache_path).await?,
                };

                let providers_data: HashMap<String, ProviderData> =
                    serde_json::from_str(&json_data)?;

                let mut radix = RadixTarget::new(&[], ScopeMode::Normal);
                let mut providers_map: HashMap<String, Vec<CloudProvider>> = HashMap::new();

                for (_, provider) in providers_data {
                    let cloud_provider = CloudProvider {
                        name: provider.name.clone(),
                        tags: provider.tags.clone(),
                    };

                    for cidr in provider.cidrs {
                        let normalized = match radix.get(&cidr) {
                            Some(n) => n,
                            None => radix.insert(&cidr).unwrap(),
                        };
                        providers_map
                            .entry(normalized.clone())
                            .or_default()
                            .push(cloud_provider.clone());
                    }

                    for domain in provider.domains {
                        let normalized = match radix.get(&domain) {
                            Some(n) => n,
                            None => radix.insert(&domain).unwrap(),
                        };
                        providers_map
                            .entry(normalized.clone())
                            .or_default()
                            .push(cloud_provider.clone());
                    }
                }

                providers_cell
                    .set(providers_map)
                    .map_err(|_| "Failed to set providers")?;

                Ok::<RadixTarget, Box<dyn std::error::Error + Send + Sync>>(radix)
            })
            .await?;

        Ok(())
    }

    pub async fn lookup(
        &self,
        target: &str,
    ) -> Result<Vec<CloudProvider>, Box<dyn std::error::Error + Send + Sync>> {
        self.ensure_loaded().await?;

        let radix = self.radix.get().unwrap();
        let providers = self.providers.get().unwrap();

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

