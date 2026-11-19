# Local TLS proxy template

This is the non-secret proxy configuration used for the separate local private-CA demonstration. It does not generate certificates, create a Secret or run anything by itself. Do not apply until reviewing the exact context, namespace, existing names, image platform, ports and certificate conditions.

The tested shape adds a ConfigMap, nonroot/read-only Deployment, ClusterIP Service and separately generated TLS Secret. The proxy uses the pinned multi-platform NGINX image, UID101, fsGroup101, dropped capabilities, no privilege escalation, no service-account token mount and bounded temporary storage. It terminates TLS on8443 and forwards HTTP to the existing wisecow Service on80. It is not an Ingress controller or end-to-end TLS.

Generate a dedicated short-lived local CA and leaf only in a new0700 directory outside the repository, with0600 keys. The CA needs critical CA:true and certificate-signing key usage plus SKI. The leaf needs CA:false, serverAuth, DNSlocalhost/IP127.0.0.1 SANs, key usage, SKI and AKI. Test an actual hostname-validating strict handshake before updating any Secret. Do not install system trust, bypass browser warnings, weaken verification flags, publish keys/certificates/Secret manifests or reuse production credentials.

Use an explicit isolated Kubernetes context and namespace. Confirm the four exact resource names are absent and the existing app baseline is healthy. Server-dry-run only the reviewed Secret and three template resources before apply, keeping Secret material local and out of terminal output. Apply only those reviewed resources, inspect rollout and runtime identity, then use a foreground port-forward bound to127.0.0.1. Verify real cow output with the explicit CA, both SANs and TLS1.2/1.3; verify untrusted CA, wrong hostname and plaintext fail. Retest concurrent/idle behavior. A TCP-ready proxy is not proof of HTTPS.

Rollback removes only Deployment/wisecow-local-tls, Service/wisecow-local-tls, ConfigMap/wisecow-local-tls-config and Secret/wisecow-local-tls in that reviewed namespace. Do not remove the original application. Stop only the dedicated TLS port-forward. Keep or remove private local key files deliberately, never commit them.

The local TLS demonstration used linux/arm64. The application CI image is now separately verified for Linux amd64 and arm64. No long-term HTTPS observation, publicly trusted browser rendering, public endpoint, automatic certificate renewal or TLS-namespace CD is claimed. The separate isolated CD demonstration does not modify this original app/TLS setup.
