pipeline {
    options {
        timeout(time: 40, unit: 'MINUTES')
    }
    agent any

    environment {
        APP_NAME = 'financial-portfolio'
        BACKEND_IMAGE = "yaveenp/investment-flask:${BUILD_NUMBER}"
        FRONTEND_IMAGE = "yaveenp/investment-frontend:${BUILD_NUMBER}"
        KUBE_NAMESPACE = "financial-portfolio"
        DOCKER_REPO = "yaveenp"
    }

    stages {
        stage('Lint Code') {
            parallel {
        stage('Lint Flask Code') {
            agent {
                docker {
                    image 'python:3.10'
                    args '-u root --label pipeline=${APP_NAME}'
                }
            }
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    echo "=== Starting Lint Flask Code Stage ==="
                    sh '''
                        apt-get update
                        apt-get install -y python3-venv
                        chmod -R 777 .
                        python3 -m venv --copies venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install flake8
                        flake8 app/Backend/main.py app/Backend/Financial_Portfolio_Tracker/ > lint_flask.log 2>&1 || true
                    '''
                }
            }
        }
        stage('Lint React Code') {
            agent {
                docker {
                    image 'node:20-bullseye'
                    args '-u root --label pipeline=${APP_NAME}'
                }
            }
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    echo "=== Starting Lint React Code Stage ==="
                    sh '''
                        npm install --prefix app/Frontend
                        npm run lint --prefix app/Frontend > lint_react.log 2>&1 || true
                    '''
                }
            }
        }
            }
        }
        

        stage('Build and Push Docker Images') {
            agent {
                docker {
                    image 'docker:24.0.0-dind'
                    args '-u root --privileged -v /var/run/docker.sock:/var/run/docker.sock --label pipeline=${APP_NAME}'
                }
            }
            steps {
                timeout(time: 20, unit: 'MINUTES') {
                    script {
                        echo "=== Starting Build and Push Docker Images Stage ==="
                        # Install Buildx if not present
                        sh '''
                            if ! docker buildx version > /dev/null 2>&1; then
                              mkdir -p ~/.docker/cli-plugins/
                              wget https://github.com/docker/buildx/releases/download/v0.12.0/buildx-v0.12.0.linux-amd64 -O ~/.docker/cli-plugins/docker-buildx
                              chmod +x ~/.docker/cli-plugins/docker-buildx
                            fi
                        '''
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
        }

        stage('Deploy to Minikube or EKS') {
            agent {
                docker {
                    image 'ubuntu:22.04'
                    args '-u root --label pipeline=${APP_NAME}'
                }
            }
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    echo "=== Installing kubectl ==="
                    sh '''
                        apt-get clean
                        apt-get update
                        apt-get install -y apt-transport-https ca-certificates curl
                        curl -LO https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl
                        install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
                    '''
                    echo "=== Starting Deploy to Kubernetes Stage ==="
                    sh "kubectl apply -f ${WORKSPACE}/Postgres/postgres-secret.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/Postgres/postgres-configmap.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/flask/flask-secret.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/Monitoring/prometheus-configmap.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/Monitoring/grafana-datasource-configmap.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/Monitoring/grafana-dashboard-configmap.yaml -n ${KUBE_NAMESPACE}"

                    echo "--- Applying node-exporter DaemonSet and Service ---"
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/Monitoring/node-exporter-daemonset.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/Monitoring/node-exporter-service.yaml -n ${KUBE_NAMESPACE}"

                    echo "--- Deploying app ---"
                    sh "kubectl apply -f ${WORKSPACE}/Postgres/postgres-deployment.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/Postgres/postgres-service.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/flask/flask-deployment.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/flask/flask-service.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/Frontend/frontend-deployment.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/Frontend/frontend-service.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/ingress.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/ingress-nginx-controller.yaml"

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
                    args '--label pipeline=${APP_NAME}'
                }
            }
            steps {
                echo "=== Starting Perform API Testing Stage ==="
                sh 'pip install pytest requests'
                echo "--- Running API tests against deployed Kubernetes app ---"
                sh 'pytest app/Backend/tests/api_tests.py -v'
            }
        }
    }

    post {
        always {
            echo "=== Pipeline Complete: Cleaning up Docker images used by this pipeline ==="
            sh "docker rmi -f ${BACKEND_IMAGE} || true"
            sh "docker rmi -f ${FRONTEND_IMAGE} || true"
            echo "=== Pipeline Complete: Removing stopped containers with pipeline label ==="
            sh "docker container rm $(docker ps -a -q --filter \"label=pipeline=${APP_NAME}\" --filter \"status=exited\") || true"
            echo "=== Pipeline Complete: Cleaning up Workspace ==="
            sh 'rm -rf $WORKSPACE/*'
        }
    }
}