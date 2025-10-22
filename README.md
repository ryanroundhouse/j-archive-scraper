# Jeopardy J-Archive Scraper

A Python script to scrape Jeopardy game data from [J-Archive](https://j-archive.com/).

## Features

Extracts the following data from J-Archive game pages:
- Episode number and air date
- Contestant information (name, description, previous winnings)
- Jeopardy Round (categories, clues, answers)
- Double Jeopardy Round (categories, clues, answers)
- Final Jeopardy (category, clue, answer)
- Daily Double detection and values
- Final scores and remarks (champion status, prize money)
- Automatic output directory creation (`output/` folder)
- Files organized by year/month (e.g., `output/2025/10/`)
- Error detection for missing/invalid game IDs
- Batch scraping with success/failure tracking
- Season scraping - scrape all games from a season page
- Support for special tournaments (Celebrity Jeopardy, Masters, ToC, etc.)
- Utility script to reorganize existing files

## Installation

1. Create and activate a virtual environment (recommended):

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. When you're done, deactivate the virtual environment:
```bash
deactivate
```

## Usage

### Single Game Scraping

Basic usage with a game ID:
```bash
python scraper.py 9293
```

Specify a custom output filename:
```bash
python scraper.py 9293 my_output.json
```

The game ID can be found in the URL. For example:
- URL: `https://j-archive.com/showgame.php?game_id=9293`
- Game ID: `9293`

### Batch Scraping

Scrape a range of games:
```bash
python batch_scraper.py 9290 9295
```

Scrape specific games:
```bash
python batch_scraper.py --list 9293 9294 9295
```

Add a delay between requests (recommended):
```bash
# Range mode - positional or --delay flag
python batch_scraper.py 9290 9295 2.0
python batch_scraper.py 9290 9295 --delay 2.0

# List mode - --delay flag
python batch_scraper.py --list 9293 9294 --delay 2.0
```

### Season Scraping

Scrape all games from a season page:
```bash
# Using full URL
python season_scraper.py https://j-archive.com/showseason.php?season=pcj

# Using season code
python season_scraper.py pcj

# With custom delay
python season_scraper.py pcj 2.0

# With custom output directory (keeps seasons separate)
python season_scraper.py pcj 2.0 output_celebrity
python season_scraper.py toc 2.0 output_toc
python season_scraper.py masters 2.0 output_masters
```

**Common season codes:**
- `42` - Current season
- `41` - Last season
- `pcj` - Primetime Celebrity Jeopardy!
- `toc` - Tournament of Champions
- `masters` - Jeopardy! Masters

**Custom output directories:** By default, all games are saved to `output/`. Use the third parameter to specify a different directory for organizing different tournaments or seasons separately.

## Output Format

The script generates a JSON file with the following structure:

```json
{
  "game_id": 9293,
  "episode_number": "9416",
  "air_date": "Monday, October 20, 2025",
  "contestants": [
    {
      "name": "Amanda Tholke",
      "description": "a criminal defense attorney from Cincinnati, Ohio",
      "previous_winnings": null
    },
    {
      "name": "Nick Petrilli",
      "description": "a casino surveillance manager from Binghamton, New York",
      "previous_winnings": null
    },
    {
      "name": "Dargan Ware",
      "description": "an attorney and writer from Bessemer, Alabama",
      "previous_winnings": "$26,200"
    }
  ],
  "jeopardy_round": {
    "categories": [
      "EVERYTHING'S COMING UP ROSES",
      "BOOK TITLE ADJECTIVES",
      "PUMPKIN CARVING",
      "ANIMALS",
      "AUTOMOTIVE OPTIONS",
      "POSTSEASON HEROES WITH MLB ON FOX"
    ],
    "clues": [
      {
        "value": "$200",
        "clue": "In Pasadena, California, 1001 this Drive is the site of a very big building of the same name",
        "answer": "the Rose Bowl",
        "daily_double": false,
        "category": "EVERYTHING'S COMING UP ROSES",
        "category_index": 0
      },
      {
        "value": "$2,800",
        "clue": "Found on many cars manufactured after 2002, the latch system provides secure attachment points for these",
        "answer": "(child) car seats",
        "daily_double": true,
        "category": "AUTOMOTIVE OPTIONS",
        "category_index": 4
      }
    ]
  },
  "double_jeopardy_round": {
    "categories": [
      "THE LIBRARY OF ALEXANDRIA",
      "THIS IS A HOLDUP...! MOVIE",
      "KINGS & QUEENS",
      "A FEW CLUES ABOUT A WORD",
      "BURY ME NOT",
      "ON THE LONE PRAIRIE"
    ],
    "clues": []
  },
  "final_jeopardy": {
    "category": "CELEBRITY AUTHORS",
    "clue": "A 1984 trip to Normandy inspired this journalist to write a book that popularized a term for an era of Americans",
    "answer": "Tom Brokaw"
  },
  "final_scores": [
    {
      "contestant": "Dargan",
      "final_score": "$21,601",
      "remarks": "2-day champion: $47,801"
    },
    {
      "contestant": "Nick",
      "final_score": "$4,200",
      "remarks": "2nd place: $3,000"
    },
    {
      "contestant": "Amanda",
      "final_score": "$0",
      "remarks": "3rd place: $2,000"
    }
  ]
}
```

## Example

```bash
python scraper.py 9293
```

Output:
```
Scraping game 9293...
Successfully scraped and saved to output/jeopardy_game_9293.json

Episode: #9416 - Monday, October 20, 2025
Contestants: 3
Jeopardy Round: 6 categories, 30 clues
Double Jeopardy Round: 6 categories, 30 clues
Final Jeopardy: CELEBRITY AUTHORS
```

All JSON files are saved to the `output/` directory (or a custom directory), organized by year and month based on the episode air date.

**Example directory structure:**
```
output/                      # Regular season games
└── 2025/
    └── 10/
        ├── jeopardy_game_9289.json
        ├── jeopardy_game_9290.json
        └── jeopardy_game_9293.json

output_celebrity/            # Celebrity Jeopardy (if scraped separately)
├── 2022/
│   ├── 09/  (1 file)
│   ├── 10/  (5 files)
│   └── 11/  (2 files)
├── 2023/
│   └── ...
└── 2024/
    └── ...

output_toc/                  # Tournament of Champions (if scraped separately)
└── ...
```

**Reorganizing existing files:**
If you have existing JSON files in the root of the output directory, you can reorganize them into year/month folders by running:
```bash
python reorganize_output.py
```

## Notes

- The scraper respects the J-Archive website structure as of October 2025
- Some clues may have incomplete data if the page structure varies
- Daily Double clues are marked with `"daily_double": true`
- Please be respectful of the J-Archive website and avoid excessive scraping

## License

This tool is for educational and personal use. The Jeopardy! game show and all elements thereof are the property of Jeopardy Productions, Inc.

