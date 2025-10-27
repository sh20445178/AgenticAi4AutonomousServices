import logging
import json
from datetime import datetime
from typing import Any, Dict, List
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init()

def setup_logging(debug: bool = False) -> logging.Logger:
    """Setup logging configuration"""
    level = logging.DEBUG if debug else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('gemini_agent.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def print_colored(text: str, color: str = 'white') -> None:
    """Print colored text to console"""
    colors = {
        'red': Fore.RED,
        'green': Fore.GREEN,
        'blue': Fore.BLUE,
        'yellow': Fore.YELLOW,
        'magenta': Fore.MAGENTA,
        'cyan': Fore.CYAN,
        'white': Fore.WHITE
    }
    
    color_code = colors.get(color.lower(), Fore.WHITE)
    print(f"{color_code}{text}{Style.RESET_ALL}")

def save_conversation(conversation: List[Dict[str, Any]], filename: str = None) -> str:
    """Save conversation history to JSON file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(conversation, f, indent=2, ensure_ascii=False)
        return filename
    except Exception as e:
        print_colored(f"Error saving conversation: {e}", 'red')
        return None

def load_conversation(filename: str) -> List[Dict[str, Any]]:
    """Load conversation history from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print_colored(f"Error loading conversation: {e}", 'red')
        return []

def format_response(response: str, max_width: int = 80) -> str:
    """Format response text for better readability"""
    import textwrap
    
    # Split by paragraphs and wrap each one
    paragraphs = response.split('\n\n')
    formatted_paragraphs = []
    
    for paragraph in paragraphs:
        if paragraph.strip():
            wrapped = textwrap.fill(paragraph.strip(), width=max_width)
            formatted_paragraphs.append(wrapped)
    
    return '\n\n'.join(formatted_paragraphs)

def validate_api_key(api_key: str) -> bool:
    """Validate Google API key format"""
    if not api_key:
        return False
    
    # Basic validation - Google API keys typically start with 'AIza'
    if not api_key.startswith('AIza') or len(api_key) < 30:
        return False
    
    return True

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."