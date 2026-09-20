# ADR 0002: Prometheus as canonical telemetry

Decision: consolidate telemetry on Prometheus. Grafana visualizes it; Python consumes it for detection and health scoring. Custom polling remains only for scheduler truth and APIs unavailable through metrics.
