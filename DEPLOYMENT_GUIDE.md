# BA Agentic AI - Complete Deployment Guide

This guide will help you deploy your BA Agentic AI project to Vercel with a separate backend API.

## Project Overview

The project consists of two main components:
1. **Frontend**: Next.js application deployed on Vercel
2. **Backend**: FastAPI Python application deployed on Railway/Render/Heroku

## Architecture

```
┌─────────────────┐    HTTP Requests    ┌─────────────────┐
│   Next.js       │ ──────────────────► │   FastAPI       │
│   Frontend      │                     │   Backend       │
│   (Vercel)      │ ◄────────────────── │   (Railway)     │
└─────────────────┘    JSON Responses   └─────────────────┘
```

## Prerequisites

- GitHub account
- Vercel account
- Railway/Render/Heroku account
- Google Gemini API key

## Step 1: Prepare Your Repository

1. **Organize your files** (already done):
   - `my-dashboard-site/` - Next.js frontend
   - `BA-Agentic-AI/api/` - FastAPI backend

2. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add Vercel integration and FastAPI backend"
   git push origin main
   ```

## Step 2: Deploy Backend (FastAPI)

### Option A: Railway Deployment (Recommended)

1. Go to [Railway](https://railway.app/) and sign in with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Set the source directory to `BA-Agentic-AI/api/`
5. Add environment variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key
6. Deploy the project
7. Note the generated URL (e.g., `https://your-app.railway.app`)

### Option B: Render Deployment

1. Go to [Render](https://render.com/) and sign in with GitHub
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `ba-agentic-ai-backend`
   - **Root Directory**: `BA-Agentic-AI/api/`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key
6. Deploy

### Option C: Heroku Deployment

1. Install Heroku CLI
2. Create a new Heroku app:
   ```bash
   heroku create your-app-name
   ```
3. Set buildpacks:
   ```bash
   heroku buildpacks:set heroku/python
   ```
4. Add environment variables:
   ```bash
   heroku config:set GEMINI_API_KEY="your-api-key"
   ```
5. Deploy:
   ```bash
   git subtree push --prefix BA-Agentic-AI/api heroku main
   ```

## Step 3: Deploy Frontend (Next.js) to Vercel

1. Go to [Vercel](https://vercel.com/) and sign in with GitHub
2. Click "New Project"
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `my-dashboard-site`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
5. Add environment variables:
   - `BACKEND_API_URL`: Your deployed backend URL (from Step 2)
6. Deploy

## Step 4: Test the Integration

1. Visit your Vercel frontend URL
2. Enter a business problem in the form
3. Click "Generate Business Analysis Report"
4. Verify that the report is generated with Mermaid diagrams

## Step 5: Environment Variables Setup

### Frontend (Vercel Dashboard)
- `BACKEND_API_URL`: `https://your-backend-url.railway.app` (or your deployed backend URL)

### Backend (Railway/Render/Heroku Dashboard)
- `GEMINI_API_KEY`: Your Google Gemini API key

## Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Check that your backend CORS settings allow your frontend domain
   - Update the CORS configuration in `BA-Agentic-AI/api/main.py`

2. **API Connection Errors**:
   - Verify the `BACKEND_API_URL` environment variable is correct
   - Check that your backend is running and accessible

3. **Mermaid Diagrams Not Rendering**:
   - Check browser console for JavaScript errors
   - Verify that the Mermaid library is properly loaded

4. **Backend Deployment Issues**:
   - Check the deployment logs for Python errors
   - Verify all dependencies are in `requirements.txt`
   - Ensure the `GEMINI_API_KEY` is set correctly

### Debug Steps

1. **Test Backend Locally**:
   ```bash
   cd BA-Agentic-AI/api
   pip install -r requirements.txt
   export GEMINI_API_KEY="your-key"
   python main.py
   ```

2. **Test Frontend Locally**:
   ```bash
   cd my-dashboard-site
   npm install
   echo "BACKEND_API_URL=http://localhost:8000" > .env.local
   npm run dev
   ```

3. **Check API Endpoints**:
   - Backend health: `https://your-backend-url/health`
   - API docs: `https://your-backend-url/docs`

## Production Considerations

### Security
1. **API Key Protection**: Never expose API keys in client-side code
2. **CORS Configuration**: Restrict CORS to your frontend domain only
3. **Rate Limiting**: Consider implementing rate limiting on the backend
4. **Input Validation**: The API already validates input using Pydantic

### Performance
1. **Caching**: Consider implementing caching for generated reports
2. **CDN**: Vercel provides CDN for static assets
3. **Database**: Consider adding a database to store generated reports

### Monitoring
1. **Vercel Analytics**: Enable Vercel Analytics for frontend monitoring
2. **Backend Logs**: Monitor backend logs for errors and performance
3. **API Health Checks**: Use the `/health` endpoint for monitoring

## Cost Optimization

### Vercel (Frontend)
- Free tier: 100GB bandwidth, 100GB storage
- Pro plan: $20/month for more resources

### Railway (Backend)
- Free tier: $5 credit monthly
- Pay-as-you-go: $0.000463 per second

### Render (Backend)
- Free tier: 750 hours/month
- Paid plans: $7/month and up

### API Costs
- Google Gemini API: Pay per token usage
- Monitor usage in Google AI Studio dashboard

## Maintenance

### Regular Tasks
1. **Update Dependencies**: Keep both frontend and backend dependencies updated
2. **Monitor Logs**: Check for errors and performance issues
3. **Backup Data**: If storing reports, implement backup strategy
4. **Security Updates**: Keep API keys secure and rotate if needed

### Scaling
1. **Traffic Increase**: Monitor usage and upgrade plans as needed
2. **Performance**: Optimize API responses and frontend loading
3. **Features**: Add new features based on user feedback

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review deployment platform documentation
3. Check GitHub issues for similar problems
4. Contact platform support if needed

## Next Steps

After successful deployment, consider:
1. Adding user authentication
2. Implementing report storage
3. Adding more analysis features
4. Creating a mobile app
5. Adding team collaboration features

---

**Congratulations!** Your BA Agentic AI is now deployed and ready to use! 🎉 