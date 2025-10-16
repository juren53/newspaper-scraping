Description of scrape-news.py

A walk through of Python news scraping script step by step.

## Overview
This script extracts article content from news websites using the `newspaper` library as the primary method, with fallback mechanisms using `requests` and `BeautifulSoup` for more robust extraction.

## Setup and Imports
```python
from newspaper import Article, Config
import sys
import requests
from bs4 import BeautifulSoup
import re
```
The script imports libraries for web scraping (`newspaper`), HTTP requests (`requests`), HTML parsing (`BeautifulSoup`), and pattern matching (`re`).

## Command Line Arguments
```python
if len(sys.argv) < 2:
    print("Usage: python3 scrape-news.py <URL> [--debug]")
    sys.exit(1)

url = str(sys.argv[1])
debug_mode = '--debug' in sys.argv
```
Takes a URL as a required argument and an optional `--debug` flag.

## Browser Headers
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36...',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9...',
    # ... more headers
}
```
Sets up realistic browser headers to avoid being blocked by websites that detect automated requests.

## Primary Extraction Method
The script first tries using the `newspaper` library:
1. Tests the connection with a direct HTTP request
2. Configures the newspaper library with custom headers
3. Downloads and parses the article
4. Falls back to manual HTML feeding if the initial download fails

## Debug Mode
If `--debug` is enabled, it:
- Prints initial extraction results
- Saves raw HTML to `debug_raw.html` for inspection

## Fallback Extraction
If the newspaper library doesn't extract enough content (title missing or text < 500 characters), it uses BeautifulSoup with multiple strategies:

### Title Extraction
```python
title_selectors = ['h1', 'title', '[data-module="ArticleHeader"] h1', '.ArticleHeader_headline']
```
Tries various CSS selectors to find the article title.

### Content Extraction
```python
content_selectors = [
    '[data-module="ArticleBody"]',
    '.ArticleBody_container',
    '.article-body',
    # ... more selectors
]
```
Attempts multiple common selectors for article content, cleans up the text by removing scripts/styles and normalizing whitespace.

### Author Extraction
The script has three methods to find authors:
1. **CSS selectors**: Looks for common author containers like `.author`, `.byline`
2. **Sign-off patterns**: Searches for "Reporting by [Author]" in the text using regex
3. **Meta tags**: Checks for `article:author` meta tags

## Output
Finally, it:
- Prints extraction results (title, authors, date, text length)
- Saves everything to a text file named after the article title
- Handles errors gracefully with specific error messages

## Key Features
- **Robust**: Multiple fallback methods ensure content extraction even when the primary method fails
- **Realistic**: Uses proper browser headers to avoid detection
- **Flexible**: Handles various website structures through multiple CSS selectors
- **Clean**: Removes unwanted elements and normalizes text formatting

The script is designed to handle the inconsistencies of different news websites while providing detailed feedback about what it's extracting.
