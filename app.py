import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from dotenv import load_dotenv
from utils import log_message, format_response, get_current_datetime
from config import BOT_NAME, BOT_VERSION, DEBUG_MODE

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Store conversation history
conversation_history = {}

@app.route('/', methods=['GET'])
def index():
    """Root endpoint - returns API information"""
    return jsonify({
        'name': BOT_NAME,
        'version': BOT_VERSION,
        'status': 'running',
        'timestamp': get_current_datetime()
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint - accepts user message and returns AI response
    Expected JSON: {"message": "user message"}
    """
    try:
        data = request.json
        user_message = data.get('message')
        user_id = data.get('user_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Log the incoming message
        log_message(f"User {user_id}: {user_message}")
        
        # Initialize conversation history for this user if needed
        if user_id not in conversation_history:
            conversation_history[user_id] = []
        
        # Add user message to history
        conversation_history[user_id].append({
            'role': 'user',
            'content': user_message
        })
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation_history[user_id],
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract assistant message
        assistant_message = response['choices'][0]['message']['content']
        
        # Add assistant message to history
        conversation_history[user_id].append({
            'role': 'assistant',
            'content': assistant_message
        })
        
        # Log the response
        log_message(f"ALEX: {assistant_message}")
        
        return jsonify({
            'response': assistant_message,
            'user_id': user_id,
            'timestamp': get_current_datetime(),
            'bot_name': BOT_NAME
        })
    
    except openai.error.AuthenticationError:
        error_msg = "Authentication failed. Please check your OpenAI API key."
        log_message(f"Error: {error_msg}")
        return jsonify({'error': error_msg}), 401
    
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        log_message(f"Error: {error_msg}")
        return jsonify({'error': error_msg}), 500

@app.route('/api/history/<user_id>', methods=['GET'])
def get_history(user_id):
    """Retrieve conversation history for a specific user"""
    if user_id not in conversation_history:
        return jsonify({'message': 'No conversation history found'}), 404
    
    return jsonify({
        'user_id': user_id,
        'history': conversation_history[user_id],
        'timestamp': get_current_datetime()
    })

@app.route('/api/clear/<user_id>', methods=['POST'])
def clear_history(user_id):
    """Clear conversation history for a specific user"""
    if user_id in conversation_history:
        conversation_history[user_id] = []
        return jsonify({'message': f'History cleared for user {user_id}'}), 200
    
    return jsonify({'message': 'No history found for this user'}), 404

@app.route('/api/status', methods=['GET'])
def status():
    """Check API status"""
    return jsonify({
        'status': 'operational',
        'bot_name': BOT_NAME,
        'version': BOT_VERSION,
        'timestamp': get_current_datetime()
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    log_message(f"Starting {BOT_NAME} v{BOT_VERSION}")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=DEBUG_MODE
    )