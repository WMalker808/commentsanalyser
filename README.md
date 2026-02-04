# Guardian Comments Analyzer

A tool that scrapes reader comments from Guardian articles and analyzes them using Claude to extract sentiment, themes, summaries, and follow-up story ideas.

## Features

- **Scraper**: Extracts all comments from any Guardian article with comments enabled
- **Analyzer**: Uses Claude API to produce actionable insights from comment data

### Analysis Outputs

| Analysis | Description |
|----------|-------------|
| **Sentiment** | Overall positive/neutral/negative distribution + breakdown by topic |
| **Themes** | Top 5-7 recurring themes with representative quotes and keywords |
| **Summary** | Executive summary, points of consensus/contention, notable comments |
| **Follow-up Ideas** | 3-5 potential story angles with headlines and suggested sources |

## Installation

```bash
pip install -r requirements.txt
```

### Requirements

- Python 3.8+
- `requests` - HTTP client for scraping
- `anthropic` - Claude API client for analysis

## Usage

### 1. Scrape Comments

```bash
python3 guardian_scraper.py <article_url> [output_file.json]
```

**Examples:**

```bash
# Auto-generate filename from URL
python3 guardian_scraper.py "https://www.theguardian.com/commentisfree/2024/jan/15/some-article"

# Specify output file
python3 guardian_scraper.py "https://www.theguardian.com/politics/2024/jan/15/some-article" politics_comments.json
```

**Output:** JSON file containing:
- Article metadata (title, URL, comment count)
- All comments with full data (author, text, likes, replies, timestamps)

### 2. Analyze Comments

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY='your-api-key-here'

# Run analysis
python3 comment_analyzer.py <comments_json> [output_file.json]
```

**Examples:**

```bash
# Analyze with auto-generated output filename
python3 comment_analyzer.py politics_comments.json

# Specify output file
python3 comment_analyzer.py politics_comments.json my_analysis.json
```

**Output:**
- JSON file with structured analysis data
- Human-readable report printed to console

## Output Formats

### Scraped Comments JSON

```json
{
  "discussion": {
    "discussionId": "/p/abc123",
    "title": "Article Title",
    "webUrl": "https://www.theguardian.com/...",
    "commentCount": 507,
    "isClosedForComments": true
  },
  "comments": [
    {
      "id": 173597111,
      "body": "<p>Comment HTML content...</p>",
      "date": "18 January 2024 4:15pm",
      "isoDateTime": "2024-01-18T16:15:36Z",
      "numRecommends": 125,
      "numResponses": 2,
      "userProfile": {
        "userId": "113474607",
        "displayName": "Username",
        "avatar": "https://avatar.guim.co.uk/user/..."
      }
    }
  ],
  "totalFetched": 507,
  "scrapedAt": "2024-01-19T10:30:00Z",
  "sourceUrl": "https://www.theguardian.com/..."
}
```

### Analysis JSON

```json
{
  "meta": {
    "articleTitle": "Article Title",
    "articleUrl": "https://...",
    "totalComments": 507,
    "uniqueCommenters": 312,
    "analyzedAt": "2024-01-19T10:35:00Z",
    "commentsAnalyzed": 200
  },
  "sentiment": {
    "overall": {
      "positive": 10,
      "neutral": 28,
      "negative": 62,
      "summary": "Readers are largely critical of..."
    },
    "byTopic": [
      {
        "topic": "Government policy",
        "sentiment": "negative",
        "percentage": 45,
        "explanation": "..."
      }
    ]
  },
  "themes": [
    {
      "name": "Economic impact",
      "description": "...",
      "frequency": "high",
      "sentiment": "negative",
      "representativeQuotes": ["..."],
      "keywords": ["economy", "jobs", "wages"]
    }
  ],
  "summary": {
    "executiveSummary": "...",
    "consensus": ["Point readers agree on", "..."],
    "contention": ["Point readers disagree about", "..."],
    "notableComments": [
      {
        "excerpt": "...",
        "why": "Particularly insightful because..."
      }
    ]
  },
  "followUpIdeas": [
    {
      "headline": "Potential follow-up headline",
      "angle": "Description of story angle",
      "interestLevel": "high",
      "evidence": "What in comments suggests this",
      "suggestedSources": ["Expert type", "Data source"]
    }
  ]
}
```

## API Key

Get your Anthropic API key at: https://console.anthropic.com/

Set it as an environment variable:

```bash
# Linux/macOS
export ANTHROPIC_API_KEY='sk-ant-...'

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY='sk-ant-...'

# Windows (CMD)
set ANTHROPIC_API_KEY=sk-ant-...
```

## Limitations

- Only works with Guardian articles that have comments enabled
- Analyzes up to 200 comments per article (prioritizes highly-recommended comments)
- Requires Anthropic API access (usage costs apply)

## File Structure

```
comments/
├── guardian_scraper.py    # Comment scraper
├── comment_analyzer.py    # LLM-based analyzer
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── PRD.md                 # Product requirements document
```
