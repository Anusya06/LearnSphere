import re
from google import genai

# Read API key
import os
key = None
with open('.streamlit/secrets.toml', 'r') as f:
    txt = f.read()
    m = re.search(r'GEMINI_API_KEY\s*=\s*"([^"]+)"', txt)
    if m:
        key = m.group(1)

if not key:
    print('NO_KEY')
    raise SystemExit(1)

client = genai.Client(api_key=key)

# Try multiple listing methods
models = None
try:
    models = client.list_models()
except Exception:
    try:
        models = client.models.list()
    except Exception as e:
        print('Failed to list models:', e)
        raise

for m in models:
    name = getattr(m, 'name', str(m))
    methods = getattr(m, 'supported_generation_methods', getattr(m, 'methods', None))
    print('Model:', name)
    print('Methods:', methods)
    print('---')
