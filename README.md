# 🚀 Project Name AIMarkTech

## 📌 Table of Contents
• Project Overview
• Key Features and Functionalities
    ◦ AI-Powered Loan Servicing Request Classification
    ◦ Confidence Scoring for AI Predictions
    ◦ Duplicate Email Detection
    ◦ Context-Based Data Extraction
    ◦ Handling Multi-Request with Primary Intent Detection
    ◦ Priority-Based Extraction

• How to Run the Project
• Testing and Results
• Demo

## 🎯 Introduction
This project leverages generative AI, specifically Google Gemini as the LLM model, to analyze emails and their attachments. It classifies the loan servicing type and sub-request type while providing a confidence score for each prediction. Built using Python, the system automates the classification of service requests, improving efficiency and accuracy in loan servicing operations.
Team Name: AIMarkTech
Git Repo: https://github.com/ewfx/gaied-ai-mark-tech/
Key Features and Functionalities of the Project

1.AI-Powered Loan Servicing Request and Sub request Classification
●Reads emails (EML format) and extracts both the email body and attachments (PDF, DOCX) and classifies loan servicing requests. Tools supports following file format as input: .eml, pdf and .docx
●Utilizes Google Gemini (LLM) to determine the loan servicing request type and sub-request type.
●Identify the sender intent for email sending.

●Defines several loan servicing types such as:

○Adjustment

○AU Transfer

○Closing Notes

○Commitment Change

○Fee Payment

○Money Movement (Inbound/Outbound)

Configuration Table for Request type and sub request types:
Request Type	Sub Request Type
 Adjustment	 
 AU Transfer	 
 Closing Notes 	 Reallocation Fees,Amendment Fees,Reallocation Principal
 Commitment Change 	 Cashless Roll, Decrease,Increase
 Fee Payment	 Ongoing Fee, Letter of Credit Fee
 Money Movement Inbound 	 Principal, Interest,Principal and Interest,Principal and Interest and Fees
 Money Movement Outbound	 Time bound,Foreign Currency



●Uses detailed instructions and examples to guide the AI model for accurate classification.


2.Confidence Scoring for AI Predictions
●Each classification includes a confidence score (0.0 - 1.0) to indicate AI certainty.

●Helps in determining whether human intervention is needed for low-confidence classifications.

3.Duplicate Email Detection
●Uses MD5 hashing to track processed emails and prevent duplicate processing.
●If an email has already been processed, it returns a duplicate flag.
●If an email is forwarded in same thread or Email is replied multiple time in same thread then, it provides duplicate flag.
●Duplicate reason provides the reason for duplication along with flag

4.Context Based data Extraction


●Context based data extraction from email and attachment based on configured fields.
●Extracting value of Deal, Amount and Expiration date from email and attachment. These fields are configured fields and it read the value from email and attachment. It first read the value from email and post that it look value from attachments. This fields are configurable. We can change the list of fields based on the requirement.

5.Handling multi request with primary intent detection:
     
●Project supports complex cases where single email can contain multiple request types and It creates multiple request type. Project supports multiple request type identification in single email. It identify the intent ask of sender and identify the request type. 
●Primary request identification which represent sender’s main intent even when the email discusses the multiple topic.

6.Priority based Extraction

●Project supports customization rule such as prioritizing emails content over documents.
●It supports extracting value from email content or attachments. Configuration is provided to extract value at fields level through email content or Attachments.

## 🎥 Demo
🔗 [Live Demo](#)  Demo Videois uploaded in Artitifacts/Demo/ 
📹 [Video Demo](#) (if applicable)  
🖼️ Screenshots:

![Screenshot 1](link-to-image)

## 💡 Inspiration
We are problem solver. We find this problemstatment very intresting. This solution will really help bank.
## ⚙️ What It Does
Key features and functionalities of your project.
Key Features and Functionalities of the Project

1.AI-Powered Loan Servicing Request and Sub request Classification
●Reads emails (EML format) and extracts both the email body and attachments (PDF, DOCX) and classifies loan servicing requests. Tools supports following file format as input: .eml, pdf and .docx
●Utilizes Google Gemini (LLM) to determine the loan servicing request type and sub-request type.
●Identify the sender intent for email sending.

●Defines several loan servicing types such as:

○Adjustment

○AU Transfer

○Closing Notes

○Commitment Change

○Fee Payment

○Money Movement (Inbound/Outbound)

Configuration Table for Request type and sub request types:
Request Type	Sub Request Type
 Adjustment	 
 AU Transfer	 
 Closing Notes 	 Reallocation Fees,Amendment Fees,Reallocation Principal
 Commitment Change 	 Cashless Roll, Decrease,Increase
 Fee Payment	 Ongoing Fee, Letter of Credit Fee
 Money Movement Inbound 	 Principal, Interest,Principal and Interest,Principal and Interest and Fees
 Money Movement Outbound	 Time bound,Foreign Currency



●Uses detailed instructions and examples to guide the AI model for accurate classification.


2.Confidence Scoring for AI Predictions
●Each classification includes a confidence score (0.0 - 1.0) to indicate AI certainty.

●Helps in determining whether human intervention is needed for low-confidence classifications.

3.Duplicate Email Detection
●Uses MD5 hashing to track processed emails and prevent duplicate processing.
●If an email has already been processed, it returns a duplicate flag.
●If an email is forwarded in same thread or Email is replied multiple time in same thread then, it provides duplicate flag.
●Duplicate reason provides the reason for duplication along with flag

4.Context Based data Extraction


●Context based data extraction from email and attachment based on configured fields.
●Extracting value of Deal, Amount and Expiration date from email and attachment. These fields are configured fields and it read the value from email and attachment. It first read the value from email and post that it look value from attachments. This fields are configurable. We can change the list of fields based on the requirement.

5.Handling multi request with primary intent detection:
     
●Project supports complex cases where single email can contain multiple request types and It creates multiple request type. Project supports multiple request type identification in single email. It identify the intent ask of sender and identify the request type. 
●Primary request identification which represent sender’s main intent even when the email discusses the multiple topic.

6.Priority based Extraction

●Project supports customization rule such as prioritizing emails content over documents.
●It supports extracting value from email content or attachments. Configuration is provided to extract value at fields level through email content or Attachments.


## 🛠️ How We Built It
We have used python code, flusk server, Google gemini LLM model and various free liberarey to build this project.

## 🚧 Challenges We Faced
Getting output in required format was challenging and integrating API with LLM Model was challenging and almost 6 requirments are asked in hackathon use case so building all in required time frame was challenging. 

## 🏃 How to Run
1. Clone the repository  
  Download or clone the project to your local system using:
  git clone https://github.com/ewfx/gaied-ai-mark-tech cd gaied-ai-mark-tech
  d gaied-ai-mark-tech
  
3. Install dependencies  
   pip install openai google-generativeai flask python-docx pymupdf
  
3. Run the project  
  python toolcode.py
   

## 🏗️ Tech Stack
- 🔹 Frontend: Python
- 🔹 Backend: API
- 🔹 Database:
- 🔹 Other: OpenAI API, Google Gemini LLM Model free version, Flusk server, Postman free desktop App for API testing

## 👥 Team
- **Harshit Gupta** - [GitHub](https://github.com/H4R5H1T-007/) | [LinkedIn](https://www.linkedin.com/in/harshit-gupta-8a7b621a4/)
- **Yogendra Rajput**- [GitHub ](https://github.com/yogirajput86)
- **Teammate 2** - [GitHub](#) | [LinkedIn](#)
