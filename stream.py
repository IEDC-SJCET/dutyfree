import json
import os
import re
import pandas as pd
import streamlit as st
from datetime import datetime
from fpdf import FPDF
from dotenv import load_dotenv
from groq import Groq  

# Load Templates
def load_templates():
    try:
        with open("templates.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        st.error("❌ templates.json file is missing or invalid!")
        st.stop()

# Load Faculty List
def load_faculty_list():
    try:
        return pd.read_excel("facultylist.xlsx")
    except FileNotFoundError:
        st.error("❌ facultylist.xlsx file not found!")
        st.stop()

faculty_df = load_faculty_list()

# Validation Functions
def validate_date(date_str):
    try:
        return datetime.strptime(date_str, "%d-%m-%Y").strftime("%d-%m-%Y")
    except ValueError:
        return None

def validate_contact(number):
    return number if re.fullmatch(r"\d{10,12}", number) else None

# AI Leave Letter Generation
def generate_ai_leave_letter(data, faculty_df):
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        return "❌ Error: Missing GROQ API Key!"
    
    client = Groq(api_key=api_key)
    
    # Get faculty designation 
    faculty_designation = ""
    recipient_line = ""
    sir_madam = ""
    
    if data['subto'] == "Principal":
        recipient_line = "The Principal"
        sir_madam = "Sir/Madam"
    else:
        faculty_info = faculty_df[faculty_df['Faculty'] == data['subto']]
        if not faculty_info.empty:
            faculty_designation = faculty_info.iloc[0]['Designation']
            recipient_line = f"{data['subto']}\n{faculty_designation}\n{faculty_info.iloc[0]['Department']}"
            sir_madam = "Sir/Madam"
    
    # AI Prompt
    prompt = f"""
    Write a formal leave letter using the following format:

    From:
    {data['user']}
    {data['year_of_study']} {data['programme']} ({data['department']})
    St. Joseph's College of Engineering and Technology
    Palai

    To:
    {recipient_line}
    St. Joseph's College of Engineering and Technology
    Palai

    Date: [Current Date]
    Subject: 
    Respected {sir_madam},

    Request leave from {data['start_date']} to {data['end_date']}.
    Reason: {data['extra_details']}

    Format it professionally having 1-3 paragraphs with a polite tone as it is given to college and include proper closing with Thanking you and Yours faithfully.In the closing section, do not want to mention the department name and college name again.
    """
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You generate professional leave letters following standard academic letter writing formats."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile"
        )
        
        return response.choices[0].message.content if response.choices else "❌ AI Response Error!"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Chat Interface Logic
def chat_interface():
    st.title("💬 SJCET Leave Letter Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.step = 0
        st.session_state.leave_data = {}
        st.session_state.messages.append({"role": "assistant", "text": "👋 What's your name?"})

    questions = [
        "👋 What's your name?",
        "📚 Select your programme:",
        "🏢 Select your department:",
        "📌 To whom is this letter addressed?",
        "📚 Which year do you study?",
        "📅 Enter the start date of your leave (DD-MM-YYYY):",
        "📅 Enter the end date of your leave (DD-MM-YYYY):",
        "📞 Enter your contact number:"
    ]

    fields = ["user", "programme", "department", "subto", "year_of_study", "start_date", "end_date", "contact_number"]
    programme_options = ["B.Tech", "M.Tech"]

    # Display previous messages
    for msg in st.session_state.messages:
        st.chat_message("assistant" if msg["role"] == "assistant" else "user").write(msg["text"])

    if st.session_state.step < len(questions):
        field_name = fields[st.session_state.step]
        user_input = None

        # Handle different input types
        if field_name == "user":
            user_input = st.chat_input("")
        
        elif field_name == "programme":
            user_input = st.radio(questions[st.session_state.step], programme_options, key="programme_radio")
            if st.button("Next", key="programme_next"):
                st.session_state.messages.append({"role": "user", "text": user_input})
                st.session_state.leave_data[field_name] = user_input
                st.session_state.step += 1
                if st.session_state.step < len(questions):
                    st.session_state.messages.append({"role": "assistant", "text": questions[st.session_state.step]})
                st.rerun()
        
        elif field_name == "department":
            selected_programme = st.session_state.leave_data.get("programme", "B.Tech")
            department_options = faculty_df[faculty_df['Programme'] == selected_programme]['Department'].unique().tolist()
            user_input = st.selectbox(questions[st.session_state.step], department_options, key="department_select")
            if st.button("Next", key="department_next"):
                st.session_state.messages.append({"role": "user", "text": user_input})
                st.session_state.leave_data[field_name] = user_input
                st.session_state.step += 1
                if st.session_state.step < len(questions):
                    st.session_state.messages.append({"role": "assistant", "text": questions[st.session_state.step]})
                st.rerun()

        elif field_name == "subto":
            recipient_type = st.radio("Select recipient:", ["Principal", "Faculty"], horizontal=True, key="recipient_radio")
            if recipient_type == "Principal":
                user_input = "Principal"
                if st.button("Next", key="principal_next"):
                    st.session_state.messages.append({"role": "user", "text": user_input})
                    st.session_state.leave_data[field_name] = user_input
                    st.session_state.step += 1
                    if st.session_state.step < len(questions):
                        st.session_state.messages.append({"role": "assistant", "text": questions[st.session_state.step]})
                    st.rerun()
            else:
                selected_department = st.session_state.leave_data.get("department", "")
                faculty_options = faculty_df[faculty_df['Department'] == selected_department]['Faculty'].tolist()
                selected_faculty = st.selectbox("📜 Select Faculty:", faculty_options, key="faculty_select")
                if st.button("Next", key="faculty_next"):
                    st.session_state.messages.append({"role": "user", "text": selected_faculty})
                    st.session_state.leave_data[field_name] = selected_faculty
                    st.session_state.step += 1
                    if st.session_state.step < len(questions):
                        st.session_state.messages.append({"role": "assistant", "text": questions[st.session_state.step]})
                    st.rerun()

        elif field_name == "year_of_study":
            selected_programme = st.session_state.leave_data.get("programme", "B.Tech")
            year_options = ["1st Year", "2nd Year", "3rd Year", "4th Year"] if selected_programme == "B.Tech" else ["1st Year", "2nd Year"]
            user_input = st.radio(questions[st.session_state.step], year_options, key="year_radio")
            if st.button("Next", key="year_next"):
                st.session_state.messages.append({"role": "user", "text": user_input})
                st.session_state.leave_data[field_name] = user_input
                st.session_state.step += 1
                if st.session_state.step < len(questions):
                    st.session_state.messages.append({"role": "assistant", "text": questions[st.session_state.step]})
                st.rerun()

        else:
            if not any(msg["text"] == questions[st.session_state.step] for msg in st.session_state.messages):
                st.session_state.messages.append({"role": "assistant", "text": questions[st.session_state.step]})
                st.rerun()
            user_input = st.chat_input("")

        # Handle text input validation and progression
        if user_input and field_name not in ["programme", "department", "subto", "year_of_study"]:
            if field_name == "contact_number":
                user_input = validate_contact(user_input)
                if not user_input:
                    st.session_state.messages.append({"role": "assistant", "text": "❌ Invalid phone number!"})
                    st.rerun()

            if field_name in ["start_date", "end_date"]:
                user_input = validate_date(user_input)
                if not user_input:
                    st.session_state.messages.append({"role": "assistant", "text": "❌ Invalid date format!"})
                    st.rerun()

            st.session_state.leave_data[field_name] = user_input
            st.session_state.messages.append({"role": "user", "text": user_input})
            st.session_state.step += 1

            if st.session_state.step < len(questions):
                st.session_state.messages.append({"role": "assistant", "text": questions[st.session_state.step]})

            st.rerun()

    else:
        templates = load_templates()
        choice = st.radio("📄 Choose a template or AI-generated letter:", ["Template", "AI"], horizontal=True)

        if choice == "Template":
            selected_template = st.selectbox("📜 Select a template:", list(templates.keys()))
            st.session_state.leave_data["template"] = selected_template
        else:
            st.session_state.leave_data["template"] = "AI-generated"
            st.session_state.leave_data["extra_details"] = st.text_area("📝 Describe your reason:")

        signature_path = st.file_uploader("✍️ Upload signature (optional)", type=["png", "jpg", "jpeg"])
        if st.button("✅ Generate Leave Letter"):
            return st.session_state.leave_data, signature_path

    # Return None if the process is not completed
    return None, None

def generate_leave_letter(data, templates, faculty_df, signature_path=None):
    
    current_date = datetime.now().strftime("%d-%m-%Y")
    
    # Get recipient with designation
    if data['subto'] == "Principal":
        faculty_designation = ""  # Empty for Principal
        faculty_department = ""  # Empty for Principal
    else:
        faculty_info = faculty_df[faculty_df['Faculty'] == data['subto']]
        faculty_designation = faculty_info.iloc[0]['Designation'] if not faculty_info.empty else ""
        faculty_department = faculty_info.iloc[0]['Department'] if not faculty_info.empty else ""
    
    template_data = {
        **data,  # Include all existing data
        'current_date': current_date,
        'faculty_designation': faculty_designation,
        'faculty_department': faculty_department
    }

    if data['template'] == "AI-generated":
        letter_content = generate_ai_leave_letter(data, faculty_df)
    else:
        # Use the selected template with the enhanced data 
        template = templates.get(data['template'])
        letter_content = template.format(**template_data)

    # Generate PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, letter_content)

    output_file = f"{data['user'].replace(' ', '_')}_leave_letter.pdf"
    pdf.output(output_file)

    with open(output_file, "rb") as file:
        st.download_button("📥 Download Leave Letter", file, file_name=output_file, mime="application/pdf")

def main():
    faculty_df = load_faculty_list()  # Load faculty list at the start
    leave_data, signature_path = chat_interface()
    if leave_data:
        generate_leave_letter(leave_data, load_templates(), faculty_df, signature_path)

if __name__ == "__main__":
    main()