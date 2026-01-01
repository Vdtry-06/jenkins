# CI/CD Pipeline với Jenkins và Ansible

## 📋 Mục lục
- [Tổng quan dự án](#tổng-quan-dự-án)
- [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
- [Các khái niệm cơ bản](#các-khái-niệm-cơ-bản)
- [Công nghệ sử dụng](#công-nghệ-sử-dụng)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Hướng dẫn cài đặt](#hướng-dẫn-cài-đặt)
- [Pipeline CI/CD](#pipeline-cicd)
- [Ansible Playbooks](#ansible-playbooks)
- [Troubleshooting](#troubleshooting)

## 🎯 Tổng quan dự án

Dự án này triển khai một quy trình CI/CD hoàn chỉnh cho ứng dụng Flask API đơn giản, tự động hóa toàn bộ quy trình từ commit code đến deploy lên production server.

**Luồng hoạt động:** Code → Git → Jenkins (CI) → Docker Hub → Ansible (CD) → Production Servers

### Ứng dụng Demo
- **Flask API**: API đơn giản thực hiện phép cộng hai số
- **Endpoint**: `/add?num1=X&num2=Y`
- **Unit Tests**: Kiểm tra tính đúng đắn của logic và xử lý lỗi

## 🏗️ Kiến trúc hệ thống

```
┌─────────────┐
│  Developer  │
└──────┬──────┘
       │ Git Push
       ▼
┌─────────────────┐
│  GitHub Repo    │
└──────┬──────────┘
       │ Webhook/Polling
       ▼
┌─────────────────┐     ┌──────────────┐
│    Jenkins      │────▶│  Docker Hub  │
│   (CI Server)   │     └──────────────┘
└──────┬──────────┘
       │ Ansible Playbook
       ▼
┌─────────────────┐
│ Production VMs  │
│ (192.168.56.10) │
└─────────────────┘
```

## 📚 Các khái niệm cơ bản

### CI/CD là gì?

#### **CI (Continuous Integration)**
Quá trình tích hợp code liên tục vào nhánh chung (main/master), mỗi lần tích hợp đều được:
- Build tự động
- Chạy unit tests
- Phát hiện lỗi sớm

#### **CD (Continuous Deployment/Delivery)**
Tự động đưa tính năng mới lên production một cách:
- An toàn
- Nhanh chóng
- Có thể rollback

### Agile Development
Làm việc theo chu kỳ ngắn (1-2 tuần), yêu cầu quy trình tự động hóa để tăng tốc độ bàn giao sản phẩm.

### Infrastructure as Code (IaC)
Định nghĩa hạ tầng (CPU, RAM, cài đặt phần mềm) bằng mã nguồn, giúp:
- Môi trường nhất quán
- Dễ dàng tái tạo
- Version control được infrastructure

## 🛠️ Công nghệ sử dụng

### CI/CD Tools
- **Jenkins**: Automation server cho CI/CD
- **Docker**: Containerization
- **Docker Hub**: Registry lưu trữ images
- **Ansible**: Configuration management và deployment

### Development
- **Flask**: Python web framework
- **Python unittest**: Testing framework
- **Git**: Version control

### Infrastructure
- **Ubuntu/Debian VMs**: Production servers
- **SSH**: Secure remote access
- **Ngrok**: Public Jenkins để nhận webhook (development)

## 📁 Cấu trúc dự án

```
project-root/
├── app.py                          # Flask application
├── test_app.py                     # Unit tests
├── Dockerfile                      # Docker image definition
├── requirements.txt                # Python dependencies
├── Jenkinsfile                     # Jenkins pipeline definition
├── docker-compose.yml              # Docker orchestration
│
├── jenkins/
│   ├── Dockerfile                  # Custom Jenkins image
│   └── docker-compose.yml          # Jenkins container setup
│
└── ansible/
    ├── ansible.cfg                 # Ansible configuration
    ├── inventory                   # Server list
    │
    ├── playbooks/
    │   ├── ansible.yaml            # Main deployment playbook
    │   └── install_nginx.yaml      # Nginx installation
    │
    └── roles/
        ├── bootstrap/              # User setup & SSH keys
        │   └── tasks/
        │       └── main.yaml
        ├── common/                 # Docker installation
        │   └── tasks/
        │       └── main.yaml
        └── backend/                # Application deployment
            ├── tasks/
            │   └── main.yaml
            └── files/
                ├── flask-api/
                │   └── docker-compose.yml
                └── sudoer_simone
```

## 🚀 Hướng dẫn cài đặt

### 1. Cài đặt Jenkins

```bash
# Build và chạy Jenkins container
cd jenkins/
docker-compose up -d

# Lấy initial admin password
docker exec jenkins_container cat /var/jenkins_home/secrets/initialAdminPassword
```

**Cấu hình Jenkins:**
- Truy cập: `http://localhost:8080`
- Cài đặt plugins: Ansible Plugin, Docker Pipeline
- Thêm credentials:
  - Docker Hub: username/password
  - Ansible SSH: private key

### 2. Setup Ansible

```bash
# Cài đặt Ansible
sudo apt install ansible -y

# Tạo SSH key pair
ssh-keygen -t ed25519 -f ~/.ssh/ansible

# Copy public key đến managed nodes
ssh-copy-id -i ~/.ssh/ansible.pub simone@192.168.56.10
```

### 3. Cấu hình Ansible

**File: `ansible/ansible.cfg`**
```ini
[defaults]
inventory = inventory
private_key_file = ~/.ssh/ansible
ansible_user = simone
```

**File: `ansible/inventory`**
```ini
[web]
192.168.56.10
```

### 4. Test kết nối

```bash
# Ping all hosts
ansible all -m ping

# Gather facts
ansible all -m gather_facts

# List inventory
ansible-inventory -i ./inventory --list
```

## 🔄 Pipeline CI/CD

### Jenkins Pipeline Stages

#### **1. Clone Repository**
```groovy
stage('Clone Repository') {
    steps {
        checkout scm
    }
}
```
Tải code mới nhất từ GitHub repository.

#### **2. Build Docker Image**
```groovy
stage('Build Docker Image') {
    steps {
        sh "docker build -t ${IMAGE_NAME} ."
    }
}
```
Build Docker image với tag version cụ thể.

#### **3. Run Tests**
```groovy
stage('Run Tests') {
    steps {
        sh "docker run --rm ${IMAGE_NAME} python -m unittest discover"
    }
}
```
Chạy unit tests bên trong container. Nếu test fail, pipeline sẽ dừng lại.

#### **4. Push to Docker Hub**
```groovy
stage('Push to Docker Hub') {
    steps {
        withCredentials([usernamePassword(...)]) {
            sh 'docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD'
            sh "docker push ${IMAGE_NAME}"
        }
    }
}
```
Đẩy image lên Docker Hub để sẵn sàng deploy.

#### **5. Deploy với Ansible**
```groovy
stage('Deploy web server') {
    steps {
        ansiblePlaybook(
            credentialsId: 'ansible',
            inventory: './ansible/inventory',
            playbook: './ansible/playbooks/ansible.yaml'
        )
    }
}
```
Tự động deploy lên production servers.

### Trigger Options

#### **Push (Webhook) - Recommended**
```
GitHub → Webhook → Jenkins (instant trigger)
```
- Phản hồi nhanh, gần như tức thời
- Cần public Jenkins URL (dùng ngrok cho local)

#### **Pull (Polling)**
```
Jenkins kiểm tra GitHub mỗi phút
```
- Dễ cấu hình
- Tốn tài nguyên, có độ trễ

## 📦 Ansible Playbooks

### Main Deployment Playbook

**File: `playbooks/ansible.yaml`**

```yaml
- hosts: all
  become: true
  tasks:
    - name: Update apt cache
      apt:
        update_cache: true
      when: ansible_os_family == "Ubuntu"

- hosts: all
  become: true
  roles:
    - ../roles/bootstrap    # Tạo user và SSH
    - ../roles/common       # Cài Docker
    - ../roles/backend      # Deploy app
```

### Role: Bootstrap (User Setup)

**Nhiệm vụ:**
- Tạo user `simone` với quyền sudo
- Copy SSH public key
- Cấu hình sudoers (NOPASSWD)

**File: `roles/bootstrap/files/sudoer_simone`**
```
simone ALL=(ALL) NOPASSWD: ALL
```

### Role: Common (Docker Installation)

**Cài đặt:**
- Docker Engine
- Docker Compose Plugin
- Containerd

**Verify:**
```yaml
- name: Check Docker version
  shell: docker --version

- name: Check Docker Compose version
  shell: docker compose version
```

### Role: Backend (Application Deployment)

**Workflow:**
1. Check và dừng container cũ nếu có
2. Xóa thư mục cũ
3. Tạo thư mục mới
4. Copy docker-compose.yml
5. Chạy `docker compose up -d`

**Zero Downtime với Serial:**
```yaml
- hosts: web
  serial: "50%"  # Deploy 50% servers trước
  roles:
    - backend
```

## 🔧 Troubleshooting

### Lỗi Permission Denied

**Nguyên nhân:** Jenkins không có quyền truy cập SSH

**Giải pháp:**
```bash
# 1. Tạo user chung trên managed node
sudo adduser simone
sudo usermod -aG sudo simone

# 2. Tạo SSH key mới
ssh-keygen -t ed25519 -f ~/.ssh/ansible

# 3. Copy key
ssh-copy-id -i ~/.ssh/ansible.pub simone@192.168.56.10

# 4. Add private key vào Jenkins credentials
```

### Docker compose command not found

**Nguyên nhân:** Dùng `docker-compose` thay vì `docker compose`

**Giải pháp:**
```yaml
# Old syntax
- shell: docker-compose up -d

# New syntax (v2)
- shell: docker compose up -d
```

### Ansible cannot find inventory

**Kiểm tra:**
```bash
# Test inventory path
ansible-inventory -i ./ansible/inventory --list

# Check ansible.cfg
cat ansible/ansible.cfg
```

### Test failed in pipeline

**Debug:**
```bash
# Run tests locally
docker run --rm vdtry06/flask-sum-api:2.1 python -m unittest discover

# Check test file
cat test_app.py
```

**Demo lỗi có chủ đích:**
```python
# app.py - thay + bằng *
return jsonify({'result': num1 * num2})  # ❌ Test sẽ fail
```

Jenkins sẽ báo lỗi và ngăn merge code lỗi vào main branch.

## 📝 Useful Commands

### Jenkins
```bash
# Restart Jenkins
docker restart jenkins_container

# View logs
docker logs -f jenkins_container

# Access Jenkins CLI
docker exec -it jenkins_container bash
```

### Ansible
```bash
# Run specific playbook
ansible-playbook playbooks/ansible.yaml -K

# Run with tags
ansible-playbook playbooks/install_nginx.yaml -t frontend -K

# Check syntax
ansible-playbook --syntax-check playbooks/ansible.yaml

# Dry run
ansible-playbook --check playbooks/ansible.yaml
```

### Docker
```bash
# Build image
docker build -t vdtry06/flask-sum-api:2.1 .

# Run container
docker run -p 5000:5000 vdtry06/flask-sum-api:2.1

# Test API
curl "http://localhost:5000/add?num1=3&num2=5"
```

## 🎓 Kiến thức mở rộng

### Các công cụ CI/CD khác
- **GitHub Actions**: Tích hợp sẵn với GitHub
- **GitLab CI/CD**: Chạy trực tiếp trên cloud
- **CircleCI, Travis CI**: Cloud-based CI/CD

### Best Practices
1. **Secrets Management**: Không hard-code credentials trong code
2. **Immutable Infrastructure**: Xây dựng image mới thay vì update
3. **Health Checks**: Kiểm tra service sau khi deploy
4. **Rollback Strategy**: Luôn có kế hoạch rollback
5. **Monitoring**: Setup logging và alerting

### Tính năng nâng cao
- **Blue-Green Deployment**: Chạy 2 môi trường song song
- **Canary Deployment**: Deploy dần dần cho một phần users
- **Multi-stage Pipeline**: Dev → Staging → Production
- **Automated Rollback**: Tự động rollback khi phát hiện lỗi

**Happy Automating! 🚀**