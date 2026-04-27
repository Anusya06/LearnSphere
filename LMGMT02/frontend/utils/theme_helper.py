"""
Dark Mode Theme Helper - Exclusive Dark Theme
"""
import streamlit as st


def apply_theme():
    """Apply dark theme globally"""
    st.session_state.theme = "dark"
    apply_dark_theme()


def apply_dark_theme():
    """Apply comprehensive dark theme styling"""
    st.markdown("""
        <style>
        /* Dark theme color variables */
        :root {
            --bg-primary: #0e1117;
            --bg-secondary: #1e1e1e;
            --bg-tertiary: #262730;
            --text-primary: #fafafa;
            --text-secondary: #b0b0b0;
            --text-muted: #808080;
            --border-color: #3e3e3e;
            --card-bg: #1e1e1e;
            --card-hover: #262730;
            --primary-color: #667eea;
            --primary-hover: #5568d3;
            --success-color: #10b981;
            --error-color: #ef4444;
            --warning-color: #f59e0b;
            --info-color: #3b82f6;
        }
        
        /* Main app background */
        .stApp {
            background-color: var(--bg-primary) !important;
            color: var(--text-primary) !important;
        }
        
        /* All text elements */
        .stApp, .stApp * {
            color: var(--text-primary) !important;
        }
        
        /* Markdown text */
        .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: var(--text-primary) !important;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-primary) !important;
        }
        
        /* Paragraphs and spans */
        p, span, div {
            color: var(--text-primary) !important;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: var(--bg-secondary) !important;
        }
        
        [data-testid="stSidebar"] * {
            color: var(--text-primary) !important;
        }
        
        /* Cards and containers */
        .element-container {
            color: var(--text-primary) !important;
        }
        
        /* Buttons */
        .stButton > button {
            background-color: var(--primary-color) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton > button:hover {
            background-color: var(--primary-hover) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > select,
        .stNumberInput > div > div > input {
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
        }
        
        .stTextInput label, .stTextArea label, .stSelectbox label, .stNumberInput label {
            color: var(--text-primary) !important;
        }
        
        /* Radio buttons */
        .stRadio > label {
            color: var(--text-primary) !important;
        }
        
        .stRadio > div {
            background-color: var(--bg-secondary) !important;
            padding: 10px !important;
            border-radius: 8px !important;
        }
        
        .stRadio label {
            color: var(--text-primary) !important;
        }
        
        /* Checkbox */
        .stCheckbox > label {
            color: var(--text-primary) !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px !important;
            background-color: var(--bg-primary) !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 12px 24px !important;
            background-color: var(--bg-secondary) !important;
            border-radius: 8px 8px 0 0 !important;
            font-weight: 600 !important;
            color: var(--text-secondary) !important;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: var(--primary-color) !important;
            color: white !important;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: var(--bg-secondary) !important;
            border-radius: 8px !important;
            color: var(--text-primary) !important;
        }
        
        .streamlit-expanderContent {
            background-color: var(--bg-tertiary) !important;
            color: var(--text-primary) !important;
        }
        
        /* Code blocks */
        .stCode, code, pre {
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
        }
        
        /* Alerts */
        .stSuccess {
            background-color: rgba(16, 185, 129, 0.1) !important;
            border-left: 4px solid var(--success-color) !important;
            color: var(--text-primary) !important;
        }
        
        .stError {
            background-color: rgba(239, 68, 68, 0.1) !important;
            border-left: 4px solid var(--error-color) !important;
            color: var(--text-primary) !important;
        }
        
        .stWarning {
            background-color: rgba(245, 158, 11, 0.1) !important;
            border-left: 4px solid var(--warning-color) !important;
            color: var(--text-primary) !important;
        }
        
        .stInfo {
            background-color: rgba(59, 130, 246, 0.1) !important;
            border-left: 4px solid var(--info-color) !important;
            color: var(--text-primary) !important;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            color: var(--text-primary) !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: var(--text-secondary) !important;
        }
        
        .stMetric {
            background-color: var(--bg-secondary) !important;
            padding: 16px !important;
            border-radius: 8px !important;
            border: 1px solid var(--border-color) !important;
        }
        
        /* Dataframe */
        .stDataFrame {
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
        }
        
        /* File uploader */
        .stFileUploader {
            background-color: var(--bg-secondary) !important;
            border: 2px dashed var(--border-color) !important;
            border-radius: 8px !important;
        }
        
        /* Progress bar */
        .stProgress > div > div > div > div {
            background-color: var(--primary-color) !important;
        }
        
        /* Spinner */
        .stSpinner > div {
            border-top-color: var(--primary-color) !important;
        }
        
        /* Plotly charts */
        .js-plotly-plot {
            background-color: var(--bg-secondary) !important;
        }
        
        .js-plotly-plot .plotly {
            background-color: var(--bg-secondary) !important;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 10px !important;
            height: 10px !important;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-secondary) !important;
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--primary-color) !important;
            border-radius: 5px !important;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary-hover) !important;
        }
        
        /* Form elements */
        .stForm {
            background-color: var(--bg-secondary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            padding: 20px !important;
        }
        
        /* Columns */
        [data-testid="column"] {
            background-color: transparent !important;
        }
        
        /* Caption text */
        .stCaption {
            color: var(--text-secondary) !important;
        }
        
        /* Links */
        a {
            color: var(--primary-color) !important;
        }
        
        a:hover {
            color: var(--primary-hover) !important;
        }
        </style>
    """, unsafe_allow_html=True)


def load_theme_css():
    """Load additional dark mode CSS"""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        * {
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Smooth transitions */
        * {
            transition: background-color 0.3s ease, color 0.3s ease !important;
        }
        
        /* Custom card styling for dark mode */
        .card {
            background: var(--card-bg, #1e1e1e) !important;
            border-radius: 15px !important;
            padding: 20px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
            margin: 10px 0 !important;
            border: 1px solid var(--border-color, #3e3e3e) !important;
            color: var(--text-primary, #fafafa) !important;
        }
        
        .card:hover {
            background: var(--card-hover, #262730) !important;
            box-shadow: 0 6px 20px rgba(0,0,0,0.4) !important;
        }
        
        /* Feature card hover effect */
        .feature-card {
            transition: transform 0.3s ease, box-shadow 0.3s ease !important;
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
        }
        
        .feature-card:hover {
            transform: translateY(-5px) !important;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
        }
        
        /* Ensure all divs have proper dark background */
        div[data-testid="stVerticalBlock"] > div {
            background-color: transparent !important;
        }
        
        /* Container backgrounds */
        .block-container {
            background-color: var(--bg-primary) !important;
        }
        
        /* Widget backgrounds */
        .stSelectbox, .stTextInput, .stTextArea, .stNumberInput {
            background-color: var(--bg-secondary) !important;
        }
        </style>
    """, unsafe_allow_html=True)


def apply_light_theme():
    """Light theme disabled - always use dark"""
    apply_dark_theme()


def toggle_theme():
    """Theme toggle disabled - always dark"""
    pass


def get_current_theme():
    """Always return dark theme"""
    return "dark"


def set_theme(theme: str):
    """Always set to dark theme"""
    st.session_state.theme = "dark"
    apply_dark_theme()
