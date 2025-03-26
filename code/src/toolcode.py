import openai
import hashlib
import json
import re
import email
import os
from email import policy
from email.parser import BytesParser
from docx import Document
import fitz  # PyMuPDF for PDFs
from flask import Flask, request, jsonify
import google.generativeai as genai

# Configure Google Gemini API
genai.configure(api_key="AIzaSyBnMJRmITq4NwdOufB7uQ3GnkqdyZKxK-0")
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize Flask app
app = Flask(__name__)

# Dictionary to track duplicate email hashes
email_hashes = {}

# Configurable Fields for Extraction
CONFIG_FIELDS = ["Deal", "Amount", "Expiration Date"]

# Rule-based configuration to determine source of extracted values
RULES_CONFIG = {
    "Deal": "body",  # Extract from email body
    "Amount": "body",  # If amount value nned to get from attachmen then use "Amount": "attachment",Extract from attachment if available, else fallback to body.
    "Expiration Date": "body"  # Extract from email body
}


REQUEST_TYPE_DEFINITIONS = {
    "Adjustment": """In commercial bank lending services, Adjustment refers to any modification made to 
    the terms of a loan or credit facility. This can include changes in interest rates, repayment schedules, 
    loan amounts, or other contractual terms to accommodate the borrower’s financial situation or market 
    conditions. Adjustments are often made due to changes in economic conditions, a borrower's creditworthiness, 
    or regulatory requirements. 

    Examples of adjustments in bank lending include:  
    - **Interest rate adjustment:** Changing the interest rate based on market fluctuations.  
    - **Loan term extension:** Extending the repayment period to reduce monthly payments.  
    - **Restructuring:** Modifying loan terms to help a borrower facing financial difficulties.
    """,

    "AU Transfer": """In commercial bank lending services, AU Transfer is not a widely recognized standard term. 
    However, depending on the context, it could refer to:

    - **Authorization (AU) Transfer:** A process where loan or credit authorization is transferred from one 
      entity or account to another within the bank’s lending system.
    - **Asset Utilization (AU) Transfer:** Movement of assets or loans between different branches or divisions 
      of a bank to optimize capital allocation.
    - **Australia (AU) Transfer:** If related to international banking, it might refer to fund transfers 
      involving Australia.
    """,

    "Closing Notes": """In commercial bank lending services, Closing Notes refer to the documented summary of 
    key details, terms, and conditions finalized at the closing of a loan transaction. These notes typically include:

    - **Confirmation of loan terms** (interest rate, repayment schedule, maturity date).
    - **Final conditions met before disbursement** (e.g., legal approvals, collateral requirements).
    - **Any last-minute changes or adjustments** agreed upon by the lender and borrower.
    - **A summary of compliance** with regulatory or internal bank policies.

    Closing notes serve as an internal reference for the bank and may also be shared with relevant stakeholders 
    to ensure all aspects of the loan closing are properly recorded and acknowledged.
    """,

    "Commitment Change": """In commercial bank lending services, Commitment Change refers to any modification 
    to the bank’s agreed-upon commitment to provide credit to a borrower. This change can involve an increase, 
    decrease, extension, or termination of the credit facility based on various factors such as the borrower’s 
    financial condition, regulatory requirements, or contractual agreements.

    Common types of commitment changes include:
    - **Increase in Commitment:** Expanding the credit facility due to borrower needs or improved creditworthiness.
    - **Reduction in Commitment:** Lowering the available credit due to risk reassessment or borrower request.
    - **Commitment Termination:** Ending the lending commitment, often due to repayment, default, or renegotiation.
    - **Extension or Renewal:** Extending the term of an existing credit commitment.

    These changes are typically documented through amendments to the loan agreement and may require approval 
    from both the borrower and the lender.
    """,

    "Fee Payment": """In commercial bank lending services, Fee Payment refers to the payment of charges 
    associated with a loan or credit facility. These fees can be one-time or recurring and are typically 
    outlined in the loan agreement.

    Common Types of Fee Payments in Lending:
    - **Origination Fee:** A fee charged for processing a new loan.
    - **Commitment Fee:** A charge for keeping a line of credit available to the borrower.
    - **Prepayment Fee:** A penalty for repaying a loan earlier than agreed.
    - **Late Payment Fee:** A charge for missing a scheduled loan payment.
    - **Annual or Maintenance Fee:** A recurring charge for keeping the loan facility active.

    Fee payments are typically scheduled along with loan payments or at specific intervals as defined in 
    the loan agreement.
    """,

    "Money Movement Inbound": """In commercial bank lending services, Money Movement Inbound refers to the 
    process of receiving funds into a bank account, typically related to loan payments, deposits, or transfers. 
    This can include:

    - **Loan Repayments:** Borrowers making scheduled or lump-sum payments toward their loans.
    - **Fund Transfers:** Inbound wire transfers, ACH payments, or checks deposited into an account.
    - **Collateral Deposits:** Funds received as part of loan security requirements.
    - **Fee Payments:** Borrowers paying required loan-related fees.

    Inbound money movement is tracked to ensure accurate application of funds to the appropriate accounts, 
    maintain compliance, and manage cash flow effectively.
    """,

    "Money Movement Outbound": """In commercial bank lending services, Money Movement Outbound refers to the 
    process of transferring funds out of a bank account, typically related to loan disbursements, payments, 
    or other financial transactions. This can include:

    - **Loan Disbursements:** Funds released to borrowers as part of an approved loan.
    - **Wire Transfers & ACH Payments:** Sending funds to third parties or external accounts.
    - **Interest & Fee Payments:** Payments made from a borrower's account to cover interest, service fees, 
      or other loan-related charges.
    - **Refunds or Adjustments:** Returning excess funds or making corrections to previous transactions.

    Banks closely monitor outbound money movement to ensure compliance, prevent fraud, and maintain proper 
    financial records.
    """
}


# Sub-Request Type Examples (for better classification)
SUB_REQUEST_TYPE_EXAMPLES = {
    "Adjustment": [],
    "AU Transfer": [],
    "Closing Notes": ["Reallocation Fees","Amendment Fees","Reallocation Principal"],
    "Commitment Change": ["Cashless Roll", "Decrease","Increase"],
    "Fee Payment": ["Ongoing Fee", "Letter of Credit Fee"],
    "Money Movement Inbound": ["Principal", "Interest","Principal and Interest","Principal and Interest and Fees"],
    "Money Movement Outbound": ["Timebound","Foreign Currency"]
}

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text() + "\n"
    except Exception as e:
        text = f"Error reading PDF: {e}"
    return text.strip()

# Function to extract text from DOCX
def extract_text_from_docx(docx_file):
    text = ""
    try:
        doc = Document(docx_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        text = f"Error reading DOCX: {e}"
    return text.strip()

# Function to extract text from EML (including attachments)

def extract_text_from_eml(eml_file):
    text = ""
    attachments = []
    try:
        msg = email.message_from_bytes(eml_file.read(), policy=policy.default)

        # Extract email body first (priority)
        if msg.is_multipart():
            for part in msg.iter_parts():
                if part.get_content_type() == "text/plain":
                    text += part.get_payload(decode=True).decode("utf-8", errors="ignore") + "\n"
                elif part.get_filename():  # Process attachments
                    attachments.append(part)
        else:
            text = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

        # If no email body content found, check attachments
        if not text and attachments:
            text = "Attachments extracted, no body content."

    except Exception as e:
        text = f"Error reading EML: {e}"
    return text.strip(), attachments

# Function to extract values based on configured fields

def extract_config_fields(text, source):
    extracted_data = {}
    patterns = {
        "Deal": r"(?:Deal|DealName):\s*([^\n]+)",
        "Amount": r"(?:Amount|Payment|loans totaling|transactions amount):\s*([^\n]+)",
        "Expiration Date": r"(?:Expiration Date|Maturity):\s*([\w\s,]+\d{4})"
    }

    for field, pattern in patterns.items():
        if RULES_CONFIG.get(field) == source:  # Only extract if the rule allows it
            match = re.search(pattern, text, re.IGNORECASE)
            extracted_data[field] = match.group(1).strip() if match else "Not Found"

    return extracted_data

     
def get_request_type_and_sub_type(text):
    if not text.strip():  # Ensure text is not empty
        return "Error", "Error", 0.0

    prompt = f"""Analyze the given content and classify it into a request type and sub-request type. 

    **Request Type Definitions:**
    {json.dumps(REQUEST_TYPE_DEFINITIONS, indent=2)}

    **Examples of Sub-Request Types:**
    {json.dumps(SUB_REQUEST_TYPE_EXAMPLES, indent=2)}

    **Instructions:**
    - Choose the most relevant request type based on the content.
    - Select an appropriate sub-request type based on the context.
    - Provide a confidence score between 0.0 and 1.0.

    **Expected JSON Output Format:**
    {{
      "request_type": "<Request Type>",
      "sub_request_type": "<Sub Request Type>",
      "confidence_score": <Confidence Score>
    }}

    **Content to analyze:**
    {text}
    """

    try:
        response = gemini_model.generate_content(prompt)
        
        if not response or not response.text.strip():
            print("Gemini returned an empty response")
            return "Error", "Error", 0.0
        
        result = response.text.strip()

        # Debugging: Print the raw response from Gemini
        print("Raw Gemini Response:", result)

        # Extract JSON block correctly
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            result = json_match.group(0)
        else:
            print("No valid JSON found in the response")
            return "Error", "Error", 0.0

        # Try parsing JSON
        parsed_result = json.loads(result)

        request_type = parsed_result.get("request_type", "Unknown")
        sub_request_type = parsed_result.get("sub_request_type", "Unknown")
        confidence_score = parsed_result.get("confidence_score", 0.0)

        return request_type, sub_request_type, confidence_score

    except json.JSONDecodeError:
        print("Error: Response is not valid JSON")
        return "Error", "Error", 0.0
    except Exception as e:
        print(f"Unexpected error in AI call: {e}")
        return "Error", "Error", 0.0
 
# Parse JSON response
        parsed_result = json.loads(result)

# Function to segment and identify requests
def segment_and_identify_requests(text):
    segments = text.split("\n\n")
    requests = []
    for segment in segments:
        if segment.strip():
            request_type, sub_request_type, confidence_score = get_request_type_and_sub_type(segment)
            requests.append({
                "request_type": request_type,
                "sub_request_type": sub_request_type,
                "confidence_score": confidence_score
            })

    # Remove duplicate requests
    unique_requests = []
    seen_requests = set()

    for request in requests:
        request_key = (request["request_type"], request["sub_request_type"])
        if request_key not in seen_requests:
            unique_requests.append(request)
            seen_requests.add(request_key)

    return unique_requests

# Function to check duplicate emails
def check_duplicate(text):
    email_hash = hashlib.md5(text.encode()).hexdigest()
    duplicate_reason = "Unique email."

    # Check for exact duplicate (already seen email hash)
    if email_hash in email_hashes:
        return True, "Duplicate email detected based on identical content."

    # Check for repeated replies (email thread duplication)
    reply_patterns = [
        r"On\s+\w{3,9},\s+\w{3,9}\s+\d{1,2},\s+\d{4}\s+at\s+\d{1,2}:\d{2}\s+(AM|PM),\s+.*wrote:",
        r"From:\s+.*\nSent:\s+.*\nTo:\s+.*\nSubject:\s+.*"
    ]
    if any(re.search(pattern, text, re.IGNORECASE) for pattern in reply_patterns):
        return True, "Duplicate email detected as a repeated reply in the same thread."

    # Check for email forward duplication
    forward_patterns = [
        r"Forwarded message",
        r"Begin forwarded message",
        r"From:\s+.*\nSent:\s+.*\nTo:\s+.*\nSubject:\s+.*"
    ]
    if any(re.search(pattern, text, re.IGNORECASE) for pattern in forward_patterns):
        return True, "Duplicate email detected as a forwarded message."

    # Store email hash to track seen messages
    email_hashes[email_hash] = True
    return False, duplicate_reason



@app.route("/process-file", methods=["POST"])
def process_file():
    print("Received request:", request.content_type)
    print("Request files:", request.files)

    if "file" not in request.files:
        print("No file found in request!")
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        print("File field is empty!")
        return jsonify({"error": "No file provided"}), 400

    print(f"File received: {file.filename}")

    file_extension = file.filename.split(".")[-1].lower()
    text = ""
    attachments = []

    # Extract text based on file type
    if file_extension == "pdf":
        text = extract_text_from_pdf(file)
    elif file_extension == "docx":
        text = extract_text_from_docx(file)
    elif file_extension == "eml":
        text, attachments = extract_text_from_eml(file)
    else:
        print("Unsupported file type!")
        return jsonify({"error": "Unsupported file type"}), 400

    if not text:
        print("No text extracted!")
        return jsonify({"error": "Could not extract text from file"}), 400

    # Extract configured fields from the primary document
    extracted_fields = extract_config_fields(text, "body")

    # Process attachments based on rules
    for attachment in attachments:
        attachment_text = ""
        filename = attachment.get_filename()
        if filename.endswith(".pdf"):
            attachment_text = extract_text_from_pdf(attachment)
        elif filename.endswith(".docx"):
            attachment_text = extract_text_from_docx(attachment)

        if attachment_text:
            attachment_extracted_fields = extract_config_fields(attachment_text, "attachment")
            for key, value in attachment_extracted_fields.items():
                if value != "Not Found":
                    extracted_fields[key] = value  # Override with attachment value if available

    # Check for duplicate emails
    is_duplicate, duplicate_reason = check_duplicate(text)

    # Identify unique requests
    unique_requests = segment_and_identify_requests(text)

    return jsonify({  # Ensure this return statement is correctly indented
        "extracted_fields": extracted_fields,
        "requests": unique_requests,
        "duplicate_flag": "Yes" if is_duplicate else "No",
        "duplicate_reason": duplicate_reason
    })

# Start Flask server
if __name__ == "__main__":
    app.run(debug=True)



# Start Flask server
if __name__ == "__main__":
    app.run(debug=True)


