"""New meeting page for processing audio and generating minutes."""

import streamlit as st
import logging
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

from src.config import Config
from src.schemas import Meeting, TranscriptSegment, ExportOptions
from src.transcription import get_transcriber
from src.diarization import merge_transcript_and_diarization
from src.summarizer import MeetingSummarizer
from src.storage import MeetingStorage
from src.export import DocumentExporter

logger = logging.getLogger(__name__)


def show():
    """Show new meeting page."""
    st.title("🎤 New Meeting")

    # Initialize session state
    if 'processing_stage' not in st.session_state:
        st.session_state.processing_stage = 'upload'

    if 'transcript_segments' not in st.session_state:
        st.session_state.transcript_segments = []

    if 'meeting_minutes' not in st.session_state:
        st.session_state.meeting_minutes = None

    if 'temp_audio_path' not in st.session_state:
        st.session_state.temp_audio_path = None

    # Progress indicator
    stages = ['upload', 'transcribe', 'minutes', 'export']
    current_idx = stages.index(st.session_state.processing_stage)

    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]

    for idx, (col, stage) in enumerate(zip(cols, ['Upload', 'Transcribe', 'Minutes', 'Export'])):
        with col:
            if idx < current_idx:
                st.success(f"✅ {stage}")
            elif idx == current_idx:
                st.info(f"⏳ {stage}")
            else:
                st.text(f"⚪ {stage}")

    st.markdown("---")

    # Route to appropriate stage
    if st.session_state.processing_stage == 'upload':
        show_upload_stage()
    elif st.session_state.processing_stage == 'transcribe':
        show_transcribe_stage()
    elif st.session_state.processing_stage == 'minutes':
        show_minutes_stage()
    elif st.session_state.processing_stage == 'export':
        show_export_stage()


def show_upload_stage():
    """Show audio upload stage."""
    st.subheader("Step 1: Upload Audio")

    # Meeting info
    col1, col2 = st.columns(2)

    with col1:
        meeting_title = st.text_input(
            "Meeting Title*",
            placeholder="Weekly Team Sync - Jan 2026"
        )

    with col2:
        meeting_date = st.date_input("Meeting Date", datetime.now())

    participants = st.text_input(
        "Participants (comma-separated)",
        placeholder="John Smith, Jane Doe, Bob Wilson"
    )

    agenda = st.text_area(
        "Agenda (optional)",
        placeholder="1. Project updates\n2. Budget review\n3. Next steps"
    )

    st.markdown("---")

    # Audio upload
    st.markdown("### Upload Audio File")

    supported_formats = ", ".join(Config.SUPPORTED_FORMATS)
    st.info(f"📁 Supported formats: {supported_formats}")
    st.info(f"📊 Max file size: {Config.MAX_FILE_SIZE_MB} MB")

    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['mp3', 'wav', 'm4a', 'flac', 'ogg']
    )

    if uploaded_file:
        # Show file info
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.success(f"✅ File uploaded: {uploaded_file.name} ({file_size_mb:.1f} MB)")

        # Validate file size
        if uploaded_file.size > Config.MAX_FILE_SIZE_BYTES:
            st.error(f"❌ File too large. Maximum size is {Config.MAX_FILE_SIZE_MB} MB")
            return

        # Save to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name

        st.session_state.temp_audio_path = temp_path

        # Process button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🎯 Process Audio", type="primary", use_container_width=True):
                if not meeting_title:
                    st.error("❌ Please enter a meeting title")
                else:
                    # Store meeting metadata
                    st.session_state.meeting_metadata = {
                        'title': meeting_title,
                        'date': datetime.combine(meeting_date, datetime.now().time()),
                        'participants': [p.strip() for p in participants.split(',')] if participants else [],
                        'agenda': agenda if agenda else None
                    }

                    # Move to transcription stage
                    st.session_state.processing_stage = 'transcribe'
                    st.rerun()


def show_transcribe_stage():
    """Show transcription stage."""
    st.subheader("Step 2: Transcription")

    if not st.session_state.temp_audio_path:
        st.error("❌ No audio file found")
        return

    # Transcription options
    with st.expander("⚙️ Transcription Options"):
        use_fast = st.checkbox("Use faster-whisper (recommended)", value=True)
        language = st.selectbox("Language", ["en", "es", "fr", "de", "it", "pt"], index=0)
        num_speakers = st.number_input(
            "Number of speakers (optional, helps with diarization)",
            min_value=1,
            max_value=10,
            value=2
        )

    # Start transcription
    if 'transcription_done' not in st.session_state:
        st.session_state.transcription_done = False

    if not st.session_state.transcription_done:
        with st.spinner("🎤 Transcribing audio... This may take a few minutes."):
            try:
                # Transcribe
                transcriber = get_transcriber(use_fast=use_fast)
                segments, metadata = transcriber.transcribe(
                    st.session_state.temp_audio_path,
                    language=language
                )

                st.success(f"✅ Transcription complete: {len(segments)} segments")

                # Apply diarization
                with st.spinner("🎭 Identifying speakers..."):
                    segments = merge_transcript_and_diarization(
                        segments,
                        st.session_state.temp_audio_path,
                        num_speakers=num_speakers
                    )

                st.session_state.transcript_segments = segments
                st.session_state.transcription_done = True
                st.rerun()

            except Exception as e:
                logger.error(f"Transcription failed: {e}")
                st.error(f"❌ Transcription failed: {str(e)}")
                return

    # Show transcript preview
    if st.session_state.transcript_segments:
        st.markdown("### 📄 Transcript Preview")

        with st.expander("View Full Transcript", expanded=True):
            # Display in a nice format
            current_speaker = None
            for seg in st.session_state.transcript_segments[:20]:  # Show first 20 segments
                if seg.speaker != current_speaker:
                    st.markdown(f"**{seg.speaker}**")
                    current_speaker = seg.speaker

                timestamp = format_timestamp(seg.start)
                confidence_emoji = "🟢" if seg.confidence > 0.8 else "🟡" if seg.confidence > 0.5 else "🔴"
                st.text(f"[{timestamp}] {confidence_emoji} {seg.text}")

            if len(st.session_state.transcript_segments) > 20:
                st.info(f"... and {len(st.session_state.transcript_segments) - 20} more segments")

        # Edit speaker names
        st.markdown("### ✏️ Edit Speaker Names (Optional)")

        unique_speakers = list(set(seg.speaker for seg in st.session_state.transcript_segments))

        speaker_mapping = {}
        cols = st.columns(min(len(unique_speakers), 3))

        for idx, speaker in enumerate(unique_speakers):
            col = cols[idx % len(cols)]
            with col:
                new_name = st.text_input(
                    f"Rename {speaker}",
                    value=speaker,
                    key=f"speaker_{speaker}"
                )
                speaker_mapping[speaker] = new_name

        # Apply speaker name changes
        if st.button("Apply Speaker Names"):
            for seg in st.session_state.transcript_segments:
                seg.speaker = speaker_mapping.get(seg.speaker, seg.speaker)
            st.success("✅ Speaker names updated")

        # Next button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Generate Minutes →", type="primary", use_container_width=True):
                st.session_state.processing_stage = 'minutes'
                st.rerun()


def show_minutes_stage():
    """Show minutes generation and editing stage."""
    st.subheader("Step 3: Meeting Minutes")

    if not st.session_state.transcript_segments:
        st.error("❌ No transcript available")
        return

    # Generate minutes if not already done
    if not st.session_state.meeting_minutes:
        with st.spinner("🤖 Generating meeting minutes... This may take a minute."):
            try:
                summarizer = MeetingSummarizer()
                minutes = summarizer.summarize(
                    st.session_state.transcript_segments,
                    meeting_context=st.session_state.meeting_metadata.get('agenda')
                )

                st.session_state.meeting_minutes = minutes
                st.success("✅ Minutes generated successfully")

            except Exception as e:
                logger.error(f"Summarization failed: {e}")
                st.error(f"❌ Failed to generate minutes: {str(e)}")
                st.info("💡 You can still proceed and manually enter the minutes")

                # Create empty minutes
                from src.schemas import MeetingMinutes
                st.session_state.meeting_minutes = MeetingMinutes()

    # Display and edit minutes
    minutes = st.session_state.meeting_minutes

    # Executive Summary
    st.markdown("### 📋 Executive Summary")
    summary_text = st.text_area(
        "Summary (one bullet per line)",
        value="\n".join(minutes.summary) if minutes.summary else "",
        height=150,
        key="summary_edit"
    )
    minutes.summary = [line.strip() for line in summary_text.split("\n") if line.strip()]

    # Key Decisions
    st.markdown("### ✅ Key Decisions")
    decisions_text = st.text_area(
        "Decisions (one per line)",
        value="\n".join(minutes.decisions) if minutes.decisions else "",
        height=100,
        key="decisions_edit"
    )
    minutes.decisions = [line.strip() for line in decisions_text.split("\n") if line.strip()]

    # Action Items
    st.markdown("### 🎯 Action Items")

    if minutes.action_items:
        for idx, item in enumerate(minutes.action_items):
            col1, col2, col3, col4 = st.columns([2, 4, 2, 1])

            with col1:
                item.owner = st.text_input("Owner", value=item.owner, key=f"owner_{idx}")

            with col2:
                item.task = st.text_input("Task", value=item.task, key=f"task_{idx}")

            with col3:
                item.due_date = st.text_input("Due Date", value=item.due_date or "", key=f"due_{idx}")

            with col4:
                if st.button("🗑️", key=f"delete_{idx}"):
                    minutes.action_items.pop(idx)
                    st.rerun()

    # Add new action item
    if st.button("➕ Add Action Item"):
        from src.schemas import ActionItem
        minutes.action_items.append(ActionItem(owner="", task="", due_date=None))
        st.rerun()

    # Risks and Open Questions
    st.markdown("### ⚠️ Risks & Open Questions")
    risks_text = st.text_area(
        "Risks (one per line)",
        value="\n".join(minutes.risks) if minutes.risks else "",
        height=100,
        key="risks_edit"
    )
    minutes.risks = [line.strip() for line in risks_text.split("\n") if line.strip()]

    # Update session state
    st.session_state.meeting_minutes = minutes

    st.markdown("---")

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("← Back to Transcript"):
            st.session_state.processing_stage = 'transcribe'
            st.rerun()

    with col3:
        if st.button("Save & Export →", type="primary", use_container_width=True):
            # Save meeting to database
            meeting = Meeting(
                **st.session_state.meeting_metadata,
                transcript=st.session_state.transcript_segments,
                minutes=st.session_state.meeting_minutes,
                audio_path=st.session_state.temp_audio_path
            )

            storage = MeetingStorage()
            meeting_id = storage.save_meeting(meeting)

            st.session_state.saved_meeting_id = meeting_id
            st.session_state.processing_stage = 'export'
            st.rerun()


def show_export_stage():
    """Show export stage."""
    st.subheader("Step 4: Export")

    st.success("✅ Meeting saved successfully!")

    # Export options
    st.markdown("### 📄 Export Options")

    col1, col2 = st.columns(2)

    with col1:
        include_transcript = st.checkbox("Include full transcript", value=True)
        include_timestamps = st.checkbox("Include timestamps", value=True)

    with col2:
        include_speaker_labels = st.checkbox("Include speaker labels", value=True)

    # Export buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 Export to DOCX", type="primary", use_container_width=True):
            with st.spinner("Generating DOCX..."):
                try:
                    meeting = Meeting(
                        **st.session_state.meeting_metadata,
                        transcript=st.session_state.transcript_segments,
                        minutes=st.session_state.meeting_minutes
                    )

                    options = ExportOptions(
                        include_transcript=include_transcript,
                        include_timestamps=include_timestamps,
                        include_speaker_labels=include_speaker_labels,
                        format="docx"
                    )

                    exporter = DocumentExporter()
                    file_path = exporter.export(meeting, options)

                    with open(file_path, 'rb') as f:
                        st.download_button(
                            "⬇️ Download DOCX",
                            f,
                            file_name=file_path.name,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )

                    st.success(f"✅ DOCX generated: {file_path.name}")

                except Exception as e:
                    st.error(f"❌ Export failed: {str(e)}")

    with col2:
        if st.button("📑 Export to PDF", type="primary", use_container_width=True):
            with st.spinner("Generating PDF..."):
                try:
                    meeting = Meeting(
                        **st.session_state.meeting_metadata,
                        transcript=st.session_state.transcript_segments,
                        minutes=st.session_state.meeting_minutes
                    )

                    options = ExportOptions(
                        include_transcript=include_transcript,
                        include_timestamps=include_timestamps,
                        include_speaker_labels=include_speaker_labels,
                        format="pdf"
                    )

                    exporter = DocumentExporter()
                    file_path = exporter.export(meeting, options)

                    with open(file_path, 'rb') as f:
                        st.download_button(
                            "⬇️ Download PDF",
                            f,
                            file_name=file_path.name,
                            mime="application/pdf"
                        )

                    st.success(f"✅ PDF generated: {file_path.name}")

                except Exception as e:
                    st.error(f"❌ Export failed: {str(e)}")

    st.markdown("---")

    # Start new meeting
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🎤 Process Another Meeting", use_container_width=True):
            # Reset session state
            st.session_state.processing_stage = 'upload'
            st.session_state.transcript_segments = []
            st.session_state.meeting_minutes = None
            st.session_state.temp_audio_path = None
            st.session_state.transcription_done = False
            st.rerun()


def format_timestamp(seconds: float) -> str:
    """Format seconds as MM:SS."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"
