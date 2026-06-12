variable "aws_region" {
  description = "AWS region for the project."
  type        = string
  default     = "eu-central-1"
}

variable "data_lake_bucket_name" {
  description = "Globally unique S3 bucket name for the train delay data lake."
  type        = string
}

variable "glue_database_name" {
  description = "Glue Data Catalog database name."
  type        = string
  default     = "db_train_delay"
}

variable "athena_workgroup_name" {
  description = "Athena workgroup name."
  type        = string
  default     = "db-train-delay"
}

