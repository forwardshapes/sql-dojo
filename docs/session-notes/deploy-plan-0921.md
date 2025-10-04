# SQL Dojo Google Cloud Run Deployment Plan
**Date**: September 21, 2025
**Goal**: Deploy Flask application to Google Cloud Run with budget-optimized configuration

## Progress Status
✅ **Completed Steps:**
1. Created Dockerfile for containerizing Flask application
2. Modified app.py for production Cloud Run deployment (port handling, debug mode)
3. Created .dockerignore file to optimize container build

🔄 **Current Step:**
4. Install Google Cloud CLI (user needs to restart VS Code/terminal)

## Remaining Steps

### 5. Enable Required Google Cloud APIs
```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com containerregistry.googleapis.com secretmanager.googleapis.com
```

### 6. Set up Google Secret Manager
Create secrets for:
- `gemini-api-key` (from your .env file)
- `supabase-url` (from your .env file)
- `supabase-publishable-key` (from your .env file)
- `flask-secret-key` (generate new production key)

Commands:
```bash
gcloud secrets create gemini-api-key --data-file=-
gcloud secrets create supabase-url --data-file=-
gcloud secrets create supabase-publishable-key --data-file=-
gcloud secrets create flask-secret-key --data-file=-
```

### 7. Build and Push Container Image
```bash
gcloud builds submit --tag gcr.io/sql-dojo/sql-dojo-app
```

### 8. Deploy Cloud Run Service (Budget-Optimized)
```bash
gcloud run deploy sql-dojo \
  --image gcr.io/sql-dojo/sql-dojo-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 256Mi \
  --cpu 0.5 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --set-secrets="GEMINI_API_KEY=gemini-api-key:latest,SUPABASE_URL=supabase-url:latest,SUPABASE_PUBLISHABLE_KEY=supabase-publishable-key:latest,FLASK_SECRET_KEY=flask-secret-key:latest"
```

### 9. Test Deployment
- Verify application loads
- Test login functionality
- Test SQL exercise validation
- Monitor logs for errors

## Budget Configuration Details
- **CPU**: 0.5 vCPU (cost-effective for low traffic)
- **Memory**: 256Mi (sufficient for Flask app)
- **Min instances**: 0 (scales to zero = $0 when not in use)
- **Max instances**: 10 (prevents runaway costs)
- **Estimated monthly cost**: $0.10-$1.00 for low traffic
- **Secret Manager cost**: ~$0.24/month for 4 secrets

## Files Created/Modified
- `Dockerfile` - Container configuration
- `.dockerignore` - Build optimization
- `app.py` - Production port handling (line 189-193)

## Next Actions After VS Code Restart
1. Test `gcloud --version` in new terminal
2. Run `gcloud auth login`
3. Run `gcloud config set project sql-dojo`
4. Continue with API enablement step