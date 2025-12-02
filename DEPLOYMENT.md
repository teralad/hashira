# Hashira Deployment Guide

## 🚀 Deployment Options

### Option 1: Streamlit Cloud (Easiest)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy with one click

**⚠️ Note:** Free tier has 1GB RAM limit. The model may be too large. Consider using Streamlit Cloud for Teams.

---

### Option 2: Docker (Recommended for Production)

#### Quick Start

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access at http://localhost:8501
```

#### Manual Docker Commands

```bash
# Build the image
docker build -t hashira:latest .

# Run the container
docker run -d \
  -p 8501:8501 \
  -v $(pwd)/generated_code:/app/generated_code \
  --name hashira \
  hashira:latest

# View logs
docker logs -f hashira

# Stop the container
docker stop hashira
```

#### GPU Support (Optional)

For faster inference, use GPU:

```bash
docker run -d \
  -p 8501:8501 \
  --gpus all \
  -v $(pwd)/generated_code:/app/generated_code \
  --name hashira \
  hashira:latest
```

---

### Option 3: Cloud Platforms

#### Deploy to Render.com

1. Create account at [render.com](https://render.com)
2. Create new "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Environment:** Docker
   - **Instance Type:** At least 4GB RAM
   - **Port:** 8501
5. Deploy

#### Deploy to Railway.app

1. Create account at [railway.app](https://railway.app)
2. Create new project from GitHub repo
3. Railway auto-detects Dockerfile
4. Add environment variables if needed
5. Deploy

#### Deploy to Google Cloud Run

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/hashira

# Deploy to Cloud Run
gcloud run deploy hashira \
  --image gcr.io/PROJECT_ID/hashira \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --port 8501 \
  --allow-unauthenticated
```

#### Deploy to AWS ECS/Fargate

```bash
# Build and push to ECR
aws ecr create-repository --repository-name hashira
docker tag hashira:latest AWS_ACCOUNT.dkr.ecr.REGION.amazonaws.com/hashira:latest
docker push AWS_ACCOUNT.dkr.ecr.REGION.amazonaws.com/hashira:latest

# Create task definition and service (use AWS Console or CLI)
```

#### Deploy to Azure Container Instances

```bash
# Login to Azure
az login

# Create resource group
az group create --name hashira-rg --location eastus

# Deploy container
az container create \
  --resource-group hashira-rg \
  --name hashira \
  --image hashira:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8501 \
  --dns-name-label hashira-app
```

---

### Option 4: Hugging Face Spaces

1. Create a new Space at [huggingface.co/spaces](https://huggingface.co/spaces)
2. Choose "Streamlit" as the SDK
3. Upload your files:
   - `app.py`
   - `requirements.txt`
   - All `llm/`, `parsers/`, `templates/` folders
4. Add a `README.md` with:
   ```yaml
   ---
   title: Hashira
   emoji: ⚡
   colorFrom: blue
   colorTo: purple
   sdk: streamlit
   sdk_version: 1.28.0
   app_file: app.py
   pinned: false
   ---
   ```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file for local development:

```bash
TRANSFORMERS_CACHE=/app/.cache/huggingface
HF_HOME=/app/.cache/huggingface
HF_ENDPOINT=https://hf-mirror.com  # Use mirror if needed
```

### Resource Requirements

- **Minimum:** 4GB RAM, 2 CPU cores
- **Recommended:** 8GB RAM, 4 CPU cores
- **With GPU:** NVIDIA GPU with 6GB+ VRAM
- **Disk:** 10GB (for model cache)

---

## 📊 Performance Optimization

### Use Smaller Model

Edit `llm/generator.py`:

```python
# Faster, smaller model
model_name = "Salesforce/codegen-350M-mono"

# Or use quantized version
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained(
    "bigcode/starcoderbase",
    load_in_8bit=True  # Reduces memory by 50%
)
```

### Enable Model Caching

The Dockerfile already caches models in a volume. First run downloads the model (~6GB), subsequent runs are fast.

---

## 🔒 Security Considerations

1. **Add authentication** for production:
   ```python
   # In app.py, add at the top
   import streamlit_authenticator as stauth
   ```

2. **Rate limiting**: Use nginx or cloud provider rate limiting

3. **HTTPS**: Always use HTTPS in production (most platforms provide this)

4. **Environment secrets**: Never commit API keys or secrets

---

## 🐛 Troubleshooting

### Out of Memory

- Reduce `max_new_tokens` in `llm/generator.py`
- Use a smaller model
- Increase container memory limits

### Model Download Fails

- Check internet connection
- Use `HF_ENDPOINT` mirror if in restricted region
- Pre-download model and bake into Docker image

### Slow Performance

- Use GPU-enabled deployment
- Enable model quantization
- Consider caching generated results

---

## 📝 Example: Deploy to Render.com

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your `hashira` repo
4. Settings:
   - **Name:** hashira
   - **Environment:** Docker
   - **Instance Type:** Standard 4GB ($25/month)
   - **Port:** 8501
5. Click "Create Web Service"
6. Wait 5-10 minutes for first deployment (model download)
7. Access your app at `https://hashira.onrender.com`

---

## 🎯 Recommended: Railway.app

Railway is the easiest for beginners:

1. Visit [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub repo"
3. Select `hashira` repo
4. Railway auto-detects Dockerfile and deploys
5. Upgrade to at least 4GB RAM plan
6. Access via generated URL

**Cost:** ~$10-20/month for 4GB instance
