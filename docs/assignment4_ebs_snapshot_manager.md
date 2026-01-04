# Assignment 4: Automatic EBS Snapshot and Cleanup Using AWS Lambda and Boto3

## Objective
Automate the creation of EBS volume snapshots and cleanup of old snapshots (older than 30 days) using AWS Lambda and Boto3.

### Step 1: Identify EBS Volume

1. Navigate to **EC2 Console** → **Volumes**
2. Identify the volume you want to backup
3. Note the **Volume ID** (e.g., `vol-08d770f6336866caf`)
4. Verify the volume state is `in-use` or `available`

**screenshot**
<img width="1920" height="912" alt="step 1  Create-volume-EC2-us-east-1-01-04-2026_11_32_AM" src="https://github.com/user-attachments/assets/8c2ee05e-7d6a-4737-8ec7-3ee6e0f47776" />

<img width="1920" height="912" alt="step 2  Volume-details-EC2-us-east-1-01-04-2026_11_35_AM" src="https://github.com/user-attachments/assets/ef7c86bd-d430-4872-9094-d26038e3c0e6" />


---

### Step 2: Create IAM Role for Lambda

1. Go to **IAM Console** → **Roles** → **Create Role**
2. Select **AWS Service** → **Lambda**
3. Create a custom policy or attach these managed policies:
   - `AmazonEC2ReadOnlyAccess`

4. **Role name:** `ghanshyam_lamdba`
5. Click **Create Role**

**screenshot**
<img width="1920" height="1160" alt="step 3  IAM role createdghanshyam_lamdba-IAM-Global-01-04-2026_11_37_AM" src="https://github.com/user-attachments/assets/80446b91-68e3-464d-986c-53181e8a6890" />


---

### Step 3: Create Lambda Function

1. **Lambda Console** → **Create Function**
2. Configuration:
   - **Function name:** `EBS-Snapshot-Manager`
   - **Runtime:** Python 3.14
   - **Architecture:** x86_64
   - **Execution role:** Use existing role → `ghanshyam_lambda`

3. Click **Create Function**

**screenshot**
<img width="1920" height="1461" alt="Step 4  Create-function-Functions-Lambda-01-04-2026_11_39_AM" src="https://github.com/user-attachments/assets/bef85b8d-f9a1-457b-bc97-97d2e3924170" />

<img width="1920" height="2215" alt="step 5  ghanshyam_lamdba-Functions-Lambda-01-04-2026_11_41_AM" src="https://github.com/user-attachments/assets/c7c6eda5-589a-414b-b2e9-af291ae755df" />



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
**screenshot**
<img width="1920" height="2215" alt="step 6  code ghanshyam_lamdba-Functions-Lambda-01-04-2026_11_42_AM" src="https://github.com/user-attachments/assets/261b77cd-d566-4e22-9706-fce078e88fdb" />


### Step 6: Added the EventBridge CloudWatch
<img width="1920" height="912" alt="step 9 Add-triggers-Lambda-01-04-2026_11_50_AM" src="https://github.com/user-attachments/assets/98f86324-46bf-4aee-b00f-04a90d880769" />
<img width="1920" height="912" alt="step 10  ghanshyam_lamdba-Functions-Lambda-01-04-2026_11_51_AM" src="https://github.com/user-attachments/assets/78e61ee2-aa19-4ba5-9917-3915bc35f579" />


### Step 5: Test the Lambda Function

**screenshot**
<img width="1920" height="2835" alt="step 7  executed successfull ghanshyam_lamdba-Functions-Lambda-01-04-2026_11_44_AM" src="https://github.com/user-attachments/assets/1ab35982-9ba1-46ea-8ec3-80510bbe755b" />

<img width="1920" height="912" alt="step 8  Snapshots-EC2-us-east-1-01-04-2026_11_45_AM" src="https://github.com/user-attachments/assets/fb10fa03-1100-4213-9546-7951b27f2603" />

