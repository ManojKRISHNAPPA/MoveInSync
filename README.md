# MoveInSync Clone
**Employee Transportation Management System** - built with Streamlit + Python + SQLite

---

## Features

### Employee Portal
- Self-registration with employee ID, department, home address
- Book cab (Home to Office or Office to Home)
- Select route, shift, and travel date
- View / cancel bookings with real-time status
- Profile page

### Admin Panel
- Live overview dashboard with charts
- View & manage all bookings; update status; assign cabs
- Employee roster
- Fleet management (add cabs, assign drivers)
- Route management (add new routes)
- Driver management (add driver accounts)
- Shift management (configure shift timings & cab times)

### Driver Portal
- View today's assigned trips
- Start trip (`confirmed` -> `in_progress`)
- Mark trip as completed (`in_progress` -> `completed`)
- Full trip history with filters

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
streamlit run app.py
```
The app opens at **http://localhost:8501**

---

## Default Credentials

| Role  | Email             | Password |
|-------|-------------------|----------|
| Admin | admin@company.com | admin123 |

Employees register themselves. Drivers are added by the admin.

---

## Recommended First-Time Flow
1. Log in as **Admin**
2. Go to **Drivers** -> Add a driver (e.g. DRV001)
3. Go to **Fleet / Cabs** -> Add a cab, assign the driver
4. Log out, then **Register** as a new employee
5. Log in as the employee -> **Book a Cab**
6. Log back in as Admin -> **All Bookings** -> confirm / assign cab
7. Log in as Driver -> **Dashboard** -> Start and complete the trip

---

## Tech Stack

| Layer          | Technology        |
|----------------|-------------------|
| Frontend       | Streamlit 1.32+   |
| Backend        | Python 3.10+      |
| Database       | SQLite (built-in) |
| Auth           | SHA-256 hashing   |
| Container      | Docker            |
| CI/CD          | Jenkins           |
| Registry       | AWS ECR           |
| Orchestration  | Kubernetes (EKS)  |

---

## Project Structure
```
MoveInSync/
├── app.py                      # Streamlit UI (all pages & navigation)
├── database.py                 # SQLite data layer (CRUD + analytics)
├── requirements.txt            # App dependencies
├── requirements-test.txt       # Test dependencies (pytest, pytest-cov)
├── Dockerfile                  # Container build (non-root user)
├── deployment.yml              # Kubernetes Deployment + Service manifest
├── Jenkinsfile                 # CI/CD pipeline (DevSecOps)
├── sonar-project.properties    # SonarQube configuration
├── dockerfile-security.rego    # OPA policy rules for Dockerfile
├── opa-k8s-security.rego       # OPA policy rules for Kubernetes manifests
├── trivy-docker-image-scan.sh  # Trivy base image vulnerability scanner
├── tests/
│   ├── __init__.py
│   └── test_database.py        # Unit tests for database.py (60+ tests)
└── README.md
```
The SQLite database file `moveinsync.db` is created automatically on first run.

---

## DevSecOps Pipeline

The Jenkins pipeline implements the following stages:

```
1.  Git Checkout
2.  Install Dependencies
3.  Unit Tests & Coverage       pytest + pytest-cov -> coverage.xml
4.  SonarQube Analysis          sonar-scanner (withSonarQubeEnv)
5.  Quality Gate                waitForQualityGate (aborts on failure)
6.  Dependency Vulnerability    pip-audit on requirements.txt
7.  Security Scan & Docker Build  (runs in parallel)
    |-- Trivy Base Image Scan   HIGH (info) + CRITICAL (blocks)
    |-- OPA Dockerfile Rules    conftest + dockerfile-security.rego
    +-- Docker Build            docker build
8.  ECR Login
9.  Tag for ECR
10. Push to ECR
11. OPA Kubernetes Rules        conftest + opa-k8s-security.rego
12. Update GitOps Deployment    sed image tag + git push to gitops repo
```

### Running Tests Locally
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run tests with coverage
pytest tests/ -v --cov=. --cov-report=term-missing
```

### OPA Policy Checks
```bash
# Validate Dockerfile
docker run --rm -v $(pwd):/project openpolicyagent/conftest test \
  --policy dockerfile-security.rego Dockerfile

# Validate Kubernetes manifest
docker run --rm -v $(pwd):/project openpolicyagent/conftest test \
  --policy opa-k8s-security.rego deployment.yml
```

### Trivy Scan
```bash
bash trivy-docker-image-scan.sh
```

---

## Jenkins Prerequisites

| Requirement    | Details                                          |
|----------------|--------------------------------------------------|
| SonarQube      | Server named `SonarQube` in Jenkins global config |
| sonar-scanner  | Installed on Jenkins agent                       |
| Trivy          | Installed on Jenkins agent                       |
| Docker         | Available on Jenkins agent                       |
| AWS CLI        | Configured for ECR access (region ap-northeast-1) |
| Credentials    | `github-creds` (username/password) in Jenkins    |

---

## Security Practices

| Practice                  | Tool / Approach                    |
|---------------------------|------------------------------------|
| Unit testing              | pytest with 60+ test cases         |
| Code quality & SAST       | SonarQube with quality gate        |
| Dependency scanning       | pip-audit                          |
| Container image scanning  | Trivy (blocks on CRITICAL CVEs)    |
| Dockerfile policy         | OPA / Conftest                     |
| Kubernetes policy         | OPA / Conftest                     |
| Non-root container        | `USER appuser` in Dockerfile       |
| GitOps deployment         | Image tag update via git push      |
