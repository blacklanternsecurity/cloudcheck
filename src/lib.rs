use radixtarget::{RadixTarget, ScopeMode};
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::Arc;
use std::time::{Duration, SystemTime};
use tokio::sync::{Mutex, OnceCell};

#[cfg(feature = "py")]
mod python;

const CLOUDCHECK_SIGNATURE_URL: &str = "https://raw.githubusercontent.com/blacklanternsecurity/cloudcheck/refs/heads/stable/cloud_providers_v2.json";

type RegexPatternsMap = HashMap<String, HashMap<String, Vec<String>>>;
type RegexPatterns = Arc<OnceCell<RegexPatternsMap>>;

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
    #[serde(default)]
    regexes: HashMap<String, Vec<String>>,
}

#[derive(Clone)]
pub struct CloudCheck {
    radix: Arc<OnceCell<RadixTarget>>,
    providers: Arc<OnceCell<HashMap<String, Vec<CloudProvider>>>>,
    regex_patterns: RegexPatterns,
    regex_cache: Arc<Mutex<HashMap<String, Vec<Regex>>>>,
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
            regex_patterns: Arc::new(OnceCell::new()),
            regex_cache: Arc::new(Mutex::new(HashMap::new())),
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
        let regex_patterns_cell = Arc::clone(&self.regex_patterns);

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

                let mut radix = RadixTarget::new(&[], ScopeMode::Normal)?;
                let mut providers_map: HashMap<String, Vec<CloudProvider>> = HashMap::new();
                let mut regex_patterns_map: RegexPatternsMap = HashMap::new();

                for (_, provider) in providers_data {
                    let cloud_provider = CloudProvider {
                        name: provider.name.clone(),
                        tags: provider.tags.clone(),
                    };

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

                    for domain in provider.domains {
                        // Clean domain: strip comments (everything after #) and trim whitespace
                        let cleaned_domain = domain.split('#').next().unwrap_or(&domain).trim();

                        if cleaned_domain.is_empty() {
                            continue;
                        }

                        let normalized = match radix.get(cleaned_domain) {
                            Some(n) => n,
                            None => match radix.insert(cleaned_domain) {
                                Ok(Some(n)) => n,
                                Ok(None) => continue,
                                Err(e) => {
                                    eprintln!("Error inserting domain '{}': {}", cleaned_domain, e);
                                    continue;
                                }
                            },
                        };
                        providers_map
                            .entry(normalized.clone())
                            .or_default()
                            .push(cloud_provider.clone());
                    }

                    // Store regex patterns per provider
                    if !provider.regexes.is_empty() {
                        regex_patterns_map.insert(provider.name.clone(), provider.regexes);
                    }
                }

                providers_cell
                    .set(providers_map)
                    .map_err(|_| "Failed to set providers")?;

                regex_patterns_cell
                    .set(regex_patterns_map)
                    .map_err(|_| "Failed to set regex patterns")?;

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

    pub async fn regex_match(
        &self,
        provider_name: &str,
        regex_name: &str,
        text: &str,
    ) -> Result<bool, Box<dyn std::error::Error + Send + Sync>> {
        self.ensure_loaded().await?;

        let regex_patterns = self.regex_patterns.get().unwrap();
        let provider_regexes = match regex_patterns.get(provider_name) {
            Some(regexes) => regexes,
            None => return Err(format!("Provider '{}' not found", provider_name).into()),
        };

        let patterns = match provider_regexes.get(regex_name) {
            Some(patterns) => patterns,
            None => {
                return Err(format!(
                    "Regex '{}' not found for provider '{}'",
                    regex_name, provider_name
                )
                .into());
            }
        };

        let cache_key = format!("{}:{}", provider_name, regex_name);
        let mut cache = self.regex_cache.lock().await;

        // Check if we already have compiled regexes for this provider:regex_name combination
        if !cache.contains_key(&cache_key) {
            // Compile all patterns for this regex name
            let mut compiled = Vec::new();
            for pattern in patterns {
                match Regex::new(pattern) {
                    Ok(re) => compiled.push(re),
                    Err(e) => {
                        eprintln!(
                            "Error compiling regex pattern '{}' for provider '{}' regex '{}': {}",
                            pattern, provider_name, regex_name, e
                        );
                        continue;
                    }
                }
            }
            cache.insert(cache_key.clone(), compiled);
        }

        // Check if any regex matches the entire string
        if let Some(compiled_regexes) = cache.get(&cache_key) {
            for re in compiled_regexes {
                if let Some(mat) = re.find(text) {
                    // Check if the match spans the entire string
                    if mat.start() == 0 && mat.end() == text.len() {
                        return Ok(true);
                    }
                }
            }
        }

        Ok(false)
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
    async fn test_regex_match_amazon_valid() {
        let cloudcheck = CloudCheck::new();
        // Test valid bucket name that matches Amazon's STORAGE_BUCKET_NAME pattern
        let result = cloudcheck
            .regex_match("Amazon", "STORAGE_BUCKET_NAME", "my-bucket-123")
            .await
            .unwrap();
        assert!(
            result,
            "Expected 'my-bucket-123' to match Amazon STORAGE_BUCKET_NAME"
        );
    }

    #[tokio::test]
    async fn test_regex_match_amazon_invalid() {
        let cloudcheck = CloudCheck::new();
        // Test invalid bucket name (too short and contains invalid characters)
        let result = cloudcheck
            .regex_match("Amazon", "STORAGE_BUCKET_NAME", "AB")
            .await
            .unwrap();
        assert!(
            !result,
            "Expected 'AB' to not match Amazon STORAGE_BUCKET_NAME"
        );
    }

    #[tokio::test]
    async fn test_regex_match_nonexistent_provider() {
        let cloudcheck = CloudCheck::new();
        // Test with a provider that doesn't exist
        let result = cloudcheck
            .regex_match("NonExistentProvider", "STORAGE_BUCKET_NAME", "my-bucket")
            .await;
        assert!(result.is_err(), "Expected error for non-existent provider");
        assert!(
            result
                .unwrap_err()
                .to_string()
                .contains("Provider 'NonExistentProvider' not found")
        );
    }

    #[tokio::test]
    async fn test_regex_match_nonexistent_regex() {
        let cloudcheck = CloudCheck::new();
        // Test with a real provider but non-existent regex name
        let result = cloudcheck
            .regex_match("Amazon", "NON_EXISTENT_REGEX", "my-bucket")
            .await;
        assert!(
            result.is_err(),
            "Expected error for non-existent regex name on real provider"
        );
        assert!(
            result
                .unwrap_err()
                .to_string()
                .contains("Regex 'NON_EXISTENT_REGEX' not found for provider 'Amazon'")
        );
    }
}
