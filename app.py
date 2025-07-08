#!/usr/bin/env python3
"""
Flask Web Application for Book Writing AI Chatbot

Provides a web interface for interacting with the AI chatbot.
Users can train the model on book files and chat with the AI for writing assistance.
"""

import os
import json
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import threading

from src.chatbot import BookWritingChatbot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global chatbot instance
chatbot = None
training_status = {
    'is_training': False,
    'status': 'ready',
    'message': 'Ready to train or chat',
    'progress': 0
}

def create_template_files():
    """Create HTML template files for the web interface."""
    templates_dir = "templates"
    static_dir = "static"
    
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)
    
    # Create main HTML template
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Book Writing AI Chatbot</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 1200px;
            height: 80vh;
            display: flex;
            overflow: hidden;
        }
        
        .sidebar {
            width: 300px;
            background: #f8f9fa;
            padding: 30px;
            border-right: 1px solid #e9ecef;
            display: flex;
            flex-direction: column;
        }
        
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: #6c757d;
            color: white;
            padding: 20px 30px;
            text-align: center;
        }
        
        .chat-container {
            flex: 1;
            padding: 30px;
            display: flex;
            flex-direction: column;
        }
        
        .messages {
            flex: 1;
            overflow-y: auto;
            margin-bottom: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 10px;
            max-width: 80%;
            word-wrap: break-word;
        }
        
        .user-message {
            background: #007bff;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        
        .bot-message {
            background: #e9ecef;
            color: #333;
            margin-right: auto;
        }
        
        .input-container {
            display: flex;
            gap: 10px;
        }
        
        .message-input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .message-input:focus {
            border-color: #007bff;
        }
        
        .send-button {
            padding: 12px 24px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }
        
        .send-button:hover {
            background: #0056b3;
        }
        
        .send-button:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }
        
        .train-section {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #e9ecef;
        }
        
        .train-button {
            width: 100%;
            padding: 12px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
            transition: background 0.3s;
        }
        
        .train-button:hover {
            background: #218838;
        }
        
        .train-button:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }
        
        .status {
            margin-top: 15px;
            padding: 10px;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .status.info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        .model-info {
            background: white;
            border-radius: 10px;
            padding: 15px;
            border: 1px solid #e9ecef;
            font-size: 14px;
        }
        
        .model-info h3 {
            margin-bottom: 10px;
            color: #333;
        }
        
        .model-info p {
            margin-bottom: 5px;
            color: #666;
        }
        
        h1 {
            margin: 0;
            font-size: 24px;
        }
        
        h2 {
            margin-bottom: 15px;
            color: #333;
            font-size: 18px;
        }
        
        .file-input {
            margin-bottom: 10px;
        }
        
        .file-input input[type="file"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #3498db;
            border-radius: 50%;
            animation: spin 2s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <div class="train-section">
                <h2>Train Model</h2>
                <div class="file-input">
                    <input type="file" id="bookFiles" multiple accept=".txt" webkitdirectory>
                    <p style="font-size: 12px; color: #666; margin-top: 5px;">
                        Select a folder containing .txt book files
                    </p>
                </div>
                <button class="train-button" onclick="trainModel()">Train on Books</button>
                <button class="train-button" onclick="createSampleBooks()" style="background: #17a2b8;">
                    Create Sample Books
                </button>
                <div id="training-status" class="status info" style="display: none;">
                    Ready to train
                </div>
            </div>
            
            <div class="model-info">
                <h3>Model Status</h3>
                <div id="model-status">
                    <p>Status: <span id="model-trained">Not trained</span></p>
                    <p>Vocabulary: <span id="vocab-size">0</span> words</p>
                    <p>N-grams: <span id="ngram-count">0</span></p>
                </div>
                <button onclick="getModelInfo()" style="margin-top: 10px; padding: 5px 10px; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    Refresh Info
                </button>
            </div>
        </div>
        
        <div class="main-content">
            <div class="header">
                <h1>📚 Book Writing AI Chatbot</h1>
                <p>Upload books to train the AI, then chat for writing assistance</p>
            </div>
            
            <div class="chat-container">
                <div class="messages" id="messages">
                    <div class="message bot-message">
                        <strong>AI Assistant:</strong> Hello! I'm a book writing AI that learns from your provided text databases. 
                        Upload some .txt book files to train me, then I can help you with writing tasks like story generation, 
                        character development, plot ideas, and text completion. Without training data, I only have basic grammar knowledge.
                    </div>
                </div>
                
                <div class="input-container">
                    <input type="text" class="message-input" id="messageInput" placeholder="Type your message..." onkeypress="handleKeyPress(event)">
                    <button class="send-button" onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let isTraining = false;
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message to chat
            addMessage(message, 'user');
            input.value = '';
            
            // Disable send button while processing
            const sendButton = document.querySelector('.send-button');
            sendButton.disabled = true;
            sendButton.innerHTML = '<div class="loading"></div>';
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    addMessage(data.response, 'bot');
                } else {
                    addMessage('Error: ' + data.error, 'bot');
                }
            } catch (error) {
                addMessage('Connection error. Please try again.', 'bot');
            }
            
            // Re-enable send button
            sendButton.disabled = false;
            sendButton.innerHTML = 'Send';
        }
        
        function addMessage(text, sender) {
            const messages = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            
            if (sender === 'bot') {
                messageDiv.innerHTML = '<strong>AI Assistant:</strong> ' + text.replace(/\\n/g, '<br>');
            } else {
                messageDiv.innerHTML = '<strong>You:</strong> ' + text;
            }
            
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        }
        
        async function trainModel() {
            if (isTraining) return;
            
            const files = document.getElementById('bookFiles').files;
            if (files.length === 0) {
                alert('Please select a folder containing .txt book files');
                return;
            }
            
            isTraining = true;
            const button = document.querySelector('.train-button');
            const status = document.getElementById('training-status');
            
            button.disabled = true;
            button.innerHTML = '<div class="loading"></div> Training...';
            status.style.display = 'block';
            status.className = 'status info';
            status.innerHTML = 'Uploading files and training model...';
            
            try {
                const formData = new FormData();
                for (let i = 0; i < files.length; i++) {
                    formData.append('books', files[i]);
                }
                
                const response = await fetch('/train', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    status.className = 'status success';
                    status.innerHTML = `Training completed! Processed ${data.stats.num_books} books with ${data.stats.total_sentences} sentences.`;
                    addMessage('Training completed! I can now help you with writing based on the books you provided.', 'bot');
                    getModelInfo();
                } else {
                    status.className = 'status error';
                    status.innerHTML = 'Training failed: ' + data.error;
                }
            } catch (error) {
                status.className = 'status error';
                status.innerHTML = 'Training failed: Connection error';
            }
            
            isTraining = false;
            button.disabled = false;
            button.innerHTML = 'Train on Books';
        }
        
        async function createSampleBooks() {
            if (isTraining) return;
            
            isTraining = true;
            const button = event.target;
            const status = document.getElementById('training-status');
            
            button.disabled = true;
            button.innerHTML = '<div class="loading"></div> Creating...';
            status.style.display = 'block';
            status.className = 'status info';
            status.innerHTML = 'Creating sample books and training...';
            
            try {
                const response = await fetch('/create_sample_books', {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    status.className = 'status success';
                    status.innerHTML = `Sample books created and training completed! Processed ${data.stats.num_books} books.`;
                    addMessage('I\\'ve been trained on sample books and am ready to help with your writing!', 'bot');
                    getModelInfo();
                } else {
                    status.className = 'status error';
                    status.innerHTML = 'Failed to create sample books: ' + data.error;
                }
            } catch (error) {
                status.className = 'status error';
                status.innerHTML = 'Failed: Connection error';
            }
            
            isTraining = false;
            button.disabled = false;
            button.innerHTML = 'Create Sample Books';
        }
        
        async function getModelInfo() {
            try {
                const response = await fetch('/model_info');
                const data = await response.json();
                
                if (data.success) {
                    const info = data.info;
                    document.getElementById('model-trained').textContent = info.is_trained ? 'Trained' : 'Not trained';
                    document.getElementById('vocab-size').textContent = info.vocabulary_size.toLocaleString();
                    document.getElementById('ngram-count').textContent = info.total_n_grams.toLocaleString();
                }
            } catch (error) {
                console.error('Failed to get model info:', error);
            }
        }
        
        // Load model info on page load
        window.onload = function() {
            getModelInfo();
        };
    </script>
</body>
</html>"""
    
    with open(os.path.join(templates_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_template)

# Initialize chatbot
def init_chatbot():
    global chatbot
    chatbot = BookWritingChatbot()
    logger.info("Chatbot initialized")

@app.route('/')
def index():
    """Serve the main web interface."""
    create_template_files()  # Ensure templates exist
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages from the web interface."""
    global chatbot
    
    if not chatbot:
        return jsonify({
            'success': False,
            'error': 'Chatbot not initialized'
        })
    
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'No message provided'
            })
        
        # Get response from chatbot
        response = chatbot.chat(user_message)
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/train', methods=['POST'])
def train():
    """Handle model training from uploaded files."""
    global chatbot, training_status
    
    if not chatbot:
        return jsonify({
            'success': False,
            'error': 'Chatbot not initialized'
        })
    
    if training_status['is_training']:
        return jsonify({
            'success': False,
            'error': 'Training already in progress'
        })
    
    try:
        # Get uploaded files
        uploaded_files = request.files.getlist('books')
        
        if not uploaded_files or len(uploaded_files) == 0:
            return jsonify({
                'success': False,
                'error': 'No files uploaded'
            })
        
        # Create temporary directory for uploaded books
        temp_dir = 'temp_books'
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save uploaded files
        txt_files = []
        for file in uploaded_files:
            if file.filename.endswith('.txt'):
                filepath = os.path.join(temp_dir, file.filename)
                file.save(filepath)
                txt_files.append(filepath)
        
        if not txt_files:
            return jsonify({
                'success': False,
                'error': 'No .txt files found in upload'
            })
        
        # Start training
        training_status['is_training'] = True
        training_status['status'] = 'training'
        training_status['message'] = 'Training model...'
        
        # Train the model
        stats = chatbot.train_from_books(temp_dir, save_model_path='trained_model.json')
        
        # Clean up temporary files
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        training_status['is_training'] = False
        training_status['status'] = 'completed'
        training_status['message'] = 'Training completed successfully'
        
        return jsonify({
            'success': True,
            'stats': stats,
            'message': 'Model trained successfully'
        })
        
    except Exception as e:
        training_status['is_training'] = False
        training_status['status'] = 'error'
        training_status['message'] = str(e)
        
        logger.error(f"Training error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/create_sample_books', methods=['POST'])
def create_sample_books():
    """Create sample books and train the model."""
    global chatbot, training_status
    
    if not chatbot:
        return jsonify({
            'success': False,
            'error': 'Chatbot not initialized'
        })
    
    try:
        training_status['is_training'] = True
        training_status['status'] = 'creating'
        training_status['message'] = 'Creating sample books...'
        
        # Train on sample books (will create them automatically)
        stats = chatbot.train_from_books('sample_books', save_model_path='trained_model.json')
        
        training_status['is_training'] = False
        training_status['status'] = 'completed'
        training_status['message'] = 'Sample books created and training completed'
        
        return jsonify({
            'success': True,
            'stats': stats,
            'message': 'Sample books created and model trained successfully'
        })
        
    except Exception as e:
        training_status['is_training'] = False
        training_status['status'] = 'error'
        training_status['message'] = str(e)
        
        logger.error(f"Sample books creation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/model_info')
def model_info():
    """Get information about the current model."""
    global chatbot
    
    if not chatbot:
        return jsonify({
            'success': False,
            'error': 'Chatbot not initialized'
        })
    
    try:
        info = chatbot.model.get_model_stats()
        return jsonify({
            'success': True,
            'info': info
        })
        
    except Exception as e:
        logger.error(f"Model info error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/training_status')
def get_training_status():
    """Get the current training status."""
    return jsonify(training_status)

if __name__ == '__main__':
    init_chatbot()
    
    # Create templates directory and files if they don't exist
    create_template_files()
    
    print("🚀 Starting Book Writing AI Chatbot Web Server...")
    print("📚 Upload .txt book files to train the AI")
    print("💬 Chat with the AI for writing assistance")
    print("🌐 Access the application at: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)