variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "europe-west2"
}

variable "bq_location" {
  description = "BigQuery dataset location"
  type        = string
  default     = "EU"
}

variable "bucket_name" {
  description = "GCS bucket for raw data"
  type        = string
}

variable "raw_dataset" {
  description = "BigQuery raw dataset name"
  type        = string
  default     = "pitwall_raw"
}

variable "mart_dataset" {
  description = "BigQuery mart dataset name"
  type        = string
  default     = "pitwall_mart"
}

variable "credentials_file" {
  description = "Path to service account JSON key"
  type        = string
}