import os
import re
import pandas as pd
import numpy as np

# Direktori
RAW_DIR = r"c:\Project_2026\Indonesian-Recipe-Recsys\data\raw"
PROCESSED_DIR = r"c:\Project_2026\Indonesian-Recipe-Recsys\data\processed"
OUTPUT_FILE = os.path.join(PROCESSED_DIR, "merged_recipes.csv")

# Stopwords indonesia
INDONESIAN_STOPWORDS = {
    'dan', 'yang', 'di', 'ke', 'dari', 'untuk', 'dengan', 'pada', 'adalah', 
    'itu', 'ini', 'sebagai', 'atau', 'secukupnya', 'sesuai', 'selera', 
    'lalu', 'kemudian', 'setelah', 'hingga', 'sampai', 'yg', 'dgn', 'sdt', 
    'sdm', 'gr', 'gram', 'kg', 'ml', 'buah', 'lembar', 'batang', 'siung', 
    'butir', 'ruas', 'ikat', 'secukup', 'biji', 'helai', 'bks', 'bungkus',
    'secukupny', 'sck', 'sckp', 'sckpnya', 'bumbu', 'bahan', 'halus', 'iris',
    'potong', 'rebus', 'goreng', 'masak', 'secukup'
}

def clean_text(text):
    """
    Bersihkan teks dengan lowercasing, menghapus karakter spesial/tanda baca,
    dan menghapus stopwords.
    """
    if not isinstance(text, str):
        return ""
    
    # Lowercase
    text = text.lower()
    
    # Hapus '--' (memisahkan ingredients/steps) dengan spasi
    text = text.replace('--', ' ')
    
    # Hapus tanda baca & special characters
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    
    # Hapus ekstra spasi
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Hapus stopwords
    words = text.split()
    cleaned_words = [w for w in words if w not in INDONESIAN_STOPWORDS]
    
    return ' '.join(cleaned_words)

def extract_cooking_time(steps_text):
    """
    Extract cooking time in minutes from steps text using regular expressions.
    """
    if not isinstance(steps_text, str):
        return None
    
    # Find patterns like:
    # "30 menit", "15 mnt", etc.
    min_matches = re.findall(r'(\d+)\s*(?:menit|mnt)', steps_text, re.IGNORECASE)
    
    # Find patterns like:
    # "1 jam", "1.5 jam", "2,5 jam"
    hour_matches = re.findall(r'(\d+(?:[.,]\d+)?)\s*jam', steps_text, re.IGNORECASE)
    
    times = []
    for m in hour_matches:
        try:
            val = float(m.replace(',', '.'))
            times.append(int(val * 60))
        except ValueError:
            pass
            
    for m in min_matches:
        try:
            times.append(int(m))
        except ValueError:
            pass
            
    if times:
        # We assume the maximum time found in steps represents the total cooking/baking time
        return max(times)
    
    return None

def classify_spice_level(ingredients_text):
    """
    Klasifikasikan tingkat kepedasan berdasarkan kata kunci di kolom bahan.
    """
    if not isinstance(ingredients_text, str):
        return "Tidak Pedas"
    
    ingredients_lower = ingredients_text.lower()
    
    # Spicy keywords
    spicy_keywords = [
        'cabe', 'cabai', 'rawit', 'sambal', 'sambel', 'lada', 'merica', 'paprika', 
        'pedas', 'pedes', 'lombok', 'rica', 'balado', 'chili', 'chilli', 'chiles'
    ]
    
    # Hitung kecocokan kata kunci
    count = sum(1 for kw in spicy_keywords if kw in ingredients_lower)
    
    # Deteksi kata kunci dengan tingkat kepedasan tinggi
    heavy_spicy_keywords = [
        'cabai rawit', 'cabe rawit', 'rawit merah', 'sambal ulek', 'pedas gila', 
        'pedas mampus', 'setan', 'mercon', 'rica-rica', 'rica rica', 'geprek',
        'pedas level', 'level pedas'
    ]
    has_heavy_spiciness = any(h_kw in ingredients_lower for h_kw in heavy_spicy_keywords)
    
    if count == 0:
        return "Tidak Pedas"
    elif has_heavy_spiciness or count > 3:
        return "Pedas"
    else:
        return "Sedang"

def classify_diet_type(ingredients_text, category):
    """
    Klasifikasikan resep sebagai Vegetarian atau Non-Vegetarian.
    Menggunakan fail-safe berbasis kategori utama.
    """
    # Fail-safe check: jika kategori inheren non-vegetarian, langsung kembalikan Non-Vegetarian
    non_veg_categories = {'Ayam', 'Ikan', 'Kambing', 'Sapi', 'Udang'}
    if isinstance(category, str) and category in non_veg_categories:
        return "Non-Vegetarian"
        
    if not isinstance(ingredients_text, str):
        return "Vegetarian"
        
    ingredients_lower = ingredients_text.lower()
    
    # Kamus kata kunci non-vegetarian (hewan, jenis ikan, potongan, organ/jeroan)
    non_veg_keywords = [
        # Meat & Poultry (Daging & Unggas)
        'ayam', 'sapi', 'kambing', 'daging', 'bebek', 'babi', 'pork', 'ham', 'bacon', 
        'beef', 'chicken', 'lamb', 'mutton', 'tetelan', 'ceker', 'tulang', 'paha', 
        'dada', 'sayap', 'kikil', 'buntut', 'has', 'sirloin', 'tenderloin', 'wagyu', 
        'jeroan', 'babat', 'paru', 'usus', 'rempelo', 'ampela', 'ati', 'limpa', 'otak',
        'gajih', 'tetelan', 'rawon', 'kornet', 'sosis', 'pepperoni', 'salami',
        
        # Fish & Seafood (Ikan & Makanan Laut)
        'ikan', 'udang', 'cumi', 'kepiting', 'kerang', 'tuna', 'tongkol', 'patin', 
        'nila', 'bandeng', 'kembung', 'gurame', 'gurami', 'lele', 'sarden', 'sardine', 
        'kakap', 'salmon', 'tenggiri', 'bawal', 'gabus', 'mujair', 'mujaer', 'dori', 
        'teri', 'rebon', 'ebi', 'lobster', 'octopus', 'gurita', 'sotong', 'kerang', 
        'tiram', 'kupang', 'makarel', 'mackerel', 'belut', 'sidat', 'seafood', 'shrimp', 
        'prawn', 'crab'
    ]
    
    is_non_veg = any(kw in ingredients_lower for kw in non_veg_keywords)
    
    if is_non_veg:
        return "Non-Vegetarian"
    else:
        return "Vegetarian"

def process_datasets():
    print("Starting data preprocessing pipeline...")
    
    # List all raw CSV files
    csv_files = [f for f in os.listdir(RAW_DIR) if f.startswith("dataset-") and f.endswith(".csv")]
    if not csv_files:
        print(f"Error: No raw CSV files found in {RAW_DIR}")
        return
        
    all_dfs = []
    
    for filename in csv_files:
        filepath = os.path.join(RAW_DIR, filename)
        print(f"Reading file: {filename}")
        
        # Determine category from filename: dataset-ayam.csv -> Ayam
        category = filename.replace("dataset-", "").replace(".csv", "").capitalize()
        
        try:
            df = pd.read_csv(filepath)
            df['category'] = category
            all_dfs.append(df)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            
    if not all_dfs:
        print("No DataFrames to merge. Exiting.")
        return
        
    # Merge all DataFrames
    merged_df = pd.concat(all_dfs, ignore_index=True)
    print(f"Merged {len(csv_files)} files. Total rows: {len(merged_df)}")
    
    # Strict Data Filtering: Drop rows with [Notitle], NaN, or empty values in Title, Ingredients, or Steps
    is_invalid_title = (
        merged_df['Title'].isnull() | 
        (merged_df['Title'].astype(str).str.lower().str.strip() == '[notitle]') |
        (merged_df['Title'].astype(str).str.strip() == '')
    )
    is_invalid_ingredients = (
        merged_df['Ingredients'].isnull() |
        (merged_df['Ingredients'].astype(str).str.strip() == '')
    )
    is_invalid_steps = (
        merged_df['Steps'].isnull() |
        (merged_df['Steps'].astype(str).str.strip() == '')
    )
    
    corrupt_rows_mask = is_invalid_title | is_invalid_ingredients | is_invalid_steps
    dropped_count = corrupt_rows_mask.sum()
    
    merged_df = merged_df[~corrupt_rows_mask].copy()
    print(f"Dropped {dropped_count} corrupt/incomplete rows from the dataset. Remaining rows: {len(merged_df)}")
    
    # Drop URL column
    if 'URL' in merged_df.columns:
        merged_df = merged_df.drop(columns=['URL'])
        print("Dropped 'URL' column.")
        
    # Standardize and clean Loves
    merged_df['Loves'] = pd.to_numeric(merged_df['Loves'], errors='coerce').fillna(0).astype(int)
    
    # Store original data for UI display
    merged_df['Title_Display'] = merged_df['Title'].fillna("Tanpa Judul").astype(str)
    merged_df['Ingredients_Display'] = merged_df['Ingredients'].fillna("").astype(str)
    merged_df['Steps_Display'] = merged_df['Steps'].fillna("").astype(str)
    
    # Feature Engineering (do this using Display/Original columns)
    print("Extracting features (cooking_time, spice_level, diet_type)...")
    merged_df['cooking_time'] = merged_df['Steps_Display'].apply(extract_cooking_time)
    
    # Fill missing cooking_time with the median value of valid extractions
    median_time = merged_df['cooking_time'].median()
    if pd.isna(median_time) or median_time == 0:
        median_time = 30 # Default to 30 mins if median is invalid
    
    merged_df['cooking_time'] = merged_df['cooking_time'].fillna(median_time).astype(int)
    print(f"Cooking times extracted. Missing values imputed with median: {median_time} minutes.")
    
    merged_df['spice_level'] = merged_df['Ingredients_Display'].apply(classify_spice_level)
    merged_df['diet_type'] = merged_df.apply(
        lambda row: classify_diet_type(row['Ingredients_Display'], row['category']), 
        axis=1
    )
    
    # Clean the core columns for TF-IDF / NLP search
    print("Cleaning text fields for NLP indexing...")
    merged_df['Title'] = merged_df['Title_Display'].apply(clean_text)
    merged_df['Ingredients'] = merged_df['Ingredients_Display'].apply(clean_text)
    merged_df['Steps'] = merged_df['Steps_Display'].apply(clean_text)
    
    # Ensure processed directory exists
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    # Save the processed dataset
    merged_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Processed dataset saved successfully to: {OUTPUT_FILE}")
    print(f"Final dataset summary:")
    print(f"- Rows: {len(merged_df)}")
    print(f"- Categories: {merged_df['category'].value_counts().to_dict()}")
    print(f"- Diet Types: {merged_df['diet_type'].value_counts().to_dict()}")
    print(f"- Spice Levels: {merged_df['spice_level'].value_counts().to_dict()}")

if __name__ == "__main__":
    process_datasets()
