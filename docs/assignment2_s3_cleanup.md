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

**Screenshot:** 
<img width="1920" height="2651" alt="step 1  Create-S3-bucket-S3-us-east-1-01-03-2026_08_37_PM" src="https://github.com/user-attachments/assets/c4bf5494-cc45-4c3a-a1df-1cd27ef8e926" />

<img width="1920" height="912" alt="step 2   s3 bucket ghanshyam-cleanup-bucket-S3-bucket-S3-us-east-1-01-03-2026_08_49_PM" src="https://github.com/user-attachments/assets/161effda-1e10-4711-996d-95758a3a8730" />

---

### Step 2: Upload Test Files

Upload multiple files to simulate different ages:

**Method 1: Using AWS Console**
1. Open your bucket
2. Click **Upload**
3. Add files
4. Upload

**Note:** For actual testing, you may need to use files that are genuinely old, or adjust your system date temporarily.

**Screenshot:** 
<img width="1920" height="912" alt="step 3  file uploaded" src="https://github.com/user-attachments/assets/e2e31375-3104-405d-a4c0-152f14683889" />


---

### Step 3: Create IAM Role for Lambda

1. Go to **IAM Console** → **Roles** → **Create Role**
2. Select **AWS Service** → **Lambda**
3. Attach policies:
   - `AmazonS3FullAccess` (for demo)
   - `CloudWatchLogsFullAccess` (for logging)

**Screenshot:**
<img width="1920" height="1267" alt="step 4  create IAM role ghanshyam_lamdba-IAM-Global-01-03-2026_08_55_PM" src="https://github.com/user-attachments/assets/8d1d140b-bbb5-4c41-a464-6c32a1214281" />


---

### Step 4: Create Lambda Function

1. **Lambda Console** → **Create Function**
2. Configuration:
   - **Function name:** `S3-Cleanup-Old-Files`
   - **Runtime:** Python 3.11 or 3.12
   - **Architecture:** x86_64
   - **Execution role:** `Lambda-S3-Cleanup-Role`

3. Click **Create Function**

**Screenshot:**
<img width="1920" height="1461" alt="step 5 2 Create-function-Functions-Lambda-01-03-2026_09_25_PM" src="https://github.com/user-attachments/assets/169466c6-7b69-43a3-9d1f-40398a282a74" />


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

**Screenshot:** 
<img width="1920" height="2278" alt="Step 6  code ghanshyam_lamdba-Functions-Lambda-01-03-2026_09_26_PM" src="https://github.com/user-attachments/assets/612c11b0-9097-4823-b231-74565aa274b6" />


---

### Step 6: Test the Lambda Function

1. Click **Test** tab

**Expected Results:**
- Files older than 30 days are deleted
- Recent files remain in bucket
- Detailed log shows which files were deleted

**Screenshot:** 
<img width="1920" height="2898" alt="step 7  delete files successfull ghanshyam_lamdba-Functions-Lambda-01-03-2026_11_08_PM" src="https://github.com/user-attachments/assets/8532529f-b289-4f41-ae26-bd94d2c93cf1" />


---

### Step 7: Verify S3 Bucket

1. Go to **S3 Console**
2. Open your bucket
3. Confirm only files newer than 30 days remain

**Screenshot:** 
<img width="1920" height="912" alt="step 8   ghanshyam-cleanup-bucket-S3-bucket-S3-us-east-1-01-03-2026_11_11_PM" src="https://github.com/user-attachments/assets/966a01b2-d09a-4f41-8601-1f873155ab58" />

---
