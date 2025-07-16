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
        KUBECTL_BIN = '/usr/local/bin/kubectl'
        KUBECONFIG = '/root/.kube/config'
    }

    stages {
        stage('Install Tools') {
            agent {
                docker {
                    image 'ubuntu:22.04'
                    args '-u root --label pipeline=${APP_NAME}'
                }
            }
            steps {
                sh '''
                    echo "=== Installing Python Tools ==="
                    apt-get update
                    apt-get install -y python3-pip wget curl apt-transport-https ca-certificates gnupg lsb-release

                    pip install flake8 pytest

                    echo "=== Installing kubectl ==="
                    curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/kubernetes-archive-keyring.gpg
                    echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" > /etc/apt/sources.list.d/kubernetes.list
                    apt-get update
                    apt-get install -y kubectl

                    echo "=== Verifying kubectl location and version ==="
                    which kubectl
                    kubectl version --client

                    echo "=== Running flake8 ==="
                    flake8 app/Backend || true
                '''
            }
        }

        stage('Test Kubernetes Connection') {
            agent {
                docker {
                    image 'ubuntu:22.04'
                    args '-u root --label pipeline=${APP_NAME}'
                }
            }
            environment {
                KUBECONFIG = '/root/.kube/config'
            }
            steps {
                echo "=== Testing Kubernetes Connection ==="
                sh '''
                    ${KUBECTL_BIN} config get-contexts
                    ${KUBECTL_BIN} get nodes
                '''
            }
        }

        stage('Pre-Build: Lint and Unit Tests') {
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
                            archiveArtifacts artifacts: 'lint_flask.log,unit_tests.log', allowEmptyArchive: true
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
                            archiveArtifacts artifacts: 'lint_react.log,unit_tests.log', allowEmptyArchive: true
                        }
                    }
                }
            }
        }

        stage('Build and Push Docker Images') {
            agent {
                docker {
                    image 'docker:24.0.0-dind'
                    args '--privileged -v /var/run/docker.sock:/var/run/docker.sock --label pipeline=${APP_NAME}'
                }
            }
            steps {
                timeout(time: 20, unit: 'MINUTES') {
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
                            sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'
                        }

                        sh """
                            docker buildx build --platform linux/amd64,linux/arm64 -t ${BACKEND_IMAGE} -f app/Backend/flask-dockerfile --push app/Backend
                            docker buildx build --platform linux/amd64,linux/arm64 -t ${FRONTEND_IMAGE} -f app/Frontend/Dockerfile --push app/Frontend
                            sed -i 's|image: yaveenp/investment-flask:.*|image: ${BACKEND_IMAGE}|' ${WORKSPACE}/kubernetes/flask/flask-deployment.yaml
                            sed -i 's|image: yaveenp/investment-frontend:.*|image: ${FRONTEND_IMAGE}|' ${WORKSPACE}/kubernetes/Frontend/frontend-deployment.yaml
                        """
                    }
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
            timeout(time: 10, unit: 'MINUTES')
            steps {
                echo "=== Ensure namespace exists ==="
                sh '''
                    ${KUBECTL_BIN} get ns ${KUBE_NAMESPACE} || ${KUBECTL_BIN} create ns ${KUBE_NAMESPACE}
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
                        sh """
                            if [ -f \"${res}\" ]; then
                                echo 'Applying: ${res}'
                                ${KUBECTL_BIN} apply -f "${res}" -n ${KUBE_NAMESPACE}
                            else
                                echo 'WARNING: Missing resource file: ${res}'
                            fi
                        """
                    }
                }

                sh '''
                    for i in {1..6}; do
                        NOT_READY=$(${KUBECTL_BIN} get pods -n ${KUBE_NAMESPACE} --no-headers | grep -v "Running" | grep -v "Completed" | wc -l)
                        if [ "$NOT_READY" -eq 0 ]; then
                            echo "All pods are running and ready."
                            exit 0
                        fi
                        echo "Waiting for pods to be ready... ($i/6)"
                        ${KUBECTL_BIN} get pods -n ${KUBE_NAMESPACE}
                        sleep 20
                    done
                    echo "Some pods are not ready."
                    ${KUBECTL_BIN} get pods -n ${KUBE_NAMESPACE}
                    exit 1
                '''
            }
        }

        stage('Deploy Application') {
            agent {
                docker {
                    image 'ubuntu:22.04'
                    args '-u root --label pipeline=${APP_NAME}'
                }
            }
            timeout(time: 10, unit: 'MINUTES')
            steps {
                sh '''
                    ${KUBECTL_BIN} set image deployment/flask-deployment flask-app=${BACKEND_IMAGE} -n ${KUBE_NAMESPACE}
                    ${KUBECTL_BIN} rollout status deployment/flask-deployment -n ${KUBE_NAMESPACE}
                    ${KUBECTL_BIN} set image deployment/frontend-deployment frontend=${FRONTEND_IMAGE} -n ${KUBE_NAMESPACE}
                    ${KUBECTL_BIN} rollout status deployment/frontend-deployment -n ${KUBE_NAMESPACE}

                    ${KUBECTL_BIN} apply -f ${WORKSPACE}/kubernetes/flask/flask-service.yaml -n ${KUBE_NAMESPACE}
                    ${KUBECTL_BIN} apply -f ${WORKSPACE}/kubernetes/Frontend/frontend-service.yaml -n ${KUBE_NAMESPACE}

                    for i in {1..6}; do
                        NOT_READY=$(${KUBECTL_BIN} get pods -n ${KUBE_NAMESPACE} --no-headers | grep -v "Running" | grep -v "Completed" | wc -l)
                        if [ "$NOT_READY" -eq 0 ]; then
                            echo "All pods are running and ready."
                            exit 0
                        fi
                        echo "Waiting for pods to be ready... ($i/6)"
                        ${KUBECTL_BIN} get pods -n ${KUBE_NAMESPACE}
                        sleep 20
                    done
                    echo "Some pods are not ready."
                    ${KUBECTL_BIN} get pods -n ${KUBE_NAMESPACE}
                    exit 1
                '''
            }
        }

        stage('Deploy Monitoring Stack') {
            agent {
                docker {
                    image 'ubuntu:22.04'
                    args '-u root --label pipeline=${APP_NAME}'
                }
            }
            timeout(time: 10, unit: 'MINUTES')
            steps {
                sh '''
                    ${KUBECTL_BIN} set image deployment/grafana-deployment grafana=yaveenp/grafana:latest -n ${KUBE_NAMESPACE}
                    ${KUBECTL_BIN} rollout status deployment/grafana-deployment -n ${KUBE_NAMESPACE}
                    ${KUBECTL_BIN} set image deployment/prometheus-deployment prometheus=yaveenp/prometheus:latest -n ${KUBE_NAMESPACE}
                    ${KUBECTL_BIN} rollout status deployment/prometheus-deployment -n ${KUBE_NAMESPACE}

                    for i in {1..6}; do
                        NOT_READY=$(${KUBECTL_BIN} get pods -n ${KUBE_NAMESPACE} --no-headers | grep -v "Running" | grep -v "Completed" | wc -l)
                        if [ "$NOT_READY" -eq 0 ]; then
                            echo "All monitoring pods are running and ready."
                            exit 0
                        fi
                        echo "Waiting for monitoring pods... ($i/6)"
                        ${KUBECTL_BIN} get pods -n ${KUBE_NAMESPACE}
                        sleep 20
                    done
                    echo "Monitoring pods not ready."
                    ${KUBECTL_BIN} get pods -n ${KUBE_NAMESPACE}
                    exit 1
                '''
            }
        }

        stage('API Test') {
            agent {
                docker {
                    image 'python:3.11'
                    args '-u root --label pipeline=${APP_NAME}'
                }
            }
            timeout(time: 5, unit: 'MINUTES')
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
            echo "Pipeline failed: Rolling back deployments..."
            sh "${KUBECTL_BIN} rollout undo deployment/flask-deployment -n ${KUBE_NAMESPACE} || true"
            sh "${KUBECTL_BIN} rollout undo deployment/frontend-deployment -n ${KUBE_NAMESPACE} || true"
            sh "${KUBECTL_BIN} rollout undo deployment/grafana-deployment -n ${KUBE_NAMESPACE} || true"
            sh "${KUBECTL_BIN} rollout undo deployment/prometheus-deployment -n ${KUBE_NAMESPACE} || true"
        }
        always {
            echo "=== Installing kubectl ==="
            sh '''
                apt-get update
                apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
                curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/kubernetes-archive-keyring.gpg
                echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" > /etc/apt/sources.list.d/kubernetes.list
                apt-get update
                apt-get install -y kubectl
            '''

            echo "Cleaning up local Docker images..."
            sh "docker rmi -f ${BACKEND_IMAGE} || true"
            sh "docker rmi -f ${FRONTEND_IMAGE} || true"

            echo "Cleaning stopped containers..."
            sh '''
                CONTAINERS=$(docker ps -a -q --filter "label=pipeline=${APP_NAME}" --filter "status=exited")
                [ -n "$CONTAINERS" ] && docker container rm $CONTAINERS || true
            '''

            echo "Cleaning workspace..."
            sh 'find $WORKSPACE -type f ! -name "lint_*.log" -delete'
        }
    }
}