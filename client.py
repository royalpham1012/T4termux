#!/usr/bin/env python3
"""
Client04.py - 2507302045 - Quản lý MT5 và Firebase từ xa
Chạy trên Android (Termux) để quản lý thông tin tài khoản và Firebase
"""

import requests
import json
import os
import sys

import time
import threading
from datetime import datetime

# Cấu hình
SERVER_URL = "https://415ac1d425dc.ngrok-free.app"  # Local server URL
TIMEOUT = 10

class ConfigManager:
    def __init__(self, server_url):
        self.server_url = server_url
        self.session = requests.Session()
        self.session.timeout = TIMEOUT

    def test_connection(self):
        """Test kết nối đến server"""
        try:
            response = self.session.get(f"{self.server_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                return data.get('status') == 'healthy'
            return False
        except Exception as e:
            print(f"❌ Lỗi kết nối: {e}")
            return False

    def get_mt5_account_info(self):
        """Lấy thông tin tài khoản MT5"""
        try:
            response = self.session.get(f"{self.server_url}/api/mt5-account-info")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Lỗi HTTP: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return None

    # YouTube Channel Management Methods
    def get_youtube_channels(self):
        """Lấy danh sách YouTube channels"""
        try:
            response = self.session.get(f"{self.server_url}/api/youtube/channels")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Lỗi HTTP: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return None

    def add_youtube_channel(self, channel_data):
        """Thêm YouTube channel mới"""
        try:
            response = self.session.post(f"{self.server_url}/api/youtube/channels", json=channel_data)
            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json()
                return error_data
        except Exception as e:
            return {"error": f"Lỗi kết nối: {e}"}

    def delete_youtube_channel(self, channel_id):
        """Xóa YouTube channel"""
        try:
            response = self.session.delete(f"{self.server_url}/api/youtube/channels/{channel_id}")
            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json()
                return error_data
        except Exception as e:
            return {"error": f"Lỗi kết nối: {e}"}

    def update_channel_id(self, channel_id):
        """Cập nhật channel ID từ handle"""
        try:
            response = self.session.post(f"{self.server_url}/api/youtube/channels/{channel_id}/update-id")
            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json()
                return error_data
        except Exception as e:
            return {"error": f"Lỗi kết nối: {e}"}

    # Firebase Management Methods
    def get_firebase_collections(self):
        """Lấy danh sách tất cả collections trong Firebase"""
        try:
            response = self.session.get(f"{self.server_url}/api/firebase/collections")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Lỗi HTTP: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return None

    def get_collection_stats(self, collection_name):
        """Lấy thống kê của một collection"""
        try:
            response = self.session.get(f"{self.server_url}/api/firebase/collection/{collection_name}/stats")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Lỗi HTTP: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return None

    def clear_collection(self, collection_name):
        """Xóa toàn bộ documents trong một collection"""
        try:
            response = self.session.delete(f"{self.server_url}/api/firebase/collection/{collection_name}/clear")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Lỗi HTTP: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return None

    def clear_old_documents(self, collection_name, days):
        """Xóa documents cũ trong một collection dựa trên số ngày"""
        try:
            response = self.session.delete(
                f"{self.server_url}/api/firebase/collection/{collection_name}/clear-old?days={days}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Lỗi HTTP: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return None

    def get_collection_documents(self, collection_name, limit=50, offset=0):
        """Lấy danh sách documents trong một collection"""
        try:
            response = self.session.get(
                f"{self.server_url}/api/firebase/collection/{collection_name}/documents?limit={limit}&offset={offset}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Lỗi HTTP: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return None

    def delete_document(self, collection_name, document_id):
        """Xóa một document cụ thể"""
        try:
            response = self.session.delete(f"{self.server_url}/api/firebase/document/{collection_name}/{document_id}")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Lỗi HTTP: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return None

    def update_document(self, collection_name, document_id, data):
        """Cập nhật một document cụ thể"""
        try:
            response = self.session.put(f"{self.server_url}/api/firebase/document/{collection_name}/{document_id}",
                                        json=data)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Lỗi HTTP: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            return None


def clear_screen():
    """Xóa màn hình"""
    os.system('clear' if os.name == 'posix' else 'cls')


def show_header():
    """Hiển thị header"""
    print("=" * 60)
    print("🤖 QUẢN LÝ MT5 VÀ FIREBASE")
    print("=" * 60)
    print(f"📡 Server: {SERVER_URL}")
    print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)


def show_mt5_account_info(config_manager):
    """Hiển thị thông tin tài khoản MT5 với cập nhật realtime"""
    # Biến để kiểm soát vòng lặp
    stop_updating = False
    update_count = 0

    def check_for_enter():
        """Thread để kiểm tra phím Enter"""
        nonlocal stop_updating
        input("Nhấn Enter để dừng cập nhật...")
        stop_updating = True

    # Bắt đầu thread kiểm tra phím Enter
    enter_thread = threading.Thread(target=check_for_enter, daemon=True)
    enter_thread.start()

    print("🔄 Bắt đầu cập nhật realtime mỗi 30 giây...")
    time.sleep(0.5)

    while not stop_updating:
        try:
            update_count += 1

            # Xóa màn hình và hiển thị header
            clear_screen()
            print("=" * 60)
            print("🤖 QUẢN LÝ MT5 VÀ FIREBASE")
            print("=" * 60)
            print(f"📡 Server: {SERVER_URL}")
            print(f"⏰ Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 60)
            print("💰 THÔNG TIN TÀI KHOẢN MT5 (REALTIME)")
            print("=" * 60)

            # Hiển thị trạng thái cập nhật
            loading_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            loading_char = loading_chars[update_count % len(loading_chars)]
            print(f"{loading_char} Đang cập nhật... (Lần thứ {update_count})")

            # Lấy thông tin tài khoản MT5
            account_info = config_manager.get_mt5_account_info()
            if not account_info:
                print("❌ Không thể lấy thông tin tài khoản MT5")
                print("Có thể do:")
                print("  - Bot chưa khởi động")
                print("  - MT5 chưa kết nối")
                print("  - Server không hỗ trợ API này")
                print("\n🔄 Đang thử lại...")
                time.sleep(3)
                continue

            # Hiển thị thông tin tài khoản
            if 'account' in account_info:
                account = account_info['account']
                print("\n📊 THÔNG TIN TÀI KHOẢN:")
                print(f"  🆔 Login: {account.get('login', 'N/A')}")
                print(f"  🏦 Server: {account.get('server', 'N/A')}")
                print(f"  💰 Balance: ${account.get('balance', 0):,.2f}")
                print(f"  💵 Equity: ${account.get('equity', 0):,.2f}")
                print(f"  📈 Profit: ${account.get('profit', 0):,.2f}")
                print(f"  💳 Margin: ${account.get('margin', 0):,.2f}")
                print(f"  🔒 Free Margin: ${account.get('free_margin', 0):,.2f}")
                print(f"  📊 Margin Level: {account.get('margin_level', 0):,.2f}%")
                print(f"  🎯 Currency: {account.get('currency', 'N/A')}")

            # Hiển thị các lệnh đang mở
            if 'positions' in account_info:
                positions = account_info['positions']
                print(f"\n📋 LỆNH ĐANG MỞ ({len(positions)} lệnh):")
                if positions:
                    print(
                        f"{'Ticket':<10} {'Symbol':<10} {'Type':<6} {'Volume':<8} {'Price':<10} {'Profit':<12} {'Comment':<15}")
                    print("-" * 80)
                    for pos in positions:
                        ticket = pos.get('ticket', 'N/A')
                        symbol = pos.get('symbol', 'N/A')
                        pos_type = 'BUY' if pos.get('type', 0) == 0 else 'SELL'
                        volume = pos.get('volume', 0)
                        price = pos.get('price_open', 0)
                        profit = pos.get('profit', 0)
                        comment = pos.get('comment', 'N/A')

                        # Thêm màu sắc cho profit
                        profit_str = f"${profit:<11.2f}"
                        if profit > 0:
                            profit_str = f"📈 {profit_str}"
                        elif profit < 0:
                            profit_str = f"📉 {profit_str}"

                        print(
                            f"{ticket:<10} {symbol:<10} {pos_type:<6} {volume:<8.2f} {price:<10.5f} {profit_str} {comment:<15}")
                else:
                    print("  Không có lệnh nào đang mở")

            # Hiển thị thống kê tổng quan
            if 'summary' in account_info:
                summary = account_info['summary']
                print(f"\n📈 THỐNG KÊ TỔNG QUAN:")
                print(f"  📊 Tổng lệnh mở: {summary.get('total_positions', 0)}")
                print(f"  💰 Tổng profit: ${summary.get('total_profit', 0):,.2f}")
                print(f"  📈 Lệnh có lãi: {summary.get('profitable_positions', 0)}")
                print(f"  📉 Lệnh thua lỗ: {summary.get('losing_positions', 0)}")

            # Hiển thị thống kê trong ngày
            if 'today_summary' in account_info:
                today_summary = account_info['today_summary']
                period = today_summary.get('period', 'Hôm nay')
                print(f"\n📅 THỐNG KÊ TRONG NGÀY ({period}):")
                print(f"  📊 Lệnh mở: {today_summary.get('total_positions', 0)}")
                print(f"  💰 Profit: ${today_summary.get('total_profit', 0):,.2f}")
                print(f"  📈 Lệnh có lãi: {today_summary.get('profitable_positions', 0)}")
                print(f"  📉 Lệnh thua lỗ: {today_summary.get('losing_positions', 0)}")

            # Hiển thị thời gian cập nhật
            if 'timestamp' in account_info:
                timestamp = account_info['timestamp']
                print(f"\n⏰ Cập nhật lúc: {timestamp}")

            print("\n" + "=" * 60)
            print(f"🔄 Cập nhật lần thứ {update_count} - Mỗi 30 giây - Nhấn Enter để dừng")

            # Chờ 30 giây trước khi cập nhật lại
            time.sleep(30)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Lỗi khi cập nhật: {e}")
            print("🔄 Đang thử lại...")
            time.sleep(3)

    print("\n✅ Đã dừng cập nhật realtime")
    input("Nhấn Enter để quay lại menu chính...")


def show_youtube_channel_management(config_manager):
    """Hiển thị menu quản lý YouTube channels"""
    while True:
        clear_screen()
        show_header()

        print("📺 QUẢN LÝ YOUTUBE CHANNELS")
        print("=" * 60)
        print("Chức năng quản lý nguồn video crawler:")
        print("  - Xem danh sách channels")
        print("  - Thêm channel mới")
        print("  - Xóa channel")
        print("  - Cập nhật channel ID")
        print("-" * 60)

        print("🔧 MENU YOUTUBE CHANNELS:")
        print("  1. 📋 Xem danh sách Channels")
        print("  2. ➕ Thêm Channel mới")
        print("  3. 🗑️ Xóa Channel")
        print("  4. 🔄 Cập nhật Channel ID")
        print("  0. 🔙 Quay lại menu chính")
        print("-" * 60)

        choice = input("Chọn chức năng (0-4): ").strip()

        if choice == '0':
            break
        elif choice == '1':
            show_youtube_channels_list(config_manager)
        elif choice == '2':
            show_add_youtube_channel(config_manager)
        elif choice == '3':
            show_delete_youtube_channel(config_manager)
        elif choice == '4':
            show_update_channel_id(config_manager)
        else:
            print("❌ Lựa chọn không hợp lệ!")
            input("Nhấn Enter để tiếp tục...")


def show_youtube_channels_list(config_manager):
    """Hiển thị danh sách YouTube channels"""
    clear_screen()
    show_header()

    print("📋 DANH SÁCH YOUTUBE CHANNELS")
    print("=" * 60)

    try:
        result = config_manager.get_youtube_channels()
        if result and result.get('success'):
            channels = result.get('channels', [])
            count = result.get('count', 0)

            print(f"✅ Tìm thấy {count} channels:")
            print("-" * 80)

            if channels:
                print(f"{'ID':<30} {'Tên Channel':<25} {'Handle':<15} {'Status':<10}")
                print("-" * 80)
                
                for channel in channels:
                    channel_id = channel.get('id', 'N/A')[:28] + '..' if len(channel.get('id', '')) > 30 else channel.get('id', 'N/A')
                    name = channel.get('name', 'N/A')[:23] + '..' if len(channel.get('name', '')) > 25 else channel.get('name', 'N/A')
                    handle = channel.get('handle', 'N/A')[:13] + '..' if len(channel.get('handle', '')) > 15 else channel.get('handle', 'N/A')
                    status = channel.get('status', 'N/A')
                    
                    print(f"{channel_id:<30} {name:<25} {handle:<15} {status:<10}")
                
                print("-" * 80)
                print(f"📊 Tổng cộng: {count} channels")
            else:
                print("  Không có channels nào")

        else:
            print("❌ Không thể lấy danh sách channels")
            if result:
                print(f"Lỗi: {result.get('error', 'Không xác định')}")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

    print("\n" + "=" * 60)
    input("Nhấn Enter để quay lại...")


def show_add_youtube_channel(config_manager):
    """Hiển thị chức năng thêm YouTube channel"""
    clear_screen()
    show_header()

    print("➕ THÊM YOUTUBE CHANNEL MỚI")
    print("=" * 60)
    print("Chức năng này sẽ thêm channel mới vào video crawler")
    print("-" * 60)

    try:
        # Nhập thông tin channel
        print("📝 Nhập thông tin channel:")
        channel_url = input("URL Channel (ví dụ: https://www.youtube.com/@channelname): ").strip()
        
        if not channel_url:
            print("❌ URL không được để trống")
            input("Nhấn Enter để quay lại...")
            return

        channel_name = input("Tên Channel (Enter để tự động lấy từ URL): ").strip()
        
        # Hỏi về loại channel
        print("\n🔧 Cấu hình channel:")
        is_streams = input("Có phải channel streams không? (y/n): ").strip().lower() == 'y'
        notifications_only = input("Chỉ dùng cho notifications? (y/n): ").strip().lower() == 'y'

        # Tạo dữ liệu channel
        channel_data = {
            'url': channel_url,
            'name': channel_name,
            'is_streams': is_streams,
            'notifications_only': notifications_only
        }

        print(f"\n📋 Thông tin channel sẽ thêm:")
        print(f"  URL: {channel_url}")
        print(f"  Tên: {channel_name}")
        print(f"  Streams: {'Có' if is_streams else 'Không'}")
        print(f"  Notifications only: {'Có' if notifications_only else 'Không'}")

        confirm = input("\nBạn có chắc chắn muốn thêm channel này? (y/n): ").strip().lower()

        if confirm == 'y':
            print("\n➕ Đang thêm channel...")

            result = config_manager.add_youtube_channel(channel_data)
            if result and result.get('success'):
                print("✅ Thêm channel thành công!")
                print(f"📝 Kết quả: {result.get('message', '')}")
                
                # Hỏi có muốn cập nhật channel ID ngay không
                channel_id = result.get('channel', {}).get('id')
                if channel_id:
                    update_now = input("\nBạn có muốn cập nhật channel ID ngay không? (y/n): ").strip().lower()
                    if update_now == 'y':
                        print("🔄 Đang cập nhật channel ID...")
                        update_result = config_manager.update_channel_id(channel_id)
                        if update_result and update_result.get('success'):
                            print("✅ Cập nhật channel ID thành công!")
                        else:
                            print("❌ Lỗi khi cập nhật channel ID")
                            if update_result:
                                print(f"Lỗi: {update_result.get('error', 'Không xác định')}")
            else:
                print("❌ Lỗi khi thêm channel")
                if result:
                    print(f"Lỗi: {result.get('error', 'Không xác định')}")
        else:
            print("❌ Đã hủy thêm channel")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

    print("\n" + "=" * 60)
    input("Nhấn Enter để quay lại...")


def show_delete_youtube_channel(config_manager):
    """Hiển thị chức năng xóa YouTube channel"""
    clear_screen()
    show_header()

    print("🗑️ XÓA YOUTUBE CHANNEL")
    print("=" * 60)
    print("Chức năng này sẽ xóa channel khỏi video crawler")
    print("-" * 60)

    # Lấy danh sách channels
    result = config_manager.get_youtube_channels()
    if not result or not result.get('success'):
        print("❌ Không thể lấy danh sách channels")
        input("Nhấn Enter để quay lại...")
        return

    channels = result.get('channels', [])
    if not channels:
        print("❌ Không có channels nào")
        input("Nhấn Enter để quay lại...")
        return

    print("📋 Chọn channel để xóa:")
    for i, channel in enumerate(channels, 1):
        name = channel.get('name', 'N/A')
        url = channel.get('url', 'N/A')
        print(f"  {i:2d}. {name}")
        print(f"      URL: {url}")

    print("-" * 60)

    try:
        choice = input("Nhập số thứ tự channel cần xóa: ").strip()

        if not choice.isdigit():
            print("❌ Vui lòng nhập số thứ tự hợp lệ")
            input("Nhấn Enter để quay lại...")
            return

        choice_num = int(choice)
        if choice_num < 1 or choice_num > len(channels):
            print("❌ Số thứ tự không hợp lệ")
            input("Nhấn Enter để quay lại...")
            return

        selected_channel = channels[choice_num - 1]
        channel_id = selected_channel.get('id')
        channel_name = selected_channel.get('name', 'Unknown')

        # Xác nhận xóa
        print(f"\n⚠️ Bạn có chắc chắn muốn xóa channel '{channel_name}'?")
        confirm = input("Nhập 'DELETE' để xác nhận: ").strip()

        if confirm == "DELETE":
            print(f"\n🗑️ Đang xóa channel '{channel_name}'...")

            result = config_manager.delete_youtube_channel(channel_id)
            if result and result.get('success'):
                print(f"✅ Đã xóa channel '{channel_name}' thành công")
            else:
                print("❌ Lỗi khi xóa channel")
                if result:
                    print(f"Lỗi: {result.get('error', 'Không xác định')}")
        else:
            print("❌ Đã hủy thao tác xóa")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

    print("\n" + "=" * 60)
    input("Nhấn Enter để quay lại...")


def show_update_channel_id(config_manager):
    """Hiển thị chức năng cập nhật channel ID"""
    clear_screen()
    show_header()

    print("🔄 CẬP NHẬT CHANNEL ID")
    print("=" * 60)
    print("Chức năng này sẽ cập nhật channel ID từ handle")
    print("-" * 60)

    # Lấy danh sách channels
    result = config_manager.get_youtube_channels()
    if not result or not result.get('success'):
        print("❌ Không thể lấy danh sách channels")
        input("Nhấn Enter để quay lại...")
        return

    channels = result.get('channels', [])
    if not channels:
        print("❌ Không có channels nào")
        input("Nhấn Enter để quay lại...")
        return

    print("📋 Chọn channel để cập nhật ID:")
    for i, channel in enumerate(channels, 1):
        name = channel.get('name', 'N/A')
        handle = channel.get('handle', 'N/A')
        channel_id = channel.get('channel_id', 'Chưa có')
        print(f"  {i:2d}. {name}")
        print(f"      Handle: {handle}")
        print(f"      Channel ID: {channel_id}")

    print("-" * 60)

    try:
        choice = input("Nhập số thứ tự channel cần cập nhật: ").strip()

        if not choice.isdigit():
            print("❌ Vui lòng nhập số thứ tự hợp lệ")
            input("Nhấn Enter để quay lại...")
            return

        choice_num = int(choice)
        if choice_num < 1 or choice_num > len(channels):
            print("❌ Số thứ tự không hợp lệ")
            input("Nhấn Enter để quay lại...")
            return

        selected_channel = channels[choice_num - 1]
        channel_id = selected_channel.get('id')
        channel_name = selected_channel.get('name', 'Unknown')
        handle = selected_channel.get('handle')

        if not handle:
            print("❌ Channel này không có handle để cập nhật ID")
            input("Nhấn Enter để quay lại...")
            return

        # Xác nhận cập nhật
        print(f"\n⚠️ Bạn có chắc chắn muốn cập nhật channel ID cho '{channel_name}'?")
        print(f"Handle: {handle}")
        confirm = input("Nhập 'UPDATE' để xác nhận: ").strip()

        if confirm == "UPDATE":
            print(f"\n🔄 Đang cập nhật channel ID cho '{channel_name}'...")

            result = config_manager.update_channel_id(channel_id)
            if result and result.get('success'):
                print(f"✅ Đã cập nhật channel ID thành công")
                print(f"Channel ID: {result.get('channel_id', 'N/A')}")
                print(f"Channel Title: {result.get('channel_title', 'N/A')}")
            else:
                print("❌ Lỗi khi cập nhật channel ID")
                if result:
                    print(f"Lỗi: {result.get('error', 'Không xác định')}")
        else:
            print("❌ Đã hủy thao tác cập nhật")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

    print("\n" + "=" * 60)
    input("Nhấn Enter để quay lại...")


def show_firebase_management(config_manager):
    """Hiển thị menu quản lý Firebase"""
    while True:
        clear_screen()
        show_header()

        print("🔥 QUẢN LÝ FIREBASE")
        print("=" * 60)
        print("Chức năng quản lý dữ liệu Firebase:")
        print("  - Xem danh sách collections")
        print("  - Xem thống kê collection")
        print("  - Xóa toàn bộ collection")
        print("  - Xóa documents cũ")
        print("  - Xem documents trong collection")
        print("  - Xóa document cụ thể")
        print("  - Cập nhật document")
        print("-" * 60)

        print("🔧 MENU FIREBASE:")
        print("  1. 📋 Xem danh sách Collections")
        print("  2. 📊 Xem thống kê Collection")
        print("  3. 🗑️ Xóa toàn bộ Collection")
        print("  4. 🗑️ Xóa Documents cũ")
        print("  5. 📄 Xem Documents trong Collection")
        print("  6. 🗑️ Xóa Document cụ thể")
        print("  7. ✏️ Cập nhật Document")
        print("  0. 🔙 Quay lại menu chính")
        print("-" * 60)

        choice = input("Chọn chức năng (0-7): ").strip()

        if choice == '0':
            break
        elif choice == '1':
            show_firebase_collections(config_manager)
        elif choice == '2':
            show_collection_stats(config_manager)
        elif choice == '3':
            show_clear_collection(config_manager)
        elif choice == '4':
            show_clear_old_documents(config_manager)
        elif choice == '5':
            show_collection_documents(config_manager)
        elif choice == '6':
            show_delete_document(config_manager)
        elif choice == '7':
            show_update_document(config_manager)
        else:
            print("❌ Lựa chọn không hợp lệ!")
            input("Nhấn Enter để tiếp tục...")


def show_firebase_collections(config_manager):
    """Hiển thị danh sách collections"""
    clear_screen()
    show_header()

    print("📋 DANH SÁCH FIREBASE COLLECTIONS")
    print("=" * 60)

    try:
        result = config_manager.get_firebase_collections()
        if result and result.get('success'):
            collections = result.get('collections', [])
            count = result.get('count', 0)

            print(f"✅ Tìm thấy {count} collections:")
            print("-" * 60)

            if collections:
                for i, collection in enumerate(collections, 1):
                    print(f"  {i:2d}. {collection}")
            else:
                print("  Không có collection nào")

            print("-" * 60)
            print(f"📊 Tổng cộng: {count} collections")

        else:
            print("❌ Không thể lấy danh sách collections")
            if result:
                print(f"Lỗi: {result.get('error', 'Không xác định')}")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

    print("\n" + "=" * 60)
    input("Nhấn Enter để quay lại...")


def show_collection_stats(config_manager):
    """Hiển thị thống kê collection"""
    clear_screen()
    show_header()

    print("📊 THỐNG KÊ COLLECTION")
    print("=" * 60)

    # Lấy danh sách collections trước
    collections_result = config_manager.get_firebase_collections()
    if not collections_result or not collections_result.get('success'):
        print("❌ Không thể lấy danh sách collections")
        input("Nhấn Enter để quay lại...")
        return

    collections = collections_result.get('collections', [])
    if not collections:
        print("❌ Không có collection nào")
        input("Nhấn Enter để quay lại...")
        return

    print("📋 Chọn collection để xem thống kê:")
    for i, collection in enumerate(collections, 1):
        print(f"  {i:2d}. {collection}")

    print("-" * 60)

    try:
        choice = input("Nhập số thứ tự hoặc tên collection: ").strip()

        # Xác định collection name
        collection_name = None
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(collections):
                collection_name = collections[choice_num - 1]
            else:
                print("❌ Số thứ tự không hợp lệ")
                input("Nhấn Enter để quay lại...")
                return
        else:
            if choice in collections:
                collection_name = choice
            else:
                print(f"❌ Không tìm thấy collection '{choice}'")
                input("Nhấn Enter để quay lại...")
                return

        # Lấy thống kê
        result = config_manager.get_collection_stats(collection_name)
        if result and result.get('success'):
            doc_count = result.get('document_count', 0)
            collection = result.get('collection', collection_name)

            print(f"\n📊 THỐNG KÊ COLLECTION: {collection}")
            print("-" * 60)
            print(f"📄 Số documents: {doc_count:,}")

            if doc_count > 0:
                print(f"💾 Kích thước ước tính: ~{doc_count * 2} KB")

        else:
            print("❌ Không thể lấy thống kê collection")
            if result:
                print(f"Lỗi: {result.get('error', 'Không xác định')}")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

    print("\n" + "=" * 60)
    input("Nhấn Enter để quay lại...")


def show_clear_collection(config_manager):
    """Hiển thị chức năng xóa collection"""
    clear_screen()
    show_header()

    print("🗑️ XÓA TOÀN BỘ COLLECTION")
    print("=" * 60)
    print("⚠️ CẢNH BÁO: Hành động này sẽ xóa TẤT CẢ documents trong collection!")
    print("⚠️ Hành động này KHÔNG THỂ HOÀN TÁC!")
    print("-" * 60)

    # Lấy danh sách collections
    collections_result = config_manager.get_firebase_collections()
    if not collections_result or not collections_result.get('success'):
        print("❌ Không thể lấy danh sách collections")
        input("Nhấn Enter để quay lại...")
        return

    collections = collections_result.get('collections', [])
    if not collections:
        print("❌ Không có collection nào")
        input("Nhấn Enter để quay lại...")
        return

    print("📋 Chọn collection để xóa:")
    for i, collection in enumerate(collections, 1):
        print(f"  {i:2d}. {collection}")

    print("-" * 60)

    try:
        choice = input("Nhập số thứ tự hoặc tên collection: ").strip()

        # Xác định collection name
        collection_name = None
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(collections):
                collection_name = collections[choice_num - 1]
            else:
                print("❌ Số thứ tự không hợp lệ")
                input("Nhấn Enter để quay lại...")
                return
        else:
            if choice in collections:
                collection_name = choice
            else:
                print(f"❌ Không tìm thấy collection '{choice}'")
                input("Nhấn Enter để quay lại...")
                return

        # Hiển thị thống kê trước khi xóa
        stats_result = config_manager.get_collection_stats(collection_name)
        if stats_result and stats_result.get('success'):
            doc_count = stats_result.get('document_count', 0)
            print(f"\n📊 Collection '{collection_name}' có {doc_count:,} documents")

        # Xác nhận xóa
        print(f"\n⚠️ Bạn có chắc chắn muốn xóa TẤT CẢ documents trong collection '{collection_name}'?")
        confirm = input("Nhập 'DELETE' để xác nhận: ").strip()

        if confirm == "DELETE":
            print(f"\n🗑️ Đang xóa collection '{collection_name}'...")

            result = config_manager.clear_collection(collection_name)
            if result and result.get('success'):
                deleted_count = result.get('deleted_count', 0)
                print(f"✅ Đã xóa thành công {deleted_count:,} documents từ collection '{collection_name}'")
            else:
                print("❌ Lỗi khi xóa collection")
                if result:
                    print(f"Lỗi: {result.get('error', 'Không xác định')}")
        else:
            print("❌ Đã hủy thao tác xóa")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

    print("\n" + "=" * 60)
    input("Nhấn Enter để quay lại...")


def show_clear_old_documents(config_manager):
    """Hiển thị chức năng xóa documents cũ"""
    clear_screen()
    show_header()

    print("🗑️ XÓA DOCUMENTS CŨ")
    print("=" * 60)
    print("Chức năng này sẽ xóa các documents cũ hơn số ngày được chỉ định")
    print("-" * 60)

    # Lấy danh sách collections
    collections_result = config_manager.get_firebase_collections()
    if not collections_result or not collections_result.get('success'):
        print("❌ Không thể lấy danh sách collections")
        input("Nhấn Enter để quay lại...")
        return

    collections = collections_result.get('collections', [])
    if not collections:
        print("❌ Không có collection nào")
        input("Nhấn Enter để quay lại...")
        return

    print("📋 Chọn collection:")
    for i, collection in enumerate(collections, 1):
        print(f"  {i:2d}. {collection}")

    print("-" * 60)

    try:
        choice = input("Nhập số thứ tự hoặc tên collection: ").strip()

        # Xác định collection name
        collection_name = None
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(collections):
                collection_name = collections[choice_num - 1]
            else:
                print("❌ Số thứ tự không hợp lệ")
                input("Nhấn Enter để quay lại...")
                return
        else:
            if choice in collections:
                collection_name = choice
            else:
                print(f"❌ Không tìm thấy collection '{choice}'")
                input("Nhấn Enter để quay lại...")
                return

        # Nhập số ngày
        while True:
            try:
                days_input = input(f"\nNhập số ngày (documents cũ hơn X ngày sẽ bị xóa): ").strip()
                days = int(days_input)
                if days > 0:
                    break
                else:
                    print("❌ Số ngày phải lớn hơn 0")
            except ValueError:
                print("❌ Vui lòng nhập số nguyên hợp lệ")

        # Hiển thị thống kê trước khi xóa
        stats_result = config_manager.get_collection_stats(collection_name)
        if stats_result and stats_result.get('success'):
            doc_count = stats_result.get('document_count', 0)
            print(f"\n📊 Collection '{collection_name}' có {doc_count:,} documents")

        # Xác nhận xóa
        print(f"\n⚠️ Bạn có chắc chắn muốn xóa documents cũ hơn {days} ngày trong collection '{collection_name}'?")
        confirm = input("Nhập 'DELETE' để xác nhận: ").strip()

        if confirm == "DELETE":
            print(f"\n🗑️ Đang xóa documents cũ hơn {days} ngày...")

            result = config_manager.clear_old_documents(collection_name, days)
            if result and result.get('success'):
                deleted_count = result.get('deleted_count', 0)
                cutoff_date = result.get('cutoff_date', 'N/A')
                print(f"✅ Đã xóa thành công {deleted_count:,} documents cũ hơn {days} ngày")
                print(f"📅 Cutoff date: {cutoff_date}")
            else:
                print("❌ Lỗi khi xóa documents cũ")
                if result:
                    print(f"Lỗi: {result.get('error', 'Không xác định')}")
        else:
            print("❌ Đã hủy thao tác xóa")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

    print("\n" + "=" * 60)
    input("Nhấn Enter để quay lại...")


def show_collection_documents(config_manager):
    """Hiển thị documents trong collection"""
    clear_screen()
    show_header()

    print("📄 XEM DOCUMENTS TRONG COLLECTION")
    print("=" * 60)

    # Lấy danh sách collections
    collections_result = config_manager.get_firebase_collections()
    if not collections_result or not collections_result.get('success'):
        print("❌ Không thể lấy danh sách collections")
        input("Nhấn Enter để quay lại...")
        return

    collections = collections_result.get('collections', [])
    if not collections:
        print("❌ Không có collection nào")
        input("Nhấn Enter để quay lại...")
        return

    print("📋 Chọn collection:")
    for i, collection in enumerate(collections, 1):
        print(f"  {i:2d}. {collection}")

    print("-" * 60)

    try:
        choice = input("Nhập số thứ tự hoặc tên collection: ").strip()

        # Xác định collection name
        collection_name = None
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(collections):
                collection_name = collections[choice_num - 1]
            else:
                print("❌ Số thứ tự không hợp lệ")
                input("Nhấn Enter để quay lại...")
                return
        else:
            if choice in collections:
                collection_name = choice
            else:
                print(f"❌ Không tìm thấy collection '{choice}'")
                input("Nhấn Enter để quay lại...")
                return

        # Lấy documents
        result = config_manager.get_collection_documents(collection_name, limit=20)
        if result and result.get('success'):
            documents = result.get('documents', [])
            count = result.get('count', 0)

            print(f"\n📄 DOCUMENTS TRONG COLLECTION: {collection_name}")
            print("=" * 80)

            if documents:
                print(f"{'ID':<30} {'Title/Name':<30} {'Date':<20}")
                print("-" * 80)

                for doc in documents:
                    doc_id = doc.get('id', 'N/A')[:28] + '..' if len(doc.get('id', '')) > 30 else doc.get('id', 'N/A')

                    # Tìm title hoặc name
                    title = 'N/A'
                    for field in ['title', 'name', 'subject', 'heading']:
                        if field in doc:
                            title = str(doc[field])[:28] + '..' if len(str(doc[field])) > 30 else str(doc[field])
                            break

                    # Tìm date
                    date = 'N/A'
                    for field in ['created_at', 'updated_at', 'timestamp', 'date', 'crawled_at', 'published_date']:
                        if field in doc:
                            date = str(doc[field])[:20]
                            break

                    print(f"{doc_id:<30} {title:<30} {date:<20}")

                print("-" * 80)
                print(f"📊 Hiển thị {len(documents)}/{count} documents (giới hạn 20)")
            else:
                print("  Không có documents nào")

        else:
            print("❌ Không thể lấy documents")
            if result:
                print(f"Lỗi: {result.get('error', 'Không xác định')}")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

    print("\n" + "=" * 60)
    input("Nhấn Enter để quay lại...")


def show_delete_document(config_manager):
    """Hiển thị chức năng xóa document cụ thể"""
    clear_screen()
    show_header()

    print("🗑️ XÓA DOCUMENT CỤ THỂ")
    print("=" * 60)
    print("Chức năng này sẽ xóa một document cụ thể trong collection")
    print("-" * 60)

    # Lấy danh sách collections
    collections_result = config_manager.get_firebase_collections()
    if not collections_result or not collections_result.get('success'):
        print("❌ Không thể lấy danh sách collections")
        input("Nhấn Enter để quay lại...")
        return

    collections = collections_result.get('collections', [])
    if not collections:
        print("❌ Không có collection nào")
        input("Nhấn Enter để quay lại...")
        return

    print("📋 Chọn collection:")
    for i, collection in enumerate(collections, 1):
        print(f"  {i:2d}. {collection}")

    print("-" * 60)

    try:
        choice = input("Nhập số thứ tự hoặc tên collection: ").strip()

        # Xác định collection name
        collection_name = None
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(collections):
                collection_name = collections[choice_num - 1]
            else:
                print("❌ Số thứ tự không hợp lệ")
                input("Nhấn Enter để quay lại...")
                return
        else:
            if choice in collections:
                collection_name = choice
            else:
                print(f"❌ Không tìm thấy collection '{choice}'")
                input("Nhấn Enter để quay lại...")
                return

        # Nhập document ID
        document_id = input(f"\nNhập Document ID cần xóa: ").strip()
        if not document_id:
            print("❌ Document ID không được để trống")
            input("Nhấn Enter để quay lại...")
            return

        # Xác nhận xóa
        print(f"\n⚠️ Bạn có chắc chắn muốn xóa document '{document_id}' trong collection '{collection_name}'?")
        confirm = input("Nhập 'DELETE' để xác nhận: ").strip()

        if confirm == "DELETE":
            print(f"\n🗑️ Đang xóa document '{document_id}'...")

            result = config_manager.delete_document(collection_name, document_id)
            if result and result.get('success'):
                print(f"✅ Đã xóa thành công document '{document_id}'")
            else:
                print("❌ Lỗi khi xóa document")
                if result:
                    print(f"Lỗi: {result.get('error', 'Không xác định')}")
        else:
            print("❌ Đã hủy thao tác xóa")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

    print("\n" + "=" * 60)
    input("Nhấn Enter để quay lại...")


def show_update_document(config_manager):
    """Hiển thị chức năng cập nhật document"""
    clear_screen()
    show_header()

    print("✏️ CẬP NHẬT DOCUMENT")
    print("=" * 60)
    print("Chức năng này sẽ cập nhật một document cụ thể trong collection")
    print("-" * 60)

    # Lấy danh sách collections
    collections_result = config_manager.get_firebase_collections()
    if not collections_result or not collections_result.get('success'):
        print("❌ Không thể lấy danh sách collections")
        input("Nhấn Enter để quay lại...")
        return

    collections = collections_result.get('collections', [])
    if not collections:
        print("❌ Không có collection nào")
        input("Nhấn Enter để quay lại...")
        return

    print("📋 Chọn collection:")
    for i, collection in enumerate(collections, 1):
        print(f"  {i:2d}. {collection}")

    print("-" * 60)

    try:
        choice = input("Nhập số thứ tự hoặc tên collection: ").strip()

        # Xác định collection name
        collection_name = None
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(collections):
                collection_name = collections[choice_num - 1]
            else:
                print("❌ Số thứ tự không hợp lệ")
                input("Nhấn Enter để quay lại...")
                return
        else:
            if choice in collections:
                collection_name = choice
            else:
                print(f"❌ Không tìm thấy collection '{choice}'")
                input("Nhấn Enter để quay lại...")
                return

        # Nhập document ID
        document_id = input(f"\nNhập Document ID cần cập nhật: ").strip()
        if not document_id:
            print("❌ Document ID không được để trống")
            input("Nhấn Enter để quay lại...")
            return

        # Nhập dữ liệu cập nhật
        print(f"\nNhập dữ liệu cập nhật (JSON format):")
        print("Ví dụ: {\"title\": \"New Title\", \"status\": \"updated\"}")

        try:
            update_data_str = input("Dữ liệu JSON: ").strip()
            if not update_data_str:
                print("❌ Dữ liệu không được để trống")
                input("Nhấn Enter để quay lại...")
                return

            import json
            update_data = json.loads(update_data_str)

            # Xác nhận cập nhật
            print(f"\n⚠️ Bạn có chắc chắn muốn cập nhật document '{document_id}'?")
            print(f"Dữ liệu: {update_data}")
            confirm = input("Nhập 'UPDATE' để xác nhận: ").strip()

            if confirm == "UPDATE":
                print(f"\n✏️ Đang cập nhật document '{document_id}'...")

                result = config_manager.update_document(collection_name, document_id, update_data)
                if result and result.get('success'):
                    print(f"✅ Đã cập nhật thành công document '{document_id}'")
                else:
                    print("❌ Lỗi khi cập nhật document")
                    if result:
                        print(f"Lỗi: {result.get('error', 'Không xác định')}")
            else:
                print("❌ Đã hủy thao tác cập nhật")

        except json.JSONDecodeError:
            print("❌ Dữ liệu JSON không hợp lệ")
        except Exception as e:
            print(f"❌ Lỗi: {e}")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

    print("\n" + "=" * 60)
    input("Nhấn Enter để quay lại...")


def show_main_menu(config_manager):
    """Hiển thị menu chính"""
    while True:
        clear_screen()
        show_header()

        # Test kết nối
        if not config_manager.test_connection():
            print("❌ Không thể kết nối đến server!")
            print("Hãy kiểm tra:")
            print("  - Server có đang chạy không?")
            print("  - IP address có đúng không?")
            print("  - Port 5000 có mở không?")
            print(f"  - URL hiện tại: {SERVER_URL}")
            print("\nNhấn Enter để thử lại...")
            input()
            continue

        print("✅ Kết nối server thành công!")

        print("\n🔧 MENU CHÍNH:")
        print("  1. 💰 Thông tin tài khoản MT5")
        print("  2. 📺 Quản lý YouTube Channels")
        print("  3. 🔥 Quản lý Firebase")
        print("  0. 🚪 Thoát")
        print("-" * 60)

        choice = input("Chọn chức năng (0-3): ").strip()

        if choice == '0':
            print("👋 Tạm biệt!")
            break
        elif choice == '1':
            show_mt5_account_info(config_manager)
        elif choice == '2':
            show_youtube_channel_management(config_manager)
        elif choice == '3':
            show_firebase_management(config_manager)
        else:
            print("❌ Lựa chọn không hợp lệ!")
            input("Nhấn Enter để tiếp tục...")


def main():
    """Hàm chính"""
    global SERVER_URL

    print("🚀 KHỞI ĐỘNG CLIENT04.PY")
    print("=" * 60)

    # Kiểm tra kết nối mạng
    print("📡 Kiểm tra kết nối...")

    config_manager = ConfigManager(SERVER_URL)

    if not config_manager.test_connection():
        print(f"❌ Không thể kết nối đến {SERVER_URL}")
        print("\n🔧 HƯỚNG DẪN KHẮC PHỤC:")
        print("1. Đảm bảo server đang chạy trên máy chủ")
        print("2. Kiểm tra IP address trong file client.py")
        print("3. Đảm bảo port 5000 được mở")
        print("4. Kiểm tra firewall")
        print(f"\nIP hiện tại: {SERVER_URL}")
        change_ip = input("Bạn có muốn thay đổi IP không? (y/n): ").lower()
        if change_ip == 'y':
            new_ip = input("Nhập IP mới: ").strip()
            if new_ip:
                SERVER_URL = f"http://{new_ip}:5000"
                config_manager = ConfigManager(SERVER_URL)
                print(f"✅ Đã thay đổi IP thành: {SERVER_URL}")
                input("Nhấn Enter để tiếp tục...")

    # Hiển thị menu chính
    show_main_menu(config_manager)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Chương trình bị gián đoạn")
        print("👋 Tạm biệt!")
    except Exception as e:
        print(f"\n❌ Lỗi không mong muốn: {e}")
        print("Hãy kiểm tra lại và thử lại") 