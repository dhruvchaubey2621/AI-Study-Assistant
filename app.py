import os
import json
import streamlit as st
from dotenv import load_dotenv
from google import genai

# Load API key
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Page Config
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="wide"
)

# Header
st.title("📚 AI Study Assistant")
st.write("Generate summaries, quizzes, and flashcards instantly.")

# Inputs
topic = st.text_input("Enter a study topic")

level = st.selectbox(
    "Select Level",
    ["School", "Class 11-12", "College"]
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

Create study material for this topic.

Return ONLY valid JSON.

JSON Format:

{{
  "summary": "Detailed notes of at least 300 words",

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
             st.warning("Gemini is currently overloaded. Please wait a minute and try again.")
         else:
             st.error(f"Error: {e}")    