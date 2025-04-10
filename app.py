import streamlit as st
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
import urllib.parse
import docx
import PyPDF2
import io

st.set_page_config(page_title="Generate your Email!!", page_icon="📬", layout="wide")

def get_response_from_clarifai(prompt):
    PAT = '492e95751129453aafedbdcd9a524186'
    USER_ID = 'meta'
    APP_ID = 'Llama-2'
    MODEL_ID = 'llama2-13b-chat'
    
    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)

    metadata = (('authorization', 'Key ' + PAT),)

    userDataObject = resources_pb2.UserAppIDSet(
        user_id=USER_ID, app_id=APP_ID)

    post_model_outputs_request = service_pb2.PostModelOutputsRequest(
        user_app_id=userDataObject,
        model_id=MODEL_ID,
        inputs=[
            resources_pb2.Input(
                data=resources_pb2.Data(
                    text=resources_pb2.Text(
                        raw=prompt
                    )
                )
            )
        ]
    )

    response = stub.PostModelOutputs(
        post_model_outputs_request,
        metadata=metadata
    )

    if response.status.code != status_code_pb2.SUCCESS:
        raise Exception("Request failed, status: " + response.status.description)

    return response.outputs[0].data.text.raw

def read_file_content(file):
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
    col1, col2 = st.columns(2)
    
    with col1:
        st.title("Email Generator")
        
        sender_name = col1.text_input("Sender's Name", key="sender_name", value="")
        sender_position = col1.text_input("Sender's Position", key="sender_position", value="")
        sender_company = col1.text_input("Sender's Company", key="sender_company", value="")
        recipient_name = col1.text_input("Recipient's Name", key="recipient_name", value="")
        recipient_position = col1.text_input("Recipient's Position", key="recipient_position", value="")
        recipient_company = col1.text_input("Recipient's Company", key="recipient_company", value="")
        
        use_attachment = col1.checkbox("Generate email from attachment content?")
        
        if not use_attachment:
            context = col1.text_input("Context", key="context", value="")
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
            try:
                if sender_name and recipient_name and ((not use_attachment and context) or (use_attachment and attachments)) and tone and preferred_length:
                    if use_attachment:
                        attachment_content = ""
                        for file in attachments:
                            attachment_content += read_file_content(file) + "\n\n"
                        context = "Based on the attached document"
                        extra_detail = f"Summary of the attachment content: {attachment_content[:500]}..."
                    
                    prompt = f"""Generate an email from {sender_name} ({sender_position}, {sender_company}) 
                    to {recipient_name} ({recipient_position}, {recipient_company}) with the following details:
                    Context: {context}
                    Write it in a {tone} tone. Make it {preferred_length} and include: {extra_detail}."""
                    
                    if attachments:
                        attachment_names = ", ".join([attachment.name for attachment in attachments])
                        prompt += f"\nAttachments: {attachment_names}"

                    email_content = get_response_from_clarifai(prompt)
                    
                    with col2:
                        with st.expander("Preview Box", expanded=True):
                            st.write(email_content)
                            if email_content:
                                encoded_context = urllib.parse.quote(context)
                                encoded_body = urllib.parse.quote(email_content)
                                mail_link = f"mailto:{recipient_name}?subject={encoded_context}&body={encoded_body}"
                                gmail_link = f"https://mail.google.com/mail/?view=cm&su={encoded_context}&body={encoded_body}"
                                st.markdown(f"[Open with Email Client]({mail_link})")
                                st.markdown(f"[Open with Gmail]({gmail_link})")
                else:
                    st.warning("Please fill in all required fields.")
            except Exception as e:
                st.error(f"Error generating email: {str(e)}")

if __name__ == "__main__":
    main()
