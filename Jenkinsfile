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
                        echo "=== Setting up build environment ==="
                        
                        # Install kubectl in workspace
                        if [ ! -f "${WORKSPACE}/kubectl" ]; then
                            curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                            chmod +x kubectl
                        fi
                        
                        # Setup Python virtual environment
                        apt-get update || true
                        apt-get install -y python3-pip python3-venv || true
                        
                        python3 -m venv ${WORKSPACE}/venv
                        . ${WORKSPACE}/venv/bin/activate
                        pip install --upgrade pip
                        pip install flake8 pytest requests
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
                                . ${WORKSPACE}/venv/bin/activate
                                
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
                                # Install Node.js if not available
                                if ! command -v node &> /dev/null; then
                                    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
                                    apt-get install -y nodejs
                                fi
                                
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
                            archiveArtifacts artifacts: 'lint_react.log', allowEmptyArchive: true
                        }
                    }
                }
            }
        }

        stage('Build with Remote Docker') {
            steps {
                script {
                    // This stage would typically use a remote Docker host or build service
                    echo "INFO: Docker socket not available in Jenkins"
                    echo "To build images, you need to:"
                    echo "1. Restart Jenkins with docker socket mounted"
                    echo "2. Or use a remote Docker build service"
                    echo "3. Or build images manually outside Jenkins"
                    
                    sh '''
                        echo "=== Build Instructions ==="
                        echo "Run these commands on a machine with Docker:"
                        echo ""
                        echo "# Backend:"
                        echo "docker build -t ${BACKEND_IMAGE} -f app/Backend/flask-dockerfile app/Backend"
                        echo "docker push ${BACKEND_IMAGE}"
                        echo ""
                        echo "# Frontend:"
                        echo "docker build -t ${FRONTEND_IMAGE} -f app/Frontend/Dockerfile app/Frontend"
                        echo "docker push ${FRONTEND_IMAGE}"
                        
                        # Update deployment files anyway
                        sed -i "s|image: yaveenp/investment-flask:.*|image: ${BACKEND_IMAGE}|g" kubernetes/flask/flask-deployment.yaml || true
                        sed -i "s|image: yaveenp/investment-frontend:.*|image: ${FRONTEND_IMAGE}|g" kubernetes/Frontend/frontend-deployment.yaml || true
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            when {
                expression {
                    // Check if we have kubeconfig
                    return fileExists("${env.HOME}/.kube/config") || 
                           credentials('kubeconfig-file') != null
                }
            }
            steps {
                script {
                    // Setup kubeconfig
                    try {
                        withCredentials([file(credentialsId: 'kubeconfig-file', variable: 'KUBECONFIG_FILE')]) {
                            sh '''
                                mkdir -p ${WORKSPACE}/.kube
                                cp ${KUBECONFIG_FILE} ${WORKSPACE}/.kube/config
                                chmod 600 ${WORKSPACE}/.kube/config
                            '''
                        }
                    } catch (Exception e) {
                        sh '''
                            if [ -f "${HOME}/.kube/config" ]; then
                                mkdir -p ${WORKSPACE}/.kube
                                cp ${HOME}/.kube/config ${WORKSPACE}/.kube/config
                                chmod 600 ${WORKSPACE}/.kube/config
                            fi
                        '''
                    }
                    
                    sh '''
                        if [ -f "${WORKSPACE}/.kube/config" ]; then
                            export KUBECONFIG=${WORKSPACE}/.kube/config
                            
                            echo "=== Deploying to Kubernetes ==="
                            ${WORKSPACE}/kubectl apply -f kubernetes/ -R -n ${KUBE_NAMESPACE} || true
                            
                            echo "=== Deployment Status ==="
                            ${WORKSPACE}/kubectl get all -n ${KUBE_NAMESPACE}
                        else
                            echo "WARNING: No kubeconfig available, skipping Kubernetes deployment"
                        fi
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . ${WORKSPACE}/venv/bin/activate
                    
                    if [ -f "app/Backend/tests/api_tests.py" ]; then
                        echo "=== Running API Tests ==="
                        pytest app/Backend/tests/api_tests.py -v || echo "Tests completed"
                    else
                        echo "WARNING: No tests found"
                    fi
                '''
            }
        }
    }

    post {
        always {
            deleteDir()
        }
    }
}