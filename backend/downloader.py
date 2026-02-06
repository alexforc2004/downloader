import yt_dlp
import os
import tempfile
import uuid
from typing import Dict, Any, Optional
# FFmpeg configuration
# On server (Linux), ffmpeg is usually in the PATH. On Windows, we use the local path.
ENV_FFMPEG_DIR = os.getenv("FFMPEG_DIR")
if ENV_FFMPEG_DIR:
    FFMPEG_DIR = ENV_FFMPEG_DIR
else:
    # Local Windows path (Fallback)
    FFMPEG_DIR = r"C:\Users\AZZEDINE\Downloads\ffmpeg-2026-02-04-git-627da11111c-essentials_build\ffmpeg\bin"

# Add FFmpeg to system PATH to ensure yt-dlp finds it for merging
if os.path.exists(FFMPEG_DIR) and FFMPEG_DIR not in os.environ["PATH"]:
    os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ["PATH"]
elif not ENV_FFMPEG_DIR:
    # If not on Windows and no ENV set, assume 'ffmpeg' is in system path (like in Docker)
    FFMPEG_DIR = "" 




class MediaDownloader:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()

    def get_info(self, url: str) -> Dict[str, Any]:
        """Fetch media metadata without downloading."""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best',
            'ffmpeg_location': FFMPEG_DIR,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "duration": info.get("duration"),
                "uploader": info.get("uploader"),
                "ext": info.get("ext"),
                "formats": [
                    {"format_id": f["format_id"], "ext": f["ext"], "resolution": f.get("resolution"), "filesize": f.get("filesize")}
                    for f in info.get("formats", []) if f.get("vcodec") != "none"
                ]
            }

    def download_media(self, url: str, format_type: str = "video", max_filesize_mb: Optional[int] = None) -> Dict[str, str]:
        """Download media and return the local file path and title."""
        task_id = str(uuid.uuid4())
        
        # Get FFmpeg path
        ffmpeg_bin = FFMPEG_DIR

        # We fetch info first to get the sanitized title
        ydl_opts_info = {
            'quiet': True,
            'no_warnings': True,
            'ffmpeg_location': FFMPEG_DIR,
        }
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'media')
            # Sanitize title for filename
            clean_title = "".join([c for c in title if c.isalnum() or c in (' ', '.', '_', '-')]).strip()
            if not clean_title:
                clean_title = "download"

        output_template = os.path.join(self.temp_dir, f"{task_id}.%(ext)s")
        
        ydl_opts = {
            'outtmpl': output_template,
            'quiet': False, # Enabled for debugging
            'no_warnings': False,
            'ffmpeg_location': ffmpeg_bin,
        }

        if format_type == "audio":
            format_str = 'bestaudio/best'
            if max_filesize_mb:
                # Prioritize audio files that fit within the limit
                format_str = f'bestaudio[filesize<{max_filesize_mb}M]/bestaudio/best'
            
            ydl_opts.update({
                'format': format_str,
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    },
                    {'key': 'EmbedThumbnail'},
                    {'key': 'FFmpegMetadata'},
                ],
                'writethumbnail': True,
            })
        else:
            format_str = 'bestvideo+bestaudio'
            if max_filesize_mb:
                # Attempt to find best combination under the limit, fallback to best overall
                # We use 40M as a safer limit for video to account for audio and merging overhead
                format_str = f'bestvideo[filesize<{max_filesize_mb-5}M]+bestaudio/best[filesize<{max_filesize_mb}M]/best'
            
            ydl_opts.update({
                'format': format_str,
                'merge_output_format': 'mp4',
                'postprocessors': [
                    {'key': 'EmbedThumbnail'},
                    {'key': 'FFmpegMetadata'},
                ],
                'writethumbnail': True,
            })


        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                # Check for post-processed filename
                if format_type == "audio":
                    filename = os.path.splitext(filename)[0] + ".mp3"
                elif format_type == "video":
                    if not filename.endswith('.mp4'):
                        potential_mp4 = os.path.splitext(filename)[0] + ".mp4"
                        if os.path.exists(potential_mp4):
                            filename = potential_mp4
                
                if not os.path.exists(filename):
                    raise Exception(f"File not found after download: {filename}")
                    
                return {"path": filename, "title": clean_title}
        except Exception as e:
            print(f"yt-dlp error: {str(e)}")
            raise e

downloader = MediaDownloader()
