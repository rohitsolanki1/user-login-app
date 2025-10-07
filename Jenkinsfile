pipeline {
  agent any

  environment {
    REGISTRY = "localhost:32000"
    PROJECT = "user-login-app"
    K8S_NS = "user-login-app"
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Build Backend Image') {
      steps {
        dir('backend') {
          sh "docker build -t ${REGISTRY}/${PROJECT}/backend:${BUILD_NUMBER} ."
          sh "docker push ${REGISTRY}/${PROJECT}/backend:${BUILD_NUMBER}"
        }
      }
    }

    stage('Build Frontend Image') {
      steps {
        dir('frontend') {
          sh "docker build -t ${REGISTRY}/${PROJECT}/frontend:${BUILD_NUMBER} ."
          sh "docker push ${REGISTRY}/${PROJECT}/frontend:${BUILD_NUMBER}"
        }
      }
    }

    stage('Deploy to K8s') {
      steps {
        sh "microk8s.kubectl -n ${K8S_NS} set image deployment/backend backend=${REGISTRY}/${PROJECT}/backend:${BUILD_NUMBER} || microk8s.kubectl -n ${K8S_NS} rollout restart deployment/backend"
        sh "microk8s.kubectl -n ${K8S_NS} set image deployment/frontend frontend=${REGISTRY}/${PROJECT}/frontend:${BUILD_NUMBER} || microk8s.kubectl -n ${K8S_NS} rollout restart deployment/frontend"
      }
    }
  }

  post {
    success { echo "Deployed ${BUILD_NUMBER}" }
    failure { echo "Build failed" }
  }
}
