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
                echo "=== Installing kubectl ==="
                sh '''
                    apt-get update
                    apt-get install -y apt-transport-https ca-certificates curl
                    apt-get install -y ca-certificates
                    curl -LO https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl
                    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
                '''
                echo "=== Testing Kubernetes Connection ==="
                sh 'kubectl config get-contexts'
                sh 'kubectl get nodes'
            }
        }
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
                        // Install Buildx if not present
                        sh '''
                            if ! docker buildx version > /dev/null 2>&1; then
                              mkdir -p ~/.docker/cli-plugins/
                              wget https://github.com/docker/buildx/releases/download/v0.12.0/buildx-v0.12.0.linux-amd64 -O ~/.docker/cli-plugins/docker-buildx
                              chmod +x ~/.docker/cli-plugins/docker-buildx
                            fi
                        '''
                        // Create and use buildx builder for multi-platform builds
                        sh 'docker buildx create --name mybuilder --use'
                        sh 'docker buildx inspect --bootstrap'
                        withCredentials([usernamePassword(credentialsId: 'docker-hub-cred-yaveen', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                            sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'
                        }

                        echo "--- Building and pushing backend image ---"
                        sh "docker buildx build --platform linux/amd64,linux/arm64 -t ${BACKEND_IMAGE} -f app/Backend/flask-dockerfile --push app/Backend"

                        echo "--- Building and pushing frontend image ---"
                        sh "docker buildx build --platform linux/amd64,linux/arm64 -t ${FRONTEND_IMAGE} -f app/Frontend/Dockerfile --push app/Frontend"
                        // Update image tags in Kubernetes YAML files
                        def backendTag = env.BUILD_NUMBER ?: 'latest'
                        def frontendTag = env.BUILD_NUMBER ?: 'latest'
                        sh "sed -i 's|image: yaveenp/investment-flask:.*|image: yaveenp/investment-flask:${backendTag}|' ${WORKSPACE}/kubernetes/flask/flask-deployment.yaml"
                        sh "sed -i 's|image: yaveenp/investment-frontend:.*|image: yaveenp/investment-frontend:${frontendTag}|' ${WORKSPACE}/kubernetes/Frontend/frontend-deployment.yaml"
                    }
                }
            }
        }

        stage('Deploy to Kubeadm and run resources') {
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
                timeout(time: 10, unit: 'MINUTES') {
                    echo "=== Installing kubectl ==="
                    sh '''
                        apt-get clean
                        apt-get update
                        apt-get install -y apt-transport-https ca-certificates curl
                        curl -LO https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl
                        install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
                    '''
                    
                    echo "=== Creating Kubernetes Namespace if not exists ==="
                    sh "kubectl create namespace ${KUBE_NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -"
                    
                    echo "=== Starting Deploy to Kubernetes Stage ==="
                    sh "kubectl apply -f ${WORKSPACE}/Postgres/postgres-pv.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/Postgres/postgres-pvc.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/Postgres/postgres-secret.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/Postgres/postgres-configmap.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/flask/flask-secret.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/Monitoring/prometheus-configmap.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/Monitoring/grafana-datasource-configmap.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/Monitoring/grafana-dashboard-configmap.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/Monitoring/grafana-dashboard-provider-configmap.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/Monitoring/grafana-service.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/Monitoring/prometheus-service.yaml -n ${KUBE_NAMESPACE}"
                    
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
                    
                    echo "=== Starting Run Prometheus and Grafana Stage ==="
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/Monitoring/prometheus-deployment.yaml -n ${KUBE_NAMESPACE}"
                    sh "kubectl apply -f ${WORKSPACE}/kubernetes/Monitoring/grafana-deployment.yaml -n ${KUBE_NAMESPACE}"

                    echo "--- Kubernetes resource status ---"
                    sh "kubectl get configmap,secret -n ${KUBE_NAMESPACE}"
                    sh "kubectl get pv,pvc -n ${KUBE_NAMESPACE}"
                    sh "kubectl get deployments,pods -n ${KUBE_NAMESPACE}"
                    sh "kubectl get services -n ${KUBE_NAMESPACE}"
                    sh "kubectl get ingress -n ${KUBE_NAMESPACE}"
                    sh "kubectl get all -n ${KUBE_NAMESPACE}"
                    
                    echo "--- Waiting for all pods to be ready ---"
                    sh '''
                    for i in {1..3}; do
                        NOT_READY=$(kubectl get pods -n ${KUBE_NAMESPACE} --no-headers | grep -v "Running" | grep -v "Completed" | wc -l)
                        if [ "$NOT_READY" -eq 0 ]; then
                        echo "All pods are running and ready."
                        exit 0
                        fi
                        echo "Waiting for pods to be ready... ($i/3)"
                        kubectl get pods -n ${KUBE_NAMESPACE}
                        sleep 30
                    done
                    echo "Timeout waiting for pods to be ready. Check pod status manually."
                    exit 1
                    '''
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
                    sh "sed -i 's|http://flask-app:5050|http://localhost:30300|g' app/Backend/tests/api_tests.py"
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
            sh(script: '''
              CONTAINERS=$(docker ps -a -q --filter "label=pipeline=${APP_NAME}" --filter "status=exited")
              if [ -n "$CONTAINERS" ]; then
                docker container rm $CONTAINERS
              fi
            ''', returnStatus: true)
            echo "=== Pipeline Complete: Cleaning up Workspace ==="
            sh 'rm -rf $WORKSPACE/*'
            echo "=== Pipeline Complete: Ensuring kubectl is installed for cleanup ==="
            sh '''
              if ! command -v kubectl > /dev/null 2>&1; then
                apt-get update
                apt-get install -y apt-transport-https ca-certificates curl
                curl -LO https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl
                install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
              fi
            '''
            echo "=== Pipeline Complete: Cleaning up Kubernetes resources ==="
            sh '''
              if command -v kubectl > /dev/null 2>&1; then
                echo "Deleting all resources in namespace ${KUBE_NAMESPACE}..."
                kubectl delete all --all -n ${KUBE_NAMESPACE} || true
                kubectl delete pvc --all -n ${KUBE_NAMESPACE} || true
                kubectl delete pv postgres-pv-k8s || true
                kubectl delete configmap --all -n ${KUBE_NAMESPACE} || true
                kubectl delete secret --all -n ${KUBE_NAMESPACE} || true
                kubectl delete namespace ${KUBE_NAMESPACE} || true
              else
                echo "kubectl not found, skipping Kubernetes cleanup."
              fi
            '''
        }
    }
}