#!/usr/bin/env python3
import os
import re

def remove_reply_links(content):
    """Remove comment reply links from the HTML"""

    # Remove comment reply links: <a ... class="comment-reply-link" ...>Reply ...</a>
    # Handle both single and multi-line patterns
    content = re.sub(
        r'<a[^>]*class="comment-reply-link"[^>]*>Reply\s*<span[^>]*>[^<]*</span></a>\s*',
        '',
        content
    )

    # Clean up leftover </div><!-- .reply --> wrappers that are now empty
    content = re.sub(r'\s*</div><!-- \.reply -->', '', content)

    return content

# Process all HTML files
fixed_count = 0
total_removed = 0

for root, dirs, files in os.walk('/Users/adam/dev/web/hostgator3'):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)

            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            original_content = content

            # Count reply links before removal
            reply_links = len(re.findall(r'class="comment-reply-link"', content))

            content = remove_reply_links(content)

            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_count += 1
                total_removed += reply_links
                if reply_links > 0:
                    print(f"✓ Cleaned: {filepath} (removed {reply_links} reply links)")

print(f"\nDone! Cleaned {fixed_count} files and removed {total_removed} reply links.")
