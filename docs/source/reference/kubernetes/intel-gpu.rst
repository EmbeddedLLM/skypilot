.. _kubernetes-intel-gpu:

Using Intel GPUs on Kubernetes
==============================

SkyPilot supports Intel GPUs that use the ``xe`` kernel driver and are exposed
through the ``gpu.intel.com/xe`` resource, such as Arc Pro B-series cards.
GPUs using the ``i915`` driver (``gpu.intel.com/i915``), including Arc
A-series, Data Center GPU Flex and Max, are not supported. Monitoring
resources are not counted as GPUs.

Cluster setup
-------------

Install the host ``xe`` GPU driver, the `Intel GPU device plugin
<https://intel.github.io/intel-device-plugins-for-kubernetes/cmd/gpu_plugin/README.html>`_,
and its Node Feature Discovery (NFD) rules, v0.37.0 or later. Use
``shared-dev-num=1`` if you want reported counts to correspond to unshared GPU
devices. With sharing enabled, Kubernetes advertises allocation slots rather
than physical GPU counts.

Each node must expose a single GPU model and a single GPU resource type.

GPU labels
----------

SkyPilot identifies Intel GPUs from the NFD ``gpu.intel.com/product`` label,
which the NFD rules set automatically:

.. code-block:: text

   gpu.intel.com/product=Arc_Pro_B60  -> Intel-Arc-Pro-B60
   gpu.intel.com/product=Arc_B580     -> Intel-Arc-B580

Request the GPU by its SkyPilot name, e.g. ``--gpus Intel-Arc-Pro-B60:1``.
Pods requesting an Intel GPU use the ``gpu.intel.com/xe`` resource. Because the
resource is derived from the label, this also works with autoscalers that
create Intel nodes on demand.

Workloads need a container image with the Intel userspace drivers and compute
runtime.

Manual verification
-------------------

After installing this version, restart the API server to pick up the changes:

.. code-block:: bash

   sky api stop
   sky api start
   kubectl get nodes -o json
   sky check kubernetes
   sky show-gpus --infra kubernetes

Verify that each Intel node advertises ``gpu.intel.com/xe`` and has a
``gpu.intel.com/product`` label. The GPU listing should show the corresponding
model and allocatable count. Repeat with NVIDIA and AMD nodes in the same
cluster and confirm their counts are unchanged.

For a launch using an Intel-compatible image and the discovered accelerator,
inspect the resulting pod with ``kubectl get pod <pod-name> -o yaml``. Its GPU
request and limit should use ``gpu.intel.com/xe``. Check dashboard free counts
before and during the workload: one allocated GPU should reduce availability
by one.
