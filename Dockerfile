# Sử dụng Python 3.9 làm base image
FROM python:3.9

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Sao chép các file vào container
COPY requirements.txt requirements.txt
COPY . .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Mở port 5000 để Flask lắng nghe
EXPOSE 5000

# Chạy ứng dụng Flask
CMD ["python", "app.py"]