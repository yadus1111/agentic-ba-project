# 🚀 Deployment Checklist

## Backend Deployment (Choose One)

### ✅ Railway (Recommended)
- [ ] Go to [Railway.app](https://railway.app/)
- [ ] Sign in with GitHub
- [ ] Click "New Project" → "Deploy from GitHub repo"
- [ ] Select your repository
- [ ] Set Root Directory: `BA-Agentic-AI/api/`
- [ ] Add Environment Variable: `GEMINI_API_KEY` = your API key
- [ ] Deploy
- [ ] Copy the generated URL (e.g., `https://your-app.up.railway.app`)

### ✅ Render
- [ ] Go to [Render.com](https://render.com/)
- [ ] Sign in with GitHub
- [ ] Click "New" → "Web Service"
- [ ] Connect your repository
- [ ] Set Root Directory: `BA-Agentic-AI/api/`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Add Environment Variable: `GEMINI_API_KEY` = your API key
- [ ] Deploy
- [ ] Copy the generated URL

### ✅ Heroku
- [ ] Install Heroku CLI
- [ ] Run: `heroku create your-app-name`
- [ ] Run: `heroku buildpacks:set heroku/python`
- [ ] Run: `heroku config:set GEMINI_API_KEY="your-api-key"`
- [ ] Run: `git subtree push --prefix BA-Agentic-AI/api heroku main`
- [ ] Copy the generated URL

## Frontend Deployment (Vercel)

- [ ] Go to [Vercel.com](https://vercel.com/)
- [ ] Sign in with GitHub
- [ ] Click "New Project"
- [ ] Import your repository
- [ ] Set Framework Preset: `Next.js`
- [ ] Set Root Directory: `my-dashboard-site`
- [ ] Set Build Command: `npm run build`
- [ ] Set Output Directory: `.next`
- [ ] Add Environment Variable: `BACKEND_API_URL` = your backend URL
- [ ] Deploy
- [ ] Copy the generated URL

## Testing

- [ ] Test Backend: Visit `your-backend-url/health`
- [ ] Test Backend Docs: Visit `your-backend-url/docs`
- [ ] Test Frontend: Visit your Vercel URL
- [ ] Enter a business problem and generate a report
- [ ] Verify Mermaid diagrams render correctly

## Environment Variables Summary

### Backend (Railway/Render/Heroku)
```
GEMINI_API_KEY=your-google-gemini-api-key
```

### Frontend (Vercel)
```
BACKEND_API_URL=https://your-backend-url.railway.app
```

## Troubleshooting

### If you get CORS errors:
- Update CORS in `BA-Agentic-AI/api/main.py` to allow your Vercel domain

### If you get API connection errors:
- Check `BACKEND_API_URL` is correct in Vercel
- Verify backend is running and accessible

### If Mermaid diagrams don't render:
- Check browser console for JavaScript errors
- Verify Mermaid library is loading

---

**🎉 Your BA Agentic AI is now deployed!** 