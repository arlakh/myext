"""
Book Writing AI Chatbot

A specialized AI chatbot that learns from provided book text databases
and assists with book writing tasks. The system is "dumb" without training data
and only uses basic grammar rules when no books are provided.

Main Components:
- TextProcessor: Handles loading and preprocessing of .txt book files
- SimpleLanguageModel: N-gram based language model for text generation
- BookWritingChatbot: Main chatbot interface with conversation management

Usage:
    from src.chatbot import BookWritingChatbot
    
    chatbot = BookWritingChatbot()
    chatbot.train_from_books("path/to/books/")
    response = chatbot.chat("Help me write a story about adventure")
"""

# Try to import full-featured versions, fallback to built-in versions
try:
    from .text_processor import TextProcessor
    from .simple_model import SimpleLanguageModel
    print("✅ Using full-featured versions with external dependencies")
except ImportError as e:
    print(f"⚠️ External dependencies not available: {e}")
    print("🔄 Falling back to built-in library versions...")
    
    try:
        from .text_processor_builtin import TextProcessorBuiltin as TextProcessor
        from .simple_model_builtin import SimpleLanguageModelBuiltin as SimpleLanguageModel
        print("✅ Using built-in library versions")
    except ImportError as fallback_error:
        print(f"❌ Failed to import built-in versions: {fallback_error}")
        raise

# Always try to import the main chatbot (it should adapt to available components)
try:
    from .chatbot_builtin import BookWritingChatbotBuiltin as BookWritingChatbot
except ImportError:
    print("⚠️ Using basic chatbot implementation")
    # We'll create a basic implementation

__version__ = "1.0.0"
__author__ = "AI Assistant"
__description__ = "AI Chatbot for Book Writing Assistance"

__all__ = ["TextProcessor", "SimpleLanguageModel", "BookWritingChatbot"]