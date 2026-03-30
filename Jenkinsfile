pipeline {
    agent any

    environment {
        IMAGE_NAME = "508262720940.dkr.ecr.ap-northeast-1.amazonaws.com/moveinsync:1"
        AWS_REGION = "ap-northeast-1"
    }

    stages {
        stage('Git Checkout') {
            steps {
                git url: 'https://github.com/ManojKRISHNAPPA/MoveInSync.git', branch: 'main'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t moveinsync .'
            }
        }

        stage('ECR Login') {
            steps {
                sh '''
                aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin 508262720940.dkr.ecr.$AWS_REGION.amazonaws.com
                '''
            }
        }

        stage('Tag for ECR') {
            steps {
                sh "docker tag moveinsync:latest $IMAGE_NAME"
            }
        }

        stage('Push to ECR') {
            steps {
                sh "docker push $IMAGE_NAME"
            }
        }
    }

    post {
        always {
            sh "docker rmi $IMAGE_NAME || true"
            sh "docker logout || true"
        }
        success {
            echo "Build and push successful: $IMAGE_NAME"
        }
        failure {
            echo "Pipeline failed. Check the logs above."
        }
    }
}