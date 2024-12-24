# Cost Optimization: Idle Resources Notification

## Introduction

Cost optimization is a critical strategy in cloud service management that DevOps Engineers, Cloud Architects, and other cloud specialists should adopt. It involves tracking unused resources, over-provisioned services, or unsuitable configurations for specific use cases. Mastering cost optimization not only reduces expenses but also improves resource efficiency and operational performance.

## Purpose
This project leverages CloudWatch and Lambda to periodically scan all resources in AWS account (In this case, RDS, EBS, S3, EC2) to determine non-utilization or underutilization and then use AWS SNS to notify SMEs, advising them to remove the resources if they are no longer needed.

![image](https://github.com/user-attachments/assets/ffc1760c-4803-46ed-8c66-2ceb80cc9e9c)


## Project Scope

- Set up an EventBridge Scheduler to trigger the Lambda function.
- Implement the core logic using a Python Lambda function with Boto3.
- Scan for under utilized resources.
- Configure an SNS topic to notify SMEs to remove resources.
