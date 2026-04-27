"""
Code Complexity Analyzer Page
AI-powered time/space complexity analysis and optimization suggestions
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from components.auth_components import check_authentication
from utils.theme_helper import apply_theme, load_theme_css
from utils.sidebar_fix import apply_sidebar_fix
from utils.code_complexity import get_complexity_analyzer

st.set_page_config(
    page_title="Code Complexity Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
load_theme_css()
apply_sidebar_fix()


def render_complexity_score(score: int):
    """Render efficiency score as a colored gauge"""
    if score >= 80:
        color = "#10b981"
        label = "Excellent"
        emoji = "🟢"
    elif score >= 60:
        color = "#f59e0b"
        label = "Good"
        emoji = "🟡"
    elif score >= 40:
        color = "#f97316"
        label = "Fair"
        emoji = "🟠"
    else:
        color = "#ef4444"
        label = "Needs Work"
        emoji = "🔴"

    st.markdown(f"""
        <div style="
            background: {color}22;
            border: 2px solid {color};
            border-radius: 15px;
            padding: 20px;
            text-align: center;
        ">
            <div style="font-size: 3em;">{emoji}</div>
            <div style="font-size: 2.5em; font-weight: 800; color: {color};">{score}/100</div>
            <div style="color: {color}; font-weight: 600; font-size: 1.1em;">{label}</div>
            <div style="
                background: rgba(0,0,0,0.2);
                border-radius: 10px;
                height: 10px;
                margin-top: 12px;
                overflow: hidden;
            ">
                <div style="
                    background: {color};
                    height: 100%;
                    width: {score}%;
                    border-radius: 10px;
                "></div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_complexity_badge(label: str, value: str, color: str):
    st.markdown(f"""
        <div style="
            background: {color}22;
            border: 2px solid {color};
            border-radius: 12px;
            padding: 15px 20px;
            text-align: center;
        ">
            <div style="color: rgba(255,255,255,0.6); font-size: 0.85em; margin-bottom: 5px;">{label}</div>
            <div style="color: {color}; font-size: 1.8em; font-weight: 800;">{value}</div>
        </div>
    """, unsafe_allow_html=True)


def main():
    if not check_authentication():
        st.warning("Please login to use the Code Complexity Analyzer")
        if st.button("Go to Login"):
            st.switch_page("Home.py")
        st.stop()

    # Header
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 30px;
        ">
            <h1 style="color: white; margin: 0;">🔍 Code Complexity Analyzer</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 1.1em;">
                Analyze time & space complexity with AI-powered optimization suggestions
            </p>
        </div>
    """, unsafe_allow_html=True)

    user_id = st.session_state.get("user_id")
    analyzer = get_complexity_analyzer()

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### ✏️ Paste Your Code")

        language = st.selectbox(
            "Language",
            ["Python", "JavaScript", "Java", "C++", "C", "Go", "Rust"],
            key="complexity_language"
        )

        code = st.text_area(
            "Code",
            height=350,
            placeholder="""# Paste your code here
def find_duplicates(arr):
    result = []
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] == arr[j]:
                result.append(arr[i])
    return result""",
            key="complexity_code",
            label_visibility="collapsed"
        )

        if st.button("🔍 Analyze Complexity", use_container_width=True, type="primary"):
            if not code.strip():
                st.error("Please paste some code to analyze")
            else:
                with st.spinner("🤖 AI is analyzing your code..."):
                    result = analyzer.analyze(code, language, user_id)
                    st.session_state.complexity_result = result
                    st.rerun()

        # Analysis history
        if user_id:
            history = analyzer.get_history(user_id, limit=5)
            if history:
                st.markdown("### 📅 Recent Analyses")
                for item in history:
                    st.markdown(f"""
                        <div style="
                            background: rgba(255,255,255,0.05);
                            padding: 10px 15px;
                            border-radius: 8px;
                            margin: 6px 0;
                            border-left: 3px solid #667eea;
                        ">
                            <span style="color: #667eea; font-weight: 600;">{item['language']}</span>
                            <span style="color: rgba(255,255,255,0.6); margin-left: 10px; font-size: 0.85em;">
                                {item['time']} • Score: {item['score']}/100
                            </span>
                        </div>
                    """, unsafe_allow_html=True)

    with col_right:
        st.markdown("### 📊 Analysis Results")

        result = st.session_state.get("complexity_result")

        if not result:
            st.markdown("""
                <div style="
                    background: rgba(102, 126, 234, 0.1);
                    border: 2px dashed #667eea;
                    border-radius: 15px;
                    padding: 40px;
                    text-align: center;
                ">
                    <div style="font-size: 4em; margin-bottom: 15px;">🔍</div>
                    <h3 style="color: #667eea;">Paste code and click Analyze</h3>
                    <p style="color: rgba(255,255,255,0.6);">
                        Get instant Big-O analysis, efficiency score, and optimization tips
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else:
            # Efficiency score
            render_complexity_score(result.get('efficiency_score', 50))

            st.markdown("<br>", unsafe_allow_html=True)

            # Complexity badges
            col_a, col_b = st.columns(2)
            with col_a:
                render_complexity_badge("⏱️ Time Complexity", result.get('time_complexity', 'N/A'), "#667eea")
            with col_b:
                render_complexity_badge("💾 Space Complexity", result.get('space_complexity', 'N/A'), "#764ba2")

            st.markdown("<br>", unsafe_allow_html=True)

            # Explanations
            with st.expander("📖 Complexity Explanation", expanded=True):
                st.markdown(f"**Time:** {result.get('complexity_explanation', 'N/A')}")
                st.markdown(f"**Space:** {result.get('space_explanation', 'N/A')}")

            # Inefficient parts
            inefficient = result.get('inefficient_parts', [])
            if inefficient:
                with st.expander("⚠️ Inefficient Parts", expanded=True):
                    for part in inefficient:
                        st.markdown(f"""
                            <div style="
                                background: rgba(239, 68, 68, 0.1);
                                border-left: 3px solid #ef4444;
                                padding: 12px;
                                border-radius: 8px;
                                margin: 8px 0;
                            ">
                                <code style="color: #ef4444;">{part.get('line', '')}</code><br>
                                <span style="color: rgba(255,255,255,0.8);">⚠️ {part.get('issue', '')}</span><br>
                                <span style="color: #10b981;">💡 {part.get('suggestion', '')}</span>
                            </div>
                        """, unsafe_allow_html=True)

            # Optimizations
            optimizations = result.get('optimizations', [])
            if optimizations:
                with st.expander("💡 Optimization Suggestions", expanded=True):
                    for i, opt in enumerate(optimizations, 1):
                        st.markdown(f"""
                            <div style="
                                background: rgba(16, 185, 129, 0.1);
                                border-left: 3px solid #10b981;
                                padding: 10px 15px;
                                border-radius: 8px;
                                margin: 6px 0;
                                color: rgba(255,255,255,0.9);
                            ">
                                <strong style="color: #10b981;">{i}.</strong> {opt}
                            </div>
                        """, unsafe_allow_html=True)

            # Optimized code
            optimized = result.get('optimized_code', '')
            if optimized and optimized != st.session_state.get("complexity_code", ""):
                with st.expander("✨ Optimized Version"):
                    st.code(optimized, language=st.session_state.get("complexity_language", "python").lower())

            # Overall assessment
            assessment = result.get('overall_assessment', '')
            if assessment:
                st.markdown(f"""
                    <div style="
                        background: rgba(102, 126, 234, 0.1);
                        border: 1px solid #667eea;
                        border-radius: 10px;
                        padding: 15px;
                        margin-top: 15px;
                        color: rgba(255,255,255,0.9);
                    ">
                        <strong style="color: #667eea;">📋 Assessment:</strong> {assessment}
                    </div>
                """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
