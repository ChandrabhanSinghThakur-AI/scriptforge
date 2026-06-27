#!/bin/bash
# ╔══════════════════════════════════════════════════════╗
# ║  ScriptForge — One-Click Launch                      ║
# ║  Just run: ./run.sh                                  ║
# ╚══════════════════════════════════════════════════════╝
set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

echo ""
echo -e "${GREEN}  ✦ ScriptForge — AI Writing Portal${NC}"
echo -e "  ${YELLOW}100% local. Nothing leaves your machine.${NC}"
echo ""

# ── 1. Check Python ──
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}❌ Python 3 not found.${NC}"
    echo "   Install from: https://www.python.org/downloads/"
    echo "   Or on Mac: brew install python3"
    exit 1
fi

# ── 2. Check/Install Ollama ──
if ! command -v ollama &>/dev/null; then
    echo -e "${YELLOW}📦 Installing Ollama (local AI engine)...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   Download from: https://ollama.com/download"
        echo "   Install it, then re-run this script."
        open "https://ollama.com/download"
        exit 1
    else
        curl -fsSL https://ollama.com/install.sh | sh
    fi
fi

# ── 3. Start Ollama ──
if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
    echo -e "${YELLOW}🔄 Starting Ollama...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open -a Ollama 2>/dev/null || ollama serve &>/dev/null &
    else
        ollama serve &>/dev/null &
    fi
    for i in {1..15}; do
        curl -s http://localhost:11434/api/tags &>/dev/null && break
        sleep 2
    done
fi
echo -e "  ✓ Ollama running"

# ── 4. Pull models (only on first run) ──
if ! ollama list 2>/dev/null | grep -q "qwen2.5:14b"; then
    echo ""
    echo -e "${YELLOW}📥 Downloading AI writing model (~9GB, first time only)...${NC}"
    echo -e "   This takes 5-15 minutes. Grab a coffee ☕"
    echo ""
    ollama pull qwen2.5:14b
fi
if ! ollama list 2>/dev/null | grep -q "nomic-embed-text"; then
    echo -e "${YELLOW}📥 Downloading memory model (~274MB)...${NC}"
    ollama pull nomic-embed-text
fi
echo -e "  ✓ AI models ready"

# ── 5. Setup Python environment (first run only) ──
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}📦 Setting up environment (first time only)...${NC}"
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    echo -e "  ✓ Dependencies installed"
else
    source .venv/bin/activate
fi

# ── 6. Create manuscripts folder ──
mkdir -p manuscripts/characters manuscripts/episodes manuscripts/world-building

# ── 7. Launch! ──
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✅ ScriptForge is starting...${NC}"
echo -e "  Open: ${GREEN}http://localhost:8000${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  Press Ctrl+C to stop."
echo ""

# Open browser after short delay
(sleep 2 && open "http://localhost:8000" 2>/dev/null || xdg-open "http://localhost:8000" 2>/dev/null) &

python manage.py runserver 8000 --noreload
