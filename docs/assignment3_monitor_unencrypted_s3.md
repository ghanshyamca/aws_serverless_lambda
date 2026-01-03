# Assignment 3: Monitor Unencrypted S3 Buckets Using AWS Lambda and Boto3


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

**screenshot**
<img width="1213" height="83" alt="step 1  S3-buckets-S3-us-east-1-01-03-2026_11_39_PM" src="https://github.com/user-attachments/assets/d1d08dec-7dce-430d-b0a8-92c3c9138b48" />


### Step 2: Create IAM Role for Lambda

**2.1 Create IAM Role**

1. Go to **IAM Console** → **Roles**
2. Click **Create role**
3. Select **AWS service** → **Lambda**
4. Click **Next**

**2.2 Attach Policies**

Attach the following managed policy:
- ✅ `AmazonS3ReadOnlyAccess`


**2.3 Name the Role**
- Role name: `Lambda-S3-Encryption-Monitor`
- Click **Create role**

**screenshot**
<img width="1920" height="1223" alt="step 2  create IAM role ghanshyam_lamdba-IAM-Global-01-03-2026_11_41_PM" src="https://github.com/user-attachments/assets/dfd09165-592f-403f-8941-da9336d65c52" />

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

**screenshot**
<img width="1920" height="1461" alt="step 3  Create-function-Functions-Lambda-01-03-2026_11_42_PM" src="https://github.com/user-attachments/assets/35d7e3be-6044-4a3e-9404-c0eff04e84b1" />

<img width="1920" height="2278" alt="step 4  ghanshyam-lamdba-Functions-Lambda-01-03-2026_11_43_PM" src="https://github.com/user-attachments/assets/21975d81-a555-4faf-a38f-1b64a12a959a" />



**3.2 Upload Function Code**

1. In the **Code** tab, delete default code
2. Copy contents from `lambda_functions/assignment3_monitor_unencrypted_s3.py`
3. Paste into the Lambda editor
4. Click **Deploy**

**screenshot**
<img width="1920" height="2278" alt="step 5  create code ghanshyam-lamdba-Functions-Lambda-01-03-2026_11_44_PM" src="https://github.com/user-attachments/assets/de63cd62-6914-43a8-b10d-514540db8bab" />


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
  "body": "{\"total_buckets\": 4, \"unencrypted_buckets\": [\"ghanshyam-no-encryption-1\", \"ghanshyam-no-encryption-2\", \"ghanshyam-unencrypted-test\", \"ghanshyam-test-no-sse\"], \"encrypted_buckets\": [], \"errors\": []}"
}
```
**screenshot**
<img width="1920" height="2817" alt="step 6  check for encrypted file ghanshyam-lamdba-Functions-Lambda-01-04-2026_12_20_AM" src="https://github.com/user-attachments/assets/4fdaf7e3-acb0-4a71-9ceb-b158e264323c" />

