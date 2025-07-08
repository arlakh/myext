import os
import re
from typing import List, Dict, Tuple
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextProcessorBuiltin:
    """
    Processes text files from a database directory for training the AI model.
    Uses only built-in Python libraries for maximum compatibility.
    """
    
    def __init__(self, min_sentence_length: int = 10, max_sentence_length: int = 500):
        self.min_sentence_length = min_sentence_length
        self.max_sentence_length = max_sentence_length
        self.book_data = []
        self.vocabulary = set()
        self.word_counts = defaultdict(int)
        
    def load_books_from_directory(self, directory_path: str) -> List[Dict]:
        """
        Load all .txt files from the specified directory.
        
        Args:
            directory_path: Path to directory containing .txt book files
            
        Returns:
            List of dictionaries containing book data
        """
        if not os.path.exists(directory_path):
            logger.error(f"Directory not found: {directory_path}")
            return []
            
        book_files = [f for f in os.listdir(directory_path) if f.endswith('.txt')]
        
        if not book_files:
            logger.warning(f"No .txt files found in {directory_path}")
            return []
            
        logger.info(f"Found {len(book_files)} book files")
        
        for filename in book_files:
            filepath = os.path.join(directory_path, filename)
            try:
                book_data = self._load_single_book(filepath, filename)
                if book_data:
                    self.book_data.append(book_data)
                    logger.info(f"Loaded: {filename}")
            except Exception as e:
                logger.error(f"Error loading {filename}: {str(e)}")
                
        return self.book_data
    
    def _load_single_book(self, filepath: str, filename: str) -> Dict:
        """Load and process a single book file."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(filepath, 'r', encoding='latin1') as f:
                    content = f.read()
            except Exception as e:
                logger.error(f"Could not read {filename}: {str(e)}")
                return None
                
        if len(content.strip()) < 100:  # Skip very short files
            logger.warning(f"Skipping {filename}: too short")
            return None
            
        # Extract title from filename or content
        title = self._extract_title(filename, content)
        
        # Clean and process the content
        cleaned_content = self._clean_text(content)
        sentences = self._split_into_sentences_builtin(cleaned_content)
        
        # Filter sentences
        filtered_sentences = self._filter_sentences(sentences)
        
        if len(filtered_sentences) < 10:  # Skip books with too few good sentences
            logger.warning(f"Skipping {filename}: too few good sentences")
            return None
            
        # Update vocabulary and word counts
        self._update_vocabulary(filtered_sentences)
        
        return {
            'title': title,
            'filename': filename,
            'content': cleaned_content,
            'sentences': filtered_sentences,
            'word_count': len(cleaned_content.split()),
            'sentence_count': len(filtered_sentences)
        }
    
    def _extract_title(self, filename: str, content: str) -> str:
        """Extract title from filename or content."""
        # Try to get title from filename
        title = os.path.splitext(filename)[0]
        title = re.sub(r'[_\-]', ' ', title)
        title = re.sub(r'\s+', ' ', title).strip()
        
        # If title is generic or too short, try to extract from content
        if len(title) < 3 or title.lower() in ['book', 'text', 'novel', 'story']:
            # Look for title in first few lines
            lines = content.split('\n')[:10]
            for line in lines:
                line = line.strip()
                if len(line) > 3 and len(line) < 100 and not line.lower().startswith('chapter'):
                    # Check if line looks like a title
                    if re.match(r'^[A-Z][^.!?]*$', line) or line.isupper():
                        title = line
                        break
                        
        return title.title()
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove or replace special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.!?;:,\'"()-]', ' ', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.!?;:,])', r'\1', text)
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)
        
        # Remove multiple consecutive punctuation
        text = re.sub(r'[.]{3,}', '...', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        return text.strip()
    
    def _split_into_sentences_builtin(self, text: str) -> List[str]:
        """Split text into sentences using built-in regex (fallback for when NLTK is not available)."""
        # Simple sentence splitting using regex
        # This is less sophisticated than NLTK but works without external dependencies
        
        # First, protect abbreviations and numbers
        text = re.sub(r'\b([A-Z][a-z]{1,3}\.)', r'\1<ABBREV>', text)
        text = re.sub(r'(\d+\.\d+)', r'\1<DECIMAL>', text)
        
        # Split on sentence endings followed by whitespace and capital letter or end of string
        sentences = re.split(r'[.!?]+(?:\s+(?=[A-Z])|$)', text)
        
        # Clean up and restore protected text
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.replace('<ABBREV>', '.').replace('<DECIMAL>', '.')
            sentence = sentence.strip()
            if sentence:
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _filter_sentences(self, sentences: List[str]) -> List[str]:
        """Filter sentences based on length and quality criteria."""
        filtered = []
        for sentence in sentences:
            # Skip sentences that are too short or too long
            if len(sentence) < self.min_sentence_length or len(sentence) > self.max_sentence_length:
                continue
                
            # Skip sentences with too many numbers or special characters
            if len(re.sub(r'[a-zA-Z\s]', '', sentence)) > len(sentence) * 0.3:
                continue
                
            # Skip sentences that are mostly uppercase (might be headers)
            if sentence.isupper() and len(sentence) > 20:
                continue
                
            # Skip sentences with repeated words (might be corrupted)
            words = sentence.lower().split()
            if len(set(words)) < len(words) * 0.6 and len(words) > 5:
                continue
                
            filtered.append(sentence)
            
        return filtered
    
    def _update_vocabulary(self, sentences: List[str]):
        """Update vocabulary and word counts from sentences."""
        for sentence in sentences:
            words = sentence.lower().split()
            for word in words:
                # Clean word
                word = re.sub(r'[^\w]', '', word)
                if word and len(word) > 1:
                    self.vocabulary.add(word)
                    self.word_counts[word] += 1
    
    def get_training_data(self) -> List[str]:
        """Get all sentences from all books for training."""
        all_sentences = []
        for book in self.book_data:
            all_sentences.extend(book['sentences'])
        return all_sentences
    
    def get_statistics(self) -> Dict:
        """Get statistics about the processed data."""
        if not self.book_data:
            return {}
            
        total_sentences = sum(book['sentence_count'] for book in self.book_data)
        total_words = sum(book['word_count'] for book in self.book_data)
        
        return {
            'num_books': len(self.book_data),
            'total_sentences': total_sentences,
            'total_words': total_words,
            'vocabulary_size': len(self.vocabulary),
            'avg_sentences_per_book': total_sentences / len(self.book_data),
            'avg_words_per_book': total_words / len(self.book_data),
            'books': [{'title': book['title'], 'sentences': book['sentence_count'], 
                      'words': book['word_count']} for book in self.book_data]
        }
    
    def create_sample_books(self, output_dir: str = "sample_books"):
        """Create sample book files for testing if no books are provided."""
        os.makedirs(output_dir, exist_ok=True)
        
        sample_books = [
            {
                'filename': 'adventure_tale.txt',
                'content': '''The Adventure of the Lost Treasure

Chapter 1: The Mysterious Map

It was a dark and stormy night when Emma discovered the old map hidden in her grandmother's attic. The parchment was yellowed with age, and strange symbols marked various locations across what appeared to be a tropical island.

"This could be the adventure I've been waiting for," she whispered to herself, carefully studying the intricate details drawn by some long-dead explorer.

The next morning, Emma shared her discovery with her best friend Jake. His eyes widened as he examined the map under a magnifying glass.

"Look at these markings," Jake pointed to a series of X marks scattered across the island. "This has to be a treasure map!"

Chapter 2: The Journey Begins

Within a week, the two friends had convinced Emma's uncle, a skilled sailor, to help them charter a boat to the Caribbean. The island depicted on the map matched a real location they found in maritime charts.

As their vessel cut through the azure waters, Emma felt a mixture of excitement and nervousness. What would they find on the mysterious island? Would the treasure still be there after all these years?

The island appeared on the horizon like a green jewel set in the endless blue. Palm trees swayed in the tropical breeze, and white beaches promised safe landing. But Emma knew that appearances could be deceiving.'''
            },
            {
                'filename': 'fantasy_realm.txt',
                'content': '''The Chronicles of Eldoria

Book One: The Awakening Magic

In the mystical realm of Eldoria, where dragons soared through crystal skies and ancient forests whispered secrets of old, a young apprentice named Lyra discovered she possessed a power that had been dormant for centuries.

The Academy of Mystic Arts stood tall on the floating island of Aethermoor, its spires reaching toward the two moons that governed the magical cycles. Lyra had always felt different from the other students, unable to cast even the simplest spells.

Master Thorne, the academy's most revered teacher, watched Lyra struggle with her studies. Little did anyone know that her apparent lack of magical ability was actually a sign of something far more powerful stirring within her.

"Magic is not about forcing energy to bend to your will," Master Thorne often told his students. "True magic flows when you become one with the natural forces that surround us."

One fateful evening, as Lyra practiced alone in the moonlit courtyard, she felt a strange warmth spreading through her hands. The air around her began to shimmer, and suddenly, flowers bloomed where she walked, and the ancient stone statues turned their heads to watch her pass.

The other students gasped in amazement. What they witnessed was not ordinary magic, but the return of the legendary Nature's Heart - a power that could either save Eldoria from the encroaching darkness or destroy it entirely.'''
            },
            {
                'filename': 'mystery_novel.txt',
                'content': '''Death in the Library

Chapter 1: A Quiet Evening Disturbed

Detective Sarah Chen had always found libraries to be peaceful places, which made the call about a murder at the Grand Metropolitan Library all the more unsettling. The imposing building with its gothic architecture and vast collection had been the city's crown jewel for over a century.

The victim was Dr. Marcus Whitfield, a renowned literature professor who had been researching rare manuscripts in the library's restricted section. Security cameras showed him entering the building at 6 PM, but his body wasn't discovered until the next morning.

"What was he working on?" Chen asked the head librarian, Mrs. Eleanor Price, who had found the body.

"Dr. Whitfield was examining some 16th-century texts," Mrs. Price replied, her voice shaking. "He had special permission to access our most valuable collection."

The crime scene was puzzling. Dr. Whitfield lay sprawled among scattered books and papers, but there were no obvious signs of struggle. The murder weapon was nowhere to be found, and the restricted section had been locked from the inside.

Chapter 2: Hidden Secrets

As Detective Chen investigated further, she discovered that Dr. Whitfield had been close to a major discovery about a lost Shakespearean manuscript. His research notes suggested he had found evidence of a play that scholars had only theorized about.

"Someone didn't want him to publish his findings," Chen mused, studying the professor's meticulous handwriting. "But who would kill for a 400-year-old play?"

The answer lay hidden in the very books that surrounded the victim, waiting for a detective clever enough to read between the lines.'''
            }
        ]
        
        for book in sample_books:
            filepath = os.path.join(output_dir, book['filename'])
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(book['content'])
                
        logger.info(f"Created {len(sample_books)} sample books in {output_dir}/")
        return output_dir