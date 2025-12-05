import streamlit as st
from dotenv import load_dotenv

from agents import build_llm, build_agents, answer_question

# Load .env (so OPENAI_API_KEY is available)
load_dotenv()

# --- Build LLM and agents on each rerun (lightweight enough) ---

llm = build_llm()
tutor_agent, research_agent = build_agents(llm)

# --- Initialize session state for chat + mode ---

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of (role, content)
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "mode" not in st.session_state:
    st.session_state.mode = "Regular answer"

# --- Callback for the Ask button ---

def handle_ask():
    question = st.session_state.user_input.strip()
    if not question:
        return

    # 1) store user message
    st.session_state.chat_history.append(("user", question))

    # 2) build a short text version of recent conversation
    history_lines = []
    for role, content in st.session_state.chat_history[-6:]:  # last 6 messages
        prefix = "User" if role == "user" else "Assistant"
        history_lines.append(f"{prefix}: {content}")
    history_text = "\n".join(history_lines)

    # 3) get current mode
    mode = st.session_state.mode  # "Regular answer", "Summary", "Explanation", "Quiz"

    # 4) call the multi-agent pipeline
    with st.spinner("Thinking..."):
        try:
            answer = answer_question(
                question,
                tutor_agent,
                research_agent,
                history=history_text,
                mode=mode,
            )
        except Exception as e:
            answer = f"Error while generating answer: {e}"

    # 5) store assistant answer
    st.session_state.chat_history.append(("assistant", answer))

    # 6) clear the input for the next turn
    st.session_state.user_input = ""


# --- UI ---

st.title("🪖 World War II History Tutor")
st.write("Ask anything about World War II (causes, events, key figures, consequences).")

# Mode selector
st.selectbox(
    "Response type:",
    ["Regular answer", "Summary", "Explanation", "Quiz"],
    key="mode",
)

# Show chat history
for role, content in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"**You:** {content}")
    else:
        st.markdown(f"**Assistant:** {content}")

# Input at the bottom
st.text_input("Your question:", key="user_input")

col1, col2 = st.columns([1, 4])
with col1:
    st.button("Ask", on_click=handle_ask)
