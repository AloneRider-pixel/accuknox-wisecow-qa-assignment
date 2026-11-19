#!/usr/bin/env python3
"""Static relationship checks. These do NOT contact or validate a live cluster."""
from pathlib import Path
import yaml

root = Path(__file__).resolve().parents[1]
deployment = yaml.safe_load((root / 'k8s/deployment.yaml').read_text())
service = yaml.safe_load((root / 'k8s/service.yaml').read_text())
ingress = yaml.safe_load((root / 'k8s/ingress-tls.example.yaml').read_text())
pod = deployment['spec']['template']
container = pod['spec']['containers'][0]
assert deployment['apiVersion'] == 'apps/v1'
assert deployment['spec']['selector']['matchLabels'] == pod['metadata']['labels']
assert service['spec']['selector'] == pod['metadata']['labels']
assert service['spec']['ports'][0]['targetPort'] == container['ports'][0]['name']
assert container['ports'][0]['containerPort'] == 4499
assert container['securityContext']['readOnlyRootFilesystem'] is True
assert pod['spec']['securityContext']['runAsNonRoot'] is True
assert container['volumeMounts'][0]['name'] == pod['spec']['volumes'][0]['name']
backend = ingress['spec']['rules'][0]['http']['paths'][0]['backend']['service']
assert backend['name'] == service['metadata']['name']
assert backend['port']['number'] == service['spec']['ports'][0]['port']
assert ingress['spec']['tls'][0]['hosts'][0] == ingress['spec']['rules'][0]['host']
assert pod['spec']['containers'][0]['image'] == 'wisecow:concurrent-v2'
print('PASS: deployment/service/optional-ingress relationships (static only)')
