import re
from google import genai
import os

# Read API key from .streamlit/secrets.toml
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
MODEL_NAME = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

print('Using model:', MODEL_NAME)
resp = client.models.generate_content(model=MODEL_NAME, contents='Explain linear regression in one short paragraph.')

print('TYPE:', type(resp))
# Try common attrs
for attr in ('text', 'content', 'candidates', 'response', 'result'):
    print(attr, getattr(resp, attr, None))

# Show repr
print('REPR:\n', repr(resp))

# If candidates exist, inspect
try:
    c = resp.candidates
    print('Candidates len:', len(c))
    for i, cand in enumerate(c[:3]):
        print('--- candidate', i)
        print('text:', getattr(cand, 'text', None))
        # some shapes have content.parts
        parts = getattr(cand, 'content', None)
        print('content obj:', parts)
        try:
            parts_list = parts.parts
            print('parts count:', len(parts_list))
            for p in parts_list[:2]:
                print('part inline_data:', getattr(p, 'inline_data', None))
        except Exception as e:
            print('no parts:', e)
except Exception as e:
    print('No candidates:', e)
