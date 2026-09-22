.. _kubernetes-intel-gpu:

Using Intel GPUs on Kubernetes
==============================

SkyPilot discovers Intel GPUs through Kubernetes node resources and labels.
Both ``gpu.intel.com/i915`` and ``gpu.intel.com/xe`` are supported. Monitoring
resources are not counted as GPUs.

Cluster setup
-------------

Install the host GPU drivers, the `Intel GPU device plugin
<https://intel.github.io/intel-device-plugins-for-kubernetes/cmd/gpu_plugin/README.html>`_,
and its Node Feature Discovery (NFD) rules. Use ``shared-dev-num=1`` if you want
reported counts to correspond to unshared GPU devices. With sharing enabled,
Kubernetes advertises allocation slots rather than physical GPU counts.

Use nodes exposing a single GPU model and a single GPU resource type.
A node containing different GPU models, such as an integrated GPU plus an Arc
card, must have the unwanted devices excluded from the device plugin before
being labeled with a single model name.

GPU labels
----------

Intel NFD product labels are recognized automatically:

.. code-block:: text

   gpu.intel.com/product=Flex_170  -> Intel-Flex-170
   gpu.intel.com/product=Max_1550  -> Intel-Max-1550

For Arc or integrated GPUs without an NFD product label, add a lowercase
SkyPilot label identifying the GPU actually exposed by the device plugin:

.. code-block:: bash

   kubectl label node <node-name> skypilot.co/accelerator=intel-arc-a770 --overwrite

PCI device-ID labels alone do not identify a model in SkyPilot yet. Do not use
``i915`` or ``xe`` as model names: they identify drivers, not GPU models.

SkyPilot chooses the pod resource key from the capacity of nodes matching the
accelerator label. If matching nodes expose different resource types, give each
group a distinct SkyPilot accelerator label, such as ``intel-i915-arc-a770`` and
``intel-xe-arc-a770``, and request the corresponding name. Intel scale-from-zero
resource selection requires an explicit ``CUSTOM_GPU_RESOURCE_KEY`` on the API
server; automatic detection requires an existing node advertising capacity.

Workloads need a container image with the appropriate Intel userspace drivers
and compute runtime. Discovery and resource selection alone do not establish
compatibility with a particular framework or workload.

Manual verification
-------------------

After installing this version, restart the API server to pick up the changes:

.. code-block:: bash

   sky api stop
   sky api start
   kubectl get nodes -o json
   sky check kubernetes
   sky show-gpus --infra kubernetes

Verify that each Intel node advertises ``gpu.intel.com/i915`` or
``gpu.intel.com/xe`` and has a product or SkyPilot accelerator label. The GPU
listing should show the corresponding model and allocatable count. Repeat with
NVIDIA and AMD nodes in the same cluster and confirm their counts are unchanged.

For a launch using an Intel-compatible image and the discovered accelerator,
inspect the resulting pod with ``kubectl get pod <pod-name> -o yaml``. Its GPU
request and limit should use the matching Intel resource key. Check dashboard
free counts before and during the workload: one allocated GPU should reduce
availability by one. Monitoring resources must not increase GPU counts.

Focused regression tests:

.. code-block:: bash

   pytest -n 0 tests/unit_tests/kubernetes/test_intel_gpu_discovery.py tests/unit_tests/kubernetes/test_gpu_label_formatters.py tests/unit_tests/kubernetes/test_kubernetes_utils.py
