import os
import json
import torch
from transformers import pipeline
from PIL import Image
try:
    from src.preprocess import process_ct_slice
except ImportError:
    # Allow running from src directory or root
    from preprocess import process_ct_slice

# Global model variable to avoid reloading if used in a server later
pipe = None

def load_medgemma_model():
    global pipe
    if pipe is None:
        print("Loading MedGemma 1.5 4B-it...")
        model_id = "google/medgemma-1.5-4b-it"
        pipe = pipeline(
            "image-text-to-text",
            model=model_id,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
        print("Model loaded successfully.")
    return pipe

def analyze_kidney_scan(image_path_or_obj):
    """
    Analyzes a kidney CT scan using MedGemma 1.5.
    
    Args:
        image_path_or_obj: Path to DICOM/Image or PIL Image object.
    
    Returns:
        dict: Parsed JSON response from the model.
    """
    pipe = load_medgemma_model()
    
    # Process Image
    if isinstance(image_path_or_obj, str):
        if image_path_or_obj.lower().endswith('.dcm'):
            image = process_ct_slice(image_path_or_obj)
        else:
            image = Image.open(image_path_or_obj)
    else:
        image = image_path_or_obj

    # Agentic System Prompt
    system_prompt = (
        "Respond ONLY in JSON with keys: 'stone_found' (boolean), "
        "'size_mm' (string or number), 'location' (string), "
        "'urgency_level' (Low/Medium/High), 'patient_summary' (string)."
    )
    
    user_prompt = "Analyze this kidney CT. Locate any stones, estimate their size in mm, and describe the potential clinical impact."
    
    # Construct messages for chat template
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": f"{system_prompt}\n\n{user_prompt}"}
            ]
        }
    ]

    # Run Inference
    outputs = pipe(messages, max_new_tokens=512)
    generated_text = outputs[0]["generated_text"][-1]["content"]
    
    # Clean up response to get pure JSON if model adds markdown formatting
    cleaned_text = generated_text.replace("```json", "").replace("```", "").strip()
    
    try:
        result_json = json.loads(cleaned_text)
        return result_json
    except json.JSONDecodeError:
        print("Failed to parse JSON. Raw output:")
        print(generated_text)
        return {
            "error": "Failed to parse JSON",
            "raw_output": generated_text
        }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        if os.path.exists(input_file):
            print(f"Analyzing {input_file}...")
            result = analyze_kidney_scan(input_file)
            print(json.dumps(result, indent=2))
        else:
            print(f"File not found: {input_file}")
    else:
        print("Usage: python inference.py <path_to_dicom_or_image>")
