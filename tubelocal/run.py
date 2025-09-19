#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import json
import yt_dlp
import logging
import requests
from datetime import datetime, timedelta

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('audio_downloader_no_api.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

DOWNLOAD_DIR = '/storage/emulated/0/_MEDIA/_TUBELOCAL/'
BBOOKS_DIR = os.path.join(DOWNLOAD_DIR, 'bbooks/')
VIDEO_LIST_FILE = 'downloaded_videos_no_api.json'

# Firebase configuration
FIREBASE_WEBAPP_URL = 'https://admin-t4.web.app'
FIREBASE_API_URL = 'https://firestore.googleapis.com/v1/projects/admin-t4/databases/(default)/documents'
SCRIPT_TUBELOCAL_COLLECTION = 'script-tubelocal'

CHANNELS = {
    'Sean Le': {
        'url': 'https://www.youtube.com/@SeanLe714/streams',
        'handle': 'SeanLe714',
        'download': 'audio',
        'channel_title': 'SLe'
    },
    'RFA Vietnamese': {
        'url': 'https://m.youtube.com/@rfavietnamese/videos',
        'handle': 'rfavietnamese',
        'download': 'audio, video',
        'channel_title': 'RFA'

    },
    'BBC Tieng Viet': {
        'url': 'https://www.youtube.com/@bbctiengviet/videos',
        'handle': 'bbctiengviet',
        'download': 'audio, video',
        'channel_title': 'BBC'
    },
    'Maybe Podcast': {
        'url': 'https://m.youtube.com/@MaybePodcastVN/videos',
        'handle': 'MaybePodcastVN',
        'download': 'audio',
        'channel_title': 'Maybe'
    },
'The SaiGonPost': {
        'url': 'https://m.youtube.com/@SGP_channel/videos',
        'handle': 'SGP_channel',
        'download': 'audio, video',
        'channel_title': 'SGP'
        
        
    },
    'Tài Chính & Kinh Doanh': {
        'url': 'https://m.youtube.com/@TaichinhKinhdoanhTV/videos',
        'handle': 'TaichinhKinhdoanhTV',
        'download': 'audio, video',
        'channel_title': 'TCKD'
    },
    'ThoiBao.De': {
        'url': 'https://m.youtube.com/@thoibao-de/videos',
        'handle': 'TaichinhKinhdoanhTV',
        'download': 'audio, video',
        'channel_title': 'TB.De'
    },
    'BBooks': {
        'url': 'https://www.youtube.com/@bbooks-channel/videos',
        'handle': 'bbooks-channel',
        'download': 'audio'
    }
}

# Tạo thư mục download nếu chưa tồn tại
for folder in [DOWNLOAD_DIR, BBOOKS_DIR, os.path.join(DOWNLOAD_DIR, 'videos')]:
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
            logging.info(f"✅ Created download directory: {folder}")
        except Exception as e:
            logging.error(f"❌ Cannot create download directory: {e}")

def test_firebase_connection():
    """Test kết nối Firebase trước khi chạy"""
    try:
        logging.info("🔍 Testing Firebase connection...")
        url = f"{FIREBASE_API_URL}/{SCRIPT_TUBELOCAL_COLLECTION}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            logging.info("✅ Firebase connection successful!")
            return True
        else:
            logging.warning(f"⚠️ Firebase connection failed: {response.status_code}")
            return False
    except Exception as e:
        logging.warning(f"⚠️ Firebase connection error: {e}")
        return False

def get_channels_from_firebase():
    """Lấy dữ liệu channels từ Firebase Firestore"""
    try:
        logging.info("🔄 Đang lấy dữ liệu channels từ Firebase...")
        
        # URL để lấy tất cả documents trong collection script-tubelocal
        url = f"{FIREBASE_API_URL}/{SCRIPT_TUBELOCAL_COLLECTION}"
        
        # Gửi request GET
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            channels = {}
            
            # Parse dữ liệu từ Firestore format
            if 'documents' in data:
                for doc in data['documents']:
                    doc_id = doc['name'].split('/')[-1]
                    fields = doc.get('fields', {})
                    
                    # Extract fields từ Firestore format
                    channel_title = fields.get('channelTitle', {}).get('stringValue', '')
                    url = fields.get('url', {}).get('stringValue', '')
                    handle = fields.get('handle', {}).get('stringValue', '')
                    download_type = fields.get('download', {}).get('stringValue', 'audio')
                    
                    if channel_title and url:
                        channels[channel_title] = {
                            'url': url,
                            'handle': handle,
                            'download': download_type,
                            'channel_title': channel_title,
                            'id': doc_id
                        }
            
            logging.info(f"✅ Đã lấy {len(channels)} channels từ Firebase")
            return channels
            
        else:
            logging.error(f"❌ Lỗi khi lấy dữ liệu từ Firebase: {response.status_code}")
            logging.error(f"Response: {response.text}")
            return {}
            
    except Exception as e:
        logging.error(f"❌ Lỗi khi kết nối Firebase: {e}")
        return {}

def safe_filename(s):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        s = s.replace(char, '_')
    if len(s) > 100:
        s = s[:100]
    return s.strip()

def load_downloaded_videos():
    if os.path.exists(VIDEO_LIST_FILE):
        try:
            with open(VIDEO_LIST_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except Exception as e:
            logging.error(f"❌ Error loading downloaded videos: {e}")
            return []
    return []

def save_downloaded_video(video_id, video_title, video_url):
    try:
        downloaded_videos = load_downloaded_videos()
        ids = [v.get('video_id', v) if isinstance(v, dict) else v for v in downloaded_videos]
        if video_id not in ids:
            downloaded_videos.append({
                'video_id': video_id,
                'title': video_title,
                'url': video_url,
                'downloaded_at': datetime.now().isoformat()
            })
            with open(VIDEO_LIST_FILE, 'w', encoding='utf-8') as f:
                json.dump(downloaded_videos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"❌ Error saving video to cache: {e}")

def remove_old_files(days=2):
    try:
        now = datetime.now()
        current_date = now.strftime("%y%m%d")
        
        # Tính ngày giới hạn (ngày hiện tại trừ đi số ngày)
        limit_date = (now - timedelta(days=days)).strftime("%y%m%d")
        
        logging.info(f"🗑️ Cleaning old files older than {days} days")
        logging.info(f"📅 Current date: {current_date}, Limit date: {limit_date}")
        logging.info(f"🛡️ Bảo vệ thư mục bbooks - không xóa file nào từ đây")
        
        deleted_count = 0
        
        # 1. Xóa file cũ từ thư mục chính (audio)
        for filename in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, filename)
            
            # Bỏ qua hoàn toàn thư mục bbooks và tất cả nội dung bên trong
            if filename == 'bbooks' or filename.startswith('bbooks'):
                logging.info(f"🛡️ Bỏ qua thư mục bbooks: {filename}")
                continue
                
            # Xử lý file .mp3
            if filename.endswith('.mp3') and os.path.isfile(file_path):
                if len(filename) >= 10 and filename[:6].isdigit():
                    try:
                        file_date = filename[:6]
                        if file_date < limit_date:
                            os.remove(file_path)
                            deleted_count += 1
                            logging.info(f"��️ Deleted old audio: {filename} (date: {file_date})")
                    except Exception as e:
                        logging.warning(f"⚠️ Could not parse date from filename: {filename}, error: {e}")
                        continue
        
        # 2. Xóa file cũ từ thư mục videos (nếu tồn tại)
        videos_dir = os.path.join(DOWNLOAD_DIR, 'videos')
        if os.path.exists(videos_dir):
            logging.info(f"📁 Kiểm tra thư mục videos: {videos_dir}")
            for filename in os.listdir(videos_dir):
                file_path = os.path.join(videos_dir, filename)
                
                # Bỏ qua thư mục bbooks trong videos
                if filename == 'bbooks' or filename.startswith('bbooks'):
                    logging.info(f"🛡️ Bỏ qua thư mục bbooks trong videos: {filename}")
                    continue
                    
                # Xử lý file .mp4
                if filename.endswith('.mp4') and os.path.isfile(file_path):
                    if len(filename) >= 10 and filename[:6].isdigit():
                        try:
                            file_date = filename[:6]
                            if file_date < limit_date:
                                os.remove(file_path)
                                deleted_count += 1
                                logging.info(f"��️ Deleted old video: {filename} (date: {file_date})")
                        except Exception as e:
                            logging.warning(f"⚠️ Could not parse date from filename: {filename}, error: {e}")
                            continue
                            
        logging.info(f"✅ Cleanup completed. Deleted {deleted_count} old files.")
        logging.info(f"🛡️ Thư mục bbooks được bảo vệ hoàn toàn")
        
    except Exception as e:
        logging.error(f"❌ Error cleaning old files: {e}")

def download_audio(video_url, video_id, video_title, channel_name, upload_date=None):
    try:
        # Định dạng tên file theo format: YYMMDDHHmm - channel_title - tiêu đề video
        if channel_name == 'BBooks':
            target_dir = BBOOKS_DIR
            filename = safe_filename(video_title)
        else:
            target_dir = DOWNLOAD_DIR
            # Lấy channel_title từ CHANNELS dict
            channel_title = CHANNELS[channel_name].get('channel_title', channel_name)
            time_part = datetime.now().strftime("%y%m%d%H%M")
            filename = f"{time_part} - {channel_title} - {safe_filename(video_title)}"
        output_template = os.path.join(target_dir, f'{filename}.%(ext)s')

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'quiet': False,
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'writethumbnail': False,
            'ignoreerrors': False,
        }

        logging.info(f"🎵 Downloading audio: {video_title}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            logging.info(f"✅ Downloaded audio successfully: {video_title}")
            save_downloaded_video(video_id, video_title, video_url)
            
           
            return True
    except Exception as e:
        logging.error(f"❌ Error downloading audio {video_url}: {e}")
        return False

def download_video(video_url, video_id, video_title, channel_name, upload_date=None):
    try:
        # Định dạng tên file theo format: YYMMDDHHmm - channel_title - tiêu đề video
        if channel_name == 'BBooks':
            target_dir = os.path.join(DOWNLOAD_DIR, 'videos', 'bbooks')
            filename = safe_filename(video_title)
        else:
            target_dir = os.path.join(DOWNLOAD_DIR, 'videos')
            # Lấy channel_title từ CHANNELS dict
            channel_title = CHANNELS[channel_name].get('channel_title', channel_name)
            time_part = datetime.now().strftime("%y%m%d%H%M")
            filename = f"{time_part} - {channel_title} - {safe_filename(video_title)}"
        
        # Tạo thư mục con nếu cần
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        output_template = os.path.join(target_dir, f'{filename}.%(ext)s')

        ydl_opts = {
            'format': 'best[height<=1080][ext=mp4]/best[height<=1080]/best[ext=mp4]/best',
            'outtmpl': output_template,
            'quiet': False,
            'noplaylist': True,
            'writethumbnail': False,
            'ignoreerrors': False,
        }

        logging.info(f"🎬 Downloading video: {video_title}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            logging.info(f"✅ Downloaded video successfully: {video_title}")
            return True
    except Exception as e:
        logging.error(f"❌ Error downloading video {video_url}: {e}")
        return False

def get_videos_via_ytdlp(channel_name, channel_info, limit=3):
    """
    Lấy tối đa {limit} video mới nhất từ channel hoặc playlist bằng yt-dlp.
    Bổ sung thông tin 'is_live' để kiểm tra.
    """
    try:
        channel_url = channel_info['url']
        logging.info(f"🔍 Fetching up to {limit} latest videos from {channel_name} using yt-dlp...")

        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'playlist_items': f'1-{limit}',
            'ignoreerrors': True,
        }

        videos = []
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(channel_url, download=False)
                if 'entries' in info and info['entries']:
                    for entry in info['entries']:
                        if len(videos) >= limit:
                            break
                        if entry and 'id' in entry and 'title' in entry:
                            video_id = entry['id']
                            # Cần lấy thông tin chi tiết để kiểm tra 'is_live'
                            full_info_opts = {'quiet': True, 'ignoreerrors': True}
                            with yt_dlp.YoutubeDL(full_info_opts) as ydl_full:
                                try:
                                    full_info = ydl_full.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                                    if full_info:
                                        videos.append({
                                            'id': video_id,
                                            'title': full_info.get('title', entry['title']),
                                            'url': full_info.get('webpage_url', f"https://www.youtube.com/watch?v={video_id}"),
                                            'upload_date': full_info.get('upload_date'),
                                            'channel': channel_name,
                                            'is_live': full_info.get('is_live', False)
                                        })
                                except Exception as e:
                                    logging.error(f"❌ Error getting full info for video {video_id}: {e}")
                                    videos.append({
                                        'id': video_id,
                                        'title': entry['title'],
                                        'url': f"https://www.youtube.com/watch?v={video_id}",
                                        'upload_date': entry.get('upload_date'),
                                        'channel': channel_name,
                                        'is_live': False
                                    })
                logging.info(f"📺 Found {len(videos)} videos from {channel_name}")
                return videos
            except Exception as e:
                logging.error(f"❌ Error extracting channel info: {e}")
                return []
    except Exception as e:
        logging.error(f"❌ Error fetching videos from {channel_name}: {e}")
        return []

def get_videos_via_ytdlp_alternative(channel_name, channel_info, limit=3):
    return get_videos_via_ytdlp(channel_name, channel_info, limit=limit)

def check_new_videos():
    try:
        logging.info("🔍 Checking for new videos...")

        # Lấy dữ liệu channels từ Firebase
        firebase_channels = get_channels_from_firebase()
        
        # Sử dụng dữ liệu từ Firebase nếu có, nếu không thì dùng dữ liệu local
        channels_to_use = firebase_channels if firebase_channels else CHANNELS
        
        if firebase_channels:
            logging.info(f"✅ Sử dụng {len(firebase_channels)} channels từ Firebase")
            logging.info("📋 Danh sách channels từ Firebase:")
            for name, info in firebase_channels.items():
                logging.info(f"  - {name}: {info['url']} ({info['download']})")
        else:
            logging.info(f"⚠️ Sử dụng {len(CHANNELS)} channels từ cấu hình local")
            logging.info("📋 Danh sách channels từ cấu hình local:")
            for name, info in CHANNELS.items():
                logging.info(f"  - {name}: {info['url']} ({info['download']})")

        downloaded_videos = load_downloaded_videos()
        downloaded_ids = [v.get('video_id', v) if isinstance(v, dict) else v for v in downloaded_videos]

        for channel_name, channel_info in channels_to_use.items():
            logging.info(f"\n{'='*50}")
            logging.info(f"📺 Checking channel: {channel_name}")
            logging.info(f"{'='*50}")

            videos = get_videos_via_ytdlp(channel_name, channel_info, limit=3)
            if not videos:
                logging.info(f"⚠️ No videos found with main method, trying alternative...")
                videos = get_videos_via_ytdlp_alternative(channel_name, channel_info, limit=3)

            for video in videos:
                video_id = video['id']
                video_title = video['title']
                video_url = video['url']
                upload_date = video.get('upload_date')
                is_live = video.get('is_live', False)

                if is_live:
                    logging.info(f"⏩ Bỏ qua video đang phát trực tiếp: {video_title}")
                    continue

                if video_id not in downloaded_ids:
                    logging.info(f"🆕 New video found: {video_title}")
                    
                    # Kiểm tra loại download cần thiết
                    download_types = channel_info.get('download', 'audio').split(', ')
                    
                    success = True
                    if 'audio' in download_types:
                        if not download_audio(video_url, video_id, video_title, channel_name, upload_date):
                            success = False
                    
                    if 'video' in download_types:
                        if not download_video(video_url, video_id, video_title, channel_name, upload_date):
                            success = False
                    
                    if success:
                        downloaded_ids.append(video_id)
                        time.sleep(2)
                else:
                    logging.info(f"⏭️ Already downloaded: {video_title}")

    except Exception as e:
        logging.error(f"❌ Error checking new videos: {e}")

def monitor_new_videos():
    logging.info("🎵 Audio YouTube Downloader (No API) Started")
    logging.info(f"📁 Download directory: {DOWNLOAD_DIR}")
    logging.info(f"⏰ Check interval: 30 phút")
    
    # Test Firebase connection on startup
    firebase_available = test_firebase_connection()
    if firebase_available:
        logging.info("🌐 Firebase integration enabled - channels will be loaded from webapp")
    else:
        logging.info("📱 Using local channel configuration")

    while True:
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logging.info(f"\n{'='*60}")
            logging.info(f"🕐 Checking for new videos at {current_time}")
            logging.info(f"{'='*60}")

            remove_old_files(2)
            check_new_videos()

            logging.info("💤 Sleeping 30 phút before next check...")
            time.sleep(1800)
        except KeyboardInterrupt:
            logging.info("⏹️ Stopped by user")
            break
        except Exception as e:
            logging.error(f"❌ Unexpected error: {e}")
            logging.info("💤 Sleeping 10 minutes before retry...")
            time.sleep(600)

if __name__ == "__main__":
    monitor_new_videos()