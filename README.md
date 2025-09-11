# T4termux

Termux tools and utilities for Android development and automation.

## Contents

- `client.py` - Main client application
- `tubelocal/` - YouTube downloader utilities
  - `tubelocal.py` - YouTube audio/video downloader with channel monitoring
  - `audio_downloader_no_api.log` - Download logs
  - `downloaded_videos_no_api.json` - Downloaded videos cache

## Features

### YouTube Downloader (tubelocal.py)
- Downloads audio and video from multiple YouTube channels
- Automatic channel monitoring
- File naming format: `YYMMDDHHmm - channel_title - video_title`
- Supports channels:
  - Sean Le (SLe)
  - RFA Vietnamese (RFA)
  - BBC Tieng Viet (BBC)
  - Maybe Podcast (Maybe)
  - The SaiGonPost (SGP)
  - Tài Chính & Kinh Doanh (TCKD)
  - ThoiBao.De (TB.De)
  - BBooks

## Usage

```bash
# Run YouTube downloader
python3 tubelocal/tubelocal.py

# Run client
python3 client.py
```

## Requirements

- Python 3.x
- yt-dlp
- Termux (Android)

## Installation

```bash
pip install yt-dlp
```

## License

MIT License
