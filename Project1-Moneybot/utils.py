import re

def clean_text(text): # to avoid error while tokenizing
    if not text or not isinstance(text, str):
        return ""

    # Remove extra whitespace and normalize spacing
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    # Remove problematic characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\'\"]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)  # Clean up any new multiple spaces

    return text.strip()