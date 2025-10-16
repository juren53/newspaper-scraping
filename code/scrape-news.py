from newspaper import Article, Config
import sys
import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
try:
    import dateutil.parser
except ImportError:
    print("Warning: dateutil not installed. Date parsing may be limited.")
    print("Install with: pip install python-dateutil")
    dateutil = None

if len(sys.argv) < 2:
    print("Usage: python3 scrape-news.py <URL> [--debug]")
    sys.exit(1)

url = str(sys.argv[1])
debug_mode = '--debug' in sys.argv

# Configure headers to mimic a real browser and bypass bot detection
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Sec-CH-UA': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'Sec-CH-UA-Mobile': '?0',
    'Sec-CH-UA-Platform': '"Windows"',
    'Cache-Control': 'max-age=0',
}

try:
    print(f"Attempting to scrape: {url}")
    
    # Test connection first with retry logic
    import time
    max_retries = 3
    retry_delay = 2
    
    final_response = None
    success = False
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"Retry attempt {attempt + 1}/{max_retries}...")
                time.sleep(retry_delay * attempt)  # Progressive delay
            
            response = requests.get(url, headers=headers, timeout=15)
            final_response = response  # Always keep the last response
            print(f"HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                success = True
                break
            elif response.status_code == 403:
                print(f"Bot protection detected (403). Trying enhanced headers...")
                # Add referrer and additional headers for bot protection
                enhanced_headers = headers.copy()
                enhanced_headers.update({
                    'Referer': 'https://www.google.com/',
                    'DNT': '1',
                    'Sec-GPC': '1'
                })
                enhanced_response = requests.get(url, headers=enhanced_headers, timeout=15)
                final_response = enhanced_response  # Update with enhanced response
                print(f"Enhanced request HTTP Status: {enhanced_response.status_code}")
                if enhanced_response.status_code == 200:
                    success = True
                    break
            elif response.status_code in [429, 503]:  # Rate limiting or service unavailable
                print(f"Rate limited or service unavailable. Waiting before retry...")
                continue
        except requests.exceptions.Timeout:
            print(f"Request timeout on attempt {attempt + 1}")
            continue
        except requests.exceptions.RequestException as e:
            print(f"Request failed on attempt {attempt + 1}: {e}")
            continue
    
    # Check if we got a successful response
    if not success:
        print(f"\nError: All retry attempts failed.")
        
        # Analyze the response we did get
        if final_response is not None:
            print(f"Final status code: {final_response.status_code}")
            if debug_mode:
                print(f"Response headers: {dict(final_response.headers)}")
            
            # Check for specific bot protection services
            server_header = final_response.headers.get('Server', '').lower()
            response_text = str(final_response.headers).lower()
            
            if 'datadome' in server_header or 'datadome' in response_text:
                print("\n🚫 DataDome bot protection detected!")
                print("This website uses advanced bot protection that blocks automated scraping.")
                print("\nSuggested workarounds:")
                print("1. Try accessing the article manually in a browser first")
                print("2. Use a different URL or try later")
                print("3. Consider using a proxy service or VPN")
                print("4. Some sites offer RSS feeds as an alternative")
                print("5. Try using browser automation tools like Selenium")
            elif 'cloudflare' in server_header or 'cf-ray' in response_text:
                print("\n🚫 Cloudflare protection detected!")
                print("This website uses Cloudflare bot protection.")
                print("\nSuggested workarounds:")
                print("1. Try using a different IP address or VPN")
                print("2. Wait and retry later")
                print("3. Use browser automation tools")
            else:
                print("\n🚫 Bot protection or access restriction detected!")
                print("The website is blocking automated access.")
                print("\nGeneral workarounds:")
                print("1. Try a different user agent or headers")
                print("2. Use a proxy service")
                print("3. Try browser automation tools")
        else:
            print("No response received from server.")
        
        sys.exit(1)
    
    # Use the successful response
    response = final_response
    
    # Create config with custom headers
    config = Config()
    config.browser_user_agent = headers['User-Agent']
    config.request_timeout = 10
    
    # Create article with custom config
    article = Article(url, config=config)
    article.download()
    
    # If newspaper fails, try with requests and feed HTML manually
    if not article.html:
        print("Newspaper download failed, trying with requests...")
        article.set_html(response.content)
    
    if not article.html:
        print("Error: No HTML content downloaded")
        sys.exit(1)
    
    article.parse()
    
    if debug_mode:
        print(f"Initial extraction - Title: {article.title}")
        print(f"Initial extraction - Text length: {len(article.text)}")
        print(f"Initial extraction - Authors: {article.authors}")
        with open('debug_raw.html', 'w', encoding='utf-8') as f:
            f.write(article.html)
        print("Raw HTML saved to debug_raw.html")
    
    # Check if parsing was successful and try alternative methods if needed
    if not article.title or len(article.text) < 500:
        print("Newspaper extraction seems incomplete, trying alternative methods...")
        
        # Try BeautifulSoup for better content extraction
        soup = BeautifulSoup(article.html, 'html.parser')
        
        # Try to extract title if missing
        if not article.title:
            title_selectors = ['h1', 'title', '[data-module="ArticleHeader"] h1', '.ArticleHeader_headline']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    article.title = title_elem.get_text().strip()
                    break
        
        # Try to extract full article content
        content_selectors = [
            '[data-module="ArticleBody"]',
            '.ArticleBody_container',
            '.article-body',
            '.story-body',
            '.content-body',
            'article',
            '[role="article"]'
        ]
        
        full_text = ""
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove script and style elements
                for script in content_elem(["script", "style"]):
                    script.decompose()
                
                # Extract text and clean it
                text = content_elem.get_text()
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                
                if len(text) > len(full_text):
                    full_text = text
        
        if full_text and len(full_text) > len(article.text):
            article.text = full_text
            print(f"Enhanced extraction found more content: {len(full_text)} characters")
        
        # Try to extract authors if missing
        if not article.authors:
            # Look for authors in multiple places
            author_selectors = ['.author', '.byline', '[data-module="Attribution"]', '.ArticleHeader_byline']
            for selector in author_selectors:
                author_elem = soup.select_one(selector)
                if author_elem:
                    author_text = author_elem.get_text().strip()
                    # Clean up author text
                    author_text = re.sub(r'^(By|Author:|Written by)\s*', '', author_text, flags=re.IGNORECASE)
                    if author_text:
                        article.authors = [author_text]
                        break
            
            # Try to extract from sign-off section (like "Reporting by...")
            if not article.authors:
                sign_off_pattern = r'Reporting by ([^;]+)'
                sign_off_match = re.search(sign_off_pattern, article.text)
                if sign_off_match:
                    authors = sign_off_match.group(1).strip()
                    # Clean up "and" separators and "in Location" parts
                    authors = re.sub(r'\s+in\s+[A-Z][a-zA-Z\s,]+$', '', authors)
                    article.authors = [authors]
                    print(f"Extracted authors from sign-off: {authors}")
            
            # Try to extract from meta tags
            if not article.authors:
                meta_author = soup.find('meta', {'name': 'article:author'})
                if meta_author and meta_author.get('content'):
                    article.authors = [meta_author.get('content')]
                    print(f"Extracted authors from meta tag: {meta_author.get('content')}")
        
        # Try to extract publication date if missing or enhance existing date
        if not article.publish_date:
            # Look for dates in multiple places
            date_selectors = ['.date', '.publish-date', '.publication-date', '[data-module="ArticleHeader"] time', 
                            '.ArticleHeader_date', '.timestamp', '.article-date', '.post-date']
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    # Try to get date from datetime attribute first
                    date_text = date_elem.get('datetime') or date_elem.get('content') or date_elem.get_text().strip()
                    if date_text:
                        try:
                            if dateutil:
                                # Try to parse the date
                                parsed_date = dateutil.parser.parse(date_text)
                                article.publish_date = parsed_date
                                print(f"Extracted date from selector {selector}: {parsed_date}")
                                break
                        except (ValueError, TypeError):
                            # If parsing fails, continue
                            continue
            
            # Try to extract from meta tags
            if not article.publish_date:
                meta_date_tags = [
                    {'property': 'article:published_time'},
                    {'name': 'article:published_time'},
                    {'property': 'og:published_time'},
                    {'name': 'publication_date'},
                    {'name': 'pubdate'},
                    {'name': 'date'},
                    {'itemprop': 'datePublished'}
                ]
                
                for meta_attrs in meta_date_tags:
                    meta_date = soup.find('meta', meta_attrs)
                    if meta_date and meta_date.get('content'):
                        try:
                            if dateutil:
                                parsed_date = dateutil.parser.parse(meta_date.get('content'))
                                article.publish_date = parsed_date
                                print(f"Extracted date from meta tag {meta_attrs}: {parsed_date}")
                                break
                        except (ValueError, TypeError):
                            continue
            
            # Try to extract from JSON-LD structured data
            if not article.publish_date:
                json_ld_scripts = soup.find_all('script', type='application/ld+json')
                for script in json_ld_scripts:
                    try:
                        data = json.loads(script.string)
                        # Handle both single objects and arrays
                        if isinstance(data, list):
                            data = data[0] if data else {}
                        
                        date_published = data.get('datePublished')
                        if date_published:
                            try:
                                if dateutil:
                                    parsed_date = dateutil.parser.parse(date_published)
                                    article.publish_date = parsed_date
                                    print(f"Extracted date from JSON-LD: {parsed_date}")
                                    break
                            except (ValueError, TypeError):
                                continue
                    except (json.JSONDecodeError, KeyError):
                        continue
            
            # Try to extract from article text using regex patterns
            if not article.publish_date:
                # Common date patterns in article text
                date_patterns = [
                    r'Published:?\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
                    r'([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
                    r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
                    r'(\d{4}-\d{2}-\d{2})',
                    r'(\d{2}/\d{2}/\d{4})',
                    r'(\d{1,2}/\d{1,2}/\d{4})'
                ]
                
                for pattern in date_patterns:
                    date_match = re.search(pattern, article.text[:1000])  # Search in first 1000 chars
                    if date_match:
                        try:
                            if dateutil:
                                parsed_date = dateutil.parser.parse(date_match.group(1))
                                article.publish_date = parsed_date
                                print(f"Extracted date from text pattern: {parsed_date}")
                                break
                        except (ValueError, TypeError):
                            continue
    
    # Try to extract publication/newspaper name (always run this)
    publication_name = None
    
    # Method 1: Extract from URL domain
    from urllib.parse import urlparse
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    
    # Clean up common domain patterns to get publication name
    domain_mappings = {
        'cnn.com': 'CNN',
        'bbc.com': 'BBC',
        'bbc.co.uk': 'BBC',
        'nytimes.com': 'The New York Times',
        'washingtonpost.com': 'The Washington Post',
        'theguardian.com': 'The Guardian',
        'reuters.com': 'Reuters',
        'apnews.com': 'Associated Press',
        'nbcnews.com': 'NBC News',
        'abcnews.go.com': 'ABC News',
        'cbsnews.com': 'CBS News',
        'foxnews.com': 'Fox News',
        'usatoday.com': 'USA Today',
        'wsj.com': 'The Wall Street Journal',
        'npr.org': 'NPR',
        'time.com': 'Time',
        'newsweek.com': 'Newsweek',
        'bloomberg.com': 'Bloomberg',
        'techcrunch.com': 'TechCrunch',
        'theverge.com': 'The Verge',
        'wired.com': 'Wired',
        'engadget.com': 'Engadget'
    }
    
    # Check for exact domain matches first
    if domain in domain_mappings:
        publication_name = domain_mappings[domain]
        print(f"Extracted publication from domain mapping: {publication_name}")
    else:
        # Try to extract from common domain patterns
        for known_domain, pub_name in domain_mappings.items():
            if known_domain in domain:
                publication_name = pub_name
                print(f"Extracted publication from domain pattern: {publication_name}")
                break
    
    # Method 2: Extract from meta tags if domain method didn't work
    if not publication_name:
        # We need soup, so create it if we haven't already
        if 'soup' not in locals():
            soup = BeautifulSoup(article.html, 'html.parser')
        
        meta_publication_tags = [
            {'property': 'og:site_name'},
            {'name': 'application-name'},
            {'name': 'apple-mobile-web-app-title'},
            {'property': 'article:publisher'},
            {'name': 'publisher'},
            {'name': 'source'},
            {'property': 'og:publisher'},
            {'name': 'twitter:site'},
            {'itemprop': 'publisher'}
        ]
        
        for meta_attrs in meta_publication_tags:
            meta_pub = soup.find('meta', meta_attrs)
            if meta_pub and meta_pub.get('content'):
                pub_content = meta_pub.get('content').strip()
                # Clean up Twitter handle format
                if pub_content.startswith('@'):
                    pub_content = pub_content[1:]
                if pub_content and len(pub_content) < 100:  # Reasonable length check
                    publication_name = pub_content
                    print(f"Extracted publication from meta tag {meta_attrs}: {publication_name}")
                    break
    
    # Method 3: Extract from JSON-LD structured data
    if not publication_name:
        if 'soup' not in locals():
            soup = BeautifulSoup(article.html, 'html.parser')
        
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                # Handle both single objects and arrays
                if isinstance(data, list):
                    data = data[0] if data else {}
                
                # Look for publisher information
                publisher = data.get('publisher')
                if publisher:
                    if isinstance(publisher, dict):
                        pub_name = publisher.get('name')
                        if pub_name:
                            publication_name = pub_name
                            print(f"Extracted publication from JSON-LD publisher.name: {publication_name}")
                            break
                    elif isinstance(publisher, str):
                        publication_name = publisher
                        print(f"Extracted publication from JSON-LD publisher: {publication_name}")
                        break
                
                # Alternative: look for organization info
                organization = data.get('organization')
                if organization and isinstance(organization, dict):
                    org_name = organization.get('name')
                    if org_name:
                        publication_name = org_name
                        print(f"Extracted publication from JSON-LD organization: {publication_name}")
                        break
                        
            except (json.JSONDecodeError, KeyError, TypeError):
                continue
    
    # Method 4: Extract from common CSS selectors
    if not publication_name:
        if 'soup' not in locals():
            soup = BeautifulSoup(article.html, 'html.parser')
        
        publication_selectors = [
            '.site-name', '.site-title', '.logo-text', '.brand-name',
            '.publication-name', '.masthead', '.site-branding',
            '[data-testid="SiteName"]', '.navbar-brand',
            'header .logo', 'header .brand', '.header-logo-text'
        ]
        
        for selector in publication_selectors:
            pub_elem = soup.select_one(selector)
            if pub_elem:
                pub_text = pub_elem.get_text().strip()
                # Filter out common non-publication text
                if (pub_text and len(pub_text) < 100 and 
                    not any(skip in pub_text.lower() for skip in 
                           ['menu', 'search', 'subscribe', 'login', 'sign in', 'register'])):
                    publication_name = pub_text
                    print(f"Extracted publication from selector {selector}: {publication_name}")
                    break
    
    # Method 5: Extract from page title if it contains publication info
    if not publication_name:
        if 'soup' not in locals():
            soup = BeautifulSoup(article.html, 'html.parser')
        
        page_title = soup.find('title')
        if page_title:
            title_text = page_title.get_text().strip()
            # Look for patterns like "Article Title - Publication Name" or "Article Title | Publication Name"
            separators = [' - ', ' | ', ' :: ', ' — ']
            for sep in separators:
                if sep in title_text:
                    parts = title_text.split(sep)
                    if len(parts) >= 2:
                        # Usually the publication name is the last part
                        potential_pub = parts[-1].strip()
                        if (len(potential_pub) < 50 and len(potential_pub) > 2 and 
                            not any(skip in potential_pub.lower() for skip in 
                                   ['breaking', 'news', 'latest', 'update'])):
                            publication_name = potential_pub
                            print(f"Extracted publication from page title: {publication_name}")
                            break
    
    # Method 6: Fallback - extract from domain name if nothing else worked
    if not publication_name:
        # Clean up domain to make it more readable
        clean_domain = domain.replace('www.', '')
        # Remove common TLDs and convert to title case
        for tld in ['.com', '.org', '.net', '.co.uk', '.gov']:
            if clean_domain.endswith(tld):
                clean_domain = clean_domain[:-len(tld)]
                break
        
        # Convert to readable format
        if clean_domain:
            # Handle special cases
            if '.' in clean_domain:
                clean_domain = clean_domain.split('.')[0]
            
            publication_name = clean_domain.replace('-', ' ').replace('_', ' ').title()
            print(f"Extracted publication from cleaned domain: {publication_name}")
    
    print(f"Successfully scraped article: {article.title}")
    print(f"Authors: {', '.join(article.authors) if article.authors else 'None found'}")
    print(f"Publication: {publication_name if 'publication_name' in locals() and publication_name else 'None found'}")
    print(f"Publish date: {article.publish_date}")
    print(f"Text length: {len(article.text)} characters")
    
    # Save to file
    filename = article.title.replace('/', '_').replace('\\', '_') if article.title else 'untitled_article'
    filename = filename[:100] + '.txt'  # Limit filename length
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"{article.title}\n\n")
        f.write(f"{', '.join(article.authors) if article.authors else 'Unknown'}\n\n")
        f.write(f"{publication_name if 'publication_name' in locals() and publication_name else 'Unknown'}\n\n")
        f.write(f"{article.publish_date}\n\n")
        f.write(f"{article.text}\n\n")
        f.write(f"{url}")
    
    print(f"Article saved to: {filename}")
    
except requests.exceptions.RequestException as e:
    print(f"Network error: {e}")
except Exception as e:
    print(f"Error: {e}")
    print(f"Error type: {type(e).__name__}")

