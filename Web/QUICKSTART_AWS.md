# Quick Start - AWS Web Control

Hướng dẫn nhanh để chạy SmartCar với điều khiển AI.

## Bước 1: Cài đặt Dependencies

```bash
pip install boto3 pyserial
```

## Bước 2: Cấu hình AWS

### Option A: Sử dụng AWS CLI (Khuyến nghị)

```bash
# Cài đặt AWS CLI
pip install awscli

# Cấu hình credentials
aws configure
```

Nhập thông tin:
```
AWS Access Key ID: [YOUR_ACCESS_KEY]
AWS Secret Access Key: [YOUR_SECRET_KEY]
Default region name: ap-northeast-1
Default output format: json
```

### Option B: Sử dụng Environment Variables

```bash
# Linux/Mac
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_DEFAULT_REGION="ap-northeast-1"

# Windows (PowerShell)
$env:AWS_ACCESS_KEY_ID="your_access_key"
$env:AWS_SECRET_ACCESS_KEY="your_secret_key"
$env:AWS_DEFAULT_REGION="ap-northeast-1"

# Windows (CMD)
set AWS_ACCESS_KEY_ID=your_access_key
set AWS_SECRET_ACCESS_KEY=your_secret_key
set AWS_DEFAULT_REGION=ap-northeast-1
```

### Option C: Sử dụng AWS Credentials File

Tạo file `~/.aws/credentials`:
```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

Tạo file `~/.aws/config`:
```ini
[default]
region = ap-northeast-1
output = json
```

## Bước 3: Enable Amazon Nova Sonic 2

1. Đăng nhập [AWS Console](https://console.aws.amazon.com/)
2. Chọn region: **ap-northeast-1** (Tokyo)
3. Vào service: **Amazon Bedrock**
4. Menu bên trái: **Model access**
5. Click **Modify model access** hoặc **Request model access**
6. Tìm và chọn: **Amazon Nova Sonic**
7. Click **Request model access** hoặc **Save changes**
8. Đợi approval (thường < 5 phút)

## Bước 4: Test LLM (không cần Arduino)

```bash
python Web/aws_web_control.py --test
```

Mở browser: http://localhost:8080

Thử các lệnh:
- "đi thẳng"
- "rẽ trái"
- "dừng lại"

## Bước 5: Chạy với Arduino

### 5.1: Upload Arduino Firmware

1. Mở Arduino IDE
2. Mở file: `Car/SmartCar.ino`
3. Chọn board và port
4. Upload
5. Mở Serial Monitor (9600 baud)
6. Nhập `3` để chọn Python Keyboard Mode

### 5.2: Chạy Server

```bash
python Web/aws_web_control.py
```

Hoặc từ menu chính:
```bash
python run.py
# Chọn [5] - AWS Web Control
```

### 5.3: Truy cập Web Interface

Mở browser:
```
http://localhost:8080
```

Hoặc từ thiết bị khác trong LAN:
```
http://[YOUR_IP]:8080
```

## Troubleshooting

### ✗ boto3 not installed
```bash
pip install boto3
```

### ✗ AWS credentials not found
```bash
aws configure
# Hoặc set environment variables
```

### ✗ Access denied to model
- Kiểm tra region: `aws configure get region` (phải là ap-northeast-1)
- Vào AWS Console → Bedrock → Model access
- Request access cho Amazon Nova Sonic

### ✗ COM port not found
```python
# Sửa trong aws_web_control.py
COM_PORT = 'COM8'  # Thay đổi port
```

### ✗ LLM response error
- Kiểm tra AWS credentials: `aws sts get-caller-identity`
- Kiểm tra model access trong AWS Console
- Xem logs trong terminal

## Test Commands

### Tiếng Việt
```
đi thẳng
rẽ trái
quay phải
lùi lại
dừng lại
```

### English
```
go forward
turn left
turn right
go backward
stop
```

## API Testing

### Manual Command
```bash
curl http://localhost:8080/cmd/W
```

### AI Command
```bash
curl -X POST http://localhost:8080/llm/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "đi thẳng"}'
```

### Status
```bash
curl http://localhost:8080/status
```

## Next Steps

- Đọc [README_AWS.md](README_AWS.md) để biết chi tiết
- Thử các lệnh phức tạp hơn
- Tùy chỉnh system prompt trong `aws_web_control.py`
- Thêm lệnh mới vào Arduino firmware

## Support

- AWS Bedrock Documentation: https://docs.aws.amazon.com/bedrock/
- Amazon Nova Models: https://aws.amazon.com/bedrock/nova/
- Project Issues: [GitHub Issues]
