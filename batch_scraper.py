#!/usr/bin/env python3
"""
Batch Jeopardy J-Archive Scraper
Scrapes multiple episodes at once
"""

import sys
import time
from scraper import JeopardyScraper


def scrape_range(start_id: int, end_id: int, delay: float = 1.0):
    """
    Scrape a range of game IDs
    
    Args:
        start_id: First game ID to scrape
        end_id: Last game ID to scrape (inclusive)
        delay: Delay between requests in seconds (be respectful to the server)
    """
    success_count = 0
    fail_count = 0
    
    for game_id in range(start_id, end_id + 1):
        print(f"\nScraping game {game_id}...")
        
        scraper = JeopardyScraper(game_id)
        data = scraper.scrape()
        
        if data:
            # Check if we actually got data (not just an empty structure)
            has_data = (
                data.get('episode_number') or 
                len(data.get('contestants', [])) > 0 or
                len(data.get('jeopardy_round', {}).get('clues', [])) > 0
            )
            
            if has_data:
                filename = scraper.save_to_json(data)
                print(f"✓ Saved to {filename}")
                success_count += 1
                
                # Print summary
                if data['episode_number']:
                    print(f"  Episode #{data['episode_number']} - {data['air_date']}")
            else:
                print(f"✗ Failed to scrape game {game_id} - no data found")
                fail_count += 1
        else:
            print(f"✗ Failed to scrape game {game_id}")
            fail_count += 1
        
        # Be respectful - add delay between requests
        if game_id < end_id:
            time.sleep(delay)
    
    return success_count, fail_count


def scrape_list(game_ids: list, delay: float = 1.0):
    """
    Scrape a list of specific game IDs
    
    Args:
        game_ids: List of game IDs to scrape
        delay: Delay between requests in seconds
    """
    success_count = 0
    fail_count = 0
    
    for i, game_id in enumerate(game_ids):
        print(f"\nScraping game {game_id} ({i+1}/{len(game_ids)})...")
        
        scraper = JeopardyScraper(game_id)
        data = scraper.scrape()
        
        if data:
            # Check if we actually got data (not just an empty structure)
            has_data = (
                data.get('episode_number') or 
                len(data.get('contestants', [])) > 0 or
                len(data.get('jeopardy_round', {}).get('clues', [])) > 0
            )
            
            if has_data:
                filename = scraper.save_to_json(data)
                print(f"✓ Saved to {filename}")
                success_count += 1
                
                # Print summary
                if data['episode_number']:
                    print(f"  Episode #{data['episode_number']} - {data['air_date']}")
            else:
                print(f"✗ Failed to scrape game {game_id} - no data found")
                fail_count += 1
        else:
            print(f"✗ Failed to scrape game {game_id}")
            fail_count += 1
        
        # Be respectful - add delay between requests
        if i < len(game_ids) - 1:
            time.sleep(delay)
    
    return success_count, fail_count


def main():
    if len(sys.argv) < 2:
        print("Batch Jeopardy Scraper")
        print("\nUsage:")
        print("  python batch_scraper.py <start_id> <end_id> [delay]")
        print("  python batch_scraper.py <start_id> <end_id> --delay <seconds>")
        print("  python batch_scraper.py --list <id1> <id2> <id3> ... [--delay <seconds>]")
        print("\nExamples:")
        print("  python batch_scraper.py 9290 9295")
        print("  python batch_scraper.py 9290 9295 2.0")
        print("  python batch_scraper.py 9290 9295 --delay 2.0")
        print("  python batch_scraper.py --list 9293 9294 9295")
        print("  python batch_scraper.py --list 9293 9294 --delay 2.0")
        sys.exit(1)
    
    # Parse command line arguments
    if sys.argv[1] == '--list':
        # List mode
        game_ids = []
        delay = 1.0
        
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == '--delay':
                if i + 1 < len(sys.argv):
                    delay = float(sys.argv[i + 1])
                    i += 2
                else:
                    print("Error: --delay requires a value")
                    sys.exit(1)
            else:
                game_ids.append(int(sys.argv[i]))
                i += 1
        
        if not game_ids:
            print("Error: No game IDs provided")
            sys.exit(1)
        
        print(f"Scraping {len(game_ids)} games with {delay}s delay between requests...")
        success_count, fail_count = scrape_list(game_ids, delay)
    else:
        # Range mode
        try:
            start_id = int(sys.argv[1])
            end_id = int(sys.argv[2])
        except (ValueError, IndexError):
            print("Error: Invalid start_id or end_id")
            sys.exit(1)
        
        # Check for --delay flag or positional delay
        delay = 1.0
        if len(sys.argv) > 3:
            if sys.argv[3] == '--delay':
                if len(sys.argv) > 4:
                    try:
                        delay = float(sys.argv[4])
                    except ValueError:
                        print("Error: --delay requires a numeric value")
                        sys.exit(1)
                else:
                    print("Error: --delay requires a value")
                    sys.exit(1)
            else:
                try:
                    delay = float(sys.argv[3])
                except ValueError:
                    print(f"Error: Invalid delay value '{sys.argv[3]}'")
                    sys.exit(1)
        
        print(f"Scraping games {start_id} to {end_id} with {delay}s delay between requests...")
        success_count, fail_count = scrape_range(start_id, end_id, delay)
    
    print("\n" + "="*60)
    print("Batch scraping complete!")
    print(f"✓ Successful: {success_count}")
    if fail_count > 0:
        print(f"✗ Failed: {fail_count}")
    print("="*60)


if __name__ == "__main__":
    main()

