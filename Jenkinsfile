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
            steps {
                script {
                    echo "=== Starting Lint Flask and React Code Stage ==="
                    // Linting Flask code for style and errors
                    echo "--- Linting Flask code ---"
                    sh 'flake8 app/Backend/main.py app/Backend/Financial_Portfolio_Tracker/'

                    // Linting React code for style and errors
                    echo "--- Linting React code ---"
                    sh 'npm install --prefix app/Frontend'
                    sh 'npm run lint --prefix app/Frontend'
                }
            }
        }

        stage('Run Unit Tests for Backend') {
            steps {
                script {
                    echo "=== Starting Run Unit Tests for Backend Stage ==="
                    // Install Python dependencies and run backend tests
                    echo "--- Installing Python dependencies ---"
                    sh 'pip install -r app/Backend/requirements.txt'
                    echo "--- Running backend tests ---"
                    sh 'pytest app/Backend/'
                }
            }
        }

        stage('Build and Push Docker Images') {
            steps {
                script {
                    echo "=== Starting Build and Push Docker Images Stage ==="
                    // Login to Docker Hub using credentials
                    echo "--- Logging in to Docker Hub ---"
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-cred-yaveen', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh '''
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        '''
                    }
                    // Build and push multi-arch Docker images for backend and frontend
                    echo "--- Building and pushing backend image ---"
                    sh "docker buildx build --platform linux/amd64,linux/arm64 -t ${BACKEND_IMAGE} -f app/Backend/flask-dockerfile --push ."
                    echo "--- Building and pushing frontend image ---"
                    sh "docker buildx build --platform linux/amd64,linux/arm64 -t ${FRONTEND_IMAGE} -f app/Frontend/Dockerfile --push ."
                }
            }
        }

        stage('Deploy to Minikube or EKS') {
            steps {
                script {
                    echo "=== Starting Deploy to Minikube or EKS Stage ==="
                    // Apply Secrets and ConfigMaps to Kubernetes
                    echo "--- Applying Secrets and ConfigMaps ---"
                    sh "kubectl apply -f Postgres/postgres-secret.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f Postgres/postgres-configmap.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/flask/flask-secret.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/Monitoring/prometheus-configmap.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/Monitoring/grafana-datasource-configmap.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/Monitoring/grafana-dashboard-configmap.yaml -n ${KUBE_NAMESPACE}"

                    // Apply node-exporter DaemonSet and Service for node-level metrics
                    echo "--- Applying node-exporter DaemonSet and Service ---"
                    sh "kubectl apply -f kubernetes/Monitoring/node-exporter-daemonset.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/Monitoring/node-exporter-service.yaml -n ${KUBE_NAMESPACE}"

                    // Deploy application manifests to Kubernetes
                    echo "--- Deploying application manifests ---"
                    sh "kubectl apply -f Postgres/postgres-deployment.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f Postgres/postgres-service.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/flask/flask-deployment.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/flask/flask-service.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/Frontend/frontend-deployment.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/Frontend/frontend-service.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/ingress.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f kubernetes/ingress-nginx-controller.yaml"

                    // Check Kubernetes resource status
                    echo "--- Checking Kubernetes resource status ---"
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
            steps {
                script {
                    echo "=== Starting Run Prometheus and Grafana Stage ==="
                    // Deploy monitoring tools
                    echo "--- Deploying Prometheus ---"
                    sh "kubectl apply -f kubernetes/Monitoring/prometheus-deployment.yaml"
                    echo "--- Deploying Grafana ---"
                    sh "kubectl apply -f kubernetes/Monitoring/grafana-deployment.yaml"
                }
            }
        }

        stage('Perform API Testing') {
            steps {
                script {
                    echo "=== Starting Perform API Testing Stage ==="
                    // Run API tests against the live deployment
                    echo "--- Running API tests ---"
                    sh 'pytest app/Backend/tests/api_tests.py'
                }
            }
        }
    }

    post {
        always {
            echo "=== Pipeline Complete: Cleaning up Docker resources ==="
            sh 'docker system prune -f'
        }
    }
}