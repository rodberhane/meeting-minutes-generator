"""Main Streamlit application for Meeting Minutes Generator."""

import streamlit as st
import logging
from pathlib import Path

from src.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Meeting Minutes Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #0066cc;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .feature-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    .status-good {
        color: #00cc00;
        font-weight: bold;
    }
    .status-bad {
        color: #cc0000;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point."""

    # Sidebar navigation
    st.sidebar.title("📝 Meeting Minutes")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Home", "🎤 New Meeting", "📋 History", "⚙️ Settings"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### System Status")

    # Display configuration status
    status_msg = Config.get_status_message()
    st.sidebar.text(status_msg)

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### Quick Start
    1. Upload audio or record
    2. Process transcript
    3. Review & edit minutes
    4. Export to DOCX/PDF
    """)

    # Route to selected page
    if page == "🏠 Home":
        show_home()
    elif page == "🎤 New Meeting":
        show_new_meeting()
    elif page == "📋 History":
        show_history()
    elif page == "⚙️ Settings":
        show_settings()


def show_home():
    """Show home page."""
    st.markdown('<div class="main-header">📝 Meeting Minutes Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Automatically generate professional meeting minutes from audio recordings</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Features
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🎯 Features")
        st.markdown("""
        - **Audio Transcription**: Whisper AI
        - **Speaker Detection**: Automatic diarization
        - **Smart Summarization**: LLM-powered
        - **Action Items**: Auto-extraction
        - **Export**: DOCX & PDF formats
        """)

    with col2:
        st.markdown("### 🔒 Privacy")
        st.markdown("""
        - **Local Processing**: All data stays on your machine
        - **No Cloud Upload**: Privacy mode enabled
        - **Audio Deletion**: Configurable retention
        - **Secure Storage**: Local SQLite database
        """)

    with col3:
        st.markdown("### 🚀 Quick Start")
        st.markdown("""
        1. Click **New Meeting** in sidebar
        2. Upload audio file (MP3/WAV/M4A)
        3. Wait for transcription
        4. Review and edit minutes
        5. Export to DOCX or PDF
        """)

    st.markdown("---")

    # Get statistics
    from src.storage import MeetingStorage
    storage = MeetingStorage()
    stats = storage.get_statistics()

    st.markdown("### 📊 Statistics")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Meetings", stats.get("total_meetings", 0))

    with col2:
        recent = stats.get("most_recent_date")
        recent_str = recent.strftime("%Y-%m-%d") if recent else "N/A"
        st.metric("Most Recent", recent_str)

    with col3:
        st.metric("Database", "Active ✅")

    st.markdown("---")

    # Get started button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🎤 Create New Meeting", type="primary", use_container_width=True):
            st.session_state.page = "new"
            st.rerun()


def show_new_meeting():
    """Show new meeting page."""
    from pages import new_meeting
    new_meeting.show()


def show_history():
    """Show meeting history page."""
    from pages import history
    history.show()


def show_settings():
    """Show settings page."""
    from pages import settings
    settings.show()


if __name__ == "__main__":
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'home'

    if 'current_meeting' not in st.session_state:
        st.session_state.current_meeting = None

    main()
