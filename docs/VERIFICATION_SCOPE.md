# Verification scope and known limits

Evidence date: 19 November 2026, through 17:58 IST.

Public CI: https://github.com/AloneRider-pixel/accuknox-wisecow-qa-assignment/actions/runs/44521052195

Reviewed source commit: `528f51d842dbcbb912b16d958eb058ea7c5b3ae3`.

Application index: `sha256:207ac0c3e20107c48db277a700663f81c64ed63417fc3d70a47fc618ee9845b8`.

Delivery artifact: `sha256:1c78931053b883495a3ff78edd19381dfaf7746591537bd60f25f1508b0d8267`.

The two-platform index was anonymously read, including both child manifests/configs. Containerd's runtime representation on the local arm64 cluster used the index digest in imageID and the arm64 config digest in status.image. Both were bound to the published index and arm64 node, rather than assuming imageID must contain a child-manifest digest.

The CI controller regression and local cluster checks cover different environments. CI ran on Linux amd64 with disposable Kind/Kubernetes 1.35; the existing user cluster is arm64. The CI test is not a claim of testing every platform-specific controller path.

An earlier minimal Deployment artifact passed kubectl server dry-run but was rejected by actual Flux because the immutable selector was missing. Flux reconciles complete desired state, not a partial merge patch. The corrected artifact retained the selector, labels, service account, token-off setting, security context, resources, probes and volumes, changing only the digest-pinned image and source-commit annotation. Actual Flux failure/recovery was reproduced in disposable CI before the corrected local reconciliation.

The final local state had source and Kustomization Ready, five-minute delivery-tag tracking, healthy demo pod, 13 real-cow HTTP responses, and unchanged original app/TLS specifications and pod identities. No subsequent code push has been exercised. There is no claim of final-rehearsal-gated delivery: publication currently precedes that downstream test job.

TLS uses a dedicated local private CA, short-lived leaf, TLS proxy termination and HTTP upstream. No public endpoint, publicly trusted browser TLS, Ingress deployment, end-to-end encrypted upstream, renewal automation, 120-second HTTPS observation or production uptime is claimed. Earlier 120-second stability evidence is HTTP only. The observed memory sample is not peak memory proof. Deliberate pod replacement/recovery is not run.

Personal local evidence remains private. This document summarizes bounded observed results, not prior professional Docker/Kubernetes experience or independent authorship. No keys, CA/leaf bytes, private paths, raw Terminal output or personal screenshots belong in this repository.
