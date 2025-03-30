from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import requests
import markdown

app = Flask(__name__)

GEMINI_API_KEY = "AIzaSyDsDQtovzykV1GA8-AMimV7e09pqLAbmAE"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

user_profile = {
    "name": "Sum It",
    "goal": "Software Engineer",
    "messages_sent": 0
}
chat_history = []

@app.route("/index")
def index():
    return render_template('index.html')

# Route for the signup form
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        user_profile["name"] = request.form.get("full_name")
        user_profile["email"] = request.form.get("email")
        user_profile["state"] = request.form.get("state")
        user_profile["mobile"] = request.form.get("mobile")
        user_profile["boards_percentage"] = request.form.get("boards_percentage")
        user_profile["city"] = request.form.get("city")
        user_profile["dob"] = request.form.get("dob")
        user_profile["disability"] = request.form.get("disability")
        # Optionally set a career goal based on boards percentage (example logic)
        boards_percentage = float(user_profile["boards_percentage"])
        if boards_percentage >= 90:
            user_profile["goal"] = "Software Engineer"
        elif boards_percentage >= 80:
            user_profile["goal"] = "Data Scientist"
        else:
            user_profile["goal"] = "Career Exploration"
        # Redirect to the chat page after form submission
        return redirect(url_for("chat"))
    return render_template('signup.html', user_profile=user_profile)

# Function to generate AI responses using the Gemini API
def generate_response(message):

    if "resume tips" in message.lower():
        return "Here are some resume tips: Tailor your resume to the job, use action verbs, keep it concise (1 page), and highlight measurable achievements."
    elif "roadmap" in message.lower():
        return "Your career roadmap: 1. Complete relevant education, 2. Gain experience through internships, 3. Build a portfolio, 4. Network with professionals."

    # Add a system prompt to make the model act as a career advisor
    system_prompt = "You are a career advisor helping students with job advice. Respond with practical and concise career guidance."
    full_message = f"{system_prompt}\nUser: {message}"

    # Prepare the API request payload
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": full_message}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.9,
            "maxOutputTokens": 500
        }
    }

    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            json=payload,
            headers=headers
        )
        response.raise_for_status()  # Raise an error for bad status codes
        result = response.json()
        # Extract the generated text
        ai_response = result["candidates"][0]["content"]["parts"][0]["text"]
        # Convert Markdown to HTML
        ai_response_html = markdown.markdown(ai_response)
        return ai_response_html
    except requests.exceptions.RequestException as e:
        return f"Error: Could not generate response. {str(e)}"

# Route for the chat interface
@app.route("/", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        # the "Clear" button
        if "clear" in request.form:
            chat_history.clear()
            user_profile["messages_sent"] = 0
            return redirect(url_for("chat"))

        # Get the user’s message (from text input or buttons)
        user_message = request.form.get("message")
        if user_message:
            # Add user message to chat history (user input is plain text)
            chat_history.append({
                "sender": "user",
                "text": user_message,
                "time": datetime.now().strftime("%H:%M:%S")
            })
            user_profile["messages_sent"] += 1

            # Generate AI response (this will be HTML)
            ai_response = generate_response(user_message)
            chat_history.append({
                "sender": "ai",
                "text": ai_response,
                "time": datetime.now().strftime("%H:%M:%S")
            })
    return render_template('aichat.html', user_profile=user_profile, chat_history=chat_history)

if __name__ == "__main__":
    app.run(debug=True)