import os
import streamlit as st
from openai import OpenAI, OpenAIError

# Define API parameters
api_key = os.getenv("OPENAI_API_KEY", "your_api_key_here")  
base_url = os.getenv("API_BASE_URL", "https://api.aimlapi.com")
model_name = os.getenv("MODEL_NAME", "meta-llama/Llama-3.2-3B-Instruct-Turbo")

client = OpenAI(api_key=api_key, base_url=base_url)

# Define the function to get project assignment
def get_project_assignment(project_description, expertise_list):
    try:
        user_input = f"The project is described as: '{project_description}'. The following people with different expertise are involved: {expertise_list}. Please intelligently assign tasks based on their expertise and guide them."
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant who assigns project tasks intelligently based on expertise.",
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

# Streamlit App
def main():
    st.title("WorkUp: AI Task Assignment")

    # Sidebar for project description and member count
    st.sidebar.header("Project Details")
    project_description = st.sidebar.text_area("Enter the project description:")
    num_members = st.sidebar.number_input("Enter the number of team members:", min_value=1, max_value=10, value=1)

    # Input fields for team members' names and expertise
    expertise_list = []
    st.subheader("Team Members' Names and Expertise")
    for i in range(num_members):
        member_name = st.text_input(f"Member {i + 1} name:")
        expertise = st.text_input(f"{member_name}'s expertise:", key=f"expertise_{i}")
        if member_name and expertise:
            expertise_list.append(f"{member_name}: {expertise}")

    # Button to trigger the task assignment
    if st.button("Assign Tasks"):
        if project_description and expertise_list:
            # Join the expertise list as a string
            expertise_str = "; ".join(expertise_list)
            assignment_response = get_project_assignment(project_description, expertise_str)
            st.write(assignment_response)
        else:
            st.warning("Please enter the project description, member names, and their expertise.")

if __name__ == "__main__":
    main()
