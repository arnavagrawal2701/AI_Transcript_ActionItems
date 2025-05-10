SUMMARY_PROMPT = """
You are an AI assistant. Your job is to read a meeting transcript and generate a professional summary of the discussion.

Transcript:
{transcript}

Summary:
"""

ACTION_ITEMS_PROMPT = """
You are an AI assistant. Extract clear and actionable items from the following meeting transcript.

For each person mentioned, group their tasks under their name, even if their name appears with a role (e.g., "Sara", "Sara (Design team)", or "Sara from Marketing" should be grouped under "Sara").

Use the format:
Person Name:
- [ ] Task 1: Deadline
- [ ] Task 2: Deadline

Only include clear tasks with deadlines or timeframes if mentioned.

Transcript:
{transcript}

Action Items:
"""

