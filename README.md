# DevSecOps18 Final Project

Welcome to the **DevSecOps18 Final Project** repository! This project demonstrates the integration of DevSecOps principles across a CI/CD pipeline, incorporating secure infrastructure provisioning, container orchestration, and automated security testing. Built as part of a DevSecOps course, it showcases practical application of secure development lifecycle practices.

---

## 💡 Project Overview

This application helps users track investments, calculate portfolio growth, and fetch real-time stock market data via external APIs. The project implements a full-stack solution with secure DevSecOps practices throughout the development lifecycle.

### Key Features
- Investment portfolio tracking and management
- Real-time stock market data integration (Alpha Vantage API)
- Portfolio growth calculations and analytics
- Secure CRUD operations for portfolio management
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
- **Terraform** - Infrastructure as Code (IaC)
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
│       │   ├── components/                # Main dashboard and UI components
│       │   │   ├── PortfolioDashboard.js  # Main dashboard component (JS)
│       │   │   ├── 1PortfolioDashboard.tsx# Main dashboard component (TS)
│       │   ├── App.js                     # App entry point
│       │   ├── App.css                    # App styles
│       │   ├── index.js                   # React entry point
│       │   ├── index.css                  # Global styles
│       ├── package.json                   # Node.js project config
│       ├── tsconfig.json                  # TypeScript config
│       ├── Dockerfile                     # Dockerfile for React frontend 
│       ├── react-dockerfile               # Alternative Dockerfile for React
│       ├── tailwind.config.js             # Tailwind CSS config
│       ├── postcss.config.js              # PostCSS config
│       └── requirements.txt               # Optional frontend Python deps
│
├── Docker/                                # Local development setup
│   ├── docker-compose.yml                 # Multi-container orchestration (Postgres, Flask, React, Prometheus, Grafana)
│   ├── init-file/
│   │   └── init-db.sh                     # DB initialization script (auto-run in container)
│   └── requirements.txt                   # Optional: Docker build-specific Python deps
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

---

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Kubernetes cluster (local or cloud)
- Python 3.8+
- Terraform (for infrastructure provisioning)

### Installation
**Clone the repository:**
   ```bash
   git clone https://github.com/Yaveenp/DevSecOps18_FProject.git
   cd DevSecOps18_FProject
   ```

 ## Local Option 1 - Docker Compose
 **Using Docker Compose with buildx option to run localy**
   ```bash
   cd /Docker
   docker-compose up -d --build
   ``` 
      
 ## Local Option 2 - Kubernetes (with kubeadm)

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

4. Apply Deployments:
   ```bash
   kubectl apply -f Postgres/postgres-deployment.yaml -n financial-portfolio
   kubectl apply -f kubernetes/flask/flask-deployment.yaml -n financial-portfolio
   kubectl apply -f kubernetes/Frontend/frontend-deployment.yaml -n financial-portfolio
   kubectl apply -f kubernetes/Monitoring/prometheus-deployment.yaml -n financial-portfolio
   kubectl apply -f kubernetes/Monitoring/grafana-deployment.yaml -n financial-portfolio
   # Check deployments and pods
   kubectl get deployments,pods -n financial-portfolio
   ```

5. Apply Services:
   ```bash
   kubectl apply -f Postgres/postgres-service.yaml -n financial-portfolio
   kubectl apply -f kubernetes/flask/flask-service.yaml -n financial-portfolio
   kubectl apply -f kubernetes/Frontend/frontend-service.yaml -n financial-portfolio
   kubectl apply -f kubernetes/Monitoring/prometheus-service.yaml -n financial-portfolio
   kubectl apply -f kubernetes/Monitoring/grafana-service.yaml -n financial-portfolio
   # Check services
   kubectl get services -n financial-portfolio
   ```

6. Apply Ingress:
   ```bash
   kubectl apply -f kubernetes/ingress.yaml -n financial-portfolio
   kubectl apply -f kubernetes/ingress-nginx-controller.yaml
   # Check ingress
   kubectl get ingress -n financial-portfolio
   kubectl get pods -n ingress-nginx
   kubectl get services -n ingress-nginx  
   ```

7. Final status check:
   ```bash
   kubectl get all -n financial-portfolio
   ```

This order ensures all dependencies are available before pods start. Adjust file paths if your manifests are in different locations.
      
## Cloud Option 1
**Deploy to AWS using Terraform:**
   ```bash
   **Need to add Terraform**
   ```
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

# Flask Configuration
FLASK_ENV=development
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
- **Infrastructure**: Terraform for cloud resource provisioning

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

## 📈 API Endpoints

### User Management
- `POST /api/portfolio/signup` - Create new user with empty portfolio
- `POST /api/portfolio/signin` - User signin with portfolio session
  
### Portfolio Management
- `GET /api/portfolio` - Retrieve user portfolios
- `POST /api/portfolio` - Create new portfolio
- `PUT /api/portfolio/{investment_id}` - Update existing portfolio
- `DELETE /api/portfolio/{investment_id}` - Delete portfolio

### Stock Data
- `GET /api/stocks/<ticker>` - Get real-time ticker data 
- `GET /api/stocks/market` - Get market trends (top gainers)

### Portfolio Analytics
- `GET /api/portfolio/analytics` - Get User portfolio profit/loss data and growth trends with comprehensive analytics
- `GET /api/portfolio/analytics/history` - Get historical portfolio analytics for the current user
  
### Monitoring
- `/metrics` - Prometheus metrics endpoint (Flask backend)

---

## 📊 Monitoring with Prometheus & Grafana

### Docker Compose

Prometheus and Grafana are included as services in the Docker Compose setup. They are automatically started and networked with the backend and frontend.

- **Prometheus** scrapes metrics from the Flask backend at `/metrics`.
- **Grafana** is pre-configured to use Prometheus as a data source and includes dashboards for API latency and stock market trends.

**Access Grafana:**
- Open your browser and go to: [http://localhost:3000](http://localhost:3000)
- Default login: `admin` / `admin`
- Explore dashboards for API and stock market metrics.

### Kubernetes
- Open your browser and go to: [http://localhost:30300](http://localhost:3000)

**Customizing Dashboards:**
- Edit or add dashboards in `grafana/dashboards/` and they will be automatically loaded by Grafana after deployment. No need to apply a dashboard ConfigMap.

---

## 📝 License

This project is part of a DevSecOps course and is intended for educational purposes.

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

