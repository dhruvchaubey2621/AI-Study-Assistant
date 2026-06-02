import os
import json
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from google import genai

# Load API key
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

HISTORY_FILE = "history.json"

if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)

# Page Config
st.set_page_config(
    page_title="Friday",
    page_icon="📚",
    layout="wide"
)
st.sidebar.title("📚 Study History")

try:
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)

    if history:
        for item in reversed(history[-10:]):
            st.sidebar.write(
             f"📖 {item['topic'].title()}\n{item['level']} • {item.get('study_mode','Unknown Mode')}"
            )
    else:
        st.sidebar.write("No history yet.")

except Exception as e:
    st.sidebar.error(str(e))

# Header
st.title("📚 Friday")
st.write("Generate summaries, quizzes, and flashcards instantly.")

# Inputs
topic = st.text_input("Enter a study topic")

level = st.selectbox(
    "Select Level",
    ["School", "Class 11-12", "College"]
)

study_mode = st.selectbox(
    "Study Mode",
    [
        "Quick Revision",
        "Detailed Notes",
        "Exam Preparation",
        "Flashcards Only"
    ]
)

# Generate Button
if st.button("Generate Study Material"):

    if not topic.strip():
        st.warning("Please enter a study topic.")
        st.stop()

    with st.spinner("Generating study material..."):

        prompt = f"""
You are an expert teacher.

Topic: {topic}
Student Level: {level}
Study Mode: {study_mode}

Instructions:

If Study Mode is "Quick Revision":
- Give concise notes
- Focus on key concepts
- Keep summary around 150-200 words

If Study Mode is "Detailed Notes":
- Give detailed explanation
- Include examples
- Include applications
- Keep summary around 400-600 words

If Study Mode is "Exam Preparation":
- Focus on important concepts
- Mention common exam questions
- Mention common mistakes
- Include exam tips

If Study Mode is "Flashcards Only":
- Keep summary very short
- Focus heavily on flashcards

Return ONLY valid JSON.

{{
  "summary": "Detailed notes here",

  "quiz": [
    "Question 1",
    "Question 2",
    "Question 3",
    "Question 4",
    "Question 5"
  ],

  "flashcards": [
    {{
      "question": "Question 1",
      "answer": "Answer 1"
    }},
    {{
      "question": "Question 2",
      "answer": "Answer 2"
    }},
    {{
      "question": "Question 3",
      "answer": "Answer 3"
    }},
    {{
      "question": "Question 4",
      "answer": "Answer 4"
    }},
    {{
      "question": "Question 5",
      "answer": "Answer 5"
    }}
  ]
}}

Return only JSON and nothing else.
"""

        try:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            result = response.text.strip()

            # Remove markdown code fences if Gemini adds them
            result = result.replace("```json", "")
            result = result.replace("```", "")
            result = result.strip()

            data = json.loads(result)

            summary = data["summary"]
            quiz = data["quiz"]
            flashcards = data["flashcards"]
            # Save to history

            new_entry = {
             "topic": topic,
             "level": level,
             "study_mode": study_mode,
             "time": datetime.now().strftime("%d-%m-%Y %H:%M")
            }

            with open("history.json", "r") as file:
             history = json.load(file)

            history.append(new_entry)
            st.success("History saved!")

            with open("history.json", "w") as file:
             json.dump(history, file, indent=4)

            with open(HISTORY_FILE, "w") as f:
             json.dump(history, f, indent=4)

            # Tabs
            tab1, tab2, tab3 = st.tabs(
                ["📖 Summary", "❓ Quiz", "🧠 Flashcards"]
            )

            with tab1:
                st.subheader("Study Summary")
                st.write(summary)

            with tab2:
                st.subheader("Quiz Questions")

                for i, question in enumerate(quiz, start=1):
                    st.write(f"{i}. {question}")

            with tab3:
                st.subheader("Flashcards")

                for card in flashcards:
                    with st.expander(card["question"]):
                        st.write(card["answer"])

            st.download_button(
                label="📥 Download Notes",
                data=summary,
                file_name=f"{topic}_notes.txt",
                mime="text/plain"
            )

        except Exception as e:
         if "503" in str(e):
             st.warning("Friday is currently overloaded. Please wait a minute and try again.")
         else:
             st.error(f"Error: {e}")    