#!/usr/bin/env python3
"""
Simple Language Model - Built-in Libraries Version

A simple n-gram based language model that uses only built-in Python libraries.
This version provides fallback functionality when NumPy is not available.
"""

import json
import random
import re
import math
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleLanguageModelBuiltin:
    """
    A simple n-gram based language model using only built-in Python libraries.
    Fallback version when NumPy is not available.
    """
    
    def __init__(self, n_gram_size: int = 3, min_word_count: int = 2):
        self.n_gram_size = n_gram_size
        self.min_word_count = min_word_count
        self.word_to_id = {}
        self.id_to_word = {}
        self.vocabulary = set()
        self.word_counts = Counter()
        self.n_grams = defaultdict(lambda: defaultdict(int))
        self.sentence_starters = []
        self.is_trained = False
        
        # Basic grammar rules (the "non-dumb" part when no training data)
        self.basic_grammar = {
            'sentence_starters': ['The', 'A', 'An', 'In', 'On', 'At', 'Once', 'When', 'After', 'Before'],
            'common_words': ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'],
            'punctuation': ['.', '!', '?'],
            'conjunctions': ['and', 'but', 'or', 'so', 'yet', 'for'],
            'prepositions': ['in', 'on', 'at', 'by', 'for', 'with', 'to', 'from', 'about', 'over', 'under']
        }
    
    def train(self, sentences: List[str]) -> None:
        """
        Train the model on a list of sentences.
        
        Args:
            sentences: List of sentences to train on
        """
        if not sentences:
            logger.warning("No sentences provided for training")
            return
            
        logger.info(f"Training on {len(sentences)} sentences...")
        
        # Preprocess and build vocabulary
        processed_sentences = []
        for sentence in sentences:
            words = self._preprocess_sentence(sentence)
            if len(words) >= self.n_gram_size:
                processed_sentences.append(words)
                
                # Track sentence starters
                if words[0].istitle():
                    self.sentence_starters.append(words[0])
                
                # Update word counts
                for word in words:
                    self.word_counts[word] += 1
        
        # Filter vocabulary by minimum count
        self.vocabulary = {word for word, count in self.word_counts.items() 
                          if count >= self.min_word_count}
        
        # Create word mappings
        self.word_to_id = {word: i for i, word in enumerate(sorted(self.vocabulary))}
        self.id_to_word = {i: word for word, i in self.word_to_id.items()}
        
        # Build n-grams
        for sentence in processed_sentences:
            # Filter sentence to only include vocabulary words
            filtered_sentence = [word for word in sentence if word in self.vocabulary]
            
            if len(filtered_sentence) >= self.n_gram_size:
                for i in range(len(filtered_sentence) - self.n_gram_size + 1):
                    n_gram = tuple(filtered_sentence[i:i + self.n_gram_size - 1])
                    next_word = filtered_sentence[i + self.n_gram_size - 1]
                    self.n_grams[n_gram][next_word] += 1
        
        # Convert counts to probabilities
        for n_gram in self.n_grams:
            total_count = sum(self.n_grams[n_gram].values())
            for word in self.n_grams[n_gram]:
                self.n_grams[n_gram][word] /= total_count
        
        self.is_trained = True
        logger.info(f"Training completed. Vocabulary size: {len(self.vocabulary)}, "
                   f"N-grams: {len(self.n_grams)}")
    
    def _preprocess_sentence(self, sentence: str) -> List[str]:
        """Preprocess a sentence into a list of words."""
        # Basic cleaning
        sentence = sentence.strip()
        
        # Split into words and punctuation
        tokens = re.findall(r'\b\w+\b|[.!?;,]', sentence)
        
        # Filter out very short tokens and normalize
        words = []
        for token in tokens:
            if token.isalpha() and len(token) > 1:
                words.append(token.lower())
            elif token in '.!?':
                words.append(token)
                
        return words
    
    def generate_text(self, prompt: str = "", max_length: int = 100, temperature: float = 0.8) -> str:
        """
        Generate text based on a prompt.
        
        Args:
            prompt: Starting text prompt
            max_length: Maximum number of words to generate
            temperature: Randomness in generation (higher = more random)
            
        Returns:
            Generated text
        """
        if not self.is_trained:
            return self._generate_basic_text(prompt, max_length)
        
        # Process prompt
        if prompt:
            words = self._preprocess_sentence(prompt)
            # Filter to vocabulary words
            words = [word for word in words if word in self.vocabulary]
        else:
            # Start with a random sentence starter
            if self.sentence_starters:
                starter = random.choice(list(set(self.sentence_starters)))
                words = [starter.lower()]
            else:
                words = [random.choice(list(self.vocabulary))]
        
        generated_words = words.copy()
        
        for _ in range(max_length):
            # Get the current context (last n-1 words)
            if len(generated_words) >= self.n_gram_size - 1:
                context = tuple(generated_words[-(self.n_gram_size - 1):])
            else:
                context = tuple(generated_words)
            
            # Find possible next words
            next_word_probs = self.n_grams.get(context, {})
            
            if not next_word_probs:
                # Fallback to shorter context or random word
                if len(context) > 1:
                    context = context[1:]
                    next_word_probs = self.n_grams.get(context, {})
                
                if not next_word_probs:
                    # Pick a random word from vocabulary
                    next_word = random.choice(list(self.vocabulary))
                else:
                    next_word = self._sample_word_builtin(next_word_probs, temperature)
            else:
                next_word = self._sample_word_builtin(next_word_probs, temperature)
            
            generated_words.append(next_word)
            
            # Stop if we hit a sentence ending
            if next_word in '.!?':
                break
        
        # Convert to readable text
        return self._format_output(generated_words)
    
    def _sample_word_builtin(self, word_probs: Dict[str, float], temperature: float) -> str:
        """Sample a word based on probabilities using built-in libraries."""
        words = list(word_probs.keys())
        probs = list(word_probs.values())
        
        if temperature == 0:
            # Greedy selection
            max_prob = max(probs)
            max_index = probs.index(max_prob)
            return words[max_index]
        
        # Apply temperature scaling
        if temperature != 1.0:
            probs = [math.pow(p, 1.0 / temperature) for p in probs]
        
        # Normalize probabilities
        total_prob = sum(probs)
        if total_prob == 0:
            return random.choice(words)
        
        probs = [p / total_prob for p in probs]
        
        # Sample using cumulative distribution
        rand_val = random.random()
        cumulative = 0.0
        
        for word, prob in zip(words, probs):
            cumulative += prob
            if rand_val <= cumulative:
                return word
        
        # Fallback (shouldn't reach here)
        return words[-1]
    
    def _format_output(self, words: List[str]) -> str:
        """Format a list of words into readable text."""
        if not words:
            return ""
        
        # Capitalize first word
        formatted = [words[0].capitalize()]
        
        for word in words[1:]:
            if word in '.!?':
                formatted[-1] += word
            else:
                formatted.append(word)
        
        text = ' '.join(formatted)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.!?])', r'\1', text)
        
        return text
    
    def _generate_basic_text(self, prompt: str, max_length: int) -> str:
        """Generate basic text when not trained (fallback mode)."""
        if prompt:
            words = prompt.split()
        else:
            words = [random.choice(self.basic_grammar['sentence_starters'])]
        
        # Generate simple sentences using basic grammar
        for _ in range(min(max_length, 20)):
            # Randomly add common words
            if random.random() < 0.3:
                words.append(random.choice(self.basic_grammar['common_words']))
            else:
                words.append("[WORD]")  # Placeholder for actual content
        
        # Add punctuation
        words.append(random.choice(self.basic_grammar['punctuation']))
        
        text = ' '.join(words)
        return f"Model not trained. Basic output: {text}"
    
    def complete_sentence(self, partial_sentence: str, max_length: int = 50) -> str:
        """Complete a partial sentence."""
        return self.generate_text(partial_sentence, max_length)
    
    def suggest_next_words(self, context: str, num_suggestions: int = 5) -> List[Tuple[str, float]]:
        """
        Suggest next words based on context.
        
        Args:
            context: The current text context
            num_suggestions: Number of suggestions to return
            
        Returns:
            List of (word, probability) tuples
        """
        if not self.is_trained:
            return [("not", 0.2), ("trained", 0.2), ("yet", 0.2), ("please", 0.2), ("wait", 0.2)]
        
        words = self._preprocess_sentence(context)
        words = [word for word in words if word in self.vocabulary]
        
        if len(words) >= self.n_gram_size - 1:
            context_tuple = tuple(words[-(self.n_gram_size - 1):])
        else:
            context_tuple = tuple(words)
        
        next_word_probs = self.n_grams.get(context_tuple, {})
        
        if not next_word_probs and len(context_tuple) > 1:
            # Try shorter context
            context_tuple = context_tuple[1:]
            next_word_probs = self.n_grams.get(context_tuple, {})
        
        # Sort by probability and return top suggestions
        suggestions = sorted(next_word_probs.items(), key=lambda x: x[1], reverse=True)
        return suggestions[:num_suggestions]
    
    def save_model(self, filepath: str) -> None:
        """Save the trained model to a file."""
        model_data = {
            'n_gram_size': self.n_gram_size,
            'min_word_count': self.min_word_count,
            'word_to_id': self.word_to_id,
            'id_to_word': self.id_to_word,
            'vocabulary': list(self.vocabulary),
            'word_counts': dict(self.word_counts),
            'n_grams': {str(k): dict(v) for k, v in self.n_grams.items()},
            'sentence_starters': self.sentence_starters,
            'is_trained': self.is_trained
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """Load a trained model from a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                model_data = json.load(f)
            
            self.n_gram_size = model_data['n_gram_size']
            self.min_word_count = model_data['min_word_count']
            self.word_to_id = model_data['word_to_id']
            self.id_to_word = {int(k): v for k, v in model_data['id_to_word'].items()}
            self.vocabulary = set(model_data['vocabulary'])
            self.word_counts = Counter(model_data['word_counts'])
            
            # Reconstruct n_grams
            self.n_grams = defaultdict(lambda: defaultdict(int))
            for k, v in model_data['n_grams'].items():
                key = eval(k)  # Convert string back to tuple
                self.n_grams[key] = defaultdict(int, v)
            
            self.sentence_starters = model_data['sentence_starters']
            self.is_trained = model_data['is_trained']
            
            logger.info(f"Model loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def get_model_stats(self) -> Dict:
        """Get statistics about the trained model."""
        return {
            'is_trained': self.is_trained,
            'vocabulary_size': len(self.vocabulary),
            'n_gram_size': self.n_gram_size,
            'total_n_grams': len(self.n_grams),
            'sentence_starters': len(set(self.sentence_starters)),
            'most_common_words': self.word_counts.most_common(10) if self.word_counts else []
        }