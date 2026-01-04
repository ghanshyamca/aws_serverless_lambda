"""
Assignment 4: Automatic EBS Snapshot and Cleanup Using AWS Lambda and Boto3

This Lambda function automates:
- Creating snapshots for specified EBS volumes
- Cleaning up snapshots older than 30 days

Author: AWS Lambda Automation Project
Date: January 2026
"""

import boto3
import json
from datetime import datetime, timezone, timedelta

# Initialize EC2 client
ec2 = boto3.client('ec2')

# Configuration
VOLUME_ID = 'vol-0123456789abcdef0'  # Replace with your volume ID
RETENTION_DAYS = 30
DESCRIPTION_PREFIX = 'Automated-Backup'

def lambda_handler(event, context):
    """
    Main Lambda handler function
    
    Args:
        event: Lambda event object (can override volume_id and retention)
        context: Lambda context object
        
    Returns:
        dict: Response with snapshot details
    """
    
    print(f"Lambda function started at {datetime.now(timezone.utc).isoformat()}")
    
    # Allow configuration override
    volume_id = event.get('volume_id', VOLUME_ID)
    retention_days = event.get('retention_days', RETENTION_DAYS)
    
    response = {
        'volume_id': volume_id,
        'retention_days': retention_days,
        'created_snapshots': [],
        'deleted_snapshots': [],
        'errors': []
    }
    
    try:
        # Create new snapshot
        print(f"Creating snapshot for volume: {volume_id}")
        snapshot = create_snapshot(volume_id)
        
        if snapshot:
            response['created_snapshots'].append(snapshot)
            print(f"Created snapshot: {snapshot['SnapshotId']}")
        
        # Cleanup old snapshots
        print(f"\nCleaning up snapshots older than {retention_days} days")
        deleted = cleanup_old_snapshots(volume_id, retention_days)
        response['deleted_snapshots'] = deleted
        
        print(f"\nSummary:")
        print(f"Snapshots created: {len(response['created_snapshots'])}")
        print(f"Snapshots deleted: {len(response['deleted_snapshots'])}")
        
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
            'body': json.dumps(response, default=str)
        }


def create_snapshot(volume_id):
    """
    Create EBS snapshot for the specified volume
    
    Args:
        volume_id: EBS volume ID
        
    Returns:
        dict: Snapshot details
    """
    try:
        # Get volume details
        volumes = ec2.describe_volumes(VolumeIds=[volume_id])
        
        if not volumes['Volumes']:
            raise Exception(f"Volume {volume_id} not found")
        
        volume = volumes['Volumes'][0]
        
        # Create description
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d-%H-%M-%S')
        description = f"{DESCRIPTION_PREFIX}-{volume_id}-{timestamp}"
        
        # Create snapshot
        snapshot = ec2.create_snapshot(
            VolumeId=volume_id,
            Description=description,
            TagSpecifications=[
                {
                    'ResourceType': 'snapshot',
                    'Tags': [
                        {'Key': 'Name', 'Value': description},
                        {'Key': 'VolumeId', 'Value': volume_id},
                        {'Key': 'CreatedBy', 'Value': 'Lambda-Automation'},
                        {'Key': 'BackupDate', 'Value': datetime.now(timezone.utc).strftime('%Y-%m-%d')}
                    ]
                }
            ]
        )
        
        snapshot_details = {
            'SnapshotId': snapshot['SnapshotId'],
            'VolumeId': volume_id,
            'StartTime': snapshot['StartTime'].isoformat(),
            'State': snapshot['State'],
            'VolumeSize': snapshot['VolumeSize'],
            'Description': description
        }
        
        return snapshot_details
        
    except Exception as e:
        print(f"Error creating snapshot: {str(e)}")
        raise


def cleanup_old_snapshots(volume_id, retention_days):
    """
    Delete snapshots older than retention period
    
    Args:
        volume_id: EBS volume ID
        retention_days: Number of days to retain snapshots
        
    Returns:
        list: List of deleted snapshot details
    """
    deleted_snapshots = []
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
    
    try:
        # Get all snapshots for this volume
        snapshots = ec2.describe_snapshots(
            Filters=[
                {'Name': 'volume-id', 'Values': [volume_id]},
                {'Name': 'status', 'Values': ['completed']}
            ],
            OwnerIds=['self']
        )
        
        print(f"Found {len(snapshots['Snapshots'])} snapshot(s) for volume {volume_id}")
        
        # Check each snapshot
        for snapshot in snapshots['Snapshots']:
            snapshot_id = snapshot['SnapshotId']
            start_time = snapshot['StartTime']
            age_days = (datetime.now(timezone.utc) - start_time).days
            
            # Check if automated backup (by description prefix)
            description = snapshot.get('Description', '')
            if not description.startswith(DESCRIPTION_PREFIX):
                print(f"Skipping {snapshot_id}: Not an automated backup")
                continue
            
            if start_time < cutoff_date:
                print(f"Deleting snapshot {snapshot_id} (Age: {age_days} days)")
                
                try:
                    ec2.delete_snapshot(SnapshotId=snapshot_id)
                    
                    deleted_snapshots.append({
                        'SnapshotId': snapshot_id,
                        'StartTime': start_time.isoformat(),
                        'AgeDays': age_days,
                        'VolumeSize': snapshot['VolumeSize']
                    })
                    
                except Exception as delete_error:
                    print(f"Error deleting {snapshot_id}: {str(delete_error)}")
            else:
                print(f"Keeping snapshot {snapshot_id} (Age: {age_days} days)")
        
        return deleted_snapshots
        
    except Exception as e:
        print(f"Error in cleanup_old_snapshots: {str(e)}")
        raise


def list_all_snapshots(volume_id=None):
    """
    List all snapshots, optionally filtered by volume
    
    Args:
        volume_id: Optional volume ID to filter by
        
    Returns:
        list: List of snapshots
    """
    try:
        filters = [{'Name': 'status', 'Values': ['completed']}]
        
        if volume_id:
            filters.append({'Name': 'volume-id', 'Values': [volume_id]})
        
        response = ec2.describe_snapshots(
            Filters=filters,
            OwnerIds=['self']
        )
        
        return response['Snapshots']
        
    except Exception as e:
        print(f"Error listing snapshots: {str(e)}")
        raise
