use cloudcheck::CloudCheck;

#[tokio::main]
async fn main() {
    env_logger::init();
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 2 {
        eprintln!("Usage: cloudcheck <domain_or_ip>");
        std::process::exit(1);
    }

    let target = &args[1];
    let cloudcheck = CloudCheck::new();
    match cloudcheck.lookup(target).await {
        Ok(results) => {
            let json = serde_json::to_string_pretty(&results).unwrap();
            println!("{}", json);
        }
        Err(e) => {
            eprintln!("Error: {}", e);
            std::process::exit(1);
        }
    }
}
