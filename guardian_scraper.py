#!/usr/bin/env python3
"""
Guardian Comments Scraper
Extracts all comments from a Guardian article and saves to JSON.
"""

import requests
import json
import re
import sys
from datetime import datetime
from urllib.parse import urlparse


def extract_short_url(article_url: str) -> str:
    """Extract the discussion short URL key from a Guardian article page."""
    response = requests.get(article_url, timeout=30)
    response.raise_for_status()

    # Look for the shortUrl in the page's JSON-LD or data attributes
    # Pattern: "shortUrl":"https://www.theguardian.com/p/xxxxx"
    match = re.search(r'"shortUrl"\s*:\s*"https?://(?:www\.)?theguardian\.com(/p/[a-z0-9]+)"', response.text)
    if match:
        return match.group(1)

    # Alternative pattern: data-short-url or shortUrlId
    match = re.search(r'data-short-url="(/p/[a-z0-9]+)"', response.text)
    if match:
        return match.group(1)

    # Try finding discussion ID directly
    match = re.search(r'"discussionId"\s*:\s*"(/p/[a-z0-9]+)"', response.text)
    if match:
        return match.group(1)

    raise ValueError(f"Could not find discussion key in article: {article_url}")


def fetch_all_comments(short_url: str) -> dict:
    """Fetch all comments for a discussion, handling pagination."""
    base_url = "https://discussion.theguardian.com/discussion-api/discussion"

    all_comments = []
    page = 1
    page_size = 100  # Max allowed by API
    total_pages = 1
    discussion_info = {}

    while page <= total_pages:
        url = f"{base_url}{short_url}"
        params = {
            "page": page,
            "pageSize": page_size,
            "orderBy": "oldest",
            "displayThreaded": "false",  # Flat list, easier to process all
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if page == 1:
            # Store discussion metadata from first request
            discussion_info = {
                "discussionId": data.get("discussion", {}).get("key"),
                "title": data.get("discussion", {}).get("title"),
                "webUrl": data.get("discussion", {}).get("webUrl"),
                "commentCount": data.get("discussion", {}).get("commentCount"),
                "isClosedForComments": data.get("discussion", {}).get("isClosedForComments"),
                "isClosedForRecommendation": data.get("discussion", {}).get("isClosedForRecommendation"),
            }
            total_pages = data.get("pages", 1)
            print(f"Found {discussion_info['commentCount']} comments across {total_pages} pages")

        comments = data.get("discussion", {}).get("comments", [])
        all_comments.extend(comments)

        print(f"Fetched page {page}/{total_pages} ({len(comments)} comments)")
        page += 1

    return {
        "discussion": discussion_info,
        "comments": all_comments,
        "totalFetched": len(all_comments),
        "scrapedAt": datetime.utcnow().isoformat() + "Z",
    }


def scrape_guardian_comments(article_url: str, output_file: str = None) -> dict:
    """
    Main function to scrape comments from a Guardian article.

    Args:
        article_url: Full URL to a Guardian article
        output_file: Optional path for JSON output (default: based on article URL)

    Returns:
        Dictionary containing all comments and metadata
    """
    print(f"Scraping comments from: {article_url}")

    # Extract discussion key from article
    print("Extracting discussion key...")
    short_url = extract_short_url(article_url)
    print(f"Found discussion key: {short_url}")

    # Fetch all comments
    print("Fetching comments...")
    result = fetch_all_comments(short_url)
    result["sourceUrl"] = article_url

    # Generate output filename if not provided
    if output_file is None:
        # Create filename from article URL
        parsed = urlparse(article_url)
        path_slug = parsed.path.strip("/").replace("/", "_")[:50]
        output_file = f"comments_{path_slug}.json"

    # Save to file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {result['totalFetched']} comments to: {output_file}")

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python guardian_scraper.py <article_url> [output_file.json]")
        print("\nExample:")
        print("  python guardian_scraper.py https://www.theguardian.com/world/2024/...")
        sys.exit(1)

    article_url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        scrape_guardian_comments(article_url, output_file)
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
