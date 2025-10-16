# Publication/Newspaper Extraction Feature for scrape-news.py

## Overview
Added a comprehensive Publication/Newspaper extraction feature to the `scrape-news.py` script, similar to the existing Title and Author extraction features. This enhancement provides robust publication name extraction capabilities to identify the news source for any scraped article.

## Publication/Newspaper Extraction Features Added:

### **6 Extraction Methods (in order of priority):**

#### **1. Domain Mapping**
- Pre-configured mapping of known news domains to their proper publication names
- Includes major outlets like CNN, BBC, The New York Times, Reuters, etc.
- Handles both exact matches and pattern matching
- Covers major news sources:
  - `cnn.com` → `CNN`
  - `bbc.com`, `bbc.co.uk` → `BBC`
  - `nytimes.com` → `The New York Times`
  - `washingtonpost.com` → `The Washington Post`
  - `theguardian.com` → `The Guardian`
  - `reuters.com` → `Reuters`
  - And many more major news outlets

#### **2. Meta Tag Extraction**
- Searches multiple meta tag formats:
  - `<meta property="og:site_name">`
  - `<meta name="application-name">`
  - `<meta name="apple-mobile-web-app-title">`
  - `<meta property="article:publisher">`
  - `<meta name="publisher">`
  - `<meta name="source">`
  - `<meta property="og:publisher">`
  - `<meta name="twitter:site">`
  - `<meta itemprop="publisher">`

#### **3. JSON-LD Structured Data**
- Parses JSON-LD structured data scripts
- Looks for `publisher.name` and `organization.name` fields in schema.org format
- Handles both single objects and arrays
- Supports nested publisher objects

#### **4. CSS Selector-based Extraction**
- Searches common CSS selectors for publication names:
  - `.site-name`, `.site-title`, `.logo-text`, `.brand-name`
  - `.publication-name`, `.masthead`, `.site-branding`
  - `[data-testid="SiteName"]`, `.navbar-brand`
  - `header .logo`, `header .brand`, `.header-logo-text`

#### **5. Page Title Analysis**
- Extracts publication name from page title patterns
- Handles formats like:
  - "Article Title - Publication Name"
  - "Article Title | Publication Name"
  - "Article Title :: Publication Name"
  - "Article Title — Publication Name"
- Filters out common non-publication words like "breaking", "news", "latest", "update"

#### **6. Domain Cleanup (Fallback)**
- As a last resort, cleans up the domain name to create a readable publication name
- Converts domains like "techcrunch.com" to "Techcrunch"
- Removes common patterns like "www." and TLDs (.com, .org, .net, etc.)
- Handles subdomains and special characters

### **Key Features:**

#### **Smart Processing**
- **Always Runs**: Publication extraction runs for every article, not just when other methods fail
- **Smart Filtering**: Filters out common non-publication text like "menu", "search", "subscribe", "login", "sign in", "register"
- **Length Validation**: Ensures extracted publication names are reasonable length (< 100 characters)
- **Twitter Handle Cleanup**: Automatically removes "@" from Twitter handles
- **Multiple Fallbacks**: If one method fails, it tries the next method sequentially

#### **Error Handling**
- Gracefully handles missing HTML elements
- Catches and continues on parsing errors (JSON-LD, malformed data)
- Provides fallback options when primary methods fail
- Creates BeautifulSoup parser only when needed for efficiency

#### **Integration with Existing Code**
- Follows the same pattern as Title and Author extraction features
- Provides informative console output showing which method successfully extracted the publication
- Integrates seamlessly with existing article processing flow

## Implementation Details

### Dependencies
- `urllib.parse` (standard library) - for URL parsing
- `BeautifulSoup` (already used) - for HTML parsing
- `json` (standard library) - for JSON-LD parsing

### Code Structure
The publication extraction feature is implemented as a standalone section that always runs after article parsing:

```python
# Try to extract publication/newspaper name (always run this)
publication_name = None

# Method 1: Extract from URL domain
# Method 2: Extract from meta tags
# Method 3: Extract from JSON-LD structured data
# Method 4: Extract from common CSS selectors
# Method 5: Extract from page title
# Method 6: Fallback - extract from domain name
```

### Output Integration
The script now provides publication information in multiple places:

#### **Console Output**
- Shows extracted publication name and which method found it
- Example: `"Extracted publication from domain mapping: CNN"`
- Displays publication in the summary: `"Publication: CNN"`

#### **File Output**
Saves publication name to the text file in the enhanced format:
```
Article Title

Author Names

Publication Name

Publication Date

Article Text

URL
```

## Benefits

### **Increased Reliability**
- Multiple extraction methods ensure publication names are found even from challenging websites
- Comprehensive fallback system provides publication info even when primary methods fail
- Domain mapping covers most major news sources with proper formatting

### **Better Metadata**
- Provides complete article metadata: Title, Authors, Publication, Date, Content
- Standardizes publication names (e.g., converts "cnn.com" to "CNN")
- Handles various publication name formats and conventions

### **Enhanced User Experience**
- Clear indication of which extraction method was successful
- Consistent publication name formatting
- Complete article attribution information

### **Flexibility**
- Works with any news website, not just predefined domains
- Adapts to different HTML structures and metadata formats
- Easily extensible domain mapping for new publications

## Usage

The feature is automatically enabled and requires no changes to the command-line interface:

```bash
python3 scrape-news.py <URL> [--debug]
```

The script will now attempt publication extraction for every article, providing more complete metadata extraction and better source attribution for scraped news articles.

## Example Output

```
Extracted publication from domain mapping: CNN
Successfully scraped article: Breaking News Story
Authors: John Doe, Jane Smith
Publication: CNN
Publish date: 2024-01-15 10:30:00
Text length: 2500 characters
Article saved to: Breaking News Story.txt
```

This enhancement makes the scraper a more complete solution for news article extraction and archival.
