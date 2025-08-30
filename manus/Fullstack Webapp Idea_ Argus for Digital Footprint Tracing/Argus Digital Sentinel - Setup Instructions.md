# Argus Digital Sentinel - Setup Instructions

## Overview
Argus Digital Sentinel is a fullstack web application that helps you monitor your digital footprint across social media platforms and prevent potential career damage through AI-powered content analysis.

**"Have you been pwnd? Preventing self-sabotage and career suicide from the get-go with MANUS AI"**

## Features
- 🔍 **Digital Footprint Scanning**: Monitor multiple social media platforms
- 🤖 **AI-Powered Analysis**: Advanced content risk assessment using OpenAI
- 📊 **Risk Visualization**: Interactive dashboards and charts
- 🚨 **Real-time Alerts**: Immediate notifications for potential risks
- 📋 **Comprehensive Reports**: Detailed analysis and recommendations
- 🛡️ **Privacy-First**: All data processed locally and securely

## Supported Platforms
- LinkedIn (Professional networking)
- Twitter (Social media posts)
- YouTube (Video content)
- TikTok (Short-form videos)
- Reddit (Community discussions)

## Prerequisites
- Python 3.11+ installed
- Node.js 20+ installed
- OpenAI API key (for AI analysis)

## Quick Start

### 1. Environment Setup
```bash
# Clone or extract the project
cd argus-digital-sentinel

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies for frontend
cd argus-frontend
npm install  # or pnpm install
cd ..
```

### 2. Configuration
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-openai-api-key-here"

# Optional: Set custom OpenAI API base URL
export OPENAI_API_BASE="https://api.openai.com/v1"
```

### 3. Build Frontend
```bash
cd argus-frontend
npm run build  # or pnpm run build
cd ..

# Copy built files to Flask static directory
cp -r argus-frontend/dist/* src/static/
```

### 4. Start the Application
```bash
# Activate virtual environment
source venv/bin/activate

# Start the Flask server
python src/main.py
```

The application will be available at: **http://localhost:5000**

## Usage Guide

### Dashboard
- View overall risk score and trends
- Monitor active platforms and recent alerts
- Visualize risk distribution across platforms

### Platforms Management
1. Click "Platforms" tab
2. Add new platforms using the form:
   - Select platform type
   - Enter your username/handle
   - Click "Add Platform"
3. Start scans by clicking "Start Scan" for each platform

### Alerts Monitoring
- View risk alerts in the "Alerts" tab
- Alerts are automatically generated based on scan results
- Risk levels: Low (green), Medium (yellow), High (red)

### Reports Generation
- Generate comprehensive reports in the "Reports" tab
- Reports include detailed analysis and recommendations
- Export reports for external review

## Technical Architecture

### Backend (Flask)
- **Framework**: Flask with SQLAlchemy ORM
- **AI Integration**: OpenAI GPT models for content analysis
- **Data Collection**: Modular platform-specific scrapers
- **API**: RESTful endpoints for frontend communication

### Frontend (React)
- **Framework**: React with Vite build system
- **UI Library**: Tailwind CSS with shadcn/ui components
- **Charts**: Recharts for data visualization
- **Icons**: Lucide React icons

### Key Components
- `src/services/ai_analyzer.py`: AI-powered content analysis
- `src/services/data_collector.py`: Platform data collection
- `src/services/report_generator.py`: Report generation
- `src/routes/scan.py`: Scanning API endpoints
- `src/routes/reports.py`: Report generation endpoints

## Security & Privacy
- All data processing happens locally
- No data is sent to external services except OpenAI for analysis
- User credentials are never stored
- Scan results are stored locally in SQLite database

## Troubleshooting

### Common Issues
1. **Port already in use**: Change the port in `src/main.py`
2. **OpenAI API errors**: Verify your API key is set correctly
3. **Frontend build errors**: Ensure Node.js dependencies are installed
4. **Database errors**: Delete `instance/app.db` to reset database

### Development Mode
For development with hot reload:
```bash
# Terminal 1: Start Flask backend
source venv/bin/activate
python src/main.py

# Terminal 2: Start React frontend
cd argus-frontend
npm run dev  # or pnpm run dev
```

Frontend will be available at: http://localhost:5173
Backend API at: http://localhost:5000

## API Documentation

### Health Check
```
GET /api/health
Response: {"status": "healthy", "service": "Argus Digital Sentinel"}
```

### Demo Scan
```
POST /api/scan/demo
Body: {"platform": "twitter", "username": "testuser"}
Response: {"success": true, "scan": {...}}
```

### Supported Platforms
```
GET /api/platforms/supported
Response: {"success": true, "platforms": [...]}
```

## Contributing
This application was built with MANUS AI assistance and follows modern web development best practices. Feel free to extend and customize based on your needs.

## License
This project is provided as-is for educational and personal use.

