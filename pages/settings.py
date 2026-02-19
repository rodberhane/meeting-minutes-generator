"""Settings page."""

import streamlit as st
from src.config import Config


def show():
    """Show settings page."""
    st.title("⚙️ Settings")

    st.markdown("### 🔒 Privacy Settings")

    privacy_mode = st.checkbox(
        "Privacy Mode",
        value=Config.PRIVACY_MODE,
        help="Process everything locally without cloud APIs"
    )

    if privacy_mode:
        st.success("✅ All processing is done locally. No data leaves your machine.")
    else:
        st.warning("⚠️ Privacy mode disabled. Cloud LLM APIs may be used.")

    st.markdown("---")

    st.markdown("### 🎤 Transcription Settings")

    whisper_model = st.selectbox(
        "Whisper Model",
        options=["tiny", "base", "small", "medium", "large"],
        index=["tiny", "base", "small", "medium", "large"].index(Config.WHISPER_MODEL),
        help="Larger models are more accurate but slower"
    )

    st.info(f"""
    **Model Sizes:**
    - Tiny: Fastest, least accurate (~75MB)
    - Base: Good balance (~150MB) - Recommended
    - Small: More accurate (~500MB)
    - Medium: Very accurate (~1.5GB)
    - Large: Most accurate (~3GB)
    """)

    st.markdown("---")

    st.markdown("### 🤖 LLM Settings")

    llm_provider = st.selectbox(
        "LLM Provider",
        options=["openai", "anthropic"],
        index=0 if Config.LLM_PROVIDER == "openai" else 1,
        help="Provider for summarization and action item extraction"
    )

    if llm_provider == "openai":
        api_key = st.text_input(
            "OpenAI API Key",
            value=Config.OPENAI_API_KEY or "",
            type="password",
            help="Required for summarization unless using local LLM"
        )

        if api_key:
            st.success("✅ API Key configured")
        else:
            st.warning("⚠️ API Key not set. Summarization will not work.")

    elif llm_provider == "anthropic":
        api_key = st.text_input(
            "Anthropic API Key",
            value=Config.ANTHROPIC_API_KEY or "",
            type="password",
            help="Required for summarization"
        )

        if api_key:
            st.success("✅ API Key configured")
        else:
            st.warning("⚠️ API Key not set. Summarization will not work.")

    st.markdown("---")

    st.markdown("### 💾 Storage Settings")

    st.info(f"**Database Location:** `{Config.STORAGE_PATH}`")

    audio_retention = st.slider(
        "Audio Retention (days)",
        min_value=0,
        max_value=30,
        value=Config.AUDIO_RETENTION_DAYS,
        help="How long to keep audio files (0 = delete immediately)"
    )

    st.markdown("---")

    st.markdown("### 📊 System Information")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Whisper Model:** {Config.WHISPER_MODEL}")
        st.markdown(f"**LLM Provider:** {Config.LLM_PROVIDER}")
        st.markdown(f"**Privacy Mode:** {'Enabled ✅' if Config.PRIVACY_MODE else 'Disabled ⚠️'}")

    with col2:
        st.markdown(f"**Max File Size:** {Config.MAX_FILE_SIZE_MB} MB")
        st.markdown(f"**Audio Retention:** {Config.AUDIO_RETENTION_DAYS} days")
        st.markdown(f"**Device:** {Config.WHISPER_DEVICE}")

    st.markdown("---")

    st.info("""
    **Note:** Settings are loaded from the `.env` file. To make permanent changes,
    edit the `.env` file in the project root directory.
    """)

    st.markdown("---")

    st.markdown("### 📚 Documentation")

    st.markdown("""
    - **README.md**: Full documentation
    - **Requirements**: Python 3.10+
    - **Installation**: `pip install -r requirements.txt`
    - **Run**: `streamlit run app.py`
    """)

    st.markdown("---")

    st.markdown("### 🔗 Resources")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("[📖 Documentation](https://github.com/)")

    with col2:
        st.markdown("[🐛 Report Issue](https://github.com/)")

    with col3:
        st.markdown("[⭐ Star on GitHub](https://github.com/)")
