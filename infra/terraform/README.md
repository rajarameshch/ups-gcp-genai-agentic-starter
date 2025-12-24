# Terraform

This module provisions baseline resources for the UPS GenAI starter:
- Required APIs
- Service account + minimal roles
- Artifact Registry repository
- Cloud Storage bucket
- Pub/Sub topic
- Secret Manager secrets
- BigQuery dataset
- Cloud Run services (placeholders)

Edit `terraform.tfvars` then apply.

> For production: split into modules per domain (networking, security, runtime, data).
