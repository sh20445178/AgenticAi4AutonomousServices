import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the Gemini AI Agent"""
    
    def __init__(self):
        self.google_api_key: Optional[str] = os.getenv('GOOGLE_API_KEY')
        self.model_name: str = os.getenv('MODEL_NAME', 'gemini-pro')
        self.max_tokens: int = int(os.getenv('MAX_TOKENS', '1000'))
        self.temperature: float = float(os.getenv('TEMPERATURE', '0.7'))
        self.debug: bool = os.getenv('DEBUG', 'False').lower() == 'true'
        
        # Validate required settings
        if not self.google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY environment variable is required. "
                "Please set it in your .env file."
            )
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        if not self.google_api_key:
            return False
        if self.temperature < 0 or self.temperature > 1:
            return False
        if self.max_tokens <= 0:
            return False
        return True

# Global config instance
config = Config()