import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from prompts import SUMMARY_PROMPT, ACTION_ITEMS_PROMPT

# Initialize environment variables
load_dotenv()

# Initialize Pinecone using the updated method
from pinecone import Pinecone, ServerlessSpec

# Initialize Pinecone instance
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Proceed with your Pinecone setup
if 'meeting-to-task' not in pc.list_indexes().names():
    pc.create_index(
        name='meeting-to-task',  # Valid index name
        dimension=1536,  # Adjust this as needed for your embeddings
        metric='euclidean',
        spec=ServerlessSpec(
            cloud='aws',  # Cloud remains as AWS
            region='us-east-1'  # Try us-east-1
        )
    )

def load_transcript(file_path):
    with open(file_path, 'r') as f:
        return f.read()

def generate_response(prompt_template: str, transcript: str, model_temp=0.3):
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro-latest",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=model_temp,
    )
    prompt = PromptTemplate.from_template(prompt_template)
    chain = prompt | llm
    return chain.invoke({"transcript": transcript})

if __name__ == "__main__":
    transcript = load_transcript("sample_meeting.txt")

    print("\n--- MEETING SUMMARY ---\n")
    summary = generate_response(SUMMARY_PROMPT, transcript)
    print(summary.content)

    print("\n--- ACTION ITEMS ---\n")
    actions = generate_response(ACTION_ITEMS_PROMPT, transcript)
    print(actions.content)
