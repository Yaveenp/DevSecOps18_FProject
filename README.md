# DevSecOps18 Final Project

Welcome to the **DevSecOps18 Final Project** repository! This project demonstrates the integration of DevSecOps principles across a CI/CD pipeline, incorporating secure infrastructure provisioning, container orchestration, and automated security testing. Built as part of a DevSecOps course, it showcases practical application of secure development lifecycle practices.

---

## 💡 Project Overview

This application helps users track investments, calculate portfolio growth, and fetch real-time stock market data via external APIs. The project implements a full-stack solution with secure DevSecOps practices throughout the development lifecycle.

### Key Features
- Investment portfolio tracking and management
- Real-time stock market data integration
- Portfolio growth calculations and analytics
- Secure CRUD operations for portfolio management
- Containerized microservices architecture

---

## 🧰 Technologies Used

- **Python** - Backend application development
- **Flask** - Web framework for API development
- **Node.js** - Frontend application development
- **PostgreSQL** - Database for data persistence
- **Docker** - Application containerization
- **Kubernetes** - Container orchestration and deployment
- **Terraform** - Infrastructure as Code (IaC)
- **Bash** - Database initialization scripts

---

## 📁 Project Structure

```
DevSecOps18_FProject/
├── app/                                    # Application Backend & Frontend
│   ├── Backend/                           # Full Backend folder
│   │   ├── Financial_Portfolio_Tracker/   # Python code for Portfolio Tracker
│   │   │   ├── Portfolio_Management/      # CRUD Operations
│   │   │   │   ├── DELETE/               # Delete CRUD Operations
│   │   │   │   │   └── DELETE_Portfolio.py
│   │   │   │   ├── GET/                  # GET CRUD Operations
│   │   │   │   │   └── GET_Portfolio.py
│   │   │   │   ├── POST/                 # POST CRUD Operations
│   │   │   │   │   └── POST_Portfolio.py
│   │   │   │   └── PUT/                  # PUT CRUD Operations
│   │   │   │       └── PUT_Portfolio.py
│   │   │   └── Real_Time_Stock_Data/     # Real-time Stock API Operations
│   │   │       ├── GET_Ticker.py        # API integration for ticker data
│   │   │       └── GET_Market_Trends.py # API integration for market trends
│   │   ├── main.py                       # Main Flask application
│   │   └── requirements.txt              # Python dependencies
│   └── Frontend/                         # Full Frontend folder
│       ├── public/
│       │   └── index.html
│       ├── src/                          # Node.js source files
│       ├── package.json                  # Node.js dependencies
│       └── tsconfig.json                 # TypeScript configuration
├── Docker/                               # Docker configuration
│   ├── docker-compose.yml               # Multi-container setup
│   ├── init-db.sh                       # Database initialization script
│   └── requirements.txt                 # Docker-specific requirements
├── Postgres/                            # Kubernetes PostgreSQL manifests
│   ├── postgres-configmap.yaml         # Configuration settings
│   ├── postgres-deployment.yaml        # Deployment specification
│   ├── postgres-pvc.yaml              # Persistent Volume Claim
│   ├── postgres-secret.yaml           # Database credentials
│   └── postgres-service.yaml          # Service definition
├── DevSecOps18 - Financial Portfolio Tracker.drawio  # Architecture diagram
└── README.md                           # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Kubernetes cluster (local or cloud)
- Node.js (v14 or higher)
- Python 3.8+
- Terraform (for infrastructure provisioning)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Yaveenp/DevSecOps18_FProject.git
   cd DevSecOps18_FProject
   ```
2. **Using Docker Compose with buildx option to run localy**
      ```bash
   docker-compose up -d --build --platform linux/amd64,linux/arm64,windows/amd64
   ``` 

3. **Deploy to Kubernetes:**
   ```bash
   kubectl apply -f Postgres/
   # Add additional deployment manifests as needed
   ```

---

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory with the following variables:
```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=portfolio_tracker
DB_USER=your_username
DB_PASSWORD=your_password

# API Configuration
STOCK_API_KEY=your_api_key
STOCK_API_URL=https://api.example.com

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your_secret_key
```

### Database Setup
The database initialization script is located in `Docker/init-db.sh`. It will automatically set up the required tables and initial data when running with Docker Compose.

---

## 🏗️ Architecture

The application follows a microservices architecture with the following components:

- **Frontend**: React/Node.js application for user interface
- **Backend**: Flask API server handling business logic
- **Database**: PostgreSQL for data persistence
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
# need to add
## 🧪 Testing 


---

## 📈 API Endpoints

### Portfolio Management
- `GET /api/portfolio` - Retrieve user portfolios
- `POST /api/portfolio` - Create new portfolio
- `PUT /api/portfolio/{investment_id}` - Update existing portfolio
- `DELETE /api/portfolio/{investment_id}` - Delete portfolio

### Stock Data
- `GET /api/stocks/ticker/{ticker}` - Get real-time ticker data
- `GET /api/stocks/trends` - Get market trends

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

- DevSecOps18 Course instructors and materials
- Open source community for tools and libraries used
- Stock market API "alphavantage" providers for real-time data access