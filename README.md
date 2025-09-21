# Project 1 - Money Bot (A Simple RAG Chatbot)

This project is a Retrieval-Augmented Generation (RAG) chatbot built using LangChain, Groq LLMs, and ChromaDB. The chatbot has been implemented with a chain-based design, where document retrieval, context assembly, and response generation are structured into clear, sequential steps. 
It is designed to answer questions based on the books related to money and finance by retrieving relevant passages from the text, feeding them through the chain, and generating human-like, contextual answers.

The project is beginner-friendly and structured for easy setup.
(This project dosen't implement session-based memory, intermediate reasoning steps, basic logging or observability features)

---

## 🚀 Features

* **RAG pipeline**: Retrieves relevant text chunks from PDFs and feeds them into an LLM.
* **Vector database**: Uses **ChromaDB** to store and query embeddings.
* **LLM integration**: Powered by **Groq LLMs** (e.g., `llama-3.1-8b-instant`).
* **Friendly responses**: Answers styled like a casual finance mentor.
* **Simple UI**: Built with **Gradio** for easy interaction.

---

## 📂 Project Structure

```
Project1-PsycheMoneybot/
│
├── Data/                # Place your source PDFs here (e.g., The Psychology of Money)
│   └── Money/           # Folder containing the PDF(s)
│
|
│── __init__.py
│── Create_db.py     # Script to load and embed documents into ChromaDB
│── RAGbot.py        # Main chatbot app (Gradio interface)
│── config.py        # Configuration (embeddings, vector DB setup)
│── utils.py         # Helper functions (e.g., text cleaning)
│
├── requirements.txt     # List of dependencies
├── .env                 # Environment variables (API keys)
└── README.md            # Project guide (this file)
```

---

## 🔑 Prerequisites

* **Python 3.9+**
* A **Groq API key** (get it from [Groq Console](https://console.groq.com/))

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/psychemoney-bot.git
cd Project1-PsycheMoneybot
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
# Activate it
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

Create a file named `.env` in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Add Your Data

Place your PDF files (like *The Psychology of Money*) into:

```
Data/Money/
```

### 6. Build the Vector Database

Run the database creation script:

```bash
python PsychMoneybot/Create_db.py
```

If successful, it will embed the text and store it in ChromaDB.

### 7. Run the Chatbot

Start the chatbot interface:

```bash
python PsychMoneybot/RAGbot.py
```

This will launch a **local Gradio app**. Open the link in your browser and start chatting!

---

## 📖 Example Usage
### Example 1
User: *"How do I make good money + have more time to enjoy doing what i love?"*

Bot: *"Let's talk about making good money and having more time to enjoy doing what you love. I think we can all agree that's a pretty sweet combo.

First, having flexibility is key. It allows you to wait for good opportunities, learn new skills, and find your passion at your own pace. Think of it like having a buffer zone in life. When most people are stressing about meeting deadlines and chasing competitors, you can take a step back, breathe, and focus on what really matters.

Now, let's talk about using your money to buy time and options. It's not just about accumulating wealth; it's about creating a lifestyle that gives you the freedom to pursue your passions. Think about it like this: if you're making a lot of money but working long hours, are you really enjoying the fruits of your labor? Probably not.

The key is to find a balance between making good money and having time to enjoy it. And that's where passion comes in. If you're passionate about what you do, you'll be more motivated to put in the work, even when things get tough. And that's when the magic happens – you'll be able to weather the ups and downs of life and come out on top.

So, what's the takeaway? It's not just about making good money; it's about creating a lifestyle that allows you to enjoy the things that bring you joy. And that's a recipe for happiness.

**Good actions to take:**

1. **Save money** to create a buffer zone in life.
2. **Invest in yourself** by learning new skills and finding your passion.
3. **Use your money to buy time and options**, not just accumulate wealth.
4. **Find a balance between making good money and having time to enjoy it**.
5. **Pursue your passions** with purpose and motivation.*

### Example 2

User: "I want to be an expert in Agentic AI, should i take the course from ready tensor??"

Bot: "This chatbot helps explain ideas from *The Psychology of Money*. Please provide a question related to money or finance."

---

## 🛠️ Tech Stack

* **Python**
* **LangChain** (for chaining LLM + retriever)
* **Groq LLMs** (`llama-3.1-8b-instant`)
* **ChromaDB** (vector database)
* **Gradio** (UI framework)


---