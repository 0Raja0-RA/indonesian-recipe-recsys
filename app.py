import re
import os
import base64
import streamlit as st
from src.recommender import RecipeRecommender

# Set page configuration
st.set_page_config(
    page_title="RasaNusantara - Rekomendasi Resep",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize recommender with caching
@st.cache_resource
def load_recommender():
    try:
        return RecipeRecommender()
    except Exception as e:
        st.error(f"Gagal memuat sistem rekomendasi: {e}")
        return None

recommender = load_recommender()

# Load custom food photo background as base64 string
food_img_base64 = None
try:
    image_path = "assets/foto_makanan.jpg"
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            food_img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
except Exception as e:
    pass

if food_img_base64:
    hero_bg_css = f"url(data:image/jpeg;base64,{food_img_base64})"
else:
    hero_bg_css = "linear-gradient(135deg, #fff3e6 0%, #ffe6cc 100%)"

# Helper to clean HTML whitespace for perfect rendering without code block escapes
def clean_html(html_str):
    return "\n".join([line.strip() for line in html_str.split("\n") if line.strip()])

# Inject Custom CSS for premium light-cream theme (matching screenshot exactly)
st.markdown(clean_html(f"""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Global CSS variables to force orange-red accent globally */
    :root {{
        --primary-color: #c2410c !important;
    }}
    
    /* Global font override (Outfit for UI and Body, warm off-white cream background) */
    .stApp {{
        font-family: 'Outfit', sans-serif !important;
        background-color: #faf7f0 !important;
        color: #1e293b !important;
    }}
    
    /* Headings in Serif */
    h1, h2, h3, h4, h5, h6, .recipe-title {{
        font-family: 'Cinzel', serif !important;
        color: #1e293b !important;
    }}
    
    /* Sidebar styling override (Warm beige side panel) */
    [data-testid="stSidebar"] {{
        background-color: #f2ece0 !important;
        border-right: 1px solid rgba(0, 0, 0, 0.04) !important;
    }}
    
    /* Style widgets header labels inside sidebar */
    [data-testid="stSidebar"] label {{
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        color: #6e5d4f !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        margin-bottom: 8px !important;
    }}
    
    /* Style slider thumb and track to use terracotta */
    div[data-testid="stSlider"] [role="slider"] {{
        background-color: #c2410c !important;
        border: 2px solid #ffffff !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }}
    div[data-testid="stSlider"] div[data-testid="stSliderTickBar"] {{
        display: none !important;
    }}
    div[data-testid="stSlider"] div[data-testid="stSliderVal"] {{
        display: none !important;
    }}
    div[data-testid="stSlider"] div[role="slider"] * {{
        display: none !important;
    }}
    div[data-testid="stSlider"] [class*="thumb"] div {{
        display: none !important;
    }}
    div[data-testid="stSlider"] [class*="value"] {{
        display: none !important;
    }}
    
    /* Hide the default widgets labels to prevent double headers */
    div.st-key-difficulty_selector label[data-testid="stWidgetLabel"],
    div.st-key-spice_level_selector label[data-testid="stWidgetLabel"],
    div.st-key-main_category_selector label[data-testid="stWidgetLabel"] {{
        display: none !important;
    }}

    /* Style horizontal difficulty and spice level segmented controls in sidebar */
    div.st-key-difficulty_selector div[role="radiogroup"],
    div.st-key-spice_level_selector div[role="radiogroup"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 5px !important;
        width: 100% !important;
    }}
    
    div.st-key-difficulty_selector div[role="radiogroup"] button,
    div.st-key-spice_level_selector div[role="radiogroup"] button {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: #ffffff !important;
        border: 1px solid #dcd7ca !important;
        padding: 10px 2px !important;
        border-radius: 8px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        box-sizing: border-box !important;
        height: auto !important;
        margin: 0 !important;
    }}
    
    div.st-key-difficulty_selector div[role="radiogroup"] button:nth-child(1),
    div.st-key-spice_level_selector div[role="radiogroup"] button:nth-child(1) {{
        flex: 1 1 100% !important;
        width: 100% !important;
    }}
    
    div.st-key-difficulty_selector div[role="radiogroup"] button:not(:nth-child(1)),
    div.st-key-spice_level_selector div[role="radiogroup"] button:not(:nth-child(1)) {{
        flex: 0 0 calc((100% - 10px) / 3) !important;
        width: calc((100% - 10px) / 3) !important;
        min-width: 0 !important;
    }}
    
    div.st-key-difficulty_selector div[role="radiogroup"] button p,
    div.st-key-spice_level_selector div[role="radiogroup"] button p {{
        color: #475569 !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        margin: 0 !important;
        white-space: normal !important;
        text-align: center !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }}
    
    div.st-key-difficulty_selector div[role="radiogroup"] button[kind="segmented_controlActive"],
    div.st-key-spice_level_selector div[role="radiogroup"] button[kind="segmented_controlActive"] {{
        background-color: #7f1d1d !important;
        border-color: #7f1d1d !important;
    }}
    
    div.st-key-difficulty_selector div[role="radiogroup"] button[kind="segmented_controlActive"] p,
    div.st-key-spice_level_selector div[role="radiogroup"] button[kind="segmented_controlActive"] p {{
        color: #ffffff !important;
        font-weight: 700 !important;
    }}
    
    div.st-key-difficulty_selector div[role="radiogroup"] button:hover,
    div.st-key-spice_level_selector div[role="radiogroup"] button:hover {{
        border-color: #7f1d1d !important;
        background-color: #faf7f0 !important;
    }}
    
    div.st-key-difficulty_selector div[role="radiogroup"] button[kind="segmented_controlActive"]:hover,
    div.st-key-spice_level_selector div[role="radiogroup"] button[kind="segmented_controlActive"]:hover {{
        background-color: #7f1d1d !important;
    }}
    
    /* Style main page horizontal category segmented control */
    div.st-key-main_category_selector div[role="radiogroup"] {{
        display: flex !important;
        flex-direction: row !important;
        gap: 8px !important;
        width: 100% !important;
        overflow-x: auto !important;
        padding-bottom: 8px !important;
        flex-wrap: nowrap !important;
    }}
    div.st-key-main_category_selector div[role="radiogroup"]::-webkit-scrollbar {{
        height: 5px !important;
    }}
    div.st-key-main_category_selector div[role="radiogroup"]::-webkit-scrollbar-track {{
        background: rgba(0, 0, 0, 0.01) !important;
    }}
    div.st-key-main_category_selector div[role="radiogroup"]::-webkit-scrollbar-thumb {{
        background: #ebdcc5 !important;
        border-radius: 3px !important;
    }}
    div.st-key-main_category_selector div[role="radiogroup"] button {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: #ffffff !important;
        border: 1px solid #dcd7ca !important;
        padding: 10px 18px !important;
        border-radius: 12px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        white-space: nowrap !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.01) !important;
        height: auto !important;
        margin: 0 !important;
    }}
    div.st-key-main_category_selector div[role="radiogroup"] button p {{
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        color: #475569 !important;
        margin: 0 !important;
        white-space: nowrap !important;
    }}
    div.st-key-main_category_selector div[role="radiogroup"] button[kind="segmented_controlActive"] {{
        background-color: #7f1d1d !important; /* Maroon red */
        border-color: #7f1d1d !important;
    }}
    div.st-key-main_category_selector div[role="radiogroup"] button[kind="segmented_controlActive"] p {{
        color: #ffffff !important;
        font-weight: 600 !important;
    }}
    div.st-key-main_category_selector div[role="radiogroup"] button:hover {{
        border-color: #7f1d1d !important;
        background-color: #faf7f0 !important;
    }}
    div.st-key-main_category_selector div[role="radiogroup"] button[kind="segmented_controlActive"]:hover {{
        background-color: #7f1d1d !important;
    }}
    
    /* Reset Button styling */
    div[data-testid="stSidebar"] button {{
        background-color: #ffffff !important;
        border: 1px solid #dcd7ca !important;
        color: #475569 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
        width: 100% !important;
    }}
    div[data-testid="stSidebar"] button:hover {{
        background-color: #faf7f0 !important;
        color: #c2410c !important;
        border-color: #c2410c !important;
    }}
    
    /* Premium Search Bar styling */
    div[data-testid="stTextInput"] input {{
        background-color: #ffffff !important;
        border: 1px solid #dcd7ca !important;
        border-radius: 8px !important;
        padding: 10px 14px 10px 38px !important;
        font-size: 0.85rem !important;
        color: #1e293b !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.005) !important;
        transition: all 0.2s ease !important;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="%2394a3b8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>') !important;
        background-repeat: no-repeat !important;
        background-position: 14px center !important;
    }}
    div[data-testid="stTextInput"] input:focus {{
        border-color: #7f1d1d !important;
        box-shadow: 0 2px 8px rgba(127, 29, 29, 0.05) !important;
    }}
    
    /* Recipe Card styling */
    .recipe-card {{
        position: relative;
        overflow: hidden;
        background: #ffffff;
        border: 1px solid #f0ebe0;
        border-radius: 20px;
        padding: 26px;
        margin-bottom: 24px;
        color: #1e293b;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.02);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        height: 100%;
        display: flex;
        flex-direction: column;
    }}
    .recipe-card:hover {{
        transform: translateY(-4px);
        border-color: #c2410c;
        box-shadow: 0 12px 25px rgba(194, 65, 12, 0.05);
    }}
    
    /* Watermark for Card (Faint emoji on light card) */
    .card-watermark {{
        position: absolute;
        right: -10px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 9rem;
        opacity: 0.035;
        pointer-events: none;
        user-select: none;
        z-index: 1;
    }}
    
    /* Card Title */
    .recipe-title {{
        font-family: 'Cinzel', serif !important;
        font-size: 1.45rem !important;
        font-weight: 700 !important;
        margin-top: 0px !important;
        margin-bottom: 12px !important;
        color: #1e293b !important;
        padding-right: 50px;
        z-index: 2;
        line-height: 1.35 !important;
    }}
    
    /* Badges layout */
    .badges-wrapper {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 12px;
        z-index: 2;
    }}
    .badge {{
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        display: inline-flex;
        align-items: center;
        z-index: 2;
    }}
    
    /* Outline & Soft Badges colors */
    .badge-category {{
        background-color: #fff1f2 !important;
        color: #be123c !important;
    }}
    .badge-spice-pedas {{
        background-color: #fef2f2 !important;
        color: #b91c1c !important;
    }}
    .badge-spice-sedang {{
        background-color: #fff7ed !important;
        color: #c2410c !important;
    }}
    .badge-spice-tidakpedas {{
        background-color: #f0fdf4 !important;
        color: #15803d !important;
    }}
    .badge-difficulty-mudah {{
        background-color: #f0fdf4 !important;
        color: #15803d !important;
    }}
    .badge-difficulty-sedang {{
        background-color: #fff7ed !important;
        color: #c2410c !important;
    }}
    .badge-difficulty-sulit {{
        background-color: #fef2f2 !important;
        color: #b91c1c !important;
    }}
    
    /* Styled details/summary expander matching user requirement */
    details.recipe-details-expander {{
        margin-top: 15px;
        width: 100%;
        margin-bottom: 0 !important;
    }}
    details.recipe-details-expander summary {{
        list-style: none !important;
        outline: none !important;
        cursor: pointer !important;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        color: #c2410c !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        text-align: center !important;
        padding: 8px 0 !important;
        border-top: 1px solid #ebdcc5 !important;
        transition: color 0.2s ease !important;
    }}
    details.recipe-details-expander summary::-webkit-details-marker {{
        display: none !important;
    }}
    details.recipe-details-expander summary:hover {{
        color: #7f1d1d !important;
    }}
    
    /* Hero section styling */
    .hero-container {{
        background: {hero_bg_css};
        background-size: cover;
        background-position: center;
        border-radius: 24px;
        padding: 60px 20px;
        text-align: center;
        margin-bottom: 30px;
        border: 1px solid #ebdcc5;
        box-shadow: 0 8px 30px rgba(0,0,0,0.03);
        position: relative;
        overflow: hidden;
        display: flex;
        justify-content: center;
        align-items: center;
    }}
    .hero-container::after {{
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #ff9f43, #c2410c, #7f1d1d);
    }}
    .hero-card {{
        background: rgba(255, 255, 255, 0.45);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 20px;
        padding: 35px 40px;
        max-width: 650px;
        width: 90%;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        display: inline-block;
    }}
    .hero-badge {{
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        color: #c2410c !important;
        letter-spacing: 3px !important;
        text-transform: uppercase !important;
        margin-bottom: 12px !important;
    }}
    .hero-title {{
        font-family: 'Cinzel', serif !important;
        font-size: 3.2rem !important;
        font-weight: 700 !important;
        margin: 0 auto 15px auto !important;
        color: #7f1d1d !important;
        background: linear-gradient(90deg, #7f1d1d, #c2410c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: none;
        line-height: 1.1 !important;
    }}
    .hero-divider {{
        width: 80px;
        height: 2px;
        background-color: #c2410c;
        margin: 0 auto 15px auto;
        border-radius: 2px;
    }}
    .hero-subtitle {{
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.05rem !important;
        color: #475569 !important;
        font-weight: 400 !important;
        margin: 0 !important;
        line-height: 1.5 !important;
    }}
    
    /* Pagination buttons styling */
    div.st-key-btn_prev button,
    div.st-key-btn_next button {{
        background-color: #ffffff !important;
        border: 1px solid #ebdcc5 !important;
        color: #7f1d1d !important;
        border-radius: 12px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        padding: 6px 16px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.01) !important;
    }}
    div.st-key-btn_prev button:hover,
    div.st-key-btn_next button:hover {{
        background-color: #7f1d1d !important;
        border-color: #7f1d1d !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(127, 29, 29, 0.15) !important;
    }}
    div.st-key-btn_prev button:disabled,
    div.st-key-btn_next button:disabled {{
        background-color: #f5f5f5 !important;
        border-color: #e5e5e5 !important;
        color: #a3a3a3 !important;
        cursor: not-allowed !important;
        box-shadow: none !important;
    }}
</style>
"""), unsafe_allow_html=True)

# Hero Section
st.markdown(clean_html("""
<div class="hero-container">
    <div class="hero-card">
        <div class="hero-badge">WARISAN KULINER NUSANTARA</div>
        <h1 class="hero-title">RasaNusantara</h1>
        <div class="hero-divider"></div>
        <p class="hero-subtitle">Sistem Rekomendasi Resep Masakan Indonesia Pintar</p>
    </div>
</div>
"""), unsafe_allow_html=True)

# Main Page search input
st.markdown("<p style='font-size: 0.75rem; font-weight: 700; color: #6e5d4f; letter-spacing: 1px; text-transform: uppercase; margin-top: 20px; margin-bottom: 8px;'>Bahan yang Anda Miliki</p>", unsafe_allow_html=True)
user_ingredients = st.text_input(
    label="CARI RESEP INPUT",
    value="",
    placeholder="Masukkan bahan makanan yang Anda miliki (contoh: ayam, kentang, wortel)...",
    label_visibility="collapsed",
    key="ingredients_search"
)

# Mappings & Helpers
CATEGORY_EMOJIS = {
    "Ayam": "🐔",
    "Ikan": "🐟",
    "Sapi": "🥩",
    "Kambing": "🐐",
    "Udang": "🦐",
    "Telur": "🥚",
    "Tahu": "🧈",
    "Tempe": "🧆",
    "Sayur": "🥦",
    "Tahu Tempe": "🌱",
    "Nasi & Mie": "🍚",
    "Sambal": "🌶️"
}



FAMOUS_RECIPE_DESCRIPTIONS = {
    "ayam bakar taliwang": "Ayam muda dibumbui sambal pedas khas Lombok, kemudian dibakar hingga harum.",
    "soto ayam lamongan": "Soto kuning dengan koya bawang gurih, kuah bening kaya rempah khas Lamongan.",
    "rendang daging sapi": "Rendang daging sapi khas Minang yang dimasak perlahan dengan santan dan rempah melimpah hingga kering dan hitam gurih.",
    "sate lilit bali": "Sate khas Bali dari bahan daging ikan/ayam cincang yang dililitkan pada batang serai dan dipanggang harum.",
    "pempek palembang": "Olahan daging ikan tenggiri gurih disajikan dengan kuah cuko asam pedas manis khas Palembang.",
    "tahu sumedang": "Tahu goreng khas Sumedang yang renyah di luar, kopong di dalam, disajikan hangat dengan cabai rawit.",
    "tempe mendoan": "Tempe tipis dibalut adonan tepung berbumbu daun bawang yang digoreng setengah matang khas Banyumas.",
    "nasi goreng": "Nasi goreng spesial dengan paduan kecap manis, bawang, dan rempah aromatik khas Nusantara."
}

def extract_origin(title, category):
    title_lower = title.lower()
    if "taliwang" in title_lower:
        return "Lombok"
    elif "lamongan" in title_lower:
        return "Jawa Timur"
    elif "padang" in title_lower:
        return "Sumatera Barat"
    elif "palembang" in title_lower:
        return "Sumatera Selatan"
    elif "bali" in title_lower:
        return "Bali"
    elif "medan" in title_lower:
        return "Sumatera Utara"
    elif "manado" in title_lower or "woku" in title_lower:
        return "Sulawesi Utara"
    elif "sunda" in title_lower:
        return "Jawa Barat"
    elif "betawi" in title_lower or "jakarta" in title_lower:
        return "Jakarta"
    elif "solo" in title_lower:
        return "Jawa Tengah"
    elif "jogja" in title_lower or "yogyakarta" in title_lower:
        return "Yogyakarta"
    elif "makassar" in title_lower or "konro" in title_lower:
        return "Sulawesi Selatan"
    elif "madura" in title_lower:
        return "Jawa Timur"
    elif "aceh" in title_lower:
        return "Aceh"
    elif "pontianak" in title_lower:
        return "Kalimantan Barat"
    elif "banjar" in title_lower:
        return "Kalimantan Selatan"
    return "Nusantara"

def get_portions(title, category):
    title_lower = title.lower()
    if "soto" in title_lower or "sup" in title_lower or "gulai" in title_lower or "rawon" in title_lower or "bakso" in title_lower:
        return "6 porsi"
    if category in ["Sapi", "Kambing", "Ikan"]:
        return "6 porsi"
    elif category in ["Ayam", "Udang"]:
        return "4 porsi"
    else:
        return "2 porsi"

def get_recipe_description(title, category, origin):
    title_lower = title.lower().strip()
    for famous_key, desc in FAMOUS_RECIPE_DESCRIPTIONS.items():
        if famous_key in title_lower:
            return desc
    return f"Resep olahan {category.lower()} pilihan khas {origin} yang lezat, diolah dengan rempah tradisional pilihan."

def get_card_watermark(row):
    cat = row.get("category", "")
    title = row.get("Title_Display", "").lower()
    if "sambal" in title or "sambel" in title:
        return "🌶️"
    if "nasi" in title or "mie" in title or "bihun" in title or "kwetiau" in title:
        return "🍚"
    if row.get("diet_type") == "Vegetarian" and cat not in ["Tahu", "Tempe", "Telur"]:
        return "🥦"
    return CATEGORY_EMOJIS.get(cat, "🍳")

def parse_ingredients_full(ingredients_str):
    items = [item.strip() for item in ingredients_str.split('--') if item.strip()]
    if not items:
        return "<p>Tidak ada daftar bahan.</p>"
    
    col1_items = []
    col2_items = []
    for idx, item in enumerate(items):
        if len(item) > 1:
            item = item[0].upper() + item[1:]
        
        html_item = f"""
        <div style='display: flex; align-items: flex-start; gap: 6px; margin-bottom: 6px; color: #475569; font-size: 0.84rem; line-height: 1.4;'>
            <span style='color: #16a34a; font-weight: 700; flex-shrink: 0;'>✓</span>
            <span style='flex-grow: 1;'>{item}</span>
        </div>
        """
        if idx % 2 == 0:
            col1_items.append(html_item)
        else:
            col2_items.append(html_item)
            
    col1_html = "".join(col1_items)
    col2_html = "".join(col2_items)
    
    html = f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: left; margin-bottom: 10px;">
        <div>{col1_html}</div>
        <div>{col2_html}</div>
    </div>
    """
    return html

def parse_steps_full(steps_str):
    items = [step.strip() for step in steps_str.split('--') if step.strip()]
    if not items:
        return "<p>Tidak ada langkah pembuatan.</p>"
    
    html = "<div style='display: flex; flex-direction: column; text-align: left;'>"
    for idx, item in enumerate(items):
        cleaned_step = re.sub(r'^\d+[\s.)-]+\s*', '', item)
        if len(cleaned_step) > 1:
            cleaned_step = cleaned_step[0].upper() + cleaned_step[1:]
            
        step_num = idx + 1
        html += f"""
        <div style='display: flex; align-items: flex-start; gap: 12px; margin-bottom: 12px; color: #475569; font-size: 0.88rem; line-height: 1.45;'>
            <span style='flex-shrink: 0; width: 20px; height: 20px; background-color: #7f1d1d; color: #ffffff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; margin-top: 2px;'>{step_num}</span>
            <span style='flex-grow: 1;'>{cleaned_step}</span>
        </div>
        """
    html += "</div>"
    return html

# Sidebar Controls
# Sidebar brand header matching screenshot style
st.sidebar.markdown(clean_html("""
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid rgba(0,0,0,0.06);">
    <div style="background-color: #7f1d1d; width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" style="color: #ffffff;">
            <path d="M12 3c-2.48 0-4.5 2.02-4.5 4.5 0 .97.31 1.87.84 2.61C6.27 10.45 5 12.08 5 14c0 2.21 1.79 4 4 4h6c2.21 0 4-1.79 4-4 0-1.92-1.27-3.55-3.34-3.89.53-.74.84-1.64.84-2.61 0-2.48-2.02-4.5-4.5-4.5zm-3 17h6v2H9v-2z"/>
        </svg>
    </div>
    <div>
        <div style="font-family: 'Cinzel', serif; font-size: 1.3rem; font-weight: 700; color: #7f1d1d; line-height: 1.1;">RasaNusantara</div>
        <div style="font-family: 'Outfit', sans-serif; font-size: 0.65rem; font-weight: 700; color: #6e5d4f; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 2px;">Dasbor Resep</div>
    </div>
</div>
"""), unsafe_allow_html=True)


st.sidebar.markdown(clean_html(f"""
<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px; margin-bottom: 8px;">
    <span style="font-size: 0.8rem; font-weight: 700; color: #6e5d4f; letter-spacing: 1px; text-transform: uppercase;">Waktu Masak</span>
    <span style="font-size: 0.85rem; font-weight: 700; color: #c2410c;">&le; {st.session_state.get('cooking_time_slider', 135)} mnt</span>
</div>
"""), unsafe_allow_html=True)

max_cooking_time = st.sidebar.slider(
    label="WAKTU MASAK SLIDER",
    min_value=15,
    max_value=240,
    value=135,
    step=15,
    label_visibility="collapsed",
    key="cooking_time_slider"
)

st.sidebar.markdown(clean_html("""
<div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: #94a3b8; margin-top: -10px; margin-bottom: 25px;">
    <span>15m</span>
    <span>4 jam</span>
</div>
"""), unsafe_allow_html=True)

st.sidebar.markdown(clean_html("""
<div style="font-size: 0.8rem; font-weight: 700; color: #6e5d4f; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px;">Kesulitan</div>
"""), unsafe_allow_html=True)

kesulitan = st.sidebar.segmented_control(
    label="Difficulty Selector",
    options=["Semua", "Mudah", "Sedang", "Sulit"],
    default="Semua",
    label_visibility="collapsed",
    key="difficulty_selector"
)
if kesulitan is None:
    kesulitan = "Semua"

st.sidebar.markdown(clean_html("""
<div style="font-size: 0.8rem; font-weight: 700; color: #6e5d4f; letter-spacing: 1px; text-transform: uppercase; margin-top: 15px; margin-bottom: 8px;">Tingkat Kepedasan</div>
"""), unsafe_allow_html=True)

tingkat_pedas = st.sidebar.segmented_control(
    label="Spice Selector",
    options=["Semua", "Tidak Pedas", "Sedang", "Pedas"],
    default="Semua",
    label_visibility="collapsed",
    key="spice_level_selector"
)
if tingkat_pedas is None:
    tingkat_pedas = "Semua"

reset_filters = st.sidebar.button("Atur Ulang Filter", use_container_width=True)

with st.sidebar.expander("Pengaturan Lanjutan"):
    diet_type = st.selectbox(
        "Tipe Diet",
        options=["Semua", "Non-Vegetarian", "Vegetarian"],
        index=0,
        key="diet_type_selector"
    )

if reset_filters:
    st.session_state.clear()
    st.rerun()

# Main Page Elements
# Horizontal Category Selector at top of Main Page (UX Upgrade)
st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

# Horizontal Category Selector at top of Main Page (UX Upgrade)
st.markdown("<p style='font-size: 0.75rem; font-weight: 700; color: #6e5d4f; letter-spacing: 1px; text-transform: uppercase; margin-top: 15px; margin-bottom: 10px;'>Pilih Kategori Kuliner</p>", unsafe_allow_html=True)
CATEGORY_OPTIONS = {
    "Semua": "Semua Kategori",
    "Sapi": "Sapi",
    "Ikan": "Ikan",
    "Sayur": "Sayur",
    "Tahu Tempe": "Tahu Tempe",
    "Telur": "Telur",
    "Nasi & Mie": "Nasi & Mie",
    "Sambal": "Sambal"
}

selected_category = st.segmented_control(
    label="Pilih Kategori Kuliner",
    options=list(CATEGORY_OPTIONS.keys()),
    format_func=lambda x: CATEGORY_OPTIONS[x],
    default="Semua",
    label_visibility="collapsed",
    key="main_category_selector"
)
if selected_category is None:
    selected_category = "Semua"

# Render Sort Selector right below Category Selector
sort_col1, sort_col2 = st.columns([3, 1.2])
with sort_col1:
    st.markdown("<p style='font-size: 0.72rem; font-weight: 700; color: #6e5d4f; letter-spacing: 1px; text-transform: uppercase; margin-top: 15px;'>Urutkan Hasil:</p>", unsafe_allow_html=True)
with sort_col2:
    sort_by = st.selectbox(
        "Urutkan",
        options=["Paling Relevan", "Paling Disukai", "Waktu Tercepat"],
        label_visibility="collapsed",
        key="sort_by_selector"
    )

# Track filter state changes to reset current page to 0
filter_keys = [
    "ingredients_search",
    "cooking_time_slider",
    "difficulty_selector",
    "spice_level_selector",
    "main_category_selector",
    "diet_type_selector",
    "sort_by_selector"
]

if "current_page" not in st.session_state:
    st.session_state.current_page = 0

filters_changed = False
for key in filter_keys:
    current_val = st.session_state.get(key)
    prev_key = f"prev_{key}"
    prev_val = st.session_state.get(prev_key)
    if current_val != prev_val:
        filters_changed = True
        st.session_state[prev_key] = current_val

if filters_changed:
    st.session_state.current_page = 0

# Header Section matching the screenshot
st.markdown(clean_html(f"""
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-top: 25px; margin-bottom: 25px; border-bottom: 1px solid rgba(0,0,0,0.04); padding-bottom: 15px;">
    <div style="flex: 1;">
        <div style="font-size: 0.72rem; font-weight: 700; color: #c2410c; text-transform: uppercase; letter-spacing: 1.5px; display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="#c2410c" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="opacity: 0.85; margin-right: 2px;"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
            Koleksi Resep
        </div>
        <h1 style="font-family: 'Cinzel', serif !important; font-size: 2.3rem !important; font-weight: 700 !important; color: #1e293b !important; margin: 0 0 10px 0 !important; line-height: 1.2;">
            Resep Pilihan Hari Ini
        </h1>
        <p style="font-size: 0.9rem; color: #64748b; margin: 0; line-height: 1.5;">
            Disaring berdasarkan preferensi Anda. Setiap resep memuat bahan lengkap dan urutan langkah memasak yang jelas.
        </p>
    </div>
    <div style="font-size: 0.8rem; color: #94a3b8; font-weight: 500; margin-top: 35px; white-space: nowrap;">
        &bull; &le; {max_cooking_time} mnt
    </div>
</div>
"""), unsafe_allow_html=True)

# Custom Category Filtering logic
def filter_by_custom_category(df, cat_choice):
    if not cat_choice or cat_choice == "Semua":
        return df
    if cat_choice == "Sapi":
        return df[df['category'] == "Sapi"]
    elif cat_choice == "Ikan":
        return df[df['category'] == "Ikan"]
    elif cat_choice == "Tahu Tempe":
        return df[df['category'].isin(["Tahu", "Tempe"])]
    elif cat_choice == "Telur":
        return df[df['category'] == "Telur"]
    elif cat_choice == "Sayur":
        return df[df['diet_type'] == "Vegetarian"]
    elif cat_choice == "Nasi & Mie":
        return df[df['Title_Display'].str.contains(r'nasi|mie|bihun|kwetiau|bakmi', case=False, na=False)]
    elif cat_choice == "Sambal":
        return df[df['Title_Display'].str.contains(r'sambal|sambel', case=False, na=False)]
    return df

# Main recommendation query execution
if recommender is not None:
    if user_ingredients.strip():
        with st.spinner("Mencari resep terbaik..."):
            recommendations = recommender.recommend(
                user_ingredients=user_ingredients,
                diet_type=None,
                max_cooking_time=max_cooking_time,
                spice_levels=None,
                top_n=100,
                limit=100
            )
    else:
        recommendations = recommender.df.copy()
        recommendations['similarity_score'] = 0.0
        recommendations = recommendations.sort_values(by="Loves", ascending=False)
        
    # Apply category filter
    if not recommendations.empty:
        recommendations = filter_by_custom_category(recommendations, selected_category)
        
    # Apply difficulty filter (simulated using cooking_time)
    if not recommendations.empty:
        if kesulitan == "Mudah":
            recommendations = recommendations[recommendations['cooking_time'] <= 20]
        elif kesulitan == "Sedang":
            recommendations = recommendations[(recommendations['cooking_time'] > 20) & (recommendations['cooking_time'] <= 45)]
        elif kesulitan == "Sulit":
            recommendations = recommendations[recommendations['cooking_time'] > 45]
            
    # Apply max cooking time filter
    if not recommendations.empty:
        recommendations = recommendations[recommendations['cooking_time'] <= max_cooking_time]
        
    # Apply advanced settings filters
    if not recommendations.empty:
        if diet_type != "Semua":
            recommendations = recommendations[recommendations['diet_type'] == diet_type]
        if tingkat_pedas != "Semua":
            recommendations = recommendations[recommendations['spice_level'] == tingkat_pedas]

    # Apply sorting logic based on sort selectbox
    if not recommendations.empty:
        if 'similarity_score' not in recommendations.columns:
            recommendations['similarity_score'] = 0.0
            
        if sort_by == "Paling Relevan":
            if user_ingredients.strip():
                recommendations = recommendations.sort_values(by="similarity_score", ascending=False)
            else:
                recommendations = recommendations.sort_values(by="Loves", ascending=False)
        elif sort_by == "Paling Disukai":
            recommendations = recommendations.sort_values(by="Loves", ascending=False)
        elif sort_by == "Waktu Tercepat":
            recommendations = recommendations.sort_values(by="cooking_time", ascending=True)

    # Dynamic match count box inside sidebar (styled premium and clean)
    num_matches = len(recommendations) if not recommendations.empty else 0
    st.sidebar.markdown(clean_html(f"""
    <div style="background: #ffffff; border: 1px solid #ebdcc5; border-radius: 16px; padding: 16px 20px; display: flex; align-items: center; gap: 15px; margin-top: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.015);">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#c2410c" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink: 0; opacity: 0.85;">
            <polygon points="12 2 15 9 22 9 17 14 18.5 21 12 17 5.5 21 7 14 2 9 9 9 12 2"></polygon>
        </svg>
        <div style="text-align: left; line-height: 1.1;">
            <div style="font-size: 1.8rem; font-weight: 700; color: #7f1d1d; font-family: 'Cinzel', serif;">{num_matches}</div>
            <div style="font-size: 0.65rem; color: #a19a8e; text-transform: uppercase; font-weight: 700; letter-spacing: 1px;">Resep Cocok</div>
        </div>
    </div>
    """), unsafe_allow_html=True)
    
    if recommendations.empty:
        st.markdown(clean_html("""
        <div style="text-align: center; padding: 60px 20px; background-color: #ffffff; border: 1px solid #f0ebe0; border-radius: 20px; margin-top: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.01); display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <div style="display: flex; justify-content: center; margin-bottom: 20px; opacity: 0.85;">
                <svg width="80" height="80" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="32" cy="32" r="22" fill="#faf7f0" stroke="#ebdcc5" stroke-width="2"/>
                    <circle cx="32" cy="32" r="15" stroke="#ebdcc5" stroke-width="1.5" stroke-dasharray="3 3"/>
                    <path d="M22 20v8a3 3 0 0 1-3 3h-1m4-11a3 3 0 0 0-3 3v8m0 0v8" stroke="#7f1d1d" stroke-width="2" stroke-linecap="round"/>
                    <path d="M42 20v10a4 4 0 0 1-4 4h-1v8" stroke="#7f1d1d" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </div>
            <h3 style="font-family: 'Cinzel', serif; font-size: 1.65rem; font-weight: 700; color: #7f1d1d; margin: 0 0 8px 0; border: none; padding: 0; text-align: center; width: 100%;">Belum ada resep yang cocok</h3>
            <p style="font-family: 'Outfit', sans-serif; font-size: 0.9rem; color: #64748b; margin: 0; max-width: 400px; line-height: 1.4; text-align: center;">Coba longgarkan filter atau ubah kata kunci pencarian Anda.</p>
        </div>
        """), unsafe_allow_html=True)
    else:
        # Pagination Opsi B: 6 recipes per page with Sebelumnya, Halaman X dari Y, and Berikutnya buttons
        import math
        recipes_per_page = 6
        total_recipes = len(recommendations)
        num_pages = math.ceil(total_recipes / recipes_per_page)
        
        if "current_page" not in st.session_state:
            st.session_state.current_page = 0
            
        # Ensure page index remains in valid range
        if st.session_state.current_page >= num_pages:
            st.session_state.current_page = max(0, num_pages - 1)
        if st.session_state.current_page < 0:
            st.session_state.current_page = 0
            
        current_page = st.session_state.current_page
        start_idx = current_page * recipes_per_page
        end_idx = min(start_idx + recipes_per_page, total_recipes)
        
        page_recipes = recommendations.iloc[start_idx:end_idx]
        
        # Grid system: display columns side-by-side (2 columns)
        cols = st.columns(2)
        
        for idx, (_, row) in enumerate(page_recipes.iterrows()):
            col = cols[idx % 2]
            
            # Badges (Minimalist: no emojis in the category badge)
            category_badge = f'<span class="badge badge-category">{row["category"].upper()}</span>'
            
            # Spice Badge
            spice_level = row["spice_level"]
            spice_class = f'badge-spice-{spice_level.lower().replace(" ", "")}'
            spice_badge = f'<span class="badge {spice_class}">{spice_level.upper()}</span>'
            
            # Difficulty badge
            if row["cooking_time"] <= 20:
                diff_label = "MUDAH"
                diff_class = "badge-difficulty-mudah"
            elif row["cooking_time"] <= 45:
                diff_label = "SEDANG"
                diff_class = "badge-difficulty-sedang"
            else:
                diff_label = "SULIT"
                diff_class = "badge-difficulty-sulit"
            difficulty_badge = f'<span class="badge {diff_class}">{diff_label}</span>'
            
            # Location, portions, time (using inline SVGs instead of emojis)
            origin_city = extract_origin(row["Title_Display"], row["category"])
            portion_label = get_portions(row["Title_Display"], row["category"])
            
            svg_pin = '<svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display: inline-block; vertical-align: middle; margin-right: 4px; margin-top: -2px;"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>'
            svg_clock = '<svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display: inline-block; vertical-align: middle; margin-right: 4px; margin-top: -2px;"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>'
            svg_people = '<svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display: inline-block; vertical-align: middle; margin-right: 4px; margin-top: -2px;"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>'
            
            metadata_html = f"""
            <div style="display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.78rem; color: #c2410c; margin-bottom: 12px; font-weight: 600;">
                <span style="display: flex; align-items: center; white-space: nowrap;">{svg_pin}{origin_city}</span>
                <span style="display: flex; align-items: center; white-space: nowrap;">{svg_clock}{row["cooking_time"]} mnt</span>
                <span style="display: flex; align-items: center; white-space: nowrap;">{svg_people}{portion_label}</span>
            </div>
            """
            
            description_text = get_recipe_description(row["Title_Display"], row["category"], origin_city)
            
            # Dividers
            bahan_divider_html = """
            <div style="display: flex; align-items: center; text-align: center; margin: 15px 0; font-size: 0.68rem; color: #a19a8e; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;">
                <div style="flex: 1; border-bottom: 1px solid #ebdcc5;"></div>
                <span style="padding: 0 10px;">Bahan-Bahan</span>
                <div style="flex: 1; border-bottom: 1px solid #ebdcc5;"></div>
            </div>
            """
            
            langkah_divider_html = """
            <div style="display: flex; align-items: center; text-align: center; margin: 15px 0; font-size: 0.68rem; color: #a19a8e; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;">
                <div style="flex: 1; border-bottom: 1px solid #ebdcc5;"></div>
                <span style="padding: 0 10px;">Langkah Pembuatan</span>
                <div style="flex: 1; border-bottom: 1px solid #ebdcc5;"></div>
            </div>
            """
            
            ingredients_html = parse_ingredients_full(row["Ingredients_Display"])
            steps_html = parse_steps_full(row["Steps_Display"])
            
            # Render card using clean_html to prevent raw markdown rendering
            # details/summary expander hides components by default and reveals full lists on click instantly in browser
            card_html = clean_html(f"""
            <div class="recipe-card">
                <div class="badges-wrapper">
                    {category_badge}
                    {spice_badge}
                    {difficulty_badge}
                </div>
                <h3 class="recipe-title">{row["Title_Display"]}</h3>
                {metadata_html}
                <p style="font-size: 0.85rem; color: #5a6a80; line-height: 1.45; margin-bottom: 15px; margin-top: 0px; z-index: 2;">{description_text}</p>
                <details class="recipe-details-expander">
                    <summary>Lihat Resep Selengkapnya ▾</summary>
                    <div style="margin-top: 15px; z-index: 2; position: relative;">
                        {bahan_divider_html}
                        {ingredients_html}
                        {langkah_divider_html}
                        {steps_html}
                    </div>
                </details>
            </div>
            """)
            col.markdown(card_html, unsafe_allow_html=True)
        
        # Render premium pagination controls at the bottom of the grid
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        pag_col1, pag_col2, pag_col3 = st.columns([1, 2, 1])
        
        with pag_col1:
            prev_disabled = current_page == 0
            if st.button("← Sebelumnya", disabled=prev_disabled, use_container_width=True, key="btn_prev"):
                st.session_state.current_page -= 1
                st.rerun()
                
        with pag_col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 6px 0; font-family: 'Outfit', sans-serif; font-size: 0.9rem; font-weight: 600; color: #6e5d4f; letter-spacing: 0.5px;">
                Halaman {current_page + 1} dari {num_pages}
            </div>
            """, unsafe_allow_html=True)
            
        with pag_col3:
            next_disabled = current_page >= num_pages - 1
            if st.button("Berikutnya →", disabled=next_disabled, use_container_width=True, key="btn_next"):
                st.session_state.current_page += 1
                st.rerun()
        
        # Main Page Footer matching screenshot
        st.markdown(clean_html("""
        <div style="text-align: center; margin-top: 60px; padding: 25px 0; border-top: 1px solid rgba(0,0,0,0.04);">
            <div style="font-family: 'Cinzel', serif; font-size: 1.25rem; font-weight: 700; color: #7f1d1d; margin-bottom: 4px;">RasaNusantara</div>
            <div style="font-family: 'Outfit', sans-serif; font-size: 0.8rem; color: #64748b;">Dasbor kuliner premium — disusun dengan cinta untuk warisan rasa Indonesia.</div>
        </div>
        """), unsafe_allow_html=True)
else:
    st.error("Gagal memulai sistem rekomendasi. Pastikan dataset telah terproses dengan benar.")
