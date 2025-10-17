# Newspaper Scraping

A Python-based web scraping tool for extracting news articles from various websites into plain text files. This project uses the `newspaper` library with advanced fallback mechanisms to handle bot detection and extract comprehensive article information.

## Features

- **Robust Article Extraction**: Uses multiple extraction methods to handle different website structures
- **Bot Detection Bypass**: Implements realistic browser headers and retry logic to avoid being blocked
- **Comprehensive Data Extraction**: Extracts title, authors, publication date, publication name, and full article text
- **Multiple Fallback Methods**: Uses BeautifulSoup, regex patterns, and meta tag parsing when primary extraction fails
- **Debug Mode**: Provides detailed extraction information and saves raw HTML for troubleshooting
- **Command Line Interface**: Simple bash wrapper script for easy terminal usage

## Requirements

- Python 3.x
- Required Python packages:
  - `newspaper3k`
  - `requests`
  - `beautifulsoup4`
  - `python-dateutil` (optional, for enhanced date parsing)

## Installation

1. Install required packages:
```bash
pip install newspaper3k requests beautifulsoup4 python-dateutil
```

2. Set up the bash wrapper (optional):
   - Add alias to `.bashrc`: `alias News='/path/to/newspaper-scraping/code/news'`
   - Or use the python script directly

## Usage

### Command Line
```bash
# Using the bash wrapper
./code/news "https://example.com/article-url"

# Using python directly
python3 code/scrape-news.py "https://example.com/article-url"

# With debug mode
python3 code/scrape-news.py "https://example.com/article-url" --debug
```

### Output
Articles are saved as text files with the following format:
```
Article Title

Author Name(s)

Publication Name

Publication Date

Full article text...

Source URL
```

## How It Works

1. **Initial Request**: Makes HTTP request with realistic browser headers to avoid bot detection
2. **Primary Extraction**: Uses the `newspaper` library for initial content extraction
3. **Fallback Methods**: If primary extraction is incomplete, employs:
   - BeautifulSoup with multiple CSS selectors
   - Meta tag parsing for authors, dates, and publication info
   - JSON-LD structured data extraction
   - Regex patterns for date and author extraction
4. **Publication Detection**: Identifies news source through domain mapping and meta tags
5. **File Output**: Saves extracted content to a text file named after the article title

## Bot Detection Handling

The script includes several mechanisms to handle bot protection:
- Realistic browser headers mimicking Chrome
- Retry logic with progressive delays
- Detection and specific handling for Cloudflare and DataDome protection
- Enhanced headers with referrer information for stubborn sites

## Project Structure

```
Newspaper-scraping/
├── code/
│   ├── scrape-news.py      # Main scraping script
│   ├── news               # Bash wrapper script
│   └── README.txt         # Original project notes
├── Docs/                  # Documentation files
├── sample-newspaper-code.py # Basic usage example
└── scrape-news.py         # Legacy version
```

## Debug Mode

Enable debug mode with the `--debug` flag to:
- See detailed extraction information
- Save raw HTML to `debug_raw.html` for inspection
- View HTTP status codes and retry attempts
- Monitor fallback method usage

## Supported Websites

The script works with most news websites and includes specific optimizations for:
- CNN, BBC, New York Times, Washington Post
- Reuters, Associated Press, NPR
- TechCrunch, The Verge, Wired
- And many more through generic extraction methods

## Error Handling

The script provides specific error messages for:
- Network connectivity issues
- Bot protection detection (with suggested workarounds)
- Rate limiting and service unavailability
- Parsing failures with fallback options

## Contributing

This project is designed to be robust and handle the diverse landscape of news website structures. Contributions for additional extraction methods or website-specific optimizations are welcome.