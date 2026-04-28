# Android Development — Lab Applications

Four Android applications built progressively, covering navigation patterns, custom domain logic, data visualisation, and Material Design composition.

**Common stack:** Java · Kotlin · AndroidX · Material Design 3 · Gradle · minSdk 23

---

## Lab 1 — Tabbed Navigation App

Fragment-based UI with a `ViewPager` and `TabLayout`. Demonstrates the `FragmentPagerAdapter` pattern and basic AndroidX component wiring. Entry point for understanding Android's fragment lifecycle and back-stack management.

---

## Lab 2 — Time Arithmetic Utility

A utility class (`TimeKF`) implementing time value arithmetic — addition, subtraction, and validation across hours, minutes, and seconds with proper carry/borrow logic. Focuses on correct domain modelling and edge-case handling (overflow, negative values).

---

## Lab 3 — Graphics & Fragment Navigation

Extends the tabbed pattern with a `GraphicFragment` that renders 2D graphics on a custom `Canvas`. Demonstrates fragment-to-fragment communication and dynamic view drawing.

---

## Lab 4 — Full Multi-Screen App

The most complete application, combining all prior concepts:

- **GreetingFragment** — welcome / onboarding screen.
- **GraphicFragment** — charts rendered with [MPAndroidChart](https://github.com/PhilJay/MPAndroidChart) (PieChart) and [GraphView](https://github.com/appsthatmatter/GraphView).
- **FilmFragment** — a film catalogue backed by `Film` and `Search` entity models with list/detail navigation.
- Material Design components throughout: `FloatingActionButton`, `Toolbar`, `Snackbar`, `CoordinatorLayout`.
