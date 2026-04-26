# PerfPilot — Project TODO & Action Plan

> **Goal:** Build a local, air-gapped VS Code extension that uses a small AI intent-classifier + Roslyn-based deterministic templates to suggest high-performance C# optimizations.

---

## Phase 0 — Project Setup & Scaffolding

### 0.1 — Init the VS Code extension project
- [ ] Scaffold a TypeScript VS Code extension with `yo code`
- [ ] Set up a monorepo structure: `extension/`, `ai-engine/`, `roslyn-service/`, `templates/`
- [ ] Configure `tsconfig.json`, `eslint`, `prettier`, `.gitignore`

**🤖 AI Prompt (Claude Code / Cursor):**
```
Create a VS Code TypeScript extension scaffold called "perf-pilot".
The repo should have 4 folders:
- extension/ (VS Code TypeScript extension)
- ai-engine/ (Python ONNX inference server)
- roslyn-service/ (C# .NET 8 console app acting as a local LSP sidecar)
- templates/ (JSON files mapping intent labels to Roslyn code templates)

Generate the root package.json, tsconfig.json, .eslintrc, .gitignore, and
a README.md explaining the architecture. Use VS Code extension API v1.90+.
```

---

### 0.2 — Define the intent taxonomy
- [ ] Define the full list of performance intent labels (e.g., `IO_Intensive`, `Memory_Intensive`, `Compute_SIMD`, `Concurrent_Throughput`, `String_Processing`)
- [ ] Create a `taxonomy.json` with label → description → example code snippets

**🤖 AI Prompt:**
```
I'm building a C# performance AI tool. Define a JSON taxonomy of exactly 8
performance intent labels for .NET 8+ code.
For each label provide:
- id (snake_case)
- description (one sentence)
- typical_patterns (list of 3 code patterns that match this intent)
- target_optimization (the .NET 8 feature to suggest: e.g., Span<T>, Channels, SIMD)
- anti_patterns (2 common anti-patterns that should trigger this label)

Output only valid JSON, no markdown.
```

---

## Phase 1 — Roslyn Service (C# Sidecar)

### 1.1 — Build the AST Extractor
- [ ] Create a .NET 8 console app in `roslyn-service/`
- [ ] Use `Microsoft.CodeAnalysis.CSharp` (Roslyn) to parse a C# snippet
- [ ] Extract: method name, parameter types, loop patterns, allocation sites, async/await usage
- [ ] Output a clean JSON summary of the AST

**🤖 AI Prompt (use in Claude Code or Cursor):**
```
Write a .NET 8 C# console app using Microsoft.CodeAnalysis.CSharp (Roslyn).
It should:
1. Accept a C# code snippet via stdin (as plain text)
2. Parse it into a SyntaxTree
3. Walk the AST and extract:
   - All method declarations (name, return type, parameters)
   - All for/foreach/while loops (nesting level, body size in lines)
   - All `new` allocations inside loops
   - All async/await usages
   - All array/List<T> declarations
4. Output a JSON summary to stdout

Use SyntaxWalker pattern. Add error handling for parse failures.
```

### 1.2 — Build the Roslyn Code Injector
- [ ] Accept an intent label + original AST + template JSON
- [ ] Use Roslyn SyntaxRewriter to replace the original code with the optimized template
- [ ] Output the final optimized C# as formatted source code

**🤖 AI Prompt:**
```
Write a .NET 8 C# class called `RoslynCodeInjector` that:
1. Takes as input: (a) original C# method source string, (b) a JSON template
   containing a code pattern with {PLACEHOLDER} tokens
2. Uses Roslyn CSharpSyntaxRewriter to replace the original method body
   with the template, substituting placeholders with actual variable names
   from the original AST
3. Returns the final formatted C# source using Roslyn's Formatter

Show usage example with a method that uses List<byte> replaced by ArrayPool<byte>.
```

### 1.3 — Template Library
- [ ] Create JSON template files for each intent label in `templates/`
- [ ] Templates must include: intent_id, description, before_pattern, after_code, nuget_dependencies

**🤖 AI Prompt:**
```
Create 8 Roslyn code-injection templates in JSON format, one for each of
these .NET 8 performance optimizations:
1. ArrayPool<T> instead of new T[]
2. Span<T> for string slicing
3. System.Threading.Channels for producer-consumer
4. SIMD via System.Runtime.Intrinsics
5. MemoryMarshal for zero-copy casting
6. IAsyncEnumerable for async streams
7. stackalloc for small fixed-size buffers
8. RecyclableMemoryStream for large I/O

Each template JSON must have:
{ "intent_id": "...", "description": "...", "before_example": "...",
  "after_template": "...", "nuget": ["..."] }

Ensure the after_template uses {VAR_NAME} and {TYPE} as substitution tokens.
```

---

## Phase 2 — AI Intent Classifier

### 2.1 — Dataset Creation
- [ ] Generate a labeled dataset of C# code snippets (min 500 per label × 8 labels = 4,000 samples)
- [ ] Format: `{ "code": "...", "label": "IO_Intensive" }`
- [ ] Split 80/10/10 train/val/test

**🤖 AI Prompt (run in a loop / batch):**
```
Generate 20 realistic C# code snippets that clearly demonstrate IO_Intensive
behavior (file reads, network calls, database queries with blocking patterns).
Each snippet should be a complete method, 10-40 lines, using .NET standard
APIs (File, HttpClient, SqlCommand, etc.) WITHOUT any performance optimizations.
Output as a JSON array: [{ "code": "...", "label": "IO_Intensive" }]
Output only valid JSON.
```
> **Agent suggestion:** Use a **batch generation agent** — loop this prompt 8× (one per label), vary the seed instructions each time. A Claude Code script can call the Anthropic API in a loop and write each result to `data/raw/{label}.json`.

### 2.2 — Tokenizer & Model Training
- [ ] Use `microsoft/codebert-base` as the backbone (pre-trained on code)
- [ ] Fine-tune with `transformers` + `torch` for 8-class classification
- [ ] Export to ONNX with `torch.onnx.export`

**🤖 AI Prompt:**
```
Write a complete Python training script using HuggingFace Transformers to
fine-tune microsoft/codebert-base for 8-class text classification.
Input: a JSONL file at data/train.jsonl with fields "code" and "label".
Steps:
1. Load and tokenize with AutoTokenizer (max_length=512)
2. Map string labels to integers via a label2id dict
3. Fine-tune with Trainer API, 3 epochs, batch size 16, lr=2e-5
4. Evaluate on data/val.jsonl
5. Export the best model to ONNX format at model/perf_pilot.onnx
6. Save label2id.json alongside the ONNX model

Use argparse for config. Add a __main__ guard.
```

### 2.3 — ONNX Inference Server
- [ ] Build a lightweight Python FastAPI server in `ai-engine/`
- [ ] Endpoint: `POST /classify` — accepts `{ "code": "..." }`, returns `{ "label": "...", "confidence": 0.97 }`
- [ ] Uses `onnxruntime` (CPU-only, no GPU dependency)

**🤖 AI Prompt:**
```
Write a FastAPI app in Python that:
1. At startup, loads model/perf_pilot.onnx via onnxruntime.InferenceSession
   and model/label2id.json
2. Exposes POST /classify accepting JSON body { "code": "string" }
3. Tokenizes the code with the saved tokenizer, runs ONNX inference,
   returns { "label": "...", "confidence": float, "all_scores": {...} }
4. Runs on localhost:5050 (uvicorn)
5. Has a GET /health endpoint returning { "status": "ok" }

Use only: fastapi, uvicorn, onnxruntime, transformers (tokenizer only).
No GPU dependencies.
```

---

## Phase 3 — VS Code Extension (TypeScript)

### 3.1 — Sidecar Process Manager
- [ ] On extension activation, spawn the Python ONNX server and Roslyn sidecar as child processes
- [ ] Implement health-check polling until both are ready
- [ ] Shut them down on extension deactivation

**🤖 AI Prompt:**
```
Write a TypeScript VS Code extension module called SidecarManager that:
1. On activate(), spawns two child processes:
   - Python: `python ai-engine/server.py` on port 5050
   - .NET: `dotnet roslyn-service/RoslynService.dll` on port 5051
2. Polls GET /health on each port every 500ms until both return 200
3. Shows a VS Code status bar item "PerfPilot: Starting..." → "PerfPilot: Ready"
4. On deactivate(), kills both child processes gracefully
5. Logs all stdout/stderr to an Output Channel called "PerfPilot Logs"

Use VS Code API (vscode.window, child_process). TypeScript only.
```

### 3.2 — Trigger & Context Extraction
- [ ] Listen for `onDidSaveTextDocument` and text selection events on `.cs` files
- [ ] Send the selected (or active method's) code to the Roslyn sidecar for AST extraction
- [ ] Pass the resulting AST JSON to the AI classifier

**🤖 AI Prompt:**
```
Write a TypeScript VS Code extension command handler for "perfpilot.analyze".
It should:
1. Get the active TextEditor; if not a .cs file, show a warning
2. Get the selected text (or if no selection, get the entire document text)
3. POST the code to http://localhost:5051/extract-ast (Roslyn sidecar)
4. Take the JSON AST response and POST it to http://localhost:5050/classify
5. Return the combined result: { ast: {...}, label: "...", confidence: 0.95 }
6. Show a VS Code notification: "Detected: IO_Intensive (95% confidence)"

Add error handling for network failures with user-friendly messages.
```

### 3.3 — Diff View & Apply
- [ ] Fetch the optimized code from the Roslyn injector
- [ ] Open a VS Code diff editor: original vs. optimized
- [ ] Add "Apply Optimization" and "Dismiss" buttons via a Webview panel

**🤖 AI Prompt:**
```
Write a TypeScript VS Code extension module that:
1. Takes: original C# code string and optimized C# code string
2. Saves both to temp files using `os.tmpdir()`
3. Opens VS Code diff editor with vscode.commands.executeCommand(
   'vscode.diff', originalUri, optimizedUri, 'PerfPilot: Suggested Optimization')
4. Shows a VS Code information message with two buttons: "Apply" and "Dismiss"
5. If "Apply": replaces the selection in the active editor with the optimized code
6. If "Dismiss": closes the diff editor

Use VS Code WorkspaceEdit for applying changes.
```

---

## Phase 4 — Integration & Testing

### 4.1 — End-to-end integration test
- [ ] Write a test fixture with 8 C# files (one per intent label) with known sub-optimal patterns
- [ ] Assert: correct label detected, correct template injected, output compiles

**🤖 AI Prompt:**
```
Write 8 C# test fixture files, one per intent label:
[IO_Intensive, Memory_Intensive, Compute_SIMD, Concurrent_Throughput,
String_Processing, Allocation_Heavy, Async_Stream, Buffer_Reuse]

Each file must:
- Contain one realistic but sub-optimal method (10-30 lines)
- Have a comment at the top: // EXPECTED_LABEL: <label>
- Be syntactically valid .NET 8 C#

These will be used as ground-truth test inputs for the PerfPilot pipeline.
```

### 4.2 — CI Pipeline
- [ ] GitHub Actions: lint → unit tests → ONNX model smoke test → extension package

**🤖 AI Prompt:**
```
Write a GitHub Actions workflow file (.github/workflows/ci.yml) for a
monorepo with:
- extension/ (Node.js TypeScript, tested with `npm test`)
- ai-engine/ (Python, tested with `pytest`)
- roslyn-service/ (C# .NET 8, tested with `dotnet test`)

Jobs:
1. lint: ESLint on extension/, flake8 on ai-engine/
2. test-extension: Node 20, npm ci, npm test
3. test-python: Python 3.11, pip install, pytest ai-engine/tests/
4. test-roslyn: dotnet 8, dotnet test roslyn-service/
5. package: on main branch only, run `vsce package` and upload artifact

All jobs run on ubuntu-latest.
```

---

## Phase 5 — Polish & Delivery

### 5.1 — Settings & Configuration
- [ ] Add VS Code extension settings: `perfpilot.autoAnalyzeOnSave`, `perfpilot.confidenceThreshold`, `perfpilot.modelPath`

**🤖 AI Prompt:**
```
Add these VS Code extension settings to package.json contributes.configuration:
- perfpilot.autoAnalyzeOnSave (boolean, default: true)
- perfpilot.confidenceThreshold (number, default: 0.80, min: 0.5, max: 1.0)
- perfpilot.modelPath (string, default: "bundled", description: path to custom ONNX model)
- perfpilot.enableTelemetry (boolean, default: false)

Then write the TypeScript code to read these settings via
vscode.workspace.getConfiguration('perfpilot') and export them as a typed config object.
```

### 5.2 — README & Demo
- [ ] Write a polished README with architecture diagram (Mermaid), installation steps, and GIF demo
- [ ] Record a demo: write bad C# → PerfPilot triggers → diff shows → apply → faster code

**🤖 AI Prompt:**
```
Write a professional GitHub README.md for a VS Code extension called PerfPilot.
Include:
1. Tagline and 3-sentence description
2. The Mermaid architecture diagram (Editor → Roslyn → ONNX Classifier → Template Injector → Diff View)
3. Features section (bullet list of 5 key capabilities)
4. Installation section (VS Code marketplace + manual VSIX)
5. How It Works section (numbered steps matching the user workflow)
6. Supported Optimizations table (label | .NET feature | example)
7. Configuration section (all 4 settings with descriptions)
8. Contributing & License section

Use shields.io badges for build status, license, VS Code installs.
```

---

## Suggested Agent Architecture

| Agent | Tool | Role |
|---|---|---|
| **Dataset Agent** | Claude API (loop) | Generate 4,000+ labeled C# snippets |
| **Code Agent** | Claude Code (terminal) | Scaffold files, run scripts, compile checks |
| **Training Agent** | Python script (local) | Fine-tune CodeBERT, export ONNX |
| **Test Agent** | Claude Code | Write and run unit tests, fix failures |
| **Review Agent** | Claude chat | Review architecture decisions, audit templates |

---

## Milestones

| # | Milestone | Deliverable |
|---|---|---|
| M1 | Roslyn sidecar working | AST JSON from any C# snippet |
| M2 | Classifier trained | ONNX model, >85% accuracy on test set |
| M3 | Extension MVP | Trigger → classify → diff → apply |
| M4 | All 8 templates wired | Full intent → optimization pipeline |
| M5 | CI green + packaged | `.vsix` file ready for submission |

---

## Key Dependencies

| Package | Purpose |
|---|---|
| `microsoft/codebert-base` | Pre-trained code model for fine-tuning |
| `onnxruntime` | CPU-only ONNX inference |
| `Microsoft.CodeAnalysis.CSharp` | Roslyn AST parsing & rewriting |
| `fastapi` + `uvicorn` | Lightweight ONNX inference server |
| `vsce` | VS Code extension packaging |
| `@types/vscode` | VS Code TypeScript API |