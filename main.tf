# This block calls an AWS official Lambda_function module. 
module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.20.0"

  function_name = var.function_name
  description   = "A lambda function that fetches idle resources and notifies subscribers"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.12"

  source_path = "./src/lambda_function.py"
  timeout     = 30

  # This block creates an IAM policy for the lambda function to use SNS, S3, EC2, RDS, and CloudWatch services.
  attach_policy_statements = true
  policy_statements = {
    ssm = {
      effect = "Allow"
      actions = [
        "s3:*",
        "s3:ListBucket",
        "ec2:DescribeInstances",
        "sns:Publish",
        "ec2:DescribeVolumes",
        "rds:DescribeDBInstances",
        "cloudwatch:GetMetricData",
        "cloudwatch:ListMetrics",
        "cloudwatch:DescribeAlarms",
        "cloudwatch:GetMetricStatistics"
      ]
      resources = ["*"]
    }
  }
  environment_variables = {
    topic_arn = module.sns_topic.topic_arn
  }

  tags = var.tags
}

# Module block for SNS topic, which is used to send notifications to subscribers
module "sns_topic" {
  source  = "terraform-aws-modules/sns/aws"
  version = "6.1.2"

  name = var.sns-name

  subscriptions = {
    email = {
      protocol = "email"
      endpoint = var.sns-subscriptions
    }
  }

  tags = var.tags
}

#Module for EventBridge rule to trigger the Lambda function every day
module "eventbridge" {
  source  = "terraform-aws-modules/eventbridge/aws"
  version = "3.14.2"

  create_bus = false

  rules = {
    crons = {
      description         = "Trigger the lambda function every day"
      schedule_expression = "rate(1 day)"
    }
  }

  targets = {
    crons = [
      {
        arn  = module.lambda_function.lambda_function_arn
        name = "crons-lambda"
      }
    ]
  }
}

#Provider block for AWS
provider "aws" {
  region = var.region
}