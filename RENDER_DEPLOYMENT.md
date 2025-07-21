# 🚀 Render.com Deployment Guide

## Quick Setup for eBay AI Analyzer

### 1. Create Render Account
- Go to [render.com](https://render.com)
- Sign up with your GitHub account

### 2. Create New Web Service
- Click **"New +"** → **"Web Service"**
- Connect your GitHub repository: `Nick-McCubbin00/EbaySearches`

### 3. Configure Service
- **Name**: `ebay-ai-analyzer` (or any name)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`
- **Plan**: Free (or paid)

### 4. Add Environment Variables
In the **Environment** section, add:
```
EBAY_ACCESS_TOKEN=your-ebay-oauth-token-here
GEMINI_API_KEY=your-gemini-api-key-here
```

### 5. Deploy
- Click **"Create Web Service"**
- Wait 2-5 minutes for deployment
- Your app will be live at: `https://your-app-name.onrender.com`

## 🔑 Getting API Keys

### eBay API Token
1. Go to [eBay Developer Program](https://developer.ebay.com/)
2. Create application and get OAuth token
3. Copy the token to Render environment variables

### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create API key
3. Copy the key to Render environment variables

## ✅ Done!
Your eBay AI Analyzer will be live and functional with real API data! 