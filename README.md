# BogoBeauty Face Analyzer

<div align="center">
  <img src="assets/BB-Icon.jpg" alt="BogoBeauty Logo" width="120" style="border-radius: 50%;" />
  
  **🥈 2nd Place Winner**
  
  **AI-powered facial analysis for personalized beauty recommendations**
  
  *Summer Micro Design Challenge 2025 — South Korea*
  
  Hannam University • Singapore Institute of Technology • Rega Technical University
</div>

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with pip
- Node.js 18+ with npm
- Webcam

### Installation & Run

1. **Clone and navigate to the project:**
   ```bash
   cd BogoBeautyFaceAnalysis
   ```

2. **Install Python dependencies:**
   ```bash
   pip install fastapi uvicorn opencv-python numpy pillow torch transformers joblib pandas openpyxl mediapipe scikit-learn
   ```

3. **Generate sample data (if `Make-Up Recommendation.xlsx` is missing):**
   ```bash
   python generate_sample_data.py
   ```

4. **Run everything with one command:**
   ```bash
   start_server.bat
   ```
   
   Or manually:
   ```bash
   # Terminal 1: Backend
   python recognition_Service.py
   
   # Terminal 2: Frontend
   cd frontend
   npm install
   npm run dev
   ```

5. **Open in browser:**
   - Local: https://localhost:3000
   - Network: https://your-ip:3000 (for mobile access)

---

## 📁 Project Structure

```
BogoBeautyFaceAnalysis/
├── 📄 recognition_Service.py    # FastAPI backend server
├── 📄 recommender_helper.py     # MediaPipe face analysis utilities
├── 📄 generate_sample_data.py   # Creates sample makeup data
├── 📄 start_server.bat          # One-click startup script
├── 📄 BogoBeauty.html           # Technical documentation
│
├── 📁 frontend/                 # React + TypeScript + Tailwind
│   ├── src/
│   │   ├── App.tsx              # Main application
│   │   ├── api.ts               # API client
│   │   └── components/
│   │       ├── Camera.tsx       # Webcam capture
│   │       ├── Header.tsx       # App header
│   │       └── Results.tsx      # Analysis display
│   └── vite.config.ts           # Vite + HTTPS config
│
├── 📁 models/                   # Trained classifiers (.pkl)
│   ├── skin_tone_classifier.pkl
│   ├── hair_color_classifier.pkl
│   ├── eye_color_classifier.pkl
│   └── eyebrow_color_classifier.pkl
│
├── 📁 training_data/            # Training datasets
│   ├── celeba_features.csv
│   └── colorScheme.json
│
├── 📁 assets/                   # Images for documentation
│
└── 📁 recognition_*.ipynb       # Jupyter notebooks (training pipeline)
```

---

## 🔧 How It Works

### 1. Frontend (React + TypeScript)
- Captures webcam frames using `getUserMedia`
- Sends JPEG images to backend via `/api/predict`
- Displays detected features and product recommendations
- Mobile-responsive with tabbed navigation

### 2. Backend API (FastAPI)
- **Endpoint:** `POST /predict`
- Receives image → Extracts CLIP ViT embeddings → Runs classifiers
- Returns: skin tone, hair color, eyebrow color + product recommendations

### 3. ML Pipeline
- **Feature Extraction:** CLIP ViT (Vision Transformer)
- **Classifiers:** Random Forest (one per attribute)
- **Training:** SMOTE for class balancing + GridSearchCV optimization

---

## 📡 API Reference

### `POST /predict`

**Request:** `multipart/form-data` with image file

**Response:**
```json
{
  "skin_tone": "medium",
  "hair_color": "dark brown",
  "eyebrow_color": "brown",
  "recommended_foundation": "[{\"Brand Name\": \"...\", \"Product Name\": \"...\", \"Price\": 29.99, \"Ratings\": 4.5}]",
  "recommended_lipstick": "[{\"Brand Name\": \"...\", \"Product Name\": \"...\", \"Price\": 21.00, \"Ratings\": 4.7}]"
}
```

**Swagger Docs:** http://localhost:8000/docs

---

## 📱 Mobile Access

To access from your phone:

1. Ensure phone and PC are on the same WiFi
2. Allow ports 3000 & 8000 through Windows Firewall
3. Access via: `https://192.168.x.x:3000`
4. Accept the self-signed certificate warning
5. Grant camera permissions

---

## 📓 Training Notebooks

| Notebook | Purpose |
|----------|---------|
| `recognition_00dataLabellingGemma3.ipynb` | Data labelling with Gemma |
| `recognition_01dataCleaning.ipynb` | Data preprocessing |
| `recognition_02datasetGen.ipynb` | Dataset generation |
| `recognition_03modelTraining.ipynb` | Model training & evaluation |
| `recognition_04modelInference.ipynb` | Inference testing |

---

## 👤 Author

**Alexi George**

---

## 📄 License

This project was created for educational use and as part of the Summer Micro Design Challenge 2025.
