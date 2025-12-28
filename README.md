# test-jenkins
test-jenkins

getent group docker
docker:x:108:vdtry06

# Dừng server

```
- name: Install Nginx on web remote server
  hosts: web
  become: true # Use sudo to run tasks as root

  tasks:
    - name: Update list of apt packages (Just with Ubuntu/Debian)
      apt:
        update_cache: yes

    - name: Install Nginx (Ubuntu/Debian)
      apt:
        name: nginx
        state: absent
      when: ansible_os_family == "Debian"
    
    - name: Stop Nginx service (Ubuntu/Debian)
      service:
        name: nginx
        state: stopped
      when: ansible_os_family == "Debian"
      
```