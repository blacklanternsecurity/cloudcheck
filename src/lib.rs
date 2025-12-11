use radixtarget::{RadixTarget, ScopeMode};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

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

pub struct CloudCheck {
    radix: RadixTarget,
    providers: HashMap<String, Vec<CloudProvider>>,
}

impl CloudCheck {
    pub fn new() -> Result<Self, Box<dyn std::error::Error>> {
        let json_data = include_str!("../cloud_providers_v2.json");
        let providers_data: HashMap<String, ProviderData> = serde_json::from_str(json_data)?;

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

        Ok(CloudCheck {
            radix,
            providers: providers_map,
        })
    }

    pub fn lookup(&self, target: &str) -> Vec<CloudProvider> {
        if let Some(normalized) = self.radix.get(target) {
            self.providers.get(&normalized).cloned().unwrap_or_default()
        } else {
            Vec::new()
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lookup_google_dns() {
        let cloudcheck = CloudCheck::new().unwrap();
        let results = cloudcheck.lookup("8.8.8.8");
        let names: Vec<String> = results.iter().map(|p| p.name.clone()).collect();
        assert!(
            names.contains(&"Google".to_string()),
            "Expected Google in results: {:?}",
            names
        );
    }

    #[test]
    fn test_lookup_amazon_domain() {
        let cloudcheck = CloudCheck::new().unwrap();
        let results = cloudcheck.lookup("asdf.amazon.com");
        let names: Vec<String> = results.iter().map(|p| p.name.clone()).collect();
        assert!(
            names.contains(&"Amazon".to_string()),
            "Expected Amazon in results: {:?}",
            names
        );
    }
}
