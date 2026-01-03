# Assignment 2: Automated S3 Bucket Cleanup Using AWS Lambda and Boto3

## Objective
Automate the deletion of files older than 30 days in an S3 bucket using AWS Lambda and Boto3.

## Overview
This Lambda function:
- Lists all objects in a specified S3 bucket
- Identifies files older than 30 days
- Deletes old files automatically
- Logs all operations for audit purposes

---

## Prerequisites
- AWS Account with S3 and Lambda access
- Basic understanding of S3 storage
- Test files (some older than 30 days)

---

## Step-by-Step Implementation

### Step 1: Create S3 Bucket

1. Navigate to **S3 Console** → **Create Bucket**
2. Configuration:
   - **Bucket name:** `my-cleanup-test-bucket-<unique-id>`
   - **Region:** Choose your preferred region
   - **Block Public Access:** Keep enabled (recommended)
   - **Versioning:** Disabled (for this demo)
   - **Encryption:** Enable default encryption

3. Click **Create Bucket**

**Screenshot:** `screenshots/assignment2_s3_bucket_create.png`

---

### Step 2: Upload Test Files

Upload multiple files to simulate different ages:

**Method 1: Using AWS Console**
1. Open your bucket
2. Click **Upload**
3. Add files
4. Upload

**Method 2: Creating Files Programmatically**

For testing purposes, you can upload files and manually modify their metadata timestamps:

```python
import boto3
from datetime import datetime, timedelta

s3 = boto3.client('s3')
bucket_name = 'my-cleanup-test-bucket-<unique-id>'

# Upload test files
test_files = [
    ('old_file_1.txt', 45),  # 45 days old
    ('old_file_2.txt', 35),  # 35 days old
    ('recent_file_1.txt', 5), # 5 days old
    ('recent_file_2.txt', 10) # 10 days old
]

for filename, days_old in test_files:
    s3.put_object(
        Bucket=bucket_name,
        Key=filename,
        Body=f'Test content for {filename}'
    )
```

**Note:** For actual testing, you may need to use files that are genuinely old, or adjust your system date temporarily.

**Screenshot:** `screenshots/assignment2_s3_files_uploaded.png`

---

### Step 3: Create IAM Role for Lambda

1. Go to **IAM Console** → **Roles** → **Create Role**
2. Select **AWS Service** → **Lambda**
3. Attach policies:
   - `AmazonS3FullAccess` (for demo)
   - `CloudWatchLogsFullAccess` (for logging)

4. Name: `Lambda-S3-Cleanup-Role`

**Production Policy (Least Privilege):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::my-cleanup-test-bucket-*",
        "arn:aws:s3:::my-cleanup-test-bucket-*/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

**Screenshot:** `screenshots/assignment2_iam_role.png`

---

### Step 4: Create Lambda Function

1. **Lambda Console** → **Create Function**
2. Configuration:
   - **Function name:** `S3-Cleanup-Old-Files`
   - **Runtime:** Python 3.11 or 3.12
   - **Architecture:** x86_64
   - **Execution role:** `Lambda-S3-Cleanup-Role`

3. Click **Create Function**

**Screenshot:** `screenshots/assignment2_lambda_create.png`

---

### Step 5: Add Lambda Code

1. In **Code** tab, replace default code with:
   - `lambda_functions/assignment2_s3_cleanup.py`

2. **Important:** Update the following in the code:
   ```python
   BUCKET_NAME = 'my-cleanup-test-bucket-<your-unique-id>'
   RETENTION_DAYS = 30
   ```

3. Click **Deploy**

**Key Features:**
- Pagination support for large buckets
- Calculates file age based on `LastModified` timestamp
- Logs detailed information about deleted files
- Returns size and count of deleted files
- Error handling for individual file deletions

**Screenshot:** `screenshots/assignment2_lambda_code.png`

---

### Step 6: Configure Lambda Settings

1. **Configuration** → **General Configuration**
   - **Timeout:** 5 minutes (for large buckets)
   - **Memory:** 256 MB (for processing large file lists)

2. **Environment Variables** (optional):
   - `BUCKET_NAME`: Your bucket name
   - `RETENTION_DAYS`: `30`

**Screenshot:** `screenshots/assignment2_lambda_config.png`

---

### Step 7: Test the Lambda Function

1. Click **Test** tab
2. Create test event:
   - **Event name:** `TestS3Cleanup`
   - **Event JSON:**
   ```json
   {
     "bucket_name": "my-cleanup-test-bucket-<unique-id>",
     "retention_days": 30
   }
   ```

3. Click **Test**

**Expected Results:**
- Files older than 30 days are deleted
- Recent files remain in bucket
- Detailed log shows which files were deleted

**Screenshot:** `screenshots/assignment2_test_result.png`

---

### Step 8: Verify S3 Bucket

1. Go to **S3 Console**
2. Open your bucket
3. Confirm only files newer than 30 days remain

**Before Cleanup:**
- old_file_1.txt (45 days old) ✓
- old_file_2.txt (35 days old) ✓
- recent_file_1.txt (5 days old) ✓
- recent_file_2.txt (10 days old) ✓

**After Cleanup:**
- ~~old_file_1.txt (45 days old)~~ ✗ Deleted
- ~~old_file_2.txt (35 days old)~~ ✗ Deleted
- recent_file_1.txt (5 days old) ✓
- recent_file_2.txt (10 days old) ✓

**Screenshot:** `screenshots/assignment2_s3_after_cleanup.png`

---

### Step 9: Review CloudWatch Logs

1. **CloudWatch** → **Log groups** → `/aws/lambda/S3-Cleanup-Old-Files`
2. View latest log stream

**Sample Log Output:**
```
Lambda function started at 2026-01-03T10:45:00.000000
Processing bucket: my-cleanup-test-bucket-12345
Retention period: 30 days
Cutoff date: 2025-12-04T10:45:00.000000+00:00
Deleting: old_file_1.txt (Last modified: 2025-11-18, Age: 45 days, Size: 2048 bytes)
Deleting: old_file_2.txt (Last modified: 2025-11-28, Age: 35 days, Size: 1024 bytes)
Keeping: recent_file_1.txt (Age: 5 days)
Keeping: recent_file_2.txt (Age: 10 days)
Cleanup completed successfully
Total files deleted: 2
Total size freed: 3072 bytes (0.00 MB)
```

**Screenshot:** `screenshots/assignment2_cloudwatch_logs.png`

---

## Optional Enhancements

### Schedule Automatic Cleanup

Set up EventBridge to run cleanup weekly:

1. **EventBridge** → **Rules** → **Create Rule**
2. Configuration:
   - **Name:** `S3-Weekly-Cleanup`
   - **Schedule:** `cron(0 2 ? * SUN *)` (2 AM every Sunday)
   - **Target:** Lambda → `S3-Cleanup-Old-Files`

**Screenshot:** `screenshots/assignment2_eventbridge.png`

### Add SNS Notifications

Modify the Lambda to send summary via SNS:

```python
import boto3

sns = boto3.client('sns')
SNS_TOPIC_ARN = 'arn:aws:sns:region:account:S3CleanupNotifications'

# After cleanup
message = f"""
S3 Cleanup Summary
Bucket: {bucket_name}
Files Deleted: {len(deleted_files)}
Size Freed: {total_size_freed / (1024*1024):.2f} MB
"""

sns.publish(
    TopicArn=SNS_TOPIC_ARN,
    Subject='S3 Cleanup Completed',
    Message=message
)
```

---

## Testing Scenarios

### Test Case 1: Mixed Age Files
- Upload files with various ages
- Run Lambda
- Verify only old files deleted

### Test Case 2: Empty Bucket
- Empty bucket
- Run Lambda
- Verify no errors occur

### Test Case 3: All Old Files
- Upload only old files
- Run Lambda
- Verify bucket is empty

### Test Case 4: All Recent Files
- Upload only recent files
- Run Lambda
- Verify no deletions occur

---

## Troubleshooting

### Issue: Access Denied
**Error:** `An error occurred (AccessDenied)`

**Solutions:**
- Verify IAM role has S3 permissions
- Check bucket policy doesn't block Lambda
- Ensure bucket name is correct

### Issue: No Files Deleted
**Problem:** Lambda runs but doesn't delete files

**Solutions:**
- Check file timestamps are genuinely old
- Verify `RETENTION_DAYS` configuration
- Review CloudWatch logs for details
- Ensure timezone handling is correct

### Issue: Lambda Timeout
**Error:** Task timed out

**Solutions:**
- Increase Lambda timeout
- Process files in batches
- Consider using S3 Lifecycle Policies for very large buckets

---

## Cost Considerations

- **Lambda:** Free tier covers 1M requests/month
- **S3:** 
  - Storage costs reduced by deleting old files
  - LIST and DELETE API calls (minimal cost)
- **CloudWatch Logs:** Free tier includes 5 GB

**Alternative: S3 Lifecycle Policies**

For simple age-based deletion, consider S3 Lifecycle Policies:
- No Lambda required
- Native S3 feature
- Transition to Glacier or delete automatically

---

## Security Best Practices

1. ✅ Use least-privilege IAM policies
2. ✅ Enable S3 versioning for critical data
3. ✅ Test on non-production buckets first
4. ✅ Enable S3 bucket logging
5. ✅ Consider MFA delete for protection
6. ⚠️ **Caution:** Deletion is permanent (unless versioning enabled)

---

## Comparison: Lambda vs S3 Lifecycle Policies

| Feature | Lambda Function | S3 Lifecycle Policy |
|---------|----------------|---------------------|
| Complexity | Custom logic possible | Simple age-based rules |
| Cost | Lambda execution costs | No compute cost |
| Flexibility | High (custom conditions) | Limited |
| Logging | Detailed CloudWatch logs | Basic S3 logs |
| Best For | Complex cleanup logic | Simple age-based cleanup |

---

## Cleanup

To avoid charges:

1. Empty and delete S3 bucket
2. Delete Lambda function
3. Delete IAM role
4. Delete CloudWatch log groups
5. Delete EventBridge rules (if created)

---

## Conclusion

This assignment demonstrates:
- ✅ S3 object management with Boto3
- ✅ Date-based file filtering
- ✅ Automated cleanup operations
- ✅ CloudWatch logging and monitoring
- ✅ Storage cost optimization

**Key Learnings:**
- S3 API operations (ListObjects, DeleteObject)
- Working with datetime and timezones
- Pagination for large result sets
- Error handling for batch operations
- When to use Lambda vs native AWS features
