<p align="center">
  <h1 align="center">✦ ScriptForge</h1>
  <p align="center"><strong>AI-powered screenwriting tool that runs 100% on your computer.</strong></p>
  <p align="center">No cloud. No subscriptions. No data leaving your machine. Ever.</p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/AI-100%25_Local-7c6ff7?style=for-the-badge" alt="Local AI">
  <img src="https://img.shields.io/badge/Privacy-Offline_First-4ade80?style=for-the-badge" alt="Privacy">
  <img src="https://img.shields.io/badge/Python-3.10+-3776ab?style=for-the-badge" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-f59e0b?style=for-the-badge" alt="MIT">
</p>

---

## 🎯 What is ScriptForge?

ScriptForge is a **local AI writing assistant** built for screenwriters, novelists, and storytellers. It gives you an AI co-writer that:

- Knows your **entire project** (characters, plot, world)
- **Remembers** past conversations and evolves with your story
- Runs **completely offline** — your unpublished work never touches the internet
- Works in a **beautiful distraction-free editor** with highlighting and formatting

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ScriptForge UI                                │
│                                                                       │
│  ┌──────────┐  ┌─────────────────────────────┐  ┌────────────────┐  │
│  │  📁 Files │  │                             │  │  🤖 AI Writer  │  │
│  │           │  │      ✍️  Your Editor         │  │                │  │
│  │ episodes/ │  │                             │  │  "Write a plot │  │
│  │ characters│  │   Write your story here...  │  │   twist for    │  │
│  │ world/    │  │   Auto-saves. Highlights.   │  │   episode 3"   │  │
│  │           │  │   Format controls.          │  │                │  │
│  │           │  │                             │  │  AI: Here's a  │  │
│  │           │  │                             │  │  twist where...│  │
│  └──────────┘  └─────────────────────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 AI Co-Writer | Ask AI to write dialogue, scenes, plot twists — in Hinglish or English |
| 🧠 Memory | AI remembers past conversations and your full project context |
| 🎨 Rich Editor | Font controls, text colors, highlighter, auto-save |
| 📁 File Manager | Organize characters, episodes, world-building in folders |
| 👤 Character Panel | Auto-shows relevant character specs while you write |
| 🔒 100% Private | Everything local — no internet, no accounts, no tracking |
| ⚡ Fast | 3-second launch after first setup |

---

## 🚀 Quick Start

### For Non-Technical Users

```
1. Download & unzip this project
2. Double-click "Start ScriptForge.command"
3. Wait 15 min (first time only — downloads AI)
4. Browser opens → start writing!
```

> ☕ First run downloads ~9GB of AI models. After that, it's instant.

### For Developers

```bash
git clone https://github.com/YOUR_USERNAME/scriptforge.git
cd scriptforge
./run.sh
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        YOUR MACHINE                           │
│                                                               │
│  ┌───────────┐     ┌──────────────┐     ┌───────────────┐   │
│  │  Browser  │◄───►│   Django     │◄───►│   Ollama      │   │
│  │  (UI)     │     │   (Server)   │     │   (Local LLM) │   │
│  └───────────┘     └──────┬───────┘     └───────────────┘   │
│                           │                                   │
│                    ┌──────▼───────┐                           │
│                    │   ChromaDB   │                           │
│                    │  (Memory)    │                           │
│                    └──────────────┘                           │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  manuscripts/                                            │ │
│  │  ├── characters/  ← Your character profiles              │ │
│  │  ├── episodes/    ← Your scripts                         │ │
│  │  └── world-building/ ← Lore, settings, rules            │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│              Nothing leaves this box. Ever.                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 How the AI Memory Works

```
 You ask: "Write Chandra's confrontation scene"
         │
         ▼
 ┌─────────────────────────────┐
 │  1. Embed your question     │  (nomic-embed-text → 768-dim vector)
 │  2. Search past memories    │  (ChromaDB similarity search)
 │  3. Load ALL project files  │  (characters, episodes, world)
 │  4. Build context prompt    │  (memory + files + your question)
 │  5. Send to local LLM       │  (qwen2.5:14b via Ollama)
 │  6. Stream response back    │  (real-time tokens)
 │  7. Save to memory          │  (for future context)
 └─────────────────────────────┘
         │
         ▼
 AI responds with a scene that knows:
 • Who Chandra is (from characters/chandra.md)
 • What happened before (from memory)
 • The tone of your series (from all files)
```

**The more you write, the smarter it gets.**

---

## 📁 Project Structure

```
scriptforge/
├── Start ScriptForge.command  ← Double-click to launch (non-tech users)
├── run.sh                     ← Launch script
├── README.md                  ← You're reading this
├── LICENSE                    ← MIT
├── requirements.txt           ← Python dependencies
├── manage.py                  ← Django entry point
├── scriptforge/               ← Django config
│   ├── settings.py
│   └── urls.py
├── writer/                    ← Main app
│   ├── views.py               ← API endpoints + AI logic
│   ├── urls.py                ← URL routing
│   └── templates/writer/
│       └── index.html         ← Single-page UI (HTML/CSS/JS)
└── manuscripts/               ← Your writing (auto-created)
    ├── characters/
    ├── episodes/
    └── world-building/
```

---

## 🔧 Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | Vanilla HTML/CSS/JS | No build step, instant load, zero deps |
| **Backend** | Django 5 | Battle-tested, simple, Python ecosystem |
| **AI Model** | Qwen 2.5:14b (via Ollama) | Best creative writing quality at local scale |
| **Memory** | mem0 + ChromaDB | Persistent vector memory across sessions |
| **Embeddings** | nomic-embed-text | Fast local embeddings for semantic search |

---

## 🎮 Daily Usage

### For Writers (Non-Technical)

1. **Double-click** `Start ScriptForge.command`
2. Browser opens → write
3. Close Terminal window when done

> 💡 Drag `Start ScriptForge.command` to your Dock for one-click launch.

### Editor Controls

| Control | What it does |
|---------|-------------|
| **Size** | Change text size (12-32px) |
| **Font** | JetBrains Mono, Courier, Inter, Georgia |
| **Color** | Pick text color |
| **Line** | Adjust line spacing |
| **🖍️ Mark** | Highlight selected text |
| **✕** | Clear all highlights |

### AI Commands (type in right panel)

```
"Write a scene where Rakesh confronts Chandra"
"Suggest 3 plot twists for episode 2"
"Write this dialogue in aggressive Hinglish"
"Describe the office setting cinematically"
"What are Chandra's motivations?"
```

---

## ⚙️ Configuration

```bash
# Custom manuscripts folder
export SCRIPTFORGE_MANUSCRIPTS=/path/to/your/writing

# Then run
./run.sh
```

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| "Python not found" | Install from [python.org/downloads](https://www.python.org/downloads/) |
| "Ollama not found" | Install from [ollama.com](https://ollama.com/download), then re-run |
| App won't start | Make sure Ollama is running (check menu bar icon) |
| AI not responding | First use loads model into RAM (~30 sec). Wait and retry. |
| Browser doesn't open | Go to `http://localhost:8000` manually |
| Want to reset memory | Delete `.mem0_db/` folder and restart |
| Port 8000 in use | Kill other process: `lsof -i :8000` then `kill <PID>` |

---

## 🔒 Privacy & Security

```
┌─────────────────────────────────────────┐
│  Your Machine                            │
│                                          │
│  ✅ Scripts stored locally               │
│  ✅ AI runs locally (no API calls)       │
│  ✅ Memory stored locally (ChromaDB)     │
│  ✅ No accounts or logins                │
│  ✅ No telemetry or tracking             │
│  ✅ Works completely offline             │
│                                          │
│  ❌ Nothing sent to cloud                │
│  ❌ No third-party access                │
│  ❌ No internet required (after setup)   │
└─────────────────────────────────────────┘
```

Your unpublished scripts are **yours alone**.

---

## 💻 System Requirements

| Requirement | Minimum | Recommended |
|------------|---------|-------------|
| **OS** | macOS 12+ / Ubuntu 20+ | macOS 14+ |
| **RAM** | 8 GB | 16 GB |
| **Disk** | 10 GB free | 15 GB free |
| **CPU** | Any 64-bit | Apple Silicon (M1+) |
| **Internet** | Only for first setup | — |

---

## 🤝 Contributing

1. Fork this repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Make changes
4. Submit a Pull Request

Ideas welcome: better UI, more AI models, export to PDF/Final Draft, collaborative writing.

---

## 📜 License

MIT — use it, fork it, make it yours.

---

<p align="center">
  <em>Built by a writer who got tired of paying $20/month for AI tools that send unpublished scripts to the cloud.</em>
</p>
