pipeline {
    agent any

    environment {
        REGISTRY = "localhost:32100"
        PROJECT = "user-login-app"
        BACKEND_IMAGE = "${REGISTRY}/${PROJECT}-backend:latest"
        FRONTEND_IMAGE = "${REGISTRY}/${PROJECT}-frontend:latest"
        NAMESPACE = "user-login-app"
    }

    stages {

        stage('Build Backend') {
            steps {
                script {
                    sh "docker build -t ${BACKEND_IMAGE} ./backend"
                }
            }
        }

        stage('Build Frontend') {
            steps {
                script {
                    sh "docker build -t ${FRONTEND_IMAGE} ./frontend"
                }
            }
        }

        stage('Push Backend Image') {
            steps {
                script {
                    sh "docker push ${BACKEND_IMAGE}"
                }
            }
        }

        stage('Push Frontend Image') {
            steps {
                script {
                    sh "docker push ${FRONTEND_IMAGE}"
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    // Apply manifests (create/update Services, PVC, Secrets, Ingress)
                    sh "microk8s kubectl apply -f k8s/ -n ${NAMESPACE}"

                    // Force rollout restart to pull latest images
                    sh "microk8s kubectl rollout restart deployment backend -n ${NAMESPACE}"
                    sh "microk8s kubectl rollout restart deployment frontend -n ${NAMESPACE}"
                }
            }
        }
    }

    post {
        success {
            echo "Deployment finished successfully! Visit the app to see changes."
        }
        failure {
            echo "Deployment failed. Check the logs."
        }
    }
}
