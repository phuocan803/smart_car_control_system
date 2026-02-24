# SmartCar AWS-Enhanced Web Control

Điều khiển SmartCar bằng ngôn ngữ tự nhiên với Amazon Nova Sonic 2.

## Tính năng

- **Điều khiển thủ công**: Giao diện web với nút W/A/S/D/X
- **Điều khiển AI**: Nhập lệnh bằng tiếng Việt hoặc tiếng Anh
- **Lịch sử lệnh**: Theo dõi tất cả lệnh đã gửi (thủ công và AI)
- **Real-time status**: Cập nhật trạng thái mỗi 500ms
- **Test mode**: Chạy không cần Arduino

## Yêu cầu

### Phần mềm
```bash
pip install boto3 pyserial
```

### AWS Account
- Tài khoản AWS với quyền truy cập Amazon Bedrock
- Region: ap-northeast-1 (Tokyo)
- Model: amazon.nova-sonic-v1:0

## Cài đặt AWS

### 1. Cài đặt AWS CLI

**Windows:**
```bash
# Download từ: https://aws.amazon.com/cli/
# Hoặc dùng pip:
pip install awscli
```

**Linux/Mac:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### 2. Cấu hình AWS Credentials

```bash
aws configure
```

Nhập thông tin:
```
AWS Access Key ID: YOUR_ACCESS_KEY
AWS Secret Access Key: YOUR_SECRET_KEY
Default region name: ap-northeast-1
Default output format: json
```

### 3. Kiểm tra quyền truy cập Bedrock

```bash
aws bedrock list-foundation-models --region ap-northeast-1
```

### 4. Enable Amazon Nova Sonic 2

1. Đăng nhập AWS Console
2. Vào Amazon Bedrock service
3. Chọn region: ap-northeast-1 (Tokyo)
4. Vào "Model access"
5. Request access cho "Amazon Nova Sonic"
6. Đợi approval (thường vài phút)

## Sử dụng

### Chạy server

**Với Arduino:**
```bash
# 1. Upload SmartCar.ino và chọn Mode [3]
# 2. Chạy server
python Web/aws_web_control.py
```

**Test mode (không cần Arduino):**
```bash
python Web/aws_web_control.py --test
```

**Tắt LLM (chỉ điều khiển thủ công):**
```bash
python Web/aws_web_control.py --no-llm
```

### Truy cập web interface

Mở trình duyệt:
```
http://localhost:8080
```

Hoặc từ thiết bị khác trong LAN:
```
http://<IP_ADDRESS>:8080
```

## Ví dụ lệnh AI

### Tiếng Việt
- "đi thẳng"
- "rẽ trái"
- "quay phải"
- "lùi lại"
- "dừng lại"
- "tiến về phía trước"
- "quay sang bên trái"

### Tiếng Anh
- "go forward"
- "turn left"
- "turn right"
- "go backward"
- "stop"
- "move ahead"
- "reverse"

## API Endpoints

### Manual Control
```bash
# Gửi lệnh trực tiếp
curl http://localhost:8080/cmd/W  # Tiến
curl http://localhost:8080/cmd/A  # Trái
curl http://localhost:8080/cmd/S  # Lùi
curl http://localhost:8080/cmd/D  # Phải
curl http://localhost:8080/cmd/X  # Dừng
```

### AI Control
```bash
# Gửi lệnh ngôn ngữ tự nhiên
curl -X POST http://localhost:8080/llm/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "đi thẳng"}'

curl -X POST http://localhost:8080/llm/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "turn left"}'
```

### Status
```bash
# Lấy trạng thái hiện tại
curl http://localhost:8080/status
```

Response:
```json
{
  "current_command": "W",
  "command_count": 150,
  "llm_command_count": 25,
  "is_running": true,
  "test_mode": false,
  "llm_available": true,
  "history": [...]
}
```

## Troubleshooting

### LLM không khả dụng

**Lỗi: "boto3 not installed"**
```bash
pip install boto3
```

**Lỗi: "AWS credentials not found"**
```bash
aws configure
# Nhập Access Key và Secret Key
```

**Lỗi: "Access denied to model"**
- Vào AWS Console → Bedrock → Model access
- Request access cho Amazon Nova Sonic
- Đợi approval

**Lỗi: "Region not supported"**
- Đảm bảo region là ap-northeast-1
- Kiểm tra: `aws configure get region`

### Arduino không kết nối

**Windows:**
```python
# Thay đổi COM port trong aws_web_control.py
COM_PORT = 'COM8'  # Thử COM3, COM4, ...
```

**Linux:**
```python
COM_PORT = '/dev/ttyUSB0'  # Hoặc /dev/ttyACM0
```

### Test LLM không cần Arduino

```bash
python Web/aws_web_control.py --test
```

Sau đó mở http://localhost:8080 và thử các lệnh AI.

## Chi phí AWS

Amazon Nova Sonic 2 pricing (ap-northeast-1):
- Input: ~$0.0006 per 1K tokens
- Output: ~$0.0024 per 1K tokens

Ước tính:
- Mỗi lệnh: ~50-100 tokens
- Chi phí: ~$0.0001 per command
- 1000 lệnh: ~$0.10

**Lưu ý**: Kiểm tra pricing mới nhất tại AWS Bedrock pricing page.

## Cấu trúc code

```python
# aws_web_control.py
├── AWSBedrockLLM          # AWS Bedrock client
│   ├── __init__()         # Initialize boto3 client
│   └── parse_command()    # Parse natural language
├── SmartCarController     # Car controller
│   ├── connect_arduino()  # Serial connection
│   ├── send_command()     # Send W/A/S/D/X
│   └── parse_natural_language()  # LLM wrapper
└── SmartCarRequestHandler # HTTP server
    ├── GET /              # Serve HTML
    ├── GET /status        # Status JSON
    ├── GET /cmd/<cmd>     # Manual command
    └── POST /llm/parse    # AI command
```

## So sánh với web_control.py

| Tính năng | web_control.py | aws_web_control.py |
|-----------|----------------|-------------------|
| Điều khiển thủ công | ✓ | ✓ |
| Điều khiển AI | ✗ | ✓ |
| Lịch sử lệnh | ✗ | ✓ |
| Test mode | ✓ | ✓ |
| AWS Bedrock | ✗ | ✓ |
| Phân biệt nguồn lệnh | ✗ | ✓ |

## Development

### Thay đổi model

```python
# Trong aws_web_control.py
MODEL_ID = 'amazon.nova-sonic-v1:0'  # Thay đổi model ID
AWS_REGION = 'ap-northeast-1'        # Thay đổi region
```

### Thay đổi system prompt

```python
# Trong AWSBedrockLLM.parse_command()
system_prompt = """Your custom prompt here"""
```

### Thêm lệnh mới

1. Thêm vào Arduino firmware (SmartCar.ino)
2. Cập nhật system prompt trong `parse_command()`
3. Thêm vào `commands` dict trong HTML

## License

MIT License - Xem file LICENSE
