import boto3
import datetime

# Initialize AWS clients
ec2_client = boto3.client('ec2')
cloudwatch_client = boto3.client('cloudwatch')
sns_client = boto3.client('sns')
rds_client = boto3.client('rds')
s3_client = boto3.client('s3')

# SNS Topic ARN (replace with your ARN)
SNS_TOPIC_ARN = 'arn:aws:sns:ca-central-1:058264270488:InstanceResizingNotifications'

# Thresholds
CPU_THRESHOLD = 10  # CPU usage threshold (%)
IOPS_THRESHOLD = 10  # EBS read/write operations threshold
DAYS = 31  # Time range in days for monitoring

def get_idle_ec2_instances():
    """Identify EC2 instances with low CPU utilization."""
    idle_instances = []
    instances = ec2_client.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            metrics = cloudwatch_client.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=datetime.datetime.utcnow() - datetime.timedelta(days=DAYS),
                EndTime=datetime.datetime.utcnow(),
                Period=86400,
                Statistics=['Average']
            )
            if metrics['Datapoints']:
                avg_cpu = metrics['Datapoints'][0]['Average']
                if avg_cpu < CPU_THRESHOLD:
                    idle_instances.append(instance_id)
    return idle_instances

def get_unused_ebs_volumes():
    """Identify unused EBS volumes."""
    unused_volumes = []
    volumes = ec2_client.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])

    for volume in volumes['Volumes']:
        volume_id = volume['VolumeId']
        unused_volumes.append(volume_id)

    return unused_volumes

def get_idle_rds_instances():
    """Identify RDS instances with low CPU utilization."""
    idle_rds_instances = []
    instances = rds_client.describe_db_instances()

    for instance in instances['DBInstances']:
        db_instance_id = instance['DBInstanceIdentifier']
        metrics = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/RDS',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_instance_id}],
            StartTime=datetime.datetime.utcnow() - datetime.timedelta(days=DAYS),
            EndTime=datetime.datetime.utcnow(),
            Period=86400,
            Statistics=['Average']
        )
        if metrics['Datapoints']:
            avg_cpu = metrics['Datapoints'][0]['Average']
            if avg_cpu < CPU_THRESHOLD:
                idle_rds_instances.append(db_instance_id)
    return idle_rds_instances

def get_idle_s3_buckets():
    """Identify S3 buckets with no recent GET/PUT activity."""
    idle_buckets = []
    buckets = s3_client.list_buckets()

    for bucket in buckets['Buckets']:
        bucket_name = bucket['Name']
        metrics = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/S3',
            MetricName='NumberOfObjects',
            Dimensions=[{'Name': 'BucketName', 'Value': bucket_name}, {'Name': 'StorageType', 'Value': 'AllStorageTypes'}],
            StartTime=datetime.datetime.utcnow() - datetime.timedelta(days=DAYS),
            EndTime=datetime.datetime.utcnow(),
            Period=86400,
            Statistics=['Sum']
        )
        if not metrics['Datapoints']:  # No data means no activity
            idle_buckets.append(bucket_name)

    return idle_buckets

def notify_smes(idle_resources):
    """Send SNS notification with idle resources."""
    if idle_resources:
        message = "The following resources have been idle or underutilized for over 30 days. Please delete if no longer needed:\n\n"
        for resource_type, resources in idle_resources.items():
            if resources:
                message += f"{resource_type}:\n" + "\n".join(resources) + "\n\n"
        
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject='Idle AWS Resources Notification',
            Message=message
        )

def lambda_handler(event, context):
    # Get idle resources
    idle_ec2_instances = get_idle_ec2_instances()
    unused_ebs_volumes = get_unused_ebs_volumes()
    idle_rds_instances = get_idle_rds_instances()
    idle_s3_buckets = get_idle_s3_buckets()

    # Consolidate results
    idle_resources = {
        'EC2 Instances': idle_ec2_instances,
        'EBS Volumes': unused_ebs_volumes,
        'RDS Instances': idle_rds_instances,
        'S3 Buckets': idle_s3_buckets
    }

    # Notify SMEs
    notify_smes(idle_resources)

    # Log unused resources (returned for debugging or chaining)
    print("Idle Resources Found:")
    for resource_type, resources in idle_resources.items():
        print(f"{resource_type}: {resources}")
    
    return {
        'statusCode': 200,
        'body': idle_resources
    }
