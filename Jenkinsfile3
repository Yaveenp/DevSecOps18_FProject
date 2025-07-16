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
        stage('Setup Build Environment') {
            steps {
                script {
                    sh '''
                        if ! command -v curl >/dev/null 2>&1; then
                            while fuser /var/lib/apt/lists/lock >/dev/null 2>&1; do
                                echo "Waiting for other apt-get processes to finish..."
                                sleep 5
                            done
                            apt-get update
                            apt-get install -y curl
                        fi
                        echo "=== Setting up build environment ==="
                        if [ ! -f "/usr/local/bin/kubectl" ]; then
                            echo "kubectl not found in /usr/local/bin. Downloading..."
                            curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                            chmod +x kubectl
                            sudo mv kubectl /usr/local/bin/kubectl
                        else
                            echo "kubectl already exists in /usr/local/bin."
                        fi
                        /usr/local/bin/kubectl version --client || {
                            echo "Failed to verify kubectl installation."
                            exit 1
                        }
                    '''
                }
            }
        }

        stage('Lint Code') {
            parallel {
                stage('Lint Flask') {
                    steps {
                        catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                            sh '''
                                while fuser /var/lib/apt/lists/lock >/dev/null 2>&1; do
                                    echo "Waiting for other apt-get processes to finish..."
                                    sleep 5
                                done
                                apt-get update
                                apt-get install -y python3-venv
                                python3 -m venv venv
                                . venv/bin/activate
                                pip install --upgrade pip flake8
                                touch lint_flask.log
                                if [ -f "app/Backend/main.py" ] || [ -d "app/Backend/Financial_Portfolio_Tracker/" ]; then
                                    flake8 app/Backend/ > lint_flask.log 2>&1 || echo "Flake8 found issues"
                                else
                                    echo "Backend files not found" > lint_flask.log
                                fi
                                cat lint_flask.log
                            '''
                            archiveArtifacts artifacts: 'lint_flask.log', allowEmptyArchive: true
                        }
                    }
                }
                stage('Lint React') {
                    steps {
                        catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                            sh '''
                                if ! command -v npm &> /dev/null; then
                                    echo "Installing npm..."
                                    apt-get install -y npm || {
                                        curl -L https://www.npmjs.com/install.sh | sh
                                    }
                                fi
                                echo "Node version: $(node --version || echo 'Not installed')"
                                echo "NPM version: $(npm --version || echo 'Not installed')"
                                touch lint_react.log
                                if [ -d "app/Frontend" ]; then
                                    cd app/Frontend
                                    if [ -f "package.json" ]; then
                                        npm install
                                        if grep -q '"lint"' package.json; then
                                            npm run lint > ${WORKSPACE}/lint_react.log 2>&1 || echo "ESLint found issues"
                                        else
                                            echo "No lint script found in package.json" > ${WORKSPACE}/lint_react.log
                                            echo "Available scripts:" >> ${WORKSPACE}/lint_react.log
                                            npm run >> ${WORKSPACE}/lint_react.log 2>&1
                                        fi
                                    else
                                        echo "No package.json found in app/Frontend" > ${WORKSPACE}/lint_react.log
                                    fi
                                else
                                    echo "Frontend directory not found" > ${WORKSPACE}/lint_react.log
                                fi
                                cat ${WORKSPACE}/lint_react.log
                            '''
                            archiveArtifacts artifacts: 'lint_react.log', allowEmptyArchive: true
                        }
                    }
                }
            }
        }

        stage('Build and Push Docker Images') {
            agent {
                docker {
                    image 'docker:24.0.0-dind'
                    args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            options {
                timeout(time: 20, unit: 'MINUTES')
            }
            steps {
                script {
                    sh '''
                        if ! docker buildx version > /dev/null 2>&1; then
                          mkdir -p ~/.docker/cli-plugins/
                          wget https://github.com/docker/buildx/releases/download/v0.12.0/buildx-v0.12.0.linux-amd64 -O ~/.docker/cli-plugins/docker-buildx
                          chmod +x ~/.docker/cli-plugins/docker-buildx
                        fi
                        docker buildx create --name mybuilder --use
                        docker buildx inspect --bootstrap
                    '''
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-cred-yaveen', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh '''
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        '''
                    }
                    sh '''
                        docker buildx build --platform linux/amd64,linux/arm64 -t ${BACKEND_IMAGE} -f app/Backend/flask-dockerfile --push app/Backend
                        docker buildx build --platform linux/amd64,linux/arm64 -t ${FRONTEND_IMAGE} -f app/Frontend/Dockerfile --push app/Frontend
                        sed -i 's|image: yaveenp/investment-flask:.*|image: ${BACKEND_IMAGE}|' ${WORKSPACE}/kubernetes/flask/flask-deployment.yaml
                        sed -i 's|image: yaveenp/investment-frontend:.*|image: ${FRONTEND_IMAGE}|' ${WORKSPACE}/kubernetes/Frontend/frontend-deployment.yaml
                    '''
                }
            }
        }

        stage('Prepare Kubernetes Resources') {
            agent {
                docker {
                    image 'ubuntu:22.04'
                    args '-u root --label pipeline=${APP_NAME}'
                }
            }
            options {
                timeout(time: 10, unit: 'MINUTES')
            }
            steps {
                sh '''
                    if ! command -v curl >/dev/null 2>&1; then
                        while fuser /var/lib/apt/lists/lock >/dev/null 2>&1; do
                            echo "Waiting for other apt-get processes to finish..."
                            sleep 5
                        done
                        apt-get update
                        apt-get install -y curl
                    fi
                    if [ ! -f "/usr/local/bin/kubectl" ]; then
                        echo "kubectl not found in /usr/local/bin. Downloading..."
                        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                        chmod +x kubectl
                        mv kubectl /usr/local/bin/kubectl
                    fi

                    /usr/local/bin/kubectl get ns ${KUBE_NAMESPACE} || /usr/local/bin/kubectl create ns ${KUBE_NAMESPACE}
                '''
                echo "=== Applying core Kubernetes resources ==="
                script {
                    def coreResources = [
                        "${WORKSPACE}/Postgres/postgres-configmap.yaml",
                        "${WORKSPACE}/kubernetes/flask/flask-secret.yaml",
                        "${WORKSPACE}/kubernetes/Monitoring/prometheus-configmap.yaml",
                        "${WORKSPACE}/kubernetes/Monitoring/grafana-datasource-configmap.yaml",
                        "${WORKSPACE}/kubernetes/Monitoring/grafana-dashboard-configmap.yaml",
                        "${WORKSPACE}/kubernetes/Monitoring/grafana-dashboard-provider-configmap.yaml",
                        "${WORKSPACE}/kubernetes/Monitoring/grafana-service.yaml",
                        "${WORKSPACE}/kubernetes/Monitoring/prometheus-service.yaml",
                        "${WORKSPACE}/kubernetes/Monitoring/node-exporter-daemonset.yaml",
                        "${WORKSPACE}/kubernetes/Monitoring/node-exporter-service.yaml",
                        "${WORKSPACE}/kubernetes/ingress.yaml",
                        "${WORKSPACE}/kubernetes/ingress-nginx-controller.yaml"
                    ]
                    for (res in coreResources) {
                        sh '''
                            if ! command -v curl >/dev/null 2>&1; then
                                while fuser /var/lib/apt/lists/lock >/dev/null 2>&1; do
                                    echo "Waiting for other apt-get processes to finish..."
                                    sleep 5
                                done
                                apt-get update
                                apt-get install -y curl
                            fi
                            if [ ! -f "/usr/local/bin/kubectl" ]; then
                                echo "kubectl not found in /usr/local/bin. Downloading..."
                                curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                                chmod +x kubectl
                                mv kubectl /usr/local/bin/kubectl
                            fi
                            if [ -f "${res}" ]; then
                                echo 'Applying: ${res}'
                                /usr/local/bin/kubectl apply -f "${res}" -n ${KUBE_NAMESPACE}
                            else
                                echo 'WARNING: Missing resource file: ${res}'
                            fi
                        '''
                    }
                }
                sh '''
                    for i in {1..6}; do
                        if ! command -v curl >/dev/null 2>&1; then
                            while fuser /var/lib/apt/lists/lock >/dev/null 2>&1; do
                                echo "Waiting for other apt-get processes to finish..."
                                sleep 5
                            done
                            apt-get update
                            apt-get install -y curl
                        fi
                        if [ ! -f "/usr/local/bin/kubectl" ]; then
                            echo "kubectl not found in /usr/local/bin. Downloading..."
                            curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                            chmod +x kubectl
                            mv kubectl /usr/local/bin/kubectl
                        fi
                        NOT_READY=$(/usr/local/bin/kubectl get pods -n ${KUBE_NAMESPACE} --no-headers | grep -v "Running" | grep -v "Completed" | wc -l)
                        if [ "$NOT_READY" -eq 0 ]; then
                            echo "All pods are running and ready."
                            exit 0
                        fi
                        echo "Waiting for pods to be ready... ($i/6)"
                        /usr/local/bin/kubectl get pods -n ${KUBE_NAMESPACE}
                        sleep 20
                    done
                    echo "Some pods are not ready."
                    /usr/local/bin/kubectl get pods -n ${KUBE_NAMESPACE}
                    exit 1
                '''
            }
        }

        stage('Deploy Application') {
            options {
                timeout(time: 10, unit: 'MINUTES')
            }
            agent {
                docker {
                    image 'ubuntu:22.04'
                    args '-u root --label pipeline=${APP_NAME}'
                }
            }
            steps {
                sh '''
                    # Wait for apt lock and install curl if missing
                    while fuser /var/lib/apt/lists/lock >/dev/null 2>&1; do
                        echo "Waiting for other apt-get processes to finish..."
                        sleep 5
                    done
                    if ! command -v curl >/dev/null 2>&1; then
                        apt-get update
                        apt-get install -y curl
                    fi
                    if [ ! -f "/usr/local/bin/kubectl" ]; then
                        echo "kubectl not found in /usr/local/bin. Downloading..."
                        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                        chmod +x kubectl
                        mv kubectl /usr/local/bin/kubectl
                    fi

                    # Apply deployments BEFORE setting images
                    /usr/local/bin/kubectl apply -f ${WORKSPACE}/kubernetes/flask/flask-deployment.yaml -n ${KUBE_NAMESPACE}
                    /usr/local/bin/kubectl apply -f ${WORKSPACE}/kubernetes/Frontend/frontend-deployment.yaml -n ${KUBE_NAMESPACE}

                    /usr/local/bin/kubectl set image deployment/flask-deployment flask-app=${BACKEND_IMAGE} -n ${KUBE_NAMESPACE}
                    /usr/local/bin/kubectl rollout status deployment/flask-deployment -n ${KUBE_NAMESPACE}
                    /usr/local/bin/kubectl set image deployment/frontend-deployment frontend=${FRONTEND_IMAGE} -n ${KUBE_NAMESPACE}
                    /usr/local/bin/kubectl rollout status deployment/frontend-deployment -n ${KUBE_NAMESPACE}

                    /usr/local/bin/kubectl apply -f ${WORKSPACE}/kubernetes/flask/flask-service.yaml -n ${KUBE_NAMESPACE}
                    /usr/local/bin/kubectl apply -f ${WORKSPACE}/kubernetes/Frontend/frontend-service.yaml -n ${KUBE_NAMESPACE}

                    for i in {1..6}; do
                        while fuser /var/lib/apt/lists/lock >/dev/null 2>&1; do
                            echo "Waiting for other apt-get processes to finish..."
                            sleep 5
                        done
                        if ! command -v curl >/dev/null 2>&1; then
                            apt-get update
                            apt-get install -y curl
                        fi
                        if [ ! -f "/usr/local/bin/kubectl" ]; then
                            echo "kubectl not found in /usr/local/bin. Downloading..."
                            curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                            chmod +x kubectl
                            mv kubectl /usr/local/bin/kubectl
                        fi
                        NOT_READY=$(/usr/local/bin/kubectl get pods -n ${KUBE_NAMESPACE} --no-headers | grep -v "Running" | grep -v "Completed" | wc -l)
                        if [ "$NOT_READY" -eq 0 ]; then
                            echo "All pods are running and ready."
                            exit 0
                        fi
                        echo "Waiting for pods to be ready... ($i/6)"
                        /usr/local/bin/kubectl get pods -n ${KUBE_NAMESPACE}
                        sleep 20
                    done
                    echo "Some pods are not ready."
                    /usr/local/bin/kubectl get pods -n ${KUBE_NAMESPACE}
                    exit 1
                '''
            }
        }

        stage('Deploy Monitoring Stack') {
            options {
                timeout(time: 10, unit: 'MINUTES')
            }
            agent {
                docker {
                    image 'ubuntu:22.04'
                    args '-u root --label pipeline=${APP_NAME}'
                }
            }
            steps {
                sh '''
                    if ! command -v curl >/dev/null 2>&1; then
                        while fuser /var/lib/apt/lists/lock >/dev/null 2>&1; do
                            echo "Waiting for other apt-get processes to finish..."
                            sleep 5
                        done
                        apt-get update
                        apt-get install -y curl
                    fi
                    if [ ! -f "/usr/local/bin/kubectl" ]; then
                        echo "kubectl not found in /usr/local/bin. Downloading..."
                        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                        chmod +x kubectl
                        mv kubectl /usr/local/bin/kubectl
                    fi

                    /usr/local/bin/kubectl set image deployment/grafana-deployment grafana=yaveenp/grafana:latest -n ${KUBE_NAMESPACE}
                    /usr/local/bin/kubectl rollout status deployment/grafana-deployment -n ${KUBE_NAMESPACE}
                    /usr/local/bin/kubectl set image deployment/prometheus-deployment prometheus=yaveenp/prometheus:latest -n ${KUBE_NAMESPACE}
                    /usr/local/bin/kubectl rollout status deployment/prometheus-deployment -n ${KUBE_NAMESPACE}

                    for i in {1..6}; do
                        if ! command -v curl >/dev/null 2>&1; then
                            while fuser /var/lib/apt/lists/lock >/dev/null 2>&1; do
                                echo "Waiting for other apt-get processes to finish..."
                                sleep 5
                            done
                            apt-get update
                            apt-get install -y curl
                        fi
                        if [ ! -f "/usr/local/bin/kubectl" ]; then
                            echo "kubectl not found in /usr/local/bin. Downloading..."
                            curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                            chmod +x kubectl
                            mv kubectl /usr/local/bin/kubectl
                        fi
                        NOT_READY=$(/usr/local/bin/kubectl get pods -n ${KUBE_NAMESPACE} --no-headers | grep -v "Running" | grep -v "Completed" | wc -l)
                        if [ "$NOT_READY" -eq 0 ]; then
                            echo "All monitoring pods are running and ready."
                            exit 0
                        fi
                        echo "Waiting for monitoring pods... ($i/6)"
                        /usr/local/bin/kubectl get pods -n ${KUBE_NAMESPACE}
                        sleep 20
                    done
                    echo "Monitoring pods not ready."
                    /usr/local/bin/kubectl get pods -n ${KUBE_NAMESPACE}
                    exit 1
                '''
            }
        }

        stage('API Test') {
            options {
                timeout(time: 5, unit: 'MINUTES')
            }
            agent {
                docker {
                    image 'python:3.11'
                    args '-u root --label pipeline=${APP_NAME}'
                }
            }
            steps {
                sh '''
                    pip install pytest requests
                    sed -i 's|http://flask-app:5050|http://localhost:30031|g' app/Backend/tests/api_tests.py
                    pytest app/Backend/tests/api_tests.py -v
                '''
            }
        }
    }

    post {
        failure {
            sh '''
                if ! command -v curl >/dev/null 2>&1; then
                    while fuser /var/lib/apt/lists/lock >/dev/null 2>&1; do
                        echo "Waiting for other apt-get processes to finish..."
                        sleep 5
                    done
                    apt-get update
                    apt-get install -y curl
                fi
                if [ ! -f "/usr/local/bin/kubectl" ]; then
                    echo "kubectl not found in /usr/local/bin. Downloading..."
                    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                    chmod +x kubectl
                    mv kubectl /usr/local/bin/kubectl
                fi
                /usr/local/bin/kubectl rollout undo deployment/flask-deployment -n ${KUBE_NAMESPACE} || true
                /usr/local/bin/kubectl rollout undo deployment/frontend-deployment -n ${KUBE_NAMESPACE} || true
                /usr/local/bin/kubectl rollout undo deployment/grafana-deployment -n ${KUBE_NAMESPACE} || true
                /usr/local/bin/kubectl rollout undo deployment/prometheus-deployment -n ${KUBE_NAMESPACE} || true
            '''
        }
        always {
            echo "Cleaning up local Docker images..."
            sh '''
                docker rmi -f ${BACKEND_IMAGE} || true
                docker rmi -f ${FRONTEND_IMAGE} || true
            '''

            echo "Cleaning stopped containers..."
            sh '''
                CONTAINERS=$(docker ps -a -q --filter "label=pipeline=${APP_NAME}" --filter "status=exited")
                [ -n "$CONTAINERS" ] && docker container rm $CONTAINERS || true
            '''

            echo "Cleaning workspace..."
            sh '''
                find $WORKSPACE -type f ! -name "lint_*.log" -delete
            '''
        }
    }
}