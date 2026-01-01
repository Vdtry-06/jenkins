FROM jenkins/jenkins:lts

USER root

# Install Docker and Ansible dependencies
RUN apt-get update && \
    apt-get install -y docker.io python3 python3-pip sshpass && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Ansible
RUN pip3 install ansible --break-system-packages

# Configure Docker group
ARG DOCKER_GID=108
RUN groupmod -g ${DOCKER_GID} docker && \   
    usermod -aG docker jenkins

USER jenkins