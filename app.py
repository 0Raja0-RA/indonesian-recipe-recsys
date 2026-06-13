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
    hero_bg_css = f"linear-gradient(rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0.85)), url(data:image/jpeg;base64,{food_img_base64})"
else:
    hero_bg_css = "linear-gradient(135deg, #fff3e6 0%, #ffe6cc 100%)"

# Helper to clean HTML whitespace for perfect rendering without code block escapes
def clean_html(html_str):
    return "\n".join([line.strip() for line in html_str.split("\n") if line.strip()])

# Inject Custom CSS for premium light-cream theme (matching screenshot exactly)
st.markdown(clean_html(f"""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&display=swap');
    
    /* Global CSS variables to force orange-red accent globally */
    :root {{
        --primary-color: #c2410c !important;
    }}
    
    /* Global font override (Inter for UI and Body, warm off-white cream background) */
    .stApp {{
        font-family: 'Inter', sans-serif !important;
        background-color: #faf7f0 !important;
        color: #1e293b !important;
    }}
    
    /* Headings in Serif */
    h1, h2, h3, h4, h5, h6, .recipe-title {{
        font-family: 'Playfair Display', serif !important;
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
    
    /* Style horizontal difficulty and spice level segmented controls in sidebar */
    div[class*="difficulty_selector"] div[role="radiogroup"],
    div[class*="spice_level_selector"] div[role="radiogroup"] {{
        display: flex !important;
        flex-direction: row !important;
        gap: 4px !important;
        width: 100% !important;
        flex-wrap: nowrap !important;
    }}

    div[class*="difficulty_selector"] div[role="radiogroup"] label,
    div[class*="spice_level_selector"] div[role="radiogroup"] label {{
        flex: 1 !important;
        margin: 0 !important;
        padding: 8px 2px !important;
        background-color: #ffffff !important;
        border: 1px solid #dcd7ca !important;
        border-radius: 6px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        min-width: 0 !important;
    }}
    
    /* Ensure text is styled and strictly visible */
    div[class*="difficulty_selector"] div[role="radiogroup"] label p,
    div[class*="spice_level_selector"] div[role="radiogroup"] label p {{
        margin: 0 !important;
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }}
    
    /* Hide the radio dot circles */
    div[class*="difficulty_selector"] div[role="radiogroup"] label div[data-testid="stRadioIndicator"],
    div[class*="spice_level_selector"] div[role="radiogroup"] label div[data-testid="stRadioIndicator"] {{
        display: none !important;
    }}
    
    /* Selected difficulty and spice level button */
    div[class*="difficulty_selector"] div[role="radiogroup"] label:has(input:checked),
    div[class*="spice_level_selector"] div[role="radiogroup"] label:has(input:checked) {{
        background-color: #7f1d1d !important;
        border-color: #7f1d1d !important;
    }}
    div[class*="difficulty_selector"] div[role="radiogroup"] label:has(input:checked) p,
    div[class*="spice_level_selector"] div[role="radiogroup"] label:has(input:checked) p {{
        color: #ffffff !important;
    }}
    
    /* Style main page horizontal category segmented control */
    div[class*="main_category_selector"] div[role="radiogroup"] {{
        display: flex !important;
        flex-direction: row !important;
        gap: 8px !important;
        width: 100% !important;
        overflow-x: auto !important;
        padding-bottom: 8px !important;
    }}
    div[class*="main_category_selector"] div[role="radiogroup"]::-webkit-scrollbar {{
        height: 5px !important;
    }}
    div[class*="main_category_selector"] div[role="radiogroup"]::-webkit-scrollbar-track {{
        background: rgba(0, 0, 0, 0.01) !important;
    }}
    div[class*="main_category_selector"] div[role="radiogroup"]::-webkit-scrollbar-thumb {{
        background: #ebdcc5 !important;
        border-radius: 3px !important;
    }}
    div[class*="main_category_selector"] div[role="radiogroup"] label {{
        margin: 0 !important;
        padding: 0 !important;
    }}
    div[class*="main_category_selector"] div[role="radiogroup"] label > div {{
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: #ffffff !important;
        border: 1px solid #dcd7ca !important;
        padding: 10px 18px !important;
        border-radius: 12px !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        color: #475569 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        white-space: nowrap !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.01) !important;
    }}
    div[class*="main_category_selector"] div[role="radiogroup"] [data-testid="stWidgetLabelCircular"],
    div[class*="main_category_selector"] div[role="radiogroup"] [class*="stWidgetLabelCircular"],
    div[class*="main_category_selector"] div[role="radiogroup"] label input[type="radio"] + div,
    div[class*="main_category_selector"] div[role="radiogroup"] label input[type="radio"] + span {{
        display: none !important;
    }}
    div[class*="main_category_selector"] div[role="radiogroup"] label[data-selected="true"] > div {{
        background-color: #7f1d1d !important; /* Maroon red */
        color: #ffffff !important;
        border-color: #7f1d1d !important;
    }}
    div[class*="main_category_selector"] div[role="radiogroup"] label[data-selected="true"] > div * {{
        color: #ffffff !important;
        font-weight: 600 !important;
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
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-size: 0.95rem !important;
        color: #1e293b !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.01) !important;
        transition: all 0.2s ease !important;
    }}
    div[data-testid="stTextInput"] input:focus {{
        border-color: #c2410c !important;
        box-shadow: 0 4px 12px rgba(194, 65, 12, 0.08) !important;
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
        font-family: 'Playfair Display', serif !important;
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
        border-radius: 20px;
        padding: 45px 30px;
        text-align: center;
        margin-bottom: 25px;
        border: 1px solid #ebdcc5;
        box-shadow: 0 8px 25px rgba(0,0,0,0.02);
        position: relative;
        overflow: hidden;
    }}
    .hero-container::after {{
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #ff9f43, #e11d48, #10b981);
    }}
    .hero-title {{
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        margin-bottom: 10px !important;
        color: #7f1d1d !important;
        background: linear-gradient(90deg, #7f1d1d, #c2410c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: none;
    }}
    .hero-subtitle {{
        font-size: 1.15rem;
        color: #475569;
        font-weight: 400;
        margin-bottom: 0px !important;
    }}
</style>
"""), unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🍳 RasaNusantara</div>
    <div class="hero-subtitle">Sistem Rekomendasi Resep Masakan Indonesia Pintar (Hybrid Filtering)</div>
</div>
""", unsafe_allow_html=True)

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

CATEGORY_ORIGINS = {
    "Ayam": "Lombok",
    "Ikan": "Palembang",
    "Sapi": "Padang",
    "Udang": "Makassar",
    "Kambing": "Solo",
    "Telur": "Bali",
    "Tahu": "Sumedang",
    "Tempe": "Jawa Tengah",
    "Sayur": "Jawa Barat",
    "Nasi & Mie": "Jakarta",
    "Sambal": "Surabaya"
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
    return CATEGORY_ORIGINS.get(category, "Nusantara")

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
st.sidebar.markdown("### 🎛️ Preferensi Pencarian")

max_cooking_time = st.sidebar.slider(
    label="WAKTU MASAK SLIDER",
    min_value=15,
    max_value=240,
    value=135,
    step=15,
    label_visibility="collapsed"
)

# Custom slider label display matching screenshot
st.sidebar.markdown(clean_html(f"""
<div style="display: flex; justify-content: space-between; align-items: center; margin-top: -35px; margin-bottom: 25px;">
    <span style="font-size: 0.8rem; font-weight: 700; color: #6e5d4f; letter-spacing: 1px; text-transform: uppercase;">WAKTU MASAK</span>
    <span style="font-size: 0.85rem; font-weight: 700; color: #c2410c;">&le; {max_cooking_time} mnt</span>
</div>
<div style="display: flex; justify-content: space-between; font-size: 0.72rem; color: #94a3b8; margin-top: -20px; margin-bottom: 25px;">
    <span>15m</span>
    <span>4 jam</span>
</div>
"""), unsafe_allow_html=True)

kesulitan = st.sidebar.radio(
    "KESULITAN",
    options=["Semua", "Mudah", "Sedang", "Sulit"],
    index=0,
    horizontal=True,
    key="difficulty_selector"
)

tingkat_pedas = st.sidebar.radio(
    "TINGKAT KEPEDASAN",
    options=["Semua", "Tidak Pedas", "Sedang", "Pedas"],
    index=0,
    horizontal=True,
    key="spice_level_selector"
)

reset_filters = st.sidebar.button("Atur Ulang Filter", use_container_width=True)

with st.sidebar.expander("⚙️ Pengaturan Lanjutan"):
    diet_type = st.selectbox(
        "Tipe Diet",
        options=["Semua", "Non-Vegetarian", "Vegetarian"],
        index=0
    )

if reset_filters:
    st.session_state.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='text-align: center; color: #a19a8e; font-size: 0.8rem;'>Dibuat dengan ❤️ untuk Kuliner Indonesia</div>",
    unsafe_allow_html=True
)

# Main Page Elements
# Premium Search Bar on main page
st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
user_ingredients = st.text_input(
    label="Bahan yang Anda Miliki",
    value="",
    placeholder="Cari berdasarkan bahan yang Anda miliki... (contoh: ayam, cabai, kecap)",
    label_visibility="collapsed",
    key="ingredients_search"
)

# Horizontal Category Selector at top of Main Page (UX Upgrade)
st.markdown("<p style='font-size: 0.75rem; font-weight: 700; color: #6e5d4f; letter-spacing: 1px; text-transform: uppercase; margin-top: 15px; margin-bottom: 10px;'>Pilih Kategori Kuliner</p>", unsafe_allow_html=True)
CATEGORY_OPTIONS = {
    "Semua": "🍽️ Semua Kategori",
    "Sapi": "🥩 Sapi",
    "Ikan": "🐟 Ikan",
    "Sayur": "🥦 Sayur",
    "Tahu Tempe": "🌱 Tahu Tempe",
    "Telur": "🥚 Telur",
    "Nasi & Mie": "🍚 Nasi & Mie",
    "Sambal": "🌶️ Sambal"
}

selected_category = st.segmented_control(
    label="Pilih Kategori Kuliner",
    options=list(CATEGORY_OPTIONS.keys()),
    format_func=lambda x: CATEGORY_OPTIONS[x],
    default="Semua",
    label_visibility="collapsed",
    key="main_category_selector"
)

# Header Section matching the screenshot
st.markdown(clean_html(f"""
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-top: 25px; margin-bottom: 25px; border-bottom: 1px solid rgba(0,0,0,0.04); padding-bottom: 15px;">
    <div style="flex: 1;">
        <div style="font-size: 0.72rem; font-weight: 700; color: #c2410c; text-transform: uppercase; letter-spacing: 1.5px; display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
            <span>📖</span> Koleksi Resep
        </div>
        <h1 style="font-family: 'Playfair Display', serif !important; font-size: 2.3rem !important; font-weight: 700 !important; color: #1e293b !important; margin: 0 0 10px 0 !important; line-height: 1.2;">
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

    # Dynamic match count box inside sidebar
    num_matches = len(recommendations) if not recommendations.empty else 0
    st.sidebar.markdown(clean_html(f"""
    <div style="background: #ffffff; border: 1px solid #ebdcc5; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 15px; margin-top: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.015);">
        <div style="font-size: 1.8rem; color: #c2410c; display: flex; align-items: center; justify-content: center; font-family: 'Playfair Display', serif;">❈</div>
        <div style="text-align: left; line-height: 1.2;">
            <div style="font-size: 2rem; font-weight: 700; color: #7f1d1d; font-family: 'Playfair Display', serif;">{num_matches}</div>
            <div style="font-size: 0.72rem; color: #a19a8e; text-transform: uppercase; font-weight: 700; letter-spacing: 0.8px;">Resep Cocok</div>
        </div>
    </div>
    """), unsafe_allow_html=True)
    
    if recommendations.empty:
        st.warning("😔 Maaf, tidak ditemukan resep yang cocok dengan kriteria filter Anda. Coba atur ulang preferensi pencarian di sidebar.")
    else:
        # Show top 6 results
        top_recommendations = recommendations.head(6)
        
        # Grid system: display columns side-by-side (2 columns)
        cols = st.columns(2)
        
        for idx, (_, row) in enumerate(top_recommendations.iterrows()):
            col = cols[idx % 2]
            
            category_emoji = CATEGORY_EMOJIS.get(row["category"], "🍳")
            watermark_emoji = get_card_watermark(row)
            
            # Badges
            category_badge = f'<span class="badge badge-category">{category_emoji} {row["category"].upper()}</span>'
            
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
            
            # Location, portions, time
            origin_city = extract_origin(row["Title_Display"], row["category"])
            portion_label = get_portions(row["Title_Display"], row["category"])
            
            metadata_html = f"""
            <div style="display: flex; gap: 14px; font-size: 0.78rem; color: #c2410c; margin-bottom: 12px; font-weight: 600;">
                <span>📍 {origin_city}</span>
                <span>⏱️ {row["cooking_time"]} mnt</span>
                <span>👥 {portion_label}</span>
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
                <div class="card-watermark">{watermark_emoji}</div>
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
else:
    st.error("Gagal memulai sistem rekomendasi. Pastikan dataset telah terproses dengan benar.")
