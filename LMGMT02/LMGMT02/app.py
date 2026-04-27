import os
import ast
import sys
import json
import time
from io import BytesIO
from typing import List, Dict, Any, Tuple

import streamlit as st
from groq import Groq
from gtts import gTTS
import graphviz


# =========================
# Configuration & constants
# =========================

# In production: keep in a config module or env
DEFAULT_MODEL_NAME = "llama-3.3-70b-versatile"
TEXT_TEMPERATURE = 0.6
CODE_TEMPERATURE = 0.4
QUIZ_TEMPERATURE = 0.7
ROADMAP_TEMPERATURE = 0.5
VISUAL_TEMPERATURE = 0.8

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2.0

# Difficulty / depth options
DIFFICULTY_LEVELS = ["Beginner", "Intermediate", "Advanced"]
DEPTH_LEVELS = ["Overview", "Standard", "Deep Dive"]


# =========================
# Prompt templates
# =========================

TEXT_PROMPT_TEMPLATE = """
You are an expert ML educator and curriculum designer.

Topic: "{topic}"
Learner level: {difficulty}
Depth: {depth}

Generate highly structured, pedagogically-sound learning content with the following sections in clear markdown:

1. Structured explanation (intro + main explanation)
2. Key concepts (bullet list)
3. Real-world applications (bullet list)
4. Common mistakes and misconceptions (bullet list)
5. Summary (short, high-signal)
6. Week-wise learning roadmap (4–6 weeks)
   - For each week: objectives, topics, practice ideas
7. Learning objectives (concise bullet list)

Output as a single markdown document with clear headings (##, ###) and bullet lists.
Keep explanations precise but not overly verbose.
"""

ROADMAP_PROMPT_TEMPLATE = """
You are an expert ML curriculum planner.

Topic: "{topic}"
Learner level: {difficulty}
Depth: {depth}

Design a structured, 4–6 week learning roadmap as JSON with this exact schema:

{{
  "weeks": [
    {{
      "id": "week1",
      "title": "Short week title",
      "summary": "1-2 sentence overview",
      "concepts": [
        "core concept 1",
        "core concept 2"
      ],
      "dependencies": [
        "optional previous concept ids, e.g., 'basics', 'linear_algebra'"
      ],
      "milestones": [
        "Milestone 1",
        "Milestone 2"
      ]
    }},
    ...
  ],
  "concept_dependencies": [
    ["Concept A", "Concept B"],  // A should be learned before B
    ["Concept B", "Concept C"]
  ]
}}

Constraints:
- Return ONLY valid JSON, no markdown, no comments.
- Use short but descriptive titles and concept names.
"""

CODE_PROMPT_TEMPLATE = """
You are a senior ML engineer and instructor.

Topic: "{topic}"
Learner level: {difficulty}
Depth: {depth}

Generate a **working Python code example** that demonstrates the core idea of the topic.
Requirements:
- Include imports.
- Use clean, modern Python.
- Add concise but meaningful comments that explain the *why* and *intuition*, not obvious operations.
- Include a simple runnable example (e.g., small dataset, quick run).
- Keep external dependencies minimal and standard for ML / data science.

Output ONLY the Python code, no explanation or markdown fences.
"""

QUIZ_PROMPT_TEMPLATE = """
You are an expert ML instructor creating a diagnostic quiz.

Topic: "{topic}"
Learner level: {difficulty}
Depth: {depth}

Goal: Create an adaptive quiz based on the topic.
Generate between 5 and 10 questions as **JSON** with the following schema:

{{
  "questions": [
    {{
      "id": "q1",
      "type": "mcq" | "true_false" | "concept",
      "question": "Question text...",
      "options": ["A", "B", "C", "D"],  // for mcq, empty list for true_false/concept
      "answer": "Correct answer text or value",
      "explanation": "Short pedagogical explanation",
      "difficulty": "easy" | "medium" | "hard"
    }},
    ...
  ]
}}

Guidelines:
- Mix of MCQ, True/False, and conceptual short-answer questions.
- Focus on core understanding, not trivia.
- Difficulty tags reflect cognitive load.
- Return ONLY valid JSON, no markdown.
"""

VISUAL_PROMPT_TEMPLATE = """
You are a data visualization and instructional design expert.

Topic: "{topic}"
Learner level: {difficulty}
Depth: {depth}

Generate a concise, high-quality prompt for an AI image generator that will create:
- A clean roadmap diagram
- A concept hierarchy
- A flow-like layout of the learning path

Constraints:
- Corporate / conference slide aesthetic
- Light background, professional color palette
- Clear labels for weeks and concepts
- Easy to read in a presentation

Return ONLY the plain-text prompt (1–3 sentences).
"""


# =========================
# AI client & helper layer
# =========================

def init_groq() -> Groq:
    """Configure Groq API from environment or Streamlit secrets, gracefully handling missing secrets.toml."""
    api_key = None

    # Try environment first so it works even if no secrets.toml exists
    env_key = os.getenv("GROQ_API_KEY")
    if env_key:
        api_key = env_key
    else:
        # Try Streamlit secrets, but handle missing secrets.toml gracefully
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            api_key = None

    if not api_key:
        st.error(
            "⚠️ Groq API key not found.\n\n"
            "Set it either as an environment variable GROQ_API_KEY\n"
            "or in a .streamlit/secrets.toml file.\n\n"
            "Get your free key at: https://console.groq.com"
        )
        st.stop()

    return Groq(api_key=api_key)


@st.cache_data(show_spinner=False)
def call_groq(_client: Groq, prompt: str, temperature: float = 0.6) -> str:
    """
    Call Groq with basic retry logic.
    Cached by prompt+temperature to reduce cost and latency.
    """
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            message = _client.chat.completions.create(
                model=DEFAULT_MODEL_NAME,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=4096
            )
            return message.choices[0].message.content
        except Exception as e:
            last_error = e
            time.sleep(RETRY_BACKOFF_SECONDS * attempt)
    raise RuntimeError(f"Groq call failed after {MAX_RETRIES} attempts: {last_error}")


# =========================
# Generator functions
# =========================

def generate_text(_client: Groq, topic: str, difficulty: str, depth: str) -> str:
    prompt = TEXT_PROMPT_TEMPLATE.format(
        topic=topic,
        difficulty=difficulty,
        depth=depth
    )
    return call_groq(_client, prompt, temperature=TEXT_TEMPERATURE)


def generate_roadmap(_client: Groq, topic: str, difficulty: str, depth: str) -> Dict[str, Any]:
    prompt = ROADMAP_PROMPT_TEMPLATE.format(
        topic=topic,
        difficulty=difficulty,
        depth=depth
    )
    raw = call_groq(_client, prompt, temperature=ROADMAP_TEMPERATURE)
    try:
        roadmap = json.loads(raw)
        assert "weeks" in roadmap
        return roadmap
    except Exception:
        # Fallback: create a minimal synthetic roadmap if parsing fails
        st.warning("Roadmap JSON could not be parsed. Using a fallback roadmap.")
        weeks = []
        for i in range(1, 5):
            weeks.append({
                "id": f"week{i}",
                "title": f"Week {i}: {topic} basics",
                "summary": f"Progress on {topic}, week {i}.",
                "concepts": [f"{topic} concept {i}a", f"{topic} concept {i}b"],
                "dependencies": [],
                "milestones": [f"Milestone {i} for {topic}"]
            })
        return {"weeks": weeks, "concept_dependencies": []}


def generate_code(_client: Groq, topic: str, difficulty: str, depth: str) -> str:
    prompt = CODE_PROMPT_TEMPLATE.format(
        topic=topic,
        difficulty=difficulty,
        depth=depth
    )
    code = call_groq(_client, prompt, temperature=CODE_TEMPERATURE)
    return code.strip()


def generate_quiz(_client: Groq, topic: str, difficulty: str, depth: str) -> Dict[str, Any]:
    prompt = QUIZ_PROMPT_TEMPLATE.format(
        topic=topic,
        difficulty=difficulty,
        depth=depth
    )
    raw = call_groq(_client, prompt, temperature=QUIZ_TEMPERATURE)
    try:
        quiz = json.loads(raw)
        assert "questions" in quiz
        return quiz
    except Exception:
        st.warning("Quiz JSON could not be parsed. Generating a simple fallback quiz.")
        return {
            "questions": [
                {
                    "id": "q1",
                    "type": "true_false",
                    "question": f"{topic} is relevant to modern machine learning applications.",
                    "options": [],
                    "answer": "True",
                    "explanation": f"{topic} is commonly used in modern ML workflows.",
                    "difficulty": "easy",
                }
            ]
        }


def generate_visual_prompt(_client: Groq, topic: str, difficulty: str, depth: str) -> str:
    prompt = VISUAL_PROMPT_TEMPLATE.format(
        topic=topic,
        difficulty=difficulty,
        depth=depth
    )
    return call_groq(_client, prompt, temperature=VISUAL_TEMPERATURE).strip()


# =========================
# Utility: dependency detection
# =========================

def extract_dependencies_from_code(code: str) -> List[str]:
    """
    Use AST to safely detect imported top-level modules and
    filter out standard library modules where possible.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                modules.add(root)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split(".")[0]
                modules.add(root)

    # Filter out standard library modules using Python's stdlib set if available
    stdlib = getattr(sys, "stdlib_module_names", set())
    filtered = [m for m in modules if m not in stdlib]
    return sorted(filtered)


def build_pip_install_commands(deps: List[str]) -> List[str]:
    """
    Turn a list of dependency module names into pip install commands.
    """
    if not deps:
        return []
    return [f"pip install {' '.join(deps)}"]


# =========================
# Utility: roadmap visualization
# =========================

def build_roadmap_graph(roadmap: Dict[str, Any]) -> graphviz.Digraph:
    """
    Build a Graphviz Digraph representing week progression and concept dependencies.
    (Original simpler layout.)
    """
    dot = graphviz.Digraph()
    # Layout left-to-right with a moderate canvas size
    dot.attr(rankdir="LR", bgcolor="white")
    dot.attr(graph_attr='size="8,5"')
    dot.attr(graph_attr='ratio="auto"')
    dot.attr("node", shape="box", style="rounded,filled", color="#1e88e5", fillcolor="#e3f2fd")

    weeks = roadmap.get("weeks", [])
    for week in weeks:
        label = f"{week['title']}\n{week.get('summary', '')}"
        dot.node(week["id"], label=label)

    # Sequential edges between weeks
    for i in range(len(weeks) - 1):
        dot.edge(weeks[i]["id"], weeks[i + 1]["id"], label="next", color="#90caf9")

    # Concept-level dependencies, if provided
    deps = roadmap.get("concept_dependencies", [])
    if deps:
        dot.attr("node", shape="ellipse", color="#43a047", fillcolor="#e8f5e9")
        for i, (src, dst) in enumerate(deps):
            src_id = f"c_{i}_src"
            dst_id = f"c_{i}_dst"
            dot.node(src_id, src)
            dot.node(dst_id, dst)
            dot.edge(src_id, dst_id, color="#a5d6a7")

    return dot


# =========================
# Utility: audio generation
# =========================

def generate_tts_audio(text: str, lang: str = "en") -> bytes:
    """
    Generate TTS audio (MP3) from text and return raw bytes.
    This is cached in session state keyed by the text hash.
    """
    tts = gTTS(text=text, lang=lang)
    buf = BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf.read()


# =========================
# Utility: quiz scoring
# =========================

def difficulty_weight(diff: str) -> float:
    mapping = {
        "easy": 1.0,
        "medium": 1.5,
        "hard": 2.0
    }
    return mapping.get(diff.lower(), 1.0)


def score_quiz(quiz: Dict[str, Any], answers: Dict[str, Any]) -> Tuple[float, float, List[Dict[str, Any]]]:
    """
    Adaptive quiz scoring:
    - Each question's weight depends on its difficulty.
    - Returns (score, max_score, per_question_feedback).
    """
    questions = quiz.get("questions", [])
    total_score = 0.0
    max_score = 0.0
    feedback = []

    for q in questions:
        qid = q["id"]
        correct_answer = str(q["answer"]).strip()
        user_answer = str(answers.get(qid, "")).strip()
        weight = difficulty_weight(q.get("difficulty", "easy"))
        max_score += weight

        is_correct = False
        if q["type"] == "true_false":
            is_correct = user_answer.lower() == correct_answer.lower()
        elif q["type"] == "mcq":
            is_correct = user_answer.strip() == correct_answer.strip()
        else:  # concept / short answer – fuzzy check (very simple)
            is_correct = correct_answer.lower() in user_answer.lower()

        if is_correct:
            total_score += weight

        feedback.append({
            "id": qid,
            "question": q["question"],
            "correct": is_correct,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "difficulty": q.get("difficulty", "easy"),
            "explanation": q.get("explanation", "")
        })

    return total_score, max_score, feedback


# =========================
# Session state helpers
# =========================

def init_session_state():
    defaults = {
        "topic": "",
        "difficulty": DIFFICULTY_LEVELS[0],
        "depth": DEPTH_LEVELS[1],
        "text_markdown": None,
        "roadmap": None,
        "code": None,
        "dependencies": None,
        "quiz": None,
        "quiz_answers": {},
        "quiz_scored": False,
        "quiz_feedback": None,
        "audio_text_hash": None,
        "audio_bytes": None,
        "visual_prompt": None,
        "gen_text": True,
        "gen_roadmap": True,
        "gen_code": True,
        "gen_quiz": True,
        "gen_audio": True,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def current_profile_signature() -> str:
    """Unique signature for topic+difficulty+depth to avoid unnecessary regeneration."""
    return f"{st.session_state.topic}::{st.session_state.difficulty}::{st.session_state.depth}"


# =========================
# UI components & layout
# =========================

def render_header():
    st.markdown(
        """
        <h2 style="text-align:center; margin-bottom:0.2rem;">
            LearnSphere – Generative AI-Powered ML Learning System
        </h2>
        <p style="text-align:center; color:gray;">
            Multi-modal, adaptive ML learning assistant powered by Gemini
        </p>
        """,
        unsafe_allow_html=True
    )


def render_sidebar(_client: Groq):
    st.sidebar.markdown("### 🎯 Learning Setup")
    
    # Example topics for dropdown menu
    example_topics = [
        "Convolutional Neural Networks",
        "Transformers",
        "Natural Language Processing",
        "Deep Reinforcement Learning",
        "Computer Vision",
        "Neural Network Optimization",
        "Generative Adversarial Networks",
        "Graph Neural Networks",
        "Attention Mechanisms",
        "Transfer Learning",
        "Custom Topic"
    ]
    
    # Topic search/dropdown
    # If the stored topic matches an example, show it. If a custom topic was previously entered,
    # pre-select "Custom Topic" so the user input is preserved and reused.
    if st.session_state.topic and st.session_state.topic in example_topics:
        default_idx = example_topics.index(st.session_state.topic)
    elif st.session_state.topic and st.session_state.topic not in example_topics:
        default_idx = example_topics.index("Custom Topic")
    else:
        default_idx = 0

    selected_topic = st.sidebar.selectbox(
        "Select a topic to learn",
        example_topics,
        index=default_idx
    )
    
    # Allow custom topic input
    if selected_topic == "Custom Topic":
        topic = st.sidebar.text_input("Enter your custom topic", value=st.session_state.topic or "")
    else:
        topic = selected_topic
    
    difficulty = st.sidebar.selectbox("Learner level", DIFFICULTY_LEVELS, index=DIFFICULTY_LEVELS.index(st.session_state.difficulty))
    depth = st.sidebar.selectbox("Learning depth", DEPTH_LEVELS, index=DEPTH_LEVELS.index(st.session_state.depth))

    st.session_state.topic = topic.strip()
    st.session_state.difficulty = difficulty
    st.session_state.depth = depth

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📚 Content Types to Generate")
    
    # Content type checkboxes
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.session_state.gen_text = st.checkbox("📖 Text", value=True)
        st.session_state.gen_roadmap = st.checkbox("🧠 Roadmap", value=True)
        st.session_state.gen_code = st.checkbox("💻 Code", value=True)
    with col2:
        st.session_state.gen_quiz = st.checkbox("❓ Quiz", value=True)
        st.session_state.gen_audio = st.checkbox("🔊 Audio", value=True)

    st.sidebar.markdown("---")
    # Generate all selected content at once
    if st.sidebar.button("Generate Selected Content", key="generate_selected"):
        if not st.session_state.topic:
            st.sidebar.warning("Please enter a topic first.")
        else:
            topic = st.session_state.topic
            # Text (and roadmap produced within text generation)
            if st.session_state.gen_text:
                with st.spinner("Generating text..."):
                    st.session_state.text_markdown = generate_text(
                        _client,
                        topic,
                        st.session_state.difficulty,
                        st.session_state.depth,
                    )
            # Roadmap (if not already produced by text generation)
            if st.session_state.gen_roadmap and st.session_state.roadmap is None:
                with st.spinner("Generating roadmap..."):
                    st.session_state.roadmap = generate_roadmap(
                        _client,
                        topic,
                        st.session_state.difficulty,
                        st.session_state.depth,
                    )
            # Code
            if st.session_state.gen_code:
                with st.spinner("Generating code..."):
                    st.session_state.code = generate_code(
                        _client,
                        topic,
                        st.session_state.difficulty,
                        st.session_state.depth,
                    )
                    st.session_state.dependencies = extract_dependencies_from_code(st.session_state.code)
            # Quiz
            if st.session_state.gen_quiz:
                with st.spinner("Generating quiz..."):
                    st.session_state.quiz = generate_quiz(
                        _client,
                        topic,
                        st.session_state.difficulty,
                        st.session_state.depth,
                    )
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_scored = False
                    st.session_state.quiz_feedback = None
            # Audio (requires text)
            if st.session_state.gen_audio:
                if not st.session_state.text_markdown:
                    # generate text first if missing
                    with st.spinner("Generating text for audio..."):
                        st.session_state.text_markdown = generate_text(
                            _client,
                            topic,
                            st.session_state.difficulty,
                            st.session_state.depth,
                        )
                with st.spinner("Generating audio..."):
                    st.session_state.audio_bytes = generate_tts_audio(st.session_state.text_markdown)

            st.sidebar.success("Selected content generated.")


def render_progress():
    steps = [
        ("Text", st.session_state.text_markdown is not None),
        ("Roadmap", st.session_state.roadmap is not None),
        ("Code", st.session_state.code is not None),
        ("Quiz", st.session_state.quiz is not None),
        ("Audio", st.session_state.audio_bytes is not None),
    ]
    completed = sum(1 for _, done in steps if done)
    total = len(steps)
    st.markdown("### 📌 Learning Journey Progress")
    st.progress(completed / total if total > 0 else 0.0)
    # Render each step as a centered badge in its own column for consistent spacing/alignment
    cols = st.columns(len(steps))
    for c, (name, done) in zip(cols, steps):
        icon = "✅" if done else "⬜"
        c.markdown(f"<div style='text-align:center; font-weight:600;'>{icon}<br>{name}</div>", unsafe_allow_html=True)


# =========================
# Tab: Text
# =========================

def render_text_tab(_client: Groq):
    st.markdown("### 📖 Text – Structured Explanation")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Generate Text", type="primary"):
            if not st.session_state.topic:
                st.warning("Please enter a topic in the sidebar.")
            else:
                with st.spinner("Generating structured explanation and roadmap with Groq..."):
                    st.session_state.text_markdown = generate_text(
                        _client,
                        st.session_state.topic,
                        st.session_state.difficulty,
                        st.session_state.depth
                    )
                    st.session_state.roadmap = generate_roadmap(
                        _client,
                        st.session_state.topic,
                        st.session_state.difficulty,
                        st.session_state.depth
                    )
                    # Reset dependent artifacts for new profile
                    st.session_state.code = None
                    st.session_state.dependencies = None
                    st.session_state.quiz = None
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_scored = False
                    st.session_state.quiz_feedback = None
                    st.session_state.audio_text_hash = None
                    st.session_state.audio_bytes = None
                    st.session_state.visual_prompt = None
                    st.success("Text and roadmap generated.")
    with col2:
        st.info("Use this as your primary learning narrative. Other tabs build on this content.")

    if st.session_state.text_markdown:
        st.markdown("---")
        st.markdown(st.session_state.text_markdown)
    else:
        st.info("Click **Generate Text** to create a structured explanation and roadmap for your topic.")


# =========================
# Tab: Path (Roadmap)
# =========================

def render_path_tab():
    st.markdown("### 🧠 Path – Learning Roadmap")
    st.markdown("---")

    if not st.session_state.roadmap:
        st.warning("No roadmap yet. Please generate text first in the 📖 Text tab.")
        return

    roadmap = st.session_state.roadmap
    weeks = roadmap.get("weeks", [])

    st.subheader("📅 Week-wise Breakdown")
    for week in weeks:
        with st.expander(f"{week['title']}"):
            st.write(week.get("summary", ""))
            st.markdown("**Key concepts**")
            st.markdown("- " + "\n- ".join(week.get("concepts", [])) if week.get("concepts") else "_None_")

            st.markdown("**Milestones**")
            milestones = week.get("milestones", [])
            if milestones:
                for m in milestones:
                    key = f"milestone_{week['id']}_{m}"
                    checked = st.checkbox(m, key=key)
            else:
                st.write("_No explicit milestones defined._")

    st.markdown("---")
    st.subheader("✅ Milestone Tracker")
    st.caption("Your progress is saved in this session.")

    # Simple aggregated progress
    milestone_keys = [k for k in st.session_state.keys() if k.startswith("milestone_")]
    if milestone_keys:
        done = sum(1 for k in milestone_keys if st.session_state.get(k))
        total = len(milestone_keys)
        st.progress(done / total if total > 0 else 0.0)
        st.write(f"Completed **{done} / {total}** milestones.")
    else:
        st.info("Milestones will appear after you expand weekly sections.")


# =========================
# Tab: Code
# =========================

def render_code_tab(_client: Groq):
    st.markdown("### 💻 Code – Working Implementation")
    st.markdown("---")

    if not st.session_state.text_markdown:
        st.warning("No context yet. Please generate text in the 📖 Text tab first.")
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Generate Code", type="primary"):
            with st.spinner("Generating Python implementation..."):
                code = generate_code(
                    _client,
                    st.session_state.topic,
                    st.session_state.difficulty,
                    st.session_state.depth
                )
                st.session_state.code = code
                deps = extract_dependencies_from_code(code)
                st.session_state.dependencies = deps
                st.success("Code generated.")
    with col2:
        st.info("Code is tailored to your topic, level, and depth.")

    if st.session_state.code:
        st.markdown("#### 🧩 Code")
        st.code(st.session_state.code, language="python")

        if st.session_state.dependencies:
            st.markdown("#### 📦 Detected Dependencies")
            cmds = build_pip_install_commands(st.session_state.dependencies)
            for cmd in cmds:
                st.code(cmd, language="bash")
        else:
            st.caption("No external dependencies detected or only standard library used.")

        st.markdown("#### ▶️ Execution Guide")
        st.markdown(
            """
            1. Create a new Python file (e.g., `learnsphere_example.py`) and paste the code.
            2. Install any dependencies shown above (if any).
            3. Run with `python learnsphere_example.py`.
            4. Experiment by changing hyperparameters or input data as suggested in comments.
            """
        )

        # Download button
        st.download_button(
            label="📥 Download Code",
            data=st.session_state.code,
            file_name="learnsphere_generated_code.py",
            mime="text/x-python",
        )
    else:
        st.info("Click **Generate Code** to create a runnable example for this topic.")


# =========================
# Tab: Audio
# =========================

def render_audio_tab():
    st.markdown("### 🔊 Audio – Listen to Explanation")
    st.markdown("---")

    if not st.session_state.text_markdown:
        st.warning("No explanation yet. Please generate text in the 📖 Text tab first.")
        return

    explanation_text = st.session_state.text_markdown
    text_hash = hash(explanation_text)

    if st.button("Generate / Refresh Audio", type="primary"):
        with st.spinner("Generating audio with gTTS..."):
            if st.session_state.audio_text_hash != text_hash:
                audio_bytes = generate_tts_audio(explanation_text)
                st.session_state.audio_bytes = audio_bytes
                st.session_state.audio_text_hash = text_hash
                st.success("Audio generated.")
            else:
                st.info("Existing audio is already in sync with the latest text. Reusing cached audio.")

    if st.session_state.audio_bytes:
        st.markdown("#### ▶️ Play Explanation")
        st.audio(st.session_state.audio_bytes, format="audio/mp3")
        st.caption("Audio is cached and only regenerated when the explanation text changes.")
    else:
        st.info("Click **Generate / Refresh Audio** to create an audio narration of the explanation.")


# =========================
# Tab: Visual
# =========================

def render_visual_tab(_client: Groq):
    st.markdown("### 🖼️ Visual – Roadmap & Concept Diagrams")
    st.markdown("---")

    if not st.session_state.roadmap:
        st.warning("No roadmap yet. Please generate text first in the 📖 Text tab.")
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Generate Visual Prompt", type="primary"):
            with st.spinner("Generating visual prompt with Groq..."):
                st.session_state.visual_prompt = generate_visual_prompt(
                    _client,
                    st.session_state.topic,
                    st.session_state.difficulty,
                    st.session_state.depth
                )
                st.success("Visual prompt generated.")

    with col2:
        st.info("Use the AI image prompt with any image generator to create polished slides.")

    st.markdown("#### 📊 Roadmap Flow (Graphviz)")
    graph = build_roadmap_graph(st.session_state.roadmap)
    st.graphviz_chart(graph)

    if st.session_state.visual_prompt:
        st.markdown("#### 🎨 AI Image Prompt")
        st.code(st.session_state.visual_prompt, language="text")
    else:
        st.info("Click **Generate Visual Prompt** to get an AI-ready image prompt for your roadmap.")


# =========================
# Tab: Quiz
# =========================

def render_quiz_tab(_client: Groq):
    st.markdown("### ❓ Quiz – Check Understanding")
    st.markdown("---")

    if not st.session_state.text_markdown:
        st.warning("No learning content yet. Please generate text in the 📖 Text tab first.")
        return

    if st.session_state.quiz is None:
        if st.button("Generate Quiz", type="primary"):
            with st.spinner("Generating quiz with Groq..."):
                st.session_state.quiz = generate_quiz(
                    _client,
                    st.session_state.topic,
                    st.session_state.difficulty,
                    st.session_state.depth
                )
                st.session_state.quiz_answers = {}
                st.session_state.quiz_scored = False
                st.session_state.quiz_feedback = None
                st.success("Quiz generated.")
        else:
            st.info("Click **Generate Quiz** to create a diagnostic test from your content.")
            return

    quiz = st.session_state.quiz
    questions = quiz.get("questions", [])

    if not questions:
        st.warning("No questions available.")
        return

    st.markdown("#### 📝 Questions")
    for q in questions:
        qid = q["id"]
        st.markdown(f"**{qid.upper()} – {q['question']}**")
        if q["type"] == "mcq":
            options = q.get("options", [])
            if not options:
                st.info("No options provided for this MCQ.")
                st.session_state.quiz_answers[qid] = ""
            else:
                key = f"quiz_{qid}"
                # Restore previous answer if present and valid; otherwise start with no selection
                prev = st.session_state.quiz_answers.get(qid)
                if prev in options:
                    default_index = options.index(prev)
                else:
                    default_index = None

                sel = st.radio(
                    "Choose one:",
                    options=options,
                    index=default_index,
                    key=key,
                )
                st.session_state.quiz_answers[qid] = sel or ""
        elif q["type"] == "true_false":
            options = ["True", "False"]
            key = f"quiz_{qid}"
            prev = st.session_state.quiz_answers.get(qid)
            if prev in options:
                default_index = options.index(prev)
            else:
                default_index = None

            sel = st.radio(
                "True / False:",
                options=options,
                index=default_index,
                key=key,
            )
            st.session_state.quiz_answers[qid] = sel or ""
        else:  # concept / short answer
            ans = st.text_area("Your answer:", key=f"quiz_{qid}")
            st.session_state.quiz_answers[qid] = ans

        st.markdown("---")

    if st.button("Score Quiz", type="primary"):
        total, max_score, feedback = score_quiz(quiz, st.session_state.quiz_answers)
        st.session_state.quiz_scored = True
        st.session_state.quiz_feedback = (total, max_score, feedback)

    if st.session_state.quiz_scored and st.session_state.quiz_feedback:
        total, max_score, feedback = st.session_state.quiz_feedback
        pct = (total / max_score * 100) if max_score > 0 else 0.0
        st.subheader(f"📊 Score: {total:.1f} / {max_score:.1f} ({pct:.0f}%)")

        if pct >= 80:
            st.success("Excellent! You have strong understanding. Consider moving to more advanced topics or projects.")
        elif pct >= 50:
            st.info("Good start. Review the explanations and focus on questions you missed.")
        else:
            st.warning("You may want to revisit the foundational sections and re-take the quiz after reviewing.")

        st.markdown("#### 🔍 Question-by-Question Feedback")
        for item in feedback:
            icon = "✅" if item["correct"] else "❌"
            st.markdown(f"**{icon} {item['id']} – {item['question']}**")
            st.write(f"- Your answer: `{item['user_answer']}`")
            st.write(f"- Correct answer: `{item['correct_answer']}`")
            st.write(f"- Difficulty: `{item['difficulty']}`")
            if item["explanation"]:
                st.write(f"- Explanation: {item['explanation']}")
            st.markdown("---")


# =========================
# Main app entrypoint
# =========================

def main():
    """
    Overall architecture notes (why this wins a hackathon):

    - Modular AI function layer with clear generators and prompt templates.
    - Safe, AST-based dependency detection for code tab.
    - Explicit per-tab temperatures and retry logic for Groq calls.
    - Session-state driven caching and regeneration avoidance across tabs.
    - Multi-modal UX (text, code, audio, visuals, quiz) around a single learning profile.
    - Powered by Groq's fast, free API for unlimited learning generation.
    """
    st.set_page_config(
        page_title="LearnSphere – ML Learning System",
        layout="wide"
    )

    init_session_state()
    client = init_groq()

    render_header()
    render_sidebar(client)
    render_progress()

    st.markdown("---")

    tab_text, tab_code, tab_audio, tab_visual, tab_path, tab_quiz = st.tabs(
        ["📖 Text", "💻 Code", "🔊 Audio", "🖼️ Visual", "🧠 Path", "❓ Quiz"]
    )

    with tab_text:
        render_text_tab(client)
    with tab_code:
        render_code_tab(client)
    with tab_audio:
        render_audio_tab()
    with tab_visual:
        render_visual_tab(client)
    with tab_path:
        render_path_tab()
    with tab_quiz:
        render_quiz_tab(client)


if __name__ == "__main__":
    main()