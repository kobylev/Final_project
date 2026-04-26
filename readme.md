# PerfPilot: AI-Powered C# Performance Optimizer

> A local, air-gapped AI assistant that detects performance bottlenecks in C# code and suggests production-ready .NET 10+ optimizations — deterministically, without hallucination.

[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![.NET](https://img.shields.io/badge/.NET-10.0-512BD4?style=flat-square&logo=dotnet)](https://dotnet.microsoft.com)

## The Problem
Optimizing C# for high-performance (low allocation, high throughput) requires deep knowledge of `Span<T>`, `Memory<T>`, `System.Threading.Channels`, and SIMD. General-purpose AI assistants (like ChatGPT or local LLMs) often:
1.  **Hallucinate:** Suggest APIs that don't exist or don't compile.
2.  **Lack Precision:** Miss subtle performance bugs like boxed allocations in hot loops.
3.  **Security Risk:** Require sending sensitive proprietary code to the cloud.

## The Solution: PerfPilot
PerfPilot uses a **hybrid AI + Deterministic** approach:
1.  **AI (Intent Classifier):** A small, fast Transformer model (15M-50M parameters) runs locally to identify the *performance intent* of your code (e.g., "This looks like a mass file read").
2.  **Deterministic (Roslyn):** Instead of the AI writing code, PerfPilot uses **expert-vetted Roslyn templates** to inject the optimized pattern. You get the speed of AI with the reliability of a compiler-grade tool.

## Key Features
| Feature | Description |
| :--- | :--- |
| 1 | **100% Local & Private** | No code ever leaves your machine. Perfect for secure/air-gapped environments. |
| 2 | **Zero-Hallucination** | Code optimizations are pulled from static templates, not generated token-by-token. |
| 3 | **VS Code Integration** | Inline suggestions and side-by-side diff views. |
| 4 | **Low Overhead** | Runs comfortably on a standard laptop CPU (no high-end GPU required). |
| 5 | **Deep .NET 10+ specialization** | Purpose-built for modern C# performance patterns, not a general-purpose assistant. |

---

## Comparison: Why PerfPilot?

| Metric | General LLM (Gemma/Ollama) | **PerfPilot** |
| :--- | :--- | :--- |
| **Connectivity** | Local or Cloud | **Strictly Local** |
| **Compilation** | Probabilistic (May fail) | **Guaranteed (Deterministic)** |
| **.NET 10 API accuracy** | ⚠️ Hit or miss | ✅ Expert-audited templates |
| **Security** | Depends on config | ✅ Air-gap safe |
| **Memory footprint** | ❌ 4–8 GB+ RAM | ✅ < 500 MB |

---

## Repository Structure
```text
.
├── extension/          # VS Code Extension (TypeScript)
├── ai-engine/          # Intent Classifier (Python + PyTorch + ONNX)
├── roslyn-service/     # .NET 10 C# sidecar (AST extractor + code injector)
├── data/               # Dataset generation & training scripts
└── scripts/            # Build and orchestration scripts
```

---

## Getting Started

### Prerequisites
- **VS Code** 1.85+
- **.NET 10** — Roslyn sidecar process
- **Python 3.10+** (for local AI inference)

### Installation
1.  Clone the repository:
    ```bash
    git clone https://github.com/your-repo/perfpilot.git
    ```
2.  Install the VS Code extension (details in `extension/README.md`).
3.  The extension will automatically manage the local AI engine and Roslyn service.

---

## Roadmap
| Phase | Goal | Status |
| :--- | :--- | :--- |
| M1 | Intent Taxonomy | ✅ Complete |
| M2 | Dataset Generation | 🔲 In progress |
| M3 | Local Transformer Training | 🔲 Pending |
| M4 | Template Library (8 labels) | 🔲 In progress |
| M5 | VS Code Extension V1 | 🔲 Pending |

---

## License
MIT License - see [LICENSE](LICENSE) for details.
