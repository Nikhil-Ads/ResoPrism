# ResoPrism

<div align="center">

![ResoPrism](https://img.shields.io/badge/ResoPrism-AI%20Research%20Assistant-00897B?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWdvbiBwb2ludHM9IjEyIDIgMiA3IDEyIDEyIDIyIDcgMTIgMiI+PC9wb2x5Z29uPjxwb2x5bGluZSBwb2ludHM9IjIgMTcgMTIgMjIgMjIgMTciPjwvcG9seWxpbmU+PHBvbHlsaW5lIHBvaW50cz0iMiAxMiAxMiAxNyAyMiAxMiI+PC9wb2x5bGluZT48L3N2Zz4=)

**Your Intelligent Research Assistant**

*Orchestrate data collection from grants, papers, and news sources with intelligent multi-agent coordination.*

[![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-4-06B6D4?logo=tailwindcss)](https://tailwindcss.com/)

</div>

---

## 🔬 About

ResoPrism is an intelligent search assistant for research labs that streamlines discovery of relevant news, funding opportunities, and scholarly articles. It automates information gathering to help researchers stay current and identify resources aligned with their research focus.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🌐 **Multi-Agent Orchestration** | Intelligent routing to specialized agents for grants, papers, and news collection with seamless coordination |
| 📊 **Deterministic Ranking** | Advanced ranking algorithm that scores results by relevance, type priority, and metadata for optimal organization |
| ⚡ **Fast API Integration** | RESTful API built with FastAPI for lightning-fast responses and easy integration with any frontend framework |
| 🛡️ **Error Resilience** | Robust error handling ensures partial results are returned even if some agents fail, maintaining system reliability |
| 🔍 **Intent-Based Routing** | Smart intent detection allows you to search for specific types (grants, papers, news) or get results from all sources |
| 📁 **Structured Data** | Clean, typed responses with comprehensive metadata including scores, dates, authors, sources, and more |
| 🤖 **LLM-Powered Extraction** | Advanced keyword extraction using OpenAI to understand research context and optimize search queries automatically |
| 💾 **MongoDB Caching** | Intelligent caching system reduces redundant API calls and speeds up responses for frequently accessed data |
| 🔗 **URL-Based Research** | Automatically scrape research lab URLs, extract keywords, and find relevant grants, papers, and news in one click |

## 🚀 How It Works

```
┌─────────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│  1. Enter Query │     │  2. AI Agents       │     │  3. Get Ranked   │
│     or Lab URL  │ ──▶ │     Search          │ ──▶ │     Results      │
└─────────────────┘     └─────────────────────┘     └──────────────────┘
        │                        │                          │
   Provide your            Multi-agent               Advanced ranking
   research query          orchestration             algorithm scores
   or paste a lab          routes to                 and organizes
   URL for keyword         specialized               results by
   extraction              agents working            relevance
                           in parallel
```

1. **Enter Query / Lab URL** – Provide your research query or paste a lab URL. The system automatically extracts keywords and understands your intent.

2. **AI Agents Search** – Multi-agent orchestration routes your query to specialized agents for grants, papers, and news. Agents work in parallel to gather comprehensive results.

3. **Get Ranked Results** – Advanced ranking algorithm scores and organizes results by relevance, type priority, and metadata. Receive a unified inbox of curated research insights.

## 🛠️ Tech Stack

### Frontend
- **Next.js 16** – React framework with App Router
- **React 19** – UI library
- **TypeScript 5** – Type-safe development
- **Tailwind CSS 4** – Utility-first styling
- **Framer Motion** – Smooth animations
- **Radix UI** – Accessible component primitives
- **Lucide React** – Beautiful icons
- **Markmap** – Interactive mind map visualization

### Backend
- **Python 3.10+** – Core backend language
- **FastAPI** – High-performance Python API
- **LangGraph** – Multi-agent orchestration and workflow management
- **OpenAI** – LLM-powered keyword extraction and intent detection
- **NewsAPI** – Real-time news aggregation
- **MongoDB** – Database for intelligent caching and data persistence

## 📦 Getting Started

### Prerequisites

- **Node.js 18+** – For the frontend application
- **Python 3.10+** – For the backend API
- **npm, yarn, pnpm, or bun** – Package manager for frontend
- **MongoDB Database** – Local instance or [MongoDB Atlas](https://www.mongodb.com/atlas) cloud cluster

### API Keys Required

You'll need to obtain the following API keys:

| Service | Purpose | Get Your Key |
|---------|---------|--------------|
| **OpenAI** | LLM-powered keyword extraction and query understanding | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| **NewsAPI** | Fetching real-time news articles | [newsapi.org/register](https://newsapi.org/register) |
| **MongoDB** | Database connection string | [MongoDB Atlas](https://www.mongodb.com/atlas) or local instance |

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ResoPrism.git
   cd ResoPrism
   ```

2. **Set up environment variables:**
   
   Create a `.env` file in the root directory (this file is not included in the repository for security):
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` with your API keys:
   ```env
   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # NewsAPI Configuration
   NEWS_API_KEY=your_newsapi_key_here
   
   # MongoDB Configuration
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/resoprism
   ```

3. **Set up the backend:**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Run the FastAPI server
   uvicorn main:app --reload
   ```

4. **Set up the frontend:**
   ```bash
   cd web
   npm install
   # or yarn install / pnpm install
   ```

5. **Run the development server:**
   ```bash
   npm run dev
   # or yarn dev / pnpm dev
   ```

6. Open [http://localhost:3000](http://localhost:3000) in your browser.

## 📁 Project Structure

```
ResoPrism/
├── agents/                    # AI agent modules
│   ├── grants_agent.py        # Grant search agent
│   ├── papers_agent.py        # Academic paper search agent
│   └── news_agent.py          # News search agent
├── web/                       # Next.js frontend application
│   ├── src/
│   │   ├── app/               # App router pages
│   │   ├── components/        # React components
│   │   │   ├── animations/    # Animation components
│   │   │   ├── backgrounds/   # Background effects
│   │   │   ├── cards/         # Card components
│   │   │   ├── hero/          # Hero section
│   │   │   └── sections/      # Page sections
│   │   └── ...
│   ├── public/                # Static assets
│   └── package.json
├── tests/                     # Test suite
├── orchestrator.py            # Multi-agent orchestration logic
├── ranking.py                 # Deterministic ranking algorithm
├── models.py                  # Data models and schemas
├── data_pipeline.py           # Data processing pipeline
├── retrieve_data.py           # Data retrieval utilities
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
└── README.md
```

## 🙏 Acknowledgements

This project was originally created as [MongoResearch](https://github.com/ManojBaasha/MongoResearch) by our team during the **[Agentic Orchestration and Collaboration Hackathon](https://cerebralvalley.ai/e/agentic-orchestration-hackathon)** hosted by MongoDB on January 10, 2026 in San Francisco.

Special thanks to:
- **MongoDB** for hosting the hackathon and providing the platform
- **Cerebral Valley** for organizing the event
- All hackathon sponsors including NVIDIA, Vercel, Fireworks AI, Voyage AI, Thesys, Augment Code, and Coinbase

### Original Contributors
- [@ManojBaasha](https://github.com/ManojBaasha) – Manoj Elango
- [@prakharsinghpersonal](https://github.com/prakharsinghpersonal) – Prakhar Kumar Singh
- [@Nikhil-Ads](https://github.com/Nikhil-Ads) - Nikhil Adlakha
- [@SinSuhas](https://github.com/SinSuhas) - SINDHU TENAGUNDLAM PRASANNA KUMAR

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

**Built with ❤️ for researchers**

*Originally created at MongoDB's Agentic Orchestration Hackathon 🏆*

</div>
