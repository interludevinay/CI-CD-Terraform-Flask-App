# 🚀 CI/CD Pipeline Project with Jenkins, Terraform, Docker & AWS EC2

This project demonstrates the deployment of a **Flask-based ToDo Application** using a **CI/CD pipeline** built with **Jenkins**, **Terraform**, **Docker**, and **AWS EC2**.  
The pipeline automates the **build, deployment, and infrastructure management** process, following a **Master–Agent Jenkins architecture**.

---

## 📑 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
  - [High-Level Overview](#1-high-level-overview)
  - [Component Map](#2-component-map-who-owns-which-responsibility)
  - [End-to-End Flow](#3-end-to-end-flow-control-vs-data)
  - [Control vs Data Path](#4-control-vs-data-path)
  - [Diagram](#5-diagram)
  - [Key Benefits](#6-key-benefits)
- [Prerequisites](#-prerequisites)
- [How the Pipeline Works](#-how-the-pipeline-works)
- [Project Folder Structure](#-project-folder-structure)
- [Pipeline Stages](#-pipeline-stages)
- [Components](#️-components)
  - [Jenkins Master](#-jenkins-master-ec2-master)
  - [Jenkins Slave](#-jenkins-slave-ec2-slave)
  - [Terraform](#-terraform)
  - [Docker & DockerHub](#-docker--dockerhub)
  - [AWS EC2](#-aws-ec2)
  - [Flask ToDo App](#-flask-todo-app)

---

## 📖 Overview
This project automates the deployment of a **Flask ToDo Application** containerized with Docker and deployed on AWS EC2 via Terraform.  

- **Jenkins Master (EC2-Master)** orchestrates jobs.  
- **Jenkins Agent (EC2-Slave)** executes all tasks: cloning code, building Docker images, pushing to DockerHub, provisioning infra with Terraform, and deploying the app.  
- **Terraform** provisions the AWS EC2 runtime environment.  
- **DockerHub** acts as the image registry.  
- The **Flask ToDo App** runs on the provisioned EC2 instance and is accessible via its public IP.  

---

## 🏗️ Architecture

### 1) High-Level Overview

- **Control Plane**
  - **Jenkins Master (EC2-Master)**:  
    Orchestrates jobs, provides UI, holds credentials, triggers pipelines.  
    👉 *Does not build or deploy.*

- **Execution Plane**
  - **Jenkins Agent (EC2-Slave)**:  
    Executes pipeline stages: clone, build, push, Terraform infra, deploy, cleanup.  
    👉 Holds Terraform state and Docker runtime.

- **Runtime Plane**
  - **App EC2 (Terraform-managed)**:  
    Provisioned on demand by Terraform.  
    👉 Runs the Flask ToDo app container pulled from DockerHub.

- **Registries & Repos**
  - **GitHub**: Source of truth for app, Terraform, and Jenkinsfile.  
  - **DockerHub**: Stores container images.

---

### 2) Component Map (Who owns which responsibility?)

| Layer            | Component                     | Purpose                                                                                           |
|------------------|-------------------------------|---------------------------------------------------------------------------------------------------|
| Source           | GitHub                        | Hosts `flask_todo_app/`, `Jenkinsfile`, `terraform/`. Triggers Jenkins via webhook/polling.       |
| Orchestration    | Jenkins **Master** (EC2-Master)| Receives triggers, schedules job on Agent, holds credentials, shows logs/UI.                     |
| Execution        | Jenkins **Agent** (EC2-Slave) | Executes pipeline steps; runs Docker & Terraform; SSH to App EC2; collects outputs.              |
| Image Registry   | DockerHub                     | Stores built images (e.g., `username/flask-todo:build-123`, `:latest`).                          |
| Infra Provision  | Terraform (on Agent)          | Creates **App EC2** + Security Group + KeyPair; outputs public IP.                               |
| Runtime Host     | **App EC2** (Terraform)       | Pulls image from DockerHub and runs the Flask container.                                          |

---

### 3) End-to-End Flow (Control vs Data)

#### 🔹 Step 1 — Developer Push
- Code pushed → **GitHub**.  
- Webhook triggers **Jenkins Master**.

#### 🔹 Step 2 — Jenkins Master Delegation
- Master forwards job to **Jenkins Agent (Slave)**.

#### 🔹 Step 3 — Agent Executes Pipeline
1. Clone repo from GitHub.  
2. Build Docker image.  
3. Push image to DockerHub.  

#### 🔹 Step 4 — Provision Infra
- Agent runs Terraform → provisions **App EC2** + security group + outputs public IP.

#### 🔹 Step 5 — Deploy App
- Agent SSHs into EC2.  
- Installs Docker (if missing).  
- Pulls image → runs container on port 5000.

#### 🔹 Step 6 — Verification
- Jenkins checks app health at `http://<EC2_IP>:5000`.

#### 🔹 Step 7 — Teardown
- With approval → Terraform `destroy` removes infra to save cost.

---

### 4) Control vs Data Path

- **Control Path**: GitHub → Jenkins Master → Jenkins Agent → Terraform → AWS  
- **Data Path**: Jenkins Agent → DockerHub → App EC2 → Browser (end user)

---

### 5) Diagram
<img width="1536" height="1024" alt="Image" src="https://github.com/user-attachments/assets/6bd7ab21-8f43-46f9-8f39-ed0fc2a54572" />

---

### 6) Key Benefits
- 🔄 Immutable deployment with Docker.  
- ☁️ Infrastructure as Code with Terraform.  
- 🔐 Clear separation of roles (Master vs Agent).  
- ⚡ Scalable with more agents.  
- 💰 Cost-efficient with teardown stage.  

## 🔑 SSH Key Setup for Jenkins ↔ EC2

For Jenkins to securely connect and deploy into the **Terraform-provisioned EC2 instance**, we configure an SSH key pair.

### 1) Generate SSH Key Pair
Run the following command on your Jenkins Agent (Slave):

```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/jenkins-ec2 -C "jenkins-ec2"
```
## 🔑 2) Generated Files

When you generate the SSH key pair, it creates two files:

### 1. Private Key → `~/.ssh/jenkins-ec2`
- Must be **kept secret**.  
- Add this key into **Jenkins Credentials** (type: *SSH private key*).  

### 2. Public Key → `~/.ssh/jenkins-ec2.pub`
- Safe to **share**.  
- Add this to **EC2 Instance (`~/.ssh/authorized_keys`)** so Jenkins can SSH.  

---

## ✅ Prerequisites
- AWS Account  
- Jenkins Master on **EC2-Master**  
- Jenkins Agent (Slave) configured  
- Terraform installed on Slave  
- Docker installed on Slave & App EC2  
- GitHub repo with Flask app + Jenkinsfile + Terraform  
- DockerHub account  

---

## ⚡ How the Pipeline Works

1. **Developer Pushes Code** → GitHub.  
2. **Jenkins Master Triggers Pipeline** → Delegates job to Slave.  
3. **Slave Executes Build & Deploy**:
   - Clone repo  
   - Build & push Docker image to DockerHub  
   - Provision AWS EC2 via Terraform  
   - Deploy app container on EC2  
4. **Access App** → `http://<EC2_PUBLIC_IP>:5000`.  
5. **Manual Approval & Teardown** → `terraform destroy` cleans infra.  

---

## 📂 Project Folder Structure

```bash
├── flask_todo_app/       # Flask ToDo application source code
│   ├── app.py            # Main Flask app
│   ├── templates/        # HTML templates
│   ├── static/           # CSS/JS files
│   └── requirements.txt  # Python dependencies
├── Dockerfile            # Docker image definition
├── Jenkinsfile           # Jenkins pipeline definition
├── terraform/            # Terraform scripts to provision AWS resources
│   ├── main.tf           # EC2 creation code
│   ├── variables.tf      # Input variables
│   └── outputs.tf        # Outputs (EC2 Public IP, etc.)
└── README.md             # Project documentation
```

---
## 🔄 Pipeline Stages

The CI/CD pipeline consists of the following stages:

1. **Declarative: Checkout SCM**  
   - Clone the source code from GitHub repository.

2. **Clone**  
   - Prepare and pull the latest source code.

3. **Docker Image**  
   - Build the Docker image for the Flask ToDo application.

4. **Docker Image Push To DockerHub**  
   - Push the built Docker image to DockerHub for distribution.

5. **Plan and Apply (Terraform)**  
   - Use Terraform to provision AWS EC2 instances (for deployment).

6. **Get EC2 Public IP**  
   - Retrieve the IP of the created EC2 instance to access the app.

7. **SSH to EC2 and Run Container**  
   - Connect via SSH and run the containerized application on the EC2 instance.

8. **Destroy Approval**  
   - Wait for manual approval before destroying infrastructure.

9. **Destroy Resources**  
   - Terraform destroys the created EC2 instances and cleans resources.

---

## ⚙️ Components

### 🔹 Jenkins Master (EC2-Master)
- Orchestrates the pipeline.
- Runs on an AWS EC2 instance.
- Manages Jenkins UI and triggers pipeline jobs.

### 🔹 Jenkins Slave (EC2-Slave)
- Executes all pipeline tasks delegated by the master.
- Builds Docker images, runs Terraform, and connects to EC2 instances.
- Ensures scalability and workload distribution.

### 🔹 Terraform
- Automates AWS EC2 instance creation.
- Defines infrastructure as code (IaC).
- Ensures reproducibility of environments.

### 🔹 Docker & DockerHub
- **Docker**: Containerizes the Flask ToDo App.  
- **DockerHub**: Centralized registry to push/pull application images.

### 🔹 AWS EC2
- **EC2 Instance** runs the deployed Docker container.  
- Provides a public IP to access the Flask ToDo application.

### 🔹 Flask ToDo App
- A simple **ToDo application** built using Flask.  
- Source code resides inside the `flask_todo_app/` folder.  
- Features CRUD (Create, Read, Update, Delete) operations for managing tasks.






