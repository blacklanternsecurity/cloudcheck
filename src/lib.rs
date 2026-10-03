use log::debug;
use radixtarget::{RadixTarget, ScopeMode};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::error::Error as StdError;
use std::path::PathBuf;
use std::sync::Arc;
use std::time::{Duration, SystemTime};
use tokio::sync::{Mutex, RwLock};

#[cfg(feature = "py")]
mod python;

const CLOUDCHECK_SIGNATURE_URL: &str = "https://raw.githubusercontent.com/blacklanternsecurity/cloudcheck/refs/heads/stable/cloud_providers_v3.json";

#[derive(Debug, Clone, Serialize, Deserialize, utoipa::ToSchema)]
pub struct CloudProvider {
    pub name: String,
    pub tags: Vec<String>,
    #[serde(default)]
    pub short_description: String,
    #[serde(default)]
    pub long_description: String,
}

#[derive(Debug, Deserialize)]
struct ProviderData {
    name: String,
    tags: Vec<String>,
    cidrs: Vec<String>,
    domains: Vec<String>,
    #[serde(default)]
    short_description: String,
    #[serde(default)]
    long_description: String,
}

type ProvidersMap = HashMap<String, Vec<Arc<CloudProvider>>>;
type Error = Box<dyn std::error::Error + Send + Sync>;

#[derive(Clone)]
pub struct CloudCheck {
    radix: Arc<RwLock<Option<RadixTarget>>>,
    providers: Arc<RwLock<Option<ProvidersMap>>>,
    last_fetch: Arc<Mutex<Option<SystemTime>>>,
    signature_url: String,
    max_retries: u32,
    retry_delay_seconds: u64,
    force_refresh: bool,
    verify_ssl: bool,
}

impl Default for CloudCheck {
    fn default() -> Self {
        Self::new()
    }
}

impl CloudCheck {
    pub fn new() -> Self {
        Self::with_config(None, None, None, None, None)
    }

    pub fn with_config(
        signature_url: Option<String>,
        max_retries: Option<u32>,
        retry_delay_seconds: Option<u64>,
        force_refresh: Option<bool>,
        verify_ssl: Option<bool>,
    ) -> Self {
        let url = signature_url
            .or_else(|| std::env::var("CLOUDCHECK_SIGNATURE_URL").ok())
            .unwrap_or_else(|| CLOUDCHECK_SIGNATURE_URL.to_string());

        CloudCheck {
            radix: Arc::new(RwLock::new(None)),
            providers: Arc::new(RwLock::new(None)),
            last_fetch: Arc::new(Mutex::new(None)),
            signature_url: url,
            max_retries: max_retries.unwrap_or(10),
            retry_delay_seconds: retry_delay_seconds.unwrap_or(1),
            force_refresh: force_refresh.unwrap_or(false),
            verify_ssl: verify_ssl.unwrap_or(true),
        }
    }

    fn get_cache_path() -> Result<PathBuf, Error> {
        let home = std::env::var("HOME")?;
        let mut path = PathBuf::from(home);
        path.push(".cache");
        path.push("cloudcheck");
        path.push("cloud_providers_v3.json");
        Ok(path)
    }

    async fn fetch_and_cache(&self, cache_path: &PathBuf) -> Result<String, Error> {
        let url = &self.signature_url;
        let max_retries = self.max_retries;
        let retry_delay_seconds = self.retry_delay_seconds;
        log::info!(
            "Fetching data from URL: {} (max_retries={}, retry_delay={}s, verify_ssl={})",
            url,
            max_retries,
            retry_delay_seconds,
            self.verify_ssl
        );

        if !self.verify_ssl {
            log::warn!(
                "SSL certificate verification is DISABLED for cloud provider signature fetch"
            );
        }
        let client = reqwest::Client::builder()
            .danger_accept_invalid_certs(!self.verify_ssl)
            .build()
            .map_err(|e| Box::new(e) as Error)?;

        let mut last_error = None;

        for attempt in 0..=max_retries {
            log::info!("Fetch attempt {}/{}", attempt + 1, max_retries + 1);
            let result = match client.get(url).send().await {
                Ok(response) => {
                    let status = response.status();
                    log::info!(
                        "HTTP response received, status: {} {}",
                        status.as_u16(),
                        status
                    );
                    if !status.is_success() {
                        let error_msg = format!("HTTP error: {} {}", status.as_u16(), status);
                        log::warn!("{}", error_msg);
                        Err(Box::new(std::io::Error::other(error_msg)) as Error)
                    } else {
                        response.text().await.map_err(|e| {
                            let error_msg = format!("Failed to read response body: {}", e);
                            log::warn!("{}", error_msg);
                            Box::new(std::io::Error::other(error_msg)) as Error
                        })
                    }
                }
                Err(e) => {
                    let error_type = if e.is_timeout() {
                        "timeout"
                    } else if e.is_connect() {
                        "connection"
                    } else if e.is_request() {
                        "request"
                    } else {
                        "unknown"
                    };
                    let mut error_details = format!("{}", e);
                    let mut current_source: Option<&(dyn StdError + 'static)> =
                        StdError::source(&e);
                    while let Some(source) = current_source {
                        error_details = format!("{}: {}", error_details, source);
                        current_source = source.source();
                    }
                    log::warn!(
                        "HTTP request failed ({} error): {}",
                        error_type,
                        error_details
                    );
                    Err(Box::new(e) as Error)
                }
            };

            match result {
                Ok(json_data) => {
                    log::info!("Fetched {} bytes from network", json_data.len());

                    if let Some(parent) = cache_path.parent() {
                        log::debug!("Creating cache directory: {:?}", parent);
                        tokio::fs::create_dir_all(parent).await?;
                    }
                    log::debug!("Writing cache file: {:?}", cache_path);
                    tokio::fs::write(cache_path, &json_data).await?;
                    log::info!("Cache file written successfully");

                    return Ok(json_data);
                }
                Err(e) => {
                    last_error = Some(e);
                    if attempt < max_retries {
                        log::warn!(
                            "Failed to fetch (attempt {}/{}), retrying in {} second(s): {}",
                            attempt + 1,
                            max_retries + 1,
                            retry_delay_seconds,
                            last_error.as_ref().unwrap()
                        );
                        tokio::time::sleep(tokio::time::Duration::from_secs(retry_delay_seconds))
                            .await;
                    } else {
                        log::error!(
                            "Failed to fetch after {} attempts: {}",
                            max_retries + 1,
                            last_error.as_ref().unwrap()
                        );
                    }
                }
            }
        }

        let final_error = last_error.unwrap_or_else(|| {
            Box::new(std::io::Error::other("Failed to fetch data after retries"))
        });

        Err(Box::new(std::io::Error::other(format!(
            "Failed to fetch cloud provider data from {} after {} attempts: {}",
            url,
            max_retries + 1,
            final_error
        ))) as Error)
    }

    /// Gets the last fetch time, checking in-memory timestamp first.
    /// If no in-memory timestamp exists (first run), falls back to checking
    /// the cache file's modification time. Returns None if file doesn't exist.
    async fn get_last_fetch_time(&self, cache_path: &PathBuf) -> Result<Option<SystemTime>, Error> {
        let last_fetch = self.last_fetch.lock().await;
        match *last_fetch {
            Some(time) => {
                debug!("Using in-memory last_fetch timestamp: {:?}", time);
                Ok(Some(time))
            }
            None => {
                // No in-memory timestamp - check file modification time
                drop(last_fetch);
                debug!(
                    "No in-memory timestamp, checking cache file modification time: {:?}",
                    cache_path
                );
                match tokio::fs::metadata(cache_path).await {
                    Ok(metadata) => {
                        if let Ok(modified) = metadata.modified() {
                            debug!("Cache file modification time: {:?}", modified);
                            Ok(Some(modified))
                        } else {
                            debug!("Cache file exists but modification time unavailable");
                            Ok(None)
                        }
                    }
                    Err(_) => {
                        debug!("Cache file does not exist: {:?}", cache_path);
                        Ok(None)
                    }
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
            log::info!("Refresh needed, fetching from network");
            let data = self.fetch_and_cache(cache_path).await?;
            Ok((data, true))
        } else {
            log::info!("No refresh needed, loading from cache: {:?}", cache_path);
            match tokio::fs::read_to_string(cache_path).await {
                Ok(data) => {
                    debug!("Successfully loaded {} bytes from cache", data.len());
                    // First load from cache - set timestamp to track process runtime
                    let now = SystemTime::now();
                    let mut last_fetch = self.last_fetch.lock().await;
                    if last_fetch.is_none() {
                        debug!("Setting in-memory last_fetch timestamp to current time");
                        *last_fetch = Some(now);
                    } else {
                        debug!(
                            "In-memory last_fetch timestamp already set, keeping existing value"
                        );
                    }
                    Ok((data, false))
                }
                Err(e) => {
                    log::warn!(
                        "Failed to read cache file ({}), falling back to network fetch",
                        e
                    );
                    // Cache file was deleted between stat and read, fetch fresh
                    let data = self.fetch_and_cache(cache_path).await?;
                    Ok((data, true))
                }
            }
        }
    }

    /// How "broad" an entry is — lower means it covers more. CIDRs sort by
    /// prefix length, a bare IP counts as a full-length prefix, and domains
    /// sort by label count. IPs and domains live in separate trees, so a
    /// domain's score never has to be meaningful against a CIDR's.
    fn entry_breadth(entry: &str) -> u32 {
        if let Some((addr, prefix)) = entry.split_once('/')
            && addr.parse::<std::net::IpAddr>().is_ok()
            && let Ok(prefix_len) = prefix.parse::<u32>()
        {
            return prefix_len;
        }
        if let Ok(addr) = entry.parse::<std::net::IpAddr>() {
            return if addr.is_ipv6() { 128 } else { 32 };
        }
        entry
            .trim_matches('.')
            .split('.')
            .filter(|label| !label.is_empty())
            .count() as u32
    }

    /// Parses JSON and builds the radix tree and providers map.
    ///
    /// Attribution has to answer "which providers' own entries contain this
    /// target" — ancestors only, never siblings or descendants. The tree is
    /// therefore built in `Normal` mode: `Acl` mode deliberately collapses a
    /// nested entry into whatever already covers it, which is right for an
    /// access list but destroys exactly the association we need. Under `Acl`,
    /// HPE's single `hpefonts.s3.amazonaws.com` bucket ended up filed under
    /// the key `amazonaws.com`, so every `*.amazonaws.com` host came back
    /// tagged HPE.
    ///
    /// Each entry stores the full set of providers that contain it, resolved
    /// once here rather than walked on every lookup. Entries are inserted
    /// broadest first, so when we reach one, every entry containing it is
    /// already present with a finished list and we can inherit it directly.
    fn build_data_structures(json_data: &str) -> Result<(RadixTarget, ProvidersMap), Error> {
        let providers_data: HashMap<String, ProviderData> = serde_json::from_str(json_data)?;

        // One allocation per provider; the map stores cheap handles to these.
        // Two providers claiming the same entry is legitimate (Microsoft and
        // GitHub both declare GitHub's S3 buckets), so entries map to a list.
        let mut owners: HashMap<String, Vec<Arc<CloudProvider>>> = HashMap::new();
        for provider in providers_data.values() {
            let cloud_provider = Arc::new(CloudProvider {
                name: provider.name.clone(),
                tags: provider.tags.clone(),
                short_description: provider.short_description.clone(),
                long_description: provider.long_description.clone(),
            });
            for entry in provider.cidrs.iter().chain(provider.domains.iter()) {
                let entry_owners = owners.entry(entry.clone()).or_default();
                if !entry_owners.iter().any(|p| p.name == cloud_provider.name) {
                    entry_owners.push(Arc::clone(&cloud_provider));
                }
            }
        }

        let mut sorted: Vec<(String, Vec<Arc<CloudProvider>>)> = owners.into_iter().collect();
        sorted.sort_by(|(a, _), (b, _)| {
            Self::entry_breadth(a)
                .cmp(&Self::entry_breadth(b))
                .then_with(|| a.cmp(b))
        });

        let mut radix = RadixTarget::new(&[], ScopeMode::Normal)?;
        let mut providers_map: ProvidersMap = HashMap::new();

        for (entry, entry_owners) in sorted {
            // Nearest already-inserted entry containing this one. Because we
            // go broadest first, its list is complete.
            let inherited: Vec<Arc<CloudProvider>> = radix
                .get(&entry)
                .and_then(|ancestor| providers_map.get(&ancestor).cloned())
                .unwrap_or_default();

            let novel: Vec<Arc<CloudProvider>> = entry_owners
                .iter()
                .filter(|p| !inherited.iter().any(|i| i.name == p.name))
                .cloned()
                .collect();

            // Adds no provider its container doesn't already have. Anything
            // under it resolves to that container and gets the same answer,
            // so keeping the node would only cost memory. This is what stops
            // a provider's own nested subnets from inflating the tree.
            if novel.is_empty() {
                continue;
            }

            let mut merged = inherited;
            merged.extend(novel);

            match radix.insert(&entry) {
                Ok(Some(normalized)) => {
                    providers_map.insert(normalized, merged);
                }
                Ok(None) => continue,
                Err(e) => {
                    log::warn!("Error inserting entry '{}': {}", entry, e);
                    continue;
                }
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
        log::info!("ensure_loaded: checking cache at {:?}", cache_path);

        // Check if we need refresh (uses in-memory timestamp, falls back to file stat)
        let last_fetch_time = self.get_last_fetch_time(&cache_path).await?;
        let needs_refresh = if self.force_refresh {
            debug!("force_refresh is enabled, needs_refresh=true");
            true
        } else {
            match last_fetch_time {
                Some(fetch_time) => {
                    let elapsed = now.duration_since(fetch_time).ok();
                    let needs = elapsed.map(|e| e >= cache_valid_duration).unwrap_or(true);
                    if let Some(e) = elapsed {
                        debug!("Time since last fetch: {:?}, needs_refresh={}", e, needs);
                    } else {
                        debug!("Could not calculate duration since last fetch, needs_refresh=true");
                    }
                    needs
                }
                None => {
                    debug!("No last_fetch_time available, needs_refresh=true");
                    true
                }
            }
        };

        // Early return if data is already loaded and fresh
        {
            let radix_guard = self.radix.read().await;
            if radix_guard.is_some() && !needs_refresh {
                log::info!("Data already loaded and fresh, returning early");
                return Ok(());
            }
            log::info!("Data not loaded or needs refresh, proceeding to load");
        }

        // Load JSON data and build structures
        let (json_data, fetched_fresh) = self.load_json_data(&cache_path, needs_refresh).await?;
        log::info!(
            "Loaded JSON data, fetched_fresh={}, building data structures",
            fetched_fresh
        );
        let (radix, providers_map) =
            tokio::task::spawn_blocking(move || Self::build_data_structures(&json_data)).await??;
        debug!("Built data structures: radix tree and providers map");

        // Update in-memory data structures
        {
            let mut radix_guard = self.radix.write().await;
            *radix_guard = Some(radix);
            debug!("Updated radix tree in memory");
        }
        {
            let mut providers_guard = self.providers.write().await;
            *providers_guard = Some(providers_map);
            debug!("Updated providers map in memory");
        }

        // Update timestamp if we fetched fresh data
        if fetched_fresh {
            let mut last_fetch = self.last_fetch.lock().await;
            *last_fetch = Some(now);
            debug!("Updated in-memory last_fetch timestamp to {:?}", now);
        }

        Ok(())
    }

    pub async fn lookup(&self, target: &str) -> Result<Vec<CloudProvider>, Error> {
        log::info!("lookup called for target: {}", target);
        match self.ensure_loaded().await {
            Ok(()) => log::debug!("ensure_loaded succeeded"),
            Err(e) => {
                log::error!("ensure_loaded failed: {}", e);
                return Err(e);
            }
        }

        let radix_guard = self.radix.read().await;
        let providers_guard = self.providers.read().await;

        let radix = radix_guard.as_ref().unwrap();
        let providers = providers_guard.as_ref().unwrap();

        if let Some(normalized) = radix.get(target) {
            debug!("Found normalized target: {} for {}", normalized, target);
            let result: Vec<CloudProvider> = providers
                .get(&normalized)
                .map(|found| found.iter().map(|p| (**p).clone()).collect())
                .unwrap_or_default();
            debug!("Returning {} providers", result.len());
            Ok(result)
        } else {
            debug!("No match found for target: {}", target);
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

    #[tokio::test]
    async fn test_lookup_with_ssl_verification_disabled() {
        // verify_ssl=false should still succeed against a host with a valid cert
        let cloudcheck = CloudCheck::with_config(None, None, None, Some(true), Some(false));
        let results = cloudcheck.lookup("8.8.8.8").await.unwrap();
        let names: Vec<String> = results.iter().map(|p| p.name.clone()).collect();
        assert!(
            names.contains(&"Google".to_string()),
            "Expected Google in results: {:?}",
            names
        );
    }

    /// Helper: provider names returned for a target.
    async fn names_for(target: &str) -> Vec<String> {
        let cloudcheck = CloudCheck::new();
        let results = cloudcheck.lookup(target).await.unwrap();
        results.iter().map(|p| p.name.clone()).collect()
    }

    /// Microsoft owns `windows.net`. GitHub owns specific storage accounts
    /// beneath it, but not this host, so GitHub must not come back.
    #[tokio::test]
    async fn test_lookup_windows_blob_domain() {
        let names = names_for("asdf.blob.core.windows.net").await;
        assert!(
            names.contains(&"Microsoft".to_string()),
            "Expected Microsoft in results: {:?}",
            names
        );
        assert!(
            !names.contains(&"GitHub".to_string()),
            "GitHub owns sibling hosts under windows.net, not this one: {:?}",
            names
        );
    }

    /// A host GitHub *does* declare returns both the tenant and the
    /// infrastructure owner — legitimate nesting, which must survive.
    #[tokio::test]
    async fn test_lookup_github_owned_blob_host() {
        let names = names_for("copilotprodattachments.blob.core.windows.net").await;
        for expected in ["GitHub", "Microsoft"] {
            assert!(
                names.contains(&expected.to_string()),
                "Expected {} in results: {:?}",
                expected,
                names
            );
        }
    }

    /// Regression: tenants with a single bucket under `amazonaws.com` used to
    /// be filed under the bare domain, so every AWS host came back as theirs.
    #[tokio::test]
    async fn test_lookup_amazonaws_no_tenant_leak() {
        let names = names_for("foo.s3.amazonaws.com").await;
        assert!(
            names.contains(&"Amazon".to_string()),
            "Expected Amazon in results: {:?}",
            names
        );
        for leaked in ["GitHub", "HPE", "Microsoft"] {
            assert!(
                !names.contains(&leaked.to_string()),
                "{} leaked onto an unrelated amazonaws.com host: {:?}",
                leaked,
                names
            );
        }
    }

    /// The tenant's own bucket still returns the tenant alongside Amazon.
    #[tokio::test]
    async fn test_lookup_tenant_bucket_keeps_both() {
        let names = names_for("hpefonts.s3.amazonaws.com").await;
        for expected in ["Amazon", "HPE"] {
            assert!(
                names.contains(&expected.to_string()),
                "Expected {} in results: {:?}",
                expected,
                names
            );
        }
    }

    /// Regression: one QUIC.cloud /32 inside AWS space used to tag the whole
    /// surrounding range as a CDN, which made bbot's portfilter drop every
    /// non-web port across millions of addresses.
    #[tokio::test]
    async fn test_lookup_aws_ip_no_cdn_leak() {
        let names = names_for("18.195.165.195").await;
        assert!(
            names.contains(&"Amazon".to_string()),
            "Expected Amazon in results: {:?}",
            names
        );
        assert!(
            !names.contains(&"Quiccloud".to_string()),
            "Quiccloud leaked onto an unrelated AWS address: {:?}",
            names
        );
    }

    /// Breadth ordering drives the build; IPs and domains are scored
    /// independently because they live in separate trees.
    #[test]
    fn test_entry_breadth_ordering() {
        assert!(CloudCheck::entry_breadth("10.0.0.0/8") < CloudCheck::entry_breadth("10.1.2.0/24"));
        assert_eq!(CloudCheck::entry_breadth("1.2.3.4"), 32);
        assert_eq!(CloudCheck::entry_breadth("::1"), 128);
        assert!(
            CloudCheck::entry_breadth("amazonaws.com")
                < CloudCheck::entry_breadth("foo.s3.amazonaws.com")
        );
        assert_eq!(CloudCheck::entry_breadth("example.com."), 2);
    }

    const NESTED: &str = r#"{
        "bigcloud": {"name": "BigCloud", "tags": ["cloud"], "cidrs": ["10.0.0.0/8"], "domains": ["bigcloud.example"]},
        "tinycdn": {"name": "TinyCdn", "tags": ["cdn"], "cidrs": ["10.1.2.3/32"], "domains": ["node.bigcloud.example"]},
        "elsewhere": {"name": "Elsewhere", "tags": ["cloud"], "cidrs": ["192.0.2.0/24"], "domains": []}
    }"#;

    fn names(target: &str) -> Vec<String> {
        let (radix, providers) = CloudCheck::build_data_structures(NESTED).unwrap();
        let mut names: Vec<String> = radix
            .get(target)
            .and_then(|entry| providers.get(&entry).cloned())
            .unwrap_or_default()
            .iter()
            .map(|p| p.name.clone())
            .collect();
        names.sort();
        names
    }

    #[test]
    fn test_nested_provider_does_not_leak_to_container() {
        assert_eq!(names("10.9.9.9"), ["BigCloud"]);
        assert_eq!(names("10.1.2.4"), ["BigCloud"]);
        assert_eq!(names("www.bigcloud.example"), ["BigCloud"]);
        assert_eq!(names("bigcloud.example"), ["BigCloud"]);
    }

    #[test]
    fn test_nested_provider_matches_its_own_entry_and_ancestors() {
        assert_eq!(names("10.1.2.3"), ["BigCloud", "TinyCdn"]);
        assert_eq!(names("node.bigcloud.example"), ["BigCloud", "TinyCdn"]);
        assert_eq!(names("a.node.bigcloud.example"), ["BigCloud", "TinyCdn"]);
    }

    #[test]
    fn test_unrelated_and_unknown_targets() {
        assert_eq!(names("192.0.2.5"), ["Elsewhere"]);
        assert!(names("203.0.113.1").is_empty());
        assert!(names("unknown.test").is_empty());
    }

    // HashMap iteration order changes per build, so rebuild repeatedly.
    #[test]
    fn test_attribution_is_independent_of_insert_order() {
        for _ in 0..32 {
            assert_eq!(names("10.9.9.9"), ["BigCloud"]);
            assert_eq!(names("10.1.2.3"), ["BigCloud", "TinyCdn"]);
        }
    }
}
