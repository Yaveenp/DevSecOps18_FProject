pipeline {
    agent any

    stages {
        stage('Lint Flask and React Code') {
            steps {
                script {
                    // Linting Flask code
                    sh 'flake8 app/Backend/main.py app/Backend/Financial_Portfolio_Tracker/'

                    // Linting React code
                    sh 'npm install --prefix app/Frontend'
                    sh 'npm run lint --prefix app/Frontend'
                }
            }
        }

        stage('Run Unit Tests for Backend') {
            steps {
                script {
                    // Install dependencies and run tests
                    sh 'pip install -r app/Backend/requirements.txt'
                    sh 'pytest app/Backend/'
                }
            }
        }

        stage('Build and Push Docker Images') {
            steps {
                script {
                    // Build Docker images
                    sh 'docker build -t your_dockerhub_username/devsecops18_backend:latest -f Docker/Dockerfile_backend .'
                    sh 'docker build -t your_dockerhub_username/devsecops18_frontend:latest -f Docker/Dockerfile_frontend .'

                    // Push Docker images to Docker Hub
                    sh 'docker push your_dockerhub_username/devsecops18_backend:latest'
                    sh 'docker push your_dockerhub_username/devsecops18_frontend:latest'
                }
            }
        }

        stage('Deploy to Minikube or EKS') {
            steps {
                script {
                    // Deploy using Kubernetes manifests
                    sh 'kubectl apply -f Postgres/postgres-deployment.yaml'
                    sh 'kubectl apply -f Postgres/postgres-service.yaml'
                    sh 'kubectl apply -f Docker/docker-compose.yml'
                }
            }
        }

        stage('Run Prometheus and Grafana') {
            steps {
                script {
                    // Deploy Prometheus and Grafana
                    sh 'kubectl apply -f path_to_prometheus_manifest.yaml'
                    sh 'kubectl apply -f path_to_grafana_manifest.yaml'
                }
            }
        }

        stage('Perform API Testing') {
            steps {
                script {
                    // Run API tests against the live deployment
                    sh 'pytest app/Backend/tests/api_tests.py'
                }
            }
        }
    }

    post {
        always {
            // Clean up resources
            sh 'docker system prune -f'
        }
    }
}