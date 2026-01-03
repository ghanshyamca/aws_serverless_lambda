# Assignment 1: Automated Instance Management Using AWS Lambda and Boto3

## Objective
Automate the stopping and starting of EC2 instances based on tags using AWS Lambda and Boto3.

## Overview
This Lambda function automatically manages EC2 instances by:
- Stopping instances tagged with `Action=Auto-Stop`
- Starting instances tagged with `Action=Auto-Start`

---

## Prerequisites
- AWS Account with appropriate permissions
- Basic understanding of AWS EC2 and Lambda
- AWS CLI configured (optional, for testing)

---

## Step-by-Step Implementation

### Step 1: Create EC2 Instances

1. Navigate to **EC2 Dashboard** in AWS Console
2. Click **Launch Instance**
3. Create two **t2.micro** instances (Free Tier eligible)

**First Instance (Auto-Stop):**
- Name: `Auto-Stop-Instance`
- Tags: 
  - Key: `Action`, Value: `Auto-Stop`
  - Key: `Name`, Value: `Auto-Stop-Instance`

**Second Instance (Auto-Start):**
- Name: `Auto-Start-Instance`
- Tags:
  - Key: `Action`, Value: `Auto-Start`
  - Key: `Name`, Value: `Auto-Start-Instance`

**Screenshot:** `screenshots/assignment1_ec2_instances.png`
- Shows both instances with their respective tags

---

### Step 2: Create IAM Role for Lambda

1. Go to **IAM Console** → **Roles** → **Create Role**
2. Select **AWS Service** → **Lambda**
3. Attach the following policies:
   - `AmazonEC2FullAccess` (for demo purposes)
   - `CloudWatchLogsFullAccess` (for logging)

4. Name the role: `Lambda-EC2-AutoManagement-Role`

**Best Practice:** In production, create a custom policy with minimal permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:StopInstances",
        "ec2:StartInstances",
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

**Screenshot:** `screenshots/assignment1_iam_role.png`

---

### Step 3: Create Lambda Function

1. Navigate to **Lambda Console** → **Create Function**
2. Configuration:
   - **Function name:** `EC2-Auto-Management`
   - **Runtime:** Python 3.11 or 3.12
   - **Architecture:** x86_64
   - **Execution role:** Use existing role → `Lambda-EC2-AutoManagement-Role`

3. Click **Create Function**

**Screenshot:** `screenshots/assignment1_lambda_create.png`

---

### Step 4: Add Lambda Code

1. In the Lambda function **Code** tab
2. Replace the default code with the contents of:
   - `lambda_functions/assignment1_ec2_auto_management.py`

3. Click **Deploy**

**Key Features of the Code:**
- Uses boto3 EC2 client
- Filters instances by tag `Action=Auto-Stop` and `Action=Auto-Start`
- Checks current instance state before performing actions
- Logs all operations for monitoring
- Returns detailed response with affected instances

**Screenshot:** `screenshots/assignment1_lambda_code.png`

---

### Step 5: Configure Lambda Settings (Optional)

1. **Configuration** → **General Configuration**
   - Timeout: 30 seconds (sufficient for EC2 operations)
   - Memory: 128 MB (default is adequate)

2. **Environment Variables** (optional):
   - Can add variables to customize behavior without code changes

---

### Step 6: Test the Lambda Function

1. Click **Test** tab
2. Create a new test event:
   - **Event name:** `TestEC2Management`
   - **Event JSON:**
   ```json
   {
     "test": "manual_invocation"
   }
   ```

3. Click **Test** button

**Expected Results:**
- Instance with `Auto-Stop` tag → Stopped
- Instance with `Auto-Start` tag → Started
- CloudWatch logs show detailed execution

**Screenshot:** `screenshots/assignment1_test_result.png`

---

### Step 7: Verify EC2 Instance States

1. Go to **EC2 Dashboard** → **Instances**
2. Check the state of both instances:
   - `Auto-Stop-Instance` should be **Stopped** (or **Stopping**)
   - `Auto-Start-Instance` should be **Running** (or **Pending**)

**Screenshot:** `screenshots/assignment1_ec2_states.png`

---

### Step 8: Review CloudWatch Logs

1. Go to **CloudWatch** → **Log groups**
2. Find log group: `/aws/lambda/EC2-Auto-Management`
3. View latest log stream

**Sample Log Output:**
```
Lambda function started at 2026-01-03T10:30:00.000000
Searching for instances with Action=Auto-Stop tag...
Found 1 instance(s) to stop: ['i-0123456789abcdef0']
Stopped instance: i-0123456789abcdef0 (Previous: running, Current: stopping)
Searching for instances with Action=Auto-Start tag...
Found 1 instance(s) to start: ['i-0123456789abcdef1']
Started instance: i-0123456789abcdef1 (Previous: stopped, Current: pending)
Lambda function completed successfully
Summary: Stopped 1 instance(s), Started 1 instance(s)
```

**Screenshot:** `screenshots/assignment1_cloudwatch_logs.png`

---

## Optional Enhancements

### Schedule with EventBridge (CloudWatch Events)

To run this function automatically (e.g., every day at 6 PM to stop instances):

1. Go to **EventBridge** → **Rules** → **Create Rule**
2. Configuration:
   - **Name:** `EC2-AutoStop-Daily`
   - **Rule type:** Schedule
   - **Schedule pattern:** `cron(0 18 * * ? *)`  # 6 PM UTC daily
   - **Target:** Lambda function → `EC2-Auto-Management`

**Screenshot:** `screenshots/assignment1_eventbridge_schedule.png`

---

## Testing Scenarios

### Test Case 1: Stop Running Instance
1. Ensure `Auto-Stop-Instance` is **Running**
2. Invoke Lambda function
3. Verify instance is **Stopped**

### Test Case 2: Start Stopped Instance
1. Ensure `Auto-Start-Instance` is **Stopped**
2. Invoke Lambda function
3. Verify instance is **Running**

### Test Case 3: No Action Needed
1. Ensure `Auto-Stop-Instance` is already **Stopped**
2. Ensure `Auto-Start-Instance` is already **Running**
3. Invoke Lambda function
4. Verify no state changes occur (logged in CloudWatch)

---

## Troubleshooting

### Issue: Permission Denied
**Error:** `An error occurred (UnauthorizedOperation)`

**Solution:** 
- Verify IAM role has EC2 permissions
- Check role is attached to Lambda function

### Issue: Instance Not Found
**Error:** No instances found with tags

**Solution:**
- Verify EC2 instances have correct tags (case-sensitive)
- Check instance is in the same region as Lambda function

### Issue: Lambda Timeout
**Error:** Task timed out after X seconds

**Solution:**
- Increase Lambda timeout (Configuration → General)
- Check for too many instances being processed

---

## Cost Considerations

- **Lambda:** First 1M requests/month are free
- **EC2:** Running hours reduced by auto-stopping instances
- **CloudWatch Logs:** Free tier includes 5 GB ingestion

**Estimated Monthly Savings:**
- Stopping instances for 12 hours/day can save ~50% on EC2 costs

---

## Security Best Practices

1. ✅ Use least-privilege IAM policies
2. ✅ Enable CloudTrail for audit logging
3. ✅ Use specific resource ARNs when possible
4. ✅ Encrypt environment variables
5. ✅ Review Lambda function logs regularly

---

## Cleanup

To avoid ongoing charges:

1. Delete Lambda function
2. Delete IAM role
3. Terminate EC2 instances
4. Delete CloudWatch log groups
5. Delete EventBridge rules (if created)

---

## Conclusion

This assignment demonstrates:
- ✅ Automated EC2 instance management
- ✅ Tag-based resource control
- ✅ AWS Lambda with Boto3
- ✅ Infrastructure automation
- ✅ Cost optimization strategies

**Key Learnings:**
- Event-driven automation
- AWS SDK (Boto3) usage
- IAM role configuration
- CloudWatch monitoring
