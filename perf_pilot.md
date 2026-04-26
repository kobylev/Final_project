# Product Requirements Document (PRD): OptiSharp

## 1. Executive Summary
**OptiSharp** is a specialized, local (air-gapped) AI assistant designed to optimize C# code for high-performance execution. Unlike general-purpose LLMs, this system focuses on identifying sub-optimal patterns and suggesting advanced .NET 8+ features such as Zero-allocation memory management (`Span<T>`), High-throughput I/O (`System.Threading.Channels`), and Hardware Intrinsics (SIMD).

## 2. Project Goals & Objectives
* **Air-Gapped Operation:** Fully functional without internet connectivity for secure environments.
* **Performance Intent Detection:** Identifying compute-heavy or I/O-heavy blocks automatically.
* **Low Overhead:** Small-scale Transformer model (15M-50M parameters) running efficiently on local CPUs.
* **Deterministic Accuracy:** A hybrid approach combining AI for detection and Roslyn-based templates for generation.

## 3. Competitive Advantage: OptiSharp vs. Local General LLMs (e.g., Gemma/Ollama)
While local models like Gemma and Ollama can provide general assistance, OptiSharp offers several critical advantages:
* **Guaranteed Compilation (Deterministic vs. Probabilistic):** Gemma and Ollama are general token predictors and can generate non-compilable or hallucinated C# suggestions. OptiSharp uses AI only to classify performance intent, while the actual code output is produced by expert-vetted Roslyn templates.
* **C# Performance Specialization:** General-purpose models often miss the nuances of `Span<T>`, `SIMD`, `Channels`, and I/O pipeline patterns. OptiSharp is specifically built to detect and suggest optimizations tailored for high-performance C#.
* **Proactive Analysis, not just completion:** Gemma and Ollama typically operate as completion engines or general assistants, while OptiSharp actively analyzes code and identifies performance bottlenecks during development.
* **Local resource efficiency:** Large local general models like Gemma and many Ollama deployments can require significant GPU/CPU memory. OptiSharp is designed as a compact 15M-50M parameter model with low memory overhead suitable for normal developer machines.
* **Deep Roslyn integration:** OptiSharp is anchored in Roslyn for structural analysis and stable code generation. This gives an advantage over general models that output free-form text without deep syntactic understanding of C#.

## 4. Proposed Architecture (Hybrid Model)
1.  **Intent Classification Engine (AI):** A custom-trained small LLM that identifies the developer's "intent" (e.g., "spatial calculations" or "mass file-read").
2.  **Expert Optimization Engine (Deterministic):** A rule-based system using Roslyn AST that injects pre-vetted templates based on the classified intent.

## 5. User Workflow
1.  **Trigger:** Developer highlights code or saves a file.
2.  **Context Extraction:** Roslyn extracts a clean AST of the block.
3.  **Local AI Inference:** The code is tokenized and classified into a domain (e.g., `IO_Intensive`).
4.  **Pattern Injection:** The extension maps the intent to a high-performance C# template.
5.  **Review:** A side-by-side Diff View appears in VS Code for user approval.

## 6. Architecture Diagram (Mermaid)
```mermaid
graph TD
    subgraph "Editor (VS Code)"
        A[Developer Writes Code] -->|Trigger| B(Roslyn Pre-processor)
    end

    subgraph "Local AI Engine (ONNX)"
        B -->|Clean AST| C{Intent Classifier}
        C -->|Label: IO_Intensive| D[Expert Template Selector]
        C -->|Label: Memory_Intensive| D
    end

    subgraph "Optimization Engine"
        D -->|Selected Template| E(Roslyn Code Injector)
        E -->|Final Code| F[Diff View & Apply]
    end
    
    F -->|Accept| G[Optimized C# Source]