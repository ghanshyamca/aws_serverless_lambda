"""
Assignment 3: Monitor Unencrypted S3 Buckets Using AWS Lambda and Boto3

This Lambda function detects S3 buckets without server-side encryption enabled
and logs the bucket names.

Author: AWS Lambda Automation Project
Date: January 2026
"""

import boto3
import json
from datetime import datetime, timezone

# Initialize S3 client
s3 = boto3.client('s3')

def lambda_handler(event, context):
    """
    Main Lambda handler function
    
    Args:
        event: Lambda event object
        context: Lambda context object
        
    Returns:
        dict: Response with unencrypted buckets list
    """
    
    print(f"Lambda function started at {datetime.now(timezone.utc).isoformat()}")
    
    response = {
        'total_buckets': 0,
        'unencrypted_buckets': [],
        'encrypted_buckets': [],
        'errors': []
    }
    
    try:
        # Get all S3 buckets
        buckets = list_all_buckets()
        response['total_buckets'] = len(buckets)
        
        # Check encryption for each bucket
        for bucket_name in buckets:
            try:
                is_encrypted = check_bucket_encryption(bucket_name)
                
                if is_encrypted:
                    response['encrypted_buckets'].append(bucket_name)
                    print(f"✓ {bucket_name}: Encrypted")
                else:
                    response['unencrypted_buckets'].append(bucket_name)
                    print(f"⚠️ {bucket_name}: NOT ENCRYPTED")
                    
            except Exception as e:
                error_msg = f"Error checking {bucket_name}: {str(e)}"
                print(error_msg)
                response['errors'].append(error_msg)
        
        print(f"\nSummary:")
        print(f"Total buckets: {response['total_buckets']}")
        print(f"Encrypted: {len(response['encrypted_buckets'])}")
        print(f"Unencrypted: {len(response['unencrypted_buckets'])}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
        
    except Exception as e:
        error_msg = f"Error in lambda_handler: {str(e)}"
        print(error_msg)
        response['errors'].append(error_msg)
        
        return {
            'statusCode': 500,
            'body': json.dumps(response)
        }


def list_all_buckets():
    """
    List all S3 buckets in the account
    
    Returns:
        list: List of bucket names
    """
    try:
        response = s3.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        return buckets
        
    except Exception as e:
        print(f"Error listing buckets: {str(e)}")
        raise


def check_bucket_encryption(bucket_name):
    """
    Check if S3 bucket has server-side encryption enabled and bucket key status
    
    Args:
        bucket_name: Name of the S3 bucket
        
    Returns:
        bool: True if encrypted with bucket key enabled (for KMS), False otherwise
    """
    try:
        # Get bucket encryption configuration
        response = s3.get_bucket_encryption(Bucket=bucket_name)
        
        # If we get here, encryption is configured
        rules = response.get('ServerSideEncryptionConfiguration', {}).get('Rules', [])
        
        if rules:
            for rule in rules:
                encryption_config = rule.get('ApplyServerSideEncryptionByDefault', {})
                encryption_type = encryption_config.get('SSEAlgorithm')
                bucket_key_enabled = rule.get('BucketKeyEnabled', False)
                
                print(f"  Encryption for {bucket_name}:")
                print(f"    - Type: {encryption_type}")
                    
            return True
        
        return False
        
    except s3.exceptions.ServerSideEncryptionConfigurationNotFoundError:
        # No encryption configured
        print(f"  ✗ Encryption is DISABLED for {bucket_name}")
        return False
        
    except Exception as e:
        print(f"Error checking encryption for {bucket_name}: {str(e)}")
        raise


def get_bucket_details(bucket_name):
    """
    Get additional bucket details
    
    Args:
        bucket_name: Name of the S3 bucket
        
    Returns:
        dict: Bucket details
    """
    try:
        # Get bucket location
        location = s3.get_bucket_location(Bucket=bucket_name)
        region = location.get('LocationConstraint', 'us-east-1')
        
        # Get bucket versioning
        try:
            versioning = s3.get_bucket_versioning(Bucket=bucket_name)
            versioning_status = versioning.get('Status', 'Disabled')
        except:
            versioning_status = 'Unknown'
        
        return {
            'name': bucket_name,
            'region': region,
            'versioning': versioning_status
        }
        
    except Exception as e:
        print(f"Error getting details for {bucket_name}: {str(e)}")
        return {
            'name': bucket_name,
            'error': str(e)
        }
