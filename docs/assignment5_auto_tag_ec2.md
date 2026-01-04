# Assignment 5: Auto-Tagging EC2 Instances on Launch

## Objective
Automatically tag newly launched EC2 instances with current date and custom tags using AWS Lambda, CloudWatch Events (EventBridge), and Boto3.

## Step-by-Step Implementation

### Step 1: Create IAM Role for Lambda

1. **IAM Console** → **Roles** → **Create Role**
2. Select **AWS Service** → **Lambda**
3. Attach policies:
   - `AmazonEC2FullAccess` (for demo)
   - `CloudWatchLogsFullAccess`

4. Name: `Lambda-EC2-AutoTag-Role`

**Screenshot:** 
<img width="1920" height="1160" alt="Step 1  IAM role ghanshyam_lamdba-IAM-Global-01-04-2026_12_36_PM" src="https://github.com/user-attachments/assets/a41e0942-2d5a-4335-921f-fb71508dbf4c" />

---

### Step 2: Create Lambda Function

1. **Lambda Console** → **Create Function**
2. Configuration:
   - **Function name:** `EC2-Auto-Tag`
   - **Runtime:** Python 3.14
   - **Architecture:** x86_64
   - **Execution role:** `Lambda-EC2-AutoTag-Role`

3. Click **Create Function**

**Screenshot:**
<img width="1920" height="1461" alt="step 2  Create-function-Functions-Lambda-01-04-2026_12_38_PM" src="https://github.com/user-attachments/assets/4dd084da-8da7-451c-9cc1-23fd555ecba4" />

<img width="1920" height="2278" alt="step 3  ghanshyam_ec2_auto_tag-Functions-Lambda-01-04-2026_12_39_PM" src="https://github.com/user-attachments/assets/e72425b2-ffa6-488e-8a77-d8e97e64353f" />



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

**Screenshot:** 
<img width="1920" height="2278" alt="step 4  ghanshyam_ec2_auto_tag-Functions-Lambda-01-04-2026_12_41_PM" src="https://github.com/user-attachments/assets/16f0b99e-aff4-4dda-8ab4-6869f4cbedd6" />


---

### Step 4: Create EventBridge Rule

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

**Screenshot:** 
<img width="1920" height="1657" alt="step 5  Add-triggers-Lambda-01-04-2026_12_45_PM" src="https://github.com/user-attachments/assets/bef5328a-f1c8-459a-b460-96f45a8c217d" />


---

### Step 5: Test by Launching an EC2 Instance

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

**Screenshot:** 
<img width="1920" height="912" alt="step 6 1 Launch-an-instance-EC2-us-east-1-01-04-2026_12_55_PM" src="https://github.com/user-attachments/assets/3e348fc3-d7f9-41ba-aa65-1a7e6ce32f05" />
<img width="1920" height="912" alt="step 7 1 Instance-details-EC2-us-east-1-01-04-2026_12_56_PM" src="https://github.com/user-attachments/assets/4faa91e8-ad71-44df-8b0a-88bf18c6a05d" />



---

### Step 6: Verify Auto-Tagging

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

**Screenshot:** 
<img width="1920" height="912" alt="step 8 3 Instance-details-EC2-us-east-1-01-04-2026_01_01_PM" src="https://github.com/user-attachments/assets/7d70ae21-c537-4954-bc3e-5554b0d96995" />


---

### Step 7: Review CloudWatch Logs

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

**Screenshot:** 
<img width="1920" height="912" alt="step 8 1 CloudWatch-us-east-1-01-04-2026_12_59_PM" src="https://github.com/user-attachments/assets/818c6f53-40c6-43ce-b7d7-b9eaa26817c2" />

<img width="1920" height="912" alt="step 8 2 CloudWatch-us-east-1-01-04-2026_01_00_PM" src="https://github.com/user-attachments/assets/94734bb3-f4d6-419d-ae32-52bc7939cc74" />



---
