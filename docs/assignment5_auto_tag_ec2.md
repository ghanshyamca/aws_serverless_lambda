# Assignment 5: Auto-Tagging EC2 Instances on Launch

## Objective
Automatically tag newly launched EC2 instances with current date and custom tags using AWS Lambda, CloudWatch Events (EventBridge), and Boto3.

## Overview
This solution creates an event-driven architecture that:
- Detects EC2 instance launch events
- Automatically applies tags to new instances
- Ensures consistent tagging across infrastructure
- Improves resource tracking and cost allocation

---

## Prerequisites
- AWS Account with EC2 and Lambda access
- Understanding of CloudWatch Events (EventBridge)
- Ability to launch EC2 instances

---

## Step-by-Step Implementation

### Step 1: Create IAM Role for Lambda

1. **IAM Console** → **Roles** → **Create Role**
2. Select **AWS Service** → **Lambda**
3. Attach policies:
   - `AmazonEC2FullAccess` (for demo)
   - `CloudWatchLogsFullAccess`

4. Name: `Lambda-EC2-AutoTag-Role`

**Production Policy (Least Privilege):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:CreateTags",
        "ec2:DescribeTags"
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

**Screenshot:** `screenshots/assignment5_iam_role.png`

---

### Step 2: Create Lambda Function

1. **Lambda Console** → **Create Function**
2. Configuration:
   - **Function name:** `EC2-Auto-Tag`
   - **Runtime:** Python 3.11 or 3.12
   - **Architecture:** x86_64
   - **Execution role:** `Lambda-EC2-AutoTag-Role`

3. Click **Create Function**

**Screenshot:** `screenshots/assignment5_lambda_create.png`

---

### Step 3: Add Lambda Code

1. In **Code** tab, replace with:
   - `lambda_functions/assignment5_auto_tag_ec2.py`

2. **Optional:** Customize tags in the code:
   ```python
   CUSTOM_TAGS = {
       'ManagedBy': 'Lambda',
       'AutoTagged': 'True',
       'Environment': 'Development',  # Change as needed
       'Project': 'AWS-Serverless-Lambda',
       'Owner': 'DevOps-Team'  # Add your team
   }
   ```

3. Click **Deploy**

**Key Features:**
- Extracts instance ID from CloudWatch Event
- Retrieves instance details
- Applies launch date and custom tags
- Handles multiple event formats
- Comprehensive error handling

**Screenshot:** `screenshots/assignment5_lambda_code.png`

---

### Step 4: Configure Lambda Settings

1. **Configuration** → **General Configuration**
   - **Timeout:** 30 seconds
   - **Memory:** 128 MB

**Screenshot:** `screenshots/assignment5_lambda_config.png`

---

### Step 5: Create EventBridge Rule

This is the key step that makes the function event-driven!

1. **EventBridge Console** → **Rules** → **Create Rule**

2. **Step 1: Define rule detail**
   - **Name:** `EC2-Instance-Launch-Trigger`
   - **Description:** `Trigger Lambda when EC2 instance enters running state`
   - **Event bus:** default
   - **Rule type:** Rule with an event pattern

3. **Step 2: Build event pattern**
   - **Event source:** AWS events
   - **Sample event:** AWS events (optional)
   - **Event pattern:**
   
   ```json
   {
     "source": ["aws.ec2"],
     "detail-type": ["EC2 Instance State-change Notification"],
     "detail": {
       "state": ["running"]
     }
   }
   ```

4. **Step 3: Select targets**
   - **Target types:** AWS service
   - **Select a target:** Lambda function
   - **Function:** `EC2-Auto-Tag`

5. **Step 4: Configure tags** (optional)
   - Add tags for the rule itself

6. **Step 5: Review and create**
   - Review settings
   - Click **Create rule**

**Screenshot:** `screenshots/assignment5_eventbridge_rule.png`

---

### Step 6: Test by Launching an EC2 Instance

Now test the automated tagging:

1. **EC2 Console** → **Launch Instance**
2. Configuration:
   - **Name:** `Test-AutoTag-Instance`
   - **AMI:** Amazon Linux 2023 (or any free-tier AMI)
   - **Instance type:** t2.micro
   - **Key pair:** Select or create
   - **Network settings:** Default VPC
   - **Do NOT manually add tags** (we want to see auto-tagging work)

3. Click **Launch Instance**

**Screenshot:** `screenshots/assignment5_ec2_launch.png`

---

### Step 7: Verify Auto-Tagging

Wait 1-2 minutes for the instance to enter "running" state, then:

1. **EC2 Console** → **Instances**
2. Select your newly launched instance
3. Click **Tags** tab
4. Verify the following tags were automatically added:
   - `LaunchDate`: 2026-01-03
   - `LaunchDateTime`: 2026-01-03 10:30:00 UTC
   - `ManagedBy`: Lambda
   - `AutoTagged`: True
   - `Environment`: Development
   - `Project`: AWS-Serverless-Lambda
   - `InstanceType`: t2.micro

**Screenshot:** `screenshots/assignment5_ec2_tags.png`

---

### Step 8: Review CloudWatch Logs

1. **CloudWatch** → **Log groups** → `/aws/lambda/EC2-Auto-Tag`
2. View latest log stream

**Sample Log Output:**
```
Lambda function started at 2026-01-03T10:30:15.000000
Event received: {
  "version": "0",
  "id": "12345678-1234-1234-1234-123456789012",
  "detail-type": "EC2 Instance State-change Notification",
  "source": "aws.ec2",
  "account": "123456789012",
  "time": "2026-01-03T10:30:00Z",
  "region": "us-east-1",
  "resources": ["arn:aws:ec2:us-east-1:123456789012:instance/i-0abcd1234efgh5678"],
  "detail": {
    "instance-id": "i-0abcd1234efgh5678",
    "state": "running"
  }
}
Processing instance: i-0abcd1234efgh5678
Instance details: {
  "InstanceId": "i-0abcd1234efgh5678",
  "InstanceType": "t2.micro",
  "State": "running",
  "LaunchTime": "2026-01-03T10:29:45+00:00",
  "AvailabilityZone": "us-east-1a",
  "PrivateIpAddress": "172.31.10.20",
  "PublicIpAddress": "54.123.45.67"
}
Tags applied: {
  "LaunchDate": "2026-01-03",
  "LaunchDateTime": "2026-01-03 10:30:15 UTC",
  "ManagedBy": "Lambda",
  "AutoTagged": "True",
  "Environment": "Development",
  "Project": "AWS-Serverless-Lambda",
  "InstanceType": "t2.micro"
}
Successfully tagged instance i-0abcd1234efgh5678
```

**Screenshot:** `screenshots/assignment5_cloudwatch_logs.png`

---

### Step 9: Review EventBridge Metrics

1. **EventBridge Console** → **Rules** → `EC2-Instance-Launch-Trigger`
2. Click **Monitoring** tab
3. View metrics:
   - Invocations
   - TriggeredRules
   - Failures

**Screenshot:** `screenshots/assignment5_eventbridge_metrics.png`

---

## Event Pattern Variations

### Trigger on Multiple States

Trigger on both `running` and `stopped` states:

```json
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"],
  "detail": {
    "state": ["running", "stopped"]
  }
}
```

### Trigger for Specific Instance Types

Only tag t2.micro instances:

```json
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"],
  "detail": {
    "state": ["running"],
    "instance-type": ["t2.micro"]
  }
}
```

---

## Advanced Tagging Strategies

### Dynamic Tags Based on Instance Properties

Modify Lambda to add tags based on instance attributes:

```python
def create_tags(instance_id, instance_details):
    # ... existing code ...
    
    # Add tag based on instance type
    if 't2.' in instance_details['InstanceType']:
        tags.append({'Key': 'CostCenter', 'Value': 'Development'})
    else:
        tags.append({'Key': 'CostCenter', 'Value': 'Production'})
    
    # Add AZ tag
    az = instance_details['AvailabilityZone']
    tags.append({'Key': 'AZ', 'Value': az})
    
    # ... rest of code ...
```

### Tag Based on Existing Tags

Check for existing tags and add complementary ones:

```python
existing_tags = get_existing_tags(instance_id)

if 'Environment' not in existing_tags:
    tags.append({'Key': 'Environment', 'Value': 'Unclassified'})
```

---

## Testing Scenarios

### Test Case 1: New Instance Launch
1. Launch new EC2 instance
2. Wait for "running" state
3. Verify tags are applied automatically

### Test Case 2: Instance with Existing Tags
1. Launch instance with manual tags
2. Verify Lambda adds additional tags
3. Ensure no tag conflicts

### Test Case 3: Multiple Instances
1. Launch multiple instances simultaneously
2. Verify all instances are tagged
3. Check CloudWatch logs for all executions

### Test Case 4: Manual Invocation
Create test event for manual testing:

```json
{
  "detail": {
    "instance-id": "i-0123456789abcdef0"
  }
}
```

---

## Troubleshooting

### Issue: Tags Not Applied
**Problem:** Instance launched but no tags appear

**Solutions:**
- Check EventBridge rule is **Enabled**
- Verify Lambda has EC2 tagging permissions
- Review CloudWatch logs for errors
- Ensure instance entered "running" state
- Check event pattern matches the event

### Issue: Lambda Not Triggered
**Problem:** Instance launched but Lambda didn't execute

**Solutions:**
- Verify EventBridge rule exists and is enabled
- Check Lambda function is set as target
- Review EventBridge metrics
- Ensure instance is in the same region as Lambda

### Issue: Permission Denied
**Error:** `User: arn:aws:sts::... is not authorized to perform: ec2:CreateTags`

**Solutions:**
- Update IAM role with EC2 tagging permissions
- Check trust relationship allows Lambda to assume role

---

## Cost Considerations

- **Lambda:** Free tier covers 1M requests/month
- **EventBridge:** Free for AWS service events
- **CloudWatch Logs:** Free tier includes 5 GB

**Estimated Cost:** $0/month for typical usage (within free tier)

---

## Use Cases

### 1. Cost Allocation
Auto-tag instances with cost center, project, and owner for billing reports

### 2. Compliance
Ensure all instances have required compliance tags

### 3. Automation
Tag instances for automated backup, patching, or shutdown policies

### 4. Resource Tracking
Track when resources were created and by whom

---

## Security Best Practices

1. ✅ Use least-privilege IAM policies
2. ✅ Enable CloudTrail for audit logging
3. ✅ Review Lambda logs regularly
4. ✅ Test on development instances first
5. ✅ Implement tag validation
6. ✅ Consider tag immutability for critical tags

---

## Extensions

### Add SNS Notification

Send notification when instances are tagged:

```python
import boto3
sns = boto3.client('sns')

sns.publish(
    TopicArn='arn:aws:sns:region:account:InstanceTagging',
    Subject='EC2 Instance Auto-Tagged',
    Message=f'Instance {instance_id} was auto-tagged with {len(tags)} tags'
)
```

### Tag Related Resources

Also tag volumes, network interfaces:

```python
# Tag attached volumes
volumes = instance_details.get('BlockDeviceMappings', [])
for volume in volumes:
    volume_id = volume['Ebs']['VolumeId']
    ec2.create_tags(Resources=[volume_id], Tags=tags)
```

---

## Cleanup

To remove the automation:

1. Disable or delete EventBridge rule
2. Delete Lambda function
3. Delete IAM role
4. Terminate test EC2 instances
5. Delete CloudWatch log groups

---

## Conclusion

This assignment demonstrates:
- ✅ Event-driven architecture with EventBridge
- ✅ Automated resource tagging
- ✅ Infrastructure governance
- ✅ CloudWatch Events integration
- ✅ Real-time automation

**Key Learnings:**
- EventBridge event patterns
- Event-driven Lambda functions
- EC2 tagging with Boto3
- Automated compliance and governance
- AWS service integration patterns
