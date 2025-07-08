# 📚 Book Writing AI Chatbot

An AI chatbot specialized for book writing assistance that learns from provided text databases (books). The system is designed to be "dumb" without training data, relying only on basic grammar rules, but becomes intelligent when trained on your book collection.

## 🌟 Features

- **📖 Text Database Learning**: Trains on .txt book files to learn writing patterns
- **💬 Interactive Chat Interface**: Web UI and command-line interface
- **✍️ Writing Assistance**: Story generation, text completion, character development
- **📝 Multiple Writing Tasks**: Plot suggestions, dialogue writing, style analysis
- **🎯 Book-Focused**: Specialized for creative writing and book authoring
- **🧠 Simple Architecture**: N-gram based model (no external AI dependencies)
- **💾 Model Persistence**: Save and load trained models

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
git clone <repository-url>
cd book-writing-ai-chatbot

# Install dependencies
pip install -r requirements.txt
```

### 2. Web Interface (Recommended)

```bash
# Start the web server
python app.py

# Open your browser to http://localhost:5000
# Upload .txt book files or create sample books
# Start chatting with the AI!
```

### 3. Command Line Interface

```bash
# Interactive chat mode
python cli.py

# Train on your books
python cli.py --train path/to/books/

# Create sample books and train
python cli.py --sample

# Single response
python cli.py --message "Help me write a story about dragons"
```

## 📁 Project Structure

```
book-writing-ai-chatbot/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── text_processor.py     # Text processing and book loading
│   ├── simple_model.py       # N-gram language model
│   └── chatbot.py           # Main chatbot logic
├── app.py                   # Flask web application
├── cli.py                   # Command line interface
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 💡 How It Works

### Training Process
1. **Text Processing**: Loads .txt book files and cleans the content
2. **Sentence Extraction**: Splits books into sentences and filters by quality
3. **Vocabulary Building**: Creates vocabulary from all processed text
4. **N-gram Training**: Builds statistical patterns for text generation
5. **Model Saving**: Saves trained model for future use

### Without Training Data
- Uses basic grammar rules and sentence structures
- Limited to simple placeholder text generation
- Provides helpful error messages about needing training data

### With Training Data
- Generates text based on learned patterns from your books
- Maintains writing style similar to training material
- Provides context-aware suggestions and completions

## 🎯 Writing Assistance Features

### Text Generation
- **Story Beginnings**: "Generate a story about adventure"
- **Chapter Outlines**: "Create a chapter about mystery"
- **Paragraph Writing**: "Write a paragraph about the forest"

### Text Completion
- **Continue Text**: "Continue this: Once upon a time..."
- **Sentence Completion**: Finish partial sentences
- **Story Development**: Extend existing narratives

### Creative Assistance
- **Character Development**: Ideas for character creation
- **Plot Suggestions**: Story plot and conflict ideas
- **Dialogue Writing**: Conversation and speech patterns
- **Title Suggestions**: Book and chapter title ideas

### Style Analysis
- **Writing Pattern Analysis**: Learn about training data style
- **Word Usage Statistics**: Most common words and patterns
- **Genre Recognition**: Identify writing style characteristics

## 🛠️ Usage Examples

### Web Interface
1. Start the web server: `python app.py`
2. Upload .txt book files or click "Create Sample Books"
3. Wait for training to complete
4. Chat with the AI for writing assistance

### Command Line Examples

```bash
# Interactive mode with sample books
python cli.py --sample --interactive

# Train on your book collection
python cli.py --train ~/Documents/Books/

# Get writing help
python cli.py --message "Help me develop a mystery character"

# Continue existing text
python cli.py --message "Continue this story: The detective entered the dark room..."

# Get plot suggestions
python cli.py --message "Suggest a plot for my fantasy novel"
```

## 📚 Preparing Your Book Collection

### Supported Format
- **File Type**: .txt files only
- **Encoding**: UTF-8 or Latin1 (auto-detected)
- **Content**: Plain text books, stories, novels

### Book Organization
```
books/
├── adventure_novel.txt
├── mystery_story.txt
├── fantasy_epic.txt
└── sci_fi_collection.txt
```

### Content Guidelines
- Include complete books or substantial excerpts
- Ensure good text quality (minimal OCR errors)
- Mix different genres for diverse writing assistance
- At least 10-20 books recommended for good results

## ⚙️ Configuration Options

### Model Parameters
- **N-gram Size**: Default 3 (trigrams), adjustable in code
- **Minimum Word Count**: Filters rare words, default 2
- **Sentence Filtering**: Removes low-quality sentences automatically

### Training Settings
- **Sentence Length**: 10-500 characters (configurable)
- **Quality Filters**: Removes repetitive, corrupted, or header text
- **Vocabulary Filtering**: Excludes very rare words

## 🔧 Advanced Usage

### Save and Load Models
```bash
# Train and save model
python cli.py --train books/ --save-model my_model.json

# Load existing model
python cli.py --model my_model.json --interactive
```

### Programming Interface
```python
from src.chatbot import BookWritingChatbot

# Initialize chatbot
chatbot = BookWritingChatbot()

# Train on books
stats = chatbot.train_from_books("path/to/books/")

# Get writing assistance
response = chatbot.chat("Help me write a character description")

# Generate text with prompt
text = chatbot.model.generate_text("The hero", max_length=50)
```

## 🚨 Troubleshooting

### Common Issues

**"No .txt files found"**
- Ensure files have .txt extension
- Check file encoding (should be UTF-8 or Latin1)
- Verify files contain readable text content

**"Model not trained"**
- Train the model first using web interface or CLI
- Ensure training completed successfully
- Check that book files were processed correctly

**"Training failed"**
- Verify book files are readable
- Check available disk space
- Ensure sufficient memory for processing

**Poor text generation quality**
- Train on more books (minimum 10-20 recommended)
- Use higher quality source texts
- Check that books are in similar style/genre

### Performance Tips
- Use SSD storage for faster book processing
- Train on books in similar genres for consistent style
- Larger vocabulary (more books) = better text generation
- Save trained models to avoid retraining

## 🤝 Contributing

This is a background agent implementation. To extend the system:

1. **Add new writing features** in `src/chatbot.py`
2. **Improve text processing** in `src/text_processor.py`
3. **Enhance the language model** in `src/simple_model.py`
4. **Extend the web interface** in `app.py`

## 📄 License

This project is open source. Use it freely for your book writing projects!

## 🎯 Future Enhancements

- Genre-specific training modes
- Export generated content to various formats
- Integration with writing software
- Collaborative writing features
- Advanced style mimicking
- Character and plot tracking across conversations

---

**Happy Writing! 📚✨**

Transform your book collection into a personalized writing assistant and never face writer's block again!