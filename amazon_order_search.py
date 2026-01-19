#!/usr/bin/env python3
"""
Amazon Order Search Tool
Crafts HTTP requests to search Amazon account for order details.

Usage:
    python amazon_order_search.py --order-number 114-3615627-2951422
    python amazon_order_search.py --show-raw-request
"""

import argparse
import json
import requests
from typing import Dict, Optional
from http.cookiejar import MozillaCookieJar
import sys


class AmazonOrderSearcher:
    """
    Handles HTTP requests to Amazon for order lookups.

    Amazon doesn't provide a public API for personal orders, so this uses
    the web interface endpoints that the browser uses.
    """

    BASE_URL = "https://www.amazon.com"
    ORDER_HISTORY_URL = f"{BASE_URL}/gp/your-account/order-history"
    ORDER_DETAILS_URL = f"{BASE_URL}/gp/your-account/order-details"

    # Common headers that mimic a browser request
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
    }

    def __init__(self, session_cookies: Optional[Dict[str, str]] = None):
        """
        Initialize the Amazon order searcher.

        Args:
            session_cookies: Dictionary of cookie name/value pairs from an authenticated session
        """
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

        if session_cookies:
            for name, value in session_cookies.items():
                self.session.cookies.set(name, value, domain=".amazon.com")

    def get_raw_request_example(self, order_number: str) -> str:
        """
        Generate a raw HTTP request string for documentation/debugging.

        Args:
            order_number: The Amazon order number to search for

        Returns:
            A formatted raw HTTP request string
        """
        request = f"""GET /gp/your-account/order-details?orderID={order_number} HTTP/1.1
Host: www.amazon.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Cookie: session-id=YOUR_SESSION_ID; ubid-main=YOUR_UBID; at-main=YOUR_AT_TOKEN; sess-at-main=YOUR_SESSION_AT
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none

"""
        return request

    def get_curl_command(self, order_number: str, cookies: Optional[Dict[str, str]] = None) -> str:
        """
        Generate a curl command for the order search request.

        Args:
            order_number: The Amazon order number to search for
            cookies: Optional dictionary of cookies

        Returns:
            A curl command string
        """
        cookie_str = ""
        if cookies:
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
        else:
            cookie_str = "session-id=YOUR_SESSION_ID; ubid-main=YOUR_UBID"

        curl_cmd = f'''curl '{self.ORDER_DETAILS_URL}?orderID={order_number}' \\
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' \\
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \\
  -H 'Accept-Language: en-US,en;q=0.5' \\
  -H 'Cookie: {cookie_str}' \\
  -H 'Connection: keep-alive' \\
  --compressed
'''
        return curl_cmd

    def search_order(self, order_number: str) -> Dict:
        """
        Search for an order by order number.

        Args:
            order_number: The Amazon order number (e.g., "114-3615627-2951422")

        Returns:
            Dictionary containing the response data
        """
        params = {
            "orderID": order_number
        }

        try:
            response = self.session.get(
                self.ORDER_DETAILS_URL,
                params=params,
                timeout=30
            )

            result = {
                "status_code": response.status_code,
                "url": response.url,
                "headers": dict(response.headers),
                "cookies": dict(response.cookies),
                "content_length": len(response.content),
                "success": response.status_code == 200
            }

            # Check if we need to authenticate
            if "ap/signin" in response.url or response.status_code == 401:
                result["error"] = "Authentication required. Please provide valid session cookies."
                result["success"] = False

            # If successful, save the HTML for parsing
            if result["success"]:
                result["html_content"] = response.text
                # Could add HTML parsing here to extract order details

            return result

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }

    def search_order_alternate_endpoint(self, order_number: str) -> Dict:
        """
        Alternative endpoint for order search (order history search).

        Args:
            order_number: The Amazon order number

        Returns:
            Dictionary containing the response data
        """
        params = {
            "search": order_number
        }

        try:
            response = self.session.get(
                self.ORDER_HISTORY_URL,
                params=params,
                timeout=30
            )

            result = {
                "status_code": response.status_code,
                "url": response.url,
                "success": response.status_code == 200
            }

            if response.status_code == 200:
                result["html_content"] = response.text

            return result

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }


def print_request_info():
    """Print detailed information about crafting Amazon order search requests."""

    print("=" * 80)
    print("AMAZON ORDER SEARCH - HTTP REQUEST DETAILS")
    print("=" * 80)
    print()

    print("ENDPOINT 1: Order Details (Direct)")
    print("-" * 80)
    print("URL: https://www.amazon.com/gp/your-account/order-details")
    print("Method: GET")
    print("Parameters:")
    print("  - orderID: <order-number> (e.g., 114-3615627-2951422)")
    print()

    print("ENDPOINT 2: Order History Search")
    print("-" * 80)
    print("URL: https://www.amazon.com/gp/your-account/order-history")
    print("Method: GET")
    print("Parameters:")
    print("  - search: <order-number>")
    print()

    print("REQUIRED HEADERS:")
    print("-" * 80)
    for key, value in AmazonOrderSearcher.HEADERS.items():
        print(f"  {key}: {value}")
    print()

    print("REQUIRED COOKIES (Authentication):")
    print("-" * 80)
    print("  session-id: Your Amazon session ID")
    print("  ubid-main: Your unique browser ID")
    print("  at-main: Your authentication token")
    print("  sess-at-main: Your session authentication token")
    print()
    print("NOTE: These cookies are obtained by logging into Amazon via a browser.")
    print("You can export them using browser dev tools or extensions.")
    print()

    searcher = AmazonOrderSearcher()
    example_order = "114-3615627-2951422"

    print("RAW HTTP REQUEST EXAMPLE:")
    print("-" * 80)
    print(searcher.get_raw_request_example(example_order))
    print()

    print("CURL COMMAND EXAMPLE:")
    print("-" * 80)
    print(searcher.get_curl_command(example_order))
    print()

    print("OBTAINING COOKIES:")
    print("-" * 80)
    print("1. Open Amazon in your browser and log in")
    print("2. Open Developer Tools (F12)")
    print("3. Go to Application/Storage tab")
    print("4. Click on Cookies > https://www.amazon.com")
    print("5. Copy the values for: session-id, ubid-main, at-main, sess-at-main")
    print()
    print("OR use a browser extension like 'Cookie Editor' or 'EditThisCookie'")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Search Amazon account for order details"
    )
    parser.add_argument(
        "--order-number",
        help="Amazon order number to search for (e.g., 114-3615627-2951422)"
    )
    parser.add_argument(
        "--show-raw-request",
        action="store_true",
        help="Display raw HTTP request details and examples"
    )
    parser.add_argument(
        "--cookies-file",
        help="Path to JSON file containing cookies (format: {\"cookie-name\": \"value\"})"
    )
    parser.add_argument(
        "--curl-only",
        action="store_true",
        help="Only output the curl command"
    )

    args = parser.parse_args()

    if args.show_raw_request:
        print_request_info()
        return

    if not args.order_number:
        print("ERROR: --order-number is required (or use --show-raw-request for examples)")
        parser.print_help()
        sys.exit(1)

    # Load cookies if provided
    cookies = None
    if args.cookies_file:
        try:
            with open(args.cookies_file, 'r') as f:
                cookies = json.load(f)
        except Exception as e:
            print(f"ERROR: Could not load cookies file: {e}")
            sys.exit(1)

    searcher = AmazonOrderSearcher(session_cookies=cookies)

    if args.curl_only:
        print(searcher.get_curl_command(args.order_number, cookies))
        return

    print(f"Searching for order: {args.order_number}")
    print("-" * 80)

    # Try primary endpoint
    print("\nAttempting primary endpoint (order-details)...")
    result = searcher.search_order(args.order_number)

    if 'status_code' in result:
        print(f"Status: {result['status_code']}")
    if 'url' in result:
        print(f"URL: {result['url']}")
    print(f"Success: {result.get('success', False)}")

    if not result.get('success'):
        if 'error' in result:
            print(f"Error: {result['error']}")

        # Try alternate endpoint
        print("\nAttempting alternate endpoint (order-history search)...")
        result2 = searcher.search_order_alternate_endpoint(args.order_number)
        if 'status_code' in result2:
            print(f"Status: {result2['status_code']}")
        print(f"Success: {result2.get('success', False)}")

    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    if not cookies:
        print("1. You need to provide authentication cookies to make this work")
        print("2. Run with --show-raw-request to see how to obtain cookies")
        print("3. Save cookies to a JSON file and use --cookies-file option")
        print("\nExample:")
        print('  python amazon_order_search.py --order-number 114-3615627-2951422 --cookies-file cookies.json')
    else:
        print("Request completed. Check the response above.")
        if result.get('success'):
            print("\nTo parse order details from HTML, you can:")
            print("1. Use BeautifulSoup to parse the HTML content")
            print("2. Extract order items, shipping info, payment details, etc.")


if __name__ == "__main__":
    main()
