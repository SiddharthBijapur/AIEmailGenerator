import streamlit as st
from langchain import PromptTemplate
from langchain.llms import Clarifai
import urllib.parse

st.set_page_config(page_title="Generate your Email!!", page_icon="📬", layout="wide")

def main():
    col1, col2 = st.columns(2)
    
    with col1:
        st.title("Email Generator")
        
        sender_name = col1.text_input("Sender's Name", key="sender_name", value="")
        
        recipient_name = col1.text_input("Recipient's Name", key="recipient_name", value="")
        
        subject = col1.text_input("Subject/Topic", key="subject", value="")
        
        extra_detail = col1.text_input("Extra Detail", key="extra_detail", value="")

        tone_options = ['Formal', 'Casual', 'Friendly']
        tone = col1.selectbox("Tone", tone_options, key="tone", index=0)
        
        length_options = ['Short', 'Medium', 'Long']
        preferred_length = col1.selectbox("Preferred Length", length_options, key="preferred_length", index=0)
        
        attachments = col1.file_uploader("Attachments", type=["pdf", "txt", "docx"], accept_multiple_files=True, key="attachments")
    
    with col2:
        col2.title("Email Preview")

    with col1:
        if col1.button("Create Email"):
            if sender_name and recipient_name and subject and tone and preferred_length:
                email_content = generate_email(sender_name, recipient_name, subject, extra_detail, tone, preferred_length, attachments)
                with col2:
                    with st.expander("Preview Box", expanded=True):
                        st.write(email_content)
                        if email_content:
                            email_links = generate_email_links(recipient_name, subject, email_content)
                            mail_link, gmail_link = email_links
                            st.markdown(f"[Open with Email Client]({mail_link})")
                            st.markdown(f"[Open with Gmail]({gmail_link})")
            else:
                st.warning("Please fill in all required fields.")

def generate_email_links(recipient_name, subject, email_content):
    encoded_subject = urllib.parse.quote(subject)
    encoded_body = urllib.parse.quote(email_content)

    mail_link = f"mailto:{recipient_name}?subject={encoded_subject}&body={encoded_body}"
    gmail_link = f"https://mail.google.com/mail/?view=cm&su={encoded_subject}&body={encoded_body}"

    return mail_link, gmail_link

def generate_email(sender_name, recipient_name, subject, extra_detail, tone, preferred_length, attachments):
    PAT = '492e95751129453aafedbdcd9a524186'
    USER_ID = 'meta'
    APP_ID = 'Llama-2'
    MODEL_ID = 'llama2-13b-chat'
    MODEL_VERSION_ID = '7b297786042c42c395324b8b9e6572f7'

    template = """Generate an email from {sender_name} to {recipient_name} with the following details:\nSubject: {subject}\n. Write it in a {tone} way. Make it {preferred_length} length and add details: {extra_detail}. 
    Write it in a proper format of a letter. Just write the email as if you are the one sending it. Make sure there are no repeated sentences."""

    if attachments:
        attachment_names = ", ".join([attachment.name for attachment in attachments])
        template += f"\nAttachments: {attachment_names}"

    prompt = PromptTemplate(
        input_variables=["sender_name", "recipient_name", "subject", "tone", "preferred_length", "extra_detail"],
        template=template,
    )
    
    llm = Clarifai(pat=PAT, user_id=USER_ID, app_id=APP_ID, model_id=MODEL_ID)

    response = llm(prompt.format(
        sender_name=sender_name,
        recipient_name=recipient_name,
        subject=subject,
        tone=tone,
        preferred_length=preferred_length,
        extra_detail=extra_detail
    ))

    return response

if __name__ == "__main__":
    main()
