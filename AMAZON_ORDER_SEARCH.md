# Amazon Order Search - HTTP Request Guide

This tool crafts HTTP requests to search your Amazon account for order details using a specific order number.

## Overview

Amazon doesn't provide a public API for personal order lookups. This tool demonstrates how to:
- Craft HTTP requests to Amazon's web interface
- Handle authentication via cookies
- Search for orders by order number
- Extract order details from responses

## Quick Start

### 1. View Raw HTTP Request Details

To see examples of the HTTP requests being made:

```bash
python amazon_order_search.py --show-raw-request
```

This shows:
- Endpoint URLs
- Required headers
- Cookie requirements
- Raw HTTP request format
- cURL command examples

### 2. Generate cURL Command

```bash
python amazon_order_search.py --order-number 114-3615627-2951422 --curl-only
```

### 3. Search with Authentication

First, create a cookies file (see "Getting Cookies" below):

```bash
python amazon_order_search.py \
  --order-number 114-3615627-2951422 \
  --cookies-file cookies.json
```

## HTTP Request Details

### Primary Endpoint: Order Details

```
GET /gp/your-account/order-details?orderID=114-3615627-2951422 HTTP/1.1
Host: www.amazon.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Cookie: session-id=XXX; ubid-main=XXX; at-main=XXX
Connection: keep-alive
```

**URL**: `https://www.amazon.com/gp/your-account/order-details`

**Method**: GET

**Query Parameters**:
- `orderID`: The order number (e.g., `114-3615627-2951422`)

### Alternate Endpoint: Order History Search

```
GET /gp/your-account/order-history?search=114-3615627-2951422 HTTP/1.1
```

**URL**: `https://www.amazon.com/gp/your-account/order-history`

**Method**: GET

**Query Parameters**:
- `search`: The order number to search for

## Required Headers

```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Cookie: [Authentication cookies]
```

## Authentication (Cookies)

To make authenticated requests, you need these cookies from an active Amazon session:

1. **session-id**: Your Amazon session identifier
2. **ubid-main**: Unique browser ID
3. **at-main**: Authentication token
4. **sess-at-main**: Session authentication token (optional but recommended)

### Getting Cookies

#### Method 1: Browser Developer Tools

1. Open Amazon.com in your browser and log in
2. Press F12 to open Developer Tools
3. Go to the **Application** tab (Chrome) or **Storage** tab (Firefox)
4. Navigate to **Cookies** → `https://www.amazon.com`
5. Find and copy the values for the required cookies

#### Method 2: Browser Extension

Use a cookie export extension like:
- Cookie Editor (Chrome/Firefox)
- EditThisCookie (Chrome)
- Export Cookies (Firefox)

#### Method 3: Network Tab

1. Open Developer Tools (F12) and go to **Network** tab
2. Navigate to an order details page on Amazon
3. Click on the request in the Network tab
4. Look at the **Request Headers** section
5. Copy the entire `Cookie:` header value

### Cookie File Format

Create a JSON file (e.g., `cookies.json`):

```json
{
  "session-id": "142-1234567-8901234",
  "ubid-main": "132-1234567-8901234",
  "at-main": "Atza|IwEBIH...",
  "sess-at-main": "\"RslZV/cIl...\""
}
```

**IMPORTANT**: Never commit this file to version control. Add it to `.gitignore`.

## Usage Examples

### Example 1: Get Raw Request Template

```bash
python amazon_order_search.py --show-raw-request
```

Output includes ready-to-use HTTP request format and cURL commands.

### Example 2: Generate cURL Command

```bash
python amazon_order_search.py \
  --order-number 114-3615627-2951422 \
  --curl-only \
  --cookies-file cookies.json
```

Copy the output and run it in your terminal:

```bash
curl 'https://www.amazon.com/gp/your-account/order-details?orderID=114-3615627-2951422' \
  -H 'User-Agent: Mozilla/5.0 ...' \
  -H 'Cookie: session-id=...; ubid-main=...' \
  --compressed
```

### Example 3: Python Script Search

```bash
python amazon_order_search.py \
  --order-number 114-3615627-2951422 \
  --cookies-file cookies.json
```

### Example 4: Using with Python Requests

```python
from amazon_order_search import AmazonOrderSearcher

# Load cookies
cookies = {
    "session-id": "142-1234567-8901234",
    "ubid-main": "132-1234567-8901234",
    "at-main": "Atza|IwEBIH..."
}

# Create searcher
searcher = AmazonOrderSearcher(session_cookies=cookies)

# Search for order
result = searcher.search_order("114-3615627-2951422")

if result['success']:
    print(f"Order found!")
    print(f"HTML content length: {result['content_length']}")
    # Parse HTML to extract order details
else:
    print(f"Error: {result.get('error', 'Unknown error')}")
```

## Parsing Order Details

The response contains HTML. To extract order details, use BeautifulSoup:

```python
from bs4 import BeautifulSoup
import re

def parse_order_details(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    order_info = {}

    # Extract order date
    order_date = soup.find('span', text=re.compile('Order Placed:'))
    if order_date:
        order_info['date'] = order_date.find_next('span').text.strip()

    # Extract total
    total = soup.find('span', text=re.compile('Order Total:'))
    if total:
        order_info['total'] = total.find_next('span').text.strip()

    # Extract items
    items = []
    for item in soup.select('.a-fixed-left-grid-col'):
        item_name = item.find('a', {'class': 'a-link-normal'})
        if item_name:
            items.append(item_name.text.strip())
    order_info['items'] = items

    return order_info

# Use it
result = searcher.search_order("114-3615627-2951422")
if result['success']:
    details = parse_order_details(result['html_content'])
    print(details)
```

## Testing Without Real Orders

You can test the HTTP request structure without valid cookies:

```bash
python amazon_order_search.py --order-number 114-3615627-2951422
```

This will show you the request attempt and explain that authentication is needed.

## cURL Examples

### Basic Request

```bash
curl 'https://www.amazon.com/gp/your-account/order-details?orderID=114-3615627-2951422' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml' \
  -H 'Cookie: session-id=YOUR_SESSION; ubid-main=YOUR_UBID' \
  --compressed
```

### With All Headers

```bash
curl 'https://www.amazon.com/gp/your-account/order-details?orderID=114-3615627-2951422' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.5' \
  -H 'Accept-Encoding: gzip, deflate, br' \
  -H 'Connection: keep-alive' \
  -H 'Cookie: session-id=142-1234567-8901234; ubid-main=132-1234567-8901234; at-main=Atza|IwEBIH...; sess-at-main="RslZV/cIl..."' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'Sec-Fetch-Dest: document' \
  -H 'Sec-Fetch-Mode: navigate' \
  -H 'Sec-Fetch-Site: none' \
  --compressed \
  -o order_details.html
```

### Search via Order History

```bash
curl 'https://www.amazon.com/gp/your-account/order-history?search=114-3615627-2951422' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' \
  -H 'Cookie: session-id=YOUR_SESSION; ubid-main=YOUR_UBID' \
  --compressed
```

## Security Notes

1. **Cookie Security**: Your Amazon cookies provide full access to your account. Keep them secure:
   - Never share cookies
   - Don't commit cookies to version control
   - Use environment variables or secure storage
   - Cookies expire - you'll need to refresh them periodically

2. **Rate Limiting**: Amazon may rate-limit requests. Use reasonable delays between requests.

3. **Terms of Service**: This tool is for personal use with your own account. Scraping Amazon at scale violates their ToS.

4. **HTTPS Only**: Always use HTTPS to protect your authentication cookies in transit.

## Troubleshooting

### "Authentication required" Error

Your cookies are missing or expired. Get fresh cookies from a logged-in browser session.

### "Redirect to login page"

Session has expired. Re-authenticate in your browser and export new cookies.

### Empty Response

Check that:
- Order number is correct
- Cookies are valid
- You have permission to view this order
- Order exists in your account

### 403 Forbidden

Amazon detected automated access. Try:
- Using more realistic headers
- Adding delays between requests
- Using cookies from the same browser/IP

## Advanced Usage

### Using with Different Amazon Domains

For Amazon UK, CA, etc., modify the base URL:

```python
searcher = AmazonOrderSearcher()
searcher.BASE_URL = "https://www.amazon.co.uk"
searcher.ORDER_DETAILS_URL = f"{searcher.BASE_URL}/gp/your-account/order-details"
```

### Batch Order Lookup

```python
import time

orders = ["114-3615627-2951422", "112-1234567-8901234", "113-9876543-2109876"]

for order_num in orders:
    result = searcher.search_order(order_num)
    print(f"Order {order_num}: {'Found' if result['success'] else 'Not found'}")
    time.sleep(2)  # Rate limiting
```

## Dependencies

Install required packages:

```bash
pip install requests beautifulsoup4
```

Or use the requirements file if it exists:

```bash
pip install -r requirements.txt
```

## License

This tool is for educational purposes and personal use only.

## Disclaimer

This tool interacts with Amazon's web interface, which is not a public API. Amazon's website structure may change, breaking this tool. Use at your own risk and in compliance with Amazon's Terms of Service.
