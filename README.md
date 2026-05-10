# notes2flow — Local Ollama Version (Deprecated)

 **This branch is not actively maintained.** 

For the current version , see the [main branch](https://github.com/04Shubhankar/notes2flow).

---

## Local Setup (Ollama)

This version runs completely locally using Ollama. No API costs, no internet required.

### Requirements
- Python 3.10+
- Ollama ([Download](https://ollama.ai))

### Steps

1. **Pull Ollama model**
```bash
   ollama pull gemma2:2b
```

2. **Install dependencies**
```bash
   cd backend
   pip install -r requirements.txt
```

3. **Start backend**
```bash
   python -m uvicorn app.main:app --reload
```

4. **Open frontend**
   - Go to `frontend/index.html` and open in browser
   - Or run: `python -m http.server 8000` in frontend folder

5. **Use it**
   - Paste notes → Click "Format & Generate" → Flowchart appears

Done.
