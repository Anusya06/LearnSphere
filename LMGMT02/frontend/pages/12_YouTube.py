"""
YouTube Video Summarizer Page
Convert YouTube videos into learning material
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from components.auth_components import check_authentication
from utils.theme_helper import apply_theme, load_theme_css
from utils.sidebar_fix import apply_sidebar_fix
from utils.youtube_summarizer import get_youtube_summarizer

st.set_page_config(
    page_title="YouTube Summarizer",
    page_icon="▶️",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
load_theme_css()
apply_sidebar_fix()


def render_quiz_section(questions: list):
    if not questions:
        st.info("No quiz questions available")
        return

    if "yt_quiz_answers" not in st.session_state:
        st.session_state.yt_quiz_answers = {}
    if "yt_quiz_submitted" not in st.session_state:
        st.session_state.yt_quiz_submitted = False

    if not st.session_state.yt_quiz_submitted:
        for i, q in enumerate(questions):
            st.markdown(f"**Q{i+1}. {q['question']}**")
            answer = st.radio("Answer", q['options'], key=f"yt_q_{i}", index=None, label_visibility="collapsed")
            if answer:
                st.session_state.yt_quiz_answers[i] = answer
            st.markdown("<br>", unsafe_allow_html=True)

        answered = len(st.session_state.yt_quiz_answers)
        if st.button(f"Submit ({answered}/{len(questions)} answered)",
                     use_container_width=True, type="primary",
                     disabled=answered < len(questions)):
            st.session_state.yt_quiz_submitted = True
            st.rerun()
    else:
        score = 0
        for i, q in enumerate(questions):
            user_ans = st.session_state.yt_quiz_answers.get(i, "")
            correct = user_ans == q['correct_answer']
            if correct:
                score += 1
            color = "#10b981" if correct else "#ef4444"
            icon = "✅" if correct else "❌"
            st.markdown(f"""
                <div style="background:{color}11;border-left:3px solid {color};padding:12px;border-radius:8px;margin:8px 0;">
                    <strong style="color:{color};">{icon} {q['question']}</strong><br>
                    <span style="color:rgba(255,255,255,0.7);">Your: {user_ans}</span> |
                    <span style="color:{color};">Correct: {q['correct_answer']}</span><br>
                    <em style="color:rgba(255,255,255,0.5);">{q.get('explanation','')}</em>
                </div>
            """, unsafe_allow_html=True)

        pct = (score / len(questions)) * 100
        st.success(f"Score: {score}/{len(questions)} ({pct:.0f}%)")

        if st.button("🔄 Retake", use_container_width=True):
            st.session_state.yt_quiz_submitted = False
            st.session_state.yt_quiz_answers = {}
            st.rerun()


def main():
    if not check_authentication():
        st.warning("Please login to use the YouTube Summarizer")
        if st.button("Go to Login"):
            st.switch_page("Home.py")
        st.stop()

    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 30px;
        ">
            <h1 style="color: white; margin: 0;">▶️ YouTube Video Summarizer</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 1.1em;">
                Turn any YouTube video into summaries, notes, and quiz questions
            </p>
        </div>
    """, unsafe_allow_html=True)

    user_id = st.session_state.get("user_id")
    summarizer = get_youtube_summarizer()

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown("### 🔗 Enter YouTube URL")

        url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            key="yt_url",
            label_visibility="collapsed"
        )

        # Quick example videos
        st.markdown("**Example topics:**")
        examples = [
            ("🧠 Neural Networks", "https://www.youtube.com/watch?v=aircAruvnKk"),
            ("🐍 Python Tutorial", "https://www.youtube.com/watch?v=_uQrJ0TkZlc"),
            ("📊 Data Science", "https://www.youtube.com/watch?v=ua-CiDNNj30"),
        ]
        for label, ex_url in examples:
            if st.button(label, key=f"ex_{label}", use_container_width=True):
                st.session_state.yt_url = ex_url
                st.rerun()

        num_quiz_q = st.slider("Quiz questions", 3, 8, 5, key="yt_quiz_count")

        if st.button("🚀 Process Video", use_container_width=True, type="primary"):
            if not url:
                st.error("Please enter a YouTube URL")
            else:
                video_id = summarizer.extract_video_id(url)
                if not video_id:
                    st.error("Invalid YouTube URL. Please check the link.")
                else:
                    with st.spinner("📥 Fetching transcript..."):
                        transcript, error = summarizer.get_transcript(video_id)

                    if error:
                        st.error(f"❌ {error}")
                        st.info("💡 Tip: Make sure the video has captions/subtitles enabled.")
                    else:
                        st.session_state.yt_transcript = transcript
                        st.session_state.yt_video_id = video_id
                        st.session_state.yt_video_url = url
                        st.session_state.yt_summary = None
                        st.session_state.yt_key_points = None
                        st.session_state.yt_notes = None
                        st.session_state.yt_quiz = None
                        st.session_state.yt_quiz_answers = {}
                        st.session_state.yt_quiz_submitted = False
                        st.success(f"✅ Transcript loaded ({len(transcript)} chars)")
                        st.rerun()

        # Previous summaries
        if user_id:
            summaries = summarizer.get_user_summaries(user_id)
            if summaries:
                st.markdown("### 📚 Recent Videos")
                for s in summaries[:5]:
                    vid_id = s.get('video_id', '')
                    st.markdown(f"""
                        <div style="
                            background: rgba(255,255,255,0.05);
                            border-radius: 8px;
                            padding: 10px;
                            margin: 5px 0;
                            border-left: 3px solid #ef4444;
                        ">
                            <a href="{s['url']}" target="_blank" style="color: #ef4444; font-size: 0.85em; text-decoration: none;">
                                ▶️ {vid_id}
                            </a><br>
                            <span style="color: rgba(255,255,255,0.5); font-size: 0.8em;">{s['date'][:10]}</span>
                        </div>
                    """, unsafe_allow_html=True)

    with col_right:
        transcript = st.session_state.get("yt_transcript")
        video_id = st.session_state.get("yt_video_id")

        if not transcript:
            st.markdown("""
                <div style="
                    background: rgba(239, 68, 68, 0.1);
                    border: 2px dashed #ef4444;
                    border-radius: 15px;
                    padding: 60px 40px;
                    text-align: center;
                ">
                    <div style="font-size: 5em; margin-bottom: 20px;">▶️</div>
                    <h3 style="color: #ef4444;">Paste a YouTube URL to get started</h3>
                    <p style="color: rgba(255,255,255,0.6);">
                        Works with any video that has captions/subtitles.<br>
                        Requires: <code>pip install youtube-transcript-api</code>
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else:
            # Embed video
            if video_id:
                st.markdown(f"""
                    <div style="position: relative; padding-bottom: 30%; height: 0; overflow: hidden; border-radius: 12px; margin-bottom: 20px;">
                        <iframe
                            src="https://www.youtube.com/embed/{video_id}"
                            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; border-radius: 12px;"
                            allowfullscreen>
                        </iframe>
                    </div>
                """, unsafe_allow_html=True)

            tab_summary, tab_points, tab_notes, tab_quiz = st.tabs(
                ["📋 Summary", "🎯 Key Points", "📝 Notes", "❓ Quiz"]
            )

            with tab_summary:
                if not st.session_state.get("yt_summary"):
                    if st.button("🤖 Generate Summary", use_container_width=True, type="primary", key="gen_yt_summary"):
                        with st.spinner("Summarizing video..."):
                            summary = summarizer.generate_summary(transcript, st.session_state.get("yt_video_url", ""))
                            st.session_state.yt_summary = summary
                            st.rerun()
                else:
                    st.markdown(st.session_state.yt_summary)

            with tab_points:
                if not st.session_state.get("yt_key_points"):
                    if st.button("🤖 Extract Key Points", use_container_width=True, type="primary", key="gen_yt_points"):
                        with st.spinner("Extracting key points..."):
                            points = summarizer.generate_key_points(transcript)
                            st.session_state.yt_key_points = points
                            st.rerun()
                else:
                    for i, point in enumerate(st.session_state.yt_key_points, 1):
                        st.markdown(f"""
                            <div style="
                                background: rgba(102, 126, 234, 0.1);
                                border-left: 3px solid #667eea;
                                padding: 12px 15px;
                                border-radius: 8px;
                                margin: 8px 0;
                                color: rgba(255,255,255,0.9);
                            ">
                                <strong style="color: #667eea;">{i}.</strong> {point}
                            </div>
                        """, unsafe_allow_html=True)

            with tab_notes:
                if not st.session_state.get("yt_notes"):
                    if st.button("🤖 Generate Notes", use_container_width=True, type="primary", key="gen_yt_notes"):
                        with st.spinner("Generating study notes..."):
                            notes = summarizer.generate_notes(transcript)
                            st.session_state.yt_notes = notes
                            st.rerun()
                else:
                    st.markdown(st.session_state.yt_notes)

            with tab_quiz:
                if not st.session_state.get("yt_quiz"):
                    if st.button("🤖 Generate Quiz", use_container_width=True, type="primary", key="gen_yt_quiz"):
                        with st.spinner("Generating quiz..."):
                            quiz = summarizer.generate_quiz(transcript, num_quiz_q)
                            st.session_state.yt_quiz = quiz
                            st.rerun()
                else:
                    render_quiz_section(st.session_state.yt_quiz)

            # Save
            if st.session_state.get("yt_summary") and user_id:
                if st.button("💾 Save to Library", use_container_width=True):
                    summarizer.save_summary(
                        user_id,
                        st.session_state.get("yt_video_url", ""),
                        video_id,
                        transcript,
                        st.session_state.get("yt_summary", ""),
                        st.session_state.get("yt_key_points", []),
                        st.session_state.get("yt_notes", ""),
                        st.session_state.get("yt_quiz", [])
                    )
                    st.success("✅ Saved to your video library!")


if __name__ == "__main__":
    main()
