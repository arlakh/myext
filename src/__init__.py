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

from .text_processor import TextProcessor
from .simple_model import SimpleLanguageModel
from .chatbot import BookWritingChatbot

__version__ = "1.0.0"
__author__ = "AI Assistant"
__description__ = "AI Chatbot for Book Writing Assistance"

__all__ = ["TextProcessor", "SimpleLanguageModel", "BookWritingChatbot"]