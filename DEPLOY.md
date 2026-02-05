# Almira Backend - Render Deployment Guide

## Prerequisites
- Render account (https://render.com)
- GitHub repository connected
- Supabase project (for database)
- Razorpay account (for payments)

## Deployment Steps

### 1. Connect Repository to Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repository: `shaibinkb16/Almira_Backend`
4. Select the branch: `main`

### 2. Configure Build Settings

**Name:** `almira-backend`

**Environment:** `Python 3`

**Region:** Choose closest to your users (e.g., Singapore)

**Branch:** `main`

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 3. Environment Variables

Add these environment variables in Render:

#### Required Variables

```env
# Application
SECRET_KEY=your-super-secret-key-min-32-chars-here-replace-this
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# API Configuration
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["https://your-frontend-url.onrender.com","https://yourdomain.com"]

# Supabase (Get from Supabase Dashboard → Settings → API)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
SUPABASE_JWT_SECRET=your-jwt-secret-here

# Database (Optional - for migrations)
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres

# Razorpay (Get from Razorpay Dashboard)
RAZORPAY_KEY_ID=rzp_live_your_key_id_here
RAZORPAY_KEY_SECRET=your_key_secret_here
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret_here

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# File Upload
MAX_UPLOAD_SIZE_MB=10
```

#### Optional Variables (Redis - Not required on free tier)

```env
# Redis (Skip if not using)
# REDIS_HOST=redis-hostname
# REDIS_PORT=6379
# REDIS_PASSWORD=your-redis-password
```

### 4. Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start the application
3. Wait for deployment to complete (2-5 minutes)

### 5. Verify Deployment

Once deployed, test your API:

**Health Check:**
```bash
curl https://almira-backend.onrender.com/api/v1/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-02-05T12:00:00Z"
}
```

### 6. Update Frontend

Update your frontend `.env` with the new backend URL:

```env
VITE_API_BASE_URL=https://almira-backend.onrender.com/api/v1
```

## Important Notes

### Free Tier Limitations
- Render free tier spins down after 15 minutes of inactivity
- First request after sleep takes ~30 seconds (cold start)
- Consider upgrading to paid tier for production

### Redis (Optional)
- Redis is optional - the app works without it
- If Redis connection fails, the app continues without cache
- For production with caching, consider Render's Redis add-on

### Logs
View logs in Render Dashboard:
1. Go to your service
2. Click **"Logs"** tab
3. Monitor startup and runtime logs

### Custom Domain (Optional)
1. In Render Dashboard → Your Service → Settings
2. Add Custom Domain
3. Follow DNS configuration instructions

## Troubleshooting

### Build Fails
- Check `requirements.txt` is valid
- Ensure Python version compatibility (3.11+)
- Check build logs for specific errors

### Application Won't Start
- Verify all required environment variables are set
- Check logs for startup errors
- Ensure Supabase credentials are correct

### CORS Errors
- Update `CORS_ORIGINS` to include your frontend URL
- Format: JSON array of strings
- Example: `["https://almira-frontend.onrender.com"]`

### Database Connection Issues
- Verify Supabase URL and keys
- Check Supabase project is active
- Test credentials with Supabase dashboard

## Monitoring

### Health Check Endpoint
```
GET /api/v1/health
```

### API Documentation
Once deployed, access interactive docs:
```
https://your-app.onrender.com/docs
```

## Security Checklist

- ✅ `DEBUG=false` in production
- ✅ Strong `SECRET_KEY` (min 32 characters)
- ✅ Correct `CORS_ORIGINS` (no wildcards)
- ✅ Use `rzp_live_` keys for production payments
- ✅ Keep service role key secret (never expose to frontend)
- ✅ Enable Supabase RLS policies
- ✅ Set appropriate rate limits

## Support

If you encounter issues:
1. Check Render logs
2. Verify environment variables
3. Test Supabase connection
4. Review API documentation at `/docs`
