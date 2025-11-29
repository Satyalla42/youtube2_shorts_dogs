# GitHub Actions Cookies Setup - Explained

## Why Are Cookies Needed?

YouTube has implemented bot detection mechanisms to prevent automated downloads. When the script runs in GitHub Actions, it's running on a fresh Ubuntu server without any browser history or cookies. YouTube sees this as suspicious activity and blocks the downloads with errors like:

- `"Sign in to confirm you're not a bot"`
- `HTTP Error 403: Forbidden`
- `Precondition check failed`

## How Cookies Help

Cookies from your browser contain authentication tokens that prove you're a legitimate user. By providing these cookies to yt-dlp, YouTube treats the requests as coming from a real browser session, allowing downloads to proceed.

## How the Script Handles Cookies

The script tries multiple methods in this order:

1. **Cookies from file (`cookies.txt`)** - For GitHub Actions
2. **Cookies from Chrome browser** - For local use
3. **Cookies from Safari browser** - macOS fallback
4. **No cookies** - Last resort (may fail)

## Setting Up Cookies for GitHub Actions

### Step 1: Export Cookies from Your Browser

You have several options:

#### Option A: Using yt-dlp (Recommended)
```bash
# Export cookies from Chrome
yt-dlp --cookies-from-browser chrome --print-to-file cookies.txt ""

# Or from Safari (macOS)
yt-dlp --cookies-from-browser safari --print-to-file cookies.txt ""
```

#### Option B: Using Browser Extension
1. Install a browser extension like "Get cookies.txt LOCALLY" for Chrome/Firefox
2. Visit youtube.com while logged in
3. Click the extension icon
4. Export cookies as `cookies.txt` format

#### Option C: Manual Export (Advanced)
1. Open browser developer tools (F12)
2. Go to Application/Storage → Cookies → https://youtube.com
3. Export cookies in Netscape format

### Step 2: Add Cookies as GitHub Secret

1. Open the exported `cookies.txt` file
2. Copy **ALL** its contents
3. Go to your GitHub repository: https://github.com/Satyalla42/youtube2_shorts_dogs
4. Navigate to: **Settings** → **Secrets and variables** → **Actions**
5. Click **"New repository secret"**
6. Set:
   - **Name**: `YOUTUBE_COOKIES`
   - **Value**: Paste the entire contents of `cookies.txt`
7. Click **"Add secret"**

### Step 3: How It Works in GitHub Actions

When the workflow runs:

1. The workflow creates `cookies.txt` from the secret:
   ```yaml
   echo "$YOUTUBE_COOKIES" > cookies.txt
   ```

2. The script detects `cookies.txt` exists and uses it:
   ```python
   (['--cookies', 'cookies.txt'], os.path.exists('cookies.txt'))
   ```

3. yt-dlp uses these cookies to authenticate with YouTube

## Important Notes

### Cookie Expiration
- Cookies expire after some time (usually weeks/months)
- If downloads start failing, re-export and update the secret
- YouTube may invalidate cookies if suspicious activity is detected

### Security
- **Never commit `cookies.txt` to git** (it's in `.gitignore`)
- Cookies give access to your YouTube account
- Only add cookies as a GitHub Secret (encrypted)
- Consider using a dedicated YouTube account for automation

### Privacy
- Cookies contain session information
- They may include your account preferences
- Use a separate account if privacy is a concern

## Troubleshooting

### "Cookies file not found"
- Make sure you added the `YOUTUBE_COOKIES` secret
- Check that the secret name is exactly `YOUTUBE_COOKIES` (case-sensitive)

### "Cookies expired or invalid"
- Re-export cookies from your browser
- Make sure you're logged into YouTube when exporting
- Update the GitHub secret with new cookies

### "Still getting bot detection errors"
- Try exporting cookies again (they may have expired)
- Make sure you're logged into YouTube when exporting
- Wait a few minutes and try again (rate limiting)

## Alternative: Without Cookies

The script will try to download without cookies as a last resort, but this often fails due to YouTube's bot detection. Cookies are **highly recommended** for reliable operation.

## Testing Locally First

Before setting up GitHub Actions, test cookie export locally:

```bash
# Export cookies
yt-dlp --cookies-from-browser chrome --print-to-file cookies.txt ""

# Test download with cookies
yt-dlp --cookies cookies.txt "https://www.youtube.com/watch?v=VIDEO_ID"
```

If this works, the same cookies will work in GitHub Actions.

