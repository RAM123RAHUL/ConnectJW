import json
import google.generativeai as genai
from app.config import GEMINI_API_KEY


# Configure Gemini client
genai.configure(api_key=GEMINI_API_KEY)


async def map_to_structure(raw_html: str, event_structure: dict, website_notes: str = "") -> dict:
    """
    Use Gemini AI to extract event data from HTML and map to structure

    Args:
        raw_html: Raw HTML content
        event_structure: Target structure definition
        website_notes: Optional hints about the website

    Returns:
        {
            "event_data": {...},
            "field_confidences": {"field": score, ...},
            "notes": "explanation"
        }
    """
    # Limit HTML to avoid token overflow
    html_content = raw_html[:15000]

    prompt = f"""
Extract event information from this HTML and map it to the exact structure provided.

TARGET STRUCTURE:
{json.dumps(event_structure, indent=2)}

HTML CONTENT:
{html_content}

WEBSITE NOTES:
{website_notes if website_notes else "No specific notes"}

For each field in the structure:
1. Find the value in the HTML
2. Transform it to match the type (string, datetime, number, etc.)
3. Give a confidence score (0-100):
   - 90-100: Perfect match, certain
   - 70-89: Good match, minor uncertainty
   - 40-69: Had to guess or interpret
   - 0-39: Missing or very uncertain

Return JSON in this exact format:
{{
    "event_data": {{...matches structure exactly...}},
    "field_confidences": {{"field_path": score, ...}},
    "notes": "Brief explanation of uncertainties or issues"
}}

IMPORTANT:
- Use dot notation for nested fields (e.g., "location.venue": 85)
- Ensure event_data matches the structure exactly
- All dates should be ISO 8601 format
- If a field is missing, set it to null and give low confidence
"""

    try:
        # Use Gemini 2.5 Pro model for structured reasoning
        model = genai.GenerativeModel("gemini-2.5-pro")


        response = await model.generate_content_async(
            prompt,
            generation_config={
                "temperature": 0.1,
                "response_mime_type": "application/json",
            },
        )

        # Parse JSON safely
        content = response.text.strip()
        result = json.loads(content)

        # Validate response structure
        if "event_data" not in result or "field_confidences" not in result:
            raise ValueError("Gemini response missing required fields")

        if "notes" not in result:
            result["notes"] = ""

        return result

    except Exception as e:
        raise Exception(f"AI mapping failed (Gemini): {str(e)}")
