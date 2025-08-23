

import streamlit as st
import requests

# --- Page & API Configuration ---
st.set_page_config(page_title="AI Legal Debate ⚖️", page_icon="🏛️", layout="wide")
API_URL = "http://127.0.0.1:8000"

# --- Style ---
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .sidebar-header { font-size: 1.5rem; font-weight: bold; color: #1E90FF; }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
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
    try:
        payload = {"case": case_description} if case_description else {}
        response = requests.post(f"{API_URL}/start", json=payload)
        response.raise_for_status()
        data = response.json()
        
        st.session_state.session_id = data.get("session_id")
        st.session_state.case_details = data
        st.session_state.messages = []
        st.session_state.app_stage = 'debate'
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend: {e}. Is the server running?")

def run_turn(user_message, filters=None):
    if not st.session_state.session_id:
        st.error("Session not started.")
        return

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
        
        if data.get("rag_lawyer_output"):
            st.session_state.messages.append({"role": "RAG Lawyer", "content": data["rag_lawyer_output"]["argument"]})
        if data.get("chaos_lawyer_output"):
            st.session_state.messages.append({"role": "Chaos Lawyer", "content": data["chaos_lawyer_output"]["argument"]})
        
        st.session_state.latest_context = data.get("rag_context", "No context retrieved.")

        if data.get("is_finished"):
            st.session_state.case_details["winner"] = data.get("winner")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error processing turn: {e}")

# --- UI Rendering ---

## Sidebar
with st.sidebar:
    st.markdown("<div class='sidebar-header'>RAG Search Filters</div>", unsafe_allow_html=True)
    st.write("Apply filters before submitting your message.")
    
    filters = {}
    jurisdiction = st.selectbox("Jurisdiction", ["Any"] + st.session_state.available_filters["jurisdiction"])
    case_type = st.selectbox("Case Type", ["Any"] + st.session_state.available_filters["case_type"])
    year = st.number_input("Year of Judgment (Optional)", min_value=1800, max_value=2025, value=None)

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
    if st.button("▶️ Start New Debate", use_container_width=True, type="primary"):
        st.session_state.app_stage = 'case_selection'
        st.rerun()

elif st.session_state.app_stage == 'case_selection':
    st.subheader("How would you like to begin the case?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎲 Generate a Random Case", use_container_width=True):
            start_debate()
            st.rerun()
    with col2:
        custom_case = st.text_input("Or, enter your own case description:", placeholder="e.g., A cat sues its owner")
        if custom_case:
            if st.button("Submit Custom Case", use_container_width=True, type="primary"):
                start_debate(custom_case)
                st.rerun()

elif st.session_state.app_stage == 'debate':
    st.subheader(f"📜 Case: {st.session_state.case_details.get('case', 'N/A')}")
    st.caption(f"RAG Lawyer: **{st.session_state.case_details.get('rag_role', 'N/A').upper()}** | Chaos Lawyer: **{st.session_state.case_details.get('chaos_role', 'N/A').upper()}**")
    st.divider()

    # Display chat history
    for message in st.session_state.messages:
        role = message["role"]
        avatar = "🧑‍⚖️" if role == "Judge" else ("🤖" if role == "RAG Lawyer" else "👹")
        with st.chat_message(role, avatar=avatar):
            st.markdown(message["content"])

    # Interaction Logic
    if st.session_state.case_details.get("winner"):
        winner = st.session_state.case_details["winner"]
        winner_name = "RAG Lawyer" if "rag" in winner else "Chaos Lawyer"
        st.success(f"**The verdict is in! {winner_name} wins the debate!**")
        st.balloons()
    else:
        st.divider()
        # Use a form to group the input and buttons, which helps with Streamlit's execution flow
        with st.form(key="input_form", clear_on_submit=True):
            prompt = st.text_input("Your question or verdict...", placeholder="Enter a verdict (e.g., prosecution wins) or a question.")
            
            submit_button = st.form_submit_button(label="Submit Message / Verdict")
            continue_button = st.form_submit_button(label="Continue Debate")

            if submit_button and prompt:
                active_filters = filters if any(filters.values()) else None
                run_turn(prompt, active_filters)
                st.rerun()
            
            if continue_button:
                active_filters = filters if any(filters.values()) else None
                run_turn("Continue the debate.", active_filters)
                st.rerun()