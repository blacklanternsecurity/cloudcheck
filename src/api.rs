use axum::Router;
use axum::response::Redirect;
use cloudcheck::CloudCheck;
use std::sync::Arc;
use tokio::net::TcpListener;
use utoipa::OpenApi;
use utoipa_swagger_ui::SwaggerUi;

#[derive(OpenApi)]
#[openapi(
    paths(lookup),
    components(schemas(cloudcheck::CloudProvider)),
    tags(
        (name = "cloudcheck", description = "Cloud provider lookup API")
    )
)]
struct ApiDoc;

async fn root() -> Redirect {
    Redirect::permanent("/swagger-ui")
}

#[utoipa::path(
    get,
    path = "/lookup/{target}",
    tag = "cloudcheck",
    params(
        ("target" = String, Path, description = "Domain or IP address to lookup")
    ),
    responses(
        (status = 200, description = "Lookup results", body = Vec<cloudcheck::CloudProvider>)
    )
)]
async fn lookup(
    axum::extract::Path(target): axum::extract::Path<String>,
    axum::extract::State(cloudcheck): axum::extract::State<Arc<CloudCheck>>,
) -> Result<axum::Json<Vec<cloudcheck::CloudProvider>>, axum::http::StatusCode> {
    log::info!("API lookup request for: {}", target);
    match cloudcheck.lookup(&target).await {
        Ok(providers) => {
            log::info!("Lookup succeeded, returning {} providers", providers.len());
            Ok(axum::Json(providers))
        }
        Err(e) => {
            log::error!("Lookup failed: {}", e);
            Err(axum::http::StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

pub async fn serve(
    host: String,
    port: u16,
) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let cloudcheck = Arc::new(CloudCheck::new());
    let app = Router::new()
        .route("/", axum::routing::get(root))
        .route("/lookup/{target}", axum::routing::get(lookup))
        .merge(SwaggerUi::new("/swagger-ui").url("/api-docs/openapi.json", ApiDoc::openapi()))
        .with_state(cloudcheck);

    let addr = format!("{}:{}", host, port);
    let listener = TcpListener::bind(&addr).await?;

    println!("Server listening on http://{}", addr);
    println!("Swagger UI available at http://{}/swagger-ui", addr);
    println!(
        "OpenAPI spec available at http://{}/api-docs/openapi.json",
        addr
    );

    axum::serve(listener, app)
        .with_graceful_shutdown(async {
            tokio::signal::ctrl_c()
                .await
                .expect("failed to install Ctrl+C handler");
        })
        .await?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    async fn start_test_server() -> String {
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let addr = listener.local_addr().unwrap();
        let port = addr.port();

        let cloudcheck = Arc::new(CloudCheck::new());
        let app = Router::new()
            .route("/", axum::routing::get(root))
            .route("/lookup/{target}", axum::routing::get(lookup))
            .merge(SwaggerUi::new("/swagger-ui").url("/api-docs/openapi.json", ApiDoc::openapi()))
            .with_state(cloudcheck);

        tokio::spawn(async move {
            axum::serve(listener, app).await.unwrap();
        });

        // Give the server a moment to start
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;

        format!("http://127.0.0.1:{}", port)
    }

    #[tokio::test]
    async fn test_lookup_endpoint() {
        let base_url = start_test_server().await;
        let url = format!("{}/lookup/8.8.8.8", base_url);

        let client = reqwest::Client::new();
        let response = client.get(&url).send().await.unwrap();

        assert!(response.status().is_success());

        let json: serde_json::Value = response.json().await.unwrap();

        // Verify response is an array
        let providers = json.as_array().unwrap();
        let names: Vec<String> = providers
            .iter()
            .filter_map(|p| p.get("name").and_then(|n| n.as_str()))
            .map(|s| s.to_string())
            .collect();

        assert!(
            names.contains(&"Google".to_string()),
            "Expected Google in response: {}",
            json
        );
    }
}
