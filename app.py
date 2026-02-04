#!/usr/bin/env python3
"""
Guardian Comments Analyzer — Flask Web App
Provides a web interface for scraping and analyzing Guardian article comments.
"""

import json
import os

from flask import Flask, Response, render_template, request

from guardian_scraper import extract_short_url, fetch_all_comments
from comment_analyzer import (
    prepare_comments_for_analysis,
    analyze_sentiment,
    extract_themes,
    generate_summary,
    generate_followup_ideas,
)

app = Flask(__name__)


def format_sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


def generate_analysis(article_url: str):
    """Generator that yields SSE events as scraping and analysis progresses."""
    try:
        # Check API key before starting analysis
        if not os.environ.get("ANTHROPIC_API_KEY"):
            yield format_sse({
                "type": "error",
                "message": "ANTHROPIC_API_KEY environment variable not set. Set it before starting the server.",
            })
            return

        # Phase 1: Scrape comments
        yield format_sse({"type": "progress", "step": "scraping", "message": "Extracting discussion key..."})
        short_url = extract_short_url(article_url)

        yield format_sse({"type": "progress", "step": "scraping", "message": f"Found key {short_url}. Fetching comments..."})
        result = fetch_all_comments(short_url)

        comments = result["comments"]
        discussion = result.get("discussion", {})
        article_title = discussion.get("title", "Unknown Article")
        total = len(comments)

        yield format_sse({"type": "progress", "step": "scraping", "message": f"Scraped {total} comments"})

        # Send metadata immediately
        meta = {
            "articleTitle": article_title,
            "articleUrl": article_url,
            "totalComments": total,
            "uniqueCommenters": len(set(
                c.get("userProfile", {}).get("userId", "") for c in comments
            )),
            "commentsAnalyzed": min(total, 200),
        }
        yield format_sse({"type": "result", "section": "meta", "data": meta})

        if total == 0:
            yield format_sse({"type": "complete", "message": "No comments to analyze."})
            return

        # Phase 2: Prepare comments
        yield format_sse({"type": "progress", "step": "preparing", "message": "Preparing comments for analysis..."})
        comments_text = prepare_comments_for_analysis(comments)

        # Phase 3: Run four analyses sequentially
        yield format_sse({"type": "progress", "step": "analyzing", "message": "Analyzing sentiment..."})
        sentiment = analyze_sentiment(comments_text, article_title)
        yield format_sse({"type": "result", "section": "sentiment", "data": sentiment})

        yield format_sse({"type": "progress", "step": "analyzing", "message": "Extracting themes..."})
        themes = extract_themes(comments_text, article_title)
        yield format_sse({"type": "result", "section": "themes", "data": themes})

        yield format_sse({"type": "progress", "step": "analyzing", "message": "Generating summary..."})
        summary = generate_summary(comments_text, article_title, total)
        yield format_sse({"type": "result", "section": "summary", "data": summary})

        yield format_sse({"type": "progress", "step": "analyzing", "message": "Generating follow-up ideas..."})
        followup = generate_followup_ideas(comments_text, article_title)
        yield format_sse({"type": "result", "section": "followUpIdeas", "data": followup})

        yield format_sse({"type": "complete", "message": "Analysis complete"})

    except ValueError as e:
        yield format_sse({"type": "error", "message": str(e)})
    except Exception as e:
        yield format_sse({"type": "error", "message": f"Error: {e}"})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze")
def analyze():
    url = request.args.get("url", "").strip()
    if not url:
        return Response(
            format_sse({"type": "error", "message": "No URL provided"}),
            content_type="text/event-stream",
        )
    if "theguardian.com" not in url:
        return Response(
            format_sse({"type": "error", "message": "Please provide a Guardian article URL"}),
            content_type="text/event-stream",
        )

    return Response(
        generate_analysis(url),
        content_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
