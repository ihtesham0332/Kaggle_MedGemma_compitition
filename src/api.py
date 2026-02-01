from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import uvicorn
import shutil
import os
import tempfile
from src.inference import analyze_kidney_scan

app = FastAPI(title="MedGemma Kidney Analysis API")

@app.get("/")
def read_root():
    return {"message": "Kidney Stone Analysis API is running."}

@app.post("/analyze")
async def analyze_scan(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        # Run inference
        result = analyze_kidney_scan(tmp_path)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        # Cleanup
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)
