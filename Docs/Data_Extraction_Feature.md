# Date Extraction Feature for scrape-news.py

## Overview
Added a comprehensive Date extraction feature to the `scrape-news.py` script, similar to the existing Title and Author extraction features. This enhancement provides robust date extraction capabilities when the newspaper library's built-in date extraction fails.

## Date Extraction Features Added:

### 1. **Enhanced Date Parsing Infrastructure**
- Added `dateutil.parser` import with graceful fallback
- Added `json` and `datetime` imports for date handling
- Handles cases where `dateutil` is not installed

### 2. **Multiple Date Extraction Methods**
The new date extraction feature tries to find publication dates in the following order:

#### **A. CSS Selector-based Extraction**
- Searches for dates in common CSS selectors:
  - `.date`, `.publish-date`, `.publication-date`
  - `[data-module="ArticleHeader"] time`, `.ArticleHeader_date`
  - `.timestamp`, `.article-date`, `.post-date`
- Looks for dates in `datetime`, `content`, or text content of elements

#### **B. Meta Tag Extraction**
- Searches multiple meta tag formats:
  - `<meta property="article:published_time">`
  - `<meta name="article:published_time">`
  - `<meta property="og:published_time">`
  - `<meta name="publication_date">`
  - `<meta name="pubdate">`
  - `<meta name="date">`
  - `<meta itemprop="datePublished">`

#### **C. JSON-LD Structured Data Extraction**
- Parses JSON-LD structured data scripts
- Looks for `datePublished` field in schema.org format
- Handles both single objects and arrays

#### **D. Text Pattern Matching**
- Uses regex patterns to find dates in article text:
  - "Published: Month Day, Year" format
  - "Month Day, Year" format
  - "Day Month Year" format
  - ISO date format (YYYY-MM-DD)
  - US date formats (MM/DD/YYYY, M/D/YYYY)
- Searches in the first 1000 characters of the article

### 3. **Integration with Existing Flow**
- The date extraction runs **only when** the newspaper library fails to extract a date
- Follows the same pattern as Title and Author extraction
- Provides informative console output showing which method successfully extracted the date
- Handles parsing errors gracefully and continues trying other methods

### 4. **Error Handling**
- Gracefully handles missing `dateutil` library
- Catches and continues on parsing errors
- Provides fallback options when one method fails

## Implementation Details

### Dependencies
- `python-dateutil` (optional but recommended for better date parsing)
- `json` (standard library)
- `datetime` (standard library)

### Code Structure
The date extraction feature is implemented as a new section in the alternative extraction methods, following the same pattern as the existing author extraction:

```python
# Try to extract publication date if missing or enhance existing date
if not article.publish_date:
    # Multiple extraction methods as described above
```

### Output
The script now provides more detailed feedback about date extraction:
- Shows which method successfully extracted the date
- Maintains the existing output format showing the publish date
- Saves the extracted date to the output file

## Benefits
- **Increased Reliability**: Multiple fallback methods ensure dates are extracted even from challenging websites
- **Better Coverage**: Handles various date formats and HTML structures
- **Consistent Interface**: Follows the same pattern as existing extraction features
- **Graceful Degradation**: Works even without optional dependencies

## Usage
The feature is automatically enabled and requires no changes to the command-line interface:

```bash
python3 scrape-news.py <URL> [--debug]
```

The script will now attempt enhanced date extraction when the newspaper library fails to find a publication date, providing more complete article metadata extraction.
