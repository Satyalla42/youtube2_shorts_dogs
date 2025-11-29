# GitHub Setup Instructions

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `youtube-creativecommons-shorts` (or your preferred name)
3. Description: "Automated YouTube Creative Commons Shorts Reuploader"
4. Choose Public or Private
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 2: Push Code to GitHub

Run these commands in your terminal:

```bash
# Add the remote repository (replace YOUR_USERNAME and YOUR_REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Set Up GitHub Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

### Add CLIENT_SECRET_JSON:
- Name: `CLIENT_SECRET_JSON`
- Value: Copy the entire contents of your `client_secret_*.json` file
- Click **Add secret**

### Add TOKEN_JSON:
- Name: `TOKEN_JSON`
- Value: Copy the entire contents of your `token.json` file (generate it first using `python3 generate_token.py` locally)
- Click **Add secret**

### Add YOUTUBE_COOKIES (Optional but Recommended):
- Name: `YOUTUBE_COOKIES`
- Value: Export cookies from your browser:
  ```bash
  # Using yt-dlp to export cookies from Chrome
  yt-dlp --cookies-from-browser chrome --print-to-file cookies.txt ""
  # Or manually export using a browser extension like "Get cookies.txt LOCALLY"
  ```
  Then copy the entire contents of `cookies.txt` to the secret
- Click **Add secret**
  
  **Note:** This helps avoid YouTube bot detection. Without cookies, downloads may fail more often.

## Step 4: Enable GitHub Actions

1. Go to **Actions** tab in your repository
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. The workflow will automatically run twice per day at:
   - 9:00 AM UTC
   - 9:00 PM UTC

## Step 5: Test the Workflow

1. Go to **Actions** tab
2. Click on **"Upload Creative Commons Shorts"** workflow
3. Click **"Run workflow"** → **"Run workflow"** (manual trigger)
4. Watch it run and check the logs

## Troubleshooting

**Workflow fails with "No client secret file found":**
- Make sure you've added the `CLIENT_SECRET_JSON` secret correctly
- The value should be the entire JSON content, not just the filename

**Workflow fails with authentication errors:**
- Make sure you've added the `TOKEN_JSON` secret
- Generate a fresh token locally first: `python3 generate_token.py`
- Copy the entire contents of `token.json` to the secret

**Workflow runs but no videos uploaded:**
- Check the workflow logs for specific error messages
- Make sure your OAuth app has the correct scopes
- Verify you're added as a test user in Google Cloud Console

