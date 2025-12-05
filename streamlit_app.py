import streamlit as st
from dotenv import load_dotenv

from agents import build_llm, build_agents, answer_question

# Page configuration
st.set_page_config(
    page_title="WW2 History Tutor",
    page_icon="🎖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .user-message {
        background-color: #e3f2fd;
        padding: 0.75rem 1rem;
        border-radius: 10px 10px 0 0;
        margin: 1rem 0 0 0;
        border-left: 4px solid #2196F3;
        font-weight: 600;
        color: #1976d2;
    }
    .assistant-message {
        background-color: #e8f5e9;
        padding: 0.75rem 1rem;
        border-radius: 10px 10px 0 0;
        margin: 1rem 0 0 0;
        border-left: 4px solid #4CAF50;
        font-weight: 600;
        color: #2e7d32;
    }
    .message-content {
        background-color: #fafafa;
        padding: 1rem;
        border-radius: 0 0 10px 10px;
        margin: 0 0 0.5rem 0;
        border-left: 4px solid #e0e0e0;
        color: #212121;
        line-height: 1.6;
    }
    .mode-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .mode-regular { background-color: #e3f2fd; color: #1976d2; }
    .mode-summary { background-color: #fff3e0; color: #f57c00; }
    .mode-explanation { background-color: #f3e5f5; color: #7b1fa2; }
    .mode-quiz { background-color: #e8f5e9; color: #388e3c; }
    </style>
""", unsafe_allow_html=True)

# Load .env (so OPENAI_API_KEY is available)
load_dotenv()

# --- Build LLM and agents on each rerun (lightweight enough) ---

llm = build_llm()
tutor_agent, research_agent, quiz_agent = build_agents(llm)

# --- Initialize session state for chat + mode ---

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of (role, content, mode)
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "mode" not in st.session_state:
    st.session_state.mode = "Regular answer"

# --- Callback for the Ask button ---

def handle_ask():
    question = st.session_state.user_input.strip()
    if not question:
        return

    # 1) store user message with current mode
    current_mode = st.session_state.mode
    st.session_state.chat_history.append(("user", question, current_mode))

    # 2) build a short text version of recent conversation
    history_lines = []
    for item in st.session_state.chat_history[-6:]:  # last 6 messages
        role, content = item[0], item[1]
        prefix = "User" if role == "user" else "Assistant"
        history_lines.append(f"{prefix}: {content}")
    history_text = "\n".join(history_lines)

    # 3) call the multi-agent pipeline
    with st.spinner("🤔 Researching and preparing your answer..."):
        try:
            answer = answer_question(
                question,
                tutor_agent,
                research_agent,
                quiz_agent,
                history=history_text,
                mode=current_mode,
            )
        except Exception as e:
            answer = f"❌ Error while generating answer: {e}"

    # 4) store assistant answer with mode
    st.session_state.chat_history.append(("assistant", answer, current_mode))

    # 5) clear the input for the next turn
    st.session_state.user_input = ""


def clear_chat():
    st.session_state.chat_history = []


def get_mode_badge(mode):
    mode_classes = {
        "Regular answer": "mode-regular",
        "Summary": "mode-summary",
        "Explanation": "mode-explanation",
        "Quiz": "mode-quiz",
    }
    mode_icons = {
        "Regular answer": "💬",
        "Summary": "📝",
        "Explanation": "📖",
        "Quiz": "❓",
    }
    css_class = mode_classes.get(mode, "mode-regular")
    icon = mode_icons.get(mode, "💬")
    return f'<span class="mode-badge {css_class}">{icon} {mode}</span>'


# --- Sidebar ---

with st.sidebar:
    st.header("⚙️ Settings")
    
    st.markdown("### Response Mode")
    mode = st.radio(
        "Choose how the assistant should respond:",
        ["Regular answer", "Summary", "Explanation", "Quiz"],
        key="mode",
        help="Select the type of response you want to receive"
    )
    
    st.markdown("---")
    
    st.markdown("### About")
    st.info("""
    **🎖️ World War II History Tutor**
    
    This AI-powered tutor helps you learn about World War II using:
    - 📚 Local history documents
    - 🌐 Online research (SerpAPI)
    - 🤖 Multi-agent system (CrewAI)
    
    **Response Modes:**
    - 💬 **Regular**: Direct answers
    - 📝 **Summary**: Key points
    - 📖 **Explanation**: Detailed info
    - ❓ **Quiz**: Test your knowledge
    """)
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        clear_chat()
        st.rerun()
    
    st.markdown("---")
    st.caption("💡 Tip: Try asking about D-Day, Pearl Harbor, or the causes of WW2!")


# --- Main Content ---

# Header
col1, col2 = st.columns([1, 6])
with col1:
    st.markdown("# 🎖️")
with col2:
    st.title("World War II History Tutor")
    st.markdown("*Ask anything about WW2: causes, battles, key figures, and consequences*")

st.markdown("---")

# Chat container
chat_container = st.container()

with chat_container:
    if len(st.session_state.chat_history) == 0:
        st.markdown("""
        <div style='text-align: center; padding: 3rem; color: #666;'>
            <h3>👋 Welcome to your WW2 History Tutor!</h3>
            <p>Start by asking a question about World War II.</p>
            <p><strong>Example questions:</strong></p>
            <ul style='list-style: none; padding: 0;'>
                <li>🎯 What were the main causes of World War II?</li>
                <li>⚔️ Tell me about the Battle of Stalingrad</li>
                <li>🗓️ What happened on D-Day?</li>
                <li>🌍 Which countries were part of the Axis powers?</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        for item in st.session_state.chat_history:
            role, content = item[0], item[1]
            mode_used = item[2] if len(item) > 2 else "Regular answer"
            
            if role == "user":
                st.markdown("""<div class='user-message'>👤 You:</div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class='message-content'>{content}</div>""", unsafe_allow_html=True)
            else:
                badge = get_mode_badge(mode_used)
                st.markdown(f"""<div class='assistant-message'>🤖 Assistant {badge}</div>""", unsafe_allow_html=True)
                st.markdown(f"""<div class='message-content'>{content}</div>""", unsafe_allow_html=True)

st.markdown("---")

# Input section at the bottom
st.markdown("### 💭 Ask your question")
col1, col2 = st.columns([5, 1])

with col1:
    st.text_input(
        "Type your question here...",
        key="user_input",
        placeholder="e.g., What was the significance of the Battle of Midway?",
        label_visibility="collapsed",
        on_change=None,
    )

with col2:
    st.button("🚀 Ask", on_click=handle_ask, use_container_width=True, type="primary")
