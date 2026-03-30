pipeline {
    agent any

    environment {
        AWS_REGION = "ap-northeast-1"
        // Use Jenkins build number if exists, otherwise use short Git commit hash
        IMAGE_TAG = "${env.BUILD_NUMBER ?: sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()}"
        IMAGE_NAME = "508262720940.dkr.ecr.ap-northeast-1.amazonaws.com/moveinsync:${IMAGE_TAG}"
    }

    stages {

        stage('Git Checkout') {
            steps {
                git url: 'https://github.com/ManojKRISHNAPPA/MoveInSync.git', branch: 'main'
            }
        }

        stage('Docker Build') {
            steps {
                sh "docker build -t moveinsync ."
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

        stage('Update GitOps Deployment') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-creds',
                    usernameVariable: 'GIT_USERNAME',
                    passwordVariable: 'GIT_PASSWORD'
                )]) {
                    sh '''
                        set -e
                        # Remove old folder if exists
                        if [ -d "MoveInSync-gitops" ]; then
                            rm -rf MoveInSync-gitops
                        fi

                        # Clone GitOps repo
                        git clone https://$GIT_USERNAME:$GIT_PASSWORD@github.com/ManojKRISHNAPPA/MoveInSync-gitops.git MoveInSync-gitops
                        cd MoveInSync-gitops/

                        git config user.email "jenkins@ci.com"
                        git config user.name "jenkins"

                        # Update image tag in deployment.yaml
                        sed -i "s|image: .*moveinsync.*|image: ${IMAGE_NAME}|g" deployment.yaml

                        # Commit only if there are changes
                        if ! git diff --quiet; then
                            git add deployment.yaml
                            git commit -m "Update moveinsync image to ${IMAGE_NAME}"
                            git push origin main
                            echo "GitOps repo updated successfully!"
                        else
                            echo "No changes detected in deployment.yaml. Skipping commit."
                        fi
                    '''
                }
            }
        }
    }

    post {
        always {
            sh "docker rmi $IMAGE_NAME || true"
            sh "docker logout || true"
        }
        success {
            echo "Build, push, and GitOps update successful: $IMAGE_NAME"
        }
        failure {
            echo "Pipeline failed. Check the logs above."
        }
    }
}