# Streamlit Cloud Deployment Guide

## 🚀 Deploying C4 Architecture Generator Chatbot to Streamlit Cloud

This guide will walk you through deploying your C4 Architecture Generator Chatbot to Streamlit Cloud, including all necessary configuration files and setup steps.

## 📋 Prerequisites

### **1. GitHub Repository**
- Your code must be in a GitHub repository
- Repository should be public (for free Streamlit Cloud) or private (for paid plans)
- All necessary files should be committed and pushed

### **2. OpenAI API Key**
- You'll need a valid OpenAI API key
- Get one from: https://platform.openai.com/api-keys

### **3. Streamlit Account**
- Create a free account at: https://share.streamlit.io/
- Connect your GitHub account

## 🏗️ Repository Structure

Ensure your repository has this structure:
```
your-repo/
├── with_ui/
│   ├── c4_chatbot_ui.py          # Main Streamlit app
│   ├── c4_generator_new.py       # C4 generation logic
│   ├── requirements.txt          # Python dependencies
│   └── README.md                 # Project documentation
├── .streamlit/
│   └── secrets.toml              # API keys (create this)
├── .gitignore                    # Git ignore file
└── README.md                     # Main project README
```

## 📁 Required Files

### **1. Create `.streamlit/secrets.toml`**
```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "your-openai-api-key-here"
```

### **2. Update `requirements.txt`**
```txt
streamlit>=1.28.0
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-core>=0.1.0
python-dotenv>=1.0.0
pydantic>=2.0.0
structurizr-dsl>=1.0.0
openai>=1.0.0
```

### **3. Create `.gitignore`**
```gitignore
# Environment variables
.env
.streamlit/secrets.toml

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Memory files
*.pkl
*.json
```

## 🔧 Deployment Steps

### **Step 1: Prepare Your Repository**

1. **Create the `.streamlit` directory** in your repository root:
   ```bash
   mkdir .streamlit
   ```

2. **Create `secrets.toml`** in the `.streamlit` directory:
   ```bash
   echo 'OPENAI_API_KEY = "your-openai-api-key-here"' > .streamlit/secrets.toml
   ```

3. **Update `requirements.txt`** with all necessary dependencies

4. **Commit and push** all changes:
   ```bash
   git add .
   git commit -m "Add Streamlit Cloud deployment configuration"
   git push origin main
   ```

### **Step 2: Deploy to Streamlit Cloud**

1. **Go to Streamlit Cloud**: https://share.streamlit.io/

2. **Click "New app"**

3. **Fill in the deployment form**:
   - **Repository**: Select your GitHub repository
   - **Branch**: `main` (or your default branch)
   - **Main file path**: `with_ui/c4_chatbot_ui.py`
   - **App URL**: Choose a custom URL (optional)

4. **Click "Deploy!"**

### **Step 3: Configure Secrets**

1. **After deployment**, go to your app's settings
2. **Navigate to "Secrets"** section
3. **Add your OpenAI API key**:
   ```toml
   OPENAI_API_KEY = "your-actual-openai-api-key-here"
   ```
4. **Save the secrets**

### **Step 4: Verify Deployment**

1. **Check the deployment logs** for any errors
2. **Test the app** by visiting your Streamlit Cloud URL
3. **Verify API key status** in the sidebar

## 🔒 Security Best Practices

### **1. Never Commit Secrets**
- Add `.streamlit/secrets.toml` to `.gitignore`
- Use environment variables or Streamlit secrets for API keys
- Never hardcode API keys in your code

### **2. Use Streamlit Secrets**
- Store sensitive information in Streamlit Cloud secrets
- Access secrets using `st.secrets["KEY_NAME"]`
- Keep secrets secure and rotate them regularly

### **3. Environment Variables**
- Use environment variables for configuration
- Set different values for development and production
- Document required environment variables

## 📊 Monitoring and Maintenance

### **1. Deployment Logs**
- Monitor deployment logs for errors
- Check for dependency issues
- Verify API key configuration

### **2. Performance Monitoring**
- Monitor app performance and response times
- Check for memory usage issues
- Optimize for Streamlit Cloud limitations

### **3. Updates and Maintenance**
- Regularly update dependencies
- Monitor for security vulnerabilities
- Keep API keys current

## 🚨 Troubleshooting

### **Common Issues**

#### **1. Import Errors**
```
ModuleNotFoundError: No module named 'langchain'
```
**Solution**: Update `requirements.txt` with correct dependencies

#### **2. API Key Issues**
```
ValueError: OpenAI API key not available
```
**Solution**: Check Streamlit secrets configuration

#### **3. File Path Issues**
```
FileNotFoundError: [Errno 2] No such file or directory
```
**Solution**: Verify file paths and repository structure

#### **4. Memory Issues**
```
MemoryError: Unable to allocate array
```
**Solution**: Optimize memory usage, reduce context length

### **Debug Steps**

1. **Check deployment logs** in Streamlit Cloud
2. **Verify file structure** matches expected layout
3. **Test locally** before deploying
4. **Check dependencies** in requirements.txt
5. **Verify secrets** configuration

## 🔄 Continuous Deployment

### **1. Automatic Updates**
- Streamlit Cloud automatically redeploys on git push
- No manual intervention needed for updates
- Monitor deployment status after each push

### **2. Branch Management**
- Use different branches for development and production
- Deploy from stable branches only
- Test changes locally before pushing

### **3. Version Control**
- Tag releases for stable versions
- Keep commit history clean
- Document changes in commit messages

## 📱 Custom Domain (Optional)

### **1. Custom URL**
- Choose a custom URL during deployment
- URLs are in format: `https://your-app-name.streamlit.app`
- Custom domains available for paid plans

### **2. SSL Certificate**
- Streamlit Cloud provides automatic SSL
- HTTPS enabled by default
- No additional configuration needed

## 💰 Pricing and Limits

### **Free Tier**
- Unlimited public apps
- 1GB RAM per app
- 1 CPU per app
- 1GB storage per app

### **Paid Plans**
- Private repositories
- More resources
- Custom domains
- Priority support

## 📚 Additional Resources

### **Streamlit Cloud Documentation**
- [Streamlit Cloud Guide](https://docs.streamlit.io/streamlit-community-cloud)
- [Deployment Best Practices](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)
- [Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

### **Troubleshooting Resources**
- [Streamlit Community Forum](https://discuss.streamlit.io/)
- [GitHub Issues](https://github.com/streamlit/streamlit/issues)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/streamlit)

## 🎯 Quick Deployment Checklist

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

## 🚀 Next Steps After Deployment

1. **Test all features** of your deployed app
2. **Share the URL** with users
3. **Monitor performance** and usage
4. **Gather feedback** from users
5. **Plan updates** and improvements
6. **Set up monitoring** and alerts
7. **Document usage** for users

---

**Congratulations!** 🎉 Your C4 Architecture Generator Chatbot is now deployed to Streamlit Cloud and accessible worldwide! Users can now access your powerful C4 diagram generation tool from anywhere with just a web browser.

**Your app URL**: `https://your-app-name.streamlit.app`

**Remember**: Keep your API keys secure, monitor your app's performance, and enjoy the benefits of cloud deployment! ☁️✨
