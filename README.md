# University Coursework — KPI

Lab works and project submissions from my studies at **Kyiv Polytechnic Institute (KPI)**. Each directory is a separate subject, progressing from low-level systems programming through distributed microservices.

---

## Subjects

| Directory | Subject | Stack |
|-----------|---------|-------|
| [`defi/`](./defi) | Distributed Systems | Java · Spring Boot · gRPC · RabbitMQ · Spring Cloud |
| [`mobile/`](./mobile) | Android Development | Java · Kotlin · Android SDK · Material Design |
| [`system_programming/`](./system_programming) | System Programming | C · C++ · ARM Assembly · Linux kernel API |
| [`statistics/`](./statistics) | Statistics & Experimental Design | Python · NumPy · SciPy |
| [`agentic_algorithms/`](./agentic_algorithms) | Agentic Algorithms | Python · NumPy · Flask · Pygame · SQLite |
| [`big_data/`](./big_data) | Big Data | Python · PySpark · Hadoop HDFS · YARN · Hive · Docker |
| [`devops/`](./devops) | DevOps | Docker · GitHub Actions · Terraform · AWS · Kubernetes · FluxCD |
| [`neural_networks/`](./neural_networks) | Neural Networks & Deep Learning | Python · PyTorch · scikit-learn |

---

## Highlights

- **[Distributed Systems](./defi)** — built three progressively complex distributed services: gRPC server-side streaming, hybrid gRPC + RabbitMQ messaging with JPA persistence, and a peer-to-peer network using UDP broadcast + Spring Cloud OpenFeign.
- **[Android](./mobile)** — four Android apps covering fragment navigation, custom time arithmetic, graph rendering with MPAndroidChart/GraphView, and a full multi-screen app with charts and a film catalogue.
- **[System Programming](./system_programming)** — C/C++ CLI tools and Linux kernel modules (ring-0), then bare-metal ARM firmware, bootloader, and kernel written in Assembly.
- **[Statistics](./statistics)** — statistical experiment design using full factorial $2^3$ DOE, coded variables, Cochran's test, and response surface regression.
- **[Agentic Algorithms](./agentic_algorithms)** — ACO metaheuristic for TSP, an evolutionary life simulation where agents grow neural networks through mutation, and a multi-source cryptocurrency event monitor correlating raw HTTP and NNTP signals.
- **[Big Data](./big_data)** — end-to-end pipeline over a 1M-row dataset: PySpark MapReduce job with broadcast variables for currency conversion, results stored in HDFS and exposed via an external Hive table, full cluster running locally in Docker Compose (Hadoop + YARN + Spark + Hive + PostgreSQL).
- **[DevOps](./devops)** — CI/CD pipeline chaining GitHub Actions (multi-arch Docker build → Terraform EC2 deploy) with a Jenkins alternative and Kubernetes manifests; FluxCD v2 GitOps setup reconciling a live cluster from git; modular Terraform provisioning a VPC, subnet, security group, and EC2 instance on AWS.
- **[Neural Networks](./neural_networks)** — CNN hyperparameter tuning and training on FashionMNIST with custom architecture and ResNet variants using PyTorch, with model serving for inference.

---

## License

[MIT](./LICENSE) — free to use as reference or inspiration.
