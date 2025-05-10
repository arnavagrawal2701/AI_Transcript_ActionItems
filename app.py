import streamlit as st
import re
from main import generate_response
from prompts import SUMMARY_PROMPT, ACTION_ITEMS_PROMPT
from datetime import datetime
import os

st.set_page_config(page_title="Meeting Summarizer", layout="wide")
st.title("📋 AI Meeting Summarizer & Action Tracker")

# Split screen
col1, col2 = st.columns(2)

# Store persistent results across interactions
if 'summaries' not in st.session_state:
    st.session_state.summaries = []  # List of summaries
if 'transcripts' not in st.session_state:
    st.session_state.transcripts = {}  # Dictionary of date -> transcript

# Define the function to parse action items
def parse_action_items(text):
    grouped = {}
    current_person = None

    # List of expected task keywords to capture
    task_keywords = [
        "optimize landing page",
        "prepare client presentation",
        "coordinate load testing",
        "review development resource usage",
        "add notes",
        "secure budget approval",
        "solicit feedback",
        "reconvene"
    ]

    # Parse each line to extract action items
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue

        # Check for a person's name at the beginning of the line (e.g., "Sara (Marketing):")
        if line.endswith(":") and not line.startswith("-"):
            current_person = line[:-1].strip()
            if current_person not in grouped:
                grouped[current_person] = []

        # Check if the line contains any action item keywords
        for task in task_keywords:
            if task in line.lower() and current_person:
                # Capture task with a deadline if available
                match = re.search(r"(\bby\b|\bfor\b)(.*)", line)  # Detect deadline mentions
                deadline = match.group(2) if match else "No deadline specified"
                grouped[current_person].append((task, deadline))

    return grouped

# Left panel: Input & Button
with col1:
    st.subheader("➤ Upload Transcript or Paste Text")

    transcript_input = st.text_area("Transcript", height=250)

    uploaded_file = st.file_uploader("Or upload a transcript (.txt)", type=["txt"])
    if uploaded_file is not None:
        transcript_input = uploaded_file.read().decode("utf-8")

        # Save the uploaded transcript content in session state
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        st.session_state.transcripts[current_datetime] = transcript_input

    if st.button("Generate Summary & Action Items"):
        if transcript_input.strip():
            with st.spinner("Analyzing transcript..."):
                # Generate the summary and actions
                summary = generate_response(SUMMARY_PROMPT, transcript_input).content
                actions = generate_response(ACTION_ITEMS_PROMPT, transcript_input).content

                # Get the current date and time for naming
                current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

                # If typed text, save it as a .txt file in session state
                if uploaded_file is None:
                    file_name = f"meeting_transcript_{current_datetime}.txt"
                    st.session_state.transcripts[current_datetime] = transcript_input

                # Store the summary, actions, and file name in session state
                st.session_state.summaries.append({
                    'date': current_datetime,
                    'summary': summary,
                    'actions': actions,
                    'file_name': file_name if uploaded_file is None else current_datetime
                })

# Right panel: Summary & Action Items
with col2:
    st.subheader(f"🗓️ Summary & Tasks History")

    if st.session_state.summaries:
        for entry in st.session_state.summaries:
            # Make date clickable, download corresponding transcript
            meeting_date = entry['date']
            file_name = entry['file_name']
            summary = entry['summary']
            actions = entry['actions']

            # Show meeting date and summary
            formatted_date = datetime.strptime(meeting_date, "%Y-%m-%d_%H-%M-%S").strftime("%B %d, %Y at %I:%M %p")
            st.markdown(f"#### 📝 Meeting Summary - {formatted_date}")
            st.write(summary)

            st.markdown("#### ✅ Action Items")
            grouped_tasks = parse_action_items(actions)
            for person in sorted(grouped_tasks.keys()):
                st.markdown(f"**{person}**")
                for i, (task, deadline) in enumerate(grouped_tasks[person]):
                    # Make each checkbox's key unique by adding a timestamp
                    task_key = f"{person}_{i}_{meeting_date}"
                    st.checkbox(f"{task} (Deadline: {deadline})", key=task_key)
    else:
        st.write("No summaries generated yet.")
