import os
import pandas as pd
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.data_processing import clean_text

class RecipeRecommender:
    def __init__(self, dataset_path="data/processed/merged_recipes.csv"):
        self.dataset_path = dataset_path
        self.df = None
        self.vectorizer = None
        self.tfidf_matrix = None
        self.load_data_and_models()

    def load_data_and_models(self):
        """
        Load the preprocessed dataset, the pre-fitted TF-IDF Vectorizer, and the TF-IDF matrix.
        """
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Processed dataset not found at {self.dataset_path}. Please run data_processing.py first.")
            
        processed_dir = os.path.dirname(self.dataset_path)
        vectorizer_path = os.path.join(processed_dir, "tfidf_vectorizer.pkl")
        matrix_path = os.path.join(processed_dir, "tfidf_matrix.pkl")
        
        if not os.path.exists(vectorizer_path) or not os.path.exists(matrix_path):
            raise FileNotFoundError("Pre-fitted TF-IDF model files not found. Please run data_processing.py first.")
            
        # Load processed data
        self.df = pd.read_csv(self.dataset_path)
        
        # Fill NaN values
        self.df['Ingredients'] = self.df['Ingredients'].fillna("")
        self.df['Title'] = self.df['Title'].fillna("")
        self.df['Steps'] = self.df['Steps'].fillna("")
        
        # Load pre-trained models using joblib
        self.vectorizer = joblib.load(vectorizer_path)
        self.tfidf_matrix = joblib.load(matrix_path)
        print("Dataset and cached TF-IDF models loaded successfully!")
        
    def recommend(self, user_ingredients, diet_type="Non-Vegetarian", max_cooking_time=60, spice_levels=None, top_n=50, limit=10):
        """
        Hybrid Recommendation Logic:
        1. Knowledge-Based Filtering (KBF):
           - Filter by Diet Type (Vegetarian / Non-Vegetarian)
           - Filter by Maximum Cooking Time
           - Filter by Spice Level list (e.g., ['Tidak Pedas', 'Sedang'])
        
        2. Content-Based Filtering (CBF):
           - Compute Cosine Similarity between user ingredients and dataset ingredients.
           - Apply similarity threshold >= 0.05 to ensure relevance.
        
        3. Popularity Weighting:
           - Retrieve the Top-N most similar recipes.
           - Re-rank those Top-N recipes based on community popularity ('Loves' count) descending.
           - Return the top 'limit' results.
        """
        if self.df is None:
            self.load_data_and_models()
            
        filtered_df = self.df.copy()
        
        # --- 1. Knowledge-Based Filtering (KBF) ---
        # Filter by Diet Type
        if diet_type:
            filtered_df = filtered_df[filtered_df['diet_type'] == diet_type]
            
        # Filter by Cooking Time
        if max_cooking_time:
            filtered_df = filtered_df[filtered_df['cooking_time'] <= max_cooking_time]
            
        # Filter by Spice Level
        if spice_levels:
            # Ensure it is a list
            if isinstance(spice_levels, str):
                spice_levels = [spice_levels]
            filtered_df = filtered_df[filtered_df['spice_level'].isin(spice_levels)]
            
        if filtered_df.empty:
            return pd.DataFrame()
            
        # Define columns we want to return
        display_cols = [
            'Title_Display', 'Ingredients_Display', 'Steps_Display', 
            'cooking_time', 'spice_level', 'diet_type', 
            'similarity_score', 'Loves', 'category'
        ]
            
        # --- 2. Content-Based Filtering (CBF) ---
        cleaned_query = clean_text(user_ingredients)
        
        # If user provides no ingredients, return the most popular recipes matching the KBF criteria
        if not cleaned_query:
            filtered_df['similarity_score'] = 0.0
            final_df = filtered_df.sort_values(by='Loves', ascending=False).head(limit)
            return final_df[[col for col in display_cols if col in final_df.columns]]
            
        # Get original indices of the filtered dataframe rows to reference the TF-IDF matrix
        indices = filtered_df.index.tolist()
        
        # Transform user input ingredients to TF-IDF vector
        query_vector = self.vectorizer.transform([cleaned_query])
        
        # Extract TF-IDF matrix subset for filtered recipes
        subset_tfidf = self.tfidf_matrix[indices]
        
        # Compute cosine similarity
        sim_scores = cosine_similarity(query_vector, subset_tfidf).flatten()
        
        # Append scores to filtered df
        filtered_df['similarity_score'] = sim_scores
        
        # Apply similarity threshold filter (min 0.05) to filter out irrelevant recipes
        filtered_df = filtered_df[filtered_df['similarity_score'] >= 0.05]
        
        if filtered_df.empty:
            return pd.DataFrame()
            
        # Sort by similarity score descending to retrieve Top-N candidates
        top_n_df = filtered_df.sort_values(by='similarity_score', ascending=False).head(top_n)
        
        # --- 3. Popularity Reranking ---
        # Re-sort the Top-N subset by Loves descending, and return 'limit' number of recipes
        final_df = top_n_df.sort_values(by='Loves', ascending=False).head(limit)
        
        return final_df[[col for col in display_cols if col in final_df.columns]]
