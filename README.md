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
│   │   │   ├── Portfolio_Management/      # CRUD (GET, POST, PUT, DELETE)
│   │   │   └── Real_Time_Stock_Data/      # API integration for stock data
│   │   ├── main.py                        # Main Flask app entry point
│   │   ├── requirements.txt               # Python dependencies
│   │   └── flask-dockerfile               # Dockerfile for Flask backend 
│   └── Frontend/                          # React Frontend (TypeScript)
│       ├── public/                        # Static index.html
│       ├── src/                           # React components and logic
│       ├── package.json                   # Node.js project config
│       ├── tsconfig.json                  # TypeScript config
│       └── Dockerfile                     # Dockerfile for React frontend 
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
│   ├── postgres-pvc.yaml                  # Persistent Volume Claim
│   ├── postgres-deployment.yaml           # Deployment (Postgres container)
│   └── postgres-service.yaml              # Service (internal ClusterIP)
│
├── kubernetes/                            # Kubernetes manifests for app stack
│   ├── flask/                             # Flask API backend
│   │   ├── flask-deployment.yaml
│   │   ├── flask-service.yaml
│   │   └── flask-secret.yaml
│   ├── frontend/                          # React frontend app
│   │   ├── frontend-deployment.yaml
│   │   └── frontend-service.yaml
│   └── monitoring/                        # Prometheus & Grafana manifests
│       ├── prometheus-deployment.yaml
│       ├── prometheus-service.yaml
│       ├── prometheus-configmap.yaml
│       ├── grafana-deployment.yaml
│       ├── grafana-service.yaml
│       ├── frontend-deployment.yaml
│       └── frontend-service.yaml
│
├── grafana/                               # Grafana dashboards and provisioning
│   ├── dashboards/                        # JSON dashboards (api_latency, stock_market_trends, top_gainers)
│   └── provisioning/                      # Datasource and dashboard provisioning
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
- Terraform (for infrastructure provisioning)

### Installation
**Clone the repository:**
   ```bash
   git clone https://github.com/Yaveenp/DevSecOps18_FProject.git
   cd DevSecOps18_FProject
   ```

 ## Local Opetion 1 - Docker Compose
 **Using Docker Compose with buildx option to run localy**
         ```bash
      cd /Docker
      docker-compose up -d --build --platform linux/amd64,linux/arm64,windows/amd64
      ``` 
      
 ## Local Opetion 2 - Kubernetes 
 **Deploy to Kubernetes:**
         ```bash
      kubectl apply -f Postgres/
      kubectl apply -f kubernetes/flask/
      kubectl apply -f kubernetes/frontend/
      kubectl apply -f kubernetes/monitoring/
      ```
      
## Cloud Opetion 1
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

To deploy monitoring in Kubernetes:

1. Apply the monitoring manifests:
   ```bash
   kubectl apply -f kubernetes/monitoring/
   ```
2. Expose Grafana and Prometheus using NodePort or Ingress as needed.
3. Access Grafana at `http://<NodeIP>:3000` (NodePort 30000 or as configured).
4. Dashboards and Prometheus data source are provisioned automatically from the `grafana/` directory.

**Dashboards:**
- `api_latency_dashboard.json`: API latency and request metrics
- `stock_market_trends_dashboard.json`: Stock market trends and API call frequency
- `top_gainers_dashboard.json`: Top stock gainers percent change over time

**Customizing Dashboards:**
- Edit or add dashboards in `grafana/dashboards/` and they will be loaded automatically on container restart.

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
