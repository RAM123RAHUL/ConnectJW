# Quick Start Guide

## ✅ Already Done

Your AI Event Scraper is **ready to use**! Here's what's already set up:

- ✅ MongoDB connected to your database
- ✅ OpenAI API configured
- ✅ Database schema created
- ✅ Server running on http://localhost:8000

## 🚀 Test the API

### 1. Open API Docs

Visit: **http://localhost:8000/docs**

This gives you an interactive API interface to test all endpoints.

### 2. Define Your Event Structure

```bash
curl -X POST http://localhost:8000/api/structure \
  -H "Content-Type: application/json" \
  -d '{
    "structure": {
      "title": "string",
      "description": "string",
      "start_date": "datetime",
      "end_date": "datetime",
      "location": {
        "venue": "string",
        "address": "string",
        "city": "string"
      },
      "price": "string",
      "organizer": "string",
      "image_url": "string",
      "url": "string"
    }
  }'
```

### 3. Register a Website

```bash
curl -X POST http://localhost:8000/api/websites \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Eventbrite",
    "base_url": "https://eventbrite.com",
    "notes": "Popular event platform with structured data"
  }'
```

**Save the `id` from the response - you'll need it!**

### 4. Crawl an Event

```bash
curl -X POST http://localhost:8000/api/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "website_id": "YOUR_WEBSITE_ID_HERE",
    "url": "https://www.eventbrite.com/e/some-event-url",
    "use_javascript": false
  }'
```

**Save the `job_id` from the response!**

### 5. Check Crawl Status

```bash
curl http://localhost:8000/api/crawl/YOUR_JOB_ID_HERE
```

Wait until status is `completed`.

### 6. Get Your Events

```bash
curl http://localhost:8000/api/events?min_confidence=70
```

## 📊 What You Get

The AI will return events like this:

```json
{
  "id": "abc123...",
  "eventData": {
    "title": "AI Conference 2025",
    "start_date": "2025-11-15T09:00:00Z",
    "location": {
      "venue": "Tech Center",
      "city": "San Francisco"
    },
    "price": "$99"
  },
  "overallConfidence": 89.2,
  "fieldConfidences": {
    "title": 95,
    "start_date": 90,
    "location.venue": 85,
    "price": 80
  },
  "aiNotes": "All fields found clearly"
}
```

## 🎯 Tips

1. **JavaScript Sites**: Set `use_javascript: true` for dynamic websites
2. **Confidence Filtering**: Use `min_confidence` parameter (70-80 is a good threshold)
3. **Batch Crawling**: Use `/api/crawl/batch` endpoint for multiple URLs
4. **Website Notes**: Add hints about the site structure for better extraction

## 🔧 Common Commands

**Stop server**:
```bash
# Press Ctrl+C in the terminal where server is running
```

**Start server**:
```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

**View logs**: Server logs appear in your terminal

**Database**: Your MongoDB database is automatically synced

## 📚 Full Documentation

See [README.md](README.md) for complete documentation.

## 🐛 Troubleshooting

**Server won't start?**
- Make sure port 8000 is free
- Check `.env` has correct MongoDB URL and OpenAI key

**Crawl fails?**
- Check the URL is valid
- Try setting `use_javascript: true` for dynamic sites
- Check crawl job error: `GET /api/crawl/{job_id}`

**Low confidence scores?**
- Add notes about website structure
- Try different event pages
- Check AI notes field for hints

---

**You're all set! Start crawling events! 🎉**
