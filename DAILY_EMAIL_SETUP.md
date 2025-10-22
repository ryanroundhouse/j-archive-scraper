# Daily Jeopardy Email Setup Guide

## Quick Start

### 1. Create your .env file

Copy the example and fill in your Mailgun credentials:

```bash
cp env.example .env
```

Edit `.env` with your actual values:
- `MAILGUN_DOMAIN`: Your Mailgun domain (e.g., `mg.yourdomain.com` or `sandbox123.mailgun.org`)
- `MAILGUN_API_KEY`: Your Mailgun API key (starts with `key-`)
- `FROM_EMAIL`: Email address to send from (must be authorized in Mailgun)
- `TO_EMAIL`: Your email address (where you want to receive the daily questions)

### 2. Get Mailgun Credentials

1. Sign up for a free account at [mailgun.com](https://www.mailgun.com/)
2. Go to your [Mailgun dashboard](https://app.mailgun.com/)
3. Find your API key in the "API Keys" section
4. Use the sandbox domain provided, or add your own domain
5. For sandbox domains, you need to add authorized recipients in the Mailgun dashboard

### 3. Test the Email (without sending)

```bash
source venv/bin/activate  # if not already activated
python test_email_generation.py
```

This will:
- Pick 3 random Jeopardy questions from different games
- Generate an HTML email
- Save it as `test_email.html`
- You can open this file in your browser to preview

### 4. Send Your First Daily Email

```bash
python daily_jeopardy_email.py
```

## What the Email Contains

Each daily email includes:

1. **3 Random Questions** from 3 different Jeopardy games
2. **Beautiful Jeopardy-Style Design**:
   - Blue gradient background (like the show)
   - Gold accents and borders
   - Category names and dollar values
3. **Mobile-Friendly Layout** (works perfectly on ALL devices):
   - **Questions First**: All 3 questions displayed at the top
   - **Think About It**: Mentally answer each question as you read
   - **Scroll to Reveal**: Scroll past a spacer section to see all answers
   - **Answers Section**: All answers clearly displayed in separate cards at the bottom
   - Works reliably on mobile, desktop, and all email clients!
4. **Game Metadata**:
   - Game ID number
   - Original air date
   - Round (Jeopardy! or Double Jeopardy!)
   - Daily Double indicator (if applicable)

## Automation

To receive questions daily, set up a cron job (Mac/Linux) or Task Scheduler (Windows).

**Example cron job (9 AM daily):**

```bash
# Edit your crontab
crontab -e

# Add this line (adjust paths):
0 9 * * * cd /Users/rg/git/jeopardy-scrape && /Users/rg/git/jeopardy-scrape/venv/bin/python daily_jeopardy_email.py
```

## Troubleshooting

### "Missing required environment variables"
- Make sure your `.env` file exists and has all 4 variables set
- Check that there are no typos in the variable names

### "Failed to send email: 401"
- Your API key is incorrect
- Check that you copied the full API key including the `key-` prefix

### "Failed to send email: 400"
- Check that your FROM_EMAIL is authorized in Mailgun
- For sandbox domains, make sure TO_EMAIL is added as an authorized recipient

### "Not enough game files"
- Make sure you have scraped at least 3 games into the `output/` directory
- Run `python batch_scraper.py 9290 9295` to scrape some games first

## Files Created

- `daily_jeopardy_email.py` - Main email script
- `test_email_generation.py` - Test script (no email sent)
- `env.example` - Template for your .env file
- `.env` - Your actual credentials (not tracked by git)
- `test_email.html` - Preview of the generated email (not tracked by git)

## Dependencies

All installed via `requirements.txt`:
- `requests` - For HTTP requests (Mailgun API)
- `beautifulsoup4` - Used by scrapers
- `python-dotenv` - Load environment variables from .env

Enjoy your daily Jeopardy! challenge! 🎯

