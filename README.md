# SDN NetDevOps Project

A reproducible Software-Defined Networking (SDN) lab that combines **Ryu**, **Mininet**, **Ansible**, **Docker**, **Prometheus**, **Grafana**, and **GitHub Actions** to demonstrate **Network Automation**, **Policy as Code**, **Infrastructure as Code**, and **CI/CD for SDN environments**.

---

## Project Overview

This project implements an automated SDN environment based on a simplified datacenter topology. It allows:

- deploying a Ryu controller in Docker
- creating a Mininet-based SDN topology
- applying **firewall** and **QoS** policies automatically
- validating network behavior through automated tests
- monitoring switch statistics with Prometheus and Grafana
- running CI/CD pipelines with GitHub Actions

The project follows a **NetDevOps** approach by separating:

- controller logic
- infrastructure definition
- policy definition
- deployment automation
- testing
- observability

---

## Objectives

The main objectives of this project are:

- automate the deployment of an SDN lab
- manage network policies as code
- validate network behavior automatically in CI
- provide a persistent lab environment for experimentation
- monitor SDN metrics using Prometheus and Grafana

---

## Project Architecture

The workflow of the project is the following:

1. **Ryu controller** is started inside a Docker container
2. **Mininet topology** connects OpenFlow switches to the controller
3. **Firewall and QoS policies** are loaded from JSON files and pushed through Ryu REST APIs
4. **Automated tests** verify connectivity, blocking rules, and QoS behavior
5. **Ryu exporter** exposes metrics to Prometheus
6. **Grafana** visualizes the collected metrics

---

## Project Structure

```bash
sdn-netdevops-project/
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
│
├── ansible/
│   ├── inventory.ini
│   ├── deploy.yml
│   ├── deploy_ci.yml
│   ├── deploy_lab.yml
│   └── roles/
│       ├── controller/
│       │   └── tasks/
│       │       ├── main.yml
│       │       ├── ci.yml
│       │       └── lab.yml
│       ├── firewall/
│       │   └── tasks/
│       │       └── main.yml
│       ├── monitoring/
│       │   └── tasks/
│       │       └── main.yml
│       └── topology/
│           └── tasks/
│               ├── main.yml
│               ├── ci.yml
│               └── lab.yml
│
├── controller/
│   ├── main_controller.py
│   └── policies/
│       ├── firewall.json
│       └── qos.json
│
├── docker/
│   ├── Dockerfile
│   └── Dockerfile.exporter
│
├── iac/
│   └── controller_config.yml
│
├── monitoring/
│   └── prometheus.yml
│
├── scripts/
│   ├── deploy_policies.py
│   └── ryu_exporter.py
│
├── tests/
│   ├── network_tests.py
│   └── validate_lab.py
│
├── topology/
│   ├── datacenter_topo.py
│   └── start_lab_topology.py
│
└── docker-compose.yml