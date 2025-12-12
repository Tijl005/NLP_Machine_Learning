import streamlit as st
from dotenv import load_dotenv
from agents import build_llm, build_agents, answer_question

# NIEUWE IMPORTS voor document- en beeldverwerking
from tools.vector_tool import add_document_to_knowledge_base
from tools.vision_tool import analyze_image

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
    
    /* Adjust chat messages for better contrast if needed */
    </style>
""", unsafe_allow_html=True)

# Initialize LLM and Agents
# Using cache_resource to avoid reloading the LLM on every rerun if possible
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

    # --- NIEUW: FILE UPLOAD SECTIE ---
    st.subheader("📂 Upload Files")
    
    # 1. Document Upload (RAG met Docling)
    uploaded_doc = st.file_uploader(
        "Add Knowledge Doc (PDF, DOCX, TXT)", 
        type=['pdf', 'docx', 'txt'],
        key="doc_uploader"
    )
    
    if uploaded_doc is not None:
        if st.button("📄 Process Document", use_container_width=True):
            with st.spinner("Reading document with Docling..."):
                # We roepen de functie aan die we in vector_tool.py hebben gemaakt
                success, message = add_document_to_knowledge_base(uploaded_doc, uploaded_doc.name)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    st.markdown("---")

    # 2. Image Upload (Vision met GPT-4o)

    st.subheader("🖼️ Upload Images")

    uploaded_img = st.file_uploader(
        "Identify Image (PNG, JPG)", 
        type=['png', 'jpg', 'jpeg'],
        key="img_uploader"
    )
    
    if uploaded_img is not None:
        st.image(uploaded_img, caption="Preview", use_column_width=True)
        
        if st.button("👁️ Analyze Image", use_container_width=True):
            with st.spinner("Analyzing image..."):
                # We roepen de functie aan die we in vision_tool.py hebben gemaakt
                description = analyze_image(uploaded_img)
                
                st.info(f"**Analysis:** {description}")
                
                # Belangrijk: Voeg de analyse toe aan de chatgeschiedenis
                # Zodat de agents weten waarover gepraat wordt in vervolgvragen
                st.session_state.chat_history.append(
                    ("assistant", f"*[System Note: I analyzed an uploaded image. Description: {description}]*", "Vision Analysis")
                )
                
                # Herlaad de pagina om de geschiedenis te updaten
                st.rerun()

    st.divider()
    
    if st.button("🗑️ Clear Chat", type="primary", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
    
    st.markdown("---")
    st.caption("Powered by CrewAI, Docling & GPT-4o")

# --- Main Interface ---

st.title("🎖️ World War II Tutor")

# Display Chat History
if not st.session_state.chat_history:
    st.info("👋 Welcome! Ask any question about World War II, or upload a document/image in the sidebar.")

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
                    # Filter out system notes if needed, but usually helpful for context
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