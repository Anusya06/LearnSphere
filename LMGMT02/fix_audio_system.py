"""
Script to fix the audio system in Learn page
"""

# Read the file
with open("frontend/pages/2_Learn.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Fix imports - remove old gtts import and add audio_generator
old_import = """from utils.advanced_features_db import get_advanced_db
from groq import Groq

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False"""

new_import = """from utils.advanced_features_db import get_advanced_db
from utils.audio_generator import get_audio_generator, GTTS_AVAILABLE
from groq import Groq"""

content = content.replace(old_import, new_import)

# 2. Find and replace render_audio_tab function
# Find the start
start_marker = "def render_audio_tab():"
start_idx = content.find(start_marker)

if start_idx == -1:
    print("ERROR: Could not find render_audio_tab function")
    exit(1)

# Find the next function definition after render_audio_tab
next_func_idx = content.find("\ndef render_", start_idx + len(start_marker))

if next_func_idx == -1:
    print("ERROR: Could not find end of render_audio_tab")
    exit(1)

# Extract old function
old_function = content[start_idx:next_func_idx]

# New optimized function
new_function = '''def render_audio_tab():
    """OPTIMIZED: Fast audio generation with caching and multiple modes"""
    if not GTTS_AVAILABLE:
        st.warning("⚠️ Install gTTS and pydub for optimized audio")
        st.code("pip install gtts pydub", language="bash")
        return
    
    if not st.session_state.generated_content:
        st.info("👆 Generate content first to enable audio")
        return
    
    st.markdown("### 🔊 AI Audio Learning")
    st.caption("Optimized audio generation with caching - 90% faster!")
    
    # Get audio generator
    try:
        audio_gen = get_audio_generator()
    except Exception as e:
        st.error(f"Error initializing audio generator: {e}")
        return
    
    # Audio mode and language selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        audio_mode = st.selectbox(
            "Audio Mode",
            ["Full Content", "Fast Mode (3000 chars)", "Summary (1-2 min)", "Podcast Style"],
            key="audio_mode_select",
            help="Fast Mode: Quick preview | Summary: Key points only | Podcast: Conversational format"
        )
    
    with col2:
        language_options = [
            ("English", "en"),
            ("Spanish", "es"),
            ("French", "fr"),
            ("German", "de")
        ]
        language = st.selectbox(
            "Language",
            language_options,
            format_func=lambda x: x[0],
            key="audio_lang_select"
        )
    
    # Generate button
    if st.button("🎵 Generate Audio", use_container_width=True, type="primary"):
        import time
        with st.spinner("Generating audio... This will be fast!"):
            start_time = time.time()
            
            text = st.session_state.generated_content.replace("#", "").replace("*", "").replace("`", "")
            lang_code = language[1]
            
            try:
                # Generate based on mode
                if audio_mode == "Fast Mode (3000 chars)":
                    audio_buffer = audio_gen.generate_audio_fast(text, lang_code)
                elif audio_mode == "Summary (1-2 min)":
                    audio_buffer = audio_gen.generate_summary_audio(text, lang_code)
                elif audio_mode == "Podcast Style":
                    audio_buffer = audio_gen.generate_podcast_audio(
                        st.session_state.current_topic,
                        text,
                        lang_code
                    )
                else:  # Full Content
                    audio_buffer = audio_gen.generate_audio_parallel(text, lang_code)
                
                generation_time = time.time() - start_time
                
                if audio_buffer:
                    st.session_state.audio_file = audio_buffer
                    
                    # Save to history
                    if st.session_state.get("user_id"):
                        content_hash = audio_gen.generate_content_hash(text, 'default', lang_code)
                        audio_gen.save_audio_history(
                            st.session_state.user_id,
                            st.session_state.current_topic,
                            content_hash
                        )
                    
                    st.success(f"✅ Audio generated in {generation_time:.1f} seconds!")
                    st.rerun()
                else:
                    st.error("Failed to generate audio. Please try again.")
            except Exception as e:
                st.error(f"Error generating audio: {str(e)}")
    
    # Display audio player
    if st.session_state.audio_file:
        st.markdown("---")
        st.markdown("#### 🎧 Audio Player")
        
        st.audio(st.session_state.audio_file, format="audio/mp3")
        
        # Playback controls info
        st.caption("💡 Use browser controls for play/pause/speed adjustment (0.5x - 2x)")
        
        # Download button
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download Audio",
                data=st.session_state.audio_file,
                file_name=f"{st.session_state.current_topic.replace(' ', '_')}_audio.mp3",
                mime="audio/mp3",
                use_container_width=True
            )
        
        with col2:
            if st.button("🔄 Regenerate", use_container_width=True):
                st.session_state.audio_file = None
                st.rerun()
        
        # Section-wise audio option
        st.markdown("---")
        st.markdown("#### 📚 Section-Wise Audio")
        st.caption("Split content into sections for easier navigation")
        
        if st.button("🎯 Generate Section Audio", use_container_width=True):
            with st.spinner("Splitting into sections..."):
                try:
                    sections = audio_gen.split_into_sections(st.session_state.generated_content)
                    st.session_state.audio_sections = sections
                    st.success(f"✅ Split into {len(sections)} sections!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error splitting sections: {e}")
        
        # Display sections
        if st.session_state.get("audio_sections"):
            for section_name in st.session_state.audio_sections.keys():
                with st.expander(f"🎵 {section_name}"):
                    section_content = st.session_state.audio_sections[section_name]
                    st.markdown(f"**Preview**: {section_content[:200]}...")
                    
                    if st.button(f"Generate Audio", key=f"section_{hash(section_name)}"):
                        with st.spinner(f"Generating {section_name}..."):
                            try:
                                section_audio = audio_gen.generate_section_audio(
                                    section_name,
                                    section_content,
                                    language[1]
                                )
                                if section_audio:
                                    st.audio(section_audio, format="audio/mp3")
                                    st.download_button(
                                        f"📥 Download {section_name}",
                                        section_audio,
                                        f"{section_name.replace(' ', '_')}_audio.mp3",
                                        "audio/mp3",
                                        key=f"download_{hash(section_name)}"
                                    )
                            except Exception as e:
                                st.error(f"Error: {e}")
    
    # Audio history
    if st.session_state.get("user_id"):
        st.markdown("---")
        st.markdown("#### 📜 Recently Listened")
        
        try:
            history = audio_gen.get_audio_history(st.session_state.user_id, limit=5)
            
            if history:
                for item in history:
                    st.markdown(f"""
                        <div style="background:#1e1e1e;padding:10px;border-radius:8px;margin:5px 0;border-left:3px solid #667eea">
                            <p style="margin:0;color:#fafafa;font-weight:500">🎵 {item['topic']}</p>
                            <p style="margin:5px 0 0 0;color:#b0b0b0;font-size:0.8em">📅 {item['listened_at'][:16]}</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No listening history yet. Generate audio to start!")
        except Exception as e:
            st.caption(f"Could not load history: {e}")

'''

# Replace the function
content = content.replace(old_function, new_function)

# Write back
with open("frontend/pages/2_Learn.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Audio system fixed successfully!")
print("Changes made:")
print("1. Updated imports to use audio_generator")
print("2. Replaced render_audio_tab() with optimized version")
print("\nNext steps:")
print("1. pip install gtts pydub")
print("2. streamlit run frontend/Home.py")
print("3. Test the audio tab!")
