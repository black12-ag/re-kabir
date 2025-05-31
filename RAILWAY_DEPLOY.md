# Railway Deployment Instructions

This guide explains how to deploy your Telegram bot to Railway.app for 24/7 operation.

## Setup Steps

1. **GitHub Repository Setup**
   - Push your code to GitHub at: https://github.com/black12-ag/re-kabir.git
   - Make sure your repository has these files at the root level:
     - `Procfile`
     - `requirements.txt`
     - `run.py`

2. **Railway.app Setup**
   - Create an account on [Railway.app](https://railway.app)
   - Create a new project → "Deploy from GitHub repo"
   - Select your repository: black12-ag/re-kabir

3. **Environment Variables**
   - In Railway, go to the Variables tab
   - Add these variables:
     ```
     TELEGRAM_BOT_TOKEN=8164759908:AAFM75mO57T5KZlREJTw43TlA2ODoe3GI4g
     ADMIN_USER_ID=497726167,5406887259
     WEBHOOK_MODE=true
     PORT=8080
     ```

4. **Deploy**
   - Railway will automatically deploy your application
   - If there are errors, check the Logs tab

5. **Get Your Domain**
   - Go to Settings → Domains
   - Copy your app's URL (like https://re-kabir-production.up.railway.app)
   - Your bot will automatically use this URL for its webhook

## Troubleshooting

If your deployment fails:

1. Check that your `Procfile` is at the repository root, not in a subfolder
2. Make sure the `Procfile` contains exactly: `worker: python run.py`
3. Verify your GitHub repository contains all necessary files
4. Check Railway logs for specific error messages 