# ==========================================
# PASTE THIS INTO A KAGGLE NOTEBOOK (Settings: GPU T4 x2, Internet ON)
# ==========================================

# 1. Install Dependencies
!pip install -q fastapi uvicorn python-multipart pyngrok transformers accelerate bitsandbytes

# 2. Authenticate with Hugging Face (Add your token in Secrets as HF_TOKEN or paste here)
import os
from huggingface_hub import login
from kaggle_secrets import UserSecretsClient

try:
    user_secrets = UserSecretsClient()
    hf_token = user_secrets.get_secret("HF_TOKEN")
    login(token=hf_token)
except:
    # Manual fallback - REPLACE WITH YOUR TOKEN IF NEEDED
    # login(token="hf_YOUR_TOKEN_HERE") 
    print("Please add your HF_TOKEN to Kaggle Secrets!") 

# 3. Define the Backend Code (Same as local src/api.py + src/inference.py combined)
import torch
from transformers import pipeline
from PIL import Image
import io
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import uvicorn
import nest_asyncio
from pyngrok import ngrok

# --- Inference Logic ---
pipe = None
def load_model():
    global pipe
    if pipe is None:
        print("Loading MedGemma on GPU...")
        pipe = pipeline(
            "image-text-to-text",
            model="google/medgemma-1.5-4b-it",
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
    return pipe

def analyze_image(image_bytes):
    model = load_model()
    image = Image.open(io.BytesIO(image_bytes))
    
    system_prompt = (
        "Respond ONLY in JSON with keys: 'stone_found' (boolean), "
        "'size_mm' (string or number), 'location' (string), "
        "'urgency_level' (Low/Medium/High), 'patient_summary' (string)."
    )
    user_prompt = "Analyze this kidney CT. Locate any stones, estimate their size in mm."
    
    messages = [{"role": "user", "content": [{"type": "image", "image": image}, {"type": "text", "text": f"{system_prompt}\n\n{user_prompt}"}]}]
    
    outputs = model(messages, max_new_tokens=512)
    generated_text = outputs[0]["generated_text"][-1]["content"]
    
    # Simple cleanup
    import json
    cleaned = generated_text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except:
        return {"raw_output": generated_text}

# --- API Server ---
app = FastAPI()

@app.get("/")
def home():
    return {"status": "Running on Kaggle GPU", "gpu": torch.cuda.get_device_name(0)}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    contents = await file.read()
    result = analyze_image(contents)
    return JSONResponse(content=result)

@app.post("/chat")
async def chat(file: UploadFile = File(...), question: str = Form(...), context: str = Form(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    model = load_model()
    
    prompt = f"Context from previous analysis: {context}\n\nUser Question: {question}\n\nAnswer the user's question helpfuly and concisely based on the image and context."
    messages = [{"role": "user", "content": [{"type": "image", "image": image}, {"type": "text", "text": prompt}]}]
    
    outputs = model(messages, max_new_tokens=256)
    answer = outputs[0]["generated_text"][-1]["content"]
    return JSONResponse(content={"answer": answer})

# 4. Start Server with Ngrok
# REPLACE 'YOUR_NGROK_TOKEN' with your actual token from https://dashboard.ngrok.com/get-started/your-authtoken
# If you don't have one, get it for free.
NGROK_TOKEN = "2Rw0NFKQwKWKdOJFGiVWv0CYb66_4oJujXyaJZ8GULnNvcU6m" 

if NGROK_TOKEN == "YOUR_NGROK_TOKEN_HERE":
    print("⚠️ PLEASE ENTER YOUR NGROK TOKEN IN THE SCRIPT ⚠️")
else:
    ngrok.set_auth_token(NGROK_TOKEN)
    public_url = ngrok.connect(8000).public_url
    print(f"🚀 BACKEND RUNNING AT: {public_url}")
    print("Copy this URL and paste it into your Local Streamlit App!")
    
    import uvicorn
    # nest_asyncio is already applied
    config = uvicorn.Config(app, port=8000, loop="asyncio")
    server = uvicorn.Server(config)
    import asyncio
    await server.serve()
