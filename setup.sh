#!/bin/bash

echo "🚀 Setting up AI Event Scraper..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Copy .env.example to .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your MongoDB URL and OpenAI API key"
fi

# Generate Prisma client
echo "🔧 Generating Prisma client..."
prisma generate

# Install Playwright browsers (optional)
read -p "Install Playwright Chromium browser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌐 Installing Playwright browsers..."
    playwright install chromium
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your MongoDB URL and OpenAI API key"
echo "2. Push Prisma schema to MongoDB: prisma db push"
echo "3. Run the server: uvicorn app.main:app --reload"
echo ""
echo "📚 API Docs will be at http://localhost:8000/docs"
