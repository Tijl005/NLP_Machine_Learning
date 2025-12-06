import streamlit as st
from dotenv import load_dotenv
from agents import build_llm, build_agents, answer_question

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="WW2 History Tutor",
    page_icon="🎖️",
    layout="centered"
)

# Custom CSS for Dark Theme and Modern UI
st.markdown("""
    <style>
    /* Force Dark Theme style */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Clean up the sidebar */
    section[data-testid="stSidebar"] {
        background-color: #262730;
    }
    
    /* Enhance Markdown headers */
    h1, h2, h3 {
        color: #E0E0E0 !important;
    }
    
    /* Adjust chat messages for better contrast if needed, 
       though native st.chat_message handles this well usually. */
       
    </style>
""", unsafe_allow_html=True)

# Initialize LLM and Agents
# Using cache_resource to avoid reloading the LLM on every rerun if possible,
# strictly speaking the original code rebuilt them every time. 
# We'll keep the rebuilding logic simple for now as per original design.
llm = build_llm()
tutor_agent, research_agent, quiz_agent = build_agents(llm)

# Session State Initialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # List of tuples: (role, content, mode)

if "mode" not in st.session_state:
    st.session_state.mode = "Regular answer"

# --- Sidebar Controls ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    st.session_state.mode = st.radio(
        "Response Mode:",
        ["Regular answer", "Summary", "Explanation", "Quiz"],
        help="Choose how the AI should respond to your questions."
    )
    
    st.divider()
    
    if st.button("🗑️ Clear Chat", type="primary", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
    
    st.markdown("---")
    st.caption("Powered by CrewAI & GPT-4")

# --- Main Interface ---

st.title("🎖️ World War II Tutor")

# Display Chat History
# If usage is new, show a welcome message (but keep it simple)
if not st.session_state.chat_history:
    st.info("👋 Welcome! Ask any question about World War II to get started.")

for role, content, mode_used in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(content)
        if role == "assistant" and mode_used != "Regular answer":
            st.caption(f"Mode: {mode_used}")

# Chat Input
if prompt := st.chat_input("Ask a question (e.g., 'What happened on D-Day?')..."):
    # 1. Display User Message
    st.chat_message("user").markdown(prompt)
    
    # 2. Add to history
    current_mode = st.session_state.mode
    st.session_state.chat_history.append(("user", prompt, current_mode))
    
    # 3. Generate Answer
    with st.chat_message("assistant"):
        with st.spinner("Analyzing history books..."):
            try:
                # Construct history string for context
                # Take last few turns to maintain context for follow-up questions
                history_lines = []
                for r, c, m in st.session_state.chat_history[-6:]:
                    prefix = "User" if r == "user" else "Assistant"
                    history_lines.append(f"{prefix}: {c}")
                history_text = "\n".join(history_lines)
                
                response = answer_question(
                    prompt,
                    tutor_agent,
                    research_agent,
                    quiz_agent,
                    history=history_text,
                    mode=current_mode,
                )
                
                st.markdown(response)
                if current_mode != "Regular answer":
                    st.caption(f"Mode: {current_mode}")
                
                # 4. Add Assistant response to history
                st.session_state.chat_history.append(("assistant", response, current_mode))
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
