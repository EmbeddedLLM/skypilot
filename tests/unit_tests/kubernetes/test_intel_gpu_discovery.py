"""Intel GPU discovery and resource selection without a live cluster."""
from types import SimpleNamespace
from unittest import mock

import pytest

from sky import exceptions
from sky.provision.kubernetes import utils


def _node(name, labels, resources):
    return SimpleNamespace(
        metadata=SimpleNamespace(name=name, labels=labels),
        status=SimpleNamespace(capacity=resources, allocatable=resources))


@pytest.mark.parametrize('raw,expected', [
    ('Flex_170', 'Intel-Flex-170'),
    ('Max_1550', 'Intel-Max-1550'),
    ('Intel_Arc_A770', 'Intel-Arc-A770'),
])
def test_intel_product_label(raw, expected):
    formatter = utils.IntelGPULabelFormatter
    assert formatter.get_accelerator_from_label_value(raw) == expected
    assert formatter.validate_label_value(raw) == (True, '')
    assert not formatter.validate_label_value('  ')[0]
    assert not formatter.match_label_key('gpu.intel.com/device.count')


@pytest.mark.parametrize('key', ['gpu.intel.com/i915', 'gpu.intel.com/xe'])
def test_intel_discovery(key, monkeypatch):
    monkeypatch.delenv('CUSTOM_GPU_RESOURCE_KEY', raising=False)
    node = _node('intel', {'gpu.intel.com/product': 'Flex_170'}, {key: '2'})
    with mock.patch.object(utils, 'get_kubernetes_nodes', return_value=[node]):
        assert utils.detect_accelerator_resource('test')[0]
        formatter, _ = utils.detect_gpu_label_formatter('test')
        assert isinstance(formatter, utils.IntelGPULabelFormatter)
        assert utils.get_unlabeled_accelerator_nodes('test') == []
        assert utils.get_accelerator_label_key_values(
            'test', 'Intel-Flex-170', 1) == (
                'gpu.intel.com/product', ['Flex_170'], None, None)
        assert utils.get_gpu_resource_key_for_labels(
            'test', 'gpu.intel.com/product', ['Flex_170']) == key
    assert utils.get_node_accelerator_count('test', node.status.allocatable) == 2
    assert utils.get_node_accelerator_count('test', {key: '1'}) == 1
    assert key in utils.get_handled_taint_keys()


@pytest.mark.parametrize('key', [
    'gpu.intel.com/monitoring',
    'gpu.intel.com/i915_monitoring',
    'gpu.intel.com/xe_monitoring',
])
def test_monitoring_is_not_compute(key, monkeypatch):
    monkeypatch.delenv('CUSTOM_GPU_RESOURCE_KEY', raising=False)
    node = _node('monitoring', {}, {key: '1'})
    with mock.patch.object(utils, 'get_kubernetes_nodes', return_value=[node]):
        assert not utils.detect_accelerator_resource('test')[0]
    assert utils.get_node_accelerator_count('test', {key: '1'}) == 0


@pytest.mark.parametrize('key,model', [
    ('gpu.intel.com/i915', 'intel-arc-a770'),
    ('gpu.intel.com/xe', 'intel-arc-b580'),
    ('amd.com/gpu', 'rx7900xtx'),
    ('nvidia.com/gpu', 'h100'),
])
def test_resource_selection_in_mixed_cluster(key, model, monkeypatch):
    monkeypatch.delenv('CUSTOM_GPU_RESOURCE_KEY', raising=False)
    label = 'skypilot.co/accelerator'
    nodes = [
        _node('other-amd', {label: 'mi300x'}, {'amd.com/gpu': '8'}),
        _node('other-nvidia', {label: 'a100'}, {'nvidia.com/gpu': '8'}),
        _node('target', {label: model}, {key: '1'}),
    ]
    with mock.patch.object(utils, 'get_kubernetes_nodes', return_value=nodes):
        assert utils.get_gpu_resource_key_for_labels('test', label,
                                                     [model]) == key


def test_ambiguous_intel_drivers(monkeypatch):
    monkeypatch.delenv('CUSTOM_GPU_RESOURCE_KEY', raising=False)
    label = 'gpu.intel.com/product'
    nodes = [
        _node(key, {label: 'Flex_170'}, {key: '1'})
        for key in ('gpu.intel.com/i915', 'gpu.intel.com/xe')
    ]
    with mock.patch.object(utils, 'get_kubernetes_nodes', return_value=nodes):
        with pytest.raises(exceptions.ResourcesUnavailableError,
                           match='multiple GPU resource types'):
            utils.get_gpu_resource_key_for_labels('test', label, ['Flex_170'])


def test_missing_intel_plugin(monkeypatch):
    monkeypatch.delenv('CUSTOM_GPU_RESOURCE_KEY', raising=False)
    node = _node('intel', {'gpu.intel.com/product': 'Flex_170'}, {})
    with mock.patch.object(utils, 'get_kubernetes_nodes', return_value=[node]):
        with pytest.raises(exceptions.ResourcesUnavailableError,
                           match='Cannot determine the Intel'):
            utils.get_gpu_resource_key_for_labels(
                'test', 'gpu.intel.com/product', ['Flex_170'])


def test_custom_resource_override(monkeypatch):
    monkeypatch.setenv('CUSTOM_GPU_RESOURCE_KEY', 'example.com/gpu')
    assert utils.get_gpu_resource_key_for_labels(
        'test', 'skypilot.co/accelerator', ['custom']) == 'example.com/gpu'
    assert utils.get_node_accelerator_count(
        'test', {'example.com/gpu': '2'}) == 2


def test_unlabeled_intel_node():
    node = _node('intel', {}, {'gpu.intel.com/xe': '1'})
    with mock.patch.object(utils, 'get_kubernetes_nodes', return_value=[node]):
        assert utils.get_unlabeled_accelerator_nodes('test') == [node]
