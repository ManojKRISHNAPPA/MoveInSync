pipeline {
    agent any

    environment {
        AWS_REGION = "ap-northeast-1"
        IMAGE_TAG  = "${env.BUILD_NUMBER ?: sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()}"
        IMAGE_NAME = "508262720940.dkr.ecr.ap-northeast-1.amazonaws.com/moveinsync:${IMAGE_TAG}"
    }

    stages {

        // ── 1. Source ──────────────────────────────────────────────────────────
        stage('Git Checkout') {
            steps {
                git url: 'https://github.com/ManojKRISHNAPPA/MoveInSync.git', branch: 'main'
            }
        }

        // ── 2. Install dependencies ────────────────────────────────────────────
        stage('Install Dependencies') {
            steps {
                sh '''
                    pip install --quiet -r requirements.txt
                    pip install --quiet -r requirements-test.txt
                '''
            }
        }

        // ── 3. Unit tests + coverage ───────────────────────────────────────────
        stage('Unit Tests & Coverage') {
            steps {
                sh '''
                    pytest tests/ \
                        --cov=. \
                        --cov-report=xml:coverage.xml \
                        --cov-report=term-missing \
                        --junitxml=test-results.xml \
                        -v
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        // ── 4. SonarQube analysis ──────────────────────────────────────────────
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh 'sonar-scanner'
                }
            }
        }

        // ── 5. Quality Gate ────────────────────────────────────────────────────
        stage('Quality Gate') {
            steps {
                timeout(time: 2, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        // ── 6. Dependency vulnerability scan ──────────────────────────────────
        stage('Dependency Vulnerability Scan') {
            steps {
                sh '''
                    pip install --quiet pip-audit
                    pip-audit -r requirements.txt --format=json -o pip-audit-report.json || true
                    pip-audit -r requirements.txt
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'pip-audit-report.json', allowEmptyArchive: true
                }
            }
        }

        // ── 7. Security scans + Docker build (parallel) ───────────────────────
        stage('Security Scan & Docker Build') {
            parallel {

                stage('Trivy Base Image Scan') {
                    steps {
                        sh 'bash trivy-docker-image-scan.sh'
                    }
                }

                stage('OPA Dockerfile Rules') {
                    steps {
                        sh 'docker run --rm -v $(pwd):/project openpolicyagent/conftest test --policy dockerfile-security.rego Dockerfile'
                    }
                }

                stage('Docker Build') {
                    steps {
                        sh 'docker build -t moveinsync .'
                    }
                }
            }
        }

        // ── 8. ECR login ───────────────────────────────────────────────────────
        stage('ECR Login') {
            steps {
                sh '''
                    aws ecr get-login-password --region $AWS_REGION \
                        | docker login --username AWS --password-stdin \
                          508262720940.dkr.ecr.$AWS_REGION.amazonaws.com
                '''
            }
        }

        // ── 9. Tag & push ──────────────────────────────────────────────────────
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

        // ── 10. OPA Kubernetes rules ───────────────────────────────────────────
        stage('OPA Kubernetes Rules') {
            steps {
                sh 'docker run --rm -v $(pwd):/project openpolicyagent/conftest test --policy opa-k8s-security.rego deployment.yml'
            }
        }

        // ── 11. GitOps update ──────────────────────────────────────────────────
        stage('Update GitOps Deployment') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-creds',
                    usernameVariable: 'GIT_USERNAME',
                    passwordVariable: 'GIT_PASSWORD'
                )]) {
                    sh '''
                        set -e

                        if [ -d "MoveInSync-gitops" ]; then
                            rm -rf MoveInSync-gitops
                        fi

                        git clone https://$GIT_USERNAME:$GIT_PASSWORD@github.com/ManojKRISHNAPPA/MoveInSync-gitops.git MoveInSync-gitops
                        cd MoveInSync-gitops/moveinsync/

                        git config user.email "jenkins@ci.com"
                        git config user.name "jenkins"

                        sed -i "s|image: .*moveinsync.*|image: ${IMAGE_NAME}|g" deployment.yaml

                        if ! git diff --quiet; then
                            git add deployment.yaml
                            git commit -m "Update moveinsync image to ${IMAGE_NAME}"
                            git push origin main
                            echo "GitOps repo updated successfully!"
                        else
                            echo "No changes detected. Skipping commit."
                        fi
                    '''
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'coverage.xml,test-results.xml', allowEmptyArchive: true
            sh "docker rmi $IMAGE_NAME || true"
            sh "docker logout || true"
        }
        success {
            echo "Pipeline succeeded: ${IMAGE_NAME}"
        }
        failure {
            echo "Pipeline failed. Check the logs above."
        }
    }
}
