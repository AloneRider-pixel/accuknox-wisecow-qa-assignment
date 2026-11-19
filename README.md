# Wisecow containerization and QA exercise

Bash Wisecow application, Dockerfile, Kubernetes Deployment and Service, GitHub Actions native multi-platform build/test/push, isolated pull-based Flux delivery, and two Python utilities.

This is assisted preparation and guided practice, not independent authorship or prior Docker/Kubernetes experience. Adapted from https://github.com/nyrahul/wisecow at commit `32b220c9deecb46d621f6c849599d838b39ad488`, with its Apache 2.0 licence retained. `docs/TRANSPORT_CHANGE.md` explains the change from sequential FIFO/netcat transport to bounded per-connection socat handlers. This training server is not a production HTTP implementation.

## Verified scope, 19 November 2026

| Area | Observed result | Limits |
|---|---|---|
| Python utilities | 31 unit tests; synthetic log and local HTTP fixtures | Selected assessment objectives 3 and 4 only |
| Container and Kubernetes | Real cow response, HTTP framing/EOF, idle peer and concurrent connections, nonroot container, local Kind rollout and Service | Bounded local checks, not production availability |
| Stability | 13 HTTP samples over 120 seconds, same pod/image, Ready, zero restarts, no Warning events | Not long-term uptime, sustained-load or peak-memory proof |
| CI | Native Linux amd64 and arm64 builds and per-platform real-cow regression, merged image pushed to GHCR | Successful run linked below, not a claim based only on workflow YAML |
| Delivery | Actual Flux controllers fetched/applied corrected CI artifact on local arm64 cluster; demo healthy; original app and TLS unchanged | Separate restricted demo namespace, not delivery to the original app/TLS namespace |
| Tracking | OCI source and Kustomization Ready, five-minute `delivery` tag checks configured | Requires Mac and Docker running; a later code push has **not** been exercised end to end |
| HTTPS | Strict explicit-private-CA validation, localhost/IP SAN, TLS 1.2/1.3, real cow, negative trust/hostname checks | Proxy terminates TLS; HTTP upstream. Not public trusted HTTPS, Ingress, browser trust or end-to-end TLS |

Successful build and actual Flux regression: https://github.com/AloneRider-pixel/accuknox-wisecow-qa-assignment/actions/runs/44521052195

The Flux regression first reproduced the old missing-selector artifact rejection and checked that the baseline stayed unchanged. The complete desired-state correction then reconciled, rolled out and preserved the Deployment UID and other reviewed settings. A later guided local check verified the running arm64 image through registry/index/config identities and tested 13 HTTP cow responses, including concurrent requests. This does not establish that a future push has been tested.

## Run the utilities and container checks

```sh
python3 -m unittest discover -s tests -v
python3 scripts/log_analyzer.py fixtures/access.log
python3 scripts/http_health_checker.py --help
docker build -t wisecow:review .
python3 tools/connection_regression.py wisecow:review
```

The helper creates/removes only a uniquely named local test container. It neither deploys to Kubernetes nor publishes an image. The synthetic fixture uses reserved example addresses.

For a Kubernetes exercise, select an explicit isolated context and namespace, inspect the image and objects, then dry-run and apply only the reviewed Deployment and Service. `k8s/deployment.yaml` is a template with a local image reference, not an instruction to deploy the published artifact. Do not apply the whole directory: it also contains an unconfigured Ingress example. Deliberate pod deletion/recovery has not been tested.

## CI and isolated delivery

`.github/workflows/ci.yml` runs checks and builds/tests each native platform. Trusted main commits can publish commit/latest image tags, a digest-pinned desired-state artifact and the moving `delivery` artifact tag. `tools/prepare_delivery_artifact.py` validates the two-platform index and descriptor and produces the complete isolated Deployment, including its immutable selector, security settings, resources and probes.

`tools/flux_regression.py` is an ephemeral hosted-CI rehearsal. The hosted workflow creates a disposable Kind cluster named `wisecow-ci`, pins its node image and always attempts cleanup. The script is CI-only and explicitly selects `kind-wisecow-ci`; it must never be repurposed against an existing user cluster. The isolated demonstration uses two Flux controllers and scoped reconciliation permissions, no incoming connection to the Mac, no self-hosted Actions runner and no new registry password. See `examples/isolated-cd/README.md` and `docs/VERIFICATION_SCOPE.md` before attempting reproduction. The workflow's `delivery` tag is published before the downstream rehearsal finishes, so this is not a claim that delivery is gated by the final rehearsal job.

## Local TLS template

`examples/local-tls/proxy.template.yaml` is non-secret configuration only. A dedicated short-lived private CA and leaf must be generated and retained outside the repository. Review `examples/local-tls/README.md` before using it. No private certificate, key, Secret payload, personal machine path, raw Terminal transcript, CV or personal screenshot is included.

No employer form submission is implied by this repository.
