# Secrets Configuration Guide

## ✅ FIXED: Secrets File Location

### Problem
The error occurred because Streamlit was looking for secrets in:
- `C:\Users\dkanu\.streamlit\secrets.toml` (user-level)
- `C:\Users\dkanu\OneDrive\Desktop\LMGMT02\LMGMT02\frontend\.streamlit\secrets.toml` (app-level)

But the file was in:
- `C:\Users\dkanu\OneDrive\Desktop\LMGMT02\LMGMT02\.streamlit\secrets.toml` (wrong location)

### Solution
Created the correct directory structure and copied the secrets file:

```
frontend/
  .streamlit/
    secrets.toml  ← Correct location!
```

## 📁 File Structure

```
LMGMT02/
├── .streamlit/
│   └── secrets.toml          ← Root level (for root app.py)
├── frontend/
│   ├── .streamlit/
│   │   └── secrets.toml      ← Frontend level (for frontend/Home.py) ✅
│   ├── Home.py
│   └── pages/
│       └── 2_📚_Learn.py     ← Uses this secrets file
└── backend/
    └── app/
        └── services/
            └── ai_service.py  ← Uses root .env file
```

## 🔑 Secrets File Content

**Location:** `frontend/.streamlit/secrets.toml`

```toml
# Add your Groq API key here
# Get a free, unlimited key at: https://console.groq.com
GROQ_API_KEY = "gsk_YOUR_API_KEY_HERE"
```

## 🚀 How It Works

### In Your Code:
```python
# frontend/pages/2_📚_Learn.py
import streamlit as st
from groq import Groq

try:
    api_key = st.secrets["GROQ_API_KEY"]  # Reads from frontend/.streamlit/secrets.toml
    groq_client = Groq(api_key=api_key)
except KeyError:
    st.error("⚠️ Groq API key not found in secrets.toml")
    st.stop()
```

### Streamlit's Search Order:
1. **App-level:** `frontend/.streamlit/secrets.toml` (checked first) ✅
2. **User-level:** `~/.streamlit/secrets.toml` (checked second)

## 📝 Important Notes

### When Running from Frontend Directory:
```bash
cd frontend
streamlit run Home.py
```
Streamlit looks for: `frontend/.streamlit/secrets.toml` ✅

### When Running from Root Directory:
```bash
streamlit run frontend/Home.py
```
Streamlit looks for: `.streamlit/secrets.toml`

### Best Practice:
Always run from the frontend directory:
```bash
cd frontend
streamlit run Home.py --server.port 8503
```

## 🔒 Security

### DO NOT:
- ❌ Commit secrets.toml to Git
- ❌ Share your API key publicly
- ❌ Use the same key in production

### DO:
- ✅ Add `.streamlit/secrets.toml` to `.gitignore`
- ✅ Use environment variables in production
- ✅ Rotate keys regularly
- ✅ Use different keys for dev/prod

### .gitignore Entry:
```gitignore
# Secrets
.streamlit/secrets.toml
frontend/.streamlit/secrets.toml
*.toml
```

## 🧪 Testing

### Verify Secrets Are Loaded:
```python
# Add to any page temporarily
if st.checkbox("Debug: Show Secrets Status"):
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        st.success(f"✅ API Key loaded: {api_key[:10]}...")
    except KeyError:
        st.error("❌ API Key not found")
```

### Test Groq Connection:
```python
# In Learn page
try:
    response = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": "Say hello"}],
        max_tokens=10
    )
    st.success("✅ Groq API connected successfully!")
except Exception as e:
    st.error(f"❌ Groq API error: {str(e)}")
```

## 🔧 Troubleshooting

### Error: "No secrets found"
**Solution:**
1. Check file exists: `frontend/.streamlit/secrets.toml`
2. Verify you're running from frontend directory
3. Restart Streamlit after creating/editing secrets

### Error: "KeyError: 'GROQ_API_KEY'"
**Solution:**
1. Check key name is exactly: `GROQ_API_KEY`
2. No quotes around the key name
3. Format: `GROQ_API_KEY = "your_key_here"`

### Error: "Invalid API key"
**Solution:**
1. Get new key from https://console.groq.com
2. Copy entire key including `gsk_` prefix
3. Paste in secrets.toml
4. Restart Streamlit

## 📦 Multiple Environments

### Development (Local):
```toml
# frontend/.streamlit/secrets.toml
GROQ_API_KEY = "gsk_dev_key_here"
```

### Production (Streamlit Cloud):
Add secrets in Streamlit Cloud dashboard:
1. Go to app settings
2. Click "Secrets"
3. Paste:
```toml
GROQ_API_KEY = "gsk_prod_key_here"
```

### Docker:
```dockerfile
# Pass as environment variable
ENV GROQ_API_KEY="gsk_key_here"
```

Then in code:
```python
import os
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
```

## ✅ Verification Checklist

- [x] File exists: `frontend/.streamlit/secrets.toml`
- [x] API key is valid (starts with `gsk_`)
- [x] Running from frontend directory
- [x] Streamlit restarted after changes
- [x] No syntax errors in secrets.toml
- [x] File not committed to Git

## 🎯 Current Status

**Location:** `frontend/.streamlit/secrets.toml` ✅
**API Key:** Loaded successfully ✅
**Groq Client:** Initialized ✅
**Learn Page:** Working ✅

## 📞 Support

If you still see errors:
1. Check the exact error message
2. Verify file path: `frontend/.streamlit/secrets.toml`
3. Test API key at https://console.groq.com
4. Clear browser cache
5. Restart Streamlit completely

---

**Status:** FIXED ✅
**Date:** March 3, 2026
**App Running:** http://localhost:8503
