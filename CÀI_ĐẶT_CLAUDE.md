# Hướng dẫn cài đặt MCP WeWork lên Claude Desktop

## Bước 1: Copy file cấu hình

Sao chép nội dung file `claude_desktop_config.json` vào file cấu hình Claude Desktop của bạn.

**Vị trí file cấu hình Claude Desktop:**

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

## Bước 2: Khởi động lại Claude Desktop

Sau khi lưu file cấu hình, khởi động lại ứng dụng Claude Desktop.

## Bước 3: Kiểm tra kết nối

Trong Claude Desktop, bạn có thể sử dụng các lệnh sau:

### Các công cụ có sẵn:

- **`test_connection`**: Kiểm tra kết nối với WeWork API
- **`search_projects`**: Tìm kiếm dự án theo tên
- **`get_project_details`**: Lấy chi tiết dự án
- **`analyze_project_tasks`**: Phân tích tasks trong dự án
- **`find_project_by_name`**: Tìm dự án theo tên với độ tương đồng
- **`get_project_statistics`**: Lấy thống kê tổng quan về dự án

### Tài nguyên có sẵn:

- **`file://projects/available`**: Xem danh sách tất cả dự án

## Ví dụ sử dụng:

```
Hãy kiểm tra kết nối WeWork của tôi
Tìm kiếm dự án có tên "Website Development"
Phân tích tasks của dự án có ID "12345"
```

## Lưu ý:

- Đảm bảo đã cài đặt Python và các dependencies cần thiết
- File `start_server.bat` sẽ tự động khởi chạy MCP server
- Server sẽ sử dụng token WeWork từ biến môi trường hoặc token mặc định
