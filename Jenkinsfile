pipeline {
    agent any

    environment {
        REGISTRY = "localhost:31000"
        APP_NAME = "user-login-app"
        KUBE_NAMESPACE = "user-login-app"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/yourname/user-login-app.git'
            }
        }

        stage('Build Docker Images') {
            steps {
                sh 'docker build -t $REGISTRY/$APP_NAME-backend:latest backend/'
                sh 'docker build -t $REGISTRY/$APP_NAME-frontend:latest frontend/'
            }
        }

        stage('Push to Local Registry') {
            steps {
                sh 'docker push $REGISTRY/$APP_NAME-backend:latest'
                sh 'docker push $REGISTRY/$APP_NAME-frontend:latest'
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh 'microk8s kubectl apply -f k8s/ -n $KUBE_NAMESPACE'
            }
        }
    }
}
