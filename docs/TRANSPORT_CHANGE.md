# Transport change and review limits

## Provenance and assignment

Assignment: https://drive.google.com/file/d/1GZv8-SCXaBcESld_1lJ_z-Kf0FF8y093/view
Source: https://github.com/nyrahul/wisecow
Original inspected source commit: 32b220c9deecb46d621f6c849599d838b39ad488.

The original script is preserved byte-for-byte in `upstream/wisecow.sh`, with Apache 2.0 `LICENSE`. The active script is an assisted adaptation, not unchanged upstream or independently authored candidate work. The supplied PDF asks to containerize and deploy this app; no explicit ban on source changes was found. That does not prove every adaptation is accepted. The active code still runs Bash with real fortune/cowsay on port 4499. It changes transport substantially enough to disclose and explain. Do not silently submit it as unchanged source.

## Why the old patch was insufficient

The original shared FIFO and one-shot netcat listener serialize connections. An idle connection can block later requests. Wrapping that whole pipeline in timeout bounded the stall but still killed accepted/queued connections and repeatedly recreated the listener. Sequential tests were insufficient. Actual Mac browser/port-forward tests failed after the timeout patch, and the new pod had a readiness warning. A zero restart count was not a full pass.

## This candidate

- One persistent `socat` TCP4 listener, port 4499, backlog 32, at most eight children. It forks an isolated Bash handler for each accepted connection. No shared FIFO or writable runtime file.
- Request line and individual headers limited to 8 KiB, total header budget 16 KiB and at most 64 header lines. Reads have two-second bounds, the complete child has an eight-second timeout with one-second forced-kill fallback, and socat inactivity is bounded at nine seconds. These bounds intentionally do not support slow clients.
- GET and HEAD only. Basic malformed requests return 400; unsupported methods 405; partial-read timeout 408; long request line 414; oversized headers 431; unavailable renderer 503. No request text is executed, passed to a shell evaluator or used as a file path.
- Fortune selection uses `fortune -s`, then passes text on stdin to cowsay, avoiding option injection from fortune text. Each renderer has a two-second limit. Cow text is HTML-escaped and wrapped in pre. Response byte length is calculated under LC_ALL=C, with CRLF framing and Connection: close. HEAD sends no body.
- Debian runtime adds socat. User 10001, dropped capabilities, read-only root filesystem, resource settings and probes remain unchanged in Kubernetes. The runtime no longer requires a FIFO, but the existing harmless runtime volume remains for minimal manifest change.
- The workflow calls the new connection helper after its local image build. Trusted main builds can publish a GHCR image after checks. Actual run and publication results must be verified from Actions; configuration alone is not execution proof.

## Tests and what they do not establish

`host-review-results.json`: 16 passed Linux host-process checks with real extracted Ubuntu fortune/cowsay binaries and their dependencies. This is not the Debian arm64 image. Eight parallel requests while an idle connection was open, forty further requests, fifty probe-like TCP connections, exact response length/clean EOF, HEAD and error bounds passed.

`host-resource-review.json`: non-root UID 1001, read-only working directory, no created files. Eight idle clients produced 25 processes and an aggregate RSS snapshot of about 44 MiB, with shared pages counted more than once. This is NOT peak memory/cgroup proof or a 128 MiB guarantee. A parent-only SIGTERM test with idle children left no tracked descendants after three seconds. A prior 16-child prototype was reduced to eight to limit pressure.

Four additional controlled-renderer handler checks passed for HTML escaping, fortune failure, cowsay failure and fortune timeout. These are fixtures, not additional real-renderer or container proof. See `handler-fixture-review.json`.

No Docker/Podman/kind/kubectl command or Docker socket was available during initial private preparation. Subsequent user Mac execution on19November2026 verified the revised Docker build, restricted container regression, exact image/config/source binding, named kind rollout, Service port-forward, HTTP concurrency/idle handling and Chrome render. See VERIFICATION.md for exact scope. The finite120-second observation passed13:10:34 to13:12:34IST with13HTTP samples, unchanged pod/image, Ready, zero restarts and no Warning events. A resource snapshot is not peak/cgroup proof; no long-term stability claim follows.

This is still a small training server, not a production HTTP implementation. It does not implement TLS, chunked requests, persistent connections, request bodies, HTTP/2, authentication or unlimited concurrency. Malformed/oversized clients may be closed, and saturation can queue/fail clients. No performance or uptime claims.

## Sources for transport semantics

https://manpages.debian.org/bookworm/socat/socat.1.en.html
https://manpages.debian.org/bookworm/netcat-openbsd/nc.1.en.html

Socat documents fork/max-children/TCP-LISTEN/EXEC. Netcat -k handles another connection after completion, not independent concurrent handlers; -w does not fix -l listener timing.
