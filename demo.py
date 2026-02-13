#!/usr/bin/env python3
"""
Demo script to showcase the Snippet Manager functionality.
"""

import subprocess
import sys
import tempfile
import os


def run_cmd(cmd):
    """Run a command and print it."""
    print(f"\n{'='*60}")
    print(f"$ {cmd}")
    print('='*60)
    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
    return result.returncode == 0


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║              🚀 SNIPPET MANAGER DEMO 🚀                      ║
║                                                              ║
║  This demo will create some sample snippets and demonstrate  ║
║  the fuzzy search, syntax highlighting, and tagging system.  ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Check if snippet command is available
    result = subprocess.run("which snippet_manager.py || which snippet", 
                           shell=True, capture_output=True, text=True)
    if not result.stdout.strip():
        print("❌ Snippet manager not found!")
        print("Please install it first: pip install -e .")
        sys.exit(1)
    
    snippet_cmd = "python3 snippet_manager.py"
    
    print("Step 1: Creating sample snippets...")
    input("Press Enter to continue...")
    
    # Create sample Python snippet
    python_code = '''def fibonacci(n):
    \"\"\"Generate Fibonacci sequence up to n terms.\"\"\"
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[-1] + fib[-2])
    return fib

# Usage
print(fibonacci(10))  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(python_code)
        temp_file = f.name
    
    run_cmd(f'{snippet_cmd} add "Fibonacci Sequence" -l python -t "algorithm,math,utility" -f {temp_file}')
    os.unlink(temp_file)
    
    # Create sample JavaScript snippet
    js_code = '''// Debounce function to limit how often a function can fire
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Usage
const handleSearch = debounce((query) => {
    console.log('Searching for:', query);
}, 300);'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
        f.write(js_code)
        temp_file = f.name
    
    run_cmd(f'{snippet_cmd} add "Debounce Function" -l javascript -t "utility,frontend,performance" -f {temp_file}')
    os.unlink(temp_file)
    
    # Create sample SQL snippet
    sql_code = '''-- Find duplicate records based on email
SELECT email, COUNT(*) as count
FROM users
GROUP BY email
HAVING COUNT(*) > 1;

-- Get users with their order counts
SELECT 
    u.id,
    u.name,
    u.email,
    COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
        f.write(sql_code)
        temp_file = f.name
    
    run_cmd(f'{snippet_cmd} add "SQL Common Queries" -l sql -t "database,postgres,utility" -f {temp_file}')
    os.unlink(temp_file)
    
    # Create sample Bash snippet
    bash_code = '''#!/bin/bash

# Backup script with timestamp
BACKUP_DIR="/backups"
SOURCE_DIR="/home/user/documents"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${TIMESTAMP}.tar.gz"

# Create backup
tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" "${SOURCE_DIR}"

# Keep only last 7 backups
ls -t ${BACKUP_DIR}/backup_*.tar.gz | tail -n +8 | xargs rm -f

echo "Backup created: ${BACKUP_FILE}"'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(bash_code)
        temp_file = f.name
    
    run_cmd(f'{snippet_cmd} add "Backup Script" -l bash -t "devops,automation" -f {temp_file}')
    os.unlink(temp_file)
    
    print("\n✅ Sample snippets created!")
    input("\nPress Enter to continue to listing...")
    
    # List all snippets
    run_cmd(f'{snippet_cmd} list')
    
    input("\nPress Enter to continue to tag listing...")
    
    # List tags
    run_cmd(f'{snippet_cmd} tags')
    
    input("\nPress Enter to continue to fuzzy search demo...")
    
    # Fuzzy search demos
    print("\n🔍 Searching for 'fib' (should match Fibonacci)...")
    run_cmd(f'{snippet_cmd} search "fib"')
    
    input("\nPress Enter...")
    
    print("\n🔍 Searching for 'debounce' in JavaScript...")
    run_cmd(f'{snippet_cmd} search "deb" -l javascript')
    
    input("\nPress Enter...")
    
    print("\n🔍 Searching with tag filter 'utility'...")
    run_cmd(f'{snippet_cmd} search "" -t "utility"')
    
    input("\nPress Enter to view statistics...")
    
    # Statistics
    run_cmd(f'{snippet_cmd} stats')
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                     🎉 DEMO COMPLETE! 🎉                      ║
║                                                              ║
║  You've seen:                                                ║
║  ✅ Adding snippets with metadata                            ║
║  ✅ Listing all snippets                                     ║
║  ✅ Tag organization                                         ║
║  ✅ Fuzzy search across titles, code, and tags               ║
║  ✅ Language filtering                                       ║
║  ✅ Usage statistics                                         ║
║                                                              ║
║  Try it yourself:                                            ║
║    snippet add "My Snippet" -l python -t "test"              ║
║    snippet search "my snippet"                               ║
╚══════════════════════════════════════════════════════════════╝
""")


if __name__ == '__main__':
    main()
