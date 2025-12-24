output "api_gateway_url" {
  value = google_cloud_run_v2_service.api_gateway.uri
}

output "agent_service_url" {
  value = google_cloud_run_v2_service.agent_service.uri
}

output "retrieval_service_url" {
  value = google_cloud_run_v2_service.retrieval_service.uri
}

output "docs_bucket" {
  value = google_storage_bucket.docs.name
}
