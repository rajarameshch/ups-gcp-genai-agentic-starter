locals {
  name_prefix = "ups-genai-${var.env}"
}

# Enable required APIs
resource "google_project_service" "services" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
    "pubsub.googleapis.com",
    "bigquery.googleapis.com",
    "aiplatform.googleapis.com",
    "cloudbuild.googleapis.com",
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com",
  ])
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

# Service account for Cloud Run
resource "google_service_account" "runtime" {
  account_id   = "${local.name_prefix}-sa"
  display_name = "UPS GenAI runtime service account"
  depends_on   = [google_project_service.services]
}

# Minimal roles (adjust per enterprise policy)
resource "google_project_iam_member" "runtime_roles" {
  for_each = toset([
    "roles/aiplatform.user",
    "roles/secretmanager.secretAccessor",
    "roles/storage.objectAdmin",
    "roles/pubsub.publisher",
    "roles/pubsub.subscriber",
    "roles/bigquery.dataEditor",
  ])
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.runtime.email}"
}

resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = var.artifact_repo
  format        = "DOCKER"
  depends_on    = [google_project_service.services]
}

resource "google_storage_bucket" "docs" {
  name                        = "${var.project_id}-${local.name_prefix}-docs"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true
  depends_on                  = [google_project_service.services]
}

resource "google_pubsub_topic" "events" {
  name       = "${local.name_prefix}-events"
  depends_on = [google_project_service.services]
}

resource "google_secret_manager_secret" "ups_api_key" {
  secret_id = "${local.name_prefix}-ups-api-key"
  replication { auto {} }
  depends_on = [google_project_service.services]
}

resource "google_bigquery_dataset" "ops" {
  dataset_id                 = replace("${local.name_prefix}_ops", "-", "_")
  location                   = var.region
  delete_contents_on_destroy = true
  depends_on                 = [google_project_service.services]
}

# Cloud Run services (placeholders)
resource "google_cloud_run_v2_service" "api_gateway" {
  name     = "${local.name_prefix}-api-gateway"
  location = var.region
  template {
    service_account = google_service_account.runtime.email
    containers {
      image = var.api_gateway_image
      env {
        name  = "AGENT_SERVICE_URL"
        value = "http://${google_cloud_run_v2_service.agent_service.uri}"
      }
      env {
        name  = "RETRIEVAL_SERVICE_URL"
        value = "http://${google_cloud_run_v2_service.retrieval_service.uri}"
      }
    }
  }
  depends_on = [google_project_service.services]
}

resource "google_cloud_run_v2_service" "agent_service" {
  name     = "${local.name_prefix}-agent-service"
  location = var.region
  template {
    service_account = google_service_account.runtime.email
    containers {
      image = var.agent_service_image
      env { name = "GOOGLE_CLOUD_PROJECT"  value = var.project_id }
      env { name = "GOOGLE_CLOUD_LOCATION" value = var.region }
    }
  }
  depends_on = [google_project_service.services]
}

resource "google_cloud_run_v2_service" "retrieval_service" {
  name     = "${local.name_prefix}-retrieval-service"
  location = var.region
  template {
    service_account = google_service_account.runtime.email
    containers {
      image = var.retrieval_service_image
    }
  }
  depends_on = [google_project_service.services]
}

# Allow unauthenticated for api-gateway only (lock down for enterprise/IAP)
resource "google_cloud_run_v2_service_iam_member" "api_public" {
  name     = google_cloud_run_v2_service.api_gateway.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}
