# AI Shop Assistant (Enterprise RAG Version)

A high-performance Telegram support bot for E-commerce, powered by **Google Gemini 2.5** and **PostgreSQL (pgvector)**.

Unlike standard chatbots that rely on keyword matching, this assistant utilizes **RAG (Retrieval-Augmented Generation)**. It understands the semantic meaning of user queries, allowing it to recommend products based on vague descriptions (e.g., *"I need a laptop for video editing"*) and perform L1 technical support.

## ⚡ Key Features

* **Hybrid AI Brain:** Uses Google Gemini for natural conversation, context retention, and automated L1 technical support (troubleshooting steps).

* **Semantic Search (pgvector):** Products are stored as 768-dimensional vectors. The bot retrieves items based on cosine similarity, ensuring highly relevant search results even without exact keyword matches.

* **Real-Time Vector Daemon:** A standalone service (`vector_manager.py`) listens to PostgreSQL database events (`LISTEN/NOTIFY`). When a product is inserted or updated, it is instantly vectorized in the background without blocking the main bot process.

* **Smart Troubleshooting:** Follows a strict protocol for diagnosing device issues (checking power, factory reset) before escalating to a human manager.

* **Conversation Analytics:** Logs user queries, AI responses, and token usage for performance monitoring.

## 🛠 Tech Stack

* **Language:** Python 3.10+
* **Framework:** Aiogram 3.x (Fully Async)
* **LLM & Embeddings:** Google GenAI SDK (Gemini Pro + `text-embedding-004`)
* **Database:** PostgreSQL 15+
* **Vector Search:** `pgvector` extension
* **ORM:** SQLAlchemy 2.0

## 📂 Project Structure

```text
├── app/
│   ├── bot/                 # Telegram handlers, keyboards, and 
│   ├── database/            # SQLAlchemy models, core connection, 
│   ├── services/
│   │   ├── ai_engine.py     # RAG logic, tool calling, session 
│   │   ├── vector_manager.py# Daemon service for real-time =
│   │   └── prompts.py       # System instructions, personas, and 
│   └── config.py            # Environment configuration
├── main.py                  # Entry point for the Telegram Bot
├── logger.py                # Conversation logging utility
└── requirements.txt         # Project dependencies
```

## 🐳 Installation & Setup (Docker)

The project is fully containerized. You don't need to install Python or PostgreSQL locally.

### 1. Prerequisites

* **Docker Desktop** (or Docker Engine + Compose) installed.

### 2. Clone the Repository

```bash
git clone https://github.com/g-osypenko/petproject.git
cd ai-shop-bot
```

### 3. Configure Environment

Create a `.env` file in the root directory.
**Note:** Inside Docker, the database host is `db`, not `localhost`.
Firstly you also need to create your api key for telegram(personally i used @BotFather) and gemini(aistudio)
```env
BOT_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_google_api_key
# Connection string for Docker containers:
DATABASE_URL=postgresql+psycopg2://user:password@db:5432/shop_db
```

### 4. Build and Run

Run this command to build images and start all services (Bot, Database, Vector Manager) in the background:

```bash
docker-compose up --build -d
```

### 5. Initialize Database (First Run Only)

Since the database is fresh, you need to create the tables and triggers. Run this command **once**:

```bash
docker-compose exec bot python -m app.database.core
```

---

## 🕹️ Management Commands

* **View Logs:**
  ```bash
  docker-compose logs -f
  ```
* **Stop Services:**
  ```bash
  docker-compose down
  ```
* **Rebuild (after changing code):**
  ```bash
  docker-compose up -d --build
  ```

## 🚀 How to Run


To run the full system, you need to execute **two separate processes** concurrently.

### Process 1: The Telegram Bot

Handles user interaction and AI response generation.

```bash
python main.py
```

### Process 2: The Vector Manager (Daemon)

Listens for database changes and generates embeddings for new products in real-time.

```bash
python -m app.services.vector_manager
```

## 🗺️ Roadmap

- [ ] **Knowledge Base Scraper:** Implement a web scraper to index external documentation (FAQ, Delivery Rules) into the vector database.
- [ ] **Admin Panel:** Web interface for managing prompts and products.
- [ ] **CRM Integration:** Sync orders directly with external CRM systems.


## 📄 License

[MIT](https://choosealicense.com/licenses/mit/)
