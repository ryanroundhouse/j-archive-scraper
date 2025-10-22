#!/usr/bin/env python3
"""
Season Scraper for J-Archive
Scrapes all games from a season page
"""

import requests
from bs4 import BeautifulSoup
import re
import sys
import time
from scraper import JeopardyScraper


def get_game_ids_from_season(season_url: str):
    """
    Extract all game IDs from a season page
    
    Args:
        season_url: URL of the season page (e.g., https://j-archive.com/showseason.php?season=42)
    
    Returns:
        List of game IDs
    """
    print(f"Fetching season page: {season_url}")
    
    try:
        response = requests.get(season_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all links to game pages
        game_ids = []
        links = soup.find_all('a', href=re.compile(r'showgame\.php\?game_id=\d+'))
        
        for link in links:
            href = link.get('href')
            match = re.search(r'game_id=(\d+)', href)
            if match:
                game_id = int(match.group(1))
                if game_id not in game_ids:  # Avoid duplicates
                    game_ids.append(game_id)
        
        # Sort game IDs
        game_ids.sort()
        
        print(f"Found {len(game_ids)} games in this season")
        return game_ids
        
    except requests.RequestException as e:
        print(f"Error fetching season page: {e}")
        return []


def scrape_season(season_url: str, delay: float = 1.5, output_dir: str = "output"):
    """
    Scrape all games from a season
    
    Args:
        season_url: URL of the season page
        delay: Delay between requests in seconds
        output_dir: Base output directory for scraped files
    """
    game_ids = get_game_ids_from_season(season_url)
    
    if not game_ids:
        print("No games found!")
        return
    
    print(f"\nStarting to scrape {len(game_ids)} games with {delay}s delay between requests...")
    print(f"Saving to: {output_dir}/")
    print("="*60)
    
    success_count = 0
    fail_count = 0
    
    for i, game_id in enumerate(game_ids, 1):
        print(f"\n[{i}/{len(game_ids)}] Scraping game {game_id}...")
        
        scraper = JeopardyScraper(game_id)
        data = scraper.scrape()
        
        if data:
            # Check if we actually got data
            has_data = (
                data.get('episode_number') or 
                len(data.get('contestants', [])) > 0 or
                len(data.get('jeopardy_round', {}).get('clues', [])) > 0
            )
            
            if has_data:
                filename = scraper.save_to_json(data, output_dir=output_dir)
                print(f"  ✓ Saved to {filename}")
                success_count += 1
                
                # Print summary
                if data.get('air_date'):
                    episode = data.get('episode_number', 'N/A')
                    print(f"  Episode #{episode} - {data['air_date']}")
            else:
                print(f"  ✗ Failed to scrape game {game_id} - no data found")
                fail_count += 1
        else:
            print(f"  ✗ Failed to scrape game {game_id}")
            fail_count += 1
        
        # Be respectful - add delay between requests
        if i < len(game_ids):
            time.sleep(delay)
    
    print("\n" + "="*60)
    print("Season scraping complete!")
    print(f"✓ Successful: {success_count}")
    if fail_count > 0:
        print(f"✗ Failed: {fail_count}")
    print("="*60)


def main():
    if len(sys.argv) < 2:
        print("Season Scraper for J-Archive")
        print("\nUsage:")
        print("  python season_scraper.py <season_url> [delay] [output_dir]")
        print("  python season_scraper.py <season_code> [delay] [output_dir]")
        print("\nExamples:")
        print("  python season_scraper.py https://j-archive.com/showseason.php?season=42")
        print("  python season_scraper.py pcj 2.0")
        print("  python season_scraper.py pcj 2.0 output_celebrity")
        print("  python season_scraper.py toc 2.0 output_toc")
        print("  python season_scraper.py 42 2.0 output_season42")
        print("\nCommon season codes:")
        print("  42        - Current season (season 42)")
        print("  41        - Last season (season 41)")
        print("  pcj       - Primetime Celebrity Jeopardy!")
        print("  toc       - Tournament of Champions")
        print("  masters   - Jeopardy! Masters")
        sys.exit(1)
    
    season_arg = sys.argv[1]
    delay = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "output"
    
    # If it's a full URL, use it directly
    if season_arg.startswith('http'):
        season_url = season_arg
    else:
        # Otherwise, construct the URL from the season code
        season_url = f"https://j-archive.com/showseason.php?season={season_arg}"
    
    scrape_season(season_url, delay, output_dir)


if __name__ == "__main__":
    main()

