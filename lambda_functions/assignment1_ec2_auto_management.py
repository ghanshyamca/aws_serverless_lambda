"""
Assignment 1: Automated Instance Management Using AWS Lambda and Boto3

This Lambda function automatically manages EC2 instances based on their tags:
- Stops instances tagged with Action=Auto-Stop
- Starts instances tagged with Action=Auto-Start

Author: AWS Lambda Automation Project
Date: January 2026
"""

import boto3
import json
from datetime import datetime

# Initialize EC2 client
ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    """
    Main Lambda handler function
    
    Args:
        event: Lambda event object
        context: Lambda context object
        
    Returns:
        dict: Response with statusCode and processed instance details
    """
    
    print(f"Lambda function started at {datetime.utcnow().isoformat()}")
    
    response = {
        'stopped_instances': [],
        'started_instances': [],
        'errors': []
    }
    
    try:
        # Process Auto-Stop instances
        print("Searching for instances with Action=Auto-Stop tag...")
        stop_instances = get_instances_by_tag('Action', 'Auto-Stop')
        
        if stop_instances:
            print(f"Found {len(stop_instances)} instance(s) to stop: {stop_instances}")
            stop_result = stop_ec2_instances(stop_instances)
            response['stopped_instances'] = stop_result
        else:
            print("No instances found with Auto-Stop tag")
        
        # Process Auto-Start instances
        print("Searching for instances with Action=Auto-Start tag...")
        start_instances = get_instances_by_tag('Action', 'Auto-Start')
        
        if start_instances:
            print(f"Found {len(start_instances)} instance(s) to start: {start_instances}")
            start_result = start_ec2_instances(start_instances)
            response['started_instances'] = start_result
        else:
            print("No instances found with Auto-Start tag")
            
    except Exception as e:
        error_msg = f"Error in lambda_handler: {str(e)}"
        print(error_msg)
        response['errors'].append(error_msg)
        
        return {
            'statusCode': 500,
            'body': json.dumps(response)
        }
    
    print(f"Lambda function completed successfully")
    print(f"Summary: Stopped {len(response['stopped_instances'])} instance(s), "
          f"Started {len(response['started_instances'])} instance(s)")
    
    return {
        'statusCode': 200,
        'body': json.dumps(response, default=str)
    }


def get_instances_by_tag(tag_key, tag_value):
    """
    Get EC2 instance IDs by tag key and value
    
    Args:
        tag_key: The tag key to filter by
        tag_value: The tag value to filter by
        
    Returns:
        list: List of instance IDs matching the tag
    """
    try:
        response = ec2.describe_instances(
            Filters=[
                {
                    'Name': f'tag:{tag_key}',
                    'Values': [tag_value]
                },
                {
                    'Name': 'instance-state-name',
                    'Values': ['running', 'stopped']
                }
            ]
        )
        
        instance_ids = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_ids.append(instance['InstanceId'])
                
        return instance_ids
        
    except Exception as e:
        print(f"Error getting instances by tag: {str(e)}")
        raise


def stop_ec2_instances(instance_ids):
    """
    Stop EC2 instances
    
    Args:
        instance_ids: List of instance IDs to stop
        
    Returns:
        list: List of dictionaries with instance details
    """
    stopped_instances = []
    
    try:
        # Filter only running instances
        running_instances = []
        for instance_id in instance_ids:
            instance_info = ec2.describe_instances(InstanceIds=[instance_id])
            state = instance_info['Reservations'][0]['Instances'][0]['State']['Name']
            
            if state == 'running':
                running_instances.append(instance_id)
            else:
                print(f"Instance {instance_id} is already {state}, skipping stop operation")
        
        if running_instances:
            response = ec2.stop_instances(InstanceIds=running_instances)
            
            for instance in response['StoppingInstances']:
                instance_detail = {
                    'InstanceId': instance['InstanceId'],
                    'PreviousState': instance['PreviousState']['Name'],
                    'CurrentState': instance['CurrentState']['Name']
                }
                stopped_instances.append(instance_detail)
                print(f"Stopped instance: {instance['InstanceId']} "
                      f"(Previous: {instance['PreviousState']['Name']}, "
                      f"Current: {instance['CurrentState']['Name']})")
        
        return stopped_instances
        
    except Exception as e:
        print(f"Error stopping instances: {str(e)}")
        raise


def start_ec2_instances(instance_ids):
    """
    Start EC2 instances
    
    Args:
        instance_ids: List of instance IDs to start
        
    Returns:
        list: List of dictionaries with instance details
    """
    started_instances = []
    
    try:
        # Filter only stopped instances
        stopped_instances = []
        for instance_id in instance_ids:
            instance_info = ec2.describe_instances(InstanceIds=[instance_id])
            state = instance_info['Reservations'][0]['Instances'][0]['State']['Name']
            
            if state == 'stopped':
                stopped_instances.append(instance_id)
            else:
                print(f"Instance {instance_id} is already {state}, skipping start operation")
        
        if stopped_instances:
            response = ec2.start_instances(InstanceIds=stopped_instances)
            
            for instance in response['StartingInstances']:
                instance_detail = {
                    'InstanceId': instance['InstanceId'],
                    'PreviousState': instance['PreviousState']['Name'],
                    'CurrentState': instance['CurrentState']['Name']
                }
                started_instances.append(instance_detail)
                print(f"Started instance: {instance['InstanceId']} "
                      f"(Previous: {instance['PreviousState']['Name']}, "
                      f"Current: {instance['CurrentState']['Name']})")
        
        return started_instances
        
    except Exception as e:
        print(f"Error starting instances: {str(e)}")
        raise
