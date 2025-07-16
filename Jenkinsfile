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
        // KUBECONFIG will be set in each stage that needs it
    }

    stages {
        stage('Install Tools') {
            steps {
                script {
                    docker.image('ubuntu:22.04').inside('-u root') {
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
                        '''
                    }
                }
            }
        }

        stage('Test Kubernetes Connection') {
            steps {
                script {
                    // Check if kubeconfig credential exists, otherwise use default location
                    def kubeconfigPath = ''
                    try {
                        withCredentials([file(credentialsId: 'kubeconfig-file', variable: 'KUBECONFIG_FILE')]) {
                            kubeconfigPath = "${KUBECONFIG_FILE}"
                        }
                    } catch (Exception e) {
                        echo "Warning: kubeconfig-file credential not found. Using default kubeconfig location."
                        kubeconfigPath = "${env.HOME}/.kube/config"
                    }
                    
                    docker.image('bitnami/kubectl:latest').inside("--entrypoint='' -v ${kubeconfigPath}:/root/.kube/config:ro") {
                        sh '''
                            echo "=== Testing Kubernetes Connection ==="
                            kubectl config get-contexts
                            kubectl get nodes
                        '''
                    }
                }
            }
        }

        stage('Pre-Build: Lint and Unit Tests') {
            parallel {
                stage('Lint Flask Code') {
                    steps {
                        script {
                            docker.image('python:3.10').inside('-u root') {
                                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                                    sh '''
                                        echo "=== Starting Lint Flask Code Stage ==="
                                        cd ${WORKSPACE}
                                        python3 -m venv venv
                                        . venv/bin/activate
                                        pip install --upgrade pip
                                        pip install flake8
                                        
                                        # Create log file
                                        touch lint_flask.log
                                        
                                        # Run flake8 with proper error handling
                                        if [ -d "app/Backend/main.py" ] || [ -d "app/Backend/Financial_Portfolio_Tracker/" ]; then
                                            flake8 app/Backend/main.py app/Backend/Financial_Portfolio_Tracker/ > lint_flask.log 2>&1 || echo "Flake8 found issues (see lint_flask.log)"
                                        else
                                            echo "Backend files not found" > lint_flask.log
                                        fi
                                    '''
                                    archiveArtifacts artifacts: 'lint_flask.log', allowEmptyArchive: true
                                }
                            }
                        }
                    }
                }
                stage('Lint React Code') {
                    steps {
                        script {
                            docker.image('node:20-bullseye').inside('-u root') {
                                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                                    sh '''
                                        echo "=== Starting Lint React Code Stage ==="
                                        cd ${WORKSPACE}
                                        
                                        # Create log file
                                        touch lint_react.log
                                        
                                        if [ -d "app/Frontend" ]; then
                                            cd app/Frontend
                                            npm install
                                            npm run lint > ${WORKSPACE}/lint_react.log 2>&1 || echo "ESLint found issues (see lint_react.log)"
                                        else
                                            echo "Frontend directory not found" > ${WORKSPACE}/lint_react.log
                                        fi
                                    '''
                                    archiveArtifacts artifacts: 'lint_react.log', allowEmptyArchive: true
                                }
                            }
                        }
                    }
                }
            }
        }

        stage('Build and Push Docker Images') {
            steps {
                timeout(time: 20, unit: 'MINUTES') {
                    script {
                        // Use host Docker daemon
                        withCredentials([usernamePassword(credentialsId: 'docker-hub-cred-yaveen', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                            sh '''
                                echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                                
                                # Setup buildx if not already available
                                if ! docker buildx version > /dev/null 2>&1; then
                                    docker buildx create --name mybuilder --use || docker buildx use mybuilder
                                else
                                    docker buildx use mybuilder || docker buildx create --name mybuilder --use
                                fi
                                
                                docker buildx inspect --bootstrap
                                
                                # Build and push images
                                docker buildx build --platform linux/amd64,linux/arm64 \
                                    -t ${BACKEND_IMAGE} \
                                    -f app/Backend/flask-dockerfile \
                                    --push app/Backend
                                
                                docker buildx build --platform linux/amd64,linux/arm64 \
                                    -t ${FRONTEND_IMAGE} \
                                    -f app/Frontend/Dockerfile \
                                    --push app/Frontend
                                
                                # Update deployment files with new image tags
                                sed -i "s|image: yaveenp/investment-flask:.*|image: ${BACKEND_IMAGE}|g" kubernetes/flask/flask-deployment.yaml
                                sed -i "s|image: yaveenp/investment-frontend:.*|image: ${FRONTEND_IMAGE}|g" kubernetes/Frontend/frontend-deployment.yaml
                            '''
                        }
                    }
                }
            }
        }

        stage('Prepare Kubernetes Resources') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    script {
                        def kubeconfigPath = ''
                        try {
                            withCredentials([file(credentialsId: 'kubeconfig-file', variable: 'KUBECONFIG_FILE')]) {
                                kubeconfigPath = "${KUBECONFIG_FILE}"
                            }
                        } catch (Exception e) {
                            kubeconfigPath = "${env.HOME}/.kube/config"
                        }
                        
                        docker.image('bitnami/kubectl:latest').inside("--entrypoint='' -v ${kubeconfigPath}:/root/.kube/config:ro") {
                            sh '''
                                echo "=== Ensure namespace exists ==="
                                kubectl get ns ${KUBE_NAMESPACE} || kubectl create ns ${KUBE_NAMESPACE}
                            '''
                            
                            // Apply core resources
                            def coreResources = [
                                "Postgres/postgres-configmap.yaml",
                                "kubernetes/flask/flask-secret.yaml",
                                "kubernetes/Monitoring/prometheus-configmap.yaml",
                                "kubernetes/Monitoring/grafana-datasource-configmap.yaml",
                                "kubernetes/Monitoring/grafana-dashboard-configmap.yaml",
                                "kubernetes/Monitoring/grafana-dashboard-provider-configmap.yaml",
                                "kubernetes/Monitoring/grafana-service.yaml",
                                "kubernetes/Monitoring/prometheus-service.yaml",
                                "kubernetes/Monitoring/node-exporter-daemonset.yaml",
                                "kubernetes/Monitoring/node-exporter-service.yaml",
                                "kubernetes/ingress.yaml",
                                "kubernetes/ingress-nginx-controller.yaml"
                            ]
                            
                            coreResources.each { resource ->
                                sh """
                                    if [ -f "${WORKSPACE}/${resource}" ]; then
                                        echo 'Applying: ${resource}'
                                        kubectl apply -f "${WORKSPACE}/${resource}" -n ${KUBE_NAMESPACE}
                                    else
                                        echo 'WARNING: Missing resource file: ${resource}'
                                    fi
                                """
                            }
                            
                            // Apply deployments
                            sh '''
                                kubectl apply -f ${WORKSPACE}/kubernetes/flask/flask-deployment.yaml -n ${KUBE_NAMESPACE}
                                kubectl apply -f ${WORKSPACE}/kubernetes/Frontend/frontend-deployment.yaml -n ${KUBE_NAMESPACE}
                                kubectl apply -f ${WORKSPACE}/kubernetes/Monitoring/grafana-deployment.yaml -n ${KUBE_NAMESPACE}
                                kubectl apply -f ${WORKSPACE}/kubernetes/Monitoring/prometheus-deployment.yaml -n ${KUBE_NAMESPACE}
                            '''
                            
                            // Wait for pods to be ready
                            sh '''
                                echo "=== Waiting for pods to be ready ==="
                                kubectl wait --for=condition=ready pod -l app=flask-app -n ${KUBE_NAMESPACE} --timeout=300s || true
                                kubectl wait --for=condition=ready pod -l app=frontend -n ${KUBE_NAMESPACE} --timeout=300s || true
                                kubectl get pods -n ${KUBE_NAMESPACE}
                            '''
                        }
                    }
                }
            }
        }

        stage('Deploy Application') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    script {
                        def kubeconfigPath = ''
                        try {
                            withCredentials([file(credentialsId: 'kubeconfig-file', variable: 'KUBECONFIG_FILE')]) {
                                kubeconfigPath = "${KUBECONFIG_FILE}"
                            }
                        } catch (Exception e) {
                            kubeconfigPath = "${env.HOME}/.kube/config"
                        }
                        
                        docker.image('bitnami/kubectl:latest').inside("--entrypoint='' -v ${kubeconfigPath}:/root/.kube/config:ro") {
                            sh '''
                                # Update deployments with new images
                                kubectl set image deployment/flask-deployment flask-app=${BACKEND_IMAGE} -n ${KUBE_NAMESPACE}
                                kubectl rollout status deployment/flask-deployment -n ${KUBE_NAMESPACE} --timeout=5m
                                
                                kubectl set image deployment/frontend-deployment frontend=${FRONTEND_IMAGE} -n ${KUBE_NAMESPACE}
                                kubectl rollout status deployment/frontend-deployment -n ${KUBE_NAMESPACE} --timeout=5m
                                
                                # Apply services
                                kubectl apply -f ${WORKSPACE}/kubernetes/flask/flask-service.yaml -n ${KUBE_NAMESPACE}
                                kubectl apply -f ${WORKSPACE}/kubernetes/Frontend/frontend-service.yaml -n ${KUBE_NAMESPACE}
                                
                                # Final status check
                                echo "=== Final deployment status ==="
                                kubectl get deployments -n ${KUBE_NAMESPACE}
                                kubectl get pods -n ${KUBE_NAMESPACE}
                                kubectl get services -n ${KUBE_NAMESPACE}
                            '''
                        }
                    }
                }
            }
        }

        stage('Deploy Monitoring Stack') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    script {
                        def kubeconfigPath = ''
                        try {
                            withCredentials([file(credentialsId: 'kubeconfig-file', variable: 'KUBECONFIG_FILE')]) {
                                kubeconfigPath = "${KUBECONFIG_FILE}"
                            }
                        } catch (Exception e) {
                            kubeconfigPath = "${env.HOME}/.kube/config"
                        }
                        
                        docker.image('bitnami/kubectl:latest').inside("--entrypoint='' -v ${kubeconfigPath}:/root/.kube/config:ro") {
                            sh '''
                                # Update monitoring deployments
                                kubectl set image deployment/grafana-deployment grafana=yaveenp/grafana:latest -n ${KUBE_NAMESPACE}
                                kubectl rollout status deployment/grafana-deployment -n ${KUBE_NAMESPACE} --timeout=5m
                                
                                kubectl set image deployment/prometheus-deployment prometheus=yaveenp/prometheus:latest -n ${KUBE_NAMESPACE}
                                kubectl rollout status deployment/prometheus-deployment -n ${KUBE_NAMESPACE} --timeout=5m
                                
                                # Check monitoring stack status
                                echo "=== Monitoring stack status ==="
                                kubectl get pods -l app=grafana -n ${KUBE_NAMESPACE}
                                kubectl get pods -l app=prometheus -n ${KUBE_NAMESPACE}
                            '''
                        }
                    }
                }
            }
        }

        stage('API Test') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    script {
                        docker.image('python:3.11').inside('-u root') {
                            sh '''
                                pip install pytest requests
                                
                                # Wait for service to be available
                                sleep 30
                                
                                # Update test endpoint
                                if [ -f "app/Backend/tests/api_tests.py" ]; then
                                    sed -i 's|http://flask-app:5050|http://localhost:30031|g' app/Backend/tests/api_tests.py
                                    pytest app/Backend/tests/api_tests.py -v --tb=short
                                else
                                    echo "WARNING: API tests not found at app/Backend/tests/api_tests.py"
                                fi
                            '''
                        }
                    }
                }
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