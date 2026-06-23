import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="CoTW Reserve Finder", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- NEW: CSS INJECTION FOR AUTOSCALING ---
st.markdown("""
    <style>
    /* Target the big metric numbers to wrap and scale */
    div[data-testid="stMetricValue"] > div {
        white-space: normal !important;
        word-wrap: break-word;
        font-size: clamp(1.2rem, 2vw, 2.5rem) !important; 
    }
    
    /* Target the Need Zone and Biome text to scale */
    .scalable-text {
        font-size: clamp(1rem, 1.2vw, 1.5rem) !important;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Helper function for icons (Defined globally so everything can use it)
def get_animal_icon(species_name):
    name = str(species_name).lower()
    if any(word in name for word in ['duck', 'mallard', 'teal', 'wigeon']): return '🦆'
    if any(word in name for word in ['rabbit', 'hare']): return '🐇'
    if any(word in name for word in ['wolf', 'coyote']): return '🐺'
    if any(word in name for word in ['fox']): return '🦊'
    if any(word in name for word in ['bear']): return '🐻'
    if any(word in name for word in ['moose']): return '🫎'
    if any(word in name for word in ['pig', 'boar', 'peccary']): return '🐗'
    if any(word in name for word in ['bird', 'pheasant', 'turkey', 'quail', 'ptarmigan', 'grouse','goose']): return '🪶'
    if any(word in name for word in ['goat', 'ibex', 'mouflon', 'sheep', 'chamois']): return '🐐'
    if any(word in name for word in ['lion', 'puma']): return '🐆'
    if any(word in name for word in ['gator', 'alligator', 'crocodile']): return '🐊'
    if any(word in name for word in ['bison', 'buffalo']): return '🦬'
    return '🦌' 

# 3. Data Loading
@st.cache_data(ttl=600)
def load_data():
    # Make sure your specific GID is at the end of this URL
    csv_url = "https://docs.google.com/spreadsheets/d/1_gZ9T8BOJGnmg0qj_eKfh_VBbaH19pmR-fB1DBxO200/export?format=csv&gid=0"
    return pd.read_csv(csv_url)

try:
    df = load_data()
    
    # Clean up the data slightly (fill blank cells with a dash)
    df = df.fillna("-")

    # 4. Sidebar Navigation
    st.sidebar.title("🌲 Reserves")
    st.sidebar.write("Select a map below:")
    
    preserves = sorted(df['Preserve'].unique())

    if 'active_reserve' not in st.session_state:
        st.session_state.active_reserve = preserves[0]

    # The Callback Function
    def update_reserve(new_reserve):
        st.session_state.active_reserve = new_reserve

    for preserve in preserves:
        is_active = st.session_state.active_reserve == preserve
        button_label = f"📍 {preserve}" if is_active else preserve
        
        st.sidebar.button(
            label=button_label, 
            key=f"btn_{preserve}", 
            use_container_width=True,
            on_click=update_reserve, 
            args=(preserve,) 
        )

    selected_preserve = st.session_state.active_reserve

    # 5. Main Application Header
    st.title(f"📍 {selected_preserve} Overview")
    st.markdown("---")

    # Filter by reserve first
    filtered_df = df[df['Preserve'] == selected_preserve].copy()

    if filtered_df.empty:
        st.warning("No data found for this reserve.")
    else:
        # 6. Sorting Controls
        st.markdown("### 🎛️ Sort Options")
        
        sort_col1, sort_col2 = st.columns([2, 2])
        with sort_col1:
            sort_by = st.selectbox(
                "Sort animals by:", 
                ["Species (Alphabetical)", "Class (Numeric)", "Diamond Score", "Max Weight"],
                label_visibility="collapsed"
            )
        with sort_col2:
            sort_order = st.radio(
                "Direction:", 
                ["Ascending 🔼", "Descending 🔽"], 
                horizontal=True,
                label_visibility="collapsed"
            )

        is_ascending = sort_order == "Ascending 🔼"

        # 7. Smart Sorting Logic
        if sort_by == "Species (Alphabetical)":
            filtered_df = filtered_df.sort_values(by="Species", ascending=is_ascending)
            
        elif sort_by == "Class (Numeric)":
            filtered_df = filtered_df.sort_values(by=["Class", "Species"], ascending=[is_ascending, True])
            
        elif sort_by == "Diamond Score":
            filtered_df['Temp_Sort'] = filtered_df['Diamond Score'].astype(str).str.extract(r'([\d\.]+)').astype(float)
            filtered_df = filtered_df.sort_values(by="Temp_Sort", ascending=is_ascending)
            
        elif sort_by == "Max Weight":
            filtered_df['Temp_Sort'] = filtered_df['Max Weight'].astype(str).str.extract(r'([\d\.]+)').astype(float)
            filtered_df = filtered_df.sort_values(by="Temp_Sort", ascending=is_ascending)

        st.markdown("<br>", unsafe_allow_html=True) 

        # 8. Render the UI Expanders
        for index, row in filtered_df.iterrows():
            
            icon = get_animal_icon(row['Species'])
            
            with st.expander(f"{icon} {row['Species']} (Class {row['Class']})"):
                
                # Top Row: Custom columns with CSS-wrapped metrics
                col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                
                # Helper to create a custom "metric" box that respects our CSS
                def custom_metric(label, value):
                    st.markdown(f"""
                        <div style='margin-bottom: 10px;'>
                            <div style='font-size: 0.8rem; color: #808495;'>{label}</div>
                            <div class='scalable-text' style='font-weight: bold;'>{value}</div>
                        </div>
                    """, unsafe_allow_html=True)

                with col1: custom_metric("Class", str(row['Class']))
                with col2: custom_metric("Difficulty", str(row['Max Difficulty Level']))
                with col3: custom_metric("Diamond Score", str(row['Diamond Score']))
                with col4: custom_metric("Max Weight", str(row['Max Weight']))
                
                st.markdown("---") 
                
                # Middle Row: Need Zones and Biome
                nz_col, biome_col = st.columns([2, 1])
                
                with nz_col:
                    st.markdown("#### 🕒 Need Zones")
                    zones_text = str(row['Need Zone Times'])
                    
                    # Swap abbreviations for icons, and replace commas with HTML line breaks
                    clean_zones = zones_text.replace("D:", "💧 <b>Drink:</b>") \
                                            .replace("F:", "🌿 <b>Feed:</b>") \
                                            .replace("R:", "💤 <b>Rest:</b>") \
                                            .replace(", ", "<br>") 
                    
                    # Uses the new scalable-text CSS class
                    st.markdown(f"<div class='scalable-text'>{clean_zones}</div>", unsafe_allow_html=True)
                    
                with biome_col:
                    st.markdown("#### 🌲 Primary Biome")
                    # Uses the new scalable-text CSS class
                    st.markdown(f"<div class='scalable-text'><b>{row['Primary Biome']}</b></div>", unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Bottom Row: Equipment Breakdown
                st.markdown("#### 🎒 Recommended Equipment")
                eq_col1, eq_col2, eq_col3 = st.columns(3)
                
                with eq_col1:
                    st.info(f"🔊 **Callers:**\n\n{row['Mouth / Electronic Caller']}")
                with eq_col2:
                    st.warning(f"🏗️ **Stationary:**\n\n{row['Stationary Lure (Feeder)']}")
                with eq_col3:
                    st.success(f"💨 **Scents & Decoys:**\n\n{row['Scent / Decoy']}")

except Exception as e:
    st.error("Could not load the application data.")
    st.exception(e)