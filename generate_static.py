#!/usr/bin/env python3
"""
Convert WordPress site to static HTML for GitHub Pages.
Fetches rendered pages from localhost:8888, post-processes HTML, copies assets.
"""

import re
import os
import sys
import shutil
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime
import requests
from bs4 import BeautifulSoup


class WordPressCrawler:
    def __init__(self, sql_file, base_url="http://localhost:8888", output_dir="."):
        self.sql_file = sql_file
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.timeout = 10

        # Parse SQL to build URL map
        self.posts = {}  # id -> {slug, type, title, date, status}
        self.pages = {}  # id -> {slug, type, title, parent_id}
        self.categories = {}  # id -> {slug, name}
        self.posts_by_date = {}  # year/month -> [post_ids]

        self.parse_sql()

    def parse_sql(self):
        """Parse SQL dump with regex to extract posts/pages."""
        print("📖 Parsing SQL dump...")

        with open(self.sql_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Find all wp_posts INSERT statements (there are multiple)
        insert_pattern = r"INSERT INTO `wp_posts`[^V]*VALUES\s*(.*?);"
        for match in re.finditer(insert_pattern, content, re.DOTALL):
            values_str = match.group(1)

            # Split by row tuples - look for complete (...)  patterns
            rows = re.findall(r'\(([^()]*(?:\([^()]*\)[^()]*)*)\)', values_str)

            for row in rows:
                try:
                    # Split carefully, respecting quoted strings
                    parts = []
                    current = ""
                    in_quotes = False
                    i = 0
                    while i < len(row):
                        if row[i] == "'" and (i == 0 or row[i-1] != '\\'):
                            in_quotes = not in_quotes
                        elif row[i] == ',' and not in_quotes:
                            parts.append(current.strip())
                            current = ""
                            i += 1
                            continue
                        current += row[i]
                        i += 1
                    parts.append(current.strip())

                    # Expected columns: ID, post_author, post_date, post_date_gmt, post_content, post_title,
                    # post_excerpt, post_status, comment_status, ping_status, post_password, post_name,
                    # to_ping, pinged, post_modified, post_modified_gmt, post_content_filtered, post_parent,
                    # guid, menu_order, post_type, post_mime_type, comment_count
                    if len(parts) < 21:
                        continue

                    post_id = int(parts[0].strip("'\""))
                    post_date = parts[2].strip("'\"")
                    post_title = parts[5].strip("'\"")
                    post_status = parts[7].strip("'\"")
                    post_name = parts[11].strip("'\"")
                    post_parent = int(parts[17].strip("'\"") or 0)
                    post_type = parts[20].strip("'\"")

                    if post_status != 'publish' or post_type not in ['post', 'page']:
                        continue

                    if post_type == 'page':
                        self.pages[post_id] = {
                            'slug': post_name,
                            'type': 'page',
                            'title': post_title,
                            'parent_id': post_parent,
                            'url': f"?page_id={post_id}"
                        }
                    elif post_type == 'post':
                        year_month = post_date.split()[0].replace('-', '/')
                        self.posts[post_id] = {
                            'slug': post_name,
                            'type': 'post',
                            'title': post_title,
                            'date': year_month,
                            'url': f"?p={post_id}"
                        }
                        if year_month not in self.posts_by_date:
                            self.posts_by_date[year_month] = []
                        self.posts_by_date[year_month].append(post_id)

                except (ValueError, IndexError) as e:
                    continue

        print(f"  ✓ Found {len(self.posts)} posts, {len(self.pages)} pages")

    def build_output_path(self, page_id, page_type):
        """Convert page ID to static file path."""
        if page_type == 'page':
            page_info = self.pages.get(page_id)
            if not page_info:
                return None

            # Handle parent pages
            parent_id = page_info.get('parent_id', 0)
            slug = page_info['slug']

            if parent_id:
                parent_info = self.pages.get(parent_id)
                if parent_info:
                    parent_slug = parent_info['slug']
                    return f"{parent_slug}/{slug}/index.html"

            return f"{slug}/index.html"

        elif page_type == 'post':
            post_info = self.posts.get(page_id)
            if not post_info:
                return None

            date_path = post_info['date'].replace('/', '/')
            slug = post_info['slug']
            return f"{date_path}/{slug}/index.html"

        return None

    def fetch_page(self, url):
        """Fetch HTML from WordPress site."""
        try:
            full_url = urljoin(self.base_url, url)
            print(f"  ⬇️  {url}")
            response = self.session.get(full_url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"  ❌ Error fetching {url}: {e}")
            return None

    def clean_html(self, html, original_url, depth=0):
        """Remove dynamic elements and fix links."""
        soup = BeautifulSoup(html, 'lxml')

        # Remove admin bar, search form, comment form
        for selector in ['#wpadminbar', '#searchform', '.comment-form', '#respond',
                        'script[src*="emoji"]', 'link[rel="EditURI"]', 'link[rel="wlwmanifest"]',
                        'link[rel="wp-json"]', 'link[rel="alternate"]',
                        '.widget_meta', '.widget_recent_entries']:  # Remove meta/login widgets
            for elem in soup.select(selector):
                elem.decompose()

        # Remove WordPress REST API and other scripts
        for script in soup.find_all('script'):
            script_str = str(script)
            if any(x in script_str for x in ['wp-api', 'emoji', 's.w.org', 'wp-emoji']):
                script.decompose()

        # Calculate relative path depth based on output path
        # e.g., index.html = 0, about-us/index.html = 1, 2012/05/post/index.html = 3
        depth = original_url.count('/') + 1

        # Rewrite internal links
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'localhost:8888' in href or href.startswith('/?') or href.startswith('?'):
                new_path = self.rewrite_link(href)
                if new_path:
                    # Make path relative
                    a['href'] = self.make_relative(new_path, depth)
                else:
                    # For links we can't map (unpublished pages), replace with #
                    if 'localhost:8888' in href:
                        a['href'] = '#'

        # Rewrite img src and srcset
        for img in soup.find_all('img'):
            if 'src' in img.attrs:
                src = img['src']
                if 'localhost:8888' in src:
                    src_clean = src.replace('http://localhost:8888', '')
                    img['src'] = self.make_relative(src_clean, depth)
            if 'srcset' in img.attrs:
                srcset = img['srcset']
                img['srcset'] = self.make_relative(srcset.replace('http://localhost:8888', ''), depth)

        # Rewrite script src
        for script in soup.find_all('script', src=True):
            src = script['src']
            if 'localhost:8888' in src:
                src_clean = src.replace('http://localhost:8888', '')
                script['src'] = self.make_relative(src_clean, depth)

        # Rewrite stylesheet links
        for link in soup.find_all('link', href=True):
            href = link['href']
            if 'localhost:8888' in href:
                href_clean = href.replace('http://localhost:8888', '')
                link['href'] = self.make_relative(href_clean, depth)

        return str(soup)

    def make_relative(self, path, depth):
        """Convert absolute path to relative based on page depth."""
        if not path.startswith('/'):
            return path

        # Go up 'depth' directories, then add the path
        if depth <= 1:
            # Top level or one level deep
            return path

        relative = '../' * (depth - 1) + path.lstrip('/')
        return relative

    def rewrite_link(self, href):
        """Convert WordPress URL to static path."""
        if 'localhost' in href:
            href = href.split('localhost:8888')[-1]

        # Remove fragment
        if '#' in href:
            href = href.split('#')[0]

        if href.startswith('/?'):
            # Parse query string
            try:
                params = parse_qs(href[2:])

                if 'p' in params:
                    post_id = int(params['p'][0])
                    return self.build_output_path(post_id, 'post')

                elif 'page_id' in params:
                    page_id = int(params['page_id'][0])
                    return self.build_output_path(page_id, 'page')

                elif 'cat' in params:
                    cat_id = int(params['cat'][0])
                    cat_slug = self.categories.get(cat_id, {}).get('slug', f'cat-{cat_id}')
                    return f"/category/{cat_slug}/"

                elif 'paged' in params:
                    return f"/page/{params['paged'][0]}/"
            except (ValueError, KeyError):
                return None

        # Return as-is if already looks like static path
        return href if href.startswith('/') else None

    def save_page(self, html, output_path):
        """Save HTML to file with directory creation."""
        full_path = self.output_dir / output_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return full_path

    def copy_assets(self):
        """Copy theme and upload directories."""
        print("\n📁 Copying assets...")

        source_theme = Path('wp-content/themes/twentyeleven')
        dest_theme = self.output_dir / 'wp-content/themes/twentyeleven'
        if source_theme.exists():
            shutil.copytree(source_theme, dest_theme, dirs_exist_ok=True)
            print(f"  ✓ Copied theme to {dest_theme}")

        source_uploads = Path('wp-content/uploads')
        dest_uploads = self.output_dir / 'wp-content/uploads'
        if source_uploads.exists():
            shutil.copytree(source_uploads, dest_uploads, dirs_exist_ok=True)
            print(f"  ✓ Copied uploads to {dest_uploads}")

    def run(self):
        """Main crawl routine."""
        print(f"\n🚀 Starting static site generation...")
        print(f"   Base URL: {self.base_url}")
        print(f"   Output: {self.output_dir}")

        self.output_dir.mkdir(exist_ok=True)

        # Fetch homepage
        print("\n📄 Fetching pages...")
        homepage = self.fetch_page('')
        if homepage:
            clean = self.clean_html(homepage, '', depth=0)
            self.save_page(clean, 'index.html')
            print(f"  ✓ Saved index.html")

        # Fetch all pages
        print(f"\n📖 Fetching {len(self.pages)} pages...")
        for page_id in sorted(self.pages.keys()):
            url = self.pages[page_id]['url']
            html = self.fetch_page(url)
            if html:
                output_path = self.build_output_path(page_id, 'page')
                if output_path:
                    depth = output_path.count('/')
                    clean = self.clean_html(html, url, depth=depth)
                    self.save_page(clean, output_path)

        # Fetch all posts
        print(f"\n✍️  Fetching {len(self.posts)} posts...")
        for post_id in sorted(self.posts.keys()):
            url = self.posts[post_id]['url']
            html = self.fetch_page(url)
            if html:
                output_path = self.build_output_path(post_id, 'post')
                if output_path:
                    depth = output_path.count('/')
                    clean = self.clean_html(html, url, depth=depth)
                    self.save_page(clean, output_path)

        # Copy assets
        self.copy_assets()

        # Create .nojekyll for GitHub Pages
        (self.output_dir / '.nojekyll').touch()
        print(f"  ✓ Created .nojekyll")

        print(f"\n✅ Done! Static site ready in {self.output_dir}/")
        print(f"\n📋 To test locally:")
        print(f"   python -m http.server 8080 --directory {self.output_dir}")
        print(f"   Then visit http://localhost:8080/")


if __name__ == '__main__':
    crawler = WordPressCrawler('ahajari_wrdp1.sql')
    crawler.run()
