use cloudcheck::CloudCheck;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 2 {
        eprintln!("Usage: cloudcheck <domain_or_ip>");
        std::process::exit(1);
    }

    let target = &args[1];
    let cloudcheck = match CloudCheck::new() {
        Ok(cc) => cc,
        Err(e) => {
            eprintln!("Error initializing CloudCheck: {}", e);
            std::process::exit(1);
        }
    };

    let results = cloudcheck.lookup(target);
    let json = serde_json::to_string_pretty(&results).unwrap();
    println!("{}", json);
}
