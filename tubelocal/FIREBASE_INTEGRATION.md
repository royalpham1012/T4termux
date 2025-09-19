# Firebase Integration - YouTube Downloader

## 🚀 Tổng quan

Script `run.py` đã được cập nhật để lấy dữ liệu channels từ Firebase thông qua HTTP request đến webapp T4Admin.

## 🔧 Cấu hình

### Firebase Settings
- **Project:** admin-t4
- **Collection:** script-tubelocal
- **Webapp URL:** https://admin-t4.web.app/_setting_channels_download
- **API URL:** https://firestore.googleapis.com/v1/projects/admin-t4/databases/(default)/documents

### Dependencies
```bash
pip install requests yt-dlp
```

## 📊 Cấu trúc dữ liệu Firebase

### Collection: `script-tubelocal`
```json
{
  "channelTitle": "SLe",
  "url": "https://www.youtube.com/@SeanLe714/streams",
  "handle": "SeanLe714",
  "download": "audio"
}
```

### Fields:
- **channelTitle** (string): Tên channel
- **url** (string): URL YouTube channel
- **handle** (string): YouTube handle
- **download** (string): Loại download (audio, video, audio+video)

## 🔄 Cách hoạt động

### 1. Firebase Integration
```python
def get_channels_from_firebase():
    # Lấy dữ liệu từ Firebase Firestore
    # Parse dữ liệu từ Firestore format
    # Trả về dictionary channels
```

### 2. Fallback Mechanism
- **Ưu tiên:** Dữ liệu từ Firebase
- **Fallback:** Dữ liệu local nếu Firebase không khả dụng

### 3. Logging
- Test kết nối Firebase khi khởi động
- Log danh sách channels được sử dụng
- Hiển thị nguồn dữ liệu (Firebase/Local)

## 🎯 Sử dụng

### Chạy script
```bash
python3 run.py
```

### Log output
```
🎵 Audio YouTube Downloader (No API) Started
🔍 Testing Firebase connection...
✅ Firebase connection successful!
🌐 Firebase integration enabled - channels will be loaded from webapp

🔄 Đang lấy dữ liệu channels từ Firebase...
✅ Đã lấy 3 channels từ Firebase
📋 Danh sách channels từ Firebase:
  - SLe: https://www.youtube.com/@SeanLe714/streams (audio)
  - BBC: https://www.youtube.com/@bbctiengviet/videos (audio, video)
  - RFA: https://m.youtube.com/@rfavietnamese/videos (audio, video)
```

## 🔧 Quản lý Channels

### Thêm channel mới
1. Truy cập: https://admin-t4.web.app/_setting_channels_download
2. Click "Thêm Channel"
3. Điền thông tin:
   - **Channel Title:** Tên hiển thị
   - **URL:** Link YouTube channel
   - **Handle:** YouTube handle
   - **Download Type:** Audio/Video/Audio+Video
4. Click "Thêm Channel"

### Chỉnh sửa channel
1. Tìm channel trong danh sách
2. Click nút "Chỉnh sửa"
3. Cập nhật thông tin
4. Click "Cập Nhật Channel"

### Xóa channel
1. Tìm channel trong danh sách
2. Click nút "Xóa"
3. Xác nhận xóa

## 🛠️ Troubleshooting

### Firebase Connection Failed
```
⚠️ Firebase connection failed: 403
```
**Giải pháp:**
- Kiểm tra kết nối internet
- Verify Firebase project configuration
- Check Firestore rules

### No Channels Retrieved
```
❌ No channels retrieved from Firebase
```
**Giải pháp:**
- Kiểm tra collection `script-tubelocal` có tồn tại
- Verify dữ liệu channels đã được thêm
- Check Firestore permissions

### Fallback to Local
```
⚠️ Sử dụng 4 channels từ cấu hình local
```
**Giải pháp:**
- Script sẽ tự động dùng dữ liệu local
- Không cần can thiệp, script vẫn hoạt động bình thường

## 📈 Monitoring

### Log Files
- `audio_downloader_no_api.log`: Log chi tiết
- Console output: Real-time status

### Key Metrics
- Số lượng channels từ Firebase
- Trạng thái kết nối Firebase
- Số lượng videos đã download
- Lỗi và warnings

## 🔐 Security

### Public Access
- Firebase Firestore API là public read-only
- Không cần authentication cho việc đọc dữ liệu
- Chỉ admin mới có thể thêm/sửa/xóa channels

### Data Privacy
- Không lưu trữ thông tin cá nhân
- Chỉ lưu URL và metadata của YouTube channels
- Logs không chứa thông tin nhạy cảm

---

**🎉 Script đã sẵn sàng sử dụng với Firebase integration!**
