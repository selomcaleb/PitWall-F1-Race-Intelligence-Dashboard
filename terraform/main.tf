terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project     = var.project_id
  region      = var.region
  credentials = file(var.credentials_file)
}

# Raw data lake bucket
resource "google_storage_bucket" "raw_data" {
  name          = var.bucket_name
  location      = "EU"
  force_destroy = false

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
}

# Raw dataset
resource "google_bigquery_dataset" "raw" {
  dataset_id  = var.raw_dataset
  location    = var.bq_location
  description = "Raw F1 data ingested from FastF1 — unmodified source data"
}

# Mart dataset (dbt target)
resource "google_bigquery_dataset" "mart" {
  dataset_id  = var.mart_dataset
  location    = var.bq_location
  description = "dbt target dataset — staging and mart models build here"
}
