import os
import streamlit as st
from openai import OpenAI, OpenAIError
import pandas as pd  # To handle file input

# Define API parameters
api_key = os.getenv("OPENAI_API_KEY", "8772096b1b3248128cf4072be826ee90")
base_url = os.getenv("API_BASE_URL", "https://api.aimlapi.com")
model_name = os.getenv("MODEL_NAME", "meta-llama/Llama-3.2-3B-Instruct-Turbo")

client = OpenAI(api_key=api_key, base_url=base_url)

# Define the function to get project assignment
def get_project_assignment(project_description, expertise_list, language):
    try:
        user_input = f"The project is described as: '{project_description}'. The following people with different expertise are involved: {expertise_list}. The preferred programming language is {language}. Please intelligently assign tasks based on their expertise and guide them, ensuring to use {language} where applicable."
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant who assigns project tasks intelligently based on expertise and the preferred programming language.",
                },
                {
                    "role": "user",
                    "content": user_input,
                },
            ],
        )

        # Extract and return the assistant's response
        message = response.choices[0].message.content
        return f"Assistant: {message}"

    except OpenAIError as e:
        return f"API request failed: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Define the function to get unique app name suggestions
def get_app_name_suggestion(project_description):
    try:
        user_input = f"Based on the project description: '{project_description}', suggest a unique and creative name for an app."
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant specializing in branding and app naming.",
                },
                {
                    "role": "user",
                    "content": user_input,
                },
            ],
        )

        # Extract and return the assistant's response
        message = response.choices[0].message.content
        return f"Suggested App Name: {message}"

    except OpenAIError as e:
        return f"API request failed: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Function to process uploaded file
def process_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        try:
            # Try reading the file as a CSV
            df = pd.read_csv(uploaded_file)
            # Extract project description and expertise from the dataframe
            project_description = df.iloc[0]['Project Description'] if 'Project Description' in df.columns else ''
            expertise_list = df[['Name', 'Expertise']].apply(lambda row: f"{row['Name']}: {row['Expertise']}", axis=1).tolist()
            return project_description, expertise_list
        except Exception as e:
            st.error(f"Error processing file: {e}")
            return None, None
    return None, None

# Streamlit App
def main():
    st.title("WorkUp: AI Task Assignment and App Name Generator")

    # Sidebar for project description and member count
    st.sidebar.header("Project Details")
    
    # File uploader to upload project description and team members
    uploaded_file = st.sidebar.file_uploader("Upload a file (CSV with columns 'Project Description', 'Name', 'Expertise')", type=['csv'])

    # Manual input as fallback
    st.sidebar.write("Or, fill out the fields below manually if no file is uploaded.")
    project_description = st.sidebar.text_area("Enter the project description:") if uploaded_file is None else ""
    num_members = st.sidebar.number_input("Enter the number of team members:", min_value=1, max_value=10, value=1) if uploaded_file is None else 1

    expertise_list = []
    st.sidebar.subheader("Team Members' Names and Expertise") if uploaded_file is None else None
    if uploaded_file is None:
        for i in range(num_members):
            member_name = st.sidebar.text_input(f"Member {i + 1} name:", key=f"member_name_{i}")
            expertise = st.sidebar.text_input(f"{member_name}'s expertise:", key=f"expertise_{i}")
            if member_name and expertise:
                expertise_list.append(f"{member_name}: {expertise}")
    else:
        # Process uploaded file
        project_description, expertise_list = process_uploaded_file(uploaded_file)

    # Add a selectbox for preferred programming language
    language = st.sidebar.selectbox("Preferred Programming Language", ["Python", "Java", "C++", "C"])

    # Display the input on the main screen in real-time
    if project_description:
        st.subheader("Project Description:")
        st.write(project_description)

    if expertise_list:
        st.subheader("Team Members and Expertise:")
        for member in expertise_list:
            st.write(member)

    # Button to trigger both the task assignment and app name generation
    if st.button("Assign Task"):
        if project_description and expertise_list:
            # Join the expertise list as a string
            expertise_str = "; ".join(expertise_list)

            # Get task assignment
            assignment_response = get_project_assignment(project_description, expertise_str, language)
            st.subheader("AI Task Assignment:")
            st.write(assignment_response)

            # Get app name suggestion
            app_name_response = get_app_name_suggestion(project_description)
            st.subheader("App Name Suggestion:")
            st.write(app_name_response)

        else:
            st.warning("Please upload a valid file or enter the project description, member names, and their expertise.")

if __name__ == "__main__":
    main()
