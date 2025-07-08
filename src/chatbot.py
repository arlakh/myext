import os
import json
import logging
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from .text_processor import TextProcessor
from .simple_model import SimpleLanguageModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BookWritingChatbot:
    """
    AI Chatbot specialized for book writing assistance.
    Learns from provided book text databases and helps with writing tasks.
    """
    
    def __init__(self, model_path: Optional[str] = None, n_gram_size: int = 3):
        self.text_processor = TextProcessor()
        self.model = SimpleLanguageModel(n_gram_size=n_gram_size)
        self.conversation_history = []
        self.writing_context = {
            'current_genre': None,
            'current_style': None,
            'characters': [],
            'plot_points': [],
            'writing_goal': None
        }
        
        # Load existing model if provided
        if model_path and os.path.exists(model_path):
            try:
                self.model.load_model(model_path)
                logger.info("Loaded existing model")
            except Exception as e:
                logger.error(f"Failed to load model: {str(e)}")
    
    def train_from_books(self, books_directory: str, save_model_path: Optional[str] = None) -> Dict:
        """
        Train the chatbot on books from a directory.
        
        Args:
            books_directory: Path to directory containing .txt book files
            save_model_path: Optional path to save the trained model
            
        Returns:
            Training statistics
        """
        logger.info(f"Training chatbot from books in: {books_directory}")
        
        # Check if directory exists, create sample books if not
        if not os.path.exists(books_directory) or not os.listdir(books_directory):
            logger.warning(f"Directory {books_directory} is empty or doesn't exist. Creating sample books...")
            books_directory = self.text_processor.create_sample_books(books_directory)
        
        # Load and process books
        books_data = self.text_processor.load_books_from_directory(books_directory)
        
        if not books_data:
            raise ValueError(f"No valid books found in {books_directory}")
        
        # Get training sentences
        training_sentences = self.text_processor.get_training_data()
        
        if not training_sentences:
            raise ValueError("No training sentences extracted from books")
        
        # Train the model
        self.model.train(training_sentences)
        
        # Save model if path provided
        if save_model_path:
            self.model.save_model(save_model_path)
        
        # Get and return statistics
        stats = self.text_processor.get_statistics()
        model_stats = self.model.get_model_stats()
        
        combined_stats = {
            **stats,
            'model_stats': model_stats,
            'training_completed': True,
            'training_time': datetime.now().isoformat()
        }
        
        logger.info("Training completed successfully")
        return combined_stats
    
    def chat(self, user_input: str) -> str:
        """
        Main chat interface for interacting with the user.
        
        Args:
            user_input: User's message/question
            
        Returns:
            Chatbot's response
        """
        # Add to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_input,
            'bot': None
        })
        
        # Parse user intent and generate response
        intent = self._parse_user_intent(user_input)
        response = self._generate_response(user_input, intent)
        
        # Update conversation history with response
        self.conversation_history[-1]['bot'] = response
        
        return response
    
    def _parse_user_intent(self, user_input: str) -> Dict:
        """Parse user input to understand their intent."""
        user_lower = user_input.lower()
        
        intent = {
            'type': 'general',
            'action': None,
            'parameters': {}
        }
        
        # Writing assistance requests
        if any(phrase in user_lower for phrase in ['write', 'continue', 'help me write', 'complete']):
            intent['type'] = 'writing_assistance'
            
            if 'continue' in user_lower or 'complete' in user_lower:
                intent['action'] = 'continue_text'
            elif 'character' in user_lower:
                intent['action'] = 'character_development'
            elif 'plot' in user_lower:
                intent['action'] = 'plot_development'
            elif 'dialogue' in user_lower:
                intent['action'] = 'dialogue_writing'
            else:
                intent['action'] = 'general_writing'
        
        # Text generation requests
        elif any(phrase in user_lower for phrase in ['generate', 'create', 'start']):
            intent['type'] = 'generation'
            
            if 'story' in user_lower or 'tale' in user_lower:
                intent['action'] = 'story_generation'
            elif 'chapter' in user_lower:
                intent['action'] = 'chapter_generation'
            elif 'paragraph' in user_lower:
                intent['action'] = 'paragraph_generation'
            else:
                intent['action'] = 'text_generation'
        
        # Style and genre analysis
        elif any(phrase in user_lower for phrase in ['style', 'genre', 'like', 'similar to']):
            intent['type'] = 'style_analysis'
            intent['action'] = 'analyze_style'
        
        # Suggestions and ideas
        elif any(phrase in user_lower for phrase in ['suggest', 'idea', 'what should', 'help with']):
            intent['type'] = 'suggestions'
            
            if 'character' in user_lower:
                intent['action'] = 'character_suggestions'
            elif 'plot' in user_lower:
                intent['action'] = 'plot_suggestions'
            elif 'title' in user_lower:
                intent['action'] = 'title_suggestions'
            else:
                intent['action'] = 'general_suggestions'
        
        # Model status and information
        elif any(phrase in user_lower for phrase in ['status', 'trained', 'model', 'info']):
            intent['type'] = 'info'
            intent['action'] = 'model_status'
        
        return intent
    
    def _generate_response(self, user_input: str, intent: Dict) -> str:
        """Generate appropriate response based on user intent."""
        
        if not self.model.is_trained:
            return ("I haven't been trained on any books yet. Please provide .txt book files "
                   "for me to learn from before I can assist with writing!")
        
        if intent['type'] == 'writing_assistance':
            return self._handle_writing_assistance(user_input, intent)
        
        elif intent['type'] == 'generation':
            return self._handle_text_generation(user_input, intent)
        
        elif intent['type'] == 'style_analysis':
            return self._handle_style_analysis(user_input)
        
        elif intent['type'] == 'suggestions':
            return self._handle_suggestions(user_input, intent)
        
        elif intent['type'] == 'info':
            return self._handle_info_request()
        
        else:
            return self._handle_general_chat(user_input)
    
    def _handle_writing_assistance(self, user_input: str, intent: Dict) -> str:
        """Handle writing assistance requests."""
        
        if intent['action'] == 'continue_text':
            # Extract the text to continue from user input
            text_to_continue = self._extract_text_to_continue(user_input)
            if text_to_continue:
                continuation = self.model.complete_sentence(text_to_continue, max_length=50)
                return f"Here's a continuation:\n\n{continuation}"
            else:
                generated = self.model.generate_text("", max_length=30)
                return f"I'll help you start writing:\n\n{generated}"
        
        elif intent['action'] == 'character_development':
            character_text = self.model.generate_text("character", max_length=40)
            return f"Here's some character inspiration:\n\n{character_text}"
        
        elif intent['action'] == 'plot_development':
            plot_text = self.model.generate_text("story", max_length=50)
            return f"Here's a plot idea:\n\n{plot_text}"
        
        elif intent['action'] == 'dialogue_writing':
            dialogue = self.model.generate_text("said", max_length=30)
            return f"Here's some dialogue inspiration:\n\n{dialogue}"
        
        else:
            # General writing help
            writing_text = self.model.generate_text("", max_length=40)
            return f"Here's some writing to inspire you:\n\n{writing_text}"
    
    def _handle_text_generation(self, user_input: str, intent: Dict) -> str:
        """Handle text generation requests."""
        
        # Extract any prompt from user input
        prompt = self._extract_prompt(user_input)
        
        if intent['action'] == 'story_generation':
            length = 80
            story = self.model.generate_text(prompt, max_length=length)
            return f"Here's a story beginning:\n\n{story}"
        
        elif intent['action'] == 'chapter_generation':
            length = 100
            chapter = self.model.generate_text(prompt, max_length=length)
            return f"Here's a chapter outline:\n\n{chapter}"
        
        elif intent['action'] == 'paragraph_generation':
            length = 50
            paragraph = self.model.generate_text(prompt, max_length=length)
            return f"Here's a paragraph:\n\n{paragraph}"
        
        else:
            length = 60
            text = self.model.generate_text(prompt, max_length=length)
            return f"Here's some generated text:\n\n{text}"
    
    def _handle_style_analysis(self, user_input: str) -> str:
        """Handle style and genre analysis requests."""
        stats = self.model.get_model_stats()
        
        if stats['most_common_words']:
            common_words = [word for word, count in stats['most_common_words']]
            style_text = f"Based on my training, I've learned from {stats['vocabulary_size']} unique words. "
            style_text += f"The most common words in my training data are: {', '.join(common_words[:5])}. "
            style_text += "This suggests the writing style tends to be descriptive and narrative."
        else:
            style_text = "I can analyze writing style once I have more training data."
        
        return style_text
    
    def _handle_suggestions(self, user_input: str, intent: Dict) -> str:
        """Handle suggestion requests."""
        
        if intent['action'] == 'character_suggestions':
            suggestions = self.model.suggest_next_words("character", num_suggestions=3)
            if suggestions:
                words = [word for word, prob in suggestions]
                return f"Character ideas based on my training: {', '.join(words)}"
            else:
                return "Create unique characters with distinct personalities, backgrounds, and motivations."
        
        elif intent['action'] == 'plot_suggestions':
            suggestions = self.model.suggest_next_words("story", num_suggestions=3)
            if suggestions:
                words = [word for word, prob in suggestions]
                return f"Plot ideas based on my training: {', '.join(words)}"
            else:
                return "Consider conflicts, character growth, and unexpected twists in your plot."
        
        elif intent['action'] == 'title_suggestions':
            title_start = self.model.generate_text("the", max_length=5)
            return f"Title suggestion: {title_start.title()}"
        
        else:
            general_text = self.model.generate_text("", max_length=20)
            return f"Writing suggestion based on my training:\n\n{general_text}"
    
    def _handle_info_request(self) -> str:
        """Handle requests for model information."""
        stats = self.model.get_model_stats()
        
        info = f"Model Status:\n"
        info += f"- Trained: {'Yes' if stats['is_trained'] else 'No'}\n"
        info += f"- Vocabulary size: {stats['vocabulary_size']:,} words\n"
        info += f"- N-gram size: {stats['n_gram_size']}\n"
        info += f"- Total patterns learned: {stats['total_n_grams']:,}\n"
        
        if stats['most_common_words']:
            common_words = [word for word, count in stats['most_common_words'][:5]]
            info += f"- Top words: {', '.join(common_words)}"
        
        return info
    
    def _handle_general_chat(self, user_input: str) -> str:
        """Handle general conversation."""
        # Try to generate relevant text based on keywords in input
        keywords = re.findall(r'\b\w+\b', user_input.lower())
        relevant_keywords = [word for word in keywords if word in self.model.vocabulary]
        
        if relevant_keywords:
            prompt = relevant_keywords[0]
            response = self.model.generate_text(prompt, max_length=30)
            return f"Based on your message, here's something from my training:\n\n{response}"
        else:
            response = self.model.generate_text("", max_length=30)
            return f"Here's something I learned from the books:\n\n{response}"
    
    def _extract_text_to_continue(self, user_input: str) -> str:
        """Extract text that the user wants to continue."""
        # Look for quoted text or text after "continue this:"
        patterns = [
            r'"([^"]+)"',
            r"'([^']+)'",
            r'continue this:?\s*(.+?)(?:\n|$)',
            r'complete this:?\s*(.+?)(?:\n|$)',
            r'finish this:?\s*(.+?)(?:\n|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_prompt(self, user_input: str) -> str:
        """Extract writing prompt from user input."""
        # Look for quoted text or text after keywords
        patterns = [
            r'"([^"]+)"',
            r"'([^']+)'",
            r'about:?\s*(.+?)(?:\n|$)',
            r'write about:?\s*(.+?)(?:\n|$)',
            r'generate:?\s*(.+?)(?:\n|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def get_conversation_history(self) -> List[Dict]:
        """Get the conversation history."""
        return self.conversation_history
    
    def clear_conversation_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_next_word_suggestions(self, text: str, num_suggestions: int = 5) -> List[Tuple[str, float]]:
        """Get suggestions for the next word given current text."""
        return self.model.suggest_next_words(text, num_suggestions)
    
    def save_conversation(self, filepath: str) -> None:
        """Save conversation history to a file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
        logger.info(f"Conversation saved to {filepath}")
    
    def export_model_info(self) -> Dict:
        """Export comprehensive information about the model and training data."""
        text_stats = self.text_processor.get_statistics()
        model_stats = self.model.get_model_stats()
        
        return {
            'text_processing': text_stats,
            'model': model_stats,
            'conversation_length': len(self.conversation_history),
            'export_time': datetime.now().isoformat()
        }