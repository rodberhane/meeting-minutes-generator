#!/usr/bin/env python3
"""Generate demo meeting data for testing and demonstrations."""

from datetime import datetime, timedelta
from src.schemas import Meeting, TranscriptSegment, MeetingMinutes, ActionItem
from src.storage import MeetingStorage


def create_demo_meeting_1():
    """Create first demo meeting: Weekly Team Sync."""
    transcript = [
        TranscriptSegment(start=0.0, end=5.0, text="Good morning everyone, let's start our weekly sync.", speaker="John Smith"),
        TranscriptSegment(start=5.0, end=12.0, text="Thanks John. I have an update on the Q1 project. We've completed 80% of the deliverables.", speaker="Sarah Johnson"),
        TranscriptSegment(start=12.0, end=18.0, text="That's excellent progress. What about the remaining 20%?", speaker="John Smith"),
        TranscriptSegment(start=18.0, end=25.0, text="We're on track to complete everything by end of month. However, we need approval for the extra budget.", speaker="Sarah Johnson"),
        TranscriptSegment(start=25.0, end=30.0, text="Let's discuss the budget. Bob, can you prepare a proposal?", speaker="John Smith"),
        TranscriptSegment(start=30.0, end=35.0, text="Sure, I'll have it ready by Friday.", speaker="Bob Wilson"),
        TranscriptSegment(start=35.0, end=42.0, text="Great. Any blockers or concerns from the team?", speaker="John Smith"),
        TranscriptSegment(start=42.0, end=48.0, text="We might need additional resources in the final week.", speaker="Sarah Johnson"),
        TranscriptSegment(start=48.0, end=53.0, text="Noted. Let's plan for that in the budget proposal.", speaker="John Smith"),
    ]

    minutes = MeetingMinutes(
        summary=[
            "Q1 project is 80% complete and on track",
            "Additional budget required for project completion",
            "Team coordination is working well",
            "Resource planning needed for final week"
        ],
        decisions=[
            "Approved proceeding with current project timeline",
            "Budget proposal to be submitted by end of week"
        ],
        action_items=[
            ActionItem(owner="Bob Wilson", task="Prepare budget proposal", due_date="2026-02-21", confidence=0.95),
            ActionItem(owner="Sarah Johnson", task="Complete remaining Q1 deliverables", due_date="2026-02-28", confidence=0.90),
            ActionItem(owner="John Smith", task="Review resource allocation for final week", due_date="2026-02-22", confidence=0.85)
        ],
        risks=[
            "Budget approval may take longer than expected",
            "Resource constraints in final week of month"
        ]
    )

    return Meeting(
        title="Weekly Team Sync - Feb 2026",
        date=datetime(2026, 2, 18, 10, 0),
        participants=["John Smith", "Sarah Johnson", "Bob Wilson"],
        agenda="1. Q1 project update\n2. Budget discussion\n3. Next steps",
        transcript=transcript,
        minutes=minutes
    )


def create_demo_meeting_2():
    """Create second demo meeting: Sprint Planning."""
    transcript = [
        TranscriptSegment(start=0.0, end=6.0, text="Let's kick off sprint planning. We have 15 story points committed.", speaker="Alice Chen"),
        TranscriptSegment(start=6.0, end=13.0, text="I'd like to take the authentication feature. That's 5 points.", speaker="David Lee"),
        TranscriptSegment(start=13.0, end=19.0, text="Sounds good. I'll handle the API integration, that's 8 points.", speaker="Maria Garcia"),
        TranscriptSegment(start=19.0, end=25.0, text="That leaves 2 points for the bug fixes. I can take those.", speaker="Tom Brown"),
        TranscriptSegment(start=25.0, end=32.0, text="Perfect. Any dependencies or blockers we should be aware of?", speaker="Alice Chen"),
        TranscriptSegment(start=32.0, end=38.0, text="The API integration depends on the infrastructure team. I'll coordinate with them.", speaker="Maria Garcia"),
    ]

    minutes = MeetingMinutes(
        summary=[
            "Sprint planning completed with 15 story points committed",
            "Team members selected their respective tasks",
            "Dependencies identified with infrastructure team"
        ],
        decisions=[
            "Sprint scope finalized at 15 points",
            "Maria to coordinate with infrastructure team"
        ],
        action_items=[
            ActionItem(owner="David Lee", task="Implement authentication feature", due_date="2026-02-25", confidence=0.90),
            ActionItem(owner="Maria Garcia", task="Complete API integration", due_date="2026-02-26", confidence=0.85),
            ActionItem(owner="Tom Brown", task="Fix high-priority bugs", due_date="2026-02-24", confidence=0.95),
            ActionItem(owner="Maria Garcia", task="Coordinate with infrastructure team", due_date="2026-02-20", confidence=0.90)
        ],
        risks=[
            "API integration may be blocked by infrastructure team availability"
        ]
    )

    return Meeting(
        title="Sprint Planning - Sprint 12",
        date=datetime(2026, 2, 17, 14, 0),
        participants=["Alice Chen", "David Lee", "Maria Garcia", "Tom Brown"],
        agenda="1. Review sprint capacity\n2. Task assignment\n3. Identify dependencies",
        transcript=transcript,
        minutes=minutes
    )


def create_demo_meeting_3():
    """Create third demo meeting: Client Kickoff."""
    transcript = [
        TranscriptSegment(start=0.0, end=7.0, text="Welcome everyone to the project kickoff. Let's start with introductions.", speaker="Project Manager"),
        TranscriptSegment(start=7.0, end=14.0, text="Hi, I'm the client stakeholder. We're excited about this project.", speaker="Client"),
        TranscriptSegment(start=14.0, end=21.0, text="Great to meet you. Let's review the timeline. We have 12 weeks for delivery.", speaker="Project Manager"),
        TranscriptSegment(start=21.0, end=28.0, text="That timeline works for us. What about the budget?", speaker="Client"),
        TranscriptSegment(start=28.0, end=35.0, text="The budget is $250K as discussed. We'll provide weekly progress reports.", speaker="Project Manager"),
    ]

    minutes = MeetingMinutes(
        summary=[
            "Project kickoff completed successfully",
            "12-week timeline confirmed",
            "$250K budget approved",
            "Weekly reporting cadence established"
        ],
        decisions=[
            "Project timeline set at 12 weeks",
            "Weekly progress reports to be delivered",
            "Budget approved at $250K"
        ],
        action_items=[
            ActionItem(owner="Project Manager", task="Send contract for signature", due_date="2026-02-20", confidence=0.95),
            ActionItem(owner="Project Manager", task="Schedule weekly status meetings", due_date="2026-02-19", confidence=0.90),
            ActionItem(owner="Client", task="Provide access to development environment", due_date="2026-02-22", confidence=0.80)
        ],
        risks=[
            "Environment access may take longer than expected"
        ]
    )

    return Meeting(
        title="Client Project Kickoff Meeting",
        date=datetime(2026, 2, 16, 11, 0),
        participants=["Project Manager", "Client", "Tech Lead", "Account Manager"],
        agenda="1. Introductions\n2. Project scope review\n3. Timeline and budget\n4. Communication plan",
        transcript=transcript,
        minutes=minutes
    )


def main():
    """Generate all demo meetings."""
    print("🎯 Generating demo meeting data...")

    storage = MeetingStorage()

    # Create meetings
    meetings = [
        create_demo_meeting_1(),
        create_demo_meeting_2(),
        create_demo_meeting_3()
    ]

    # Save to database
    for meeting in meetings:
        meeting_id = storage.save_meeting(meeting)
        print(f"✅ Created meeting: {meeting.title} (ID: {meeting_id})")

    # Get statistics
    stats = storage.get_statistics()
    print(f"\n📊 Database Statistics:")
    print(f"   Total meetings: {stats['total_meetings']}")
    print(f"   Database: {stats['database_path']}")

    print("\n✨ Demo data generation complete!")
    print("\n🚀 Run 'streamlit run app.py' to view the meetings")


if __name__ == "__main__":
    main()
