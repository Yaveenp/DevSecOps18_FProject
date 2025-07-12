pipeline {
    agent any

    environment {
        APP_NAME = 'financial-portfolio'
        BACKEND_IMAGE = "yaveenp/investment-flask:${BUILD_NUMBER}"
        FRONTEND_IMAGE = "yaveenp/investment-frontend:${BUILD_NUMBER}"
        KUBE_NAMESPACE = "financial-portfolio"
        DOCKER_REPO = "yaveenp"
    }

    stages {
        stage('Lint Flask and React Code') {
            agent {
                docker {
                    image 'python:3.10'
                }
            }
            steps {
                script {
                    echo "=== Starting Lint Flask and React Code Stage ==="
                    echo "--- Installing Python dependencies ---"
                    sh 'sudo pip install --no-cache-dir -r app/Backend/requirements.txt'
                    
                    echo "--- Linting Flask code ---"
                    sh 'flake8 app/Backend/main.py app/Backend/Financial_Portfolio_Tracker/'

                    echo "--- Installing Node.js & Linting React code ---"
                    sh '''
                        sudo apt-get update && apt-get install -y npm
                        sudo npm install --prefix app/Frontend
                        sudo npm run lint --prefix app/Frontend
                    '''
                }
            }
        }

        stage('Run Unit Tests for Backend') {
            agent {
                docker {
                    image 'python:3.10'
                }
            }
            steps {
                script {
                    echo "=== Starting Run Unit Tests for Backend Stage ==="
                    sh 'pytest app/Backend/'
                }
            }
        }

        stage('Build and Push Docker Images') {
            agent any
            steps {
                script {
                    echo "=== Starting Build and Push Docker Images Stage ==="
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-cred-yaveen', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'
                    }

                    echo "--- Building and pushing backend image ---"
                    sh "docker buildx build --platform linux/amd64,linux/arm64 -t ${BACKEND_IMAGE} -f app/Backend/flask-dockerfile --push ."

                    echo "--- Building and pushing frontend image ---"
                    sh "docker buildx build --platform linux/amd64,linux/arm64 -t ${FRONTEND_IMAGE} -f app/Frontend/Dockerfile --push ."
                }
            }
        }

        stage('Deploy to Minikube or EKS') {
            agent any
            steps {
                script {
                    echo "=== Starting Deploy to Kubernetes Stage ==="
                    sh "kubectl apply -f Postgres/postgres-secret.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f Postgres/postgres-configmap.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/flask/flask-secret.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/Monitoring/prometheus-configmap.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/Monitoring/grafana-datasource-configmap.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/Monitoring/grafana-dashboard-configmap.yaml -n ${KUBE_NAMESPACE}"

                    echo "--- Applying node-exporter DaemonSet and Service ---"
                    sh "kubectl apply -f kubernetes/Monitoring/node-exporter-daemonset.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/Monitoring/node-exporter-service.yaml -n ${KUBE_NAMESPACE}"

                    echo "--- Deploying app ---"
                    sh "kubectl apply -f Postgres/postgres-deployment.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f Postgres/postgres-service.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/flask/flask-deployment.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/flask/flask-service.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/Frontend/frontend-deployment.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/Frontend/frontend-service.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/ingress.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/ingress-nginx-controller.yaml"

                    echo "--- Kubernetes resource status ---"
                    sh "kubectl get configmap,secret -n ${KUBE_NAMESPACE}"
                    sh "kubectl get pv,pvc -n ${KUBE_NAMESPACE}"
                    sh "kubectl get deployments,pods -n ${KUBE_NAMESPACE}"
                    sh "kubectl get services -n ${KUBE_NAMESPACE}"
                    sh "kubectl get ingress -n ${KUBE_NAMESPACE}"
                    sh "kubectl get all -n ${KUBE_NAMESPACE}"
                }
            }
        }

        stage('Run Prometheus and Grafana') {
            agent any
            steps {
                script {
                    echo "=== Starting Run Prometheus and Grafana Stage ==="
                    sh "kubectl apply -f kubernetes/Monitoring/prometheus-deployment.yaml"
                    sh "kubectl apply -f kubernetes/Monitoring/grafana-deployment.yaml"
                }
            }
        }

        stage('Perform API Testing') {
            agent {
                docker {
                    image 'python:3.10'
                }
            }
            steps {
                script {
                    echo "=== Starting Perform API Testing Stage ==="
                    sh 'pip install --no-cache-dir -r app/Backend/requirements.txt'
                    sh 'pytest app/Backend/tests/api_tests.py'
                }
            }
        }
    }

    post {
        always {
            echo "=== Pipeline Complete: Cleaning up Docker resources ==="
            sh 'docker system prune -f || true'
            echo "=== Pipeline Complete: Cleaning up Workspace ==="
            sh 'rm -rf $WORKSPACE/*'
        }
    }
}