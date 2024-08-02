import streamlit as st
import sqlite3
import google.generativeai as genai
import os

# Set up the API key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', st.secrets.get("GOOGLE_API_KEY"))
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize SQLite Database
conn = sqlite3.connect('team_selector.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS team_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        project_management TEXT,
        public_speaking TEXT,
        ppt_development TEXT,
        database_management TEXT,
        coding TEXT,
        deployment TEXT,
        passion TEXT,
        recommended_role TEXT,
        explanation TEXT
    )
''')
conn.commit()

# Function to generate response from the model
def generate_response(prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return "Sorry, I couldn't process your request."

# Function to save data to SQLite
def save_to_sqlite(data):
    c.execute('''
        INSERT INTO team_members (
            name, project_management, public_speaking, ppt_development, 
            database_management, coding, deployment, passion, recommended_role, explanation
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data["name"], data["project_management"], data["public_speaking"], data["ppt_development"], 
        data["database_management"], data["coding"], data["deployment"], data["passion"], 
        data["recommended_role"], data["explanation"]
    ))
    conn.commit()

# Streamlit app
def main():
    st.title("Team Selection App")
    st.image("teamselectorapp.jpg", width=100)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Input fields for Team Selection
    st.subheader("Enter your details and skills")
    name = st.text_input("Name")
    project_management = st.selectbox("Project Management", ["Novice", "Competent", "Proficient", "Expert"])
    public_speaking = st.selectbox("Public Speaking", ["Novice", "Competent", "Proficient", "Expert"])
    ppt_development = st.selectbox("PPT/Story Development", ["Novice", "Competent", "Proficient", "Expert"])
    database_management = st.selectbox("Database Management", ["Novice", "Competent", "Proficient", "Expert"])
    coding = st.selectbox("Coding", ["Novice", "Competent", "Proficient", "Expert"])
    deployment = st.selectbox("Deployment", ["Novice", "Competent", "Proficient", "Expert"])
    passion = st.selectbox("Passion", ["Coding", "Documentation & Research", "Presentation & Communication"])

    # Collect all inputs into a single prompt for the chatbot
    user_input = (
        f"Name: {name}\n"
        f"Project Management: {project_management}\n"
        f"Public Speaking: {public_speaking}\n"
        f"PPT/Story Development: {ppt_development}\n"
        f"Database Management: {database_management}\n"
        f"Coding: {coding}\n"
        f"Deployment: {deployment}\n"
        f"Passion: {passion}\n"
        "Based on these skills and interests, please analyze the information and recommend the best fit role for this person to lead in the team. Also, explain why you chose this role:"
    )

    # Button to save input and recommend role
    if st.button("Submit"):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        response = generate_response(user_input)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Display chat history
        for message in st.session_state.chat_history:
            st.write(f"{message['role'].capitalize()}: {message['content']}")
        
        # Extract recommended role and explanation from chatbot response
        recommended_role = "No specific role recommended"
        explanation = "No explanation provided"
        lines = response.split('\n')
        for i, line in enumerate(lines):
            if "recommend" in line.lower():
                recommended_role = line.split(':')[-1].strip()
            if "explain" in line.lower() or "reason" in line.lower():
                explanation = lines[i + 1].strip() if i + 1 < len(lines) else explanation
        
        data = {
            "name": name,
            "project_management": project_management,
            "public_speaking": public_speaking,
            "ppt_development": ppt_development,
            "database_management": database_management,
            "coding": coding,
            "deployment": deployment,
            "passion": passion,
            "recommended_role": recommended_role,
            "explanation": explanation
        }
        save_to_sqlite(data)
        st.success(f"Data saved to SQLite database! Recommended Role: {recommended_role}\nExplanation: {explanation}")

if __name__ == "__main__":
    main()
