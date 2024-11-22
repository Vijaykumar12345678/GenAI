
'''
@Author:vijay kumar m n
@Date: 2024-11-22
@Last Modified by: vijay kumar m n
@Last Modified time: 2024-11-22 
@Title :Check the reviews positive or negitive

'''
import google.generativeai as genai  # For Gemini API (Palm2)
import pandas as pd  # For handling CSV files
from dotenv import load_dotenv
import os

def configure_gemini(api_key):
    """
    Configures the Gemini API with the provided API key.

    Args:
        api_key (str): Your Gemini API key.
    """
    try:
        print("Configuring Gemini API...")
        genai.configure(api_key=api_key)
        print("Gemini API configured successfully.")
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")


def read_reviews(file_path):
    """
    Reads reviews from a text file and extracts Product and Review fields.

    Args:
        file_path (str): Path to the file containing product reviews.

    Returns:
        list of dict: A list of dictionaries with keys 'Product' and 'Review'.
    """
    reviews = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            review_data = {}
            for line in file:
                line = line.strip()
                if line.startswith("Product:"):
                    review_data["Product"] = line.replace("Product:", "").strip()
                elif line.startswith("Review:"):
                    review_data["Review"] = line.replace("Review:", "").strip()
                elif line == "END":
                    if review_data:
                        reviews.append(review_data)
                        review_data = {}
    except Exception as e:
        print(f"Error reading reviews: {e}")
    return reviews


def analyze_review(review, chat_session):
    """
    Analyzes the review to determine the guessed product, sentiment, and generates a reply.

    Args:
        review (str): The product review text.
        chat_session: An initialized chat session with the Gemini API.

    Returns:
        tuple: A tuple containing guessed product (str), sentiment (str), and reply (str).
    """
    try:
        # Guess the product name
        guessed_product_response = chat_session.send_message(
            f"Guess the product category or name for this review: {review}"
        )
        guessed_product = guessed_product_response.text.strip()

        # Perform sentiment analysis
        sentiment_response = chat_session.send_message(
            f"Categorize the sentiment of this review as Positive, Negative, or Neutral: {review}"
        )
        sentiment = sentiment_response.text.strip()

        # Generate a reply based on sentiment
        reply_response = chat_session.send_message(
            f"Write a 30-word reply to this review. The sentiment is {sentiment}: {review}"
        )
        reply = reply_response.text.strip()

        return guessed_product, sentiment, reply
    except Exception as e:
        return "Error", "Error", f"Error generating reply: {e}"


def save_to_csv(data, output_file):
    """
    Saves the processed data to a CSV file.

    Args:
        data (list of dict): The processed data containing product, review, guessed product, sentiment, and reply.
        output_file (str): The path to the output CSV file.
    """
    try:
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Data saved to {output_file}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")


def main():
    # File paths
    input_file = "reviews.txt"
    output_file = "processed_reviews.csv"
    load_dotenv()
    # Your Gemini API key (replace with your actual key)
    api_key =os.getenv('GEMINI_API_KEY')

    # Configure Gemini API
    configure_gemini(api_key)

    # Create model configuration
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "max_output_tokens": 200,
    }

    # Initialize chat session with the Gemini model
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
    chat_session = model.start_chat(history=[])

    # Read reviews from file
    reviews = read_reviews(input_file)
    if not reviews:
        print("No reviews found. Check the file format and content.")
        return

    # Process reviews
    data = []
    for review in reviews:
        print(f"Processing review for product: {review['Product']}")
        guessed_product, sentiment, reply = analyze_review(review["Review"], chat_session)
        data.append({
            "Original Product": review["Product"],
            "Guessed Product": guessed_product,
            "Review": review["Review"],
            "Sentiment": sentiment,
            "Reply": reply,
        })

    # Save results to CSV
    save_to_csv(data, output_file)


if __name__ == "__main__":
    main()
