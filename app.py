from dotenv import load_dotenv

load_dotenv()
import base64
import io
import streamlit as st
import os
from PIL import Image
import PyPDF2 as pdf2
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text


def input_pdf_to_text(uploaded_file):
    if uploaded_file is not None:
        ## Convert the PDF to image
        reader=pdf2.PdfReader(uploaded_file)
        text = ""

        for page in range(len(reader.pages)):
            page = reader.pages[page]
            text+=str(page.extract_text())
        return text 

    else:
        raise FileNotFoundError("No file uploaded")
    

## Prompt 

input_prompt = """
Hey Act like a skilled and very experience ATS(Application Tracking System)
with the deep understanding of tech field, software engineering, data science, data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide best assistance
for imporving the resume. Assign the percentage Match based on JD  and the missing keywords 
with high accuracy.

resume:{text}
description:{jd}

Before matching the resume with description, first validate the given description correct. 
If description is correct then match it with text and go ahead with response else return the 
Warning: Please provide a valid Job Description.

I want the response in the single string having the structure as 
JD Match : %
MissingKeywords: keywords in bullets

Profile Summary : "" 
"""
## streamlit app
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")
jd=st.text_area("Job Description: ")

uploaded_file=st.file_uploader("Upload Your Resume",type=["pdf"],help="Please upload the PDF")

if uploaded_file is not None:
    # Additional validation: check if the file name contains "resume"
    if "resume" not in uploaded_file.name.lower():
        st.warning("Please upload a file with 'resume' in its name.")
        st.stop()
    st.write("PDF Uploaded Successfully")

# Validation for text area not being blank
if not jd.strip():
    st.warning("Job Description cannot be blank. Please provide a description.")
    st.stop()

RESUME_KEYWORDS = ['experience', 'education', 'skills', 'summary', 'career objective']

def is_resume_content(text):
    """
    Check if the given text contains keywords typically found in resumes.
    """
    text_lower = text.lower()
    for keyword in RESUME_KEYWORDS:
        if keyword in text_lower:
            return True
    return False

submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        text=input_pdf_to_text(uploaded_file)
        # Additional validation: check if the content resembles a resume
        if not is_resume_content(text):
            st.warning("The uploaded file does not appear to contain resume content.")
            st.stop()
        response=get_gemini_response(input_prompt)
        st.subheader(response)
    else:
        st.write("Please uplaod the resume")
