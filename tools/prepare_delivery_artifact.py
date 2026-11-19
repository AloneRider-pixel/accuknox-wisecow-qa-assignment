#!/usr/bin/env python3
"""Create only a minimal existing-Deployment image update for the isolated CD demo."""
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
    obj = {'apiVersion': 'apps/v1', 'kind': 'Deployment',
           'metadata': {'name': 'wisecow', 'namespace': 'accuknox-cd-demo'},
           'spec': {'template': {'metadata': {'annotations': {'qa.accuknox.example/source-commit': sha}},
                                 'spec': {'containers': [{'name': 'wisecow', 'image': image + '@' + digest}]}}}}
    (out / 'deployment-image.json').write_text(json.dumps(obj, indent=2) + '\n')
    (out / 'kustomization.yaml').write_text('apiVersion: kustomize.config.k8s.io/v1beta1\nkind: Kustomization\nresources:\n  - deployment-image.json\n')
    print(json.dumps({'image': image, 'digest': digest, 'commit': sha, 'target': 'accuknox-cd-demo/wisecow'}))


if __name__ == '__main__':
    main(*sys.argv[1:])
