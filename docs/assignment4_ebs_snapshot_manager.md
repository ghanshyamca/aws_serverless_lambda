# Assignment 4: Automatic EBS Snapshot and Cleanup Using AWS Lambda and Boto3

## Objective
Automate the creation of EBS volume snapshots and cleanup of old snapshots (older than 30 days) using AWS Lambda and Boto3.

## Overview
This Lambda function:
- Creates automated snapshots for specified EBS volumes
- Tags snapshots with metadata for tracking
- Identifies snapshots older than 30 days
- Deletes old snapshots automatically
- Logs all operations for audit purposes
- Supports configuration overrides via Lambda event

---

## Prerequisites
- AWS Account with EC2, EBS, and Lambda access
- An existing EBS volume attached to an EC2 instance
- Basic understanding of EBS snapshots and backup strategies
- IAM permissions for snapshot management

---

## Step-by-Step Implementation

### Step 1: Identify EBS Volume

1. Navigate to **EC2 Console** → **Volumes**
2. Identify the volume you want to backup
3. Note the **Volume ID** (e.g., `vol-08d770f6336866caf`)
4. Verify the volume state is `in-use` or `available`

**Key Information to Note:**
- Volume ID
- Volume Size
- Availability Zone
- Attached Instance (if any)

---

### Step 2: Create IAM Role for Lambda

1. Go to **IAM Console** → **Roles** → **Create Role**
2. Select **AWS Service** → **Lambda**
3. Create a custom policy or attach these managed policies:
   - `AmazonEC2ReadOnlyAccess`
   - `CloudWatchLogsFullAccess`

4. **Custom Policy for EBS Snapshots:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateSnapshot",
        "ec2:DeleteSnapshot",
        "ec2:DescribeSnapshots",
        "ec2:DescribeVolumes",
        "ec2:CreateTags"
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

5. **Role name:** `Lambda-EBS-Snapshot-Role`
6. Click **Create Role**

---

### Step 3: Create Lambda Function

1. **Lambda Console** → **Create Function**
2. Configuration:
   - **Function name:** `EBS-Snapshot-Manager`
   - **Runtime:** Python 3.11 or 3.12
   - **Architecture:** x86_64
   - **Execution role:** Use existing role → `Lambda-EBS-Snapshot-Role`

3. Click **Create Function**

---

### Step 4: Add Lambda Code

1. In **Code** tab, replace default code with:
   - `lambda_functions/assignment4_ebs_snapshot_manager.py`

2. **Important Configuration:**
   ```python
   VOLUME_ID = 'vol-08d770f6336866caf'  # Replace with your volume ID
   RETENTION_DAYS = 30
   DESCRIPTION_PREFIX = 'Automated-Backup'
   ```

3. Click **Deploy**

**Key Features:**
- **Automated Snapshot Creation:** Creates timestamped snapshots with descriptive tags
- **Retention Management:** Deletes snapshots older than configured retention period
- **Smart Filtering:** Only deletes automated backups (by description prefix)
- **Event Override:** Supports runtime configuration via Lambda event
- **Comprehensive Tagging:** Tags include Name, VolumeId, CreatedBy, BackupDate
- **Error Handling:** Individual snapshot operations are error-tolerant
- **Detailed Logging:** Tracks creation, deletion, and errors

---

### Step 5: Configure Lambda Settings

1. **Configuration** → **General Configuration**
   - **Timeout:** 3 minutes (for large volumes)
   - **Memory:** 256 MB

2. **Configuration** → **Environment Variables** (Optional)
   - `VOLUME_ID`: Your volume ID
   - `RETENTION_DAYS`: Number of days (default: 30)

---

### Step 6: Test the Lambda Function

#### Test Event 1: Default Configuration
```json
{}
```

**Expected Results:**
- New snapshot created for configured volume
- Snapshot tagged with timestamp and metadata
- Old snapshots (>30 days) deleted
- Response includes created and deleted snapshot details

#### Test Event 2: Override Configuration
```json
{
  "volume_id": "vol-08d770f6336866caf",
  "retention_days": 7
}
```

**Expected Results:**
- Creates snapshot for specified volume
- Deletes snapshots older than 7 days
- More aggressive cleanup with shorter retention

**CloudWatch Logs Output Example:**
```
Lambda function started at 2026-01-04T15:30:00.000000+00:00
Creating snapshot for volume: vol-08d770f6336866caf
Created snapshot: snap-0abc123def456789
Snapshot ID: snap-0abc123def456789
Volume ID: vol-08d770f6336866caf
Start Time: 2026-01-04T15:30:05.000000+00:00
State: pending
Volume Size: 8 GB

Cleaning up snapshots older than 30 days
Found 5 snapshot(s) for volume vol-08d770f6336866caf
Deleting snapshot snap-0old123abc456789 (Age: 35 days)
Deleting snapshot snap-0old456def789abc (Age: 42 days)
Keeping snapshot snap-0new789ghi012def (Age: 15 days)

Summary:
Snapshots created: 1
Snapshots deleted: 2
```

**Lambda Response Example:**
```json
{
  "statusCode": 200,
  "body": {
    "volume_id": "vol-08d770f6336866caf",
    "retention_days": 30,
    "created_snapshots": [
      {
        "SnapshotId": "snap-0abc123def456789",
        "VolumeId": "vol-08d770f6336866caf",
        "StartTime": "2026-01-04T15:30:05+00:00",
        "State": "pending",
        "VolumeSize": 8,
        "Description": "Automated-Backup-vol-08d770f6336866caf-2026-01-04-15-30-05"
      }
    ],
    "deleted_snapshots": [
      {
        "SnapshotId": "snap-0old123abc456789",
        "StartTime": "2025-11-30T10:15:00+00:00",
        "AgeDays": 35,
        "VolumeSize": 8
      },
      {
        "SnapshotId": "snap-0old456def789abc",
        "StartTime": "2025-11-23T14:20:00+00:00",
        "AgeDays": 42,
        "VolumeSize": 8
      }
    ],
    "errors": []
  }
}
```

---

### Step 7: Verify in EC2 Console

1. Go to **EC2 Console** → **Snapshots**
2. Filter by **Volume ID** or **Owner: Self**
3. Verify:
   - New snapshot is created with current timestamp
   - Snapshot description follows pattern: `Automated-Backup-vol-xxx-YYYY-MM-DD-HH-MM-SS`
   - Tags include: Name, VolumeId, CreatedBy, BackupDate
   - Old snapshots (>30 days) with `Automated-Backup` prefix are deleted
   - Manual snapshots (without prefix) are preserved

**Snapshot Tags:**
- **Name:** Automated-Backup-vol-08d770f6336866caf-2026-01-04-15-30-05
- **VolumeId:** vol-08d770f6336866caf
- **CreatedBy:** Lambda-Automation
- **BackupDate:** 2026-01-04

---

### Step 8: Schedule Automatic Backups (Optional)

#### Option 1: EventBridge Rule for Daily Backups

1. **EventBridge Console** → **Rules** → **Create Rule**
2. Configuration:
   - **Name:** `Daily-EBS-Snapshot`
   - **Rule type:** Schedule
   - **Schedule pattern:** Cron expression
     - `0 2 * * ? *` (Daily at 2 AM UTC)
   - **Target:** Lambda function → `EBS-Snapshot-Manager`

3. Click **Create**

#### Option 2: Weekly Backups
- Cron: `0 2 ? * SUN *` (Every Sunday at 2 AM UTC)

#### Option 3: Hourly Backups
- Cron: `0 * * * ? *` (Every hour)

---

## Configuration Options

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `VOLUME_ID` | EBS Volume ID to backup | `vol-08d770f6336866caf` |
| `RETENTION_DAYS` | Days to retain snapshots | `30` |
| `DESCRIPTION_PREFIX` | Prefix for automated snapshots | `Automated-Backup` |

### Event Override
Pass parameters in Lambda event to override defaults:
```json
{
  "volume_id": "vol-different123",
  "retention_days": 7
}
```

---

## Code Functions

### 1. `lambda_handler(event, context)`
- Main entry point
- Orchestrates snapshot creation and cleanup
- Returns detailed response with results

### 2. `create_snapshot(volume_id)`
- Creates new EBS snapshot
- Generates timestamped description
- Applies comprehensive tags
- Returns snapshot details

### 3. `cleanup_old_snapshots(volume_id, retention_days)`
- Lists all snapshots for specified volume
- Filters by automated backup prefix
- Deletes snapshots older than retention period
- Returns list of deleted snapshots

### 4. `list_all_snapshots(volume_id=None)`
- Helper function to list snapshots
- Optional volume filtering
- Returns completed snapshots only

---

## Best Practices

### 1. Snapshot Management
- **Regular Schedule:** Run daily or weekly based on data criticality
- **Retention Policy:** Balance cost vs. recovery requirements
- **Tagging Strategy:** Use consistent tags for tracking and cost allocation
- **Monitoring:** Set up CloudWatch alarms for snapshot failures

### 2. Security
- **Least Privilege:** Use minimal IAM permissions required
- **Encryption:** Enable EBS encryption for sensitive data
- **Cross-Region Copy:** Consider copying critical snapshots to another region
- **Access Control:** Restrict snapshot sharing to authorized accounts only

### 3. Cost Optimization
- **Lifecycle Management:** Delete old snapshots automatically
- **Incremental Backups:** EBS snapshots are incremental (only changed blocks)
- **Monitor Costs:** Track snapshot storage costs in Cost Explorer
- **Description Prefix:** Use prefix to differentiate automated vs. manual snapshots

### 4. Error Handling
- **Graceful Degradation:** Continue processing even if one snapshot fails
- **Logging:** Log all operations for troubleshooting
- **Notifications:** Set up SNS alerts for critical failures
- **Retry Logic:** Consider adding retry for transient failures

---

## Monitoring and Troubleshooting

### CloudWatch Metrics to Monitor
1. **Lambda Metrics:**
   - Invocations
   - Errors
   - Duration
   - Throttles

2. **Custom Metrics (Optional):**
   - Number of snapshots created
   - Number of snapshots deleted
   - Total snapshot storage size

### Common Issues

#### Issue 1: "Volume not found"
**Cause:** Incorrect volume ID or volume deleted
**Solution:** Verify volume ID in EC2 console

#### Issue 2: "Insufficient permissions"
**Cause:** Missing IAM permissions
**Solution:** Add required EC2 permissions to Lambda role

#### Issue 3: "Snapshot deletion failed"
**Cause:** Snapshot in use or insufficient permissions
**Solution:** Check if snapshot is being used for AMI or restore operations

#### Issue 4: No snapshots deleted
**Cause:** No snapshots older than retention period
**Solution:** Normal behavior if all snapshots are recent

---

## Cost Estimation

### EBS Snapshot Pricing (Example: US East)
- **Snapshot Storage:** ~$0.05 per GB-month
- **Lambda Execution:** Free tier covers most usage
- **Data Transfer:** Free within same region

### Example Calculation
- **Volume Size:** 100 GB
- **Daily Snapshots:** 30 snapshots retained
- **Incremental Change:** 5% daily (5 GB)
- **Approximate Cost:** $7.50/month for snapshots

**Note:** EBS snapshots are incremental, so only changed blocks are stored.

---

## Advanced Features

### Multi-Volume Backup
Modify the function to accept array of volume IDs:
```json
{
  "volume_ids": ["vol-123", "vol-456", "vol-789"],
  "retention_days": 30
}
```

### Cross-Region Snapshot Copy
Add functionality to copy snapshots to DR region:
```python
ec2_dr = boto3.client('ec2', region_name='us-west-2')
ec2_dr.copy_snapshot(
    SourceSnapshotId=snapshot_id,
    SourceRegion='us-east-1',
    Description='DR-Copy'
)
```

### SNS Notifications
Send notifications on success/failure:
```python
sns = boto3.client('sns')
sns.publish(
    TopicArn='arn:aws:sns:region:account:topic',
    Subject='EBS Snapshot Report',
    Message=f"Created: {len(created)}, Deleted: {len(deleted)}"
)
```

---

## Testing Checklist

- [ ] Lambda function creates snapshot successfully
- [ ] Snapshot has correct tags (Name, VolumeId, CreatedBy, BackupDate)
- [ ] Description follows naming pattern
- [ ] Old snapshots (>30 days) are deleted
- [ ] Manual snapshots (without prefix) are preserved
- [ ] CloudWatch logs show detailed execution
- [ ] IAM permissions are minimal and sufficient
- [ ] EventBridge rule triggers function on schedule
- [ ] Function handles errors gracefully
- [ ] Response includes all required details

---

## Security Best Practices

1. **Encryption:**
   - Enable EBS volume encryption
   - Snapshots automatically encrypted from encrypted volumes
   - Use customer-managed KMS keys for compliance

2. **Access Control:**
   - Limit snapshot sharing to trusted accounts
   - Use resource tags for access policies
   - Enable CloudTrail for audit logging

3. **Backup Verification:**
   - Periodically test snapshot restore process
   - Verify data integrity after restoration
   - Document recovery procedures

4. **Compliance:**
   - Follow data retention policies
   - Tag snapshots with compliance metadata
   - Automate compliance reporting

---

## Conclusion

This Lambda function provides:
- ✅ Automated EBS snapshot creation
- ✅ Intelligent retention management
- ✅ Cost-effective incremental backups
- ✅ Comprehensive tagging and logging
- ✅ Flexible configuration options
- ✅ Production-ready error handling

**Next Steps:**
1. Set up EventBridge rule for automated scheduling
2. Configure SNS notifications for alerts
3. Test snapshot restore procedures
4. Monitor costs and adjust retention as needed
5. Consider multi-region backup strategy for critical data

---

## Additional Resources

- [AWS EBS Snapshots Documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSSnapshots.html)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [EventBridge Scheduling](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-create-rule-schedule.html)
- [EBS Snapshot Pricing](https://aws.amazon.com/ebs/pricing/)
