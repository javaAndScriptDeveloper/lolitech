# Distributed Systems — Lab Submissions

Three incremental submissions exploring distributed communication patterns in Java with Spring Boot.

---

## Submission 1 — gRPC Notification Service

**Stack:** Java 21 · Spring Boot 4 · gRPC · Protocol Buffers

A gRPC server implementing server-side streaming. Clients subscribe once and receive a continuous stream of scheduled messages. The proto contract defines a `NotificationService` with a `SubscribeMessages` RPC that pushes `ScheduledMessage` objects (content + timestamp) until the stream closes.

**Key concepts:** proto IDL, server-side streaming RPC, reactive delivery.

---

## Submission 2 — Greenhouse Flower Registry

**Stack:** Java 21 · Spring Boot 3.3 · gRPC · RabbitMQ · Spring Data JPA · H2

A distributed flower registration system combining two messaging protocols. The `GreenProvider` service exposes a gRPC endpoint that accepts flower registration requests (name, description, soil type, visual parameters). On receipt it persists the entity via JPA and publishes an AMQP event to RabbitMQ. A separate `Greenhouse` consumer picks up messages and processes them asynchronously.

**Key concepts:** hybrid gRPC + AMQP architecture, protobuf serialisation with Jackson, transactional persistence, in-memory H2 for integration testing.

---

## Submission 3 — Peer-to-Peer Node Discovery

**Stack:** Java 17 · Spring Boot 3.4 · Spring Cloud 2024 · OpenFeign · UDP Datagram

A decentralised service mesh where nodes discover each other without a central registry. Each node:

1. Broadcasts its presence on a UDP multicast address at a fixed interval.
2. Listens for broadcasts from peers and registers them locally.
3. Sends REST health notifications to all known peers via OpenFeign clients.
4. Exposes a REST API (`NodeController`) to inspect the current node list.

**Key concepts:** UDP broadcast, Spring Cloud OpenFeign with load balancer, scheduled tasks, P2P topology without Eureka/Consul.
