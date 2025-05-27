# Translation Language Checker

A standalone command-line tool that checks if your Android `strings.xml` file contains missing or untranslated (e.g., English) entries. It uses a lightweight [FastText](https://fasttext.cc/) model to detect language and outputs the results as a CSV.

---

## ✅ Features

- Parses Android-style `strings.xml` files
- Detects untranslated or empty strings
- Uses Facebook's `lid.176.ftz` language model (~960 KB)
- Outputs a detailed `output.csv` report
- Packaged as a **single-file binary** (no Python needed)

---

## 🚀 Quick Start

### 1. **Download the Release**

- [📦 Download the latest release](https://github.com/DeakyuLee/TranslationChecker/releases/tag/v1.0.0)
- translation_checker

---

### 2. **Prepare Your Config File**

Create a file called `config.json` in the **same folder** as the binary:

```json
{
  "input_file": "strings.xml",
  "output_file": "output.csv"
}
```

### 3. Update permission

run `chmod +x translation_checker`

### 4. Run the binary

run `./translation_checker`

### 5. (Optional) When running on mac

run `xattr -d com.apple.quarantine translation_checker` to override Gatekeeper warning
