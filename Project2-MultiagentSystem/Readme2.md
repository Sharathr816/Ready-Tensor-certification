# 🛠 SmartAIMaid – Your intelligent multi-agent assistant for news, PC management, and automation.

## 📊 Overview of the Project

This project is a **multi-agent system** designed to automate everyday tasks on your PC while keeping you informed with curated news updates. The system runs automatically at startup and provides a unified **web dashboard** where results and actions are displayed.

The agents collaborate to:

* Fetch and filter **tech & personal development news** from reliable sources.
* Collect tech updates from **messaging apps channels(This project uses telegram)**.
* Manage **local files and applications** for better organization and performance.
* Monitor and optimize **system processes & RAM usage**.

---

## ✨ Features

### **News Fetching**

* Automated collection of **tech + self-improvement news** from trusted sources (e.g., HackerNews, TechCrunch, Reddit).
* Delivers curated, relevant, and reliable content.

### **Telegram Integration**

* Connects to the user’s Telegram account.
* Reads only from **specific folders** chosen by the user.
* Filters messages using **keywords** (e.g., “AI”, “blockchain”, “cloud”).
* Ensures only useful updates reach the dashboard.

### **File Organization**

* Automatically sorts the **Downloads folder** into:

  * Media (images, videos, music)
  * Documents
  * Executables & Shortcuts
  * Archives (zips, dirs)
* Deletes empty folders **except system folders** (safety ensured).
* Keeps PC storage clean and structured.

### **App & Process Management** (via ProcessManagingAgent)

Works like a **smart Task Manager** with additional optimization features.

1. **App Usage Insights**

   * Tracks Most Frequently Used (MFU) apps.
   * Provides quick-open option for recommended apps.

2. **Running Processes Overview**

   * Displays running processes (excluding critical background ones).
   * Shows **RAM usage** of each process.
   * Provides an **End Task** option.

3. **One-Click RAM Booster**

   * Frees up memory by closing unnecessary processes.
   * Cleans temporary junk/cache files.
   * Helps the system run smoother without manual intervention.

### **Automation & Orchestration**

* Agents run automatically at **PC startup**.
* Routine tasks (e.g., file cleanup, news fetching, RAM monitoring) are scheduled.
* The **OrchestratorAgent** ensures smooth coordination and request routing.

### **Dashboard Control**

* A web-based dashboard provides a single view of:

  * News feed
  * Telegram updates
  * File organization status
  * App usage insights & RAM usage
* Users can also **manually trigger agents** (e.g., “clean files now”).

---

## 👥 Agents in the System 

1. 🌐 **SearchAgent** – Fetches reliable news and personal development content.
2. 💬 **TelegramAgent** – Collects and filters updates from chosen Telegram folders.
3. 📂 **FileManagerAgent** – Sorts Downloads, deletes safe empty folders.
4. 🖥 **ProcessManagingAgent** – Tracks apps, manages processes, boosts RAM.
5. 🤖 **OrchestratorAgent** – Manages all agents and schedules automation.

| 🧩 **Agent Name**           | ⚡ **Trigger Type**                                                                                     | 🧠 **Inputs**                                                                                                      | 📤 **Outputs**                                                                                                                                                                                                                     | 🧭 **Special Notes**                                                                                                  |
| --------------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| 🌐 **SearchAgent**          | **Timed Trigger** – runs at specific times (e.g., 8 AM daily) or when user commands.                   | • Default news topics (Tech, Personal Development)  <br>• Optional custom topics via user message to Orchestrator. | • News list: each with **title**, **short summary**, and **source link**.                                                                                                                                                          | • Can fetch from HackerNews, TechCrunch, Reddit, etc. <br>• Auto-refreshes on schedule but user can override anytime. |
| 💬 **TelegramAgent**        | **System State Trigger** – active while PC is on.                                                      | • Default keyword list (e.g., AI, Cloud, Startup). <br>• Telegram folders selected by user.                        | • Alerts for **incoming messages** in personal chats. <br>• **Filtered updates** from tech-related channels.                                                                                                                       | • Runs quietly in background. <br>• Can alert Orchestrator if message is suspicious/unusual.                          |
| 📂 **FileManagerAgent**     | **Event Trigger** – activated when file changes occur (e.g., new download).                            | • Folder path to monitor (Downloads, Desktop, etc.) <br>• Sorting rules.                                           | • Automatically organizes new files into folders (media, docs, zips, etc.) <br>• Displays **candidate empty folders** for deletion and **asks confirmation** via Orchestrator before deleting.                                     | • Never touches system folders. <br>• Safe auto-cleaning behaviour.                                                   |
| 🖥 **ProcessManagingAgent** | **Continuous + On-Demand Trigger** – always monitoring system; actions triggered by dashboard buttons. | • No manual input — actions triggered via UI buttons (Open app, End Task, RAM Boost).                              | • **App Usage Insights:** MFU/LRU list with launch count + active time. <br>• **Running Processes Overview:** list of non-background processes + RAM usage. <br>• **RAM Booster:** clears memory + junk files when button pressed. | • Avoids closing critical background/system processes. <br>• Acts as a sub-orchestrator for system maintenance tasks. |
| 🤖 **OrchestratorAgent**    | **Reactive Trigger** – responds to both agent alerts and user chat.                                    | • Messages from user (commands, overrides). <br>• Alerts & outputs from all agents.                                | • Routes requests to right agent. <br>• Displays consolidated info on dashboard. <br>• Sends alerts and confirmations back to user.                                                                                                | • Only agent user directly interacts with. <br>• Overrides any automation on user command.                            |


**Future Decomposition Note:**
The **ProcessManagingAgent** can be split into three specialized agents for modularity:

* **AppUsageAgent** (tracks MFU/LRU apps)
* **ProcessOverviewAgent** (running processes + RAM usage)
* **RamBoosterAgent** (system cleanup & memory boost)

Currently, these are combined for simplicity and performance. Future decomposition can improve modularity at the cost of slight overhead.

---

## 🧰 Tools in the System (Count: 5 Tools)

1. **Web Search APIs & Scraping Tools** – Fetch news & content.
2. **Telegram API (Telethon)** – Access and filter Telegram channel messages.
3. **File System Utilities (os, shutil)** – Manage files & folders safely.
4. **Process Management Tools (psutil, OS utilities)** – Track and manage system processes.
5. **RAM Monitor & Cleaner Tool** – Display memory usage and optimize RAM.

*(The web dashboard isn’t counted as a tool — it’s the user interface for results.)*

---

## 📂 Project Structure

```
multiagent-system/
│-- agents/
│   ├── search_agent.py
│   ├── telegram_agent.py
│   ├── file_manager_agent.py
│   ├── process_manager_agent.py
│   └── orchestrator_agent.py
│
│-- tools/
│   ├── web_scraper.py
│   ├── telegram_api_handler.py
│   ├── file_utils.py
│   ├── process_utils.py
│   └── ram_cleaner.py
│
│-- dashboard/
│   ├── static/
│   ├── templates/
│   └── app.py
│
│-- README.md
│-- requirements.txt
```

---

## ⚙️ Prerequisites

* Python 3.9+
* Telegram account with API credentials (for TelegramAgent)
* Basic libraries: `psutil`, `telethon`, `flask`/`fastapi`, etc.

---

## 🚀 Setup Instructions

1. Clone the repository:

   ```bash
   git clone <repo_url>
   cd multiagent-system
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables for Telegram API keys.

4. Run the orchestrator:

   ```bash
   python agents/orchestrator_agent.py
   ```

5. Access the dashboard at:

   ```
   http://localhost:5000
   ```

---

## 🖥 Tech Stack

(To be added later)
