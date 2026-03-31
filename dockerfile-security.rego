# ──────────────────────────────────────────────────────────────────────────────
# OPA / Conftest — Dockerfile security policy
# MoveInSync (adapted from gameapp DevSecOps standards)
# ──────────────────────────────────────────────────────────────────────────────
package main

import future.keywords.in

# ── Helpers ───────────────────────────────────────────────────────────────────

# Secret-related keywords that must NOT appear in ENV instructions
secret_keywords := {
    "passwd", "password", "pass", "secret", "key",
    "access", "api_key", "token", "apikey", "api_secret",
    "auth", "credentials", "private_key"
}

# Trusted base image prefixes (must NOT contain a registry host with a dot)
is_trusted_base(image) {
    not contains(image, ".")
}

is_trusted_base(image) {
    startswith(image, "python:")
}

is_trusted_base(image) {
    startswith(image, "eclipse-temurin:")
}

is_trusted_base(image) {
    startswith(image, "openjdk:")
}

is_trusted_base(image) {
    startswith(image, "node:")
}

is_trusted_base(image) {
    startswith(image, "alpine:")
}

is_trusted_base(image) {
    startswith(image, "ubuntu:")
}

is_trusted_base(image) {
    startswith(image, "debian:")
}

# ── Rule 1: No secrets in ENV instructions ────────────────────────────────────
deny[msg] {
    cmd := input[i]
    cmd.Cmd == "env"
    val := cmd.Value[_]
    keyword := secret_keywords[_]
    contains(lower(val), keyword)
    msg := sprintf("Line %d: Potential secret '%s' found in ENV instruction: %s", [i + 1, keyword, val])
}

# ── Rule 2: Do not use the 'latest' tag ───────────────────────────────────────
deny[msg] {
    cmd := input[i]
    cmd.Cmd == "from"
    image := cmd.Value[0]
    endswith(image, ":latest")
    msg := sprintf("Line %d: Do not use 'latest' tag in FROM instruction: %s", [i + 1, image])
}

# ── Rule 3: FROM image must not be empty ──────────────────────────────────────
deny[msg] {
    cmd := input[i]
    cmd.Cmd == "from"
    cmd.Value[0] == ""
    msg := sprintf("Line %d: FROM instruction has an empty image name", [i + 1])
}

# ── Rule 4: Use COPY instead of ADD ───────────────────────────────────────────
deny[msg] {
    cmd := input[i]
    cmd.Cmd == "add"
    msg := sprintf("Line %d: Use COPY instead of ADD to avoid unintended archive extraction", [i + 1])
}

# ── Rule 5: Non-root USER required ────────────────────────────────────────────
deny[msg] {
    not any_non_root_user
    msg := "Dockerfile must define a non-root USER instruction (not root/0)"
}

any_non_root_user {
    cmd := input[_]
    cmd.Cmd == "user"
    user_val := cmd.Value[0]
    not user_val == "root"
    not user_val == "0"
    not user_val == ""
}

# ── Rule 6: Do not use sudo ───────────────────────────────────────────────────
deny[msg] {
    cmd := input[i]
    cmd.Cmd == "run"
    val := cmd.Value[_]
    contains(val, "sudo ")
    msg := sprintf("Line %d: Do not use sudo in RUN instructions", [i + 1])
}

# ── Rule 7: Avoid curl | bash / wget | sh pipe installs ───────────────────────
deny[msg] {
    cmd := input[i]
    cmd.Cmd == "run"
    val := cmd.Value[_]
    contains(val, "curl")
    contains(val, "bash")
    msg := sprintf("Line %d: Avoid piping curl output to bash (supply chain risk)", [i + 1])
}

deny[msg] {
    cmd := input[i]
    cmd.Cmd == "run"
    val := cmd.Value[_]
    contains(val, "wget")
    contains(val, "sh")
    msg := sprintf("Line %d: Avoid piping wget output to sh (supply chain risk)", [i + 1])
}

# ── Rule 8: Pin pip installs (do not use --upgrade without version) ────────────
warn[msg] {
    cmd := input[i]
    cmd.Cmd == "run"
    val := cmd.Value[_]
    contains(val, "pip install")
    not contains(val, "==")
    not contains(val, "-r requirements")
    msg := sprintf("Line %d: Consider pinning pip package versions for reproducible builds", [i + 1])
}
