# Import required libraries
import streamlit as st
from langchain_core.prompts import PromptTemplate
from langchain.llms import Clarifai
import urllib.parse
import docx
import PyPDF2
import io

# Configure Streamlit page settings
st.set_page_config(page_title="Generate your Email!!", page_icon="📬", layout="wide")

def read_file_content(file):
    """
    Extract text content from uploaded files (PDF, DOCX, TXT)
    Args:
        file: StreamlitUploadedFile object
    Returns:
        str: Extracted text content from the file
    """
    content = ""
    if file.type == "text/plain":
        content = str(file.read(), 'utf-8')
    elif file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        for page in pdf_reader.pages:
            content += page.extract_text()
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(io.BytesIO(file.read()))
        content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return content

def main():
    """Main function to render the Streamlit UI and handle user interactions"""
    # Create two-column layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.title("Email Generator")
        
        # Input fields for sender and recipient information
        sender_name = col1.text_input("Sender's Name", key="sender_name", value="")
        sender_position = col1.text_input("Sender's Position", key="sender_position", value="")
        sender_company = col1.text_input("Sender's Company", key="sender_company", value="")
        recipient_name = col1.text_input("Recipient's Name", key="recipient_name", value="")
        recipient_position = col1.text_input("Recipient's Position", key="recipient_position", value="")
        recipient_company = col1.text_input("Recipient's Company", key="recipient_company", value="")
        
        # Toggle between manual input and attachment-based generation
        use_attachment = col1.checkbox("Generate email from attachment content?")
        
        # Show context fields only if not using attachment
        if not use_attachment:
            context = col1.text_input("Context", key="context", value="")
            extra_detail = col1.text_input("Extra Detail", key="extra_detail", value="")
        
        # Email style options
        tone_options = ['Formal', 'Casual', 'Friendly']
        tone = col1.selectbox("Tone", tone_options, key="tone", index=0)
        
        length_options = ['Short', 'Medium', 'Long']
        preferred_length = col1.selectbox("Preferred Length", length_options, key="preferred_length", index=0)
        
        # File upload widget
        attachments = col1.file_uploader("Attachments", type=["pdf", "txt", "docx"], accept_multiple_files=True, key="attachments")
    
    # Email preview section
    with col2:
        col2.title("Email Preview")

    with col1:
        if col1.button("Create Email"):
            # Validate required fields
            if sender_name and recipient_name and ((not use_attachment and context) or (use_attachment and attachments)) and tone and preferred_length:
                # Process attachment content if using attachment mode
                if use_attachment:
                    attachment_content = ""
                    for file in attachments:
                        attachment_content += read_file_content(file) + "\n\n"
                    context = "Based on the attached document"
                    extra_detail = f"Summary of the attachment content: {attachment_content[:500]}..."
                
                # Generate email content
                email_content = generate_email(sender_name, sender_position, sender_company, 
                                            recipient_name, recipient_position, recipient_company, 
                                            context, extra_detail, tone, preferred_length, attachments)
                
                # Display email preview and mail client links
                with col2:
                    with st.expander("Preview Box", expanded=True):
                        st.write(email_content)
                        if email_content:
                            email_links = generate_email_links(recipient_name, context, email_content)
                            mail_link, gmail_link = email_links
                            st.markdown(f"[Open with Email Client]({mail_link})")
                            st.markdown(f"[Open with Gmail]({gmail_link})")
            else:
                st.warning("Please fill in all required fields.")

def generate_email_links(recipient_name, context, email_content):
    """
    Generate mailto and Gmail links for the email
    Args:
        recipient_name: Name of recipient
        context: Email subject
        email_content: Generated email body
    Returns:
        tuple: (mailto link, Gmail link)
    """
    encoded_context = urllib.parse.quote(context)
    encoded_body = urllib.parse.quote(email_content)

    mail_link = f"mailto:{recipient_name}?subject={encoded_context}&body={encoded_body}"
    gmail_link = f"https://mail.google.com/mail/?view=cm&su={encoded_context}&body={encoded_body}"

    return mail_link, gmail_link

def generate_email(sender_name, sender_position, sender_company, recipient_name, 
                  recipient_position, recipient_company, context, extra_detail, 
                  tone, preferred_length, attachments):
    """
    Generate email content using Clarifai's LLM
    Args:
        sender_name, position, company: Sender details
        recipient_name, position, company: Recipient details
        context: Email context/subject
        extra_detail: Additional information
        tone: Email tone (Formal/Casual/Friendly)
        preferred_length: Desired email length
        attachments: List of attached files
    Returns:
        str: Generated email content
    """
    # Clarifai API credentials
    PAT = '492e95751129453aafedbdcd9a524186'
    USER_ID = 'meta'
    APP_ID = 'Llama-2'
    MODEL_ID = 'llama2-13b-chat'
    MODEL_VERSION_ID = '7b297786042c42c395324b8b9e6572f7'

    # Create email generation prompt template
    template = """Generate a sales pitch email about a data analytics software from {sender_name} ({sender_position}, {sender_company}) to {recipient_name} ({recipient_position}, {recipient_company})
      with the following details:  
Context : {context}  
Write it in a {tone} tone. Make it {preferred_length} and include: {extra_detail}.  
Write the email in a proper format, as if you are the sender. Ensure there are no repeated sentences."""

    # Add attachment information to prompt if files are attached
    if attachments:
        attachment_names = ", ".join([attachment.name for attachment in attachments])
        template += f"\nAttachments: {attachment_names}"

    # Initialize prompt template
    prompt = PromptTemplate(
        input_variables=["sender_name", "recipient_name", "context", "tone", 
                        "preferred_length", "extra_detail"],
        template=template,
    )
    
    # Initialize Clarifai LLM
    llm = Clarifai(pat=PAT, user_id=USER_ID, app_id=APP_ID, model_id=MODEL_ID)

    # Generate email content using LLM
    response = llm(prompt.format(
        sender_name=sender_name,
        sender_position=sender_position,
        sender_company=sender_company,
        recipient_name=recipient_name,
        recipient_position=recipient_position,
        recipient_company=recipient_company,
        context=context,
        tone=tone,
        preferred_length=preferred_length,
        extra_detail=extra_detail,
        attachments=attachments
    ))

    return response

if __name__ == "__main__":
    main()
