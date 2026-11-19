# Wisecow containerization and QA exercise

Bash Wisecow application, Dockerfile, Kubernetes Deployment/Service, GitHub Actions build/test/push workflow and two Python utilities: web-log analysis and application HTTP health checking.

This is assisted preparation and guided practice. It is not a claim of independent authorship or prior Docker/Kubernetes experience. The source is adapted from https://github.com/nyrahul/wisecow at commit32b220c9deecb46d621f6c849599d838b39ad488. Original source and Apache2.0 licence are retained. See docs/TRANSPORT_CHANGE.md for the disclosed replacement of sequential FIFO/netcat transport with bounded per-connection socat handlers. The original and timeout-only variant had failed browser/port-forward tests; the revised candidate was checked separately.

## Verified locally, 19 November2026

-31Python unit tests and log-fixture/HTTP-status scenarios passed.
- Revised linux/arm64 Docker image built; nonroot/read-only/resource-limited container regression passed real-cow/framing/idle/concurrent/probe-like connection checks.
- Explicitly scoped local kind cluster: server API dry-run, rollout, source/config/runtime identity binding and Service port-forward passed.
- Real HTTP200/cow/framing/EOF,8concurrent requests while another peer was idle, clean idle closure and24further concurrent requests passed through the Service.
- Actual Chrome screenshot was inspected and showed cow output at a localhost-only endpoint.
- A120-second observation from13:10:34 to13:12:34IST passed13HTTP samples, unchanged pod/image, Ready/Running,zero restarts and no Warning events. This is bounded evidence, not a long-term stability/performance guarantee.18.84MiB was a container snapshot, not peak memory proof.

## Reproduce in your own isolated environment

Review the code and requirements first. Local Docker example:

```sh
docker build -t wisecow:review .
python3 tools/connection_regression.py wisecow:review
python3 -m unittest discover -s tests -v
python3 scripts/log_analyzer.py fixtures/access.log
```

The helper creates/removes only a uniquely named local test container. It does not deploy to Kubernetes or push an image. For Kubernetes, choose an explicit context/namespace, load or pull your reviewed image, create a separate exact-tag/digest Deployment from k8s/deployment.yaml, server-dry-run and review only that Deployment and service.yaml, then apply and inspect rollout/events/HTTP. The generic wisecow:concurrent-v2 image reference is a local template, not a published-image identity. Do not apply the whole k8s directory: it contains an unconfigured TLS ingress example.

## CI and remaining gaps

.github/workflows/ci.yml checks Python/Bash/manifest relationships, builds a local image and runs the real-cow regression. On trusted main it can push GHCR commit/latest tags after checks. A workflow file is not proof of a successful run; consult actual Actions results and registry digest. No CV, personal logs, credentials or private screenshots are included.

Automatic continuous deployment is NOT IMPLEMENTED. TLS ingress is an example only and HTTPS has NOT been verified. The assessment labels CD/TLS Challenge Goals while mentioning them in the end goal; these gaps are not represented as complete. Pod replacement recovery, sustained-load performance and long-term uptime are also untested. This small training server is not a production HTTP implementation.

## Python utilities

- scripts/log_analyzer.py summarizes common/combined web logs,404counts,top paths and source IPs. The included fixture is synthetic reserved-address data.
- scripts/http_health_checker.py samples HTTP response status/timing, does not follow redirects, and reports observed sample uptime, not historical availability. Run --help for arguments.

No employer form submission is implied by this repository.
