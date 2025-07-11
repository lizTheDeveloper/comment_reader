#!/usr/bin/env python3
"""
TikTok Comment Parser
Parses TikTok comments from a markdown file and splits them into individual comment files.
"""

import re
import os
import hashlib
from typing import List, Dict
from pathlib import Path

class TikTokCommentParser:
    def __init__(self, output_dir: str = "comments/tiktok"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_username(self, text: str) -> str:
        """Extract username from markdown link line."""
        username_pattern = r'\[([^\]]+)\]\(https://www.tiktok.com/@[^)]+\)'
        match = re.match(username_pattern, text.strip())
        if match:
            return match.group(1).strip()
        return ""

    def parse_comment_block(self, lines: List[str]) -> Dict:
        """Parse a single comment block and extract relevant information."""
        if not lines:
            return None
        comment_data = {
            'username': '',
            'content': '',
            'timestamp': '',
            'likes': '',
            'raw_text': '\n'.join(lines)
        }
        # Username is usually the first [username](url) line
        for line in lines:
            if line.strip().startswith('[') and '](' in line and 'tiktok.com/@' in line:
                comment_data['username'] = self.extract_username(line)
                break
        # Timestamp and likes are usually near the end
        for line in reversed(lines):
            if re.match(r'^[0-9]+[hdm] agoReply$', line.strip()) or re.match(r'^[0-9]+d agoReply$', line.strip()):
                comment_data['timestamp'] = line.strip()
            elif line.strip().isdigit():
                comment_data['likes'] = line.strip()
            if comment_data['timestamp'] and comment_data['likes']:
                break
        # Content is between username and timestamp/likes
        content_lines = []
        in_content = False
        for line in lines:
            if in_content:
                # Stop at timestamp or likes
                if re.match(r'^[0-9]+[hdm] agoReply$', line.strip()) or line.strip().isdigit():
                    break
                content_lines.append(line.strip())
            elif line.strip().startswith('[') and '](' in line and 'tiktok.com/@' in line:
                in_content = True
        comment_data['content'] = '\n'.join([l for l in content_lines if l])
        return comment_data

    def split_into_comment_blocks(self, text: str) -> List[List[str]]:
        """Split the text into individual comment blocks."""
        lines = text.split('\n')
        comment_blocks = []
        current_block = []
        for line in lines:
            # Start of a new comment: [username](url)
            if line.strip().startswith('[') and '](' in line and 'tiktok.com/@' in line:
                if current_block:
                    comment_blocks.append(current_block)
                current_block = [line]
            else:
                if current_block:
                    current_block.append(line)
        if current_block:
            comment_blocks.append(current_block)
        return comment_blocks

    def sanitize_filename(self, username: str, content_preview: str) -> str:
        """Create a safe filename from username and content preview."""
        clean_username = re.sub(r'[^\w\-_.]', '', username)[:20]
        clean_content = re.sub(r'[^\w\s]', '', content_preview)
        words = clean_content.split()[:5]
        content_preview = '_'.join(words)[:30]
        if clean_username:
            filename = f"{clean_username}_{content_preview}"
        else:
            filename = f"unknown_user_{content_preview}"
        hash_obj = hashlib.md5(f"{username}_{content_preview}".encode())
        filename += f"_{hash_obj.hexdigest()[:8]}"
        return f"{filename}.txt"

    def format_comment_content(self, comment: Dict) -> str:
        """Format a comment for saving to file."""
        content = f"Username: {comment['username']}\n"
        content += f"Timestamp: {comment['timestamp']}\n"
        content += f"Likes: {comment['likes']}\n"
        content += f"Content:\n{comment['content']}\n"
        content += f"\nRaw Text:\n{comment['raw_text']}\n"
        return content

    def parse_file(self, input_file: str) -> None:
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            print(f"Error: File {input_file} not found")
            return
        except Exception as e:
            print(f"Error reading file: {e}")
            return
        print(f"Parsing file: {input_file}")
        comment_blocks = self.split_into_comment_blocks(text)
        print(f"Found {len(comment_blocks)} comment blocks")
        saved_count = 0
        for block in comment_blocks:
            comment_data = self.parse_comment_block(block)
            if comment_data and comment_data['username']:
                content_preview = comment_data['content'][:50] if comment_data['content'] else "no_content"
                filename = self.sanitize_filename(comment_data['username'], content_preview)
                filepath = self.output_dir / filename
                try:
                    comment_content = self.format_comment_content(comment_data)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(comment_content)
                    saved_count += 1
                    print(f"Saved comment: {filename}")
                except Exception as e:
                    print(f"Error saving comment {filename}: {e}")
        print(f"\nCompleted! Saved {saved_count} comment files to {self.output_dir}")

def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python parse_into_comments_tiktok.py <input_file>")
        print("Example: python parse_into_comments_tiktok.py 'why don't you like AI - Tiktok.md'")
        return
    input_file = sys.argv[1]
    parser = TikTokCommentParser()
    parser.parse_file(input_file)

if __name__ == "__main__":
    main() 