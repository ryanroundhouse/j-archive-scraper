#!/usr/bin/env python3
"""
Daily Jeopardy Email Script
Picks 3 random Jeopardy questions from 3 different games and sends them via email.
"""

import os
import json
import random
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

def get_all_game_files():
    """Get all JSON game files from the output directory."""
    output_dir = Path(__file__).parent / "output"
    game_files = list(output_dir.glob("**/*.json"))
    return game_files

def load_game_data(game_file):
    """Load and parse a game JSON file."""
    with open(game_file, 'r') as f:
        return json.load(f)

def get_random_clue(game_data):
    """Get a random clue from a game's jeopardy or double jeopardy rounds."""
    # Combine both rounds
    all_clues = []
    
    if 'jeopardy_round' in game_data and game_data['jeopardy_round']:
        all_clues.extend([
            {**clue, 'round': 'Jeopardy!'}
            for clue in game_data['jeopardy_round'].get('clues', [])
        ])
    
    if 'double_jeopardy_round' in game_data and game_data['double_jeopardy_round']:
        all_clues.extend([
            {**clue, 'round': 'Double Jeopardy!'}
            for clue in game_data['double_jeopardy_round'].get('clues', [])
        ])
    
    # Filter out clues without both clue and answer
    valid_clues = [c for c in all_clues if c.get('clue') and c.get('answer')]
    
    if not valid_clues:
        return None
    
    return random.choice(valid_clues)

def pick_random_questions(num_questions=3):
    """Pick random questions from different games."""
    game_files = get_all_game_files()
    
    if len(game_files) < num_questions:
        raise ValueError(f"Not enough game files. Found {len(game_files)}, need {num_questions}")
    
    questions = []
    used_game_files = set()
    max_attempts = len(game_files)  # Try all games if needed
    attempts = 0
    
    while len(questions) < num_questions and attempts < max_attempts:
        # Get remaining game files that haven't been tried yet
        available_games = [gf for gf in game_files if gf not in used_game_files]
        
        if not available_games:
            break  # No more games to try
        
        # Pick a random game from available games
        game_file = random.choice(available_games)
        used_game_files.add(game_file)
        attempts += 1
        
        try:
            game_data = load_game_data(game_file)
            clue = get_random_clue(game_data)
            
            if clue:
                questions.append({
                    'game_id': game_data.get('game_id'),
                    'air_date': game_data.get('air_date'),
                    'category': clue.get('category'),
                    'value': clue.get('value'),
                    'clue': clue.get('clue'),
                    'answer': clue.get('answer'),
                    'round': clue.get('round'),
                    'daily_double': clue.get('daily_double', False)
                })
            else:
                print(f"Skipping {game_file}: No valid clues found")
        except Exception as e:
            print(f"Error processing {game_file}: {e}")
            continue
    
    if len(questions) < num_questions:
        raise ValueError(f"Could not find {num_questions} valid questions. Only found {len(questions)} after checking {attempts} games.")
    
    return questions

def generate_html_email(questions):
    """Generate HTML email content with Jeopardy-style board."""
    
    html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #0c1445 0%, #1a2980 100%);
            margin: 0;
            padding: 20px;
            color: #ffffff;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: #0c1445;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .title {
            font-size: 48px;
            font-weight: bold;
            color: #ffffff;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.7);
            margin: 0;
            letter-spacing: 2px;
        }
        .subtitle {
            font-size: 18px;
            color: #ffd700;
            margin-top: 10px;
        }
        .instructions {
            text-align: center;
            color: #a0a0ff;
            font-size: 16px;
            margin-bottom: 30px;
            padding: 15px;
            background-color: rgba(26, 41, 128, 0.3);
            border-radius: 5px;
            line-height: 1.6;
        }
        .clue-card {
            background: linear-gradient(135deg, #060a2e 0%, #1a2980 100%);
            border: 3px solid #ffd700;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.4);
        }
        .clue-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ffd700;
        }
        .category {
            font-size: 20px;
            font-weight: bold;
            color: #ffd700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .value {
            font-size: 24px;
            font-weight: bold;
            color: #ffd700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        .daily-double {
            background-color: #ff4444;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 14px;
            font-weight: bold;
            margin-left: 10px;
        }
        .round-info {
            font-size: 14px;
            color: #a0a0ff;
            margin-bottom: 10px;
        }
        .clue-text {
            font-size: 20px;
            line-height: 1.6;
            color: #ffffff;
            margin: 20px 0;
            padding: 20px;
            background-color: rgba(26, 41, 128, 0.5);
            border-radius: 5px;
            text-align: center;
        }
        .think-space {
            font-size: 14px;
            color: #ffd700;
            text-align: center;
            margin-top: 20px;
            font-style: italic;
        }
        .game-info {
            font-size: 12px;
            color: #888;
            text-align: center;
            margin-top: 10px;
            font-style: italic;
        }
        .divider {
            border-top: 3px solid #ffd700;
            margin: 50px 0;
            position: relative;
        }
        .divider-text {
            position: absolute;
            top: -12px;
            left: 50%;
            transform: translateX(-50%);
            background-color: #0c1445;
            padding: 0 20px;
            color: #ffd700;
            font-weight: bold;
            font-size: 16px;
        }
        .answers-section {
            margin-top: 50px;
        }
        .answers-header {
            text-align: center;
            font-size: 28px;
            color: #ffd700;
            font-weight: bold;
            margin-bottom: 30px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .answer-card {
            background: linear-gradient(135deg, #1a2050 0%, #2a3080 100%);
            border: 2px solid #ffd700;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .answer-question-num {
            font-size: 18px;
            color: #ffd700;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .answer-category-small {
            font-size: 14px;
            color: #a0a0ff;
            margin-bottom: 15px;
        }
        .answer-label {
            font-size: 14px;
            color: #ffd700;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .answer-text {
            font-size: 22px;
            color: #ffffff;
            background-color: rgba(255, 215, 0, 0.1);
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            border-left: 4px solid #ffd700;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ffd700;
            color: #a0a0ff;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">JEOPARDY!</h1>
            <p class="subtitle">Your Daily Trivia Challenge</p>
        </div>
        <div class="instructions">
            📱 Try answering all questions below, then scroll down to see the answers!
        </div>
"""

    # Questions section
    for i, q in enumerate(questions, 1):
        dd_badge = '<span class="daily-double">DAILY DOUBLE!</span>' if q['daily_double'] else ''
        
        html += f"""
        <div class="clue-card">
            <div class="round-info">Question {i} of {len(questions)} • {q['round']}</div>
            <div class="clue-header">
                <div class="category">{q['category']}</div>
                <div>
                    <span class="value">{q['value']}</span>
                    {dd_badge}
                </div>
            </div>
            <div class="clue-text">
                {q['clue']}
            </div>
            <div class="think-space">🤔 Think you know it?</div>
            <div class="game-info">
                Game #{q['game_id']} • Aired: {q['air_date']}
            </div>
        </div>
"""

    # Divider
    html += """
        <div class="divider">
            <span class="divider-text">⬇️ SCROLL FOR ANSWERS ⬇️</span>
        </div>
        
        <!-- Spacer to create separation -->
        <div style="height: 300px; background: transparent;"></div>
        
        <div class="answers-section">
            <div class="answers-header">📋 Answers</div>
"""

    # Answers section
    for i, q in enumerate(questions, 1):
        html += f"""
        <div class="answer-card">
            <div class="answer-question-num">Question {i}</div>
            <div class="answer-category-small">{q['category']} • {q['value']}</div>
            <div class="answer-label">WHAT IS / WHO IS / WHERE IS...</div>
            <div class="answer-text">
                {q['answer']}
            </div>
        </div>
"""

    html += """
        </div>
        <div class="footer">
            <p>How many did you get right? 🎯</p>
            <p>This is Jeopardy!</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def send_email(to_email, subject, html_content):
    """Send email using Mailgun API."""
    mailgun_domain = os.getenv('MAILGUN_DOMAIN')
    mailgun_api_key = os.getenv('MAILGUN_API_KEY')
    from_email = os.getenv('FROM_EMAIL')
    
    if not all([mailgun_domain, mailgun_api_key, from_email]):
        raise ValueError("Missing required environment variables. Check your .env file.")
    
    # Mailgun API endpoint
    url = f"https://api.mailgun.net/v3/{mailgun_domain}/messages"
    
    # Prepare the email data
    data = {
        "from": from_email,
        "to": to_email,
        "subject": subject,
        "html": html_content
    }
    
    # Send the email via Mailgun API
    response = requests.post(
        url,
        auth=("api", mailgun_api_key),
        data=data
    )
    
    # Check response
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to send email: {response.status_code} - {response.text}")

def main():
    """Main function to run the daily Jeopardy email."""
    print("🎯 Daily Jeopardy Email Generator")
    print("=" * 50)
    
    # Get recipient email from environment or prompt
    recipient = os.getenv('TO_EMAIL')
    if not recipient:
        print("Error: TO_EMAIL not set in .env file")
        return
    
    print(f"\n📧 Recipient: {recipient}")
    print("\n🎲 Selecting random Jeopardy questions...")
    
    try:
        # Pick 3 random questions
        questions = pick_random_questions(3)
        
        if len(questions) < 3:
            print(f"Warning: Only found {len(questions)} valid questions")
        
        print(f"\n✅ Selected {len(questions)} questions:")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q['category']} - {q['value']} (Game #{q['game_id']})")
        
        # Generate HTML email
        print("\n📝 Generating email HTML...")
        html_content = generate_html_email(questions)
        
        # Send email
        print("\n📮 Sending email via Mailgun...")
        subject = "🎯 Your Daily Jeopardy! Challenge"
        
        response = send_email(recipient, subject, html_content)
        
        print("\n✅ Email sent successfully!")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

