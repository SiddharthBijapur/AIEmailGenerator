Email Generator with Attachment Processing

A Streamlit application that generates professional emails with customizable formatting, tone, and length. The application supports both manual input and document-based generation.

Features
- Generate emails based on user input or document content
- Customize sender and recipient information
- Select email tone (Formal, Casual, Friendly)
- Choose preferred email length
- Upload and process multiple document types (PDF, DOCX, TXT)
- Generate links to open emails in mail clients

Installation
1. Clone this repository:
```bash
git clone https://github.com/yourusername/email-generator.git
cd email-generator
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run email_generator.py
```

Usage
1. Fill in the sender and recipient information
2. Choose whether to generate from attachment or manual input
3. If using manual input:
   - Enter the context and any extra details
4. If using attachment:
   - Enter the purpose of the email
   - Upload relevant documents
5. Select tone and preferred length
6. Click "Create Email" to generate your email
7. Use the provided links to open the email in your preferred mail client

API Configuration
The application uses Clarifai's LLM API for email generation. To use your own API key:
1. Create an account at [Clarifai](https://clarifai.com/)
2. Get your Personal Access Token (PAT)
3. Replace the PAT variable in the code with your token



