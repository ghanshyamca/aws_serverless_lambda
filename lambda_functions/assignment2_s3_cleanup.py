"""
Assignment 2: Automated S3 Bucket Cleanup Using AWS Lambda and Boto3

This Lambda function automatically deletes files older than 30 days 
from a specified S3 bucket.

Author: AWS Lambda Automation Project
Date: January 2026
"""

import boto3
import json
from datetime import datetime, timezone, timedelta

# Initialize S3 client
s3 = boto3.client('s3')

# Configuration
BUCKET_NAME = 'ghanshyam-cleanup-bucket'  # Replace with your bucket name
RETENTION_DAYS = 30

def lambda_handler(event, context):
    """
    Main Lambda handler function
    
    Args:
        event: Lambda event object (can override bucket name)
        context: Lambda context object
        
    Returns:
        dict: Response with statusCode and deleted files details
    """
    
    print(f"Lambda function started at {datetime.now(timezone.utc).isoformat()}")
    
    # Allow bucket name override from event
    bucket_name = event.get('bucket_name', BUCKET_NAME)
    retention_days = event.get('retention_days', RETENTION_DAYS)
    
    print(f"Processing bucket: {bucket_name}")
    print(f"Retention period: {retention_days} days")
    
    response = {
        'bucket': bucket_name,
        'retention_days': retention_days,
        'deleted_files': [],
        'total_size_deleted_bytes': 0,
        'errors': []
    }
    
    try:
        # Calculate cutoff date
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
        print(f"Cutoff date: {cutoff_date.isoformat()}")
        
        # List and delete old objects
        deleted_files = delete_old_files(bucket_name, cutoff_date)
        
        response['deleted_files'] = deleted_files
        response['total_size_deleted_bytes'] = sum(f['size'] for f in deleted_files)
        
        print(f"Cleanup completed successfully")
        print(f"Total files deleted: {len(deleted_files)}")
        print(f"Total size freed: {response['total_size_deleted_bytes']} bytes "
              f"({response['total_size_deleted_bytes'] / (1024*1024):.2f} MB)")
        
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


def delete_old_files(bucket_name, cutoff_date):
    """
    Delete files older than the cutoff date from S3 bucket
    
    Args:
        bucket_name: Name of the S3 bucket
        cutoff_date: Datetime object representing the cutoff date
        
    Returns:
        list: List of deleted file details
    """
    deleted_files = []
    continuation_token = None
    
    try:
        while True:
            # List objects in bucket (with pagination)
            list_params = {
                'Bucket': bucket_name,
                'MaxKeys': 1000
            }
            
            if continuation_token:
                list_params['ContinuationToken'] = continuation_token
            
            response = s3.list_objects_v2(**list_params)
            
            if 'Contents' not in response:
                print(f"No objects found in bucket: {bucket_name}")
                break
            
            # Process each object
            for obj in response['Contents']:
                key = obj['Key']
                last_modified = obj['LastModified']
                size = obj['Size']
                
                # Check if file is older than cutoff date
                if last_modified < cutoff_date:
                    age_days = (datetime.now(timezone.utc) - last_modified).days
                    
                    print(f"Deleting: {key} (Last modified: {last_modified.isoformat()}, "
                          f"Age: {age_days} days, Size: {size} bytes)")
                    
                    try:
                        # Delete the object
                        s3.delete_object(Bucket=bucket_name, Key=key)
                        
                        deleted_files.append({
                            'key': key,
                            'last_modified': last_modified.isoformat(),
                            'age_days': age_days,
                            'size': size
                        })
                        
                    except Exception as delete_error:
                        print(f"Error deleting {key}: {str(delete_error)}")
                else:
                    age_days = (datetime.now(timezone.utc) - last_modified).days
                    print(f"Keeping: {key} (Age: {age_days} days)")
            
            # Check if there are more objects to process
            if response.get('IsTruncated', False):
                continuation_token = response['NextContinuationToken']
            else:
                break
        
        return deleted_files
        
    except Exception as e:
        print(f"Error in delete_old_files: {str(e)}")
        raise


def get_bucket_info(bucket_name):
    """
    Get information about the S3 bucket
    
    Args:
        bucket_name: Name of the S3 bucket
        
    Returns:
        dict: Bucket information
    """
    try:
        # Get bucket location
        location = s3.get_bucket_location(Bucket=bucket_name)
        
        # Get bucket versioning status
        try:
            versioning = s3.get_bucket_versioning(Bucket=bucket_name)
        except:
            versioning = {'Status': 'Not configured'}
        
        bucket_info = {
            'name': bucket_name,
            'region': location.get('LocationConstraint', 'us-east-1'),
            'versioning': versioning.get('Status', 'Disabled')
        }
        
        print(f"Bucket info: {json.dumps(bucket_info)}")
        return bucket_info
        
    except Exception as e:
        print(f"Error getting bucket info: {str(e)}")
        raise
