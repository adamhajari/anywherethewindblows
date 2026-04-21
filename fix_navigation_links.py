#!/usr/bin/env python3
import os
import re
from datetime import datetime

# Build a chronological list of all blog posts
posts = []
base_dir = '/Users/adam/dev/web/hostgator3'
for root, dirs, files in os.walk(os.path.join(base_dir, '2012')):
    if 'index.html' in files:
        # Extract date from path structure: /2012/MM/DD/slug/
        parts = root.split('/')
        # parts = [..., '2012', 'MM', 'DD', 'slug']
        if len(parts) >= 4:
            try:
                year = int(parts[-4])
                month = int(parts[-3])
                day = int(parts[-2])
                date = datetime(year, month, day)
                rel_path = root.replace(base_dir + '/', '')
                posts.append({
                    'date': date,
                    'path': root,
                    'rel_path': rel_path
                })
            except (ValueError, IndexError) as e:
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

    # Previous post
    if i > 0:
        prev_post = posts[i - 1]
        prev_href = '/' + prev_post['rel_path'] + '/index.html'
        # Replace empty href in nav-previous with correct link
        content = re.sub(
            r'(<span class="nav-previous"><a href=")("")',
            r'\1' + prev_href + r'"',
            content,
            count=1
        )

    # Next post
    if i < len(posts) - 1:
        next_post = posts[i + 1]
        next_href = '/' + next_post['rel_path'] + '/index.html'
        # Replace empty href in nav-next with correct link
        content = re.sub(
            r'(<span class="nav-next"><a href=")("")',
            r'\1' + next_href + r'"',
            content,
            count=1
        )

    if content != original_content:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        fixed_count += 1
        print(f"✓ Fixed: {html_file}")

print(f"\nDone! Fixed navigation in {fixed_count} files.")
