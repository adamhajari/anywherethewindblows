#!/usr/bin/env python3
"""
Fix WordPress URL references in static HTML files.
Converts localhost URLs and query parameter URLs to proper relative paths.
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

# Build content mapping
content_map = {}

def scan_content():
    """Scan all HTML files and build ID-to-path mapping."""
    for root, dirs, files in os.walk('.'):
        if 'index.html' in files:
            filepath = os.path.join(root, 'index.html')
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Extract ID from various class formats: pageid-XXX, postid-XXX, page-id-XXX, page_id-XXX
            # Also try data-postid attribute
            id_match = re.search(r'(?:(?:page|post)[_-]?id)[_-](\d+)', content)
            if not id_match:
                id_match = re.search(r'data-postid="(\d+)"', content)

            if id_match:
                item_id = id_match.group(1)
                rel_path = filepath.lstrip('./')

                # Extract date
                date_match = re.search(r'datetime="(\d{4}-\d{2}-\d{2})', content)
                date_str = date_match.group(1) if date_match else None

                content_map[item_id] = {
                    'path': rel_path,
                    'date': date_str,
                    'is_post': 'single-post' in content,
                }

def get_prev_next_posts():
    """Get chronologically sorted posts with their prev/next links."""
    posts = [(pid, data) for pid, data in content_map.items() if data['is_post'] and data['date']]
    posts.sort(key=lambda x: x[1]['date'])

    nav_map = {}
    for i, (post_id, data) in enumerate(posts):
        nav_map[post_id] = {
            'path': data['path'],
            'prev': posts[i-1][0] if i > 0 else None,
            'next': posts[i+1][0] if i < len(posts) - 1 else None,
        }
    return posts, nav_map

def fix_url_in_href(href, nav_map):
    """Convert a URL to the correct path."""
    # Extract the target ID from various URL patterns
    target_id = None

    # Pattern 1: localhost URLs (URL encoded and unencoded)
    if 'localhost' in href:
        match = re.search(r'(?:%3F|\\?)(?:p|page_id)(?:%3D|=)(\d+)', href)
        if match:
            target_id = match.group(1)

    # Pattern 2: Query param URLs with various prefixes
    if not target_id:
        match = re.search(r'\?(?:p|page_id)=(\d+)', href)
        if match:
            target_id = match.group(1)

    # If we found a target ID, return the corrected path
    if target_id and target_id in content_map:
        return '/' + content_map[target_id]['path']

    return href

def fix_file(filepath, nav_map):
    """Fix all URLs in a single HTML file."""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    original = content

    # Fix all href attributes that contain query params or localhost
    def replace_href(match):
        href = match.group(1)
        new_href = fix_url_in_href(href, nav_map)
        if new_href != href:
            return f'href="{new_href}"'
        return match.group(0)

    # Match any href that might contain problematic URLs
    # This handles various patterns like:
    # - /path/?page_id=123
    # - /path/?p=123
    # - http://localhost:8002/?page_id=123
    # - URL-encoded localhost
    content = re.sub(
        r'href="([^"]*(?:[\?&](?:p|page_id)=\d+|localhost)[^"]*)"',
        replace_href,
        content
    )

    # Fix post navigation links with chronological ordering
    current_id_match = re.search(r'(?:(?:page|post)[_-]?id)[_-](\d+)', content)
    if not current_id_match:
        current_id_match = re.search(r'data-postid="(\d+)"', content)

    if current_id_match:
        current_id = current_id_match.group(1)
        if current_id in nav_map:
            nav_data = nav_map[current_id]

            # Fix previous link - extract current text and update href
            if nav_data['prev']:
                prev_id = nav_data['prev']
                prev_path = nav_map[prev_id]['path']
                prev_match = re.search(
                    r'<span class="nav-previous"><a[^>]*href="[^"]*"[^>]*>.*?</a></span>',
                    content,
                    re.DOTALL
                )
                if prev_match:
                    prev_section = prev_match.group(0)
                    # Extract any text content (excluding the meta-nav span)
                    text_match = re.search(r'</span>\s*([^<]*)\s*</a>', prev_section)
                    prev_title = text_match.group(1).strip() if text_match else 'Previous'
                    prev_link = f'<span class="nav-previous"><a href="/{prev_path}" rel="prev"><span class="meta-nav">&larr;</span> {prev_title}</a></span>'
                    content = content.replace(prev_section, prev_link, 1)

            # Fix next link - extract current text and update href
            if nav_data['next']:
                next_id = nav_data['next']
                next_path = nav_map[next_id]['path']
                next_match = re.search(
                    r'<span class="nav-next"><a[^>]*href="[^"]*"[^>]*>.*?</a></span>',
                    content,
                    re.DOTALL
                )
                if next_match:
                    next_section = next_match.group(0)
                    # Extract any text content (before the meta-nav span)
                    text_match = re.search(r'<a[^>]*>[^<]*?(<span[^>]*>[^<]*</span>)?\s*([^<]*)', next_section)
                    next_title = text_match.group(2).strip() if text_match and text_match.group(2) else 'Next'
                    next_link = f'<span class="nav-next"><a href="/{next_path}" rel="next">{next_title} <span class="meta-nav">→</span></a></span>'
                    content = content.replace(next_section, next_link, 1)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("Scanning content...")
    scan_content()
    print(f"Found {len(content_map)} content items\n")

    print("Building chronological nav map...")
    posts, nav_map = get_prev_next_posts()
    print(f"Found {len(posts)} posts\n")

    # Scan and fix all HTML files
    print("Fixing URLs in HTML files...")
    fixed_count = 0
    file_count = 0

    for root, dirs, files in os.walk('.'):
        for file in files:
            if file == 'index.html':
                filepath = os.path.join(root, file)
                file_count += 1
                if fix_file(filepath, nav_map):
                    fixed_count += 1
                    print(f"  ✓ {filepath}")

    print(f"\nDone! Fixed {fixed_count}/{file_count} files")

if __name__ == '__main__':
    main()
