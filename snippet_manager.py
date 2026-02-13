#!/usr/bin/env python3
"""
Code Snippet Manager - Save, tag, and retrieve code snippets with fuzzy search and syntax highlighting.
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from difflib import SequenceMatcher
import argparse
import subprocess

# Syntax highlighting
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer, get_all_lexers
from pygments.formatters import TerminalFormatter, Terminal256Formatter
from pygments.util import ClassNotFound

# Clipboard support
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False


class SnippetManager:
    """Main snippet manager class."""
    
    SNIPPETS_DIR = Path.home() / ".snippet_manager"
    SNIPPETS_FILE = SNIPPETS_DIR / "snippets.json"
    CONFIG_FILE = SNIPPETS_DIR / "config.json"
    
    def __init__(self):
        self.snippets: Dict[str, Any] = {}
        self.config = {"default_language": "text", "theme": "default"}
        self._ensure_dirs()
        self._load_data()
    
    def _ensure_dirs(self):
        """Create necessary directories."""
        self.SNIPPETS_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load_data(self):
        """Load snippets and config from disk."""
        if self.SNIPPETS_FILE.exists():
            try:
                with open(self.SNIPPETS_FILE, 'r', encoding='utf-8') as f:
                    self.snippets = json.load(f)
            except json.JSONDecodeError:
                self.snippets = {}
        
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self.config.update(json.load(f))
            except json.JSONDecodeError:
                pass
    
    def _save_data(self):
        """Save snippets to disk."""
        with open(self.SNIPPETS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.snippets, f, indent=2, ensure_ascii=False)
    
    def _save_config(self):
        """Save config to disk."""
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
    
    def _generate_id(self) -> str:
        """Generate a unique snippet ID."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _fuzzy_score(self, query: str, text: str) -> float:
        """Calculate fuzzy match score between query and text."""
        if not query or not text:
            return 0.0
        
        query = query.lower()
        text = text.lower()
        
        # Exact match gets highest score
        if query == text:
            return 100.0
        
        # Contains match
        if query in text:
            return 80.0 + (len(query) / len(text)) * 20
        
        # Word-by-word partial match
        query_words = query.split()
        text_words = text.split()
        
        matches = 0
        for qw in query_words:
            for tw in text_words:
                if qw in tw or SequenceMatcher(None, qw, tw).ratio() > 0.7:
                    matches += 1
                    break
        
        if matches == len(query_words):
            return 60.0 + (matches / len(query_words)) * 20
        
        # Sequence matcher as fallback
        return SequenceMatcher(None, query, text).ratio() * 50
    
    def add(self, title: str, code: str, language: str = "text", 
            tags: List[str] = None, description: str = "") -> str:
        """Add a new snippet."""
        snippet_id = self._generate_id()
        
        # Process tags
        if tags is None:
            tags = []
        tags = [t.strip().lower() for t in tags if t.strip()]
        
        self.snippets[snippet_id] = {
            "id": snippet_id,
            "title": title.strip(),
            "code": code,
            "language": language.lower(),
            "tags": tags,
            "description": description.strip(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        self._save_data()
        return snippet_id
    
    def get(self, snippet_id: str) -> Optional[Dict]:
        """Get a snippet by ID."""
        snippet = self.snippets.get(snippet_id)
        if snippet:
            snippet["usage_count"] = snippet.get("usage_count", 0) + 1
            snippet["last_used"] = datetime.now().isoformat()
            self._save_data()
        return snippet
    
    def update(self, snippet_id: str, **kwargs) -> bool:
        """Update an existing snippet."""
        if snippet_id not in self.snippets:
            return False
        
        allowed_fields = ["title", "code", "language", "tags", "description"]
        for field, value in kwargs.items():
            if field in allowed_fields:
                if field == "tags" and value:
                    value = [t.strip().lower() for t in value if t.strip()]
                self.snippets[snippet_id][field] = value
        
        self.snippets[snippet_id]["updated_at"] = datetime.now().isoformat()
        self._save_data()
        return True
    
    def delete(self, snippet_id: str) -> bool:
        """Delete a snippet."""
        if snippet_id in self.snippets:
            del self.snippets[snippet_id]
            self._save_data()
            return True
        return False
    
    def search(self, query: str, language: str = None, tags: List[str] = None,
               limit: int = 10) -> List[Dict]:
        """Fuzzy search snippets."""
        results = []
        query = query.lower() if query else ""
        
        for snippet in self.snippets.values():
            # Filter by language
            if language and snippet.get("language") != language.lower():
                continue
            
            # Filter by tags
            if tags:
                snippet_tags = set(snippet.get("tags", []))
                if not all(tag.lower() in snippet_tags for tag in tags):
                    continue
            
            # Calculate fuzzy score
            if query:
                title_score = self._fuzzy_score(query, snippet.get("title", ""))
                code_score = self._fuzzy_score(query, snippet.get("code", "")) * 0.5
                tag_score = max(
                    [self._fuzzy_score(query, tag) for tag in snippet.get("tags", [])] + [0]
                ) * 0.8
                desc_score = self._fuzzy_score(query, snippet.get("description", "")) * 0.6
                
                total_score = max(title_score, code_score, tag_score, desc_score)
                
                if total_score < 20:  # Threshold
                    continue
            else:
                total_score = snippet.get("usage_count", 0)  # Sort by usage if no query
            
            results.append({**snippet, "_score": total_score})
        
        # Sort by score descending
        results.sort(key=lambda x: x["_score"], reverse=True)
        return results[:limit]
    
    def list_tags(self) -> List[tuple]:
        """List all tags with counts."""
        tag_counts = {}
        for snippet in self.snippets.values():
            for tag in snippet.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    
    def list_languages(self) -> List[tuple]:
        """List all languages with counts."""
        lang_counts = {}
        for snippet in self.snippets.values():
            lang = snippet.get("language", "text")
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
        return sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)
    
    def get_stats(self) -> Dict:
        """Get snippet statistics."""
        total = len(self.snippets)
        languages = len(self.list_languages())
        tags = len(self.list_tags())
        total_usage = sum(s.get("usage_count", 0) for s in self.snippets.values())
        
        return {
            "total_snippets": total,
            "unique_languages": languages,
            "unique_tags": tags,
            "total_usage": total_usage
        }


class SnippetCLI:
    """Command-line interface for the snippet manager."""
    
    def __init__(self):
        self.manager = SnippetManager()
    
    def _highlight_code(self, code: str, language: str) -> str:
        """Apply syntax highlighting to code."""
        try:
            if language == "text":
                lexer = guess_lexer(code)
            else:
                lexer = get_lexer_by_name(language)
        except ClassNotFound:
            lexer = get_lexer_by_name("text")
        
        # Use 256 color formatter if terminal supports it
        formatter = Terminal256Formatter(style='monokai')
        return highlight(code, lexer, formatter)
    
    def _print_snippet(self, snippet: Dict, show_code: bool = True, 
                       highlight: bool = True):
        """Pretty print a snippet."""
        print(f"\n{'='*60}")
        print(f"📋 {snippet['title']}")
        print(f"   ID: {snippet['id']}")
        print(f"   Language: {snippet.get('language', 'text')}")
        print(f"   Tags: {', '.join(snippet.get('tags', [])) or 'none'}")
        
        if snippet.get('description'):
            print(f"   Description: {snippet['description']}")
        
        print(f"   Created: {snippet.get('created_at', 'unknown')[:10]}")
        print(f"   Used: {snippet.get('usage_count', 0)} times")
        
        if show_code and snippet.get('code'):
            print(f"\n{'─'*60}")
            if highlight and sys.stdout.isatty():
                try:
                    highlighted = self._highlight_code(
                        snippet['code'], 
                        snippet.get('language', 'text')
                    )
                    print(highlighted.rstrip())
                except Exception:
                    print(snippet['code'])
            else:
                print(snippet['code'])
            print(f"{'─'*60}")
    
    def _copy_to_clipboard(self, text: str) -> bool:
        """Copy text to clipboard."""
        if CLIPBOARD_AVAILABLE:
            try:
                pyperclip.copy(text)
                return True
            except Exception:
                pass
        
        # Fallback to pbcopy (macOS) or xclip/xsel (Linux)
        try:
            if sys.platform == 'darwin':
                subprocess.run(['pbcopy'], input=text.encode(), check=True)
                return True
            elif sys.platform == 'linux':
                subprocess.run(['xclip', '-selection', 'clipboard'], 
                             input=text.encode(), check=True)
                return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return False
    
    def cmd_add(self, args):
        """Handle add command."""
        # Read code from file or stdin
        code = args.code
        if args.file:
            with open(args.file, 'r') as f:
                code = f.read()
        elif not code:
            print("Enter code (Ctrl+D when done, Ctrl+C to cancel):")
            try:
                code = sys.stdin.read()
            except KeyboardInterrupt:
                print("\nCancelled.")
                return
        
        if not code.strip():
            print("Error: Code cannot be empty.")
            return
        
        # Parse tags
        tags = [t.strip() for t in args.tags.split(',')] if args.tags else []
        
        snippet_id = self.manager.add(
            title=args.title,
            code=code,
            language=args.language,
            tags=tags,
            description=args.description or ""
        )
        
        print(f"✅ Snippet added with ID: {snippet_id}")
    
    def cmd_get(self, args):
        """Handle get command."""
        snippet = self.manager.get(args.id)
        if not snippet:
            print(f"❌ Snippet not found: {args.id}")
            return
        
        self._print_snippet(snippet, show_code=not args.no_code)
        
        if args.copy:
            if self._copy_to_clipboard(snippet['code']):
                print("\n📋 Code copied to clipboard!")
            else:
                print("\n⚠️  Could not copy to clipboard.")
    
    def cmd_search(self, args):
        """Handle search command."""
        tags = [t.strip() for t in args.tags.split(',')] if args.tags else None
        
        results = self.manager.search(
            query=args.query or "",
            language=args.language,
            tags=tags,
            limit=args.limit
        )
        
        if not results:
            print("No snippets found.")
            return
        
        print(f"\n🔍 Found {len(results)} snippet(s):\n")
        
        for i, snippet in enumerate(results, 1):
            tags_str = ', '.join(snippet.get('tags', [])) or 'none'
            print(f"{i}. [{snippet['id']}] {snippet['title']}")
            print(f"   Language: {snippet.get('language', 'text')} | Tags: {tags_str}")
            
            if args.query:
                print(f"   Match score: {snippet['_score']:.1f}")
            
            if args.show_preview:
                preview = snippet['code'][:100].replace('\n', ' ')
                if len(snippet['code']) > 100:
                    preview += "..."
                print(f"   Preview: {preview}")
        
        # Interactive selection if requested
        if args.interactive and results:
            try:
                choice = input("\nEnter number to view (or Enter to skip): ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(results):
                    selected = results[int(choice) - 1]
                    self._print_snippet(selected)
                    
                    copy = input("Copy to clipboard? [y/N]: ").strip().lower()
                    if copy == 'y':
                        if self._copy_to_clipboard(selected['code']):
                            print("📋 Copied!")
            except (KeyboardInterrupt, EOFError):
                print()
    
    def cmd_list(self, args):
        """Handle list command."""
        results = self.manager.search(
            query="",
            language=args.language,
            limit=args.limit
        )
        
        if not results:
            print("No snippets found.")
            return
        
        print(f"\n📚 {len(results)} snippet(s):\n")
        
        for snippet in results:
            tags_str = ', '.join(snippet.get("tags", [])) or 'none'
            lang = snippet.get("language", "text")
            print(f"  [{snippet['id']}] {snippet['title']}")
            print(f"       {lang} | {tags_str} | used {snippet.get('usage_count', 0)}x")
    
    def cmd_edit(self, args):
        """Handle edit command."""
        snippet = self.manager.snippets.get(args.id)
        if not snippet:
            print(f"❌ Snippet not found: {args.id}")
            return
        
        updates = {}
        
        if args.title:
            updates['title'] = args.title
        if args.language:
            updates['language'] = args.language
        if args.tags is not None:
            updates['tags'] = [t.strip() for t in args.tags.split(',') if t.strip()]
        if args.description is not None:
            updates['description'] = args.description
        
        if args.code:
            if args.file:
                with open(args.file, 'r') as f:
                    updates['code'] = f.read()
            else:
                updates['code'] = args.code
        
        if self.manager.update(args.id, **updates):
            print(f"✅ Snippet updated: {args.id}")
        else:
            print("❌ Update failed.")
    
    def cmd_delete(self, args):
        """Handle delete command."""
        if args.force or input(f"Delete snippet {args.id}? [y/N]: ").lower() == 'y':
            if self.manager.delete(args.id):
                print(f"✅ Snippet deleted: {args.id}")
            else:
                print(f"❌ Snippet not found: {args.id}")
        else:
            print("Cancelled.")
    
    def cmd_tags(self, args):
        """Handle tags command."""
        tags = self.manager.list_tags()
        
        if not tags:
            print("No tags found.")
            return
        
        print(f"\n🏷️  {len(tags)} tag(s):\n")
        
        for tag, count in tags:
            print(f"  {tag}: {count} snippet(s)")
    
    def cmd_stats(self, args):
        """Handle stats command."""
        stats = self.manager.get_stats()
        
        print("\n📊 Snippet Manager Statistics")
        print(f"{'='*40}")
        print(f"  Total Snippets: {stats['total_snippets']}")
        print(f"  Unique Languages: {stats['unique_languages']}")
        print(f"  Unique Tags: {stats['unique_tags']}")
        print(f"  Total Usage: {stats['total_usage']}")
    
    def cmd_import(self, args):
        """Handle import command."""
        try:
            with open(args.file, 'r') as f:
                data = json.load(f)
            
            imported = 0
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, dict) and 'code' in value:
                        self.manager.add(
                            title=value.get('title', key),
                            code=value['code'],
                            language=value.get('language', 'text'),
                            tags=value.get('tags', []),
                            description=value.get('description', '')
                        )
                        imported += 1
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and 'code' in item:
                        self.manager.add(
                            title=item.get('title', 'Untitled'),
                            code=item['code'],
                            language=item.get('language', 'text'),
                            tags=item.get('tags', []),
                            description=item.get('description', '')
                        )
                        imported += 1
            
            print(f"✅ Imported {imported} snippet(s)")
        except Exception as e:
            print(f"❌ Import failed: {e}")
    
    def cmd_export(self, args):
        """Handle export command."""
        try:
            with open(args.file, 'w') as f:
                json.dump(self.manager.snippets, f, indent=2)
            print(f"✅ Exported to {args.file}")
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    def run(self):
        """Run the CLI."""
        parser = argparse.ArgumentParser(
            prog='snippet',
            description='Code Snippet Manager - Save, tag, and retrieve code snippets'
        )
        subparsers = parser.add_subparsers(dest='command', help='Commands')
        
        # Add command
        add_parser = subparsers.add_parser('add', help='Add a new snippet')
        add_parser.add_argument('title', help='Snippet title')
        add_parser.add_argument('-c', '--code', help='Code content')
        add_parser.add_argument('-f', '--file', help='Read code from file')
        add_parser.add_argument('-l', '--language', default='text', 
                               help='Programming language')
        add_parser.add_argument('-t', '--tags', help='Comma-separated tags')
        add_parser.add_argument('-d', '--description', help='Description')
        add_parser.set_defaults(func=self.cmd_add)
        
        # Get command
        get_parser = subparsers.add_parser('get', help='Get snippet by ID')
        get_parser.add_argument('id', help='Snippet ID')
        get_parser.add_argument('-n', '--no-code', action='store_true',
                               help='Show metadata only')
        get_parser.add_argument('-c', '--copy', action='store_true',
                               help='Copy code to clipboard')
        get_parser.set_defaults(func=self.cmd_get)
        
        # Search command
        search_parser = subparsers.add_parser('search', help='Search snippets')
        search_parser.add_argument('query', nargs='?', help='Search query')
        search_parser.add_argument('-l', '--language', help='Filter by language')
        search_parser.add_argument('-t', '--tags', help='Filter by tags (comma-separated)')
        search_parser.add_argument('-n', '--limit', type=int, default=10,
                                  help='Max results')
        search_parser.add_argument('-p', '--show-preview', action='store_true',
                                  help='Show code preview')
        search_parser.add_argument('-i', '--interactive', action='store_true',
                                  help='Interactive selection')
        search_parser.set_defaults(func=self.cmd_search)
        
        # List command
        list_parser = subparsers.add_parser('list', help='List all snippets')
        list_parser.add_argument('-l', '--language', help='Filter by language')
        list_parser.add_argument('-n', '--limit', type=int, default=50,
                                help='Max results')
        list_parser.set_defaults(func=self.cmd_list)
        
        # Edit command
        edit_parser = subparsers.add_parser('edit', help='Edit a snippet')
        edit_parser.add_argument('id', help='Snippet ID')
        edit_parser.add_argument('-T', '--title', help='New title')
        edit_parser.add_argument('-c', '--code', help='New code')
        edit_parser.add_argument('-f', '--file', help='Read code from file')
        edit_parser.add_argument('-l', '--language', help='New language')
        edit_parser.add_argument('-t', '--tags', help='New tags (comma-separated)')
        edit_parser.add_argument('-d', '--description', help='New description')
        edit_parser.set_defaults(func=self.cmd_edit)
        
        # Delete command
        del_parser = subparsers.add_parser('delete', help='Delete a snippet')
        del_parser.add_argument('id', help='Snippet ID')
        del_parser.add_argument('-f', '--force', action='store_true',
                               help='Force deletion without confirmation')
        del_parser.set_defaults(func=self.cmd_delete)
        
        # Tags command
        tags_parser = subparsers.add_parser('tags', help='List all tags')
        tags_parser.set_defaults(func=self.cmd_tags)
        
        # Stats command
        stats_parser = subparsers.add_parser('stats', help='Show statistics')
        stats_parser.set_defaults(func=self.cmd_stats)
        
        # Import command
        import_parser = subparsers.add_parser('import', help='Import snippets from JSON')
        import_parser.add_argument('file', help='JSON file to import')
        import_parser.set_defaults(func=self.cmd_import)
        
        # Export command
        export_parser = subparsers.add_parser('export', help='Export snippets to JSON')
        export_parser.add_argument('file', help='Output JSON file')
        export_parser.set_defaults(func=self.cmd_export)
        
        args = parser.parse_args()
        
        if args.command is None:
            parser.print_help()
            sys.exit(1)
        
        args.func(args)


def main():
    """Entry point."""
    cli = SnippetCLI()
    cli.run()


if __name__ == '__main__':
    main()
