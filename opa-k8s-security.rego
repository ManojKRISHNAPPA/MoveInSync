# ──────────────────────────────────────────────────────────────────────────────
# OPA / Conftest — Kubernetes manifest security policy
# MoveInSync (adapted from gameapp DevSecOps standards)
# ──────────────────────────────────────────────────────────────────────────────
package main

import future.keywords.in

# ── Rule 1: Service type must be LoadBalancer ─────────────────────────────────
deny[msg] {
    input.kind == "Service"
    input.spec.type != "LoadBalancer"
    msg := sprintf("Service '%s' must use type: LoadBalancer, got: %s", [
        input.metadata.name,
        input.spec.type
    ])
}

# ── Rule 2: Deployment must specify resource requests ────────────────────────
deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    not container.resources.requests
    msg := sprintf("Container '%s' in Deployment '%s' must define resource requests", [
        container.name,
        input.metadata.name
    ])
}

# ── Rule 3: Deployment must specify resource limits ──────────────────────────
deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    not container.resources.limits
    msg := sprintf("Container '%s' in Deployment '%s' must define resource limits", [
        container.name,
        input.metadata.name
    ])
}

# ── Rule 4: Deployment must have at least 1 replica ──────────────────────────
deny[msg] {
    input.kind == "Deployment"
    input.spec.replicas < 1
    msg := sprintf("Deployment '%s' must have at least 1 replica", [input.metadata.name])
}

# ── Rule 5: Container image must not use 'latest' tag ────────────────────────
deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    endswith(container.image, ":latest")
    msg := sprintf("Container '%s' must not use the 'latest' image tag", [container.name])
}
