// API Types
export interface Product {
    "Brand Name": string;
    "Product Name": string;
    Price: number;
    Ratings: number;
}

export interface PredictionResult {
    hair_color: string;
    eyebrow_color: string;
    skin_tone: string;
    eye_color?: string;
    recommended_lipstick: string; // JSON string
    recommended_foundation: string; // JSON string
}

export interface ParsedResult {
    hair_color: string;
    eyebrow_color: string;
    skin_tone: string;
    eye_color?: string;
    lipsticks: Product[];
    foundations: Product[];
}

// API Client
const API_BASE = "/api";

export async function analyzeFace(imageBlob: Blob): Promise<ParsedResult> {
    const formData = new FormData();
    formData.append("file", imageBlob, "capture.jpg");

    const response = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }

    const data: PredictionResult = await response.json();

    // Parse the JSON strings for recommendations
    const lipsticks: Product[] = data.recommended_lipstick
        ? JSON.parse(data.recommended_lipstick)
        : [];
    const foundations: Product[] = data.recommended_foundation
        ? JSON.parse(data.recommended_foundation)
        : [];

    return {
        hair_color: data.hair_color,
        eyebrow_color: data.eyebrow_color,
        skin_tone: data.skin_tone,
        eye_color: data.eye_color,
        lipsticks,
        foundations,
    };
}
