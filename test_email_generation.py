#!/usr/bin/env python3
"""
Test script for the Daily Jeopardy Email
Tests question selection and HTML generation without sending email.
"""

import sys
from pathlib import Path

# Import functions from the main script
from daily_jeopardy_email import (
    get_all_game_files,
    pick_random_questions,
    generate_html_email
)

def main():
    print("🎯 Testing Daily Jeopardy Email Generation")
    print("=" * 50)
    
    # Check if game files exist
    print("\n📁 Checking for game files...")
    game_files = get_all_game_files()
    print(f"Found {len(game_files)} game files")
    
    if len(game_files) < 3:
        print("❌ Error: Need at least 3 game files to test")
        sys.exit(1)
    
    # Pick random questions
    print("\n🎲 Selecting 3 random questions...")
    try:
        questions = pick_random_questions(3)
        
        if len(questions) < 3:
            print(f"⚠️  Warning: Only found {len(questions)} valid questions")
        
        print(f"\n✅ Selected {len(questions)} questions:\n")
        for i, q in enumerate(questions, 1):
            print(f"Question {i}:")
            print(f"  Category: {q['category']}")
            print(f"  Value: {q['value']}")
            print(f"  Round: {q['round']}")
            print(f"  Daily Double: {'Yes' if q['daily_double'] else 'No'}")
            print(f"  Clue: {q['clue'][:80]}...")
            print(f"  Answer: {q['answer']}")
            print(f"  Game: #{q['game_id']} ({q['air_date']})")
            print()
        
        # Generate HTML
        print("\n📝 Generating HTML email...")
        html = generate_html_email(questions)
        
        # Save to test file
        test_file = Path(__file__).parent / "test_email.html"
        with open(test_file, 'w') as f:
            f.write(html)
        
        print(f"✅ HTML email generated successfully!")
        print(f"📄 Saved to: {test_file}")
        print(f"\nOpen this file in your browser to preview the email:")
        print(f"  file://{test_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

