"""
Assignment 5: Auto-Tagging EC2 Instances on Launch Using AWS Lambda and Boto3

This Lambda function automatically tags newly launched EC2 instances with:
- Current launch date
- Custom tags (Owner, Environment, etc.)

This function is triggered by CloudWatch Events (EventBridge) when an EC2 
instance state changes to 'running'.

Author: AWS Lambda Automation Project
Date: January 2026
"""

import boto3
import json
from datetime import datetime, timezone

# Initialize EC2 client
ec2 = boto3.client('ec2')

# Custom tags configuration
CUSTOM_TAGS = {
    'ManagedBy': 'Lambda',
    'AutoTagged': 'True',
    'Environment': 'Development',
    'Project': 'AWS-Serverless-Lambda'
}

def lambda_handler(event, context):
    """
    Main Lambda handler function triggered by EC2 state change events
    
    Args:
        event: CloudWatch Event with EC2 instance details
        context: Lambda context object
        
    Returns:
        dict: Response with statusCode and tagging details
    """
    
    print(f"Lambda function started at {datetime.now(timezone.utc).isoformat()}")
    print(f"Event received: {json.dumps(event)}")
    
    response = {
        'tagged_instances': [],
        'errors': []
    }
    
    try:
        # Extract instance ID from the event
        instance_id = extract_instance_id(event)
        
        if not instance_id:
            error_msg = "No instance ID found in event"
            print(error_msg)
            response['errors'].append(error_msg)
            
            return {
                'statusCode': 400,
                'body': json.dumps(response)
            }
        
        print(f"Processing instance: {instance_id}")
        
        # Get instance details
        instance_details = get_instance_details(instance_id)
        
        # Create tags for the instance
        tags = create_tags(instance_id, instance_details)
        
        response['tagged_instances'].append({
            'instance_id': instance_id,
            'tags_applied': tags,
            'instance_type': instance_details.get('InstanceType'),
            'availability_zone': instance_details.get('AvailabilityZone')
        })
        
        print(f"Successfully tagged instance {instance_id}")
        print(f"Tags applied: {json.dumps(tags)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(response, default=str)
        }
        
    except Exception as e:
        error_msg = f"Error in lambda_handler: {str(e)}"
        print(error_msg)
        response['errors'].append(error_msg)
        
        return {
            'statusCode': 500,
            'body': json.dumps(response)
        }


def extract_instance_id(event):
    """
    Extract instance ID from CloudWatch Event
    
    Args:
        event: CloudWatch Event object
        
    Returns:
        str: Instance ID or None
    """
    try:
        # CloudWatch Event structure for EC2 state change
        if 'detail' in event and 'instance-id' in event['detail']:
            return event['detail']['instance-id']
        
        # Alternative structure
        if 'detail' in event and 'EC2InstanceId' in event['detail']:
            return event['detail']['EC2InstanceId']
        
        # Manual invocation with instance_id parameter
        if 'instance_id' in event:
            return event['instance_id']
        
        return None
        
    except Exception as e:
        print(f"Error extracting instance ID: {str(e)}")
        return None


def get_instance_details(instance_id):
    """
    Get EC2 instance details
    
    Args:
        instance_id: EC2 instance ID
        
    Returns:
        dict: Instance details
    """
    try:
        response = ec2.describe_instances(InstanceIds=[instance_id])
        
        if not response['Reservations']:
            raise Exception(f"Instance {instance_id} not found")
        
        instance = response['Reservations'][0]['Instances'][0]
        
        details = {
            'InstanceId': instance['InstanceId'],
            'InstanceType': instance['InstanceType'],
            'State': instance['State']['Name'],
            'LaunchTime': instance['LaunchTime'],
            'AvailabilityZone': instance['Placement']['AvailabilityZone'],
            'PrivateIpAddress': instance.get('PrivateIpAddress', 'N/A'),
            'PublicIpAddress': instance.get('PublicIpAddress', 'N/A')
        }
        
        print(f"Instance details: {json.dumps(details, default=str)}")
        return details
        
    except Exception as e:
        print(f"Error getting instance details: {str(e)}")
        raise


def create_tags(instance_id, instance_details):
    """
    Create and apply tags to EC2 instance
    
    Args:
        instance_id: EC2 instance ID
        instance_details: Dictionary with instance information
        
    Returns:
        list: List of applied tags
    """
    try:
        # Get current date
        current_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        current_datetime = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Build tags list
        tags = [
            {
                'Key': 'LaunchDate',
                'Value': current_date
            },
            {
                'Key': 'LaunchDateTime',
                'Value': current_datetime
            }
        ]
        
        # Add custom tags
        for key, value in CUSTOM_TAGS.items():
            tags.append({
                'Key': key,
                'Value': value
            })
        
        # Add instance type tag
        tags.append({
            'Key': 'InstanceType',
            'Value': instance_details.get('InstanceType', 'Unknown')
        })
        
        # Apply tags to instance
        ec2.create_tags(
            Resources=[instance_id],
            Tags=tags
        )
        
        # Convert tags to dictionary for response
        tags_dict = {tag['Key']: tag['Value'] for tag in tags}
        
        return tags_dict
        
    except Exception as e:
        print(f"Error creating tags: {str(e)}")
        raise


def get_existing_tags(instance_id):
    """
    Get existing tags on an EC2 instance
    
    Args:
        instance_id: EC2 instance ID
        
    Returns:
        dict: Existing tags
    """
    try:
        response = ec2.describe_tags(
            Filters=[
                {
                    'Name': 'resource-id',
                    'Values': [instance_id]
                }
            ]
        )
        
        existing_tags = {tag['Key']: tag['Value'] for tag in response['Tags']}
        print(f"Existing tags on {instance_id}: {existing_tags}")
        
        return existing_tags
        
    except Exception as e:
        print(f"Error getting existing tags: {str(e)}")
        return {}
