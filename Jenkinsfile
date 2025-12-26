pipeline {
    agent any

    environment {
        DOCKER_USERNAME = 'vdtry06'
        DOCKER_HUB_CREDENTIALS = 'docker-acc'
        IMAGE_NAME = "${DOCKER_USERNAME}/flask-sum-api:1.0"
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
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-acc', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                    sh 'docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD'
                }
                sh "docker push ${IMAGE_NAME}"
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