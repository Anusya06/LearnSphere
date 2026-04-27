"""
Reusable UI components with modern design
"""
import streamlit as st
from typing import Optional, List, Dict, Any


def gradient_card(
    title: str,
    content: str,
    icon: str = "📚",
    gradient: str = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    action_label: Optional[str] = None,
    action_key: Optional[str] = None
):
    """Modern gradient card component"""
    
    action_html = ""
    if action_label and action_key:
        action_html = f"""
        <button style="
            background: white;
            color: #667eea;
            border: none;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 15px;
        ">{action_label}</button>
        """
    
    st.markdown(f"""
        <div style="
            background: {gradient};
            padding: 25px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            margin: 15px 0;
            color: white;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        " onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 15px 40px rgba(0,0,0,0.25)';"
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 10px 30px rgba(0,0,0,0.15)';">
            <h3 style="margin: 0 0 10px 0; font-size: 1.5em;">{icon} {title}</h3>
            <p style="margin: 0; opacity: 0.95; line-height: 1.6;">{content}</p>
            {action_html}
        </div>
    """, unsafe_allow_html=True)


def glass_card(title: str, content: str, icon: str = "✨"):
    """Glassmorphism card component - theme aware"""
    st.markdown(f"""
        <div style="
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 25px;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            margin: 15px 0;
        ">
            <h3 style="margin: 0 0 15px 0; color: #667eea;">{icon} {title}</h3>
            <p style="margin: 0; line-height: 1.6; color: var(--text-primary, #ffffff);">{content}</p>
        </div>
    """, unsafe_allow_html=True)


def animated_progress_bar(percentage: float, label: str = "", color: str = "#667eea"):
    """Animated progress bar with percentage - theme aware"""
    st.markdown(f"""
        <div style="margin: 20px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="font-weight: 600; color: var(--text-primary, #ffffff);">{label}</span>
                <span style="font-weight: 700; color: {color};">{percentage:.0f}%</span>
            </div>
            <div style="
                background: var(--bg-tertiary, #262730);
                border-radius: 10px;
                height: 12px;
                overflow: hidden;
                position: relative;
            ">
                <div style="
                    background: linear-gradient(90deg, {color}, {color}dd);
                    width: {percentage}%;
                    height: 100%;
                    border-radius: 10px;
                    transition: width 1s ease;
                    box-shadow: 0 0 10px {color}88;
                "></div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def stat_card(value: str, label: str, icon: str, color: str = "#667eea"):
    """Stat card for dashboard metrics - theme aware"""
    st.markdown(f"""
        <div class="stat-card" style="
            background: var(--card-bg, #1c1f26);
            color: var(--text-primary, #ffffff);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            text-align: center;
            border-left: 4px solid {color};
        ">
            <div style="font-size: 2.5em; margin-bottom: 5px;">{icon}</div>
            <div style="font-size: 2em; font-weight: 700; color: {color}; margin: 10px 0;">{value}</div>
            <div style="color: var(--text-secondary, #bbbbbb); font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px;">{label}</div>
        </div>
    """, unsafe_allow_html=True)


def toast_notification(message: str, type: str = "success"):
    """Toast notification"""
    colors = {
        "success": "#10b981",
        "error": "#ef4444",
        "warning": "#f59e0b",
        "info": "#3b82f6"
    }
    
    icons = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️"
    }
    
    color = colors.get(type, colors["info"])
    icon = icons.get(type, icons["info"])
    
    st.markdown(f"""
        <div style="
            background: {color};
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            margin: 10px 0;
            display: flex;
            align-items: center;
            gap: 10px;
            animation: slideIn 0.3s ease;
        ">
            <span style="font-size: 1.5em;">{icon}</span>
            <span style="font-weight: 500;">{message}</span>
        </div>
        <style>
        @keyframes slideIn {{
            from {{ transform: translateX(-100%); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        </style>
    """, unsafe_allow_html=True)


def badge(text: str, color: str = "#667eea"):
    """Small badge component"""
    return f"""
        <span style="
            background: {color};
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
            display: inline-block;
            margin: 2px;
        ">{text}</span>
    """


def timeline_item(title: str, description: str, completed: bool = False):
    """Timeline item for roadmap - theme aware"""
    color = "#10b981" if completed else "#555555"
    icon = "✓" if completed else "○"
    
    st.markdown(f"""
        <div style="
            display: flex;
            gap: 15px;
            margin: 20px 0;
            padding-left: 10px;
            border-left: 3px solid {color};
        ">
            <div style="
                width: 30px;
                height: 30px;
                background: {color};
                color: white;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                flex-shrink: 0;
            ">{icon}</div>
            <div style="flex: 1;">
                <h4 style="margin: 0 0 5px 0; color: var(--text-primary, #ffffff);">{title}</h4>
                <p style="margin: 0; color: var(--text-secondary, #bbbbbb); font-size: 0.9em;">{description}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)


def floating_action_button(icon: str = "💬", label: str = "Chat"):
    """Floating action button"""
    st.markdown(f"""
        <div style="
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 25px;
            border-radius: 50px;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
            cursor: pointer;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
            transition: transform 0.3s ease;
        " onmouseover="this.style.transform='scale(1.1)';"
           onmouseout="this.style.transform='scale(1)';">
            <span style="font-size: 1.3em;">{icon}</span>
            <span>{label}</span>
        </div>
    """, unsafe_allow_html=True)


def theme_toggle_button():
    """Theme toggle button component"""
    import streamlit as st
    
    current_theme = st.session_state.get("theme", "light")
    theme_icon = "🌙" if current_theme == "light" else "☀️"
    theme_text = "Dark Mode" if current_theme == "light" else "Light Mode"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(f"{theme_icon} {theme_text}", key="theme_toggle_main", use_container_width=True):
            st.session_state.theme = "dark" if current_theme == "light" else "light"
            st.rerun()


def empty_state(
    icon: str = "📊",
    title: str = "No Data Yet",
    message: str = "Get started to see content here",
    actions: Optional[List[Dict[str, str]]] = None
):
    """Empty state component for when no data exists - theme aware"""
    
    actions_html = ""
    if actions:
        actions_html = '<div style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">'
        for action in actions:
            style = "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;" if action.get("primary") else "background: var(--card-bg, #1c1f26); color: #667eea; border: 2px solid #667eea;"
            actions_html += f'''
                <a href="{action.get('url', '#')}" style="
                    {style}
                    padding: 12px 30px;
                    border-radius: 25px;
                    text-decoration: none;
                    font-weight: 600;
                ">{action.get('label', 'Action')}</a>
            '''
        actions_html += '</div>'
    
    st.markdown(f"""
        <div style="
            text-align: center;
            padding: 80px 20px;
            background: linear-gradient(135deg, #667eea22 0%, #764ba244 100%);
            border-radius: 20px;
            margin: 40px 0;
        ">
            <div style="font-size: 5em; margin-bottom: 20px;">{icon}</div>
            <h2 style="color: #667eea; margin-bottom: 15px;">{title}</h2>
            <p style="color: var(--text-secondary, #bbbbbb); font-size: 1.2em; margin-bottom: 30px;">
                {message}
            </p>
            {actions_html}
        </div>
    """, unsafe_allow_html=True)
