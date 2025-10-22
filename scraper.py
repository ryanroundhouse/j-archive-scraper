#!/usr/bin/env python3
"""
Jeopardy J-Archive Scraper
Scrapes episode data including questions, answers, categories, and contestants
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional


class JeopardyScraper:
    def __init__(self, game_id: int):
        self.game_id = game_id
        self.url = f"https://j-archive.com/showgame.php?game_id={game_id}"
        self.soup = None
        
    def fetch_page(self) -> bool:
        """Fetch the page content"""
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check for error messages
            body_text = self.soup.get_text()
            if 'ERROR:' in body_text or 'No game' in body_text:
                error_msg = body_text[body_text.find('ERROR:'):body_text.find('ERROR:') + 100].strip()
                print(f"Error from J-Archive: {error_msg}")
                return False
            
            return True
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return False
    
    def extract_episode_info(self) -> Dict:
        """Extract episode number and date"""
        # Try to find from page heading first (more reliable)
        heading = self.soup.find('h1')
        if heading:
            heading_text = heading.text.strip()
            
            # Pattern 1: "Show #9416 - Monday, October 20, 2025"
            match = re.search(r'Show #(\d+) - (.+)', heading_text)
            if match:
                return {
                    "episode_number": match.group(1),
                    "air_date": match.group(2).strip()
                }
            
            # Pattern 2: "Jeopardy! Masters game #21 - Wednesday, May 1, 2024"
            # Or other special games that don't have "Show #"
            match = re.search(r'(?:game|Game) #(\d+) - (.+)', heading_text)
            if match:
                return {
                    "episode_number": match.group(1),
                    "air_date": match.group(2).strip()
                }
            
            # Pattern 3: Just extract the date if there's a dash
            match = re.search(r' - ([A-Z][a-z]+day, [A-Z][a-z]+ \d+, \d{4})', heading_text)
            if match:
                return {
                    "episode_number": None,
                    "air_date": match.group(1).strip()
                }
        
        # Try to find from page title as fallback
        title = self.soup.find('title')
        if title:
            title_text = title.text.strip()
            
            # Pattern: "Show #9416 - Monday, October 20, 2025"
            match = re.search(r'Show #(\d+)', title_text)
            if match:
                episode = match.group(1)
                # Try to extract date from title
                date_match = re.search(r'aired (\d{4}-\d{2}-\d{2})', title_text)
                if date_match:
                    # Convert YYYY-MM-DD to readable format
                    try:
                        from datetime import datetime
                        date_obj = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                        air_date = date_obj.strftime("%A, %B %d, %Y")
                        return {
                            "episode_number": episode,
                            "air_date": air_date
                        }
                    except:
                        pass
                return {
                    "episode_number": episode,
                    "air_date": None
                }
            
            # Try to extract date from "aired YYYY-MM-DD" format in title
            match = re.search(r'aired (\d{4}-\d{2}-\d{2})', title_text)
            if match:
                try:
                    date_obj = datetime.strptime(match.group(1), "%Y-%m-%d")
                    air_date = date_obj.strftime("%A, %B %d, %Y")
                    return {
                        "episode_number": None,
                        "air_date": air_date
                    }
                except:
                    pass
        
        return {"episode_number": None, "air_date": None}
    
    def extract_contestants(self) -> List[Dict]:
        """Extract contestant information"""
        contestants = []
        
        # Find the contestants table
        table = self.soup.find('table')
        if table:
            # Look for contestant links
            contestant_links = table.find_all('a', href=re.compile(r'showplayer\.php'))
            
            for link in contestant_links:
                name = link.text.strip()
                # Get the text following the link (description)
                parent = link.parent
                text = parent.get_text()
                
                # Extract description (everything after the name)
                description_match = re.search(f'{re.escape(name)},?\\s*(.+?)(?=\\[|$)', text)
                description = description_match.group(1).strip() if description_match else ""
                
                # Check if they're a returning champion
                is_champion = 'day' in description.lower() and 'champion' not in description.lower()
                winnings_match = re.search(r'\$[\d,]+', text)
                previous_winnings = winnings_match.group(0) if winnings_match else None
                
                contestants.append({
                    "name": name,
                    "description": description,
                    "previous_winnings": previous_winnings
                })
        
        return contestants
    
    def extract_clue(self, clue_elem) -> Optional[Dict]:
        """Extract a single clue (question and answer)"""
        if not clue_elem:
            return None
        
        # Get the value
        value = None
        clue_value = clue_elem.find('td', class_=re.compile(r'clue_value'))
        if clue_value:
            value_text = clue_value.get_text(strip=True)
            # Handle Daily Double values
            if 'DD:' in value_text:
                value = value_text.replace('DD:', '').strip()
            else:
                value = value_text
        
        # Get the clue text (visible one without _r suffix)
        clue_text_elem = None
        all_clue_texts = clue_elem.find_all('td', class_='clue_text')
        for elem in all_clue_texts:
            elem_id = elem.get('id', '')
            # Find the visible one (not ending with _r and not having display:none)
            if not elem_id.endswith('_r'):
                clue_text_elem = elem
                break
        
        if not clue_text_elem:
            return None
        
        # Get clue text
        clue_text = clue_text_elem.get_text(strip=True)
        
        # Get the answer from the hidden td (with _r suffix)
        answer = None
        clue_id = clue_text_elem.get('id', '')
        if clue_id:
            # Look for the response td (has _r suffix)
            response_elem = clue_elem.find('td', id=f'{clue_id}_r')
            if response_elem:
                correct_response = response_elem.find('em', class_='correct_response')
                if correct_response:
                    answer = correct_response.get_text(strip=True)
        
        # Check for Daily Double
        is_daily_double = 'DD:' in str(clue_value) if clue_value else False
        
        return {
            "value": value,
            "clue": clue_text,
            "answer": answer,
            "daily_double": is_daily_double
        }
    
    def extract_round(self, round_id: str) -> Dict:
        """Extract all clues from a round (jeopardy or double_jeopardy)"""
        round_div = self.soup.find('div', id=round_id)
        if not round_div:
            return {"categories": [], "clues": []}
        
        # Extract categories
        categories = []
        category_names = round_div.find_all('td', class_='category_name')
        for cat in category_names:
            category_text = cat.get_text(strip=True)
            # Remove any parenthetical host comments
            category_text = re.sub(r'\(.*?\)', '', category_text).strip()
            categories.append(category_text)
        
        # Extract clues
        clues = []
        clue_rows = round_div.find_all('tr')
        
        for row in clue_rows:
            clue_cells = row.find_all('td', class_='clue')
            if clue_cells:
                row_clues = []
                for i, cell in enumerate(clue_cells):
                    clue_data = self.extract_clue(cell)
                    if clue_data and i < len(categories):
                        clue_data['category'] = categories[i]
                        clue_data['category_index'] = i
                    row_clues.append(clue_data)
                clues.extend([c for c in row_clues if c])
        
        return {
            "categories": categories,
            "clues": clues
        }
    
    def extract_final_jeopardy(self) -> Dict:
        """Extract Final Jeopardy information"""
        final_div = self.soup.find('div', id='final_jeopardy_round')
        if not final_div:
            return {"category": None, "clue": None, "answer": None}
        
        # Get category
        category = None
        category_elem = final_div.find('td', class_='category_name')
        if category_elem:
            category = category_elem.get_text(strip=True)
        
        # Get clue text (look for clue_FJ, not clue_FJ_r)
        clue_text_elem = final_div.find('td', id='clue_FJ')
        clue = None
        answer = None
        
        if clue_text_elem:
            # Get clue text from the visible td
            clue = clue_text_elem.get_text(strip=True)
            
            # Get answer from the hidden response td (clue_FJ_r)
            response_elem = final_div.find('td', id='clue_FJ_r')
            if response_elem:
                correct_response = response_elem.find('em', class_='correct_response')
                if correct_response:
                    answer = correct_response.get_text(strip=True)
        
        return {
            "category": category,
            "clue": clue,
            "answer": answer
        }
    
    def extract_final_scores(self) -> List[Dict]:
        """Extract final scores for all contestants"""
        scores = []
        
        # Find the "Final scores:" heading
        h3s = self.soup.find_all('h3')
        for h3 in h3s:
            if 'Final scores' in h3.get_text():
                # Get the next table after this heading
                table = h3.find_next('table')
                if table:
                    rows = table.find_all('tr')
                    
                    # Extract contestant names (first row)
                    names = []
                    if len(rows) > 0:
                        name_cells = rows[0].find_all('td', class_='score_player_nickname')
                        names = [cell.get_text(strip=True) for cell in name_cells]
                    
                    # Extract scores (second row)
                    score_values = []
                    if len(rows) > 1:
                        score_cells = rows[1].find_all('td', class_='score_positive')
                        score_values = [cell.get_text(strip=True) for cell in score_cells]
                    
                    # Extract remarks (third row) - optional
                    remarks = []
                    if len(rows) > 2:
                        remark_cells = rows[2].find_all('td', class_='score_remarks')
                        remarks = [cell.get_text(strip=True) for cell in remark_cells]
                    
                    # Combine the data
                    for i, name in enumerate(names):
                        score_data = {"contestant": name}
                        if i < len(score_values):
                            score_data["final_score"] = score_values[i]
                        if i < len(remarks):
                            score_data["remarks"] = remarks[i]
                        scores.append(score_data)
                    
                    break
        
        return scores
    
    def scrape(self) -> Dict:
        """Main scraping method"""
        if not self.fetch_page():
            return None
        
        # Extract all data
        episode_info = self.extract_episode_info()
        contestants = self.extract_contestants()
        jeopardy_round = self.extract_round('jeopardy_round')
        double_jeopardy_round = self.extract_round('double_jeopardy_round')
        final_jeopardy = self.extract_final_jeopardy()
        final_scores = self.extract_final_scores()
        
        return {
            "game_id": self.game_id,
            "episode_number": episode_info["episode_number"],
            "air_date": episode_info["air_date"],
            "contestants": contestants,
            "jeopardy_round": jeopardy_round,
            "double_jeopardy_round": double_jeopardy_round,
            "final_jeopardy": final_jeopardy,
            "final_scores": final_scores
        }
    
    def save_to_json(self, data: Dict, filename: str = None, output_dir: str = "output") -> str:
        """Save scraped data to JSON file in the output directory organized by year/month"""
        # Try to get year and month from air_date
        air_date = data.get('air_date')
        year_month_path = ""
        
        if air_date:
            try:
                # Parse the date (format: "Monday, October 20, 2025")
                date_obj = datetime.strptime(air_date, "%A, %B %d, %Y")
                year = str(date_obj.year)
                month = f"{date_obj.month:02d}"  # Zero-padded month
                year_month_path = os.path.join(year, month)
            except (ValueError, AttributeError):
                # If date parsing fails, just use the base output directory
                pass
        
        # Create full output path with year/month subdirectories
        full_output_dir = os.path.join(output_dir, year_month_path) if year_month_path else output_dir
        os.makedirs(full_output_dir, exist_ok=True)
        
        if filename is None:
            filename = f"jeopardy_game_{self.game_id}.json"
        
        # Create full file path
        if not os.path.dirname(filename):
            # If filename has no directory component, add the full output path
            filename = os.path.join(full_output_dir, filename)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filename


def main():
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <game_id> [output_file]")
        print("Example: python scraper.py 9293")
        sys.exit(1)
    
    game_id = int(sys.argv[1])
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    scraper = JeopardyScraper(game_id)
    print(f"Scraping game {game_id}...")
    
    data = scraper.scrape()
    if data:
        # Check if we actually got data (not just an empty structure)
        has_data = (
            data.get('episode_number') or 
            len(data.get('contestants', [])) > 0 or
            len(data.get('jeopardy_round', {}).get('clues', [])) > 0
        )
        
        if has_data:
            filename = scraper.save_to_json(data, output_file)
            print(f"Successfully scraped and saved to {filename}")
            
            # Print summary
            print(f"\nEpisode: #{data['episode_number']} - {data['air_date']}")
            print(f"Contestants: {len(data['contestants'])}")
            print(f"Jeopardy Round: {len(data['jeopardy_round']['categories'])} categories, {len(data['jeopardy_round']['clues'])} clues")
            print(f"Double Jeopardy Round: {len(data['double_jeopardy_round']['categories'])} categories, {len(data['double_jeopardy_round']['clues'])} clues")
            print(f"Final Jeopardy: {data['final_jeopardy']['category']}")
        else:
            print("Failed to scrape data - game may not exist or page is empty")
            sys.exit(1)
    else:
        print("Failed to scrape data")
        sys.exit(1)


if __name__ == "__main__":
    main()

