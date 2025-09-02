# 🚀 C4 Chatbot Deployment Guide

## Quick Start

### **1. Local Testing**
```bash
# Test locally first
python run_local.py
```

### **2. Prepare for Deployment**
```bash
# Check deployment readiness
python deploy_to_streamlit.py
```

### **3. Deploy to Streamlit Cloud**
1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. Click "New app"
3. Select your repository
4. Set main file path to: `with_ui/c4_chatbot_ui.py`
5. Deploy!

## 📁 Repository Structure

```
your-repo/
├── with_ui/
│   ├── c4_chatbot_ui.py          # Main Streamlit app
│   ├── c4_generator_new.py       # C4 generation logic
│   ├── requirements.txt          # Python dependencies
│   ├── deploy_to_streamlit.py    # Deployment helper
│   ├── run_local.py              # Local testing script
│   └── README_Deployment.md      # This file
├── .streamlit/
│   └── secrets.toml              # API keys (create this)
├── .gitignore                    # Git ignore file
└── README.md                     # Main project README
```

## 🔧 Setup Steps

### **Step 1: Create Secrets File**
```bash
mkdir .streamlit
echo 'OPENAI_API_KEY = "your-openai-api-key-here"' > .streamlit/secrets.toml
```

### **Step 2: Update Requirements**
```bash
# requirements.txt is already configured with all dependencies
```

### **Step 3: Test Locally**
```bash
python run_local.py
```

### **Step 4: Check Deployment Readiness**
```bash
python deploy_to_streamlit.py
```

### **Step 5: Deploy to Streamlit Cloud**
1. **Go to**: https://share.streamlit.io/
2. **Click**: "New app"
3. **Repository**: Select your GitHub repo
4. **Main file path**: `with_ui/c4_chatbot_ui.py`
5. **Deploy!**

## 🔑 API Key Configuration

### **For Local Development**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

### **For Streamlit Cloud**
1. Go to your app's settings
2. Navigate to "Secrets"
3. Add:
   ```toml
   OPENAI_API_KEY = "your-actual-api-key-here"
   ```

## 🧪 Testing

### **Local Testing**
```bash
# Run the local testing script
python run_local.py

# Or run directly with Streamlit
streamlit run c4_chatbot_ui.py
```

### **Deployment Testing**
```bash
# Check deployment readiness
python deploy_to_streamlit.py
```

## 🚨 Troubleshooting

### **Common Issues**

#### **1. Import Errors**
```
ModuleNotFoundError: No module named 'langchain'
```
**Solution**: Update requirements.txt and reinstall dependencies

#### **2. API Key Issues**
```
ValueError: OpenAI API key not available
```
**Solution**: Check environment variables or Streamlit secrets

#### **3. File Path Issues**
```
FileNotFoundError: [Errno 2] No such file or directory
```
**Solution**: Verify repository structure and file paths

### **Debug Steps**
1. **Check local setup**: `python run_local.py`
2. **Verify deployment readiness**: `python deploy_to_streamlit.py`
3. **Check Streamlit Cloud logs** for deployment errors
4. **Verify secrets configuration** in Streamlit Cloud

## 📊 Deployment Checklist

- [ ] Repository is public and accessible
- [ ] All files are committed and pushed
- [ ] `.streamlit/secrets.toml` is created (not committed)
- [ ] `requirements.txt` is updated
- [ ] `.gitignore` includes secrets
- [ ] OpenAI API key is obtained
- [ ] Streamlit Cloud account is created
- [ ] App is deployed successfully
- [ ] Secrets are configured
- [ ] App is tested and working

## 🎯 Quick Commands

```bash
# Test locally
python run_local.py

# Check deployment readiness
python deploy_to_streamlit.py

# Run Streamlit directly
streamlit run c4_chatbot_ui.py

# Check git status
git status

# Commit changes
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

## 📚 Additional Resources

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Deployment Best Practices](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)
- [Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

## 🎉 Success!

Once deployed, your C4 Architecture Generator Chatbot will be available at:
`https://your-app-name.streamlit.app`

**Features Available:**
- ✅ Multi-tab conversations
- ✅ C4 diagram generation
- ✅ Persona analysis
- ✅ User experience integration
- ✅ Persistent memory
- ✅ API key management
- ✅ Real-time status monitoring

**Enjoy your deployed C4 chatbot!** 🚀✨
