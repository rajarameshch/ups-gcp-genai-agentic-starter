variable "project_id" {
  type        = string
  description = "GCP project id"
}

variable "region" {
  type        = string
  description = "Default region"
  default     = "us-central1"
}

variable "artifact_repo" {
  type        = string
  description = "Artifact Registry repo name"
  default     = "ups-genai"
}

variable "env" {
  type        = string
  description = "Environment name (dev/stage/prod)"
  default     = "dev"
}

variable "api_gateway_image" {
  type        = string
  description = "Container image for api-gateway"
  default     = "us-docker.pkg.dev/PROJECT/ups-genai/api-gateway:latest"
}

variable "agent_service_image" {
  type        = string
  description = "Container image for agent-service"
  default     = "us-docker.pkg.dev/PROJECT/ups-genai/agent-service:latest"
}

variable "retrieval_service_image" {
  type        = string
  description = "Container image for retrieval-service"
  default     = "us-docker.pkg.dev/PROJECT/ups-genai/retrieval-service:latest"
}
