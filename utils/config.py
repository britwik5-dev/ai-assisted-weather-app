"""
Configuration file for Weather Data Parser & API Assistant.
Handles loading the system prompt from prompt.txt file.
"""

import os
import logging

logger = logging.getLogger(__name__)

def load_system_prompt() -> str:
    """Load the system prompt from prompt.txt file."""
    
    project_root = os.path.dirname(os.path.dirname(__file__))
    prompt_path  = os.path.join(project_root, "prompt.txt")
    
    logger.info(f"Looking for prompt.txt at: {prompt_path}")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read()
    
        content = content.strip()
    
        if not content:
            # The file exists but is completely empty — warn the user
            logger.warning("prompt.txt was found but is empty!")
            return ""
    
        logger.info("Successfully loaded system prompt from prompt.txt")
        return content
    
    except FileNotFoundError:
        error_msg = (
            f"prompt.txt not found at '{prompt_path}'. "
            "Please make sure prompt.txt exists in the project root folder."
        )
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    except Exception as e:
        error_msg = f"Unexpected error while reading prompt.txt: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


def get_system_prompt() -> str:
    """Get the system prompt with weather data placeholder."""
    try:
        return load_system_prompt()
    except (FileNotFoundError, Exception) as e:
        logger.warning(
            f"Could not load prompt.txt ({e}). Using built-in default prompt."
        )
        default_prompt = (
            "You are a helpful weather assistant. "
            "Given weather data, provide a short, friendly recommendation "
            "and practical insights about the current conditions. "
            "Keep your response concise and useful."
        )
        return default_prompt
    


SYSTEM_PROMPT = get_system_prompt()
# A "constant" is a variable that is set once and never changed.
# By convention in Python, constants are written in ALL_CAPS.
