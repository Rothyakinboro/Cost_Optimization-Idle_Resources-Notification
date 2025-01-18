variable "function_name" {
  description = "A unique name for your Lambda Function"
  type        = string
  default     = ""
}

variable "region" {
  description = "Region to provision resources"
  default     = ""
}

variable "sns-name" {
  description = "SNS Topic name, to be used for notification"
  type        = string
  default     = "test-prj"
}

variable "tags" {
  description = "Tags for project identification and environment"
  type        = map(string)

  default = {
    Project     = "Idle-Resources-Notification"
    Environment = ""
  }
}

variable "sns-subscriptions" {
  description = "Email address to subscribe to SNS topic"
  type        = string
  default     = ""
}

variable "eventbridge-name" {
  description = "EventBridge name"
  type        = string
  default     = ""
}