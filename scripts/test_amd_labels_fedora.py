#!/usr/bin/env python3
"""Test AMD GPU label detection against a Kubernetes node.

No sky module required — all logic is inlined.

Usage:
    python3 scripts/test_amd_labels_fedora.py
    python3 scripts/test_amd_labels_fedora.py --node <node-name>
    python3 scripts/test_amd_labels_fedora.py --context <kube-context>
"""
import argparse
import json
import re
import subprocess
import sys

# ── Inlined from sky/utils/gpu_names.py ──────────────────────────────────────
CANONICAL_GPU_NAMES = [
    # Blackwell
    'GB300', 'GB200', 'B300', 'B200', 'B100',
    # Hopper
    'GH200', 'H200', 'H100-80GB', 'H100-MEGA', 'H100',
    # Ampere
    'A100-80GB', 'A100', 'A10G', 'A10', 'A16', 'A30', 'A40',
    # Ada Lovelace
    'RTX6000-Ada', 'L40S', 'L40', 'L4',
    # Quadro/RTX Professional
    'A6000', 'A5000', 'A4000',
    # Older
    'V100-32GB', 'V100', 'P100', 'P40', 'P4000', 'P4', 'T4g', 'T4', 'K80', 'M60',
    # AMD Instinct CDNA4
    'MI355X', 'MI350X', 'MI350', 'MI325X',
    # AMD Instinct CDNA3
    'MI300X', 'MI300A', 'MI300',
    # AMD Instinct CDNA2
    'MI250X', 'MI250',
    # AMD Instinct CDNA/CDNA1
    'MI210', 'MI100',
    # AMD Radeon Pro workstation RDNA3
    'W7900', 'W7800', 'W7700',
    # AMD Radeon Pro workstation RDNA2
    'W6800', 'W6600',
    # AMD Radeon RX RDNA3
    'RX7900XTX', 'RX7900XT', 'RX7900GRE', 'RX7800XT', 'RX7700XT', 'RX7600XT', 'RX7600',
    # AMD Radeon RX RDNA2
    'RX6950XT', 'RX6900XT', 'RX6800XT', 'RX6800',
    'RX6750XT', 'RX6700XT', 'RX6700', 'RX6650XT', 'RX6600XT', 'RX6600',
]

# ── Inlined from AMDGPULabelFormatter in sky/provision/kubernetes/utils.py ───
LABEL_KEY_DIRECT = 'amd.com/gpu.product-name'
LABEL_KEY_PREFIX = 'amd.com/gpu.product-name.'

_IGPU_NAMES = frozenset(['amd_radeon_graphics', 'radeon_graphics'])
_IGPU_VEGA_RE = re.compile(r'_vega_(\d+)(?:_|$)')
_IGPU_MOBILE_RE = re.compile(r'\d{3}m$')


def _is_igpu(name_lower: str) -> bool:
    if name_lower in _IGPU_NAMES:
        return True
    m = _IGPU_VEGA_RE.search(name_lower)
    if m:
        try:
            if int(m.group(1)) <= 16:
                return True
        except ValueError:
            pass
    last = name_lower.rstrip('_').rsplit('_', 1)[-1]
    return bool(_IGPU_MOBILE_RE.fullmatch(last))


def match_label_key(label_key: str) -> bool:
    if label_key == LABEL_KEY_DIRECT:
        return True
    if label_key.startswith(LABEL_KEY_PREFIX):
        suffix = label_key[len(LABEL_KEY_PREFIX):]
        return not _is_igpu(suffix.lower())
    return False


def _normalize(raw: str) -> str:
    name = raw.lower().replace('_', ' ')
    name_nospace = name.replace(' ', '')
    for canonical in CANONICAL_GPU_NAMES:
        if canonical.lower() in name_nospace:
            return canonical
    name = name.replace('amd ', '').replace('instinct ', '').replace('radeon ', '')
    return name.replace(' ', '')


def get_accelerator_from_label(label_key: str, value: str) -> str:
    if label_key.startswith(LABEL_KEY_PREFIX):
        raw = label_key[len(LABEL_KEY_PREFIX):]
    else:
        raw = value
    return _normalize(raw)


# ── Helpers ───────────────────────────────────────────────────────────────────
def kubectl(args, context=None):
    cmd = ['kubectl']
    if context:
        cmd += ['--context', context]
    cmd += args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if result.returncode != 0:
        print(f'ERROR: {result.stderr.strip()}')
        sys.exit(1)
    return result.stdout


def sep(title=''):
    w = 62
    if title:
        pad = (w - len(title) - 2) // 2
        print(f"\n{'─' * pad} {title} {'─' * (w - len(title) - 2 - pad)}")
    else:
        print('─' * w)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--node', default='fedora')
    parser.add_argument('--context', default=None)
    args = parser.parse_args()

    node, context = args.node, args.context
    print(f'Node: {node}' + (f'  context: {context}' if context else ''))

    labels = json.loads(kubectl(['get', 'node', node, '-o', 'jsonpath={.metadata.labels}'], context))
    capacity = json.loads(kubectl(['get', 'node', node, '-o', 'jsonpath={.status.capacity}'], context))

    sep('All AMD labels on node')
    amd_labels = {k: v for k, v in labels.items() if 'amd.com' in k}
    if amd_labels:
        for k, v in sorted(amd_labels.items()):
            print(f'  {k} = {v!r}')
    else:
        print('  (none — is the AMD device plugin running?)')

    sep('GPU resource capacity')
    gpu_cap = {k: v for k, v in capacity.items() if 'gpu' in k.lower()}
    if gpu_cap:
        for k, v in sorted(gpu_cap.items()):
            print(f'  {k} = {v}')
    else:
        print('  (none)')

    sep('match_label_key — GPU vs iGPU filtering')
    product_labels = {k: v for k, v in labels.items()
                      if k == LABEL_KEY_DIRECT or k.startswith(LABEL_KEY_PREFIX)}
    if product_labels:
        for k, v in sorted(product_labels.items()):
            matched = match_label_key(k)
            tag = '✓ GPU    ' if matched else '✗ iGPU  '
            print(f'  {tag}  {k} = {v!r}')
    else:
        print('  (no amd.com/gpu.product-name* labels found)')

    sep('Resolved GPU names (what sky would see)')
    resolved = []
    for k, v in labels.items():
        if not match_label_key(k):
            continue
        name = get_accelerator_from_label(k, v)
        resolved.append(name)
        print(f'  {name!r}')
        print(f'    from key   = {k}')
        print(f'    from value = {v!r}')
    if not resolved:
        print('  (nothing matched)')

    sep('_normalize spot-checks')
    samples = [
        ('AMD_Radeon_RX_7900_XTX', False),
        ('AMD_Radeon_RX_7900_XT',  False),
        ('AMD_Instinct_MI300X',    False),
        ('AMD_Radeon_Pro_W7900',   False),
        ('AMD_Radeon_Graphics',    True),
        ('AMD_Radeon_780M',        True),
        ('AMD_Radeon_Vega_8',      True),
    ]
    for raw, expect_igpu in samples:
        name = _normalize(raw)
        igpu = _is_igpu(raw.lower())
        tag = '[iGPU filtered]' if igpu else '               '
        print(f'  {tag}  {raw:42s} -> {name!r}')

    sep()
    if resolved:
        print(f'OK — {len(resolved)} GPU type(s) detected on {node!r}: {resolved}')
    else:
        print(f'WARN — no GPU types resolved on {node!r}')


if __name__ == '__main__':
    main()
