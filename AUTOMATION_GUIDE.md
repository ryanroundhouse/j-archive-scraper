# Automation Guide for Daily Jeopardy Email

## Quick Start

### 1. Test the Script

```bash
cd /Users/rg/git/jeopardy-scrape
./send_daily_jeopardy.sh
```

This will:
- Activate the virtual environment
- Run the daily Jeopardy email script
- Send you 3 random questions via email

### 2. Set Up Daily Automation

**Edit your crontab:**
```bash
crontab -e
```

**Add one of these lines:**

```bash
# Send daily at 9:00 AM
0 9 * * * /Users/rg/git/jeopardy-scrape/send_daily_jeopardy.sh

# With logging (recommended)
0 9 * * * /Users/rg/git/jeopardy-scrape/send_daily_jeopardy.sh >> /Users/rg/git/jeopardy-scrape/daily_email.log 2>&1
```

**Save and exit** (in vi/vim: press `Esc`, type `:wq`, press Enter)

### 3. Verify Cron Setup

```bash
# List your cron jobs
crontab -l

# Check if cron service is running (macOS)
sudo launchctl list | grep cron
```

## Cron Schedule Examples

```bash
# Time format: minute hour day month day-of-week

0 7 * * *       # 7:00 AM every day
0 9 * * 1-5     # 9:00 AM weekdays only (Mon-Fri)
0 10 * * 0      # 10:00 AM every Sunday
30 8 * * *      # 8:30 AM every day
0 6,18 * * *    # 6:00 AM and 6:00 PM daily
```

## What the Shell Script Does

The `send_daily_jeopardy.sh` script:

1. **Finds its own location** - works no matter where you call it from
2. **Changes to the project directory** - ensures correct working directory
3. **Activates the virtual environment** - loads Python dependencies
4. **Runs the email script** - sends your daily Jeopardy questions
5. **Cleans up** - deactivates the virtual environment
6. **Returns status** - exits with the Python script's exit code

## Troubleshooting

### Cron Job Not Running?

**Check cron logs (macOS):**
```bash
log show --predicate 'process == "cron"' --last 1h
```

**Check your email script logs:**
```bash
tail -f /Users/rg/git/jeopardy-scrape/daily_email.log
```

### Permission Denied?

Make sure the script is executable:
```bash
chmod +x /Users/rg/git/jeopardy-scrape/send_daily_jeopardy.sh
```

### Environment Variables Not Loading?

Cron runs in a minimal environment. The script is designed to work with this, but if you have issues:

```bash
# Option 1: Use absolute paths in your .env file

# Option 2: Source your profile in the cron job
0 9 * * * source ~/.bash_profile && /Users/rg/git/jeopardy-scrape/send_daily_jeopardy.sh
```

### Email Not Sending?

1. **Check your .env file exists:**
   ```bash
   ls -la /Users/rg/git/jeopardy-scrape/.env
   ```

2. **Verify all variables are set:**
   ```bash
   cat /Users/rg/git/jeopardy-scrape/.env
   ```

3. **Test manually:**
   ```bash
   cd /Users/rg/git/jeopardy-scrape
   source venv/bin/activate
   python daily_jeopardy_email.py
   ```

4. **Check Mailgun dashboard** for delivery status

## Viewing Logs

**If you set up logging in your cron job:**

```bash
# View the entire log
cat /Users/rg/git/jeopardy-scrape/daily_email.log

# View last 20 lines
tail -20 /Users/rg/git/jeopardy-scrape/daily_email.log

# Follow the log in real-time
tail -f /Users/rg/git/jeopardy-scrape/daily_email.log

# View logs from a specific date
grep "2025-10-22" /Users/rg/git/jeopardy-scrape/daily_email.log
```

## Disabling the Daily Email

**Temporarily disable:**
```bash
crontab -e
# Add a # at the start of the line to comment it out:
# 0 9 * * * /Users/rg/git/jeopardy-scrape/send_daily_jeopardy.sh
```

**Remove completely:**
```bash
crontab -e
# Delete the entire line, save and exit
```

## Advanced: Multiple Schedules

You can send emails at different times:

```bash
crontab -e

# Morning email at 7 AM
0 7 * * * /Users/rg/git/jeopardy-scrape/send_daily_jeopardy.sh >> /Users/rg/git/jeopardy-scrape/daily_email_morning.log 2>&1

# Evening email at 7 PM
0 19 * * * /Users/rg/git/jeopardy-scrape/send_daily_jeopardy.sh >> /Users/rg/git/jeopardy-scrape/daily_email_evening.log 2>&1
```

Each run will pick 3 different random questions!

## Testing Without Waiting

Don't want to wait for the scheduled time?

```bash
# Run it manually right now
./send_daily_jeopardy.sh

# Or just test the email generation without sending
python test_email_generation.py
```

Enjoy your daily Jeopardy challenge! 🎯


