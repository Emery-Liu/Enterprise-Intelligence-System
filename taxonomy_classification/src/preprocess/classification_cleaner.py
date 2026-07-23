"""
text cleaner

only python function, not rely on LLM/request, Remove noise such as 
HTML tags and extra whitespace commonly found in the raw text of web_data_list, yuqing_data_list, etc.
"""

import re
from bs4 import BeautifulSoup


def clean_html(text: str) -> str:
    """Remove HTML tags (including script and style content) and retain only plain text"""
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")

    for tag in soup([
    "script",
    "style",
    "nav",
    "footer",
    "header"
    ]):
        tag.decompose()
    return soup.get_text(separator=" ")


def normalize_text(text: str) -> str:
    """Merge multiple spaces, line breaks, and tabs into a single space; remove leading and trailing whitespace"""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def clean_text(text: str) -> str:
    """main entrance of this .py file """
    return normalize_text(clean_html(text))