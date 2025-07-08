#!/usr/bin/env python3
"""
Book Writing AI Chatbot - Interactive Demo

This script demonstrates the core functionality of the AI chatbot
that learns from book text databases for writing assistance.
"""

import sys
import os
sys.path.append('.')

from src import BookWritingChatbot

def main():
    print("📚 Book Writing AI Chatbot - Interactive Demo")
    print("=" * 60)
    print("Welcome! I'm an AI that learns from book text databases")
    print("to help you with book writing tasks.")
    print()
    
    # Initialize chatbot
    print("🤖 Initializing AI chatbot...")
    chatbot = BookWritingChatbot()
    
    # Train on sample books
    print("📖 Training on sample books (this may take a moment)...")
    try:
        stats = chatbot.train_from_books('sample_books')
        print(f"✅ Training completed!")
        print(f"   📊 Processed: {stats['num_books']} books")
        print(f"   📝 Learned from: {stats['total_sentences']} sentences")
        print(f"   🔤 Vocabulary: {stats['vocabulary_size']} unique words")
        
        # List the books that were processed
        if 'books' in stats:
            print(f"   📚 Books used for training:")
            for book in stats['books']:
                print(f"      - {book['title']}")
        
    except Exception as e:
        print(f"❌ Training failed: {str(e)}")
        return
    
    print("\n" + "=" * 60)
    print("🎯 Demonstrating Writing Assistance Features")
    print("=" * 60)
    
    # Demo different features
    demos = [
        {
            'title': '📖 Story Generation',
            'prompt': 'Generate a story about adventure',
            'description': 'Creating original story content based on learned patterns'
        },
        {
            'title': '🔄 Text Completion',
            'prompt': 'Continue this: Once upon a time, there was a brave explorer who',
            'description': 'Completing partial text with relevant continuation'
        },
        {
            'title': '👤 Character Development',
            'prompt': 'Help me develop a character for my story',
            'description': 'Providing character development assistance'
        },
        {
            'title': '🕵️ Plot Suggestions',
            'prompt': 'Suggest a plot for my mystery novel',
            'description': 'Offering plot ideas and story structure suggestions'
        },
        {
            'title': '🎨 Writing Style Analysis',
            'prompt': 'What writing style did you learn from the books?',
            'description': 'Analyzing and describing learned writing patterns'
        },
        {
            'title': '📊 Model Information',
            'prompt': 'Show me your training status and capabilities',
            'description': 'Displaying model statistics and capabilities'
        }
    ]
    
    for i, demo in enumerate(demos, 1):
        print(f"\n{i}. {demo['title']}")
        print(f"   {demo['description']}")
        print(f"   User: {demo['prompt']}")
        
        try:
            response = chatbot.chat(demo['prompt'])
            # Truncate very long responses for demo purposes
            if len(response) > 200:
                response = response[:200] + "..."
            print(f"   AI: {response}")
        except Exception as e:
            print(f"   AI: Error generating response: {str(e)}")
        
        print("-" * 60)
    
    print("\n🎉 Demo completed successfully!")
    print("\n💡 Key Capabilities Demonstrated:")
    print("   ✅ Learns from .txt book files (text databases)")
    print("   ✅ Generates original text based on learned patterns")
    print("   ✅ Provides writing assistance for various tasks")
    print("   ✅ Offers context-aware text completion")
    print("   ✅ Helps with character and plot development")
    print("   ✅ Analyzes and describes writing styles")
    print("   ✅ Maintains conversation history and context")
    
    print("\n🚀 Ready for Interactive Use!")
    print("   - Run 'python3 cli.py' for command-line interface")
    print("   - Run 'python3 app.py' for web interface (requires Flask)")
    print("   - Run 'python3 start.py' for guided setup")
    
    print("\n📖 Training Your Own Model:")
    print("   1. Create a folder with .txt book files")
    print("   2. Use the training functions to process your books")
    print("   3. Chat with the AI for personalized writing assistance!")
    
    print("\n🌟 The AI is 'dumb' without training data but becomes")
    print("   intelligent when trained on your book collection!")

if __name__ == "__main__":
    main()