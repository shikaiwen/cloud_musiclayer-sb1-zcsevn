import yt_dlp

def search_videos(keyword, max_results=10):
    ydl_opts = {
        'default_search': 'ytsearch',
        'format': 'bestaudio/best',
        'noplaylist': True,
        'extract_flat': True,
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search_query = f"ytsearch{max_results}:{keyword}"
        result = ydl.extract_info(search_query, download=False)
        
        if 'entries' in result:
            video_urls = [f"https://www.youtube.com/watch?v={entry['id']}" for entry in result['entries']]
            return video_urls
        else:
            return []

# Example usage
keyword = "python tutorial"
videos = search_videos(keyword)

for i, url in enumerate(videos, 1):
    print(f"{i}. {url}")