![AWS Architecture Diagram](images/architecture.png)



HumanGov is a secure, multi-tenant Software-as-a-Service (SaaS) Human Resources application designed for government agencies.

This project demonstrates the architecture and deployment of the HumanGov platform using a **production-grade, Zero-Trust infrastructure** on AWS. The entire stack—from the VPC networking to the Application Layer—is provisioned using **Terraform** modules and orchestrated via **Amazon EKS (Elastic Kubernetes Service)**.

The solution emphasizes **security, scalability, and automation**, moving away from manual "ClickOps" to a fully automated Infrastructure-as-Code (IaC) and Continuous Delivery workflow.

---

      Architecture Design

The architecture follows the **AWS Well-Architected Framework**, prioritizing security and operational excellence.

![Architecture Diagram](humangov_aws_architecture_(us-east-1).png)
*(Generated programmatically using Python Diagrams)*

    Key Components
    **Networking:** A custom VPC with strict Public/Private subnet isolation.
*   **Compute:** Amazon EKS cluster with worker nodes isolated in private subnets.
*   **Traffic Management:** AWS Application Load Balancer (ALB) managed via the Kubernetes Ingress Controller.
*   **Edge Security:** AWS WAF (Web Application Firewall) attached to the ALB to block SQL injection and common exploits.
*   **Data Persistence:** Amazon DynamoDB (State Storage) and S3 (File Storage).
*   **CI/CD:** A fully automated pipeline using AWS CodePipeline and CodeBuild.

---

## 🔐 "Gold Standard" Security Implementation

This project implements a **Zero-Trust** security model, suitable for sensitive government data.

### 1. Network Isolation
*   **Private Nodes:** EKS Worker nodes reside in **Private Subnets** with NO Public IP addresses. They communicate with the internet solely via a NAT Gateway.
*   **Ingress Routing:** Application traffic is routed strictly through the ALB Ingress, with no direct access to pods allowed.

### 2. Identity & Access Management (IRSA)
*   **No Access Keys:** The application does *not* use hardcoded AWS Access Keys.
*   **OIDC Federation:** Kubernetes Service Accounts are mapped to AWS IAM Roles using OpenID Connect (OIDC).
*   **Least Privilege:** The application pod is granted permissions *only* to its specific S3 bucket and DynamoDB table via IAM policies.

### 3. Encryption & Secret Management
*   **KMS Envelope Encryption:** The Kubernetes `etcd` database secrets are encrypted at rest using AWS KMS.
*   **Secrets Store CSI Driver:** Sensitive credentials (like DB passwords) are mounted directly from AWS Secrets Manager into pods as volumes, bypassing environment variables.

---

## 🚀 CI/CD Pipeline Workflow

The project features a **Continuous Delivery** pipeline provisioned entirely via Terraform (`modules/cicd`).

1.  **Source:** AWS CodeStar connection watches the **GitHub Repository** for changes.
2.  **Build:** AWS CodeBuild:
    *   Authenticates with the Private **ECR Repository**.
    *   Builds the Docker Image.
    *   Tags the image with the **Git Commit Hash** (Immutable Versioning).
    *   Pushes the image to ECR.
3.  **Deploy:** CodeBuild authenticates with the private EKS cluster (via IAM RBAC mapping) and updates the Kubernetes workloads using `kubectl`.

![CI/CD Pipeline](screenshots/pipeline-success.png)

---

## 📂 Repository Structure

The project follows a modular Terraform structure for maintainability.

```bash
human-gov-project/
├── buildspec.yml                   # CI/CD instructions
├── human-gov-application/          # Application Source Code
│   └── src/
│       ├── Dockerfile              # Container definition
│       └── humangov-california.yaml # Kubernetes Manifests
│
└── human-gov-infrastructure/       # Infrastructure as Code
    └── terraform/
        ├── main.tf                 # Root Manager
        └── modules/
            ├── network/            # VPC, Subnets, NAT Gateway
            ├── eks/                # Cluster, Node Groups, OIDC, IRSA, Add-ons
            ├── cicd/               # CodePipeline, CodeBuild, IAM Roles
            └── application/        # S3 Buckets, DynamoDB Tables
📸 Deployment Evidence
1. Application Running on EKS
Live application accessible via Route 53 domain (humangovv.click) with secure HTTPS.
![alt text](screenshots/app-running.png)
2. Secure Private Nodes
Proof that worker nodes have no Public IP addresses (Security Best Practice).
![alt text](screenshots/private-nodes.png)
3. Ingress Controller & ALB
The AWS Load Balancer Controller dynamically provisioning the ALB based on Ingress YAML.
![alt text](screenshots/alb-console.png)
4. ECR Artifact Versioning
Docker images tagged with Git Commit hashes for traceability.
![alt text](screenshots/ecr-repo.png)
💻 How to Deploy
Prerequisites
Terraform installed (v1.5+).
AWS CLI configured.
kubectl installed.
Step 1: Provision Infrastructure
We use a layered approach to prevent dependency conflicts.
code
Powershell
cd human-gov-infrastructure/terraform
terraform init

# Phase 1: Build Network & Cluster Foundation
terraform apply -target="module.network" -target="module.eks"

# Phase 2: Deploy Services, Databases, and CI/CD
terraform apply
Step 2: Configure DNS
Get the ALB Address: kubectl get ingress
Update Route 53 CNAME records to point to the ALB address.
Step 3: Trigger Deployment
Push a change to the GitHub repository. The pipeline will automatically build the Docker image and deploy the application to the cluster.
code
Powershell
git add .
git commit -m "Trigger deployment"
git push