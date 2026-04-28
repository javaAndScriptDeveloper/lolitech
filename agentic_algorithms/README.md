# Agentic Algorithms — Lab Works

Three labs on autonomous agent systems: a metaheuristic optimizer, an evolutionary life simulation, and a multi-source event monitor.

**Stack:** Python · NumPy · Matplotlib · Pygame · Flask · SQLite

---

## Lab 1 — Ant Colony Optimization ([`labFirst/`](./labFirst))

Solves the Travelling Salesman Problem using Ant Colony Optimization (ACO).

Ants build tours probabilistically, weighting each edge by its pheromone level (τ) and inverse distance (η). After each iteration pheromones evaporate globally and get reinforced along the routes ants walked. The elite ant variant deposits extra pheromone on the globally best tour found so far, which accelerates convergence on larger problems.

Configurable parameters: α (pheromone weight), β (distance weight), ρ (evaporation rate), colony size. The demo compares ACO against a greedy nearest-neighbour baseline and plots convergence curves and pheromone heatmaps. Scalability tests run from 10 to 30 cities; the best solution usually stabilises within 20–40 iterations.

**Dependencies:** `numpy`, `matplotlib`

---

## Lab 2 — Artificial Life Simulation ([`labSecond/`](./labSecond))

An agent-based ecosystem with three trophic levels: plants, herbivores, and carnivores.

Each mobile agent carries a small neural network (12 inputs → 4 outputs) that maps what it senses around it to actions (turn left, turn right, move, eat). The 12 inputs cover counts of each entity type in four directional zones (front, left, right, near). Herbivores have a built-in aversion to frontal predators baked into the initial weights; carnivores are biased toward prey. When an agent accumulates enough energy it reproduces, passing on a mutated copy of its weights to the offspring.

The world uses a spatial hash grid for fast neighbour queries. Population is soft-capped at 25–50 % of the starting size. You can run it headless (fast, outputs CSV + PNG) or with a Pygame visualisation that shows population dynamics in real time.

**Dependencies:** `numpy`, `matplotlib`, `pygame` (optional for visualisation)

---

## Lab 3 — Cryptocurrency Event Monitor ([`labThird/`](./labThird))

A multi-source monitoring system that watches exchange announcements and newsgroup discussions, correlates the signals, and scores the probability that a market-moving event is occurring for a given token.

Three worker threads run concurrently:

- **HTTP monitor** — polls Binance, Coinbase, and Kraken announcement pages over raw TCP sockets (no `requests`/`urllib`; HTTP/1.1 implemented at socket level). Flags a change when the content-length shifts by more than 5 %. Uses exponential backoff (1 s → 2 s → 4 s) on failures.
- **NNTP monitor** — connects to a newsgroup server using the NNTP protocol directly over sockets, fetches the last 20 articles per group, and scans for configured token names and action keywords (listing, fork, hack, ETF, etc.).
- **Correlator** — wakes on signals from either monitor (or every 15 s) and computes a confidence score per token: +30 for an HTTP change, +40 for an NNTP article spike above 200 % of the 4-week baseline, +15 for multi-newsgroup discussion, +15 for action keywords. Events scoring ≥ 70 are high priority; ≥ 50 trigger monitoring; ≥ 30 are logged.

Results land in SQLite (WAL mode for concurrent writes) and are exposed over a Flask web dashboard with REST endpoints for live status, raw feed, and alerts.

**Dependencies:** `flask`, `sqlite3` (built-in)
