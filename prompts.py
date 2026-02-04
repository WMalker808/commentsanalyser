"""
Prompt templates for Guardian Comments Analyzer.

Each prompt is a template string with {article_title} and {comments_text} placeholders.
Edit these directly to change what Claude is asked to do.
"""

DISCUSSION_QUESTIONS = """\
You are helping a journalist publish discussion questions alongside the article "{article_title}" to encourage reader comments. Use the existing comments below to understand the article's subject matter and key issues, then generate 3 questions that could be published with the article to tee up discussion.

Each question must be:
- Short (one sentence, under 20 words)
- Easy to understand, conversational, jargon-free
- Directly about the article's specific subject matter — not generic or tangential
- Designed to invite readers to share their views on the issues in the article

COMMENTS (use these to understand the article's content and key issues):
{comments_text}

JSON format (no other text):
{{
  "questions": [
    {{
      "question": "<short, specific question about the article's subject>",
      "intent": "<one line: what it aims to surface>"
    }}
  ]
}}

Exactly 3 questions. They should read as prompts published alongside the article, not as responses to comments."""

SENTIMENT = """\
Analyze the sentiment of these reader comments on the article "{article_title}".

COMMENTS:
{comments_text}

Provide your analysis in the following JSON format (no other text):
{{
  "overall": {{
    "positive": <percentage 0-100>,
    "neutral": <percentage 0-100>,
    "negative": <percentage 0-100>,
    "summary": "<one sentence describing overall mood>"
  }},
  "byTopic": [
    {{
      "topic": "<specific topic discussed>",
      "sentiment": "positive|negative|mixed|neutral",
      "percentage": <% of comments touching this topic>,
      "explanation": "<brief explanation>"
    }}
  ]
}}

Include 3-5 topics in byTopic. Percentages in "overall" must sum to 100."""

FOLLOWUP_IDEAS = """\
Based on these reader comments on "{article_title}", identify potential follow-up story ideas that a journalist could pursue.

Look for:
- Questions readers are asking that weren't answered
- Personal experiences readers mention that could be explored
- Related topics readers want covered
- Controversies or debates that deserve deeper investigation
- Expert perspectives readers are requesting

COMMENTS:
{comments_text}

Provide your analysis in the following JSON format (no other text):
{{
  "followUpIdeas": [
    {{
      "headline": "<potential headline for follow-up piece>",
      "angle": "<description of the story angle>",
      "interestLevel": "high|medium|low",
      "evidence": "<what in the comments suggests this>",
      "suggestedSources": ["<type of source to interview>", "<data to gather>"]
    }}
  ]
}}

Provide 3-5 actionable follow-up ideas, ordered by potential reader interest."""

COMMERCIAL_OPPORTUNITIES = """\
Analyze these reader comments on "{article_title}" to identify commercial and advertising opportunities.

Extract:
1. **Brands & products** mentioned by readers — any companies, products, services, destinations, hotels, airlines, restaurants, or similar that readers name or discuss.
2. **Reader recommendations** — specific things readers recommend to others (products, places, services, experiences), with direct quotes as evidence.
3. **Commercial opportunities** — actionable advertising or partnership angles that a commercial team could pursue, based on reader interest and engagement patterns.

COMMENTS:
{comments_text}

Provide your analysis in the following JSON format (no other text):
{{
  "brands": [
    {{
      "name": "<brand/product/destination name>",
      "category": "<e.g. airline, hotel, destination, restaurant, product>",
      "sentiment": "positive|negative|mixed|neutral",
      "mentions": <approximate number of mentions>
    }}
  ],
  "recommendations": [
    {{
      "item": "<what is being recommended>",
      "category": "<category>",
      "quote": "<direct quote from a reader recommending it>",
      "endorsements": <number of readers recommending this or similar>
    }}
  ],
  "opportunities": [
    {{
      "type": "<sponsored content|affiliate|display advertising|partnership|event>",
      "target": "<brand, sector, or product category to approach>",
      "rationale": "<why this is a good opportunity based on the comments>"
    }}
  ]
}}

Include all brands mentioned (even once). Include 3-8 recommendations. Include 3-5 opportunities ordered by potential value. If the article is not consumer-focused and comments contain no brand mentions or recommendations, return empty arrays."""

THEMES = """\
Identify the main themes/topics that readers are discussing in these comments on "{article_title}".

COMMENTS:
{comments_text}

Provide your analysis in the following JSON format (no other text):
{{
  "themes": [
    {{
      "name": "<theme name>",
      "description": "<brief description of this theme>",
      "frequency": "<high|medium|low>",
      "sentiment": "positive|negative|mixed|neutral",
      "representativeQuotes": ["<exact quote from comment>", "<another quote>"],
      "keywords": ["keyword1", "keyword2"]
    }}
  ]
}}

Identify 5-7 themes, ordered by prominence. Use actual quotes from the comments."""

SUMMARY = """\
Summarize the reader discussion on "{article_title}" ({comment_count} total comments).

COMMENTS (sample):
{comments_text}

Provide your analysis in the following JSON format (no other text):
{{
  "executiveSummary": "<2-3 paragraph summary of the discussion, key points of agreement/disagreement, and overall reader reception>",
  "consensus": ["<point most readers agree on>", "<another point>"],
  "contention": ["<point readers disagree about>", "<another contentious point>"],
  "notableComments": [
    {{
      "excerpt": "<shortened quote from a particularly insightful/representative comment>",
      "why": "<why this comment is notable>"
    }}
  ]
}}

Include 2-4 consensus points, 2-4 contention points, and 3-5 notable comments."""
