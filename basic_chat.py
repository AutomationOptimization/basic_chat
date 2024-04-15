from flask import Flask, request, jsonify, session, render_template
import requests
import uuid  # for generating unique IDs

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

def get_response(user_input, session_id, chat_history):
    url = "https://prod-122.westus.logic.azure.com:443/workflows/0332a9b984a8426aac7be2576dcf11b5/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=8lzS2TQrjrlYiv3-Z1PlQZ58A6vPSgpU_6-GxtAGF9Y"
    payload = {
        "user_input": user_input,
        "session_id": session_id,
        "chat_history": chat_history
    }
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            response_json = response.json()
            assistant_response = response_json.get('response', "I'm sorry, the server didn't provide a response.")
            return assistant_response
        else:
            return f"Error: Received status code {response.status_code}"
    except Exception as e:
        return f"An error occurred: {e}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('user_input')
    
    # Generate a unique ID if it doesn't exist
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    # Initialize chat history if it doesn't exist
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    # Add user's message to chat history
    session['chat_history'].append({"role": "user", "content": user_input})
    
    # Get assistant's response
    assistant_response = get_response(user_input, session['session_id'], session['chat_history'])
    
    # Make sure the assistant's response is not empty before adding it to chat history
    if assistant_response:
        session['chat_history'].append({"role": "assistant", "content": assistant_response})
        
    # Mark session as modified to make sure it gets saved
    session.modified = True
    
    return jsonify({'response': assistant_response})

if __name__ == '__main__':
    app.run(debug=True)