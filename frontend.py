

import streamlit as st
import requests
import time
import json


st.set_page_config(
    page_title="AI Legal Debate ⚖️",
    page_icon="🏛️",
    layout="wide"
)


API_URL = "http://127.0.0.1:8000"


st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .lawyer-name {
        font-weight: bold;
        font-size: 1.1rem;
    }
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1E90FF;
    }
</style>
""", unsafe_allow_html=True)


if 'app_stage' not in st.session_state:
    st.session_state.app_stage = 'start'
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'case_details' not in st.session_state:
    st.session_state.case_details = {}
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'latest_context' not in st.session_state:
    st.session_state.latest_context = "No precedent retrieved yet."
if 'available_filters' not in st.session_state:
    
    st.session_state.available_filters = {
        "jurisdiction": ["Supreme Court of India", "High Court of Delhi", "California Family Court", "US Federal Court"],
        "case_type": ["Service Law", "Divorce", "Defamation", "Property Dispute"],
    }

# --- API Helper Functions ---
def start_debate(case_description=None):
    """Calls the /start endpoint to initialize a new debate."""
    try:
        payload = {"case": case_description} if case_description else {}
        response = requests.post(f"{API_URL}/start", json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Store session info
        st.session_state.session_id = data.get("session_id")
        st.session_state.case_details = data
        st.session_state.messages = [] # Clear previous messages
        st.session_state.app_stage = 'debate'
        st.rerun()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend: {e}. Is the server running?")

def run_turn(user_message, filters=None):
    """Calls the /run endpoint to process one turn of the debate."""
    if not st.session_state.session_id:
        st.error("Session not started. Please start a new debate.")
        return

    # Add Judge's message to chat history
    st.session_state.messages.append({"role": "Judge", "content": user_message})

    payload = {
        "session_id": st.session_state.session_id,
        "user_message": user_message,
        "filters": filters or {}
    }

    try:
        with st.spinner("The lawyers are preparing their arguments..."):
            response = requests.post(f"{API_URL}/run", json=payload)
            response.raise_for_status()
            data = response.json()
        
        # Update chat with new arguments
        if data.get("rag_lawyer_output"):
            st.session_state.messages.append({"role": "RAG Lawyer", "content": data["rag_lawyer_output"]["argument"]})
        if data.get("chaos_lawyer_output"):
            st.session_state.messages.append({"role": "Chaos Lawyer", "content": data["chaos_lawyer_output"]["argument"]})
        
        # Update sidebar context
        st.session_state.latest_context = data.get("rag_context", "No context retrieved.")

        # Check for winner
        if data.get("is_finished"):
            st.session_state.case_details["winner"] = data.get("winner")
            time.sleep(1) # Dramatic pause
            st.balloons()
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error processing turn: {e}")

# --- UI Rendering ---

## Sidebar
with st.sidebar:
    st.markdown("<div class='sidebar-header'>RAG Search Filters</div>", unsafe_allow_html=True)
    st.write("Apply filters before submitting your message.")
    
    # Create filter widgets
    filters = {}
    jurisdiction = st.selectbox(
        "Jurisdiction", 
        options=["Any"] + st.session_state.available_filters["jurisdiction"],
        index=0
    )
    case_type = st.selectbox(
        "Case Type", 
        options=["Any"] + st.session_state.available_filters["case_type"],
        index=0
    )
    year = st.number_input("Year of Judgment (Optional)", min_value=1800, max_value=2025, value=None, placeholder="e.g., 1975")

    if jurisdiction != "Any": filters["jurisdiction"] = jurisdiction
    if case_type != "Any": filters["case_type"] = case_type
    if year: filters["year"] = year
    
    st.divider()
    
    st.markdown("<div class='sidebar-header'>Retrieved Precedent</div>", unsafe_allow_html=True)
    with st.expander("Show Latest Retrieved Context", expanded=True):
        st.info(st.session_state.latest_context)
        
    if st.button("↩️ Start New Debate"):
        st.session_state.app_stage = 'start'
        st.rerun()

## Main App UI
if st.session_state.app_stage == 'start':
    st.markdown("<div class='main-header'>AI Legal Debate Arena 🏛️</div>", unsafe_allow_html=True)
    st.write("")
    if st.button("▶️ Start New Debate", use_container_width=True, type="primary"):
        st.session_state.app_stage = 'case_selection'
        st.rerun()

elif st.session_state.app_stage == 'case_selection':
    st.subheader("How would you like to begin the case?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎲 Generate a Random Case", use_container_width=True):
            start_debate()
    with col2:
        custom_case = st.text_input("Or, enter your own case description:", placeholder="e.g., A cat sues its owner for emotional distress")
        if custom_case and st.button("Submit Custom Case", use_container_width=True, type="primary"):
            start_debate(custom_case)

elif st.session_state.app_stage == 'debate':
    st.subheader(f"📜 Case: {st.session_state.case_details.get('case', 'N/A')}")
    st.caption(f"RAG Lawyer: **{st.session_state.case_details.get('rag_lawyer_role', 'N/A')}** | Chaos Lawyer: **{st.session_state.case_details.get('chaos_lawyer_role', 'N/A')}**")
    st.divider()

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle winner display
    if st.session_state.case_details.get("winner"):
        winner = st.session_state.case_details["winner"]
        winner_name = "RAG Lawyer" if "rag" in winner else "Chaos Lawyer"
        st.success(f"**The verdict is in! {winner_name} wins the debate!**")
        st.balloons()
    else:
        # Otherwise, show the interaction buttons.
        st.divider()
        prompt = st.text_input("Your question or verdict...", placeholder="Enter a specific verdict (e.g., prosecution wins) or a question.")
        
        col1, col2 = st.columns([3, 2])
        with col1:
            if st.button("Submit Message / Verdict", type="primary", disabled=(not prompt)):
                active_filters = filters if any(filters.values()) else None
                run_turn(prompt, active_filters)
        with col2:
            if st.button("Continue Debate"):
                active_filters = filters if any(filters.values()) else None
                # Send a generic message to prompt the next turn
                run_turn("Continue the debate.", active_filters)
