#!/usr/bin/env python3
"""Create the complete reviewed isolated-demo Deployment for Flux SSA."""
import hashlib
import json
import os
from pathlib import Path
import re
import sys


def main(index_path, descriptor_path, output_path):
    raw = Path(index_path).read_bytes()
    index = json.loads(raw)
    entries = index['manifests']
    actual = {(x['platform']['os'], x['platform']['architecture']) for x in entries}
    assert actual == {('linux', 'amd64'), ('linux', 'arm64')}, actual
    assert len(entries) == 2
    assert all(re.fullmatch(r'sha256:[a-f0-9]{64}', x['digest']) for x in entries)
    image = os.environ['IMAGE']
    sha = os.environ['GITHUB_SHA']
    assert image == 'ghcr.io/alonerider-pixel/accuknox-wisecow-qa-assignment'
    assert re.fullmatch(r'[a-f0-9]{40}', sha)
    descriptor = json.loads(Path(descriptor_path).read_text())
    digest = descriptor['digest']
    assert re.fullmatch(r'sha256:[a-f0-9]{64}', digest)
    assert digest in {'sha256:' + hashlib.sha256(candidate).hexdigest()
                      for candidate in (raw, raw.rstrip(b'\n'))}, 'Registry descriptor does not match index bytes'
    out = Path(output_path)
    out.mkdir(exist_ok=False)
    # Flux reconciles complete desired state, not a partial kubectl merge patch.
    # Preserve every reviewed isolated-demo field, including the immutable selector.
    obj = json.loads('''
{
  "apiVersion": "apps/v1",
  "kind": "Deployment",
  "metadata": {
    "name": "wisecow",
    "namespace": "accuknox-cd-demo"
  },
  "spec": {
    "replicas": 1,
    "selector": {
      "matchLabels": {
        "app": "wisecow"
      }
    },
    "template": {
      "metadata": {
        "labels": {
          "app": "wisecow"
        }
      },
      "spec": {
        "securityContext": {
          "runAsNonRoot": true,
          "runAsUser": 10001,
          "runAsGroup": 10001,
          "fsGroup": 10001,
          "seccompProfile": {
            "type": "RuntimeDefault"
          }
        },
        "containers": [
          {
            "name": "wisecow",
            "image": "wisecow:concurrent-v2-20261119-1248",
            "imagePullPolicy": "IfNotPresent",
            "ports": [
              {
                "name": "http",
                "containerPort": 4499
              }
            ],
            "securityContext": {
              "allowPrivilegeEscalation": false,
              "readOnlyRootFilesystem": true,
              "capabilities": {
                "drop": [
                  "ALL"
                ]
              }
            },
            "resources": {
              "requests": {
                "cpu": "50m",
                "memory": "64Mi"
              },
              "limits": {
                "cpu": "250m",
                "memory": "128Mi"
              }
            },
            "startupProbe": {
              "tcpSocket": {
                "port": "http"
              },
              "periodSeconds": 2,
              "failureThreshold": 15
            },
            "readinessProbe": {
              "tcpSocket": {
                "port": "http"
              },
              "initialDelaySeconds": 3,
              "periodSeconds": 10
            },
            "livenessProbe": {
              "tcpSocket": {
                "port": "http"
              },
              "initialDelaySeconds": 10,
              "periodSeconds": 20,
              "failureThreshold": 3
            },
            "volumeMounts": [
              {
                "name": "runtime",
                "mountPath": "/run/wisecow"
              }
            ]
          }
        ],
        "volumes": [
          {
            "name": "runtime",
            "emptyDir": {
              "sizeLimit": "1Mi"
            }
          }
        ],
        "automountServiceAccountToken": false,
        "serviceAccountName": "wisecow-app"
      }
    }
  }
}
    ''')
    obj['spec']['template']['metadata']['annotations'] = {'qa.accuknox.example/source-commit': sha}
    obj['spec']['template']['spec']['containers'][0]['image'] = image + '@' + digest
    (out / 'deployment-image.json').write_text(json.dumps(obj, indent=2) + '\n')
    (out / 'kustomization.yaml').write_text('apiVersion: kustomize.config.k8s.io/v1beta1\nkind: Kustomization\nresources:\n  - deployment-image.json\n')
    print(json.dumps({'image': image, 'digest': digest, 'commit': sha, 'target': 'accuknox-cd-demo/wisecow'}))


if __name__ == '__main__':
    main(*sys.argv[1:])
