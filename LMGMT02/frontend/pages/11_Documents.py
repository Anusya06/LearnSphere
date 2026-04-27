"""
Document Learning Page
Upload PDF/DOCX/TXT and generate summaries, notes, and quizzes
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from components.auth_components import check_authentication
from utils.theme_helper import apply_theme, load_theme_css
from utils.sidebar_fix import apply_sidebar_fix
from utils.document_processor import get_document_processor

st.set_page_config(
    page_title="Document Learning",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
load_theme_css()
apply_sidebar_fix()


def render_quiz_section(questions: list):
    """Render interactive quiz from document"""
    if not questions:
        st.info("No quiz questions generated")
        return

    if "doc_quiz_answers" not in st.session_state:
        st.session_state.doc_quiz_answers = {}
    if "doc_quiz_submitted" not in st.session_state:
        st.session_state.doc_quiz_submitted = False

    if not st.session_state.doc_quiz_submitted:
        for i, q in enumerate(questions):
            st.markdown(f"**Q{i+1}. {q['question']}**")
            answer = st.radio(
                "Select answer",
                q['options'],
                key=f"doc_q_{i}",
                index=None,
                label_visibility="collapsed"
            )
            if answer:
                st.session_state.doc_quiz_answers[i] = answer
            st.markdown("<br>", unsafe_allow_html=True)

        answered = len(st.session_state.doc_quiz_answers)
        if st.button(f"Submit Quiz ({answered}/{len(questions)} answered)",
                     use_container_width=True, type="primary",
                     disabled=answered < len(questions)):
            st.session_state.doc_quiz_submitted = True
            st.rerun()
    else:
        # Show results
        score = 0
        for i, q in enumerate(questions):
            user_ans = st.session_state.doc_quiz_answers.get(i, "")
            correct = user_ans == q['correct_answer']
            if correct:
                score += 1
            color = "#10b981" if correct else "#ef4444"
            icon = "✅" if correct else "❌"
            st.markdown(f"""
                <div style="
                    background: {color}11;
                    border-left: 3px solid {color};
                    padding: 12px;
                    border-radius: 8px;
                    margin: 8px 0;
                ">
                    <strong style="color: {color};">{icon} Q{i+1}. {q['question']}</strong><br>
                    <span style="color: rgba(255,255,255,0.7);">Your answer: {user_ans}</span><br>
                    <span style="color: {color};">Correct: {q['correct_answer']}</span><br>
                    <span style="color: rgba(255,255,255,0.6); font-style: italic;">{q.get('explanation', '')}</span>
                </div>
            """, unsafe_allow_html=True)

        pct = (score / len(questions)) * 100
        st.markdown(f"""
            <div style="
                background: rgba(102, 126, 234, 0.2);
                border: 2px solid #667eea;
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                margin-top: 20px;
            ">
                <h2 style="color: #667eea; margin: 0;">Score: {score}/{len(questions)} ({pct:.0f}%)</h2>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Retake Quiz", use_container_width=True):
            st.session_state.doc_quiz_submitted = False
            st.session_state.doc_quiz_answers = {}
            st.rerun()


def main():
    if not check_authentication():
        st.warning("Please login to use Document Learning")
        if st.button("Go to Login"):
            st.switch_page("Home.py")
        st.stop()

    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 30px;
        ">
            <h1 style="color: white; margin: 0;">📄 Document Learning</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 1.1em;">
                Upload PDF, DOCX, or TXT files and get AI-generated summaries, notes & quizzes
            </p>
        </div>
    """, unsafe_allow_html=True)

    user_id = st.session_state.get("user_id")
    processor = get_document_processor()

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown("### 📤 Upload Document")

        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "docx", "txt"],
            key="doc_upload",
            help="Supported: PDF, DOCX, TXT (max ~10MB)"
        )

        if uploaded_file:
            file_size = len(uploaded_file.getvalue()) / 1024
            st.markdown(f"""
                <div style="
                    background: rgba(16, 185, 129, 0.1);
                    border: 1px solid #10b981;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 10px 0;
                ">
                    <strong style="color: #10b981;">📎 {uploaded_file.name}</strong><br>
                    <span style="color: rgba(255,255,255,0.6); font-size: 0.85em;">
                        {uploaded_file.type} • {file_size:.1f} KB
                    </span>
                </div>
            """, unsafe_allow_html=True)

            num_quiz_q = st.slider("Quiz questions to generate", 3, 10, 5)

            if st.button("🚀 Process Document", use_container_width=True, type="primary"):
                with st.spinner("📖 Extracting text..."):
                    text = processor.extract_text(uploaded_file)

                if not text or text.startswith("["):
                    st.error(f"Could not extract text: {text}")
                else:
                    st.session_state.doc_text = text
                    st.session_state.doc_filename = uploaded_file.name
                    st.session_state.doc_summary = None
                    st.session_state.doc_notes = None
                    st.session_state.doc_quiz = None
                    st.session_state.doc_quiz_answers = {}
                    st.session_state.doc_quiz_submitted = False
                    st.success(f"✅ Extracted {len(text)} characters")
                    st.rerun()

        # Previous documents
        if user_id:
            docs = processor.get_user_documents(user_id)
            if docs:
                st.markdown("### 📚 Previous Documents")
                for doc in docs[:5]:
                    st.markdown(f"""
                        <div style="
                            background: rgba(255,255,255,0.05);
                            border-radius: 8px;
                            padding: 10px;
                            margin: 5px 0;
                            border-left: 3px solid #f59e0b;
                        ">
                            <strong style="color: #f59e0b; font-size: 0.9em;">📄 {doc['filename']}</strong><br>
                            <span style="color: rgba(255,255,255,0.5); font-size: 0.8em;">{doc['date'][:10]}</span>
                        </div>
                    """, unsafe_allow_html=True)

    with col_right:
        text = st.session_state.get("doc_text")
        filename = st.session_state.get("doc_filename", "")

        if not text:
            st.markdown("""
                <div style="
                    background: rgba(245, 158, 11, 0.1);
                    border: 2px dashed #f59e0b;
                    border-radius: 15px;
                    padding: 60px 40px;
                    text-align: center;
                ">
                    <div style="font-size: 5em; margin-bottom: 20px;">📄</div>
                    <h3 style="color: #f59e0b;">Upload a document to get started</h3>
                    <p style="color: rgba(255,255,255,0.6);">
                        Supports PDF, DOCX, and TXT files.<br>
                        AI will generate summaries, notes, and quiz questions.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"### 📖 {filename}")

            # Text preview
            with st.expander("📝 Document Preview", expanded=False):
                st.text(text[:2000] + ("..." if len(text) > 2000 else ""))

            tab_summary, tab_notes, tab_quiz = st.tabs(["📋 Summary", "📝 Notes", "❓ Quiz"])

            with tab_summary:
                if not st.session_state.get("doc_summary"):
                    if st.button("🤖 Generate Summary", use_container_width=True, type="primary"):
                        with st.spinner("Generating summary..."):
                            summary = processor.generate_summary(text)
                            st.session_state.doc_summary = summary
                            st.rerun()
                else:
                    st.markdown(st.session_state.doc_summary)
                    if st.button("🔄 Regenerate", key="regen_summary"):
                        st.session_state.doc_summary = None
                        st.rerun()

            with tab_notes:
                if not st.session_state.get("doc_notes"):
                    if st.button("🤖 Generate Notes", use_container_width=True, type="primary"):
                        with st.spinner("Generating study notes..."):
                            notes = processor.generate_notes(text)
                            st.session_state.doc_notes = notes
                            st.rerun()
                else:
                    st.markdown(st.session_state.doc_notes)
                    if st.button("🔄 Regenerate", key="regen_notes"):
                        st.session_state.doc_notes = None
                        st.rerun()

            with tab_quiz:
                if not st.session_state.get("doc_quiz"):
                    if st.button("🤖 Generate Quiz", use_container_width=True, type="primary"):
                        with st.spinner("Generating quiz questions..."):
                            quiz = processor.generate_quiz(text, num_quiz_q if 'num_quiz_q' in dir() else 5)
                            st.session_state.doc_quiz = quiz
                            st.rerun()
                else:
                    render_quiz_section(st.session_state.doc_quiz)

            # Save button
            if (st.session_state.get("doc_summary") or st.session_state.get("doc_notes")) and user_id:
                if st.button("💾 Save to Library", use_container_width=True):
                    processor.save_document(
                        user_id, filename,
                        filename.split('.')[-1].upper(),
                        text[:500],
                        st.session_state.get("doc_summary", ""),
                        st.session_state.get("doc_notes", ""),
                        st.session_state.get("doc_quiz", [])
                    )
                    st.success("✅ Saved to your document library!")


if __name__ == "__main__":
    main()
