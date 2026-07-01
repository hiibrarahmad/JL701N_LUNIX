---
tags: [guide, quick-start, build, setup]
date: 2026-05-01
difficulty: beginner
---

# 🚀 Building the Firmware

**Time:** 5 minutes | **Difficulty:** Beginner

---

## Prerequisites

- Windows workspace with VS Code
- Build system: `.vscode/winmk.bat` configured
- GCC compiler in PATH

---

## Quick Build Steps

### Step 1: Open Terminal
```
Press Ctrl+` to open VS Code terminal
CD to: D:\jl7016g final approach\SDKS\FIRST PERIORITY SDK
```

### Step 2: Clean Build (First Time)
```
.vscode/winmk.bat clean
.vscode/winmk.bat all
```

### Step 3: Verify Success
✅ Look for:
- `0 errors, 0 warnings`
- `ota.bin generated`
- Exit code: 0

---

## Build Artifacts

| Artifact | Purpose |
|----------|---------|
| **ota.bin** | Firmware image for deployment |
| **obj/Release/** | Compiled object files |
| **Build Log** | Detailed compilation output |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Build fails** | Check README → FIXING folder |
| **Undefined references** | Review board_*_cfg.h configuration |
| **Slow build** | Ensure clean build: `winmk.bat clean` first |

---

**Next Step:** [→ Configuration Guide](../GUIDES/README.md)
