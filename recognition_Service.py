from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import cv2
import numpy as np
from PIL import Image
import torch
import joblib
from transformers import CLIPProcessor, CLIPModel
import pandas as pd
import re
import os
import sys

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from recommender_helper import *
from pprint import pprint

"""
Attribute Recognition & Makeup Recommendation API (FastAPI)

Overview
--------
This service exposes a single POST /predict endpoint that:
1) accepts an uploaded face image,
2) extracts a CLIP image embedding,
3) predicts appearance attributes via pre-trained scikit-learn classifiers, and
4) returns lightweight product recommendations (foundation & lipstick) filtered
   from Excel sheets.

Loaded Assets
-------------
- Datasets (Excel):
  * "Make-Up Recommendation.xlsx" sheet "Foundation" and "Lipstick"
- Models (joblib):
  * eye_color_classifier.pkl
  * hair_color_classifier.pkl
  * eyebrow_color_classifier.pkl
  * skin_tone_classifier.pkl
- CLIP:
  * Model/processor: "openai/clip-vit-base-patch32" (Hugging Face Transformers)

Label Mappings
--------------
`get_labels()` defines string↔int label spaces for:
  - eye_color:  {'blue', 'brown', 'dark', 'dark brown', 'gray', 'green'}
  - hair_color: {'black', 'blonde', 'brown', 'dark', 'dark brown', 'gray', 'light brown', 'red'}
  - eyebrow_color: {'black', 'blonde', 'brown', 'dark', 'dark brown', 'gray'}
  - skin_tone: {'dark', 'fair', 'light', 'medium'}
The module also constructs inverse mappings (id→name) for decoding predictions.

Recommendations
---------------
Two helpers select top products by season and skin type:
  - recommend_lipstick(season, skin_type, sample_k=3, seed=None)
  - recommend_foundation(season, skin_type, sample_k=3, seed=None)

Internally `_filter_and_serialize`:
  - Filters rows via regex on columns:
        "Suitable for which weather" (season)
        "Use for which Skin Type"   (skin type)
  - Sorts by Ratings (desc) then Price (asc).
  - Takes the top `pool_n` (default 10) and returns a random sample of `sample_k`
    (default 3), serialized as JSON (list of {Brand Name, Product Name, Price, Ratings}).
  - If no matches, returns "[]".

API
---
POST /predict
  - Request: multipart/form-data with a single image file field named "file".
  - Processing:
      1) Read bytes → NumPy → OpenCV BGR image.
      2) Convert to PIL (RGB) and preprocess with CLIPProcessor.
      3) Get CLIP image features (no grad), flatten to 1D embedding.
      4) Run four classifiers on the embedding to predict:
           eye_color, hair_color, eyebrow_color, skin_tone
         (eye_color is currently computed but commented out in the response.)
      5) Return decoded labels plus two product recommendation lists:
           - recommended_lipstick: recommend_lipstick("all seasons", "Dry")
           - recommended_foundation: recommend_foundation("Summer", "Oily")
  - Response (application/json), example:
      {
        "hair_color": "dark brown",
        "eyebrow_color": "brown",
        "skin_tone": "medium",
        "recommended_lipstick": "[{\"Brand Name\":\"...\",\"Product Name\":\"...\",\"Price\":...,\"Ratings\":...}, ...]",
        "recommended_foundation": "[{\"Brand Name\":\"...\",\"Product Name\":\"...\",\"Price\":...,\"Ratings\":...}, ...]"
      }
    Note: the recommendation fields are JSON-encoded strings; parse them client-side
    if you need arrays.

Running
-------
- Start locally:
    uvicorn main:app --host 0.0.0.0 --port 8000
  (Or run this module directly; it calls uvicorn.run(...) in __main__.)

- Example request (curl):
    curl -X POST http://localhost:8000/predict \
      -F "file=@/path/to/face.jpg"

Dependencies
------------
- fastapi, uvicorn
- opencv-python (cv2), numpy, pillow (PIL)
- torch, transformers (CLIPModel, CLIPProcessor)
- scikit-learn (joblib)
- pandas, openpyxl (for reading .xlsx)
- recommender_helper (must be importable in PYTHONPATH)

Assumptions & Notes
-------------------
- Classifiers were trained on CLIP (ViT-B/32) image embeddings.
- Only the first (and only) uploaded image is processed.
- The service prints basic progress logs on import (data/models/CLIP).
- Excel sheets must include the columns named in COLS:
    "Brand Name", "Product Name", "Price", "Ratings",
    "Suitable for which weather", "Use for which Skin Type"
- Ratings/Price columns are coerced to numeric for sorting.
- For deterministic sampling, pass a `seed` to the recommend_* helpers (the
  endpoint currently uses default randomness).
- Eye color prediction is computed but omitted from the JSON; uncomment in the
  response if required.

Error Handling
--------------
- Any exception in /predict returns HTTP 500 with {"error": "..."}.
  Verify model files, Excel sheets, and Hugging Face assets are available.

Security & Performance Tips
---------------------------
- Validate and size-limit uploads in production.
- Consider GPU acceleration for CLIP if available (move tensors to CUDA).
- Cache CLIP processor/model and classifiers (already module-level).
- If recommendations should be structured, return parsed lists instead of
  JSON strings (adjust serialization accordingly).
"""


# -----------------------------
# Load models and mappings
# -----------------------------

# Load datasets (using absolute paths)
data_path = os.path.join(SCRIPT_DIR, "Make-Up Recommendation.xlsx")
foundation_data = pd.read_excel(data_path, sheet_name="Foundation")
lipstick_data   = pd.read_excel(data_path, sheet_name="Lipstick")
print("Load data")

# Classifiers (using absolute paths from models folder)
models_dir = os.path.join(SCRIPT_DIR, 'models')
eye_color_classifier = joblib.load(os.path.join(models_dir, 'eye_color_classifier.pkl'))
hair_color_classifier = joblib.load(os.path.join(models_dir, 'hair_color_classifier.pkl'))
eyebrow_color_classifier = joblib.load(os.path.join(models_dir, 'eyebrow_color_classifier.pkl'))
skin_tone_classifier = joblib.load(os.path.join(models_dir, 'skin_tone_classifier.pkl'))
print("Load classifiers")

# CLIP
model_name = "openai/clip-vit-base-patch32"
clip_model = CLIPModel.from_pretrained(model_name)
clip_processor = CLIPProcessor.from_pretrained(model_name)
print("Load data")

# Function to extract the correct label mappings from the CSV file
def get_labels():
    eye_color_label = {'blue': 0, 'brown': 1, 'dark': 2, 'dark brown': 3, 'gray': 4, 'green': 5}
    hair_color_label = {'black': 0, 'blonde': 1, 'brown': 2, 'dark': 3, 'dark brown': 4, 'gray': 5, 'light brown': 6, 'red': 7}
    eyebrow_color_label = {'black': 0, 'blonde': 1, 'brown': 2, 'dark': 3, 'dark brown': 4, 'gray': 5}
    skin_tone_label = {'dark': 0, 'fair': 1, 'light': 2, 'medium': 3}
    return eye_color_label, hair_color_label, eyebrow_color_label, skin_tone_label

COLS = {
    "season": "Suitable for which weather",
    "skin":   "Use for which Skin Type",
    "brand":  "Brand Name",
    "name":   "Product Name",
    "price":  "Price",
    "rating": "Ratings",
}

def _filter_and_serialize(df, season, skin_type, pool_n=10, sample_k=3, seed=None):
    season_col = COLS["season"]
    skin_col   = COLS["skin"]

    df = df.copy()
    for c in [season_col, skin_col]:
        df[c] = df[c].astype(str).str.strip()

    season_pat = rf"\b{re.escape(season.strip())}\b"
    skin_pat   = rf"\b{re.escape(skin_type.strip())}\b"

    season_mask = df[season_col].str.contains(season_pat, case=False, na=False)
    skin_mask   = df[skin_col].str.contains(skin_pat, case=False, na=False)
    filtered = df[season_mask & skin_mask].copy()

    # Sort: Ratings desc, Price asc
    if COLS["rating"] in filtered.columns:
        filtered[COLS["rating"]] = pd.to_numeric(filtered[COLS["rating"]], errors="coerce")
    if COLS["price"] in filtered.columns:
        filtered[COLS["price"]] = pd.to_numeric(filtered[COLS["price"]], errors="coerce")

    filtered = filtered.sort_values(by=[COLS["rating"], COLS["price"]], ascending=[False, True])

    if filtered.empty:
        return "[]"

    keep = [c for c in [COLS["brand"], COLS["name"], COLS["price"], COLS["rating"]] if c in filtered.columns]

    # Take top `pool_n`, then randomly sample `sample_k` from that pool
    pool = filtered[keep].head(int(pool_n))
    if pool.empty:
        return "[]"

    k = min(len(pool), int(sample_k))
    sampled = pool.sample(n=k, replace=False, random_state=(None if seed is None else int(seed)))

    return sampled.to_json(orient="records")

def recommend_lipstick(season, skin_type, sample_k=3, seed=None):
    return _filter_and_serialize(lipstick_data, season, skin_type, pool_n=10, sample_k=sample_k, seed=seed)

def recommend_foundation(season, skin_type, sample_k=3, seed=None):
    return _filter_and_serialize(foundation_data, season, skin_type, pool_n=10, sample_k=sample_k, seed=seed)



# Function to generate label mappings for each attribute
eye_color_mapping, hair_color_mapping, eyebrow_color_mapping, skin_tone_mapping = get_labels()

# Invert mappings for ID -> label
eye_color_inv = {v:k for k,v in eye_color_mapping.items()}
hair_color_inv = {v:k for k,v in hair_color_mapping.items()}
eyebrow_color_inv = {v:k for k,v in eyebrow_color_mapping.items()}
skin_tone_inv = {v:k for k,v in skin_tone_mapping.items()}

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(title="Attribute Recognition Microservice API")

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("FastAPI app initialized with CORS")

@app.post("/predict")
async def predict_attributes(file: UploadFile = File(...)):
    try:
        # Read image file
        img_bytes = await file.read()
        np_img = np.frombuffer(img_bytes, np.uint8)
        cv_img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        
        # Convert to PIL for CLIP
        pil_image = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
        
        # Preprocess for CLIP
        inputs = clip_processor(images=pil_image, return_tensors="pt")
        
        # Get embeddings
        with torch.no_grad():
            embeddings = clip_model.get_image_features(**inputs)
        embeddings = embeddings.flatten().numpy()
        
        # Predict
        eye_color_pred = eye_color_classifier.predict([embeddings])[0]
        hair_color_pred = hair_color_classifier.predict([embeddings])[0]
        eyebrow_color_pred = eyebrow_color_classifier.predict([embeddings])[0]
        skin_tone_pred = skin_tone_classifier.predict([embeddings])[0]

        
        # Map IDs to names
        result = {
            # "eye_color": eye_color_inv.get(eye_color_pred, "Unknown"),
            "hair_color": hair_color_inv.get(hair_color_pred, "Unknown"),
            "eyebrow_color": eyebrow_color_inv.get(eyebrow_color_pred, "Unknown"),
            "skin_tone": skin_tone_inv.get(skin_tone_pred, "Unknown"),
            "recommended_lipstick": recommend_lipstick("all seasons", "Dry"),
            "recommended_foundation": recommend_foundation("Summer", "Oily"),
        }

        pprint(result)
        
        return JSONResponse(content=result)
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    print("\n" + "="*50)
    print("  BogoBeauty Face Analyzer API")
    print("="*50)
    print("  Server starting on: http://localhost:8000")
    print("  API docs available: http://localhost:8000/docs")
    print("="*50 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)