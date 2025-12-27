pipeline {
    agent any

    environment {
        DOCKER_USERNAME = 'vdtry06'
        DOCKER_HUB_CREDENTIALS = 'dockerhub-acc'
        IMAGE_NAME = "${DOCKER_USERNAME}/flask-sum-api:2.0"
        CONTAINER_NAME = "flask-test-container"
    }

    stages {
        stage('Clone Repository') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t ${IMAGE_NAME} ."
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    sh "docker run --rm ${IMAGE_NAME} python -m unittest discover -s /app -p 'test_*.py'"
                }
            }
        }

        stage('Push to Docker Hub') {
            when {
                expression { env.DOCKER_HUB_CREDENTIALS != '' }
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: "${DOCKER_HUB_CREDENTIALS}", 
                    usernameVariable: 'DOCKER_USERNAME', 
                    passwordVariable: 'DOCKER_PASSWORD'
                )]) {
                    sh 'echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin'
                    sh "docker push ${IMAGE_NAME}"
                }
            }
        }

        stage('Deploy web server') {
            steps {
                ansiblePlaybook credentialsId: 'ansible',
                                disableHostKeyChecking: true,
                                installation: 'ansible',
                                inventory: './ansible/inventory',
                                playbook: './ansible/playbooks/ansible.yaml'
            }
        }
    }

    post {
        always {
            echo "Job Completed! Cleaning up resources..."
        }
        success {
            echo "Build & Test Passed. Image pushed to Docker Hub successfully!"
        }
        failure {
            echo "Job failed. Cleaning up unused Docker resources..."
        }
    }
}
