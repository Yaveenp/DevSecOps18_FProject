# DevSecOps18 Final Project

Welcome to the **DevSecOps18 Final Project** repository! This project demonstrates the integration of DevSecOps principles in a CI/CD pipeline, including secure infrastructure provisioning, container orchestration, and automated security testing. Built as part of a DevSecOps course, it showcases the practical application of secure development lifecycle practices.

---

## 💡 Project Overview

This application helps users track investments, calculate portfolio growth, and fetch real-time stock market data via external APIs. The project implements a full-stack solution with secure DevSecOps practices throughout the development lifecycle.

### Key Features
- Investment portfolio tracking and management
- Real-time stock market data integration (Alpha Vantage API)
- Portfolio growth calculation and analytics
- Secure CRUD operations for managing portfolios
- Containerized microservices architecture
- Prometheus & Grafana monitoring (API metrics, stock trends)
- Docker Compose & Kubernetes deployment support

---

## 🏁 Project Progression
The project is structured to guide users and contributors through a clear progression of DevSecOps practices:
[https://trello.com](https://trello.com/b/VTjAbok5/financial-portfolio-tracker)

---

## 🧰 Technologies Used

- **Python** - Backend application development
- **Flask** - Web framework for API development
- **Node.js** - Frontend application development (React/TypeScript)
- **PostgreSQL** - Database for data persistence
- **Docker** - Application containerization
- **Kubernetes** - Container orchestration and deployment
- **Prometheus** - Monitoring and metrics
- **Grafana** - Visualization and dashboards
- **Bash** - Database initialization scripts

---

## 📁 Project Structure

```
DevSecOps18_FProject/
├── app/                                   # Application source code (Backend & Frontend)
│   ├── Backend/                           # Flask Backend
│   │   ├── Financial_Portfolio_Tracker/   # Modularized CRUD & API logic
│   │   │   ├── Portfolio_Management/      # Portfolio CRUD endpoints (GET, POST, PUT, DELETE)
│   │   │   │   ├── GET/                   # GET portfolio endpoints
│   │   │   │   ├── POST/                  # POST portfolio endpoints
│   │   │   │   ├── PUT/                   # PUT portfolio endpoints
│   │   │   │   ├── DELETE/                # DELETE portfolio endpoints
│   │   │   └── Real_Time_Stock_Data/      # Real-time stock data API integration
│   │   ├── main.py                        # Main Flask app entry point
│   │   ├── requirements.txt               # Python dependencies
│   │   └── flask-dockerfile               # Dockerfile for Flask backend 
│   └── Frontend/                          # React Frontend (TypeScript)
│       ├── public/                        # Static index.html and assets
│       ├── src/                           # React components and logic
│       ├── package.json                   # Node.js project config
│       ├── tsconfig.json                  # TypeScript config
│       ├── Dockerfile                     # Dockerfile for React frontend 
│       ├── tailwind.config.js             # Tailwind CSS config
│       ├── postcss.config.js              # PostCSS config
│       └── requirements.txt               # Optional frontend Python deps
│
├── Docker/                                # Local development setup
│   ├── docker-compose.yml                 # Multi-container orchestration (Postgres, Flask, React, Prometheus, Grafana)
│   ├── init-file/
│   │   └── init-db.sh                     # DB initialization script (auto-run in container)
│
├── Postgres/                              # Kubernetes manifests for PostgreSQL
│   ├── postgres-configmap.yaml            # ConfigMap (DB name)
│   ├── postgres-secret.yaml               # Secret (username/password)
│   ├── postgres-pv.yaml                   # Persistent Volume
│   ├── postgres-pvc.yaml                  # Persistent Volume Claim
│   ├── postgres-deployment.yaml           # Deployment (Postgres container)
│   └── postgres-service.yaml              # Service (internal ClusterIP)
│
├── kubernetes/                            # Kubernetes manifests for app stack
│   ├── flask/                             # Flask API backend
│   │   ├── flask-deployment.yaml          # Flask backend deployment
│   │   ├── flask-service.yaml             # Flask backend service
│   │   └── flask-secret.yaml              # Flask backend secrets
│   ├── Frontend/                          # React frontend app
│   │   ├── frontend-deployment.yaml       # Frontend deployment
│   │   └── frontend-service.yaml          # Frontend service
│   ├── Monitoring/                        # Prometheus & Grafana manifests
│   │   ├── prometheus-deployment.yaml     # Prometheus deployment
│   │   ├── prometheus-service.yaml        # Prometheus service
│   │   ├── prometheus-configmap.yaml      # Prometheus config
│   │   ├── grafana-deployment.yaml        # Grafana deployment
│   │   ├── grafana-service.yaml           # Grafana service
│   │   ├── grafana-dashboard-configmap.yaml      # ConfigMap (all dashboards auto-loaded from ConfigMap at startup)
│   │   ├── grafana-datasource-configmap     # Prometheus datasource config
│   │   ├── frontend-deployment.yaml       # (Optional) monitoring frontend deployment
│   │   └── frontend-service.yaml          # (Optional) monitoring frontend service
│   ├── ingress-nginx-controller.yaml      # Ingress controller manifest
│   ├── ingress.yaml                       # Ingress rules for routing
│
├── grafana/                               # Grafana dashboards and provisioning
│   ├── dashboards/                        # JSON dashboards (api_latency, stock_market_trends, top_gainers)
│   └── provisioning/                      # Datasource and dashboard provisioning
│       ├── dashboards/
│       │   └── dashboard.yaml             # Dashboard provisioning config
│       └── datasources/
│           └── datasource.yaml            # Datasource provisioning config
│
├── Jenkinsfile                            # CI/CD pipeline for build/test/deploy
├── DevSecOps18 - Financial Portfolio Tracker.drawio  # System architecture diagram
└── README.md                              # Project documentation 

```
---

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Kubernetes cluster (local or cloud)
- Python 3.8+

### Installation
**Clone the repository:**
   ```bash
   git clone https://github.com/Yaveenp/DevSecOps18_FProject.git
   cd DevSecOps18_FProject
   ```


 ## Option 1 - Docker Compose
 **Using Docker Compose with buildx option to run locally**
   ```bash
   cd Docker/
   docker-compose up -d --build
   ``` 
      
 ## Option 2 - Kubernetes (with kubeadm)

**Deploy to Kubernetes using kubeadm:**

1. Create the namespace (if not already created):
   ```bash
   kubectl create namespace financial-portfolio
   # Check namespace exists
   kubectl get namespaces | findstr financial-portfolio
   ```

2. Apply Secrets and ConfigMaps:
   ```bash
   kubectl apply -f Postgres/postgres-secret.yaml -n financial-portfolio 
   kubectl apply -f Postgres/postgres-configmap.yaml -n financial-portfolio
   kubectl apply -f kubernetes/flask/flask-secret.yaml -n financial-portfolio
   kubectl apply -f kubernetes/Monitoring/prometheus-configmap.yaml -n financial-portfolio
   kubectl apply -f kubernetes/Monitoring/grafana-datasource-configmap.yaml -n financial-portfolio
   kubectl apply -f kubernetes/Monitoring/grafana-dashboard-configmap.yaml -n financial-portfolio
   kubectl apply -f kubernetes/Monitoring/grafana-dashboard-provider-configmap.yaml -n financial-portfolio
   # Check configmaps and secrets
   kubectl get configmap,secret -n financial-portfolio
   ```

3. Apply Persistent Volumes and Claims (if needed):
   ```bash
   kubectl apply -f Postgres/postgres-pv.yaml -n financial-portfolio
   kubectl apply -f Postgres/postgres-pvc.yaml -n financial-portfolio
   # Check PV and PVC status
   kubectl get pv,pvc -n financial-portfolio
   ```

4. Apply Deployments & Services:
   ```bash
   kubectl apply -f Postgres/postgres-deployment.yaml -n financial-portfolio
   kubectl apply -f kubernetes/flask/flask-deployment.yaml -n financial-portfolio
   kubectl apply -f kubernetes/Frontend/frontend-deployment.yaml -n financial-portfolio
   kubectl apply -f kubernetes/Monitoring/prometheus-deployment.yaml -n financial-portfolio
   kubectl apply -f kubernetes/Monitoring/grafana-deployment.yaml -n financial-portfolio
   kubectl apply -f kubernetes/Monitoring/node-exporter-daemonset.yaml -n financial-portfolio
   kubectl apply -f Postgres/postgres-service.yaml -n financial-portfolio
   kubectl apply -f kubernetes/flask/flask-service.yaml -n financial-portfolio
   kubectl apply -f kubernetes/Frontend/frontend-service.yaml -n financial-portfolio
   kubectl apply -f kubernetes/Monitoring/prometheus-service.yaml -n financial-portfolio
   kubectl apply -f kubernetes/Monitoring/grafana-service.yaml -n financial-portfolio
   kubectl apply -f kubernetes/Monitoring/node-exporter-service.yaml -n financial-portfolio
   # Check deployments and services
   kubectl get deployments,pods,services -n financial-portfolio
   ```

5. Apply Ingress:
   ```bash
   kubectl apply -f kubernetes/ingress.yaml -n financial-portfolio
   kubectl apply -f kubernetes/ingress-nginx-controller.yaml
   # Check ingress
   kubectl get ingress -n financial-portfolio
   kubectl get pods -n ingress-nginx
   kubectl get services -n ingress-nginx  
   ```

6. Final status check:
   ```bash
   kubectl get all -n financial-portfolio
   ```

This order ensures all dependencies are available before pods start. Adjust file paths if your manifests are located elsewhere.

8. To access different parts of the application:
   - Frontend: Open your browser and go to [http://localhost](http://localhost)
   - Grafana: Open your browser and go to [http://localhost:30300](http://localhost:30300)
   - Prometheus: Open your browser and go to [http://localhost:30090](http://localhost:30090)
      
---

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory with the following variables:
```env
# Database Configuration
POSTGRES_HOST: postgres
POSTGRES_PORT: 5432
POSTGRES_DB: investment_db
POSTGRES_USER: admin
POSTGRES_PASSWORD: thisisastrongpassword

# API Configuration
ALPHA_VANTAGE_API_KEY=your_api_key
STOCK_API_URL=https://www.alphavantage.co/query

```

### Database Setup
The database initialization script is located in `Docker/init-file/init-db.sh`. It will automatically set up the required tables and initial data when running with Docker Compose.

---

## 🏗️ Architecture

The application follows a microservices architecture with the following components:

- **Frontend**: React/Node.js application for user interface
- **Backend**: Flask API server handling business logic
- **Database**: PostgreSQL for data persistence
- **Monitoring**: Prometheus for metrics, Grafana for dashboards
- **Container Orchestration**: Kubernetes for deployment and scaling

---

## 🔐 Security Features

This project implements several DevSecOps security practices:
- Container image scanning
- Secret management with Kubernetes secrets
- Infrastructure as Code security scanning
- Automated security testing in CI/CD pipeline
- Database credential encryption

---

## 🧪 Testing 

- Unit and integration tests for backend and frontend
- Security and compliance checks in CI/CD
- Manual and automated API endpoint testing

---

## ⚙️ CI/CD Pipeline Overview

This project uses a robust Jenkins-based CI/CD pipeline to automate code quality checks, testing, containerization, and deployment to Kubernetes. Below are the detailed steps and customizations implemented:

### Pipeline Stages

1. **Lint Flask and React Code**
   - Runs `flake8` on backend Python files for style and error checking.
   - Installs frontend dependencies and runs ESLint for React/TypeScript code.
   - Uses parallel stages for faster linting of both backend and frontend.

2. **Run Unit Tests for Backend**
   - Installs backend Python dependencies.
   - Executes backend unit tests with `pytest`.
   - Runs in a clean Python environment for reliability.

3. **Build and Push Docker Images**
   - Logs in to Docker Hub using Jenkins credentials.
   - Builds multi-architecture Docker images for backend and frontend using Docker Buildx.
   - Pushes images to Docker Hub.
   - Automatically updates image tags in Kubernetes YAML files to use the Jenkins build number, reverting to `latest` if no version is set.

4. **Deploy to Minikube or EKS**
   - Installs `kubectl` in the pipeline agent if not present.
   - Automatically creates the `financial-portfolio` namespace if it does not exist, preventing deployment errors.
   - Applies Kubernetes secrets, configmaps, deployments, services, and ingress manifests to the correct namespace.
   - Checks resource status (configmaps, secrets, pods, services, ingress, etc.) for validation.

5. **Run Prometheus and Grafana**
   - Deploys monitoring tools (Prometheus and Grafana) to Kubernetes.
   - Enables real-time metrics and dashboards for the application.

6. **Perform API Testing**
   - Runs API tests against the live backend deployment using `pytest`.
   - Installs required Python packages for API testing.
   - Ensures endpoints are working as expected after deployment.

7. **Post Actions**
   - Cleans up Docker images used by the pipeline to save space.
   - Removes stopped containers with the pipeline label.
   - Cleans up the Jenkins workspace after pipeline completion.

### Automation Highlights

 - Dynamic image tag updates in manifests for versioned deployments.
 - Namespace creation logic to prevent deployment failures.

**See `Jenkinsfile` for the full pipeline implementation.**


### Test Environment Setup with Docker Desktop and Jenkins

For local testing and development, the pipeline is designed to work seamlessly with Docker Desktop's built-in Kubernetes cluster. Jenkins runs as a container and is configured to access the Kubernetes API by mounting the kubeconfig directory from the host.

To start the Jenkins server container and bind it to your local kubeconfig and persistent Jenkins home, use:

```sh
docker run -d \
  --name jenkins-server \
  -p 8080:8080 -p 50000:50000 \
  -v ~/.kube:/root/.kube \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts
```

This setup allows Jenkins pipeline stages to interact directly with the local Kubernetes cluster, enabling automated deployments and resource management during CI/CD runs.


---

## 📈 API Endpoints

### User Management
- `POST /api/portfolio/signup` - Create new user with an empty portfolio
- `POST /api/portfolio/signin` - User sign-in with portfolio session
  
### Portfolio Management
- `GET /api/portfolio` - Retrieve user portfolios
- `POST /api/portfolio` - Create new portfolio
- `PUT /api/portfolio/{investment_id}` - Update existing portfolio
- `DELETE /api/portfolio/{investment_id}` - Delete portfolio

### Stock Data
- `GET /api/stocks/<ticker>` - Get real-time ticker data 
- `GET /api/stocks/market` - Get market trends (top gainers)

### Portfolio Analytics
- `GET /api/portfolio/analytics` - Get user portfolio profit/loss data and growth trends with comprehensive analytics
- `GET /api/portfolio/analytics/history` - Get historical portfolio analytics for the user
  
### Monitoring
- `/metrics` - Prometheus metrics endpoint (Flask backend)

---

## 📊 Monitoring with Prometheus & Grafana

### Docker Compose

Prometheus and Grafana are included as services in the Docker Compose setup. They are automatically started and networked with the backend and frontend.

- **Prometheus** scrapes metrics from the Flask backend at the `/metrics` endpoint.
- **Node Exporter** is deployed as a DaemonSet and Service in Kubernetes to provide node-level metrics. Prometheus scrapes metrics from node-exporter at `http://node-exporter:9100/metrics`.
- **Grafana** is pre-configured to use Prometheus as a data source and includes dashboards for API latency and stock market trends.

**Access Grafana:**
- Open your browser and go to: [http://localhost:3000](http://localhost:3000)
- Default login: `admin` / `admin`
- Explore dashboards for API and stock market metrics.

**Customizing Dashboards:**
- Edit or add dashboards in `grafana/dashboards/` and they will be automatically loaded by Grafana after deployment. No need to apply a dashboard ConfigMap.

---

## 📝 License

This project is part of a DevSecOps course and is intended for educational purposes only.

---

## 👥 Authors

- **Yaveen Peled** - *Initial work* - [GitHub Profile](https://github.com/Yaveenp)
- **Zohar Zilcha** - *Initial work* - [GitHub Profile](https://github.com/ZoharZil)
- **Alex Voloshin** - *Initial work* - [GitHub Profile](https://github.com/AlexVol400)
---

## 🙏 Acknowledgments

- DevSecOps18 Course instructors and materials from the hitech school in Bar Ilan university [Course Page](https://akadima.biu.ac.il/course-218)
- Open source community for tools and libraries used
- Stock market API "alphavantage" providers for real-time data access

