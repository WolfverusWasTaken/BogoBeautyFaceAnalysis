import cv2
import numpy as np
import mediapipe as mp
from sklearn.cluster import KMeans
import json


"""
Utility functions for extracting facial colors and virtually applying makeup.

Overview
--------
This module provides helpers to:
1) derive representative skin and lip colors from an image using masks built
   from MediaPipe Face Mesh landmarks, and
2) pick complementary makeup colors from a JSON color scheme and render them
   back onto the image with controllable opacity.

Key Capabilities
----------------
- Load a color scheme JSON (foundation/eyeshadow/lipstick swatches).
- Convert between HEX and RGB, measure color distance/brightness, and darken colors.
- Detect face landmarks (MediaPipe Face Mesh) and build masks for: full face
  skin (eyes excluded) and lips.
- Compute mean skin/lip colors within those masks (with sensible fallbacks).
- Recommend makeup colors closest to the detected tones, ensuring lipstick is
  darker than the foundation via brightness checks.
- Overlay makeup colors onto the original image using alpha blending.

Main Functions
--------------
- load_color_scheme(path) -> dict
    Read a color palette JSON. Expected keys:
    { "foundation_colors": [{"hex": "#..."}, ...],
      "eyeshadow_colors" : [{"hex": "#..."}, ...],
      "lipstick_colors"  : [{"hex": "#..."}, ...] }

- hex_to_rgb(hex_str) / rgb_to_hex(rgb_tuple)
    Bidirectional HEX <-> RGB conversion.

- calculate_color_distance(color1, color2) -> float
    Euclidean distance in RGB space; used to find nearest swatch.

- calculate_brightness(rgb) -> float
    Perceived brightness (0.299 R + 0.587 G + 0.114 B).

- darken_color(rgb, factor=0.9) -> (r, g, b)
    Multiplies channels by factor, clamped to [0, 255].

- compute_mean_skin_color(frame, face_mask) -> (R, G, B)
    Averages non-black pixels from the masked region. Input frame is BGR;
    returns RGB. Falls back to (200, 180, 160) if the mask yields no pixels.

- compute_mean_lip_color(frame, lips_mask) -> (R, G, B)
    Same as above, tailored for lips; fallback (150, 50, 70).

- recommend_complementary_colors(average_skin_color, average_lip_color, scheme)
    Selects the closest foundation and eyeshadow to the detected skin color,
    and the closest lipstick to the detected lip color. Ensures the final
    lipstick brightness is darker than the foundation by iteratively darkening
    it (factor 0.9) until that condition holds.
    Returns: (foundation_rgb, eyeshadow_rgb, lipstick_rgb)

- read_landmarks(image) -> dict[int, (x, y)] | None
    Runs MediaPipe Face Mesh (refine_landmarks=True) and converts normalized
    landmarks to pixel coordinates for the first detected face. Returns a map
    of landmark index -> (x, y) or None if no face is found.

- add_reverse_mask_and_lips(mask_shape_like, idx_to_coordinates, face_connections, lip_connections)
    Builds two uint8 single-channel masks:
      * face_mask: fills defined facial regions (eyes removed) based on
        `face_points` indices.
      * lips_mask: fills the polygon defined by `lip_connections`.
    Returns: (face_mask, lips_mask)

- apply_makeup_directly(image, mask, makeup_color, opacity=0.3) -> image
    Alpha-blends `makeup_color` into `image` only where `mask != 0` using BGRA
    compositing. `image` is expected in BGR; returns BGR.

Data & Landmarks
----------------
- Uses MediaPipe Face Mesh landmark indices for face/eyes/lips/eyebrows defined
  in `face_points`. Eyes are excluded from the face mask via `features_to_remove`.
- Inputs are OpenCV images in BGR. Functions that return colors document whether
  they return RGB (most color utilities) or operate in BGR (masking step).

Assumptions & Fallbacks
-----------------------
- If no face/lips pixels are available (mask empty or black), mean color
  functions return predefined fallback tones.
- The color scheme JSON must provide HEX strings for each category.
- Only the first detected face is processed.

Typical Workflow
----------------
1) Detect landmarks: `idx = read_landmarks(image)`
2) Build masks: `face_mask, lips_mask = add_reverse_mask_and_lips(...)`
3) Measure colors: `skin_rgb = compute_mean_skin_color(image, face_mask)`
                   `lip_rgb  = compute_mean_lip_color(image, lips_mask)`
4) Pick swatches:  `fnd, eye, lip = recommend_complementary_colors(skin_rgb, lip_rgb, scheme)`
5) Render:         `image = apply_makeup_directly(image, face_mask, fnd, opacity=...)`
                   `image = apply_makeup_directly(image, lips_mask, lip, opacity=...)`

Notes
-----
- OpenCV uses BGR; conversions are handled internally where needed.
- MediaPipe requires RGB input for processing; ensure your pipeline passes the
  correct format if you modify `read_landmarks`.
- Opacity in `apply_makeup_directly` controls both the blend weight and the
  per-pixel alpha used to construct the overlay.

Dependencies
------------
- OpenCV (cv2), NumPy, MediaPipe, scikit-learn (for KMeans if needed), and json.
"""

# Load the JSON file
def load_color_scheme(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Convert HEX color to RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Convert RGB tuple to HEX color
def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


# Calculate the Euclidean distance between two RGB colors
def calculate_color_distance(color1, color2):
    return np.sqrt(np.sum((np.array(color1) - np.array(color2)) ** 2))

# Function to calculate brightness of a color (perceived brightness formula)
def calculate_brightness(color):
    return 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]

# Function to darken a color by adjusting its brightness
def darken_color(color, factor=0.9):
    """
    Darken a given color by reducing its brightness.
    """
    return tuple(max(0, int(c * factor)) for c in color)

def compute_mean_skin_color(frame, face_mask):
    """
    Compute the mean skin color from the face region using the mask.
    Returns (R, G, B) tuple.
    """
    # Ensure mask is single-channel uint8 in 0/255
    if face_mask.ndim == 3:
        face_mask = cv2.cvtColor(face_mask, cv2.COLOR_BGR2GRAY)
    if face_mask.dtype != np.uint8:
        face_mask = face_mask.astype(np.uint8)
    if face_mask.max() == 1:  # boolean or 0/1 mask
        face_mask = face_mask * 255

    # Apply mask correctly
    masked = cv2.bitwise_and(frame, frame, mask=face_mask)

    # Extract only non-black pixels
    pixels = masked[np.where((masked > [0, 0, 0]).all(axis=2))]
    if len(pixels) == 0:
        return (200, 180, 160)  # fallback

    mean_color = np.mean(pixels, axis=0)  # BGR
    return (int(mean_color[2]), int(mean_color[1]), int(mean_color[0]))  # to RGB


def compute_mean_lip_color(frame, lips_mask):
    """
    Compute the mean lip color from the lips region using the mask.
    Returns (R, G, B) tuple.
    """
    # Ensure mask is single-channel uint8 in 0/255
    if lips_mask.ndim == 3:
        lips_mask = cv2.cvtColor(lips_mask, cv2.COLOR_BGR2GRAY)
    if lips_mask.dtype != np.uint8:
        lips_mask = lips_mask.astype(np.uint8)
    if lips_mask.max() == 1:  # boolean or 0/1 mask
        lips_mask = lips_mask * 255

    # Apply mask correctly
    masked = cv2.bitwise_and(frame, frame, mask=lips_mask)

    # Extract only non-black pixels
    pixels = masked[np.where((masked > [0, 0, 0]).all(axis=2))]
    if len(pixels) == 0:
        return (150, 50, 70)  # fallback pinkish tone

    mean_color = np.mean(pixels, axis=0)  # BGR
    return (int(mean_color[2]), int(mean_color[1]), int(mean_color[0]))  # to RGB



# Function to recommend the most complementary colors
def recommend_complementary_colors(average_skin_color, average_lip_color, color_scheme):
    # Extract all color categories from the color scheme
    foundation_colors = color_scheme["foundation_colors"]
    eyeshadow_colors = color_scheme["eyeshadow_colors"]
    lipstick_colors = color_scheme["lipstick_colors"]
    
    # Find the closest foundation color to the average skin color
    closest_foundation = min(foundation_colors, key=lambda f: calculate_color_distance(hex_to_rgb(f['hex']), average_skin_color))
    
    # Find the closest eyeshadow color to the average skin color
    closest_eyeshadow = min(eyeshadow_colors, key=lambda e: calculate_color_distance(hex_to_rgb(e['hex']), average_skin_color))
    
    # Calculate the brightness of the foundation color
    foundation_brightness = calculate_brightness(hex_to_rgb(closest_foundation['hex']))
    
    # Find the closest lipstick color to the average lip color
    closest_lipstick = min(lipstick_colors, key=lambda l: calculate_color_distance(hex_to_rgb(l['hex']), average_lip_color))
    lipstick_color = hex_to_rgb(closest_lipstick['hex'])
    
    # Calculate brightness of the selected lipstick color
    lipstick_brightness = calculate_brightness(lipstick_color)
    
    # Darken the lipstick color until it is darker than the foundation
    while lipstick_brightness >= foundation_brightness:
        lipstick_color = darken_color(lipstick_color, factor=0.9)  # Darken by 10% each iteration
        lipstick_brightness = calculate_brightness(lipstick_color)
    
    return hex_to_rgb(closest_foundation['hex']), hex_to_rgb(closest_eyeshadow['hex']), lipstick_color


# Initialize MediaPipe functions
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# Landmarks of features from MediaPipe
face_points = {
    "BLUSH_LEFT": [50],
    "BLUSH_RIGHT": [280],
    "LEFT_EYE": [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7, 33],
    "RIGHT_EYE": [362, 298, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382, 362],
    "EYELINER_LEFT": [243, 112, 26, 22, 23, 24, 110, 25, 226, 130, 33, 7, 163, 144, 145, 153, 154, 155, 133, 243],
    "EYELINER_RIGHT": [463, 362, 382, 381, 380, 374, 373, 390, 249, 263, 359, 446, 255, 339, 254, 253, 252, 256, 341, 463],
    "EYESHADOW_LEFT": [226, 247, 30, 29, 27, 28, 56, 190, 243, 173, 157, 158, 159, 160, 161, 246, 33, 130, 226],
    "EYESHADOW_RIGHT": [463, 414, 286, 258, 257, 259, 260, 467, 446, 359, 263, 466, 388, 387, 386, 385, 384, 398, 362, 463],
    "FACE": [152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109, 10, 338, 297, 332, 284, 251, 389, 454, 323, 401, 361, 435, 288, 397, 365, 379, 378, 400, 377, 152],
    "LIP_UPPER": [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 308, 415, 310, 312, 13, 82, 81, 80, 191, 78],
    "LIP_LOWER": [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 402, 317, 14, 87, 178, 88, 95, 78, 61],
    "EYEBROW_LEFT": [55, 107, 66, 105, 63, 70, 46, 53, 52, 65, 55],
    "EYEBROW_RIGHT": [285, 336, 296, 334, 293, 300, 276, 283, 295, 285]
}

# Features to remove (eyes, lips, etc.)
features_to_remove = [
    "LEFT_EYE", "RIGHT_EYE"
]

# Function to apply makeup to the main feed using BGRA with opacity
def apply_makeup_directly(image: np.array, mask: np.array, makeup_color: tuple, opacity: float = 0.3):
    """
    Apply makeup to the specified mask area by filling it with the given color.
    Opacity is the level of transparency for the makeup, where 0 is fully transparent and 1 is fully opaque.
    """
    # Convert the makeup color to BGRA (adding an alpha channel for transparency)
    makeup_bgra = makeup_color + (int(opacity * 255),)  # Set the alpha channel based on opacity

    # Create an empty BGRA image with the same size as the input image
    makeup_layer = np.zeros((image.shape[0], image.shape[1], 4), dtype=np.uint8)

    # Apply the makeup color to the face/lips region based on the mask (keep only the mask area)
    makeup_layer[mask != 0] = makeup_bgra  # Fill makeup color in the masked region

    # Convert the original image to BGRA (if not already)
    image_bgra = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    # Overlay the makeup layer onto the original image with the specified opacity
    image_bgra = cv2.addWeighted(image_bgra, 1 - opacity, makeup_layer, opacity, 0)

    # Convert back to BGR before returning (optional, depending on your needs)
    return cv2.cvtColor(image_bgra, cv2.COLOR_BGRA2BGR)

# Function to add reverse mask (remove features except the face) and mask for lips
def add_reverse_mask_and_lips(mask: np.array, idx_to_coordinates: dict, face_connections: list, lip_connections: list):
    """
    Remove features like eyes and keep only the face skin.
    Also, create a mask for the lips to apply makeup.
    """
    # Create a blank (black) single-channel mask (8-bit single channel)
    face_mask = np.zeros(mask.shape[:2], dtype=np.uint8)
    lips_mask = np.zeros(mask.shape[:2], dtype=np.uint8)

    # Keep the face region, remove the rest
    for feature, feature_points in face_points.items():
        if feature not in features_to_remove:
            points = [idx_to_coordinates[idx] for idx in feature_points if idx in idx_to_coordinates]
            if points:
                cv2.fillPoly(face_mask, [np.array(points)], 255)  # Keep face as white region

    # Create lips mask
    lips_points = []
    for idx in lip_connections:
        if idx in idx_to_coordinates:
            lips_points.append(idx_to_coordinates[idx])
    if lips_points:
        cv2.fillPoly(lips_mask, [np.array(lips_points)], 255)  # Keep lips as white region

    return face_mask, lips_mask

# Function to read landmarks from the image
def read_landmarks(image: np.array):
    """
    Process the image and detect facial landmarks.
    """
    landmark_cordinates = {}
    with mp_face_mesh.FaceMesh(refine_landmarks=True) as face_mesh:
        results = face_mesh.process(image)
        
        # Check if any faces were detected
        if results.multi_face_landmarks is None:
            return None
        
        # Extract the first face's landmarks
        face_landmarks = results.multi_face_landmarks[0].landmark

        # Convert normalized points to pixel coordinates
        for idx, landmark in enumerate(face_landmarks):
            landmark_px = mp_drawing._normalized_to_pixel_coordinates(
                landmark.x, landmark.y, image.shape[1], image.shape[0]
            )
            if landmark_px:
                landmark_cordinates[idx] = landmark_px
    return landmark_cordinates
