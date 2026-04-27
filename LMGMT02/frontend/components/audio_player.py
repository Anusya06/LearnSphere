"""
Audio player component with Text-to-Speech functionality
"""
import streamlit as st
import streamlit.components.v1 as components


def text_to_speech_player(text: str, key: str = "tts_player"):
    """
    Text-to-Speech player using Web Speech API
    
    Args:
        text: Text to convert to speech
        key: Unique key for the component
    """
    
    # Clean text for JavaScript
    clean_text = text.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .tts-container {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
                margin: 20px 0;
            }}
            
            .tts-controls {{
                display: flex;
                gap: 10px;
                justify-content: center;
                align-items: center;
                flex-wrap: wrap;
            }}
            
            .tts-button {{
                background: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 12px 24px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .tts-button:hover {{
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            }}
            
            .tts-button:active {{
                transform: translateY(0);
            }}
            
            .tts-button:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
            }}
            
            .tts-status {{
                color: white;
                text-align: center;
                margin-top: 15px;
                font-size: 14px;
                min-height: 20px;
            }}
            
            .tts-settings {{
                display: flex;
                gap: 15px;
                justify-content: center;
                margin-top: 15px;
                flex-wrap: wrap;
            }}
            
            .tts-select {{
                background: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 14px;
                cursor: pointer;
            }}
            
            .tts-select option {{
                background: #667eea;
                color: white;
            }}
        </style>
    </head>
    <body>
        <div class="tts-container">
            <div class="tts-controls">
                <button class="tts-button" id="playBtn" onclick="playText()">
                    <span>▶️</span> Play
                </button>
                <button class="tts-button" id="pauseBtn" onclick="pauseSpeech()" disabled>
                    <span>⏸️</span> Pause
                </button>
                <button class="tts-button" id="resumeBtn" onclick="resumeSpeech()" disabled>
                    <span>▶️</span> Resume
                </button>
                <button class="tts-button" id="stopBtn" onclick="stopSpeech()" disabled>
                    <span>⏹️</span> Stop
                </button>
            </div>
            
            <div class="tts-settings">
                <select class="tts-select" id="voiceSelect" onchange="updateVoice()">
                    <option value="">Select Voice</option>
                </select>
                <select class="tts-select" id="rateSelect" onchange="updateRate()">
                    <option value="0.5">0.5x</option>
                    <option value="0.75">0.75x</option>
                    <option value="1" selected>1x</option>
                    <option value="1.25">1.25x</option>
                    <option value="1.5">1.5x</option>
                    <option value="2">2x</option>
                </select>
            </div>
            
            <div class="tts-status" id="status">Ready to play</div>
        </div>
        
        <script>
            let synth = window.speechSynthesis;
            let utterance = null;
            let voices = [];
            let selectedVoice = null;
            let rate = 1;
            
            // Text to speak
            const textToSpeak = `{clean_text}`;
            
            // Load voices
            function loadVoices() {{
                voices = synth.getVoices();
                const voiceSelect = document.getElementById('voiceSelect');
                voiceSelect.innerHTML = '<option value="">Default Voice</option>';
                
                voices.forEach((voice, index) => {{
                    const option = document.createElement('option');
                    option.value = index;
                    option.textContent = `${{voice.name}} (${{voice.lang}})`;
                    voiceSelect.appendChild(option);
                }});
                
                // Select first English voice by default
                const englishVoice = voices.findIndex(v => v.lang.startsWith('en'));
                if (englishVoice !== -1) {{
                    voiceSelect.value = englishVoice;
                    selectedVoice = voices[englishVoice];
                }}
            }}
            
            // Load voices when available
            if (synth.onvoiceschanged !== undefined) {{
                synth.onvoiceschanged = loadVoices;
            }}
            loadVoices();
            
            function updateVoice() {{
                const voiceSelect = document.getElementById('voiceSelect');
                const index = voiceSelect.value;
                if (index !== '') {{
                    selectedVoice = voices[index];
                }} else {{
                    selectedVoice = null;
                }}
            }}
            
            function updateRate() {{
                const rateSelect = document.getElementById('rateSelect');
                rate = parseFloat(rateSelect.value);
            }}
            
            function updateStatus(message) {{
                document.getElementById('status').textContent = message;
            }}
            
            function updateButtons(playing, paused) {{
                document.getElementById('playBtn').disabled = playing;
                document.getElementById('pauseBtn').disabled = !playing || paused;
                document.getElementById('resumeBtn').disabled = !paused;
                document.getElementById('stopBtn').disabled = !playing;
            }}
            
            function playText() {{
                if (synth.speaking) {{
                    synth.cancel();
                }}
                
                utterance = new SpeechSynthesisUtterance(textToSpeak);
                
                if (selectedVoice) {{
                    utterance.voice = selectedVoice;
                }}
                
                utterance.rate = rate;
                utterance.pitch = 1;
                utterance.volume = 1;
                
                utterance.onstart = function() {{
                    updateStatus('🔊 Playing...');
                    updateButtons(true, false);
                }};
                
                utterance.onend = function() {{
                    updateStatus('✅ Finished');
                    updateButtons(false, false);
                }};
                
                utterance.onerror = function(event) {{
                    updateStatus('❌ Error: ' + event.error);
                    updateButtons(false, false);
                }};
                
                utterance.onpause = function() {{
                    updateStatus('⏸️ Paused');
                    updateButtons(true, true);
                }};
                
                utterance.onresume = function() {{
                    updateStatus('🔊 Playing...');
                    updateButtons(true, false);
                }};
                
                synth.speak(utterance);
            }}
            
            function pauseSpeech() {{
                if (synth.speaking && !synth.paused) {{
                    synth.pause();
                }}
            }}
            
            function resumeSpeech() {{
                if (synth.paused) {{
                    synth.resume();
                }}
            }}
            
            function stopSpeech() {{
                if (synth.speaking) {{
                    synth.cancel();
                    updateStatus('⏹️ Stopped');
                    updateButtons(false, false);
                }}
            }}
            
            // Initialize button states
            updateButtons(false, false);
        </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=200, scrolling=False)


def simple_audio_player(text: str):
    """Simple audio player with basic controls"""
    st.markdown("### 🔊 Audio Player")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ Play", key="play_audio", use_container_width=True):
            text_to_speech_player(text, key="tts_main")
    
    with col2:
        st.info("🎧 Click Play to hear the content")
    
    with col3:
        st.caption("Uses browser's built-in TTS")
