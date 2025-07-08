#!/usr/bin/env python3
"""
Command Line Interface for Book Writing AI Chatbot

A terminal-based interface for interacting with the AI chatbot.
Supports training the model on book files and interactive chat sessions.
"""

import os
import sys
import argparse
import logging
from typing import Optional
import json

from src.chatbot import BookWritingChatbot

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class BookWritingCLI:
    """Command line interface for the Book Writing AI Chatbot."""
    
    def __init__(self):
        self.chatbot = None
        self.model_path = "trained_model.json"
        
    def initialize_chatbot(self, model_path: Optional[str] = None):
        """Initialize the chatbot, optionally loading an existing model."""
        if model_path:
            self.model_path = model_path
            
        self.chatbot = BookWritingChatbot(model_path=self.model_path if os.path.exists(self.model_path) else None)
        
        if os.path.exists(self.model_path):
            print(f"✅ Loaded existing model from {self.model_path}")
        else:
            print("🆕 Initialized new chatbot (no existing model found)")
    
    def train_model(self, books_directory: str, save_path: Optional[str] = None):
        """Train the chatbot on books from a directory."""
        if not self.chatbot:
            self.initialize_chatbot()
        
        print(f"📚 Training model on books from: {books_directory}")
        print("⏳ This may take a few minutes...")
        
        try:
            save_path = save_path or self.model_path
            stats = self.chatbot.train_from_books(books_directory, save_model_path=save_path)
            
            print("\n✅ Training completed successfully!")
            print(f"📊 Training Statistics:")
            print(f"   - Books processed: {stats['num_books']}")
            print(f"   - Total sentences: {stats['total_sentences']:,}")
            print(f"   - Total words: {stats['total_words']:,}")
            print(f"   - Vocabulary size: {stats['vocabulary_size']:,}")
            print(f"   - Model saved to: {save_path}")
            
            if 'books' in stats:
                print("\n📖 Books processed:")
                for book in stats['books']:
                    print(f"   - {book['title']}: {book['sentences']} sentences, {book['words']} words")
            
        except Exception as e:
            print(f"❌ Training failed: {str(e)}")
            logger.error(f"Training error: {str(e)}")
    
    def create_sample_books(self, output_dir: str = "sample_books"):
        """Create sample books for testing."""
        if not self.chatbot:
            self.initialize_chatbot()
        
        print(f"📝 Creating sample books in: {output_dir}")
        
        try:
            # Create sample books and train
            stats = self.chatbot.train_from_books(output_dir, save_model_path=self.model_path)
            
            print("✅ Sample books created and model trained!")
            print(f"📊 Processed {stats['num_books']} sample books")
            print(f"💾 Model saved to: {self.model_path}")
            
        except Exception as e:
            print(f"❌ Failed to create sample books: {str(e)}")
            logger.error(f"Sample books error: {str(e)}")
    
    def interactive_chat(self):
        """Start an interactive chat session."""
        if not self.chatbot:
            self.initialize_chatbot()
        
        print("\n🤖 Book Writing AI Chatbot - Interactive Mode")
        print("=" * 50)
        print("Type 'quit', 'exit', or 'bye' to end the conversation")
        print("Type 'help' for available commands")
        print("Type 'status' to see model information")
        print("=" * 50)
        
        if not self.chatbot.model.is_trained:
            print("⚠️  Warning: Model is not trained. Responses will be basic.")
            print("   Use 'train <directory>' or 'sample' to train the model first.")
        
        print("\nAI: Hello! I'm your book writing assistant. How can I help you today?")
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\nAI: Goodbye! Happy writing! 📚✨")
                    break
                
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                elif user_input.lower() == 'status':
                    self.show_status()
                    continue
                
                elif user_input.lower().startswith('train '):
                    directory = user_input[6:].strip()
                    if directory:
                        self.train_model(directory)
                    else:
                        print("Please specify a directory: train <directory>")
                    continue
                
                elif user_input.lower() == 'sample':
                    self.create_sample_books()
                    continue
                
                elif user_input.lower() == 'clear':
                    self.chatbot.clear_conversation_history()
                    print("Conversation history cleared.")
                    continue
                
                elif user_input.lower() == 'save':
                    self.save_conversation()
                    continue
                
                # Get response from chatbot
                response = self.chatbot.chat(user_input)
                print(f"\nAI: {response}")
                
            except KeyboardInterrupt:
                print("\n\nAI: Goodbye! Happy writing! 📚✨")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")
                logger.error(f"Chat error: {str(e)}")
    
    def show_help(self):
        """Show available commands."""
        print("\n📚 Available Commands:")
        print("  help              - Show this help message")
        print("  status            - Show model training status and statistics")
        print("  train <directory> - Train model on .txt files in directory")
        print("  sample            - Create sample books and train model")
        print("  clear             - Clear conversation history")
        print("  save              - Save conversation to file")
        print("  quit/exit/bye     - End conversation")
        print("\n💡 Writing Assistant Features:")
        print("  - Ask me to continue text: 'Continue this: Once upon a time...'")
        print("  - Request story generation: 'Generate a story about adventure'")
        print("  - Get character ideas: 'Help me develop a character'")
        print("  - Plot suggestions: 'Suggest a plot for my mystery novel'")
        print("  - Writing style analysis: 'What writing style did you learn?'")
    
    def show_status(self):
        """Show model status and statistics."""
        if not self.chatbot:
            print("Chatbot not initialized.")
            return
        
        stats = self.chatbot.model.get_model_stats()
        text_stats = self.chatbot.text_processor.get_statistics()
        
        print("\n📊 Model Status:")
        print(f"  Trained: {'Yes' if stats['is_trained'] else 'No'}")
        print(f"  Vocabulary size: {stats['vocabulary_size']:,} words")
        print(f"  N-gram size: {stats['n_gram_size']}")
        print(f"  Total patterns: {stats['total_n_grams']:,}")
        
        if stats['most_common_words']:
            top_words = [word for word, count in stats['most_common_words'][:5]]
            print(f"  Top words: {', '.join(top_words)}")
        
        if text_stats:
            print(f"\n📚 Training Data:")
            print(f"  Books processed: {text_stats['num_books']}")
            print(f"  Total sentences: {text_stats['total_sentences']:,}")
            print(f"  Total words: {text_stats['total_words']:,}")
        
        conversation_count = len(self.chatbot.get_conversation_history())
        print(f"\n💬 Conversation: {conversation_count} messages")
    
    def save_conversation(self):
        """Save conversation history to a file."""
        if not self.chatbot:
            print("No chatbot initialized.")
            return
        
        history = self.chatbot.get_conversation_history()
        if not history:
            print("No conversation to save.")
            return
        
        filename = f"conversation_{len(history)}messages.json"
        try:
            self.chatbot.save_conversation(filename)
            print(f"💾 Conversation saved to: {filename}")
        except Exception as e:
            print(f"Failed to save conversation: {str(e)}")
    
    def single_response(self, message: str):
        """Get a single response without interactive mode."""
        if not self.chatbot:
            self.initialize_chatbot()
        
        response = self.chatbot.chat(message)
        return response

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Book Writing AI Chatbot - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Start interactive chat
  %(prog)s --train books/                     # Train on books in directory
  %(prog)s --sample                           # Create sample books and train
  %(prog)s --message "Help me write a story"  # Get single response
  %(prog)s --train books/ --interactive       # Train then start chat
        """
    )
    
    parser.add_argument(
        '--train', '-t',
        metavar='DIRECTORY',
        help='Train model on .txt book files in directory'
    )
    
    parser.add_argument(
        '--sample', '-s',
        action='store_true',
        help='Create sample books and train model'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Start interactive chat mode'
    )
    
    parser.add_argument(
        '--message', '-m',
        metavar='TEXT',
        help='Send a single message and get response'
    )
    
    parser.add_argument(
        '--model', '-M',
        metavar='PATH',
        help='Path to saved model file (default: trained_model.json)'
    )
    
    parser.add_argument(
        '--save-model', '-S',
        metavar='PATH',
        help='Path to save trained model (default: trained_model.json)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize CLI
    cli = BookWritingCLI()
    
    # Handle arguments
    if args.model:
        cli.model_path = args.model
    
    # Training operations
    if args.sample:
        cli.create_sample_books()
    
    if args.train:
        save_path = args.save_model or cli.model_path
        cli.train_model(args.train, save_path)
    
    # Chat operations
    if args.message:
        cli.initialize_chatbot()
        response = cli.single_response(args.message)
        print(f"AI: {response}")
    
    # Interactive mode (default if no other operations)
    if args.interactive or (not args.train and not args.sample and not args.message):
        cli.interactive_chat()

if __name__ == "__main__":
    main()