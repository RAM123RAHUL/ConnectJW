# AI Event Scraper - Project Summary

## 🎯 What This Does

A **dead-simple** event scraper that uses AI to extract event information from any website. No manual field mapping - just tell it what structure you want, and GPT-4o figures out the rest.

## 🏗️ Architecture

### Tech Stack
- **Backend**: FastAPI (Python 3.11+)
- **Database**: MongoDB with Prisma ORM
- **AI**: OpenAI GPT-4o for intelligent extraction
- **Crawling**: httpx (simple) + playwright (JavaScript sites)

### How It Works

```
URL → Crawler → HTML → AI Mapper → Event with Confidence Scores
```

1. **Crawler** fetches the page HTML
2. **AI Mapper** sends HTML + your structure to GPT-4o
3. **GPT-4o** extracts event data and assigns confidence scores per field
4. **Database** stores everything for retrieval

## 📁 Project Structure

```
crawler/
├── app/
│   ├── main.py              # FastAPI app with lifespan management
│   ├── config.py            # Environment configuration
│   ├── database.py          # Prisma client singleton
│   ├── api/
│   │   ├── websites.py      # Website CRUD endpoints
│   │   ├── structure.py     # Event structure management
│   │   ├── crawl.py         # Crawl job orchestration
│   │   └── events.py        # Event retrieval and filtering
│   └── services/
│       ├── crawler.py       # HTTP/Playwright crawler
│       ├── ai_mapper.py     # OpenAI GPT-4o integration
│       └── confidence.py    # Confidence score calculator
├── prisma/
│   └── schema.prisma        # MongoDB schema definition
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── setup.sh                 # Automated setup script
├── README.md                # Full documentation
├── QUICKSTART.md            # Quick start guide
└── PROJECT_SUMMARY.md       # This file
```

## 🗄️ Database Schema

### Collections

**target_websites**
- Websites to scrape
- Fields: name, baseUrl, notes, active
- Cascades to crawl_jobs and events

**event_structure**
- Your custom event format (versioned)
- Fields: version, isActive, structure (JSON)
- One active structure at a time

**crawl_jobs**
- Crawl job status tracking
- Fields: websiteId, url, status, rawHtml, error
- Status: pending → processing → completed/failed

**events**
- Extracted events with AI confidence
- Fields: eventData (JSON), overallConfidence, fieldConfidences (JSON), aiNotes
- Linked to crawlJobId and websiteId

## 🔑 Key Features

### 1. AI-Powered Extraction
- No manual mapping required
- GPT-4o analyzes HTML and extracts data
- Handles various website structures automatically

### 2. Confidence Scoring
- Per-field confidence scores (0-100)
- Overall confidence calculation
- AI explains uncertainties

Score interpretation:
- 90-100: Perfect match, certain
- 70-89: Good match, minor uncertainty
- 40-69: Had to guess/interpret
- 0-39: Missing or very uncertain

### 3. Flexible Structure
- Define YOUR event format once
- Supports nested fields (e.g., location.venue)
- Versioned structures for backward compatibility

### 4. Background Processing
- Crawl jobs run in background tasks
- Non-blocking API responses
- Status tracking per job

### 5. Batch Operations
- Crawl multiple URLs at once
- Each gets its own job for tracking

## 🚀 API Endpoints

### Websites
- `POST /api/websites` - Register website to crawl
- `GET /api/websites` - List all websites
- `GET /api/websites/{id}` - Get specific website
- `DELETE /api/websites/{id}` - Delete website

### Structure
- `POST /api/structure` - Define event structure
- `GET /api/structure` - Get active structure
- `GET /api/structure/versions` - List all versions

### Crawl
- `POST /api/crawl` - Trigger single crawl
- `POST /api/crawl/batch` - Trigger batch crawl
- `GET /api/crawl/{job_id}` - Check job status

### Events
- `GET /api/events` - List events (with filters)
  - Query params: `website_id`, `min_confidence`, `limit`
- `GET /api/events/{id}` - Get event details
- `DELETE /api/events/{id}` - Delete event

## 🔧 Configuration

### Environment Variables
```bash
DATABASE_URL=mongodb+srv://...
OPENAI_API_KEY=sk-proj-...
CRAWL_TIMEOUT=30
```

### Optional Features
- `use_javascript: true` - Use Playwright for dynamic sites
- `notes` field - Hints for AI about website structure

## 📊 Example Workflow

1. **Define Structure** (once)
```json
{
  "title": "string",
  "start_date": "datetime",
  "location": {"venue": "string", "city": "string"},
  "price": "string"
}
```

2. **Register Website**
```json
{
  "name": "Eventbrite",
  "base_url": "https://eventbrite.com"
}
```

3. **Crawl Event**
```json
{
  "website_id": "abc123",
  "url": "https://eventbrite.com/e/event-123"
}
```

4. **Get Results**
```json
{
  "eventData": {...},
  "overallConfidence": 89.2,
  "fieldConfidences": {"title": 95, ...},
  "aiNotes": "..."
}
```

## 🎨 Design Decisions

### Why MongoDB + Prisma?
- MongoDB: Flexible JSON storage for dynamic event structures
- Prisma: Type-safe database access with great DX

### Why OpenAI GPT-4o?
- Best at understanding unstructured HTML
- Follows instructions precisely for data extraction
- Provides confidence scores naturally

### Why FastAPI?
- Modern async Python framework
- Auto-generated OpenAPI docs
- Background tasks support

### Why Not Scrapy/BeautifulSoup for Parsing?
- Every website is different
- Manual selectors are brittle and time-consuming
- AI handles variety automatically

## 🚦 Status

- ✅ **Complete and working**
- ✅ MongoDB connected
- ✅ Server running on http://localhost:8000
- ✅ API docs at http://localhost:8000/docs

## 📈 Future Enhancements

Possible improvements:
- [ ] Webhook notifications when crawl completes
- [ ] Scheduled recurring crawls
- [ ] Rate limiting per website
- [ ] Duplicate event detection
- [ ] Bulk export (CSV, JSON)
- [ ] Authentication/API keys
- [ ] Crawler user agent rotation
- [ ] Proxy support

## 🐛 Known Limitations

1. **Token limits**: Large HTML pages truncated to 15K chars
2. **API costs**: Each crawl uses OpenAI API (approx $0.01-0.05 per page)
3. **Rate limits**: No built-in rate limiting (add if needed)
4. **JavaScript**: Playwright is slower (30s timeout)

## 📝 License

MIT

---

**Simple. No bullshit. AI does the work.**
