"""
Sidebar Navigation Fix - Hide keyboard_double icon and ensure hamburger menu works
"""
import streamlit as st


def apply_sidebar_fix():
    """
    Apply minimal sidebar fixes:
    - Hide the keyboard_double collapse control
    - Ensure hamburger menu is visible and functional
    - Keep layout centered
    """
    st.markdown("""
    <style>
    /* ========================================
       HIDE KEYBOARD_DOUBLE ICON
       ======================================== */
    
    /* Hide the keyboard_double collapse control */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* ========================================
       HAMBURGER MENU STYLING
       ======================================== */
    
    /* Ensure hamburger menu button is visible */
    button[kind="header"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    /* ========================================
       LAYOUT CENTERING AND SPACING
       ======================================== */
    
    /* Ensure main content is properly centered */
    .main .block-container {
        max-width: 1400px !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        padding-top: 2rem !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    
    /* Fix column alignment */
    [data-testid="column"] {
        padding: 0.5rem !important;
    }
    
    /* Responsive grid for cards */
    .stColumns {
        gap: 1.5rem !important;
    }
    
    /* ========================================
       SIDEBAR TEXT VISIBILITY
       ======================================== */

    /* All sidebar text bright white */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
        -webkit-font-smoothing: antialiased !important;
    }

    /* Sidebar nav links */
    [data-testid="stSidebarNav"] a,
    [data-testid="stSidebarNav"] span,
    [data-testid="stSidebarNav"] p {
        color: #e8e8e8 !important;
        font-weight: 500 !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebarNav"] a:hover {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Sidebar section headers */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Sidebar caption/small text */
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] small {
        color: #b0b0b0 !important;
    }

    /* ========================================
       WIDGET LABEL VISIBILITY
       ======================================== */

    /* All widget labels - bright and readable */
    label, .stWidgetLabel, [data-testid="stWidgetLabel"] {
        color: #ffffff !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }

    /* Input placeholder text */
    input::placeholder, textarea::placeholder {
        color: rgba(255,255,255,0.45) !important;
        opacity: 1 !important;
    }

    /* Selectbox selected value */
    [data-baseweb="select"] span,
    [data-baseweb="select"] div[class*="singleValue"],
    [data-baseweb="select"] div[class*="placeholder"] {
        color: #ffffff !important;
        opacity: 1 !important;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin: 12px 0 !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
        color: #ffffff !important;
    }
    
    .glass-card-header {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        margin-bottom: 16px !important;
    }
    
    .glass-card-icon {
        font-size: 1.5rem !important;
    }
    
    .glass-card-title {
        margin: 0 !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #ffffff !important;
    }
    
    /* ========================================
       STAT CARD STYLES
       ======================================== */
    
    .stat-card {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        display: flex !important;
        align-items: center !important;
        gap: 16px !important;
        transition: all 0.3s ease !important;
    }
    
    .stat-card:hover {
        background: rgba(255, 255, 255, 0.08) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3) !important;
    }
    
    .stat-icon {
        font-size: 2rem !important;
        width: 50px !important;
        height: 50px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: rgba(102, 126, 234, 0.15) !important;
        border-radius: 12px !important;
    }
    
    .stat-content {
        flex: 1 !important;
    }
    
    .stat-value {
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        line-height: 1 !important;
    }
    
    .stat-label {
        font-size: 0.8rem !important;
        color: rgba(255, 255, 255, 0.6) !important;
        margin-top: 4px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    /* ========================================
       HERO HEADER STYLES
       ======================================== */
    
    .hero-header {
        text-align: center !important;
        padding: 2rem 0 !important;
    }
    
    .hero-title {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        margin: 0 0 0.5rem 0 !important;
    }
    
    .hero-subtitle {
        color: rgba(255, 255, 255, 0.7) !important;
        font-size: 1.1rem !important;
        margin: 0 !important;
    }
    
    /* ========================================
       ACHIEVEMENT CARD STYLES
       ======================================== */
    
    .achievement-card {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        padding: 12px !important;
        border-radius: 10px !important;
        margin: 8px 0 !important;
        transition: all 0.3s ease !important;
    }
    
    .achievement-unlocked {
        background: rgba(245, 158, 11, 0.1) !important;
        border: 1px solid rgba(245, 158, 11, 0.3) !important;
    }
    
    .achievement-locked {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        opacity: 0.5 !important;
    }
    
    .achievement-icon {
        font-size: 1.5rem !important;
        width: 40px !important;
        text-align: center !important;
    }
    
    .achievement-content {
        flex: 1 !important;
    }
    
    .achievement-title {
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        color: #ffffff !important;
    }
    
    .achievement-description {
        font-size: 0.75rem !important;
        color: rgba(255, 255, 255, 0.5) !important;
        margin-top: 2px !important;
    }
    
    /* ========================================
       RESPONSIVE DESIGN
       ======================================== */
    
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        .hero-title {
            font-size: 1.8rem !important;
        }
        
        .stat-card {
            padding: 15px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
