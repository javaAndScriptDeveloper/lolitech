# CI/CD Pipeline — Lab Work

End-to-end delivery pipeline for a Spring Boot application: code push → Docker image build → image pushed to Docker Hub → EC2 instance provisioned and container started.

**Stack:** Java 21 · Spring Boot · Gradle · Docker · GitHub Actions · Terraform · Kubernetes · Kustomize · Jenkins

---

## Application

A minimal Spring Boot service (`HelloWorldController`) that exposes a single endpoint on port 8080. The application itself is intentionally simple — the focus is the pipeline around it.

---

## Docker

The `Dockerfile` uses `gradle:8.5.0-jdk21` as the build image. It copies the full Gradle wrapper and source, runs `./gradlew build`, and starts the app with `bootRun` on container launch.

---

## GitHub Actions

Two chained workflows in `.github/workflows/`:

**`docker-image.yml`** — triggers on every push to any branch:
- Sets up QEMU and Docker Buildx for multi-architecture builds.
- Logs in to Docker Hub using repository secrets.
- Builds and pushes the image (`vampir/app:latest`) only when the push is to `main`; other branches build but don't push.

**`terraform.yml`** — triggers automatically when `docker-image` completes:
- Runs `terraform init`, `terraform plan`, and `terraform apply -auto-approve` against `./terraform/`.
- AWS credentials are passed from repository secrets as Terraform variables.
- Provisions (or updates) the EC2 instance in `eu-north-1` where the fresh image will run.

---

## Terraform (`terraform/`)

Provisions an AWS EC2 `t3.micro` instance (Ubuntu, region `eu-north-1`) with:
- A security group allowing inbound SSH (22) and HTTP (80).
- A `user_data` bootstrap script that installs Docker, pulls `vampir/app`, and starts it as a detached container.

---

## Kubernetes (`k8s/`)

An alternative deployment path for running the app in a cluster:
- `deployment.yaml` — 2-replica Deployment selecting pods by `app: spring-app`.
- `service.yaml` — NodePort Service forwarding port 8080.
- `kustomization.yaml` — Kustomize entry point grouping both resources, ready to be applied with `kubectl apply -k k8s/`.

---

## Jenkinsfile

A two-stage declarative pipeline as an alternative to GitHub Actions: **Build** (`docker build`) → **Push** (`docker push`). Runs on any Jenkins agent.
