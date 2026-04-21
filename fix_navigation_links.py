#!/usr/bin/env python3
import os
import re
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

# Build a chronological list of all blog posts
posts = []
for root, dirs, files in os.walk('/Users/adam/dev/web/hostgator3/2012'):
    if 'index.html' in files:
        # Extract date from path
        parts = root.split('/')
        if len(parts) >= 3:
            try:
                year = int(parts[-3])
                month = int(parts[-2])
                day = int(parts[-1])
                date = datetime(year, month, day)
                posts.append({
                    'date': date,
                    'path': root,
                    'rel_path': root.replace('/Users/adam/dev/web/hostgator3/', '')
                })
            except (ValueError, IndexError):
                pass

# Sort posts chronologically
posts.sort(key=lambda x: x['date'])

print(f"Found {len(posts)} blog posts")

# Fix navigation links
fixed_count = 0
for i, post in enumerate(posts):
    html_file = os.path.join(post['path'], 'index.html')

    with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    original_content = content

    # Find the navigation nav-single element
    # Previous post
    if i > 0:
        prev_post = posts[i - 1]
        prev_rel = prev_post['rel_path'].replace(post['rel_path'].rsplit('/', 1)[0] + '/', '')

        # Calculate relative path from current to previous
        current_depth = post['path'].count('/')
        prev_depth = prev_post['path'].count('/')
        depth_diff = current_depth - prev_depth

        # Build relative path
        if depth_diff > 0:
            rel_prefix = '../' * depth_diff
        else:
            rel_prefix = ''

        prev_href = rel_prefix + prev_post['rel_path'].split('/')[-1] + '/index.html'
        # Normalize to use ../../../ pattern consistently
        prev_href = '/' + prev_post['rel_path'] + '/index.html'

        # Replace empty href in nav-previous with correct link
        content = re.sub(
            r'(<span class="nav-previous"><a href=")("")([^>]*>.*?</a></span>)',
            r'\1' + prev_href + r'\3',
            content,
            flags=re.DOTALL
        )

    # Next post
    if i < len(posts) - 1:
        next_post = posts[i + 1]
        next_href = '/' + next_post['rel_path'] + '/index.html'

        # Replace empty href in nav-next with correct link
        content = re.sub(
            r'(<span class="nav-next"><a href=")("")([^>]*>.*?</a></span>)',
            r'\1' + next_href + r'\3',
            content,
            flags=re.DOTALL
        )

    if content != original_content:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        fixed_count += 1
        print(f"✓ Fixed: {html_file}")

print(f"\nDone! Fixed navigation in {fixed_count} files.")
