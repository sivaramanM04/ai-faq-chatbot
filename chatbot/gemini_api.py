import google.generativeai as genai

genai.configure(api_key="YOUR_GEMINI_API_KEY")

model = genai.GenerativeModel("gemini-2.5-flash")

def get_gemini_response(user_message):

    response = model.generate_content(user_message)

    return response.text