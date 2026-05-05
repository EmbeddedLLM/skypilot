#!/usr/bin/env python3
"""Validate the resource-key selection logic for mixed AMD + NVIDIA clusters.

Replicates the logic from sky/clouds/kubernetes.py (post-f65b71f6c) and
sky/provision/kubernetes/utils.py (AMDGPULabelFormatter + GFDLabelFormatter)
without importing the sky module. Queries the cluster directly via kubectl.

For each requested GPU, prints:
  - which node labels matched
  - which label key was selected (k8s_acc_label_key)
  - which resource key the pod will request (k8s_resource_key)
  - PASS/FAIL based on expected vendor

Usage:
    python3 scripts/validate_gpu_resource_key.py
    python3 scripts/validate_gpu_resource_key.py --context my-cluster
    python3 scripts/validate_gpu_resource_key.py --gpus A4000 RX7900XTX MI300X
"""
import argparse
import json
import subprocess
import sys
from typing import Dict, List, Optional

# ── Inlined GFD (NVIDIA) formatter ──────────────────────────────────────────
GFD_LABEL_KEY = 'nvidia.com/gpu.product'


def gfd_get_accelerator(value: str) -> str:
    """GFDLabelFormatter.get_accelerator_from_label_value, simplified."""
    # NVIDIA-A4000  →  A4000   (word-boundary regex, prefix stripping)
    # Just return the last hyphen-separated segment for our test purposes.
    cleaned = (value.replace('NVIDIA-', '').replace('GeForce-', '')
               .replace('RTX-', 'RTX'))
    return cleaned


def gfd_match(label_key: str) -> bool:
    return label_key == GFD_LABEL_KEY


# ── Inlined AMD formatter (direct format only — homogeneous-node assumption) ─
AMD_LABEL_KEY = 'amd.com/gpu.product-name'

CANONICAL_GPU_NAMES = [
    'MI355X', 'MI350X', 'MI350', 'MI325X', 'MI300X', 'MI300A', 'MI300',
    'MI250X', 'MI250', 'MI210', 'MI100',
    'W7900', 'W7800', 'W7700', 'W6800', 'W6600',
    'RX7900XTX', 'RX7900XT', 'RX7900GRE', 'RX7800XT', 'RX7700XT',
    'RX7600XT', 'RX7600',
    'RX6950XT', 'RX6900XT', 'RX6800XT', 'RX6800', 'RX6750XT',
    'RX6700XT', 'RX6700', 'RX6650XT', 'RX6600XT', 'RX6600',
]


def amd_match(label_key: str) -> bool:
    return label_key == AMD_LABEL_KEY


def amd_normalize(raw: str) -> str:
    name = raw.lower().replace('_', ' ')
    name_nospace = name.replace(' ', '')
    for c in CANONICAL_GPU_NAMES:
        if c.lower() in name_nospace:
            return c
    name = (name.replace('amd ', '').replace('instinct ', '')
            .replace('radeon ', ''))
    return name.replace(' ', '')


def amd_get_accelerator(label_key: str, value: str) -> str:
    del label_key
    return amd_normalize(value)


# ── Resource-key selection ──────────────────────────────────────────────────
SUPPORTED_GPU_RESOURCE_KEYS = {'amd': 'amd.com/gpu', 'nvidia': 'nvidia.com/gpu'}


def get_gpu_resource_key_cluster_default(
        node_capacity_keys: List[Dict[str, str]]) -> str:
    """Replicates _gpu_resource_key_helper in sky/provision/kubernetes/utils.py.

    Scans node capacity, returns the FIRST vendor key in dict-iteration order
    that exists on any node. In a mixed cluster this is 'amd.com/gpu' because
    'amd' comes before 'nvidia' in SUPPORTED_GPU_RESOURCE_KEYS.
    """
    supported = set(SUPPORTED_GPU_RESOURCE_KEYS.values())
    capacity_keys: set = set()
    for cap in node_capacity_keys:
        capacity_keys.update(supported.intersection(cap.keys()))
    for v in SUPPORTED_GPU_RESOURCE_KEYS.values():
        if v in capacity_keys:
            return v
    return SUPPORTED_GPU_RESOURCE_KEYS['nvidia']  # default


def select_resource_key_FIXED(k8s_acc_label_key: Optional[str],
                              cluster_default: str) -> str:
    """The CORRECT logic from f65b71f6c."""
    if (k8s_acc_label_key is not None and
            k8s_acc_label_key.startswith('amd.com/')):
        return SUPPORTED_GPU_RESOURCE_KEYS['amd']
    elif k8s_acc_label_key is not None:
        return SUPPORTED_GPU_RESOURCE_KEYS['nvidia']
    else:
        return cluster_default


def select_resource_key_BROKEN(k8s_acc_label_key: Optional[str],
                               cluster_default: str) -> str:
    """The BUGGY logic that was in 9cd2668c8 (fixed by f65b71f6c).

    Falls back to get_gpu_resource_key(context) for non-AMD label keys,
    which in a mixed cluster picks the wrong vendor.
    """
    if (k8s_acc_label_key is not None and
            k8s_acc_label_key.startswith('amd.com/')):
        return SUPPORTED_GPU_RESOURCE_KEYS['amd']
    else:
        return cluster_default  # ← BUG: returns 'amd.com/gpu' in mixed cluster


# ── Cluster scanning ────────────────────────────────────────────────────────
def _have_kubectl() -> bool:
    try:
        subprocess.run(['kubectl', 'version', '--client', '-o', 'json'],
                       capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _get_nodes_via_kubectl(context=None):
    cmd = ['kubectl']
    if context:
        cmd += ['--context', context]
    cmd += ['get', 'nodes', '-o', 'json']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if r.returncode != 0:
        print(f'ERROR: kubectl failed: {r.stderr.strip()}')
        sys.exit(1)
    data = json.loads(r.stdout)
    out = []
    for n in data.get('items', []):
        labels = n['metadata'].get('labels', {})
        capacity = n.get('status', {}).get('capacity', {})
        out.append((n['metadata']['name'], labels, capacity))
    return out


def _get_nodes_via_k8s_client(context=None):
    try:
        from kubernetes import client, config
    except ImportError:
        print('ERROR: kubectl unavailable and kubernetes python client not '
              'installed. Run on host with kubectl, or install kubernetes pkg.')
        sys.exit(1)
    try:
        config.load_incluster_config()
    except Exception:
        try:
            config.load_kube_config(context=context)
        except Exception as e:
            print(f'ERROR: could not load kubeconfig: {e}')
            sys.exit(1)
    v1 = client.CoreV1Api()
    nodes = v1.list_node().items
    return [(n.metadata.name, dict(n.metadata.labels or {}),
             dict(n.status.capacity or {})) for n in nodes]


def get_all_nodes(context=None):
    if _have_kubectl():
        return _get_nodes_via_kubectl(context)
    return _get_nodes_via_k8s_client(context)


def find_label_for_gpu(gpu, nodes):
    """Return list of (node, label_key, label_value, resolved_name) matches."""
    matches = []
    for node_name, labels, _capacity in nodes:
        for lk, lv in labels.items():
            # AMD path
            if amd_match(lk):
                resolved = amd_get_accelerator(lk, lv)
                if resolved.lower() == gpu.lower():
                    matches.append((node_name, lk, lv, resolved))
            # GFD (NVIDIA) path
            elif gfd_match(lk):
                resolved = gfd_get_accelerator(lv)
                if gpu.lower() in resolved.lower():
                    matches.append((node_name, lk, lv, resolved))
    return matches


def sep(title=''):
    w = 70
    if title:
        pad = (w - len(title) - 2) // 2
        print(f"\n{'─' * pad} {title} {'─' * (w - len(title) - 2 - pad)}")
    else:
        print('─' * w)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--context', default=None)
    ap.add_argument('--gpus', nargs='+',
                    default=['A4000', 'RX7900XTX'],
                    help='GPUs to test (default: A4000 RX7900XTX)')
    args = ap.parse_args()

    sep('Cluster nodes')
    nodes = get_all_nodes(args.context)
    for n, lbls, _ in nodes:
        gpu_lbls = sorted(k for k in lbls if 'gpu.product' in k or 'gpu' == k.split('/')[-1])
        gpu_lbls = [k for k in gpu_lbls if amd_match(k) or gfd_match(k)]
        print(f'  {n}: {gpu_lbls if gpu_lbls else "no GPU labels"}')

    # Compute the cluster-wide default that get_gpu_resource_key(context)
    # would return — this is what the BUGGY code falls back to.
    cluster_default = get_gpu_resource_key_cluster_default(
        [cap for _, _, cap in nodes])
    sep('Cluster default GPU resource key')
    print(f'  get_gpu_resource_key(context) = {cluster_default}')
    print(f'  (this is what the BUGGY 9cd2668 code falls back to for')
    print(f'   non-AMD label keys — e.g. NVIDIA pods get this key by mistake)')

    overall_pass = True

    for gpu in args.gpus:
        sep(f'Test: GPU = {gpu!r}')

        matches = find_label_for_gpu(gpu, nodes)
        if not matches:
            print(f'  ⚠ No nodes match GPU {gpu!r} — cannot test')
            continue

        is_amd = (
            gpu.upper().startswith('MI') or
            gpu.upper().startswith('RX') or
            gpu.upper().startswith('W6') or
            gpu.upper().startswith('W7'))
        expected = 'amd.com/gpu' if is_amd else 'nvidia.com/gpu'

        for node, lk, lv, resolved in matches:
            print(f'  matched on node:   {node}')
            print(f'    label key:       {lk}')
            print(f'    label value:     {lv!r}')
            print(f'    resolved name:   {resolved}')
            print(f'    expected key:    {expected}')

            broken_key = select_resource_key_BROKEN(lk, cluster_default)
            fixed_key = select_resource_key_FIXED(lk, cluster_default)

            broken_ok = broken_key == expected
            fixed_ok = fixed_key == expected
            broken_tag = '✓' if broken_ok else '✗ BUG'
            fixed_tag = '✓' if fixed_ok else '✗'

            print(f'    BROKEN (9cd2668):  {broken_key:20s} {broken_tag}')
            print(f'    FIXED  (f65b71f):  {fixed_key:20s} {fixed_tag}')

            if not fixed_ok:
                overall_pass = False

    sep()
    if overall_pass:
        print('OK — fixed logic maps all tested GPUs to the correct resource key.')
        print('     (BUG markers above show what the broken intermediate '
              'commit would have done.)')
    else:
        print('FAIL — fixed logic mapped some GPU to wrong resource key.')
        sys.exit(1)


if __name__ == '__main__':
    main()
