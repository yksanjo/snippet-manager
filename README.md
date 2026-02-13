# 🚀 Code Snippet Manager

A powerful CLI tool for developers to save, tag, search, and retrieve code snippets with **fuzzy search** and **syntax highlighting**.

## ✨ Features

- 💾 **Save snippets** with metadata (title, language, tags, description)
- 🔍 **Fuzzy search** across titles, tags, descriptions, and code
- 🎨 **Syntax highlighting** in the terminal
- 🏷️ **Tagging system** for easy organization
- 📋 **Clipboard integration** - copy snippets with one command
- 📊 **Usage tracking** - see which snippets you use most
- 📤 **Import/Export** - backup and share your snippets
- 🖥️ **Interactive mode** - browse results and select interactively

## 📦 Installation

```bash
# Clone or download the repository
cd snippet_manager

# Install dependencies
pip install -r requirements.txt

# Make executable (optional)
chmod +x snippet_manager.py

# Create an alias for easy access (recommended)
echo 'alias snippet="python3 /path/to/snippet_manager.py"' >> ~/.bashrc
# or for zsh
echo 'alias snippet="python3 /path/to/snippet_manager.py"' >> ~/.zshrc
```

## 🚀 Quick Start

```bash
# Add a new snippet
snippet add "Python HTTP Request" -l python -t "api,requests,http"

# Search snippets
snippet search "http request"

# Get snippet by ID
snippet get abc123 -c  # -c copies to clipboard

# List all snippets
snippet list

# View statistics
snippet stats
```

## 📖 Usage

### Adding Snippets

```bash
# Add from command line
snippet add "Quick Sort" -l python -t "algorithm,sorting" -c "def quicksort(arr): ..."

# Add from file
snippet add "Config Template" -l yaml -t "config" -f ./template.yaml

# Add interactively (enter code via stdin)
snippet add "Database Query" -l sql -t "postgres"
# Then paste your code and press Ctrl+D
```

### Searching

```bash
# Basic fuzzy search
snippet search "python http"

# Search with language filter
snippet search "function" -l javascript

# Search with tag filter
snippet search "auth" -t "security,api"

# Interactive search with preview
snippet search "class" -i -p
```

### Retrieving Snippets

```bash
# View snippet
snippet get abc123

# View without code (metadata only)
snippet get abc123 -n

# Copy to clipboard
snippet get abc123 -c
```

### Managing Snippets

```bash
# List all snippets
snippet list

# List snippets by language
snippet list -l python

# Edit a snippet
snippet edit abc123 -t "new title" -l golang

# Delete a snippet
snippet delete abc123

# Force delete (no confirmation)
snippet delete abc123 -f
```

### Tags & Statistics

```bash
# List all tags
snippet tags

# View statistics
snippet stats
```

### Import/Export

```bash
# Export all snippets
snippet export my_snippets.json

# Import snippets
snippet import my_snippets.json
```

## 🎯 Fuzzy Search Examples

The fuzzy search works across multiple fields:

```bash
# Matches "Fibonacci" even if you type "fib"
snippet search "fib"

# Matches tags containing "api"
snippet search "api"

# Partial word matches work too
snippet search "qsort"  # Matches "Quick Sort"

# Multi-word queries
snippet search "python database connection"
```

## 🎨 Supported Languages

The snippet manager supports syntax highlighting for 500+ languages including:

- Python, JavaScript, TypeScript, Go, Rust
- SQL, Bash, PowerShell
- HTML, CSS, JSON, YAML, Markdown
- C, C++, Java, C#, Swift
- And many more...

Use any language name or alias that Pygments supports.

## 📁 Data Storage

Snippets are stored in `~/.snippet_manager/snippets.json` as plain JSON for easy backup and version control.

## 🔧 Configuration

Configuration is stored in `~/.snippet_manager/config.json`:

```json
{
  "default_language": "text",
  "theme": "default"
}
```

## 💡 Tips

1. **Use descriptive titles** - Makes searching easier
2. **Tag consistently** - Use common tags like `utility`, `algorithm`, `config`
3. **Add descriptions** - For complex snippets, add context
4. **Track usage** - Popular snippets bubble up in search results
5. **Export regularly** - Backup your snippet library

## 🛠️ Keyboard Shortcuts in Interactive Mode

When using `-i` (interactive) flag:
- Enter number to view snippet
- Press `y` to copy to clipboard
- Press Enter to skip

## 📋 Requirements

- Python 3.7+
- pygments (syntax highlighting)
- pyperclip (clipboard support, optional)

## 📝 License

MIT License - Feel free to use, modify, and share!

---

Happy coding! 🎉
