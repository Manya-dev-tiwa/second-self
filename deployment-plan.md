# SecondSelf - Streamlit Deployment Plan

## Overview
This document outlines the deployment strategy for the SecondSelf AI Second Brain Dashboard on Streamlit Cloud and alternative platforms.

## Table of Contents
1. [Deployment Options](#deployment-options)
2. [Streamlit Cloud Deployment (Recommended)](#streamlit-cloud-deployment)
3. [Alternative Deployment Options](#alternative-deployment-options)
4. [Pre-Deployment Checklist](#pre-deployment-checklist)
5. [Environment Configuration](#environment-configuration)
6. [Post-Deployment Steps](#post-deployment-steps)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Deployment Options

### Option 1: Streamlit Cloud (Recommended)
- **Pros**: Free tier available, easiest setup, optimized for Streamlit apps, automatic SSL
- **Cons**: Resource limits on free tier, limited customization
- **Cost**: Free for hobby projects, $20/month for professional tier
- **Best for**: Portfolio projects, prototypes, personal use

### Option 2: Railway/Render
- **Pros**: More control, supports background processes, generous free tier
- **Cons**: Requires more configuration, need to set up web server
- **Cost**: Free tier available, paid plans from $5/month
- **Best for**: Production apps needing more resources

### Option 3: AWS/GCP/Azure
- **Pros**: Maximum control, scalable, enterprise features
- **Cons**: Complex setup, higher cost, requires DevOps knowledge
- **Cost**: Pay-as-you-go, typically $20-100/month for small apps
- **Best for**: Enterprise applications, high-traffic scenarios

### Option 4: Self-Hosted (VPS)
- **Pros**: Full control, cost-effective for long-term, customizable
- **Cons**: Requires server management, security setup, maintenance
- **Cost**: $5-20/month for VPS (DigitalOcean, Linode, etc.)
- **Best for**: Technical users wanting full control

---

## Streamlit Cloud Deployment (Recommended)

### Prerequisites
- GitHub account with the project repository
- Streamlit Cloud account (sign up at https://share.streamlit.io)
- Groq API key

### Step 1: Prepare Repository

#### 1.1 Create `.streamlit/config.toml`
Create the directory and file:
```bash
mkdir .streamlit
```

Create `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#0f0f1a"
secondaryBackgroundColor = "#1a1a2e"
textColor = "#ffffff"
font = "sans serif"

[client]
showErrorDetails = false
toolbarMode = "minimal"

[logger]
level = "info"
```

#### 1.2 Update `.gitignore`
Ensure `.gitignore` includes:
```
.env
data/embeddings.pkl
data/file_hashes.pkl
__pycache__/
*.pyc
.DS_Store
.obsidian/
*.lnk
```

#### 1.3 Verify `requirements.txt`
Ensure `requirements.txt` contains:
```
streamlit
sentence-transformers
groq
streamlit-agraph
python-dotenv
torch
numpy
```

#### 1.4 Create `packages.txt` (if needed)
If you encounter system dependency issues, create `packages.txt`:
```
# No system packages typically needed for this project
```

### Step 2: Prepare Data Files

#### 2.1 Commit Essential Data Files
```bash
# Make sure data directory structure exists
mkdir -p data

# Add placeholder if embeddings are too large for git
# Update embeddings.pkl path handling in production
```

#### 2.2 Handle Large Files
If `data/embeddings.pkl` is too large for GitHub:
- Option A: Use Git LFS (Large File Storage)
- Option B: Load embeddings from external storage (S3, etc.)
- Option C: Generate embeddings on first run

For Streamlit Cloud, recommend Option C (generate on first run):
```python
# In ask.py, modify to handle missing embeddings gracefully
def _load_data(self):
    if not os.path.exists(EMBEDDINGS_PATH):
        print("No embeddings found. Will generate on first use.")
        return
    # ... existing code
```

### Step 3: Deploy to Streamlit Cloud

#### 3.1 Push to GitHub
```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

#### 3.2 Connect to Streamlit Cloud
1. Go to https://share.streamlit.io
2. Click "New app"
3. Connect your GitHub account
4. Select your repository
5. Select branch: `main`
6. Main file path: `app.py`
7. Click "Deploy"

#### 3.3 Configure Environment Variables
In Streamlit Cloud dashboard:
1. Go to your app settings
2. Navigate to "Secrets" or "Environment Variables"
3. Add:
   - `GROQ_API_KEY`: Your Groq API key

### Step 4: Verify Deployment
1. Wait for deployment to complete (2-5 minutes)
2. Visit the provided URL
3. Test core functionality:
   - Chat interface
   - Knowledge graph loading
   - Statistics dashboard
4. Check logs for any errors

---

## Alternative Deployment Options

### Railway Deployment

#### Prerequisites
- Railway account
- GitHub repository
- Groq API key

#### Steps
1. Create `railway.json` in project root:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0"
  }
}
```

2. Create `Procfile`:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

3. Deploy via Railway:
   - Connect GitHub repository
   - Add environment variable: `GROQ_API_KEY`
   - Deploy

### Render Deployment

#### Steps
1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: secondself
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
    envVars:
      - key: GROQ_API_KEY
        sync: false
```

2. Connect repository to Render
3. Deploy and configure environment variables

### Docker Deployment

#### Create `Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create data directory
RUN mkdir -p data

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Create `docker-compose.yml`
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./data:/app/data
```

#### Build and Run
```bash
docker build -t secondself .
docker run -p 8501:8501 -e GROQ_API_KEY=your_key secondself
```

---

## Pre-Deployment Checklist

### Code Preparation
- [ ] Update `.gitignore` to exclude sensitive files
- [ ] Create `.streamlit/config.toml` for app configuration
- [ ] Verify `requirements.txt` is complete and pinned to specific versions
- [ ] Test application locally with `streamlit run app.py`
- [ ] Handle large data files (embeddings, etc.)
- [ ] Add error handling for missing API keys
- [ ] Optimize imports and reduce cold start time

### Environment Setup
- [ ] Secure Groq API key
- [ ] Test API key validity
- [ ] Prepare environment variable documentation
- [ ] Set up monitoring/logging strategy

### Repository Preparation
- [ ] Commit all necessary files
- [ ] Create comprehensive README
- [ ] Add license file
- [ ] Tag/release version (optional)
- [ ] Ensure repository is public or accessible

### Testing
- [ ] Test all core features locally
- [ ] Test with sample data
- [ ] Verify responsive design
- [ ] Test error scenarios (missing API key, no data)
- [ ] Performance testing (load time, memory usage)

---

## Environment Configuration

### Required Environment Variables
- `GROQ_API_KEY`: Groq API key for AI responses

### Optional Environment Variables
- `STREAMLIT_SERVER_PORT`: Server port (default: 8501)
- `STREAMLIT_SERVER_ADDRESS`: Server address (default: localhost)
- `PYTHON_VERSION`: Python version for deployment

### Streamlit Cloud Secrets
In Streamlit Cloud, add secrets in `.streamlit/secrets.toml` (don't commit this):
```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

---

## Post-Deployment Steps

### 1. Performance Optimization
- Monitor cold start time
- Optimize model loading
- Implement caching strategies
- Consider using Streamlit's `@st.cache_resource` for expensive operations

### 2. Analytics and Monitoring
- Set up Streamlit analytics (built-in)
- Monitor usage patterns
- Track error rates
- Set up uptime monitoring (UptimeRobot, etc.)

### 3. Backup and Recovery
- Regular backups of knowledge graph data
- Version control for data files
- Disaster recovery plan
- Database backup strategy (if using external DB)

### 4. Security Hardening
- Rotate API keys regularly
- Implement rate limiting
- Add authentication (if needed)
- Enable HTTPS (automatic on Streamlit Cloud)
- Sanitize user inputs

### 5. Documentation Updates
- Update README with deployment URL
- Document any deployment-specific configurations
- Add troubleshooting guide
- Create user guide

---

## Monitoring and Maintenance

### Monitoring Tools
- **Streamlit Dashboard**: Built-in app monitoring
- **Log Analysis**: Streamlit Cloud logs
- **Uptime Monitoring**: UptimeRobot, Pingdom
- **Error Tracking**: Sentry (optional)

### Regular Maintenance Tasks
- Weekly: Check error logs and user feedback
- Monthly: Update dependencies, review performance
- Quarterly: Security audit, API key rotation
- As needed: Bug fixes, feature updates

### Scaling Considerations
- **Vertical Scaling**: Increase resources on Streamlit Cloud (Professional tier)
- **Horizontal Scaling**: Use load balancer with multiple instances
- **Database Scaling**: Move to managed database for large datasets
- **CDN**: Use CDN for static assets

---

## Troubleshooting

### Common Issues

#### 1. Deployment Fails
**Problem**: Build fails during deployment
**Solutions**:
- Check Streamlit Cloud logs for specific errors
- Verify `requirements.txt` format
- Ensure all dependencies are compatible
- Check Python version compatibility

#### 2. App Crashes on Startup
**Problem**: App starts but crashes immediately
**Solutions**:
- Check environment variables are set correctly
- Verify API key validity
- Check data file paths and permissions
- Review error logs in Streamlit Cloud

#### 3. Slow Performance
**Problem**: App loads slowly or times out
**Solutions**:
- Optimize model loading with caching
- Reduce initial data loading
- Use lazy loading for large models
- Consider upgrading to professional tier

#### 4. API Key Errors
**Problem**: Groq API errors or authentication failures
**Solutions**:
- Verify API key is correctly set in secrets
- Check API key hasn't expired
- Ensure API key has necessary permissions
- Test API key locally first

#### 5. Memory Issues
**Problem**: App runs out of memory
**Solutions**:
- Optimize embeddings size
- Implement model unloading when not in use
- Use Streamlit's resource cleanup
- Upgrade to tier with more memory

#### 6. Data Loading Issues
**Problem**: Embeddings or graph data fails to load
**Solutions**:
- Verify data files are included in deployment
- Check file paths are correct for production
- Implement graceful fallback for missing data
- Consider using external storage for large files

### Debugging Tips
1. **Enable Debug Mode**: Add `[client] showErrorDetails = true` to config
2. **Local Reproduction**: Reproduce issues locally with same environment
3. **Log Analysis**: Review Streamlit Cloud logs carefully
4. **Version Isolation**: Pin dependency versions in requirements.txt
5. **Incremental Testing**: Test changes locally before deploying

### Getting Help
- Streamlit Community: https://discuss.streamlit.io
- Streamlit Docs: https://docs.streamlit.io
- Groq API Docs: https://console.groq.com/docs
- Project Issues: Check project repository issues

---

## Deployment Timeline Estimate

### Streamlit Cloud Deployment
- **Preparation**: 1-2 hours
- **Configuration**: 30 minutes
- **Deployment**: 10-15 minutes
- **Testing**: 1-2 hours
- **Total**: 3-5 hours

### Alternative Platforms
- **Railway/Render**: 4-6 hours (additional configuration)
- **Docker/VPS**: 8-12 hours (setup and configuration)
- **Cloud Providers**: 16-24 hours (complex setup)

---

## Cost Estimates

### Streamlit Cloud
- **Free Tier**: $0/month (limited resources)
- **Professional**: $20/month (more resources, priority support)

### Alternative Platforms
- **Railway**: $5-20/month
- **Render**: Free tier available, $7/month for paid
- **DigitalOcean VPS**: $5-20/month
- **AWS/GCP**: $20-100/month depending on usage

### Additional Costs
- **Groq API**: Pay-as-you-go (typically very affordable)
- **Domain Name**: $10-15/year (optional)
- **Monitoring Tools**: $0-20/month (optional)

---

## Security Considerations

### API Key Management
- Never commit API keys to repository
- Use environment variables or secrets management
- Rotate API keys regularly
- Use separate keys for development and production

### Data Privacy
- Ensure user data is encrypted in transit (HTTPS)
- Implement data retention policies
- Comply with relevant data protection regulations
- Consider data anonymization for analytics

### Access Control
- Implement authentication if handling sensitive data
- Use strong, unique passwords
- Enable two-factor authentication where possible
- Regular access audits

---

## Conclusion

This deployment plan provides multiple options for deploying SecondSelf, with Streamlit Cloud being the recommended choice for ease of use and cost-effectiveness. The included troubleshooting guide and monitoring recommendations will help ensure a smooth deployment and ongoing operation.

For most use cases, Streamlit Cloud deployment provides the best balance of simplicity, cost, and performance. Consider alternative platforms only when specific requirements necessitate additional control or resources.

---

**Last Updated**: 2026-08-03
**Version**: 1.0
