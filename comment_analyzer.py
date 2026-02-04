#!/usr/bin/env python3
"""
Guardian Comments Analyzer
Analyzes scraped comments using Claude API to extract insights.
"""

import json
import sys
import os
import re
from datetime import datetime
from anthropic import Anthropic
from prompts import SENTIMENT, FOLLOWUP_IDEAS, DISCUSSION_QUESTIONS, COMMERCIAL_OPPORTUNITIES, THEMES, SUMMARY

# Initialize Anthropic client
def get_client():
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        print("\nTo use this analyzer, set your API key:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        print("\nGet an API key at: https://console.anthropic.com/")
        sys.exit(1)
    return Anthropic(api_key=api_key)

client = None  # Initialized lazily


def clean_html(html_text: str) -> str:
    """Strip HTML tags from comment body."""
    clean = re.sub(r'<[^>]+>', ' ', html_text)
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()


def prepare_comments_for_analysis(comments: list, max_comments: int = 200) -> str:
    """
    Prepare comments for LLM analysis.
    Prioritizes highly-recommended comments and samples from the rest.
    """
    # Sort by recommendations to prioritize popular comments
    sorted_comments = sorted(comments, key=lambda c: c.get('numRecommends', 0), reverse=True)

    # Take top recommended + sample of others
    if len(sorted_comments) > max_comments:
        top_comments = sorted_comments[:max_comments // 2]
        # Sample from remaining
        remaining = sorted_comments[max_comments // 2:]
        step = len(remaining) // (max_comments // 2) if len(remaining) > max_comments // 2 else 1
        sampled = remaining[::step][:max_comments // 2]
        selected = top_comments + sampled
    else:
        selected = sorted_comments

    # Format for analysis
    formatted = []
    for i, c in enumerate(selected, 1):
        body = clean_html(c.get('body', ''))
        recommends = c.get('numRecommends', 0)
        author = c.get('userProfile', {}).get('displayName', 'Anonymous')
        formatted.append(f"[Comment {i}] ({recommends} likes) @{author}: {body}")

    return "\n\n".join(formatted)


def ensure_client():
    """Ensure the Anthropic client is initialized."""
    global client
    if client is None:
        client = get_client()
    return client


def analyze_sentiment(comments_text: str, article_title: str) -> dict:
    """Analyze overall sentiment and sentiment by topic."""
    ensure_client()

    prompt = SENTIMENT.format(article_title=article_title, comments_text=comments_text)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        result = json.loads(response.content[0].text)
        return result
    except json.JSONDecodeError:
        # Try to extract JSON from response
        text = response.content[0].text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"error": "Failed to parse sentiment analysis", "raw": text}


def extract_themes(comments_text: str, article_title: str) -> list:
    """Extract main themes from comments."""
    ensure_client()

    prompt = THEMES.format(article_title=article_title, comments_text=comments_text)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        result = json.loads(response.content[0].text)
        return result.get("themes", [])
    except json.JSONDecodeError:
        text = response.content[0].text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group()).get("themes", [])
        return [{"error": "Failed to parse themes", "raw": text}]


def generate_summary(comments_text: str, article_title: str, comment_count: int) -> dict:
    """Generate executive summary and identify notable comments."""
    ensure_client()

    prompt = SUMMARY.format(article_title=article_title, comments_text=comments_text, comment_count=comment_count)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        result = json.loads(response.content[0].text)
        return result
    except json.JSONDecodeError:
        text = response.content[0].text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"error": "Failed to parse summary", "raw": text}


def generate_followup_ideas(comments_text: str, article_title: str) -> list:
    """Generate follow-up story ideas from comments."""
    ensure_client()

    prompt = FOLLOWUP_IDEAS.format(article_title=article_title, comments_text=comments_text)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        result = json.loads(response.content[0].text)
        return result.get("followUpIdeas", [])
    except json.JSONDecodeError:
        text = response.content[0].text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group()).get("followUpIdeas", [])
        return [{"error": "Failed to parse follow-up ideas", "raw": text}]


def generate_discussion_questions(comments_text: str, article_title: str) -> list:
    """Generate thought-provoking questions to promote constructive debate."""
    ensure_client()

    prompt = DISCUSSION_QUESTIONS.format(article_title=article_title, comments_text=comments_text)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        result = json.loads(response.content[0].text)
        return result.get("questions", [])
    except json.JSONDecodeError:
        text = response.content[0].text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group()).get("questions", [])
        return [{"error": "Failed to parse discussion questions", "raw": text}]


def extract_commercial_opportunities(comments_text: str, article_title: str) -> dict:
    """Extract brand mentions, recommendations, and commercial opportunities from comments."""
    ensure_client()

    prompt = COMMERCIAL_OPPORTUNITIES.format(article_title=article_title, comments_text=comments_text)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        result = json.loads(response.content[0].text)
        return result
    except json.JSONDecodeError:
        text = response.content[0].text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"error": "Failed to parse commercial opportunities", "raw": text}


def analyze_comments(input_file: str, output_file: str = None) -> dict:
    """
    Main function to analyze comments from a scraped JSON file.

    Args:
        input_file: Path to JSON file from guardian_scraper.py
        output_file: Optional output path (default: input_file with _analysis suffix)

    Returns:
        Analysis results dictionary
    """
    # Load scraped comments
    print(f"Loading comments from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    comments = data.get('comments', [])
    discussion = data.get('discussion', {})
    article_title = discussion.get('title', 'Unknown Article')
    article_url = data.get('sourceUrl', discussion.get('webUrl', ''))

    print(f"Article: {article_title}")
    print(f"Total comments: {len(comments)}")

    # Prepare comments for analysis
    print("\nPreparing comments for analysis...")
    comments_text = prepare_comments_for_analysis(comments)

    # Run analyses
    print("Analyzing sentiment...")
    sentiment = analyze_sentiment(comments_text, article_title)

    print("Extracting themes...")
    themes = extract_themes(comments_text, article_title)

    print("Generating summary...")
    summary = generate_summary(comments_text, article_title, len(comments))

    print("Generating follow-up ideas...")
    followup_ideas = generate_followup_ideas(comments_text, article_title)

    # Compile results
    results = {
        "meta": {
            "articleTitle": article_title,
            "articleUrl": article_url,
            "totalComments": len(comments),
            "uniqueCommenters": len(set(c.get('userProfile', {}).get('userId', '') for c in comments)),
            "analyzedAt": datetime.utcnow().isoformat() + "Z",
            "commentsAnalyzed": min(len(comments), 200)
        },
        "sentiment": sentiment,
        "themes": themes,
        "summary": summary,
        "followUpIdeas": followup_ideas
    }

    # Generate output filename
    if output_file is None:
        base = os.path.splitext(input_file)[0]
        output_file = f"{base}_analysis.json"

    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nAnalysis saved to: {output_file}")

    return results


def print_report(results: dict):
    """Print a human-readable report to console."""
    meta = results.get('meta', {})
    sentiment = results.get('sentiment', {})
    themes = results.get('themes', [])
    summary = results.get('summary', {})
    followup = results.get('followUpIdeas', [])

    print("\n" + "="*70)
    print(f"COMMENT ANALYSIS REPORT")
    print("="*70)
    print(f"\nArticle: {meta.get('articleTitle', 'Unknown')}")
    print(f"Comments analyzed: {meta.get('commentsAnalyzed', 0)} of {meta.get('totalComments', 0)}")
    print(f"Unique commenters: {meta.get('uniqueCommenters', 0)}")

    # Sentiment
    print("\n" + "-"*70)
    print("SENTIMENT")
    print("-"*70)
    overall = sentiment.get('overall', {})
    print(f"Positive: {overall.get('positive', 0)}% | Neutral: {overall.get('neutral', 0)}% | Negative: {overall.get('negative', 0)}%")
    print(f"Summary: {overall.get('summary', 'N/A')}")

    if sentiment.get('byTopic'):
        print("\nBy Topic:")
        for topic in sentiment.get('byTopic', [])[:5]:
            print(f"  - {topic.get('topic')}: {topic.get('sentiment')} ({topic.get('percentage', '?')}% of comments)")

    # Themes
    print("\n" + "-"*70)
    print("KEY THEMES")
    print("-"*70)
    for i, theme in enumerate(themes[:5], 1):
        print(f"\n{i}. {theme.get('name', 'Unknown')} [{theme.get('frequency', '?')} frequency, {theme.get('sentiment', '?')}]")
        print(f"   {theme.get('description', '')}")
        quotes = theme.get('representativeQuotes', [])
        if quotes:
            print(f'   Quote: "{quotes[0][:100]}..."' if len(quotes[0]) > 100 else f'   Quote: "{quotes[0]}"')

    # Summary
    print("\n" + "-"*70)
    print("EXECUTIVE SUMMARY")
    print("-"*70)
    print(summary.get('executiveSummary', 'N/A'))

    if summary.get('consensus'):
        print("\nPoints of Consensus:")
        for point in summary.get('consensus', []):
            print(f"  + {point}")

    if summary.get('contention'):
        print("\nPoints of Contention:")
        for point in summary.get('contention', []):
            print(f"  ? {point}")

    # Follow-up Ideas
    print("\n" + "-"*70)
    print("FOLLOW-UP STORY IDEAS")
    print("-"*70)
    for i, idea in enumerate(followup[:5], 1):
        print(f"\n{i}. {idea.get('headline', 'Unknown')}")
        print(f"   Interest: {idea.get('interestLevel', '?').upper()}")
        print(f"   Angle: {idea.get('angle', '')}")
        sources = idea.get('suggestedSources', [])
        if sources:
            print(f"   Sources: {', '.join(sources)}")

    print("\n" + "="*70)


def main():
    if len(sys.argv) < 2:
        print("Usage: python comment_analyzer.py <comments_json> [output_file.json]")
        print("\nExample:")
        print("  python comment_analyzer.py test_output.json")
        print("  python comment_analyzer.py test_output.json my_analysis.json")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    try:
        results = analyze_comments(input_file, output_file)
        print_report(results)
    except Exception as e:
        print(f"Error during analysis: {e}")
        raise


if __name__ == "__main__":
    main()
