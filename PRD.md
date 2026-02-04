# Guardian Comments Analyzer - Product Requirements Document

## Overview

A tool that analyzes reader comments from Guardian articles to extract insights, sentiment, themes, and content opportunities that journalists and editors can use to understand audience engagement and identify follow-up story ideas.

## Problem Statement

News organizations publish articles but have limited visibility into:
- How readers actually feel about the content (beyond comment counts)
- What aspects of a story resonate most with the audience
- What questions remain unanswered for readers
- What related topics readers want covered
- The overall discourse quality and sentiment

Manually reading hundreds of comments is time-prohibitive. Automated analysis can surface actionable insights in seconds.

## Target Users

| User | Need |
|------|------|
| Journalists | Identify follow-up story angles, understand reader reception |
| Editors | Gauge audience sentiment, prioritize coverage areas |
| Researchers | Analyze public discourse on specific topics |
| Content strategists | Identify content gaps and opportunities |

## Core Features

### 1. Sentiment Analysis

**Purpose**: Understand the emotional tone of reader response.

**Outputs**:
- Overall sentiment score (positive/negative/neutral distribution)
- Sentiment breakdown by subtopic within comments
- Sentiment trend over time (early vs late comments)
- Most positively/negatively received aspects of the article

**Example Output**:
```
Overall Sentiment: 62% Negative, 28% Neutral, 10% Positive
- Government policy: 78% negative
- Proposed solutions: 45% positive
- Article quality: 65% positive
```

### 2. Theme Extraction

**Purpose**: Identify the main topics readers are discussing.

**Outputs**:
- Top 5-10 recurring themes/topics
- Theme frequency and prominence
- Representative quotes for each theme
- Theme sentiment correlation

**Example Output**:
```
Theme: "Housing affordability" (mentioned in 34% of comments)
  - Sentiment: Strongly negative
  - Key quote: "Until wages catch up with house prices..."

Theme: "Immigration policy" (mentioned in 28% of comments)
  - Sentiment: Mixed/Polarized
  - Key quote: "The real issue isn't..."
```

### 3. Gap Analysis (Reader Interests vs Article Coverage)

**Purpose**: Identify topics readers care about that the article didn't address.

**Outputs**:
- Topics frequently raised by readers not covered in article
- Questions readers are asking
- Requests for clarification or additional information
- Related topics readers want explored

**Example Output**:
```
Gaps Identified:
1. "Historical context" - 45 comments asked about precedents
2. "Regional differences" - Article focused on London, readers want national view
3. "Long-term projections" - Readers want 10-year outlook, article only covered 2 years
```

### 4. Follow-up Story Ideas

**Purpose**: Generate actionable story leads from reader discourse.

**Outputs**:
- Ranked list of potential follow-up angles
- Supporting evidence from comments
- Estimated reader interest level
- Suggested interview subjects or data sources mentioned by readers

**Example Output**:
```
Follow-up Opportunities:
1. "Impact on small businesses" - High interest (67 mentions), unexplored angle
2. "Comparison with EU approach" - Moderate interest, readers sharing anecdotes
3. "Interview request: Affected workers" - Multiple readers offering to share stories
```

### 5. Comment Summary

**Purpose**: Provide a digestible overview of the comment section.

**Outputs**:
- Executive summary (2-3 paragraphs)
- Key statistics (comment count, unique commenters, avg engagement)
- Notable/highly-recommended comments
- Points of consensus and contention

### 6. Discourse Quality Metrics

**Purpose**: Assess the health of the discussion.

**Outputs**:
- Civility score
- Constructiveness rating
- Echo chamber vs diverse viewpoints indicator
- Ratio of substantive vs reactive comments

## Data Model

### Input
```json
{
  "article_url": "string",
  "article_title": "string",
  "article_text": "string (optional - for gap analysis)",
  "comments": [
    {
      "id": "string",
      "body": "string (HTML)",
      "date": "ISO datetime",
      "author": "string",
      "numRecommends": "number",
      "numResponses": "number",
      "responseTo": "string (parent comment ID, if reply)"
    }
  ]
}
```

### Output
```json
{
  "meta": {
    "articleUrl": "string",
    "articleTitle": "string",
    "analyzedAt": "ISO datetime",
    "totalComments": "number",
    "uniqueCommenters": "number"
  },
  "sentiment": {
    "overall": { "positive": 0.0, "neutral": 0.0, "negative": 0.0 },
    "byTopic": [ { "topic": "string", "sentiment": {} } ],
    "overTime": [ { "period": "string", "sentiment": {} } ]
  },
  "themes": [
    {
      "name": "string",
      "frequency": "number",
      "sentiment": "string",
      "representativeQuotes": ["string"],
      "keywords": ["string"]
    }
  ],
  "gaps": [
    {
      "topic": "string",
      "evidence": ["string"],
      "commentCount": "number",
      "readerQuestions": ["string"]
    }
  ],
  "followUpIdeas": [
    {
      "angle": "string",
      "interestLevel": "high|medium|low",
      "supportingEvidence": ["string"],
      "suggestedSources": ["string"]
    }
  ],
  "summary": {
    "executive": "string",
    "consensus": ["string"],
    "contention": ["string"],
    "notableComments": [{ "id": "string", "excerpt": "string", "recommends": "number" }]
  },
  "discourseQuality": {
    "civilityScore": "number (0-100)",
    "constructivenessScore": "number (0-100)",
    "viewpointDiversity": "number (0-100)"
  }
}
```

## Technical Approach

### Option A: LLM-Based Analysis (Recommended for Prototype)

Use a large language model (Claude, GPT-4) to analyze comments in batches.

**Pros**:
- High accuracy for nuanced analysis
- Can handle sarcasm, context, British idioms
- Flexible - easy to add new analysis types
- Good at identifying themes without predefined categories

**Cons**:
- API costs scale with comment volume
- Rate limits may slow large analyses
- Requires careful prompt engineering

**Implementation**:
1. Chunk comments into batches (e.g., 50 comments per request)
2. Run parallel analysis prompts for each feature
3. Aggregate and reconcile results
4. Generate final report

### Option B: Hybrid (NLP + LLM)

Use traditional NLP for bulk processing, LLM for synthesis.

**Components**:
- spaCy/NLTK: Tokenization, entity extraction
- VADER/TextBlob: Basic sentiment scoring
- BERTopic/LDA: Topic modeling
- LLM: Summary generation, insight synthesis, gap analysis

**Pros**:
- Lower cost at scale
- Faster for large comment sets
- More deterministic results

**Cons**:
- More complex implementation
- Less accurate for nuanced content
- Requires model tuning

### Recommended Architecture (Prototype)

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Guardian        │────▶│ Comment          │────▶│ Analysis        │
│ Scraper         │     │ Preprocessor     │     │ Engine (LLM)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ JSON Report     │◀────│ Report           │◀────│ Result          │
│ Output          │     │ Generator        │     │ Aggregator      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## MVP Scope

For initial prototype, implement:

1. **Sentiment Analysis** - Overall + top 3 topics
2. **Theme Extraction** - Top 5 themes with quotes
3. **Summary** - Executive summary + notable comments
4. **Follow-up Ideas** - Top 3 story angles

Defer to v2:
- Gap analysis (requires article text parsing)
- Discourse quality metrics
- Time-series sentiment
- Full topic breakdown

## Success Metrics

| Metric | Target |
|--------|--------|
| Analysis time | < 2 minutes for 500 comments |
| Theme accuracy | 80%+ alignment with human review |
| Actionable insights | 3+ usable follow-up ideas per article |
| User satisfaction | Editors find report useful 4/5 times |

## Open Questions

1. **Article text access**: Should we scrape article text for gap analysis, or require manual input?
2. **Historical analysis**: Should we support comparing sentiment across multiple articles on same topic?
3. **Real-time monitoring**: Is there value in monitoring comments as they come in (live articles)?
4. **Export formats**: JSON only, or also PDF/HTML reports?
5. **Batch processing**: Should users be able to analyze multiple articles at once?

## Next Steps

1. Implement MVP analyzer with LLM backend
2. Test on 10 diverse articles (politics, sports, culture, etc.)
3. Gather feedback from target users
4. Iterate on output format and analysis depth
