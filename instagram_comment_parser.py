#!/usr/bin/env python3
"""
Instagram Comment Parser
Parses Instagram comments from a text file and splits them into thread-based files.
A thread consists of consecutive comments from the same user.
"""

import re
import os
import hashlib
from typing import List, Dict, Tuple
from pathlib import Path

class InstagramCommentParser:
    def __init__(self, output_dir: str = "/Users/annhoward/src/comment_reader/comments/instagram"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def extract_username(self, text: str) -> str:
        """Extract username from profile picture line or username line."""
        # Pattern for username in markdown link format [username](url)
        username_pattern = r'\[([^\]]+)\](?:\([^)]*\))?'
        matches = re.findall(username_pattern, text)
        if matches:
            # Get the last match which is usually the username
            username = matches[-1]
            # Clean up common patterns
            username = username.replace("'s profile picture", "")
            username = username.replace("@", "")
            return username.strip()
        return ""
    
    def remove_markdown_links(self, text: str) -> str:
        """Remove all markdown-formatted links from the text."""
        # Pattern: [text](url)
        return re.sub(r'\[[^\]]*\]\([^)]*\)', '', text)
    
    def parse_comment_block(self, lines: List[str]) -> Dict:
        """Parse a single comment block and extract relevant information."""
        if not lines:
            return None
            
        comment_data = {
            'username': '',
            'content': '',
            'timestamp': '',
            'likes': '',
            'is_reply': False,
            'raw_text': '\n'.join(lines)
        }
        
        # Check if this is a reply (indented or has "Hide replies" nearby)
        first_line = lines[0] if lines else ""
        comment_data['is_reply'] = (
            first_line.strip().startswith('- [![') or 
            any('Hide replies' in line for line in lines[:5])
        )
        
        # Extract username from profile picture line or username line
        for i, line in enumerate(lines[:3]):  # Check first 3 lines for username
            if '[![' in line and 'profile picture' in line:
                username = self.extract_username(line)
                if username:
                    comment_data['username'] = username
                    break
            elif line.strip().startswith('[') and '](' in line and not 'profile picture' in line:
                username = self.extract_username(line)
                if username:
                    comment_data['username'] = username
                    break
        
        # Extract comment content (skip profile pic and username lines)
        content_lines = []
        skip_next = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip profile picture lines
            if '[![' in line and 'profile picture' in line:
                continue
                
            # Skip username-only lines
            if line.startswith('[') and '](' in line and len(line) < 100:
                continue
                
            # Skip timestamp/engagement lines
            if re.match(r'^\d+[hdm].*Reply$', line) or 'likes' in line.lower():
                comment_data['timestamp'] = line
                continue
                
            # Skip navigation elements
            if line in ['Hide replies', 'Reply']:
                continue
                
            # Remove markdown links from the line
            line = self.remove_markdown_links(line)
            # This is likely content
            content_lines.append(line)
        
        comment_data['content'] = '\n'.join(content_lines)
        return comment_data
    
    def split_into_comment_blocks(self, text: str) -> List[List[str]]:
        """Split the text into individual comment blocks."""
        lines = text.split('\n')
        comment_blocks = []
        current_block = []
        
        for line in lines:
            # Start of a new comment (profile picture line)
            if '[![' in line and 'profile picture' in line:
                if current_block:
                    comment_blocks.append(current_block)
                current_block = [line]
            else:
                if current_block:  # Only add to block if we've started one
                    current_block.append(line)
        
        # Don't forget the last block
        if current_block:
            comment_blocks.append(current_block)
            
        return comment_blocks
    
    def group_into_threads(self, comments: List[Dict]) -> List[List[Dict]]:
        """Group consecutive comments from the same user into threads."""
        if not comments:
            return []
            
        threads = []
        current_thread = [comments[0]]
        
        for comment in comments[1:]:
            # If same username and not a reply, continue the thread
            if (comment['username'] == current_thread[-1]['username'] and 
                not comment['is_reply']):
                current_thread.append(comment)
            else:
                # Start a new thread
                threads.append(current_thread)
                current_thread = [comment]
        
        # Don't forget the last thread
        if current_thread:
            threads.append(current_thread)
            
        return threads
    
    def sanitize_filename(self, username: str, content_preview: str) -> str:
        """Create a safe filename from username and content preview."""
        # Clean username
        clean_username = re.sub(r'[^\w\-_.]', '', username)[:20]
        
        # Create content preview
        clean_content = re.sub(r'[^\w\s]', '', content_preview)
        words = clean_content.split()[:5]  # First 5 words
        content_preview = '_'.join(words)[:30]
        
        # Create filename
        if clean_username:
            filename = f"{clean_username}_{content_preview}"
        else:
            filename = f"unknown_user_{content_preview}"
            
        # Add hash for uniqueness
        hash_obj = hashlib.md5(f"{username}_{content_preview}".encode())
        filename += f"_{hash_obj.hexdigest()[:8]}"
        
        return f"{filename}.txt"
    
    def format_thread_content(self, thread: List[Dict]) -> str:
        """Format a thread for saving to file."""
        if not thread:
            return ""
            
        username = thread[0]['username']
        header = f"=== THREAD: {username} ===\n"
        header += f"Comments: {len(thread)}\n"
        header += "=" * 50 + "\n\n"
        
        content = header
        
        for i, comment in enumerate(thread, 1):
            content += f"--- Comment {i} ---\n"
            content += f"Username: {comment['username']}\n"
            content += f"Is Reply: {comment['is_reply']}\n"
            content += f"Timestamp: {comment['timestamp']}\n"
            content += f"Content:\n{comment['content']}\n"
            content += f"\nRaw Text:\n{comment['raw_text']}\n"
            content += "-" * 30 + "\n\n"
            
        return content
    
    def parse_file(self, input_file: str) -> None:
        """Parse the input file and create thread files."""
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
        
        # Split into comment blocks
        comment_blocks = self.split_into_comment_blocks(text)
        print(f"Found {len(comment_blocks)} comment blocks")
        
        # Parse each block
        comments = []
        for block in comment_blocks:
            comment_data = self.parse_comment_block(block)
            if comment_data and comment_data['username']:
                comments.append(comment_data)
        
        print(f"Successfully parsed {len(comments)} comments")
        
        # Group into threads
        threads = self.group_into_threads(comments)
        print(f"Organized into {len(threads)} threads")
        
        # Save each thread
        saved_count = 0
        for thread in threads:
            if not thread:
                continue
                
            username = thread[0]['username']
            content_preview = thread[0]['content'][:50] if thread[0]['content'] else "no_content"
            
            filename = self.sanitize_filename(username, content_preview)
            filepath = self.output_dir / filename
            
            try:
                thread_content = self.format_thread_content(thread)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(thread_content)
                saved_count += 1
                print(f"Saved thread: {filename}")
            except Exception as e:
                print(f"Error saving thread {filename}: {e}")
        
        print(f"\nCompleted! Saved {saved_count} thread files to {self.output_dir}")


def main():
    """Main function to run the parser."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python instagram_comment_parser.py <input_file>")
        print("Example: python instagram_comment_parser.py paste.txt")
        return
    
    input_file = sys.argv[1]
    parser = InstagramCommentParser()
    parser.parse_file(input_file)


if __name__ == "__main__":
    main()
