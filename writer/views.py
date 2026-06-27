import os
import json
import httpx
import threading
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

MANUSCRIPTS_DIR = os.environ.get("SCRIPTFORGE_MANUSCRIPTS", os.path.join(settings.BASE_DIR, "manuscripts"))
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:14b"

# --- Persistent Memory via mem0 (lazy loaded) ---
from mem0 import Memory

_memory = None

def get_memory():
    global _memory
    if _memory is None:
        _memory = Memory.from_config({
            "llm": {
                "provider": "ollama",
                "config": {"model": OLLAMA_MODEL, "ollama_base_url": "http://localhost:11434"}
            },
            "embedder": {
                "provider": "ollama",
                "config": {"model": "nomic-embed-text", "ollama_base_url": "http://localhost:11434"}
            },
            "vector_store": {
                "provider": "chroma",
                "config": {"collection_name": "corporate_series", "path": os.path.join(settings.BASE_DIR, ".mem0_db")}
            }
        })
    return _memory

def _save_memory_bg(text, metadata=None):
    """Save to memory in background thread — doesn't block response."""
    def _save():
        try:
            get_memory().add(text, user_id="writer", metadata=metadata or {})
        except Exception:
            pass
    threading.Thread(target=_save, daemon=True).start()


# --- RAG: Load reference materials into ChromaDB ---
REFERENCES_DIR = os.path.join(settings.BASE_DIR, "references")
_references_loaded = False

def _load_references_bg():
    """Load reference files into memory (one-time, skips if already loaded)."""
    global _references_loaded
    if _references_loaded or not os.path.isdir(REFERENCES_DIR):
        return
    _references_loaded = True
    def _load():
        try:
            m = get_memory()
            existing = m.get_all(filters={"user_id": "reference"})
            if existing and len(existing.get("results", [])) > 0:
                return
            _index_references(m)
        except Exception:
            pass
    threading.Thread(target=_load, daemon=True).start()


def _index_references(m):
    """Index all reference files into ChromaDB."""
    for f in os.listdir(REFERENCES_DIR):
        if not f.endswith((".md", ".txt")):
            continue
        fpath = os.path.join(REFERENCES_DIR, f)
        text = open(fpath, "r").read()
        chunks = [text[i:i+500] for i in range(0, len(text), 450)]
        for chunk in chunks:
            if len(chunk.strip()) > 50:
                m.add(f"[Reference: {f}] {chunk.strip()}", user_id="reference", metadata={"type": "reference", "source": f})


@csrf_exempt
def reload_references(request):
    """Delete existing references and re-index from references/ folder."""
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    def _reload():
        try:
            m = get_memory()
            # Delete all existing references
            existing = m.get_all(filters={"user_id": "reference"})
            results = existing.get("results", []) if isinstance(existing, dict) else existing
            for r in results:
                try:
                    m.delete(r.get("id"), user_id="reference")
                except Exception:
                    pass
            # Re-index
            _index_references(m)
        except Exception:
            pass
    threading.Thread(target=_reload, daemon=True).start()
    return JsonResponse({"status": "reloading", "message": "References are being updated. Takes ~30 seconds."})


def list_memories(request):
    """Show all stored memories and references."""
    try:
        m = get_memory()
        writer_mems = m.get_all(filters={"user_id": "writer"})
        ref_mems = m.get_all(filters={"user_id": "reference"})
        w = writer_mems.get("results", []) if isinstance(writer_mems, dict) else writer_mems
        r = ref_mems.get("results", []) if isinstance(ref_mems, dict) else ref_mems
        return JsonResponse({
            "conversations": [{"id": x.get("id"), "memory": x.get("memory", "")[:200]} for x in (w or [])],
            "references": [{"id": x.get("id"), "memory": x.get("memory", "")[:200]} for x in (r or [])],
            "total_conversations": len(w or []),
            "total_references": len(r or []),
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def add_reference(request):
    """Add text directly as a reference to ChromaDB."""
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    data = json.loads(request.body)
    text = data.get("text", "").strip()
    if not text:
        return JsonResponse({"error": "No text provided"}, status=400)
    # Save as file
    os.makedirs(REFERENCES_DIR, exist_ok=True)
    import time
    filename = f"custom-{int(time.time())}.md"
    with open(os.path.join(REFERENCES_DIR, filename), "w") as f:
        f.write(text)
    # Index into memory
    def _index():
        try:
            m = get_memory()
            chunks = [text[i:i+500] for i in range(0, len(text), 450)]
            for chunk in chunks:
                if len(chunk.strip()) > 50:
                    m.add(f"[Reference: {filename}] {chunk.strip()}", user_id="reference", metadata={"type": "reference", "source": filename})
        except Exception:
            pass
    threading.Thread(target=_index, daemon=True).start()
    return JsonResponse({"status": "added", "file": filename})


def index(request):
    _load_references_bg()
    return render(request, "writer/index.html")


def list_files(request):
    """Return folder tree structure including empty folders."""
    tree = {}
    # Add top-level folders even if empty
    for d in os.listdir(MANUSCRIPTS_DIR):
        full = os.path.join(MANUSCRIPTS_DIR, d)
        if os.path.isdir(full) and not d.startswith("."):
            tree.setdefault(d, [])

    for root, dirs, filenames in os.walk(MANUSCRIPTS_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in filenames:
            if f.startswith("."):
                continue
            rel = os.path.relpath(os.path.join(root, f), MANUSCRIPTS_DIR)
            parts = rel.split(os.sep)
            folder = parts[0] if len(parts) > 1 else "_root"
            tree.setdefault(folder, []).append(rel)
    return JsonResponse({"tree": tree})


def read_file(request):
    filename = request.GET.get("file", "")
    filepath = os.path.join(MANUSCRIPTS_DIR, filename)
    if not os.path.realpath(filepath).startswith(os.path.realpath(MANUSCRIPTS_DIR)):
        return JsonResponse({"error": "Invalid path"}, status=400)
    if not os.path.isfile(filepath):
        return JsonResponse({"error": "File not found"}, status=404)
    with open(filepath, "r") as f:
        return JsonResponse({"file": filename, "content": f.read()})


@csrf_exempt
def save_file(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    data = json.loads(request.body)
    filename, content = data.get("file", ""), data.get("content", "")
    filepath = os.path.join(MANUSCRIPTS_DIR, filename)
    if not os.path.realpath(filepath).startswith(os.path.realpath(MANUSCRIPTS_DIR)):
        return JsonResponse({"error": "Invalid path"}, status=400)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(content)
    return JsonResponse({"status": "saved"})


@csrf_exempt
def create_folder(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    data = json.loads(request.body)
    folder = data.get("folder", "")
    path = os.path.join(MANUSCRIPTS_DIR, folder)
    if not os.path.realpath(path).startswith(os.path.realpath(MANUSCRIPTS_DIR)):
        return JsonResponse({"error": "Invalid path"}, status=400)
    os.makedirs(path, exist_ok=True)
    return JsonResponse({"status": "created"})


@csrf_exempt
def rename_file(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    data = json.loads(request.body)
    old = os.path.join(MANUSCRIPTS_DIR, data.get("old", ""))
    new = os.path.join(MANUSCRIPTS_DIR, data.get("new", ""))
    if not os.path.realpath(old).startswith(os.path.realpath(MANUSCRIPTS_DIR)):
        return JsonResponse({"error": "Invalid path"}, status=400)
    if not os.path.realpath(new).startswith(os.path.realpath(MANUSCRIPTS_DIR)):
        return JsonResponse({"error": "Invalid path"}, status=400)
    if not os.path.exists(old):
        return JsonResponse({"error": "File not found"}, status=404)
    os.makedirs(os.path.dirname(new), exist_ok=True)
    os.rename(old, new)
    return JsonResponse({"status": "renamed"})


@csrf_exempt
def delete_file(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    data = json.loads(request.body)
    filepath = os.path.join(MANUSCRIPTS_DIR, data.get("file", ""))
    if not os.path.realpath(filepath).startswith(os.path.realpath(MANUSCRIPTS_DIR)):
        return JsonResponse({"error": "Invalid path"}, status=400)
    if not os.path.exists(filepath):
        return JsonResponse({"error": "File not found"}, status=404)
    if os.path.isdir(filepath):
        import shutil
        shutil.rmtree(filepath)
    else:
        os.remove(filepath)
    return JsonResponse({"status": "deleted"})


@csrf_exempt
def ai_assist(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    data = json.loads(request.body)
    prompt = data.get("prompt", "")
    context = data.get("context", "")

    # Auto-load ALL project files as world knowledge
    world_knowledge = ""
    for root, dirs, filenames in os.walk(MANUSCRIPTS_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in filenames:
            if f.startswith("."):
                continue
            if f.endswith((".md", ".txt", ".script", ".fountain")):
                fpath = os.path.join(root, f)
                rel = os.path.relpath(fpath, MANUSCRIPTS_DIR)
                with open(fpath, "r") as fh:
                    content = fh.read()[:2000]
                world_knowledge += f"\n--- FILE: {rel} ---\n{content}\n"
                if len(world_knowledge) > 8000:
                    break

    # Retrieve relevant memories (only embedding call — fast ~0.5s)
    relevant_memories = ""
    try:
        results = get_memory().search(prompt, user_id="writer", limit=5)
        if results and results.get("results"):
            relevant_memories = "\n".join([f"- {r['memory']}" for r in results["results"]])
    except Exception:
        pass

    # Retrieve relevant reference material (RAG)
    reference_context = ""
    try:
        ref_results = get_memory().search(prompt, user_id="reference", limit=5)
        if ref_results and ref_results.get("results"):
            reference_context = "\n".join([r['memory'] for r in ref_results["results"]])
    except Exception:
        pass

    full_prompt = f"""You are a professional Indian screenwriter helping write a web series called "Corporate".
Genre: Dark comedy/thriller set in Indian startup culture.
Tone: Raw, aggressive, ambitious — like Scam 1992 meets TVF Pitchers.

COMPLETE PROJECT KNOWLEDGE (all files in the project):
{world_knowledge[:8000]}

{"SCREENWRITING REFERENCE KNOWLEDGE:" + chr(10) + reference_context if reference_context else ""}

{"MEMORY FROM PAST CONVERSATIONS:" + chr(10) + relevant_memories if relevant_memories else ""}

RULES:
- You know EVERYTHING about this project from the files above.
- Screenplay format (INT/EXT, character names CAPS, parentheticals)
- Dialogue in Hinglish — natural mix of Hindi + English + corporate jargon
- Be specific. Sharp memorable lines. No generic filler.
- Match character personalities from the files exactly.

CURRENT PAGE:
{context[:5000]}

REQUEST: {prompt}

Write directly. No preamble."""

    # Save question in background (doesn't block)
    _save_memory_bg(f"Writer asked: {prompt[:300]}", {"type": "query"})

    try:
        def stream():
            full_response = []
            with httpx.Client(timeout=120) as client:
                with client.stream("POST", OLLAMA_URL, json={"model": OLLAMA_MODEL, "prompt": full_prompt, "stream": True}) as resp:
                    for line in resp.iter_lines():
                        if line:
                            chunk = json.loads(line)
                            token = chunk.get("response", "")
                            if token:
                                full_response.append(token)
                                yield f"data: {json.dumps({'token': token})}\n\n"
                            if chunk.get("done"):
                                yield "data: {\"done\":true}\n\n"
            # Save response in background
            response_text = "".join(full_response)[:500]
            _save_memory_bg(f"AI responded about '{prompt[:100]}': {response_text}", {"type": "response"})
        return StreamingHttpResponse(stream(), content_type="text/event-stream")
    except httpx.ConnectError:
        return JsonResponse({"error": "Ollama not running. Run: ollama serve"}, status=503)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
