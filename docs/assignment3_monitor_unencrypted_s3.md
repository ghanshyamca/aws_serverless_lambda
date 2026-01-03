# Assignment 3: Monitor Unencrypted S3 Buckets Using AWS Lambda and Boto3

## 📋 Overview

This Lambda function enhances AWS security posture by automatically detecting S3 buckets without server-side encryption enabled. It scans all S3 buckets in your account and identifies those that lack encryption protection.

**Objective:** Automate the detection of S3 buckets that don't have server-side encryption enabled.

---

## 🎯 Key Features

- ✅ **Automatic Bucket Scanning** - Lists all S3 buckets in the AWS account
- ✅ **Filtered Scanning** - Scans only buckets starting with 'ghanshyam' prefix
- ✅ **Encryption Detection** - Checks for server-side encryption configuration
- ✅ **Detailed Logging** - Logs encryption status for each bucket
- ✅ **JSON Response** - Returns structured data with encrypted/unencrypted bucket lists
- ✅ **Error Handling** - Gracefully handles bucket access errors
- ✅ **Encryption Type Identification** - Shows AES256, aws:kms, etc.

---

## 📁 Files

- **Lambda Function:** `lambda_functions/assignment3_monitor_unencrypted_s3.py`
- **IAM Policy:** `iam_policies/s3_encryption_monitor_policy.json` (to be created)
- **Test Setup Script:** `old/setup_buckets_assignment3.py`

---

## 🔧 Prerequisites

### AWS Resources
- AWS Account with appropriate permissions
- S3 buckets (mix of encrypted and unencrypted for testing)
- IAM role for Lambda execution

### Required AWS Services
- AWS Lambda
- Amazon S3
- AWS IAM
- Amazon CloudWatch (for logs)

### Python Requirements
```
boto3>=1.34.0
```

---

## 📝 Setup Instructions

### Step 1: Create Test S3 Buckets

Create a few S3 buckets with different encryption configurations:

**Option A: Using AWS Console**

1. Navigate to S3 Console
2. Click **Create bucket**
3. Name: `ghanshyam-no-encryption-1`
4. Region: `us-east-1`
5. **DO NOT enable** default encryption
6. Click **Create bucket**
7. Repeat for additional test buckets

**Option B: Using Setup Script**

```powershell
cd old
python setup_buckets_assignment3.py
```

This creates 4 unencrypted test buckets:
- `ghanshyam-no-encryption-1`
- `ghanshyam-no-encryption-2`
- `ghanshyam-unencrypted-test`
- `ghanshyam-test-no-sse`

---

### Step 2: Create IAM Role for Lambda

**2.1 Create IAM Role**

1. Go to **IAM Console** → **Roles**
2. Click **Create role**
3. Select **AWS service** → **Lambda**
4. Click **Next**

**2.2 Attach Policies**

Attach the following managed policy:
- ✅ `AmazonS3ReadOnlyAccess`

Or create custom policy with minimal permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "s3:GetEncryptionConfiguration",
                "s3:GetBucketLocation"
            ],
            "Resource": "*"
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

**2.3 Name the Role**
- Role name: `Lambda-S3-Encryption-Monitor`
- Click **Create role**

---

### Step 3: Create Lambda Function

**3.1 Basic Configuration**

1. Go to **Lambda Console**
2. Click **Create function**
3. Choose **Author from scratch**
4. Function name: `S3-Encryption-Monitor`
5. Runtime: **Python 3.11** (or latest 3.x)
6. Architecture: `x86_64`
7. Execution role: **Use an existing role**
8. Select: `Lambda-S3-Encryption-Monitor`
9. Click **Create function**

**3.2 Upload Function Code**

1. In the **Code** tab, delete default code
2. Copy contents from `lambda_functions/assignment3_monitor_unencrypted_s3.py`
3. Paste into the Lambda editor
4. Click **Deploy**

**3.3 Configure Function Settings**

- **Memory:** 256 MB
- **Timeout:** 1 minute
- **Description:** "Monitor S3 buckets for missing server-side encryption"

---

### Step 4: Configure CloudWatch Logs

Lambda automatically creates a CloudWatch log group:
- Log group: `/aws/lambda/S3-Encryption-Monitor`
- Retention: Set to 7 days (recommended)

---

## 🧪 Testing

### Test 1: Manual Invocation

1. In Lambda Console, click **Test** tab
2. Create new test event:
   - Event name: `TestEncryptionScan`
   - Template: `hello-world`
   - Event JSON: `{}`
3. Click **Save**
4. Click **Test**

**Expected Output:**
```json
{
  "statusCode": 200,
  "body": "{\"total_buckets\": 25, \"unencrypted_buckets\": [\"ghanshyam-no-encryption-1\", \"ghanshyam-no-encryption-2\", \"ghanshyam-unencrypted-test\", \"ghanshyam-test-no-sse\"], \"encrypted_buckets\": [], \"errors\": []}"
}
```

**Note:** The function filters buckets by prefix ('ghanshyam'), so only matching buckets are checked for encryption.

### Test 2: Check CloudWatch Logs

1. Go to **CloudWatch Console** → **Log groups**
2. Find `/aws/lambda/S3-Encryption-Monitor`
3. Click latest log stream
4. Verify output shows:
   ```25 bucket(s) total, 4 bucket(s) starting with 'ghanshyam'
   ✗ Encryption is DISABLED for ghanshyam-no-encryption-1
   ⚠️ ghanshyam-no-encryption-1: NOT ENCRYPTED
   ...
   Summary:
   Total buckets: 25
   Encrypted: 0
   Unencrypted: 4
   ```

**Note:** Total buckets shows all buckets in account, but only 'ghanshyam' prefixed buckets are scanned.rypted: 0
   Unencrypted: 4
   ```

### Test 3: Enable Encryption on One Bucket

1. Go to S3 Console
2. Select `ghanshyam-no-encryption-1`
3. Go to **Properties** tab
4. Scroll to **Default encryption**
5. Click **Edit**
6. Enable **Server-side encryption**
7. Choose **Amazon S3 managed keys (SSE-S3)**
8. Click **Save changes**
9. Run Lambda function again
10. Verify this bucket now appears in `encrypted_buckets`

---

## 📊 Sample Output

### CloudWatch Logs
```
START RequestId: abc123...
Lambda function started at 2026-01-04T10:30:00.000000+00:00
Found 25 bucket(s) total, 4 bucket(s) starting with 'ghanshyam'

  ✗ Encryption is DISABLED for ghanshyam-no-encryption-1
⚠️ ghanshyam-no-encryption-1: NOT ENCRYPTED

  ✗ Encryption is DISABLED for ghanshyam-no-encryption-2
⚠️ ghanshyam-no-encryption-2: NOT ENCRYPTED

  Encryption for ghanshyam-cleanup-bucket:
    - Type: AES256
✓ ghanshyam-cleanup-bucket: Encrypted

  ✗ Encryption is DISABLED for ghanshyam-unencrypted-test
⚠️ ghanshyam-unencrypted-test: NOT ENCRYPTED

Summary:
Total buckets: 25
Encrypted: 1
Unencrypted: 3
END RequestId: abc123...
```

### Lambda Response
```json
{
  "statusCode": 200,25,
    "unencrypted_buckets": [
      "ghanshyam-no-encryption-1",
      "ghanshyam-no-encryption-2",
      "ghanshyam-unencrypted-test"
    ],
    "encrypted_buckets": [
      "ghanshyam-cleanup-bucket"
    ],
    "errors": []
  }
}
```

**Note:** The function scans all buckets but only checks those starting with 'ghanshyam' prefix (configurable in code).
}
```

---

## 🔐 Security Best Practices

### 1. Least Privilege IAM
- Use custom IAM policy instead of `AmazonS3ReadOnlyAccess`
- Only grant necessary permissions
- Don't include `s3:*` or overly broad permissions

### 2. Encryption Recommendations
- **Always enable** S3 server-side encryption
- Use **SSE-S3** (AES-256) for general use

### 4. Monitoring
- Set up CloudWatch alarms for unencrypted buckets
- Review logs regularly
- Schedule periodic scans
- Consider SNS notifications for immediate alertls and execution time
- Use **SSE-KMS** for additional key management control
- Enable **Bucket Key** for KMS to reduce API calls and costs

### 3. Monitoring
- Set up CloudWatch alarms for unencrypted buckets
- Review logs regularly
- Schedule periodic scans

---

## 📅 Scheduling (Optional)

To run this scan automatically:

### Option 1: EventBridge Schedule

1. Go to **EventBridge Console** → **Rules**
2. Click **Create rule**
3. Name: `S3-Encryption-Daily-Scan`
4. Rule type: **Schedule**
5. Schedule pattern: `cron(0 9 * * ? *)` (daily at 9 AM UTC)
6. Target: **Lambda function**
7. Select: `S3-Encryption-Monitor`
8. Click **Create**

### Option 2: Manual Schedule via AWS CLI
```bash
aws events put-rule --name S3-Encryption-Daily-Scan \
  --schedule-expression "cron(0 9 * * ? *)" \
  --state ENABLED

aws events put-targets --rule S3-Encryption-Daily-Scan \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:ACCOUNT_ID:function:S3-Encryption-Monitor"

aws lambda add-permission --function-name S3-Encryption-Monitor \
  --statement-id EventBridgeInvoke \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:ACCOUNT_ID:rule/S3-Encryption-Daily-Scan
```

---

## 🐛 Troubleshooting

### Issue: "Access Denied" Error

**Cause:** Lambda IAM role lacks S3 permissions

**Solution:**
1. Check IAM role has `s3:ListAllMyBuckets` permission
2. Check IAM role has `s3:GetEncryptionConfiguration` permission
3. Verify role is attached to Lambda function

### Issue: No Buckets Found

**Cause:** Buckets in different region or account

**Solution:**
- `ListBuckets` is global and should show all buckets
- Verify AWS credentials are correct
- Check CloudWatch logs for error messages

### Issue: Function Timeout

**Cause:** Too many buckets to scan in 3 seconds

**Solution:**
1. Increase Lambda timeout to 1-3 minutes
2. Add pagination or filtering logic
3. Consider processing in batches

### Issue: Some Buckets Show Errors

**Cause:** Cross-region or permission issues

**Solution:**
- Function logs individual bucket errors
- Check `errors` array in response
- Verify bucket ownership and access

---

## 💰 Cost Estimation

**Monthly Cost Breakdown:**

| Service | Usage | Cost |
|---------|-------|------|
| Lambda Invocations | 30 runs/month | $0.00 (free tier) |
| Lambda Duration | 30 × 5 sec | $0.00 (free tier) |
| CloudWatch Logs | 1 MB/month | $0.00 (free tier) |
| S3 API Calls | 30 × 10 buckets | $0.00 (negligible) |
| **Total** | | **~$0.00/month** |

*Assumes free tier eligibility and <100 buckets*

---

## 📚 Additional Features (Enhancements)

### Send SNS Notification for Unencrypted Buckets

Add to lambda function:
```python
import boto3
sns = boto3.client('sns')
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:ACCOUNT:S3EncryptionAlerts'

# After scanning, if unencrypted buckets found:
if response['unencrypted_buckets']:
    message = f"⚠️ Found {len(response['unencrypted_buckets'])} unencrypted S3 bucket(s):\n"
    message += "\n".join(response['unencrypted_buckets'])
    
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject='S3 Encryption Alert',
        Message=message
    )
```

### Auto-Enable Encryption (Advanced)

Modify function to automatically enable encryption:
```python
def auto_enable_encryption(bucket_name):
    s3.put_bucket_encryption(
        Bucket=bucket_name,
        ServerSideEncryptionConfiguration={
            'Rules': [{
                'ApplyServerSideEncryptionByDefault': {
                    'SSEAlgorithm': 'AES256'
                }
            }]
        }
    )
```

---

## 🎓 Learning Outcomes

After completing this assignment, you will understand:

✅ How to use Boto3 to interact with S3  
✅ S3 server-side encryption configurations  
✅ Lambda function development and deployment  
✅ IAM policies and least-privilege access  
✅ CloudWatch Logs for monitoring  
✅ Error handling in Python Lambda functions  
✅ AWS security best practices for S3  

---

## 📖 References

- [AWS S3 Encryption Documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/serv-side-encryption.html)
- [Boto3 S3 Client Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)
- [AWS Lambda Python Documentation](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [S3 Bucket Key](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-key.html)

---

## ✅ Completion Checklist

- [ ] Created test S3 buckets (some without encryption)
- [ ] Created IAM role with S3 read permissions
- [ ] Created Lambda function with Python 3.x runtime
- [ ] Deployed function code
- [ ] Configured timeout and memory
- [ ] Tested function manually
- [ ] Verified CloudWatch logs
- [ ] Tested with encrypted bucket
- [ ] (Optional) Set up EventBridge schedule
- [ ] (Optional) Added SNS notifications

---

**Assignment Status:** ✅ Complete  
**Documentation Date:** January 2026  
**Last Updated:** January 4, 2026
