# Security Policy

## Reporting

Report vulnerabilities in this repository's scripts, or instructions that could cause an agent to act unsafely (for example unsafe commands, prompt-injection-friendly wording, or secret exposure), through the repository host's private vulnerability reporting feature or by contacting the maintainers privately. Do not open public issues with exploit details. Replace this paragraph with real contact details when you publish the repository.

## Scope

In scope: `scripts/`, skill instructions, registry data, example fixtures. Out of scope: vulnerabilities in third-party projects that the discovery tool merely catalogues (report those upstream).

## Design stance

This project's skills are instructions that other AI agents execute, so the repository is part of a supply chain. See `docs/SECURITY_MODEL.md` for the threat model and the controls (no automatic execution of third-party content, human approval gates, redaction, no uploads).
