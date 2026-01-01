# Training Data & Pipeline

> **Note:** This folder is excluded from version control (`.gitignore`) due to large file sizes.
> See the [main README](../README.md) for project overview and setup instructions.

---

## 📁 Contents

| File | Size | Description |
|------|------|-------------|
| `celeba_embeddings_with_all_labels.npz` | ~4.5MB | Pre-computed CLIP ViT embeddings + labels |
| `celeba_features.csv` | ~1.9MB | Raw CelebA feature annotations |
| `celeba_features_final.csv` | ~200KB | Cleaned feature dataset |
| `colorScheme.json` | ~2KB | Makeup color palette for recommendations |

---

## 🔄 Data Pipeline

### Step 1: Data Labelling (`recognition_00dataLabellingGemma3.ipynb`)

Uses **Gemma 3** (via Google AI) to automatically label facial attributes from CelebA images:

```
Input: CelebA face images
Output: Labels for skin_tone, hair_color, eye_color, eyebrow_color
```

**Process:**
1. Load images from CelebA dataset
2. Send to Gemma 3 with structured prompts
3. Parse responses into categorical labels
4. Save as `celeba_features.csv`

---

### Step 2: Data Cleaning (`recognition_01dataCleaning.ipynb`)

Cleans and standardizes the labeled data:

- Remove invalid/empty labels
- Standardize color names (e.g., "Dark Brown" → "dark brown")
- Handle missing values
- Filter low-quality samples
- Output: `celeba_features_final.csv`

---

### Step 3: Dataset Generation (`recognition_02datasetGen.ipynb`)

Generates training-ready embeddings:

```python
# For each image:
1. Load image
2. Preprocess with CLIPProcessor
3. Extract 512-dim embedding with CLIPModel
4. Store embedding + labels
```

**Output:** `celeba_embeddings_with_all_labels.npz`

```python
# NPZ structure:
{
    'embeddings': np.array([N, 512]),  # CLIP features
    'skin_tone': np.array([N]),        # Labels
    'hair_color': np.array([N]),
    'eye_color': np.array([N]),
    'eyebrow_color': np.array([N])
}
```

---

### Step 4: Model Training (`recognition_03modelTraining.ipynb`)

Trains Random Forest classifiers for each attribute:

```python
# For each attribute (skin_tone, hair_color, etc.):
1. Load embeddings + labels from .npz
2. Train/test split (80/20)
3. Apply SMOTE for class balancing
4. Train RandomForestClassifier
5. Optimize with GridSearchCV
6. Evaluate (accuracy, F1-score)
7. Save model as .pkl
```

**Hyperparameters tuned:**
- `n_estimators`: [100, 200, 300]
- `max_depth`: [10, 20, 30, None]
- `min_samples_split`: [2, 5, 10]

**Output:** `models/*.pkl`

---

### Step 5: Inference Testing (`recognition_04modelInference.ipynb`)

Tests the trained models on new images:

```python
1. Load image
2. Extract CLIP embedding
3. Load classifiers
4. Predict attributes
5. Display results
```

---

## 🎨 Color Scheme (`colorScheme.json`)

Defines makeup color palettes for recommendation matching:

```json
{
  "foundation_colors": [
    {"name": "Porcelain", "hex": "#F5E6D3"},
    {"name": "Ivory", "hex": "#F0E0C8"},
    ...
  ],
  "eyeshadow_colors": [...],
  "lipstick_colors": [...]
}
```

Used by `recommender_helper.py` to match detected skin/lip tones to product colors.

---

## 🔁 Reproducing the Pipeline

To regenerate training data from scratch:

1. **Download CelebA dataset** from [official source](http://mmlab.ie.cuhk.edu.hk/projects/CelebA.html)

2. **Run notebooks in order:**
   ```
   recognition_00dataLabellingGemma3.ipynb  → celeba_features.csv
   recognition_01dataCleaning.ipynb         → celeba_features_final.csv
   recognition_02datasetGen.ipynb           → celeba_embeddings_with_all_labels.npz
   recognition_03modelTraining.ipynb        → models/*.pkl
   ```

3. **Verify with inference notebook:**
   ```
   recognition_04modelInference.ipynb
   ```

---

## ⬅️ Back to Main

See [README.md](../README.md) for:
- Quick start guide
- Project structure
- API documentation
- Deployment instructions
