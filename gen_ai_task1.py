'''
@Author:vijay kumar m n
@Date: 2024-11-21
@Last Modified by: vijay kumar m n
@Last Modified time: 2024-11-21 
@Title :summirazing the mails for given text file

'''
import google.generativeai as genai  # For Gemini API (Palm2)
import pandas as pd  # For handling CSV files
import os
from dotenv import load_dotenv

# Configure the Gemini API
def configure_gemini(api_key):
    try:
        print("Configuring Gemini API...")
        genai.configure(api_key=api_key)
        print("Gemini API configured successfully.")
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")

# Function to summarize the email body using the chat session
def summarize_email(body, chat_session):
    """
    Description:
        Summarizes the body of an email using the Gemini AI model.

    Parameters:
        body (str): The email body content.
        chat_session: The chat session with the Gemini model.

    Returns:
        str: Summarized email content.
    """
    try:
        # Send message to summarize the email body
        response = chat_session.send_message(f"Summarize the following email: {body}")
        return response.text
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return f"Error summarizing text: {e}"

def translate_email(text, chat_session, target_language="kannada"):  # Kannada as an example
    """
    Translates the given text to a specified language using the Gemini AI model.

    Parameters:
        text (str): The text to be translated.
        chat_session: The chat session with the Gemini model.
        target_language (str): The target language code (default is Kannada - 'kn').

    Returns:
        str: Translated text in the target language.
    """
    try:
        # Modify the prompt to get a clean, direct translation
        response = chat_session.send_message(f"Translate the following text to {target_language} (provide only the translation, no extra details): {text}")
        return response.text.strip()  # Strip any extra spaces or newlines
    except Exception as e:
        print(f"Error translating text: {e}")
        return f"Error translating text: {e}"

# Function to save the data to a CSV file
def save_to_csv(data, output_file):
    """
    Saves the processed data to a CSV file.
    """
    if not data:
        print("No data to save.")
        return
    try:
        print(f"Saving data to {output_file}...")
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Data saved to {output_file}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

# Function to read emails from a file
def read_emails(file_path):
    print(f"Reading emails from {file_path}...")
    emails = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            email = {}
            for line in file:
                line = line.strip()
                if line.startswith("From:"):
                    email['from'] = line.replace("From:", "").strip()
                elif line.startswith("To:"):
                    email['to'] = line.replace("To:", "").strip()
                elif line.startswith("Body:"):
                    email['body'] = line.replace("Body:", "").strip()
                elif line.lower() == "end":
                    if email:
                        emails.append(email)
                    email = {}
        print(f"Total {len(emails)} emails read.")
        return emails
    except Exception as e:
        print(f"Error reading emails: {e}")
        return []

# Function to process a single email
def process_email(email, chat_session):
    """
    Processes a single email: Summarizes and translates the content.
    """
    try:
        print(f"Processing email: From: {email['from']}, To: {email['to']}")

        # Summarize the email body using the chat session
        summary = summarize_email(email.get('body', 'No body text'), chat_session)

        # Translate the summary to the desired language (e.g., Chinese)
        translation = translate_email(summary, chat_session)

        # Return the processed data
        return {
            "From": email['from'],
            "To": email['to'],
            "Summary": summary,
            "Translated Summary": translation
        }
    except Exception as e:
        print(f"Error processing email: {e}")
        return {
            "From": email.get('from', 'Unknown'),
            "To": email.get('to', 'Unknown'),
            "Summary": "Error processing email",
            "Translated Summary": "Error processing email"
        }

# Main function to execute the workflow
def main():
    input_file = "emails.txt"
    output_file = "processed_emails.csv"
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')  # Replace with your actual Gemini API key

    # Configure Gemini API
    configure_gemini(api_key)

    # Create model configuration
    generation_config = {
            "temperature": 0.9,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
        }

    # Initialize chat session with the Gemini model
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
    chat_session = model.start_chat(history=[])

    # Read emails
    emails = read_emails(input_file)
    if not emails:
        print("No emails to process.")
        return

    # Process emails
    data = []
    for email in emails:
        processed_email = process_email(email, chat_session)
        data.append(processed_email)

    # Save to CSV
    save_to_csv(data, output_file)

if __name__ == "__main__":
    main()
