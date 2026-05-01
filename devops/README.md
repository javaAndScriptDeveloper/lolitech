# DevOps — Lab Works

Three labs covering the main DevOps disciplines: CI/CD pipelines, GitOps with FluxCD, and infrastructure provisioning with Terraform.

---

## CI/CD Pipeline ([`ci_cd/`](./ci_cd))

Full delivery pipeline for a Spring Boot application — from source commit to running container on AWS.

---

## GitOps with FluxCD ([`gitops/`](./gitops))

FluxCD v2 cluster configuration demonstrating the GitOps loop: git is the single source of truth and Flux continuously reconciles the cluster state against it.

---

## Infrastructure as Code ([`terraform/`](./terraform))

Modular Terraform configuration that provisions a full AWS environment — VPC, subnet, security group, and an EC2 instance — using the official AWS provider and the community EC2 module.
