#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json
import re
import sys

def get_transcript(video_id):
    """Fetch transcript from YouTube video"""
    # YouTube's transcript API endpoint
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    # Try to get the page source which contains caption data
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            
        # Look for caption tracks in the HTML
        caption_pattern = r'"captionTracks":\[(.*?)\]'
        match = re.search(caption_pattern, html)
        
        if match:
            caption_data = match.group(1)
            # Extract baseUrl
            base_url_pattern = r'"baseUrl":"([^"]+)"'
            url_match = re.search(base_url_pattern, caption_data)
            if url_match:
                transcript_url = url_match.group(1).replace('\\u0026', '&')
                # Fetch transcript
                transcript_req = urllib.request.Request(transcript_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(transcript_req, timeout=15) as tr_response:
                    transcript_xml = tr_response.read().decode('utf-8')
                    
                # Parse XML to extract text
                text_pattern = r'<text[^>]*>([^<]+)</text>'
                texts = re.findall(text_pattern, transcript_xml)
                return '\n'.join(texts)
        return None
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_id = sys.argv[1]
    else:
        video_id = "_uXnyhrqmsU"  # Default Jeff Su video
    
    transcript = get_transcript(video_id)
    if transcript:
        print(transcript[:5000])  # Limit output
    else:
        print("No transcript found or error occurred")
