"""
Script to generate sample Make-Up Recommendation data.
Run this once to create the Excel file needed by the API.
"""

import pandas as pd

# Sample Foundation Data
foundation_data = [
    {"Brand Name": "Maybelline", "Product Name": "Fit Me Matte + Poreless Foundation", "Price": 8.99, "Ratings": 4.5, "Suitable for which weather": "all seasons, Summer, Winter", "Use for which Skin Type": "Oily, Combination"},
    {"Brand Name": "L'Oreal", "Product Name": "True Match Super-Blendable Foundation", "Price": 10.99, "Ratings": 4.6, "Suitable for which weather": "all seasons, Spring, Fall", "Use for which Skin Type": "Normal, Dry"},
    {"Brand Name": "MAC", "Product Name": "Studio Fix Fluid SPF 15", "Price": 35.00, "Ratings": 4.7, "Suitable for which weather": "all seasons, Summer", "Use for which Skin Type": "Oily, Normal"},
    {"Brand Name": "Fenty Beauty", "Product Name": "Pro Filt'r Soft Matte Foundation", "Price": 40.00, "Ratings": 4.8, "Suitable for which weather": "all seasons, Summer, Spring", "Use for which Skin Type": "Oily, Combination, Normal"},
    {"Brand Name": "NARS", "Product Name": "Natural Radiant Longwear Foundation", "Price": 49.00, "Ratings": 4.6, "Suitable for which weather": "all seasons, Winter", "Use for which Skin Type": "Dry, Normal"},
    {"Brand Name": "Estee Lauder", "Product Name": "Double Wear Stay-in-Place Foundation", "Price": 48.00, "Ratings": 4.9, "Suitable for which weather": "all seasons, Summer, Winter", "Use for which Skin Type": "Oily, Combination"},
    {"Brand Name": "IT Cosmetics", "Product Name": "CC+ Cream with SPF 50+", "Price": 44.00, "Ratings": 4.5, "Suitable for which weather": "all seasons, Summer", "Use for which Skin Type": "Dry, Normal, Sensitive"},
    {"Brand Name": "Covergirl", "Product Name": "Clean Fresh Skin Milk Foundation", "Price": 13.99, "Ratings": 4.3, "Suitable for which weather": "all seasons, Spring, Fall", "Use for which Skin Type": "Normal, Combination"},
    {"Brand Name": "NYX", "Product Name": "Born To Glow! Naturally Radiant Foundation", "Price": 11.00, "Ratings": 4.4, "Suitable for which weather": "all seasons, Fall, Winter", "Use for which Skin Type": "Dry, Normal"},
    {"Brand Name": "Rare Beauty", "Product Name": "Liquid Touch Weightless Foundation", "Price": 29.00, "Ratings": 4.7, "Suitable for which weather": "all seasons, Summer, Spring", "Use for which Skin Type": "All, Normal, Oily, Dry"},
    {"Brand Name": "Charlotte Tilbury", "Product Name": "Airbrush Flawless Foundation", "Price": 46.00, "Ratings": 4.8, "Suitable for which weather": "all seasons, Winter, Fall", "Use for which Skin Type": "Normal, Dry, Combination"},
    {"Brand Name": "Clinique", "Product Name": "Even Better Clinical Serum Foundation", "Price": 36.00, "Ratings": 4.5, "Suitable for which weather": "all seasons", "Use for which Skin Type": "Normal, Oily, Combination"},
]

# Sample Lipstick Data
lipstick_data = [
    {"Brand Name": "MAC", "Product Name": "Matte Lipstick - Ruby Woo", "Price": 21.00, "Ratings": 4.7, "Suitable for which weather": "all seasons, Winter", "Use for which Skin Type": "All, Dry, Normal"},
    {"Brand Name": "Maybelline", "Product Name": "SuperStay Matte Ink", "Price": 9.49, "Ratings": 4.6, "Suitable for which weather": "all seasons, Summer, Spring", "Use for which Skin Type": "All, Oily, Normal"},
    {"Brand Name": "Charlotte Tilbury", "Product Name": "Matte Revolution Lipstick - Pillow Talk", "Price": 34.00, "Ratings": 4.8, "Suitable for which weather": "all seasons, Fall, Winter", "Use for which Skin Type": "Dry, Normal"},
    {"Brand Name": "Fenty Beauty", "Product Name": "Gloss Bomb Universal Lip Luminizer", "Price": 21.00, "Ratings": 4.5, "Suitable for which weather": "all seasons, Summer", "Use for which Skin Type": "All, Normal"},
    {"Brand Name": "NARS", "Product Name": "Audacious Lipstick - Anita", "Price": 34.00, "Ratings": 4.6, "Suitable for which weather": "all seasons, Spring, Fall", "Use for which Skin Type": "Normal, Dry"},
    {"Brand Name": "NYX", "Product Name": "Soft Matte Lip Cream", "Price": 6.50, "Ratings": 4.4, "Suitable for which weather": "all seasons, Summer, Spring", "Use for which Skin Type": "All, Oily, Normal"},
    {"Brand Name": "Rare Beauty", "Product Name": "Soft Pinch Liquid Blush", "Price": 23.00, "Ratings": 4.7, "Suitable for which weather": "all seasons", "Use for which Skin Type": "All"},
    {"Brand Name": "L'Oreal", "Product Name": "Colour Riche Ultra Matte Lipstick", "Price": 10.99, "Ratings": 4.3, "Suitable for which weather": "all seasons, Winter, Fall", "Use for which Skin Type": "Dry, Normal, Combination"},
    {"Brand Name": "Dior", "Product Name": "Addict Lip Glow", "Price": 38.00, "Ratings": 4.8, "Suitable for which weather": "all seasons, Summer, Spring", "Use for which Skin Type": "All, Dry"},
    {"Brand Name": "Too Faced", "Product Name": "Lip Injection Maximum Plump", "Price": 29.00, "Ratings": 4.4, "Suitable for which weather": "all seasons, Winter", "Use for which Skin Type": "Dry, Normal"},
    {"Brand Name": "Clinique", "Product Name": "Pop Lip Colour + Primer", "Price": 22.00, "Ratings": 4.5, "Suitable for which weather": "all seasons, Fall, Spring", "Use for which Skin Type": "Normal, Combination, Dry"},
    {"Brand Name": "Revlon", "Product Name": "Super Lustrous Lipstick", "Price": 8.49, "Ratings": 4.2, "Suitable for which weather": "all seasons, Summer, Winter", "Use for which Skin Type": "All, Oily, Normal, Dry"},
]

# Create DataFrames
df_foundation = pd.DataFrame(foundation_data)
df_lipstick = pd.DataFrame(lipstick_data)

# Save to Excel with two sheets
with pd.ExcelWriter("Make-Up Recommendation.xlsx", engine='openpyxl') as writer:
    df_foundation.to_excel(writer, sheet_name="Foundation", index=False)
    df_lipstick.to_excel(writer, sheet_name="Lipstick", index=False)

print("✅ Created 'Make-Up Recommendation.xlsx' with sample data!")
print(f"   - Foundation: {len(df_foundation)} products")
print(f"   - Lipstick: {len(df_lipstick)} products")
