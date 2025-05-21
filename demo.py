from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
from flask_cors import CORS
CORS(app)
# Gemini API Key (make sure it's still valid)
GEMINI_API_KEY = "AIzaSyDWKfO3SfxcFHAjCmN71P1M5x1r8vgixwM"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat()

# UPDATED scraper
def scrape_website(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return f"Failed to retrieve website data. Status code: {response.status_code}"
        
        soup = BeautifulSoup(response.content, 'html.parser')
        headlines = soup.select('h1, h2, h3')  # Grab h1 to h3 headlines

        filtered = [h.get_text(strip=True) for h in headlines if h.get_text(strip=True)]
        if not filtered:
            return "Sorry, I couldn't find any headlines."

        return "\n".join(filtered[:5])  # Top 5 headlines

    except Exception as e:
        return f"Scraping error: {str(e)}"

def chatbot_reply(message):
    news_keywords = ["news", "latest", "headlines", "today", "breaking", "update"]
    if any(word in message.lower() for word in news_keywords):
        return scrape_website("https://www.bbc.com/news")  # or use Times of India
    else:
        return chat.send_message(message).text

@app.route('/')
def home():
    return "Flask chatbot server is running. Use POST /chat endpoint to talk."

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'error': 'Message is required'}), 400
    reply = chatbot_reply(user_input)
    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
