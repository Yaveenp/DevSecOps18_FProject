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
        // Use docker.sock from host
        DOCKER_HOST = "unix:///var/run/docker.sock"
    }

    stages {
        stage('Verify Environment') {
            steps {
                script {
                    sh '''
                        echo "=== Environment Information ==="
                        whoami
                        pwd
                        echo "Jenkins Home: ${JENKINS_HOME}"
                        
                        echo "=== Docker Information ==="
                        docker version || {
                            echo "ERROR: Docker is not available"
                            exit 1
                        }
                        
                        echo "=== Docker Socket Permissions ==="
                        ls -la /var/run/docker.sock || echo "Docker socket not found"
                        
                        echo "=== Testing Docker Access ==="
                        docker ps || {
                            echo "ERROR: Cannot connect to Docker daemon"
                            echo "Please ensure Jenkins container is running with:"
                            echo "  -v /var/run/docker.sock:/var/run/docker.sock"
                            echo "  And Jenkins user has access to docker group"
                            exit 1
                        }
                    '''
                }
            }
        }

        stage('Setup Workspace') {
            steps {
                script {
                    sh '''
                        echo "=== Setting up workspace ==="
                        # Ensure we have a clean workspace
                        cd ${WORKSPACE}
                        
                        # Install kubectl directly in workspace
                        if [ ! -f "${WORKSPACE}/kubectl" ]; then
                            echo "Downloading kubectl..."
                            curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                            chmod +x kubectl
                        fi
                        
                        # Verify kubectl
                        ${WORKSPACE}/kubectl version --client
                    '''
                }
            }
        }

        stage('Setup Kubeconfig') {
            steps {
                script {
                    // Try to get kubeconfig from credentials
                    def hasKubeconfig = false
                    try {
                        withCredentials([file(credentialsId: 'kubeconfig-file', variable: 'KUBECONFIG_FILE')]) {
                            sh '''
                                mkdir -p ${WORKSPACE}/.kube
                                cp ${KUBECONFIG_FILE} ${WORKSPACE}/.kube/config
                                chmod 600 ${WORKSPACE}/.kube/config
                                echo "Kubeconfig set up from Jenkins credentials"
                            '''
                            hasKubeconfig = true
                        }
                    } catch (Exception e) {
                        echo "kubeconfig-file credential not found, checking default location..."
                    }
                    
                    if (!hasKubeconfig) {
                        sh '''
                            # Check if kubeconfig exists in default location
                            if [ -f "${HOME}/.kube/config" ]; then
                                mkdir -p ${WORKSPACE}/.kube
                                cp ${HOME}/.kube/config ${WORKSPACE}/.kube/config
                                chmod 600 ${WORKSPACE}/.kube/config
                                echo "Using kubeconfig from default location"
                            else
                                echo "WARNING: No kubeconfig found. Kubernetes stages will be skipped."
                                echo "To fix: Create 'kubeconfig-file' credential or place config in ~/.kube/config"
                            fi
                        '''
                    }
                }
            }
        }

        stage('Test Kubernetes Connection') {
            when {
                expression {
                    return fileExists("${WORKSPACE}/.kube/config")
                }
            }
            steps {
                sh '''
                    export KUBECONFIG=${WORKSPACE}/.kube/config
                    echo "=== Testing Kubernetes Connection ==="
                    ${WORKSPACE}/kubectl config get-contexts
                    ${WORKSPACE}/kubectl get nodes
                '''
            }
        }

        stage('Pre-Build: Lint and Unit Tests') {
            parallel {
                stage('Lint Flask Code') {
                    steps {
                        script {
                            docker.image('python:3.10').inside {
                                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                                    sh '''
                                        echo "=== Linting Flask Code ==="
                                        cd ${WORKSPACE}
                                        
                                        pip install flake8
                                        
                                        touch lint_flask.log
                                        
                                        if [ -f "app/Backend/main.py" ] || [ -d "app/Backend/Financial_Portfolio_Tracker/" ]; then
                                            flake8 app/Backend/main.py app/Backend/Financial_Portfolio_Tracker/ > lint_flask.log 2>&1 || echo "Flake8 found issues"
                                        else
                                            echo "Backend files not found" > lint_flask.log
                                        fi
                                        
                                        cat lint_flask.log
                                    '''
                                }
                            }
                            archiveArtifacts artifacts: 'lint_flask.log', allowEmptyArchive: true
                        }
                    }
                }
                stage('Lint React Code') {
                    steps {
                        script {
                            docker.image('node:20-alpine').inside {
                                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                                    sh '''
                                        echo "=== Linting React Code ==="
                                        cd ${WORKSPACE}
                                        
                                        touch lint_react.log
                                        
                                        if [ -d "app/Frontend" ]; then
                                            cd app/Frontend
                                            npm install
                                            npm run lint > ${WORKSPACE}/lint_react.log 2>&1 || echo "ESLint found issues"
                                        else
                                            echo "Frontend directory not found" > ${WORKSPACE}/lint_react.log
                                        fi
                                        
                                        cat ${WORKSPACE}/lint_react.log
                                    '''
                                }
                            }
                            archiveArtifacts artifacts: 'lint_react.log', allowEmptyArchive: true
                        }
                    }
                }
            }
        }

        stage('Build and Push Docker Images') {
            steps {
                timeout(time: 20, unit: 'MINUTES') {
                    script {
                        withCredentials([usernamePassword(credentialsId: 'docker-hub-cred-yaveen', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                            sh '''
                                echo "=== Docker Login ==="
                                echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                                
                                echo "=== Setting up Docker Buildx ==="
                                # Remove existing builder if any
                                docker buildx rm mybuilder || true
                                
                                # Create new builder
                                docker buildx create --name mybuilder --driver docker-container --use
                                docker buildx inspect --bootstrap
                                
                                echo "=== Building Backend Image ==="
                                docker buildx build --platform linux/amd64,linux/arm64 \
                                    -t ${BACKEND_IMAGE} \
                                    -f app/Backend/flask-dockerfile \
                                    --push app/Backend
                                
                                echo "=== Building Frontend Image ==="
                                docker buildx build --platform linux/amd64,linux/arm64 \
                                    -t ${FRONTEND_IMAGE} \
                                    -f app/Frontend/Dockerfile \
                                    --push app/Frontend
                                
                                echo "=== Updating Kubernetes manifests ==="
                                sed -i "s|image: yaveenp/investment-flask:.*|image: ${BACKEND_IMAGE}|g" kubernetes/flask/flask-deployment.yaml
                                sed -i "s|image: yaveenp/investment-frontend:.*|image: ${FRONTEND_IMAGE}|g" kubernetes/Frontend/frontend-deployment.yaml
                            '''
                        }
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            when {
                expression {
                    return fileExists("${WORKSPACE}/.kube/config")
                }
            }
            steps {
                timeout(time: 15, unit: 'MINUTES') {
                    script {
                        sh '''
                            export KUBECONFIG=${WORKSPACE}/.kube/config
                            export KUBECTL=${WORKSPACE}/kubectl
                            
                            echo "=== Creating namespace ==="
                            $KUBECTL get ns ${KUBE_NAMESPACE} || $KUBECTL create ns ${KUBE_NAMESPACE}
                            
                            echo "=== Applying ConfigMaps and Secrets ==="
                            # Apply configurations first
                            for file in Postgres/postgres-configmap.yaml \
                                       kubernetes/flask/flask-secret.yaml \
                                       kubernetes/Monitoring/prometheus-configmap.yaml \
                                       kubernetes/Monitoring/grafana-datasource-configmap.yaml \
                                       kubernetes/Monitoring/grafana-dashboard-configmap.yaml \
                                       kubernetes/Monitoring/grafana-dashboard-provider-configmap.yaml; do
                                if [ -f "$file" ]; then
                                    echo "Applying: $file"
                                    $KUBECTL apply -f "$file" -n ${KUBE_NAMESPACE}
                                else
                                    echo "WARNING: $file not found"
                                fi
                            done
                            
                            echo "=== Applying Services ==="
                            for file in kubernetes/flask/flask-service.yaml \
                                       kubernetes/Frontend/frontend-service.yaml \
                                       kubernetes/Monitoring/grafana-service.yaml \
                                       kubernetes/Monitoring/prometheus-service.yaml \
                                       kubernetes/Monitoring/node-exporter-service.yaml; do
                                if [ -f "$file" ]; then
                                    echo "Applying: $file"
                                    $KUBECTL apply -f "$file" -n ${KUBE_NAMESPACE}
                                else
                                    echo "WARNING: $file not found"
                                fi
                            done
                            
                            echo "=== Applying Deployments ==="
                            # Apply deployments with updated images
                            $KUBECTL apply -f kubernetes/flask/flask-deployment.yaml -n ${KUBE_NAMESPACE}
                            $KUBECTL apply -f kubernetes/Frontend/frontend-deployment.yaml -n ${KUBE_NAMESPACE}
                            
                            # Apply monitoring deployments if they exist
                            [ -f kubernetes/Monitoring/grafana-deployment.yaml ] && \
                                $KUBECTL apply -f kubernetes/Monitoring/grafana-deployment.yaml -n ${KUBE_NAMESPACE}
                            [ -f kubernetes/Monitoring/prometheus-deployment.yaml ] && \
                                $KUBECTL apply -f kubernetes/Monitoring/prometheus-deployment.yaml -n ${KUBE_NAMESPACE}
                            [ -f kubernetes/Monitoring/node-exporter-daemonset.yaml ] && \
                                $KUBECTL apply -f kubernetes/Monitoring/node-exporter-daemonset.yaml -n ${KUBE_NAMESPACE}
                            
                            echo "=== Applying Ingress ==="
                            [ -f kubernetes/ingress.yaml ] && \
                                $KUBECTL apply -f kubernetes/ingress.yaml -n ${KUBE_NAMESPACE}
                            
                            echo "=== Waiting for deployments ==="
                            $KUBECTL rollout status deployment/flask-deployment -n ${KUBE_NAMESPACE} --timeout=5m || true
                            $KUBECTL rollout status deployment/frontend-deployment -n ${KUBE_NAMESPACE} --timeout=5m || true
                            
                            echo "=== Deployment Status ==="
                            $KUBECTL get all -n ${KUBE_NAMESPACE}
                        '''
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    docker.image('python:3.11-slim').inside {
                        sh '''
                            echo "=== Running API Tests ==="
                            pip install pytest requests
                            
                            # Wait for services to be ready
                            sleep 30
                            
                            if [ -f "app/Backend/tests/api_tests.py" ]; then
                                # Update test endpoint if needed
                                sed -i 's|http://flask-app:5050|http://localhost:30031|g' app/Backend/tests/api_tests.py || true
                                
                                # Run tests
                                pytest app/Backend/tests/api_tests.py -v --tb=short || echo "Tests completed with issues"
                            else
                                echo "WARNING: API tests not found"
                            fi
                        '''
                    }
                }
            }
        }
    }

    post {
        failure {
            script {
                if (fileExists("${WORKSPACE}/.kube/config")) {
                    sh '''
                        export KUBECONFIG=${WORKSPACE}/.kube/config
                        export KUBECTL=${WORKSPACE}/kubectl
                        
                        echo "=== Rolling back deployments ==="
                        $KUBECTL rollout undo deployment/flask-deployment -n ${KUBE_NAMESPACE} || true
                        $KUBECTL rollout undo deployment/frontend-deployment -n ${KUBE_NAMESPACE} || true
                        $KUBECTL rollout undo deployment/grafana-deployment -n ${KUBE_NAMESPACE} || true
                        $KUBECTL rollout undo deployment/prometheus-deployment -n ${KUBE_NAMESPACE} || true
                    '''
                }
            }
        }
        always {
            script {
                sh '''
                    echo "=== Cleanup ==="
                    # Remove buildx builder
                    docker buildx rm mybuilder || true
                    
                    # Clean up images
                    docker rmi ${BACKEND_IMAGE} || true
                    docker rmi ${FRONTEND_IMAGE} || true
                    
                    # Clean workspace (but keep archived artifacts)
                    rm -rf ${WORKSPACE}/.kube
                    rm -f ${WORKSPACE}/kubectl
                '''
            }
        }
    }
}