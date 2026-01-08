mod api;

use clap::{Parser, Subcommand};
use cloudcheck::CloudCheck;

#[derive(Parser)]
#[command(name = "cloudcheck")]
#[command(about = "CloudCheck - Check if an IP address or hostname belongs to a cloud provider")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Lookup a domain or IP address
    Lookup {
        /// The domain or IP address to lookup
        target: String,
    },
    /// Start the API server
    Serve {
        /// Host to bind to
        #[arg(long, default_value = "127.0.0.1")]
        host: String,
        /// Port to bind to
        #[arg(long, default_value = "8080")]
        port: u16,
    },
}

#[tokio::main]
async fn main() {
    env_logger::init();
    let cli = Cli::parse();

    match cli.command {
        Commands::Lookup { target } => {
            let cloudcheck = CloudCheck::new();
            match cloudcheck.lookup(&target).await {
                Ok(results) => {
                    let json = serde_json::to_string(&results).unwrap();
                    println!("{}", json);
                }
                Err(e) => {
                    eprintln!("Error: {}", e);
                    std::process::exit(1);
                }
            }
        }
        Commands::Serve { host, port } => {
            if let Err(e) = api::serve(host, port).await {
                eprintln!("Server error: {}", e);
                std::process::exit(1);
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use std::process::Command;

    #[test]
    fn test_lookup_command_output() {
        let bin_path = std::env::var("CARGO_BIN_EXE_cloudcheck").unwrap_or_else(|_| {
            let mut path = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR"));
            path.push("target");
            path.push("debug");
            path.push("cloudcheck");
            let bin_path = path.to_string_lossy().to_string();

            if !std::path::Path::new(&bin_path).exists() {
                let status = Command::new("cargo")
                    .args(["build", "--bin", "cloudcheck"])
                    .status()
                    .expect("Failed to run cargo build");
                assert!(status.success(), "Failed to build cloudcheck binary");
            }

            bin_path
        });
        let mut cmd = Command::new(bin_path);
        cmd.args(["lookup", "8.8.8.8"]);
        let output = cmd.output().expect("Failed to execute cloudcheck command");

        assert!(output.status.success());

        let stdout = String::from_utf8(output.stdout).unwrap();

        // Verify output is valid JSON
        let parsed: Vec<serde_json::Value> = serde_json::from_str(&stdout).unwrap();

        // Verify it contains expected provider
        let names: Vec<String> = parsed
            .iter()
            .filter_map(|v| v.get("name").and_then(|n| n.as_str()))
            .map(|s| s.to_string())
            .collect();
        assert!(
            names.contains(&"Google".to_string()),
            "Expected Google in output JSON: {}",
            stdout
        );
    }
}
