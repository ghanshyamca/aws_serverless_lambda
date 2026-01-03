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

**Screenshot:** 
<img width="1920" height="912" alt="step 1  Launch-an-instance-EC2-us-east-1-01-03-2026_07_32_PM" src="https://github.com/user-attachments/assets/32e70d01-dfbe-49db-9b84-6744bb81bd2a" />
<img width="1920" height="912" alt="step 2  Added tag" src="https://github.com/user-attachments/assets/22f9ffd2-3566-41ee-9487-c80e4c08da30" />
<img width="1920" height="912" alt="step 3  Launch stop ec2 Instance-details-EC2-us-east-1-01-03-2026_07_38_PM" src="https://github.com/user-attachments/assets/90216d2c-c37a-4c4f-ac5a-34d0c7138b41" />
<img width="1920" height="912" alt="step 4  Added tag Instances-EC2-us-east-1-01-03-2026_07_41_PM" src="https://github.com/user-attachments/assets/77b8a093-eb30-4393-a884-5b58b8be0918" />


### Step 2: Create IAM Role for Lambda

1. Go to **IAM Console** → **Roles** → **Create Role**
2. Select **AWS Service** → **Lambda**
3. Attach the following policies:
   - `AmazonEC2FullAccess` (for demo purposes)
   - `CloudWatchLogsFullAccess` (for logging)

**Screenshot:** 
<img width="1920" height="1265" alt="step 5  ghanshyam_lamdba-IAM-Global-01-03-2026_07_46_PM" src="https://github.com/user-attachments/assets/3ceba505-2d78-4c61-9290-ae728b94a4de" />

---

### Step 3: Create Lambda Function

1. Navigate to **Lambda Console** → **Create Function**
2. Configuration:
   - **Function name:** `EC2-Auto-Management`
   - **Runtime:** Python 3.14
   - **Architecture:** x86_64
   - **Execution role:** Use existing created role

3. Click **Create Function**

**Screenshot:** 
<img width="1920" height="2278" alt="step 6   created lamdba function ghanshyam_lamdba_ec2-Functions-Lambda-01-03-2026_07_48_PM" src="https://github.com/user-attachments/assets/1bf27eb4-666c-4193-a49b-e646201da563" />

<img width="1920" height="2278" alt="Step 6 1 create lamdba function ghanshyam_lamdba_ec2-Functions-Lambda-01-03-2026_07_53_PM" src="https://github.com/user-attachments/assets/a95f1f9b-08fb-47a8-8369-de68dee92a1c" />

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

**Screenshot:** 
<img width="1920" height="912" alt="step 7  execution lamdba sucessfull" src="https://github.com/user-attachments/assets/2881edc5-ccbd-41cf-90ba-b9aa0650248a" />


---

### Step 5: Test the Lambda Function

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

**Screenshot:** 
<img width="1920" height="912" alt="step 8  CloudWatch-us-east-1-01-03-2026_08_11_PM" src="https://github.com/user-attachments/assets/ac099b6c-d0c9-44d1-9e18-180b5f1183ad" />


---

### Step 6: Verify EC2 Instance States

1. Go to **EC2 Dashboard** → **Instances**
2. Check the state of both instances:
   - `Auto-Stop-Instance` should be **Stopped** (or **Stopping**)
   - `Auto-Start-Instance` should be **Running** (or **Pending**)

**Screenshot:** 
<img width="1920" height="912" alt="Step 9  Instances-EC2-us-east-1-01-03-2026_08_15_PM" src="https://github.com/user-attachments/assets/7d2c474f-e420-41d7-b321-85d647c0b9c6" />


---
