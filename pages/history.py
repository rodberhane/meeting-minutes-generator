"""Meeting history page."""

import streamlit as st
import logging
from src.storage import MeetingStorage
from src.export import DocumentExporter
from src.schemas import ExportOptions

logger = logging.getLogger(__name__)


def show():
    """Show meeting history page."""
    st.title("📋 Meeting History")

    storage = MeetingStorage()

    # Search bar
    search_query = st.text_input("🔍 Search meetings", placeholder="Search by title or participant...")

    # Get meetings
    meetings = storage.list_meetings(limit=50, search=search_query if search_query else None)

    if not meetings:
        st.info("📭 No meetings found. Create your first meeting!")
        return

    st.markdown(f"### Found {len(meetings)} meeting(s)")

    # Display meetings
    for meeting in meetings:
        with st.expander(f"📅 {meeting.title} - {meeting.date.strftime('%Y-%m-%d %H:%M')}"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**Date:** {meeting.date.strftime('%B %d, %Y %H:%M')}")
                st.markdown(f"**Participants:** {', '.join(meeting.participants) if meeting.participants else 'N/A'}")

                if meeting.agenda:
                    st.markdown(f"**Agenda:** {meeting.agenda[:100]}...")

                # Show summary if available
                if meeting.minutes and meeting.minutes.summary:
                    st.markdown("**Summary:**")
                    for bullet in meeting.minutes.summary[:3]:
                        st.markdown(f"- {bullet}")
                    if len(meeting.minutes.summary) > 3:
                        st.markdown(f"  ... and {len(meeting.minutes.summary) - 3} more")

                # Show action items count
                if meeting.minutes and meeting.minutes.action_items:
                    st.markdown(f"**Action Items:** {len(meeting.minutes.action_items)}")

            with col2:
                # Export buttons
                if st.button("📄 Export DOCX", key=f"docx_{meeting.id}"):
                    try:
                        options = ExportOptions(
                            include_transcript=True,
                            include_timestamps=True,
                            include_speaker_labels=True,
                            format="docx"
                        )
                        exporter = DocumentExporter()
                        file_path = exporter.export(meeting, options)

                        with open(file_path, 'rb') as f:
                            st.download_button(
                                "⬇️ Download",
                                f,
                                file_name=file_path.name,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"download_docx_{meeting.id}"
                            )
                    except Exception as e:
                        st.error(f"Export failed: {str(e)}")

                if st.button("📑 Export PDF", key=f"pdf_{meeting.id}"):
                    try:
                        options = ExportOptions(
                            include_transcript=True,
                            include_timestamps=True,
                            include_speaker_labels=True,
                            format="pdf"
                        )
                        exporter = DocumentExporter()
                        file_path = exporter.export(meeting, options)

                        with open(file_path, 'rb') as f:
                            st.download_button(
                                "⬇️ Download",
                                f,
                                file_name=file_path.name,
                                mime="application/pdf",
                                key=f"download_pdf_{meeting.id}"
                            )
                    except Exception as e:
                        st.error(f"Export failed: {str(e)}")

                # Delete button
                if st.button("🗑️ Delete", key=f"delete_{meeting.id}"):
                    if storage.delete_meeting(meeting.id):
                        st.success("Meeting deleted")
                        st.rerun()
                    else:
                        st.error("Failed to delete meeting")
