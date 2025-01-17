output "lambda_function_arn" {
  description = "The ARN of the Lambda Function"
  value       = module.lambda_function.lambda_function_arn
}

output "sns_topic" {
  description = "The SNS topic ARN"
  value       = module.sns_topic.subscriptions
}