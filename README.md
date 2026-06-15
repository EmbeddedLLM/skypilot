<h2>🍴 EmbeddedLLM Fork</h2>

<p>
  This is a downstream fork of <a href="https://github.com/skypilot-org/skypilot">skypilot-org/skypilot</a> maintained by <a href="https://github.com/EmbeddedLLM">EmbeddedLLM</a>.
  It tracks upstream releases and stacks a small set of custom patches on top.
</p>

<table>
  <tr><td><b>Upstream version</b></td><td><code>0.12.0</code></td></tr>
  <tr><td><b>Branch</b></td><td><code>ellm-0.12.0</code></td></tr>
  <tr><td><b>Image</b></td><td><code>ghcr.io/embeddedllm/skypilot:v0.12.0</code></td></tr>
  <tr><td><b>Upstream repo</b></td><td><a href="https://github.com/skypilot-org/skypilot">skypilot-org/skypilot</a></td></tr>
</table>

<h3>🐳 Image Tags</h3>

<table>
  <thead>
    <tr><th>Tag</th><th>Meaning</th></tr>
  </thead>
  <tbody>
    <tr><td><code>v0.12.0</code></td><td>Stable, production-ready build based on upstream v0.12.0</td></tr>
    <tr><td><code>v0.12.0-dev</code></td><td>Development build off <code>ellm-0.12.0</code> branch, not yet stable</td></tr>
  </tbody>
</table>

<h3>🔧 Custom Patches</h3>

<table>
  <thead>
    <tr>
      <th>Patch</th>
      <th>Commit</th>
      <th>Files Changed</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Enable dual GPU in a single API server</b></td>
      <td><code>493fb1f</code></td>
      <td>
        <code>sky/clouds/kubernetes.py</code><br>
        <code>sky/provision/kubernetes/utils.py</code>
      </td>
      <td>
        Makes <code>get_node_accelerator_count</code> check both <code>nvidia.com/gpu</code>
        and <code>amd.com/gpu</code> resource keys so nodes with either vendor GPU report
        a non-zero accelerator count.<br>
        <em>Note: the original <code>kubernetes.py</code> resource-key selection from
        this patch keyed off <code>skypilot.co/gpu</code> node labels. The
        formatter-driven resource-key selection in <code>9cd2668</code> + the
        mixed-cluster fix in <code>f65b71f</code> superseded that logic; this patch's
        contribution is now the <code>get_node_accelerator_count</code> change.</em>
      </td>
    </tr>
    <tr>
      <td><b>Automatic AMD GPU detection via device plugin labels</b></td>
      <td><code>9cd2668</code><br>(simplified by <code>b35db4a</code>)</td>
      <td>
        <code>sky/provision/kubernetes/utils.py</code><br>
        <code>sky/catalog/kubernetes_catalog.py</code><br>
        <code>sky/clouds/kubernetes.py</code><br>
        <code>sky/utils/gpu_names.py</code><br>
        <code>sky/client/cli/command.py</code>
      </td>
      <td>
        AMD GPU nodes are detected automatically when the
        <a href="https://github.com/ROCm/k8s-device-plugin">AMD device plugin</a>
        is installed — no <code>sky gpus label</code> required.
        Adds <code>AMDGPULabelFormatter</code> which reads the
        <code>amd.com/gpu.product-name = &lt;NAME&gt;</code> direct label.
        Each node must expose exactly one GPU type (homogeneous-node assumption);
        nodes with multiple distinct AMD GPUs (e.g. iGPU + dGPU) are not
        supported, and neither is the AMD device plugin's suffix label format
        emitted on such nodes. iGPU-only nodes are treated like any other GPU node.
        All GPU detection code paths — <code>sky gpus list</code>, per-node status,
        pod scheduling, CPU-only node selection — iterate all formatters per node,
        enabling mixed NVIDIA + AMD clusters with no extra configuration.
        Adds 33 AMD canonical GPU names (MI Instinct CDNA1–4, Radeon Pro W-series,
        Radeon RX RDNA2/3) to the shared GPU name registry.<br>
        <em>Follow-up <code>b35db4a</code> dropped suffix-format support
        (<code>amd.com/gpu.product-name.&lt;NAME&gt; = "1"</code>, only emitted on
        multi-GPU-type nodes which we don't support) and removed iGPU/APU
        filtering, since iGPU-only nodes are valid GPU nodes under the
        homogeneous-node assumption. Net effect: <code>AMDGPULabelFormatter</code>
        is now structurally identical to other single-key formatters.</em>
      </td>
    </tr>
    <tr>
      <td><b>Fix pod scheduling for mixed NVIDIA + AMD clusters</b></td>
      <td><code>e9581a9</code></td>
      <td><code>sky/provision/kubernetes/instance.py</code></td>
      <td>
        Fixes pod scheduling and SkyServe replica placement on AMD GPU nodes in
        a mixed cluster. <code>instance.py</code> previously called
        <code>get_gpu_resource_key(context)</code> (cluster-wide default) in three places,
        which returned the wrong vendor key for the non-default GPU type:
        <ul>
          <li><b>needs_gpus</b>: AMD pods were seen as not needing GPUs (NVIDIA key missing from AMD pod limits) → nvidia RuntimeClass never skipped, toleration never added</li>
          <li><b>gpu_toleration</b>: wrong vendor key in pod toleration → pod rejected by AMD node taint</li>
          <li><b>error messages</b>: wrong resource key shown when scheduling fails</li>
        </ul>
        Fix reads the GPU resource key directly from the pod's resource limits and
        checks all <code>SUPPORTED_GPU_RESOURCE_KEYS</code> values instead of the cluster default.
      </td>
    </tr>
    <tr>
      <td><b>Fix wrong GPU resource key for NVIDIA pods in mixed clusters</b></td>
      <td><code>f65b71f</code></td>
      <td><code>sky/clouds/kubernetes.py</code></td>
      <td>
        In a mixed AMD + NVIDIA cluster, requesting an NVIDIA GPU (e.g. A4000)
        previously put <code>amd.com/gpu</code> in the pod's resource limits
        instead of <code>nvidia.com/gpu</code>, making the pod unschedulable —
        NVIDIA nodes don't have <code>amd.com/gpu</code> capacity, and AMD
        nodes don't have the right node-affinity label. Root cause: when the
        matched label key was non-AMD (GFD, SkyPilot, etc.), the code called
        <code>get_gpu_resource_key(context)</code>, which scans the cluster
        and returns the first vendor key in dict-iteration order
        (<code>amd.com/gpu</code> before <code>nvidia.com/gpu</code>); in a
        mixed cluster this picks AMD for an NVIDIA-targeted request. Fix:
        derive the resource key directly from the label-formatter category —
        <code>amd.com/*</code> → <code>amd.com/gpu</code>; any other
        recognized GPU label → <code>nvidia.com/gpu</code>; fall back to
        <code>get_gpu_resource_key</code> only when no formatter matched.
      </td>
    </tr>
    <tr>
      <td><b>Fix GPU count display for NVIDIA replicas in mixed clusters</b></td>
      <td><code>57c8ba2</code></td>
      <td><code>sky/provision/kubernetes/utils.py</code></td>
      <td>
        <code>process_skypilot_pods</code> read each pod's <code>gpu_count</code>
        from the cluster-default resource key
        (<code>get_gpu_resource_key(context)</code>). In a mixed cluster this
        is <code>amd.com/gpu</code>, so an NVIDIA pod's
        <code>nvidia.com/gpu</code> request was missed and <code>gpu_count</code>
        came back as 0. Effect: <code>sky status</code> / cost-report displayed
        NVIDIA replicas as having no accelerators in mixed clusters. Replica
        scheduling itself was correct (handled by <code>f65b71f</code>); only
        the status display lied. Fix: iterate
        <code>SUPPORTED_GPU_RESOURCE_KEYS.values()</code> and read whichever
        vendor key the pod actually requested.
      </td>
    </tr>
    <tr>
      <td><b>Fix node-affinity values rendered as int for AMD GPU labels</b></td>
      <td><code>37a0b54</code></td>
      <td>
        <code>sky/provision/kubernetes/utils.py</code><br>
        <code>sky/templates/kubernetes-ray.yml.j2</code>
      </td>
      <td>
        For AMD device-plugin suffix labels (e.g.
        <code>amd.com/gpu.product-name.AMD_Radeon_RX_7900_XTX="1"</code>), the
        Kubernetes Python client deserializes the value <code>"1"</code> as
        Python <code>int 1</code>. The int leaked into
        <code>k8s_acc_label_values</code> and was rendered into the
        node-affinity <code>matchExpressions.values</code> list as a JSON
        number, causing pod creation to fail with:
        <code>cannot unmarshal number into Go struct field
        NodeSelectorRequirement…values of type string</code>. Two fixes:
        coerce the label value to <code>str</code> in
        <code>get_accelerator_label_key_values</code> (source of truth), and
        explicitly quote <code>{{label_value}}</code> in the j2 template as
        defense against future int leakage. NVIDIA via GFD is unaffected
        because GFD label values are non-numeric strings.
      </td>
    </tr>
    <tr>
      <td><b>[Kubernetes] Fix podip endpoint in HA mode</b></td>
      <td><code>f3b4561</code></td>
      <td><code>sky/provision/kubernetes/network.py</code></td>
      <td>
        Fixes <code>http://None</code> endpoint when using <code>high_availability</code>
        + <code>podip</code> port mode for sky-serve-controller. In HA mode the controller
        runs as a Deployment — Kubernetes assigns random pod name suffixes so the expected
        <code>{cluster_name}-head</code> pod never exists. Fix uses label selectors instead
        of pod name lookup, working correctly for both HA and non-HA modes.
      </td>
    </tr>
    <tr>
      <td><b>[Kubernetes] Replace rsync with tar-stream for in-pod file transfer</b></td>
      <td><code>4f1c887</code><br>(plus <code>d5731f4</code>, <code>e3237a7</code>)</td>
      <td>
        <code>sky/utils/command_runner.py</code><br>
        <code>sky/utils/kubernetes/rsync_helper.sh</code>
      </td>
      <td>
        rsync 3.4.x over <code>kubectl exec</code> deadlocks at session teardown on
        Ubuntu 26 / kernel 6.8+: the data transfer completes (visible <code>100%</code>
        in logs) but neither end ever exits, leaving the SkyServe controller stuck
        at <em>Preparing SkyPilot runtime (1/3 - initializing)</em>. Reproduces with
        both rsync ends at 3.4.1, with <code>--protocol=31</code>, <code>--old-args</code>,
        <code>--whole-file</code>, <code>--inplace</code>, <code>--timeout=N</code>;
        a one-way <code>tar -c | kubectl exec -i -- tar -x</code> works fine.
        Override <code>KubernetesCommandRunner.rsync</code> to use a one-way tar pipeline,
        sidestepping rsync's bidirectional teardown handshake entirely. Replicates
        rsync features: <code>.skyignore</code>/<code>.gitignore</code> via
        <code>--exclude-ignore</code>, <code>.git/info/exclude</code> via
        <code>--exclude-from</code>, file-target rename via
        <code>tar --transform='s/^src$/dst/'</code>, <code>--no-same-owner</code>
        in lieu of <code>--no-owner --no-group</code>. Also forces SPDY transport
        (<code>KUBECTL_REMOTE_COMMAND_WEBSOCKETS=false</code>) for any kubectl
        subprocess, since the WebSocket transport on newer kernels deadlocks at
        ~2-3 MB of bidirectional traffic on the same HTTP/2 stream.
      </td>
    </tr>
    <tr>
      <td><b>[Kubernetes] Fix kubectl exec hang after setup script completes</b></td>
      <td><code>502df1c</code><br>(plus <code>32e4e61</code>)</td>
      <td><code>sky/templates/kubernetes-ray.yml.j2</code></td>
      <td>
        Setup at phase 2/3 hung indefinitely on Ubuntu 26+ even though the remote
        bash exited cleanly with rc=0. Forensic traces showed the wait stanza's
        <code>tail -f /tmp/runtime-setup.log &amp; … kill $TAIL_PID</code> failing
        with <code>kill: (PID) - Permission denied</code> under
        <code>bash --login -c -i</code> — the orphaned tail kept the kubectl exec
        stdout fd open, so the session never received EOF. Fix: use
        <code>tail -f --pid=$$</code> so tail self-terminates when the parent
        script exits regardless of <code>kill</code> succeeding; add
        <code>jobs -p | xargs kill</code> + <code>pkill -P $$</code> belt-and-
        suspenders before <code>exec 1&gt;&amp;-; exec 2&gt;&amp;-</code>. Also adds
        forensic <code>set -x</code> tracing tee'd to
        <code>/tmp/setup_commands_trace.log</code>, EXIT/ERR traps recording line
        + rc + timestamp, and end-of-body marker
        <code>===SKY_SETUP_BODY_COMPLETE===</code> for diagnosing future hangs.
      </td>
    </tr>
    <tr>
      <td><b>[Serve] Raise per-controller service capacity for k8s workloads</b></td>
      <td><code>c6f8f23</code></td>
      <td><code>sky/utils/controller_utils.py</code></td>
      <td>
        Upstream's <code>_get_number_of_services</code> reserves
        <code>LAUNCHES_PER_SERVICE × LONG_WORKER_MEM_GB</code> (4 × 0.4 ≈ 1.6 GB)
        per service for an embedded API server's worker pool inside the
        controller pod, sized for slow cloud-VM launches that load heavyweight
        cloud SDKs. With 8 GB controller memory this caps services at 2.
        For k8s-mostly deployments where replica launches are pod-create operations,
        this is excessive. Lower <code>LAUNCHES_PER_SERVICE</code> 4 → 2 and
        introduce <code>SERVE_LOCAL_API_LONG_WORKER_MEM_GB = 0.25</code> (separate
        knob from the global <code>LONG_WORKER_MEM_GB</code>, so it doesn't affect
        the central API server's worker pool). Per-service cost drops from
        ~2.1 GB to ~1.0 GB. Capacity:
        8 GB → 6 services (was 2), 16 GB → 14, 32 GB → 30. Tradeoff: a service
        firing &gt;2 simultaneous replica launches will queue.
      </td>
    </tr>
    <tr>
      <td><b>Pin uv pip to runtime venv's Python via <code>--python</code> flag</b></td>
      <td><code>78fe751</code></td>
      <td>
        <code>sky/skylet/constants.py</code><br>
        <code>sky/templates/kubernetes-ray.yml.j2</code><br>
        <code>sky/adaptors/oci.py</code>
      </td>
      <td>
        uv's environment auto-discovery is unreliable on user-provided Docker
        images that ship a Python interpreter at a non-standard prefix
        (e.g. ROCm images with <code>/opt/python</code> python-build-standalone
        layouts in <code>PATH</code>). <code>VIRTUAL_ENV</code> is silently ignored
        and uv resolves against the image's Python: on Python 3.12 base images
        ray 2.9.3 install hard-fails (<em>no wheels with a matching Python ABI
        tag (cp312)</em>); on 3.10/3.11 base images uv silently mutates the
        wrong Python's site-packages without erroring. Add
        <code>--python &lt;venv&gt;/bin/python</code> to every uv pip
        install/uninstall/list and <code>uv run</code> invocation that targets
        the SkyPilot runtime venv. Centralised via new
        <code>SKY_UV_PIP_INSTALL_CMD</code> / <code>UNINSTALL</code> /
        <code>LIST</code> constants. Strict improvement on working images
        (same end state, no longer mutates system Python); enables broken images.
      </td>
    </tr>
    <tr>
      <td><b>[Kubernetes] Exclude <code>kubernetes==36.0.0</code> (in-cluster auth regression)</b></td>
      <td><code>69b0a69</code></td>
      <td><code>sky/setup_files/dependencies.py</code></td>
      <td>
        The <code>kubernetes</code> Python client <code>36.0.0</code> restructured
        bearer-token storage: <code>Configuration.auth_settings()</code> reads the
        token from <code>api_key['BearerToken']</code>, but
        <code>load_incluster_config()</code> still writes it to the old
        <code>api_key['authorization']</code> key. Result: in-cluster pods send
        every request with <b>no</b> <code>Authorization</code> header and the
        apiserver rejects them as <code>system:anonymous</code> → <code>401</code>,
        surfacing as <code>sky check</code> reporting <em>"Invalid credentials"</em>
        even though the ServiceAccount token, RBAC, and cluster are all healthy.
        Because <code>dependencies.py</code> only floored the version
        (<code>&gt;=20.0.0,!=32.0.0</code>), a fresh image build picked up the
        just-released 36.0.0 and broke the API server. Fix: extend the exclusion to
        <code>!=32.0.0,!=36.0.0</code>. Upstream fixed it in 36.0.1
        (<a href="https://github.com/kubernetes-client/python/pull/2585">PR #2585</a>);
        the resolver now lands on 36.0.2+.
      </td>
    </tr>
    <tr>
      <td><b>[Kubernetes] Accept PEP 585 <code>dict[K, V]</code> type strings in pod_config validator</b></td>
      <td><code>827ff42</code></td>
      <td><code>sky/provision/kubernetes/utils.py</code></td>
      <td>
        Second fallout from the <code>kubernetes</code> client <code>36.x</code>
        upgrade (companion to the <code>!=36.0.0</code> exclusion above, which lands
        the resolver on 36.0.2). The 36.x models were regenerated with PEP 585 type
        strings, so map fields like <code>metadata.labels</code> now declare their
        type as <code>dict[str, str]</code> (square brackets) instead of the old
        <code>dict(str, str)</code> (parentheses). SkyPilot's hand-rolled
        <code>PodValidator</code> (a reimplementation of the client's deserializer)
        only matched the parenthesized form, so the bracket form fell through to the
        model-import path and failed with
        <code>No module named 'kubernetes.client.models.dict[str, str]'</code>,
        breaking <code>sky serve up</code> / <code>sky launch</code> at pod_config
        validation. Fix: match both <code>dict(</code> and <code>dict[</code> and
        parse either closing bracket. Note <code>dict_to_k8s_object()</code> is
        unaffected — it delegates to the client's own (self-consistent)
        <code>deserialize()</code> rather than reimplementing it.
      </td>
    </tr>
  </tbody>
</table>

<h3>🛠️ Development Workflow</h3>

Never commit directly to `ellm-{version}`. Create a feature branch off it, then open a PR back into it.

```bash
# 1. Branch off the active version branch
git checkout ellm-0.12.0
git checkout -b feat/my-feature

# 2. Make changes, commit
git add <files>
git commit -m "[Area] Description"
git push origin feat/my-feature

# 3. Open a PR → target ellm-0.12.0 (not master)
gh pr create --base ellm-0.12.0 --title "..." --body "..."
```

Build and push a dev image to test before merging:
```bash
docker buildx build --push --platform linux/amd64 \
  -t ghcr.io/embeddedllm/skypilot:v0.12.0-dev \
  -f Dockerfile .
```

Once the PR is merged and validated, promote to stable:
```bash
docker tag ghcr.io/embeddedllm/skypilot:v0.12.0-dev ghcr.io/embeddedllm/skypilot:v0.12.0
docker push ghcr.io/embeddedllm/skypilot:v0.12.0
```

**Deploying with Helm**

The Helm chart is pinned to the same upstream version. Always specify `--version` explicitly:
```bash
helm upgrade --install $RELEASE_NAME skypilot/skypilot \
  --version 0.12.0 \
  --namespace $NAMESPACE \
  --create-namespace \
  --set apiService.image=ghcr.io/embeddedllm/skypilot:v0.12.0 \
  --set ingress.authCredentials=$AUTH_STRING
```

> When moving to a new upstream version (e.g. `v0.13.0`), update **both** `--version` and `--set apiService.image` together. The Helm chart version must always match the image version.

<h3>⬆️ Updating to a New Upstream Version</h3>

Each upstream version gets its own branch (`ellm-0.12.0`, `ellm-0.13.0`, ...). Old branches are kept as rollback points.

```bash
# 1. Sync master with upstream
git checkout master
git fetch upstream
git merge upstream/master
git push origin master

# 2. Create new branch from updated master
git checkout -b ellm-{new_version}

# 3. Cherry-pick custom patches (commit hashes from the table above)
git cherry-pick 493fb1f  # Enable dual GPU in a single API server
git cherry-pick f3b4561  # Fix podip endpoint in HA mode
git cherry-pick 9cd2668  # Automatic AMD GPU detection via device plugin labels
git cherry-pick b35db4a  # Drop suffix-format + iGPU filtering (simplifies 9cd2668)
git cherry-pick f65b71f  # Fix wrong GPU resource key for NVIDIA pods in mixed clusters
git cherry-pick 57c8ba2  # Fix GPU count display for NVIDIA replicas in mixed clusters
git cherry-pick 37a0b54  # Fix node-affinity values rendered as int for AMD GPU labels
git cherry-pick e9581a9  # Fix pod scheduling for mixed NVIDIA + AMD clusters
# Replace rsync with tar-stream for in-pod transfer (3 commits, in order):
git cherry-pick d5731f4 e3237a7 4f1c887
# Fix kubectl exec hang at end of setup script (2 commits, in order):
git cherry-pick 32e4e61 502df1c
git cherry-pick c6f8f23  # Raise per-controller service capacity for k8s
git cherry-pick 78fe751  # Pin uv pip to runtime venv via --python
git cherry-pick 69b0a69  # Exclude kubernetes==36.0.0 (in-cluster auth regression)
git cherry-pick 827ff42  # Accept PEP 585 dict[K,V] type strings in pod_config validator
# Resolve any conflicts if upstream changed the same files

# 4. Push new branch
git push origin ellm-{new_version}
```

> After creating the new branch, update this README: bump **Upstream version**, **Branch**, **Image**, and the commit hashes in the patch table. Build and push the new image as `ghcr.io/embeddedllm/skypilot:v{new_version}`.

---



<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/skypilot-org/skypilot/master/docs/source/images/skypilot-wide-dark-1k.png">
    <img alt="SkyPilot" src="https://raw.githubusercontent.com/skypilot-org/skypilot/master/docs/source/images/skypilot-wide-light-1k.png" width=55%>
  </picture>
</p>

<p align="center">
  <a href="https://docs.skypilot.co/">
    <img alt="Documentation" src="https://img.shields.io/badge/docs-gray?logo=readthedocs&logoColor=f5f5f5">
  </a>

  <a href="https://github.com/skypilot-org/skypilot/releases">
    <img alt="GitHub Release" src="https://img.shields.io/github/release/skypilot-org/skypilot.svg">
  </a>

  <a href="http://slack.skypilot.co">
    <img alt="Join Slack" src="https://img.shields.io/badge/SkyPilot-Join%20Slack-blue?logo=slack">
  </a>

  <a href="https://github.com/skypilot-org/skypilot/releases">
    <img alt="Downloads" src="https://img.shields.io/pypi/dm/skypilot">
  </a>

</p>

<h3 align="center">
    Run AI on Any Infrastructure
</h3>

<div align="center">

#### [🌟 **SkyPilot Demo** 🌟: Click to see a 1-minute tour](https://demo.skypilot.co/dashboard/)

</div>


SkyPilot is a system to run, manage, and scale AI workloads on any AI infrastructure.

SkyPilot gives **AI teams** a simple interface to run jobs on any infra.
**Infra teams** get a unified control plane to manage any AI compute — with advanced scheduling, scaling, and orchestration.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./docs/source/images/skypilot-abstractions-long-2-dark.png">
  <img src="./docs/source/images/skypilot-abstractions-long-2.png" alt="SkyPilot Abstractions">
</picture>

-----

:fire: *News* :fire:
- [Dec 2025] **SkyPilot v0.11** released: Multi-Cloud Pools, Fast Managed Jobs, Enterprise-Readiness at Large Scale, Programmability. [**Release notes**](https://github.com/skypilot-org/skypilot/releases/tag/v0.11.0)
- [Dec 2025] **SkyPilot Pools** released: Run batch inference and other jobs on a managed pool of warm workers (across clouds or clusters). [**blog**](https://blog.skypilot.co/skypilot-pools-deepseek-ocr/), [**docs**](https://docs.skypilot.co/en/latest/examples/pools.html)
- [Dec 2025] Train **an agent to use Google Search** as a tool with RL on your Kubernetes or clouds: [**blog**](https://blog.skypilot.co/verl-tool-calling/), [**example**](./llm/verl/)
- [Nov 2025] Serve **Kimi K2 Thinking** with reasoning capabilities on your Kubernetes or clouds: [**example**](./llm/kimi-k2-thinking/)
- [Oct 2025] Run **RL training for LLMs** with SkyRL on your Kubernetes or clouds: [**example**](./llm/skyrl/)
- [Oct 2025] Train and serve [Andrej Karpathy's](https://x.com/karpathy/status/1977755427569111362) **nanochat** - the best ChatGPT that $100 can buy: [**example**](./llm/nanochat)
- [Oct 2025] Run large-scale **LLM training with TorchTitan** on any AI infra: [**example**](./examples/training/torchtitan)
- [Sep 2025] Scaling AI infrastructure at Abridge - **10x faster development** with SkyPilot: [**blog**](https://blog.skypilot.co/abridge/)
- [Sep 2025] Network and Storage Benchmarks for LLM training on the cloud: [**blog**](https://maknee.github.io/blog/2025/Network-And-Storage-Training-Skypilot/)
- [Aug 2025] Serve and finetune **OpenAI GPT-OSS models** (gpt-oss-120b, gpt-oss-20b) with one command on any infra: [**serve**](./llm/gpt-oss/) + [**LoRA and full finetuning**](./llm/gpt-oss-finetuning/)
- [Jul 2025] Run distributed **RL training for LLMs** with Verl (PPO, GRPO) on any cloud: [**example**](./llm/verl/)

## Overview

SkyPilot **is easy to use for AI teams**:
- Quickly spin up compute on your own infra
- Environment and job as code — simple and portable
- Easy job management: queue, run, and auto-recover many jobs

SkyPilot **makes Kubernetes easy for AI & Infra teams**:

- Slurm-like ease of use, cloud-native robustness
- Local dev experience on K8s: SSH into pods, sync code, or connect IDE
- Turbocharge your clusters: gang scheduling, multi-cluster, and scaling

SkyPilot **unifies multiple clusters, clouds, and hardware**:
- One interface to use reserved GPUs, Kubernetes clusters, Slurm clusters, or 20+ clouds
- [Flexible provisioning](https://docs.skypilot.co/en/latest/examples/auto-failover.html) of GPUs, TPUs, CPUs, with auto-retry
- [Team deployment](https://docs.skypilot.co/en/latest/reference/api-server/api-server.html) and resource sharing

SkyPilot **cuts your cloud costs & maximizes GPU availability**:
* Autostop: automatic cleanup of idle resources
* [Spot instance support](https://docs.skypilot.co/en/latest/examples/managed-jobs.html#running-on-spot-instances): 3-6x cost savings, with preemption auto-recovery
* Intelligent scheduling: automatically run on the cheapest & most available infra

SkyPilot supports your existing GPU, TPU, and CPU workloads, with no code changes.

Install with pip:
```bash
# Choose your clouds:
pip install -U "skypilot[kubernetes,aws,gcp,azure,oci,nebius,lambda,runpod,fluidstack,paperspace,cudo,ibm,scp,seeweb,shadeform,verda]"
```
To get the latest features and fixes, use the nightly build or [install from source](https://docs.skypilot.co/en/latest/getting-started/installation.html):
```bash
# Choose your clouds:
pip install "skypilot-nightly[kubernetes,aws,gcp,azure,oci,nebius,lambda,runpod,fluidstack,paperspace,cudo,ibm,scp,seeweb,shadeform,verda]"
```

To use SkyPilot directly with your agent (Claude Code, Codex, etc.), install the [SkyPilot Skill](https://docs.skypilot.co/en/latest/getting-started/skill.html). Tell your agent:
```
Fetch and follow https://github.com/skypilot-org/skypilot/blob/HEAD/agent/INSTALL.md to install the skypilot skill
```

<p align="center">
  <img src="docs/source/_static/intro.gif" alt="SkyPilot">
</p>

Current supported infra: Kubernetes, Slurm, AWS, GCP, Azure, OCI, CoreWeave, Nebius, Lambda Cloud, RunPod, Fluidstack,
Cudo, Digital Ocean, Paperspace, Cloudflare, Samsung, IBM, Vast.ai, VMware vSphere, Seeweb, Prime Intellect, Shadeform, Verda Cloud, VastData, Crusoe.
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/skypilot-org/skypilot/master/docs/source/images/cloud-logos-dark.png">
    <img alt="SkyPilot" src="https://raw.githubusercontent.com/skypilot-org/skypilot/master/docs/source/images/cloud-logos-light.png" width=85%>
  </picture>
</p>
<!-- source xcf file: https://drive.google.com/drive/folders/1S_acjRsAD3T14qMeEnf6FFrIwHu_Gs_f?usp=drive_link -->


## Getting started
You can find our documentation [here](https://docs.skypilot.co/).
- [Installation](https://docs.skypilot.co/en/latest/getting-started/installation.html)
- [Quickstart](https://docs.skypilot.co/en/latest/getting-started/quickstart.html)
- [CLI reference](https://docs.skypilot.co/en/latest/reference/cli.html)

## SkyPilot in 1 minute

A SkyPilot task specifies: resource requirements, data to be synced, setup commands, and the task commands.

Once written in this [**unified interface**](https://docs.skypilot.co/en/latest/reference/yaml-spec.html) (YAML or Python API), the task can be launched on any available infra (Kubernetes, Slurm, cloud, etc.).  This avoids vendor lock-in, and allows easily moving jobs to a different provider.

Paste the following into a file `my_task.yaml`:

```yaml
resources:
  accelerators: A100:8  # 8x NVIDIA A100 GPU

num_nodes: 1  # Number of VMs to launch

# Working directory (optional) containing the project codebase.
# Its contents are synced to ~/sky_workdir/ on the cluster.
workdir: ~/torch_examples

# Commands to be run before executing the job.
# Typical use: pip install -r requirements.txt, git clone, etc.
setup: |
  cd mnist
  pip install -r requirements.txt

# Commands to run as a job.
# Typical use: launch the main program.
run: |
  cd mnist
  python main.py --epochs 1
```

Prepare the workdir by cloning:
```bash
git clone https://github.com/pytorch/examples.git ~/torch_examples
```

Launch with `sky launch` (note: [access to GPU instances](https://docs.skypilot.co/en/latest/cloud-setup/quota.html) is needed for this example):
```bash
sky launch my_task.yaml
```

SkyPilot then performs the heavy-lifting for you, including:
1. Find the cheapest & available infra across your clusters or clouds
2. Provision the GPUs (pods or VMs), with auto-failover if the infra returned capacity errors
3. Sync your local `workdir` to the provisioned cluster
4. Auto-install dependencies by running the task's `setup` commands
5. Run the task's `run` commands, and stream logs

See [Quickstart](https://docs.skypilot.co/en/latest/getting-started/quickstart.html) to get started with SkyPilot.

## Runnable examples

See [**SkyPilot examples**](https://docs.skypilot.co/en/docs-examples/examples/index.html) that cover: development, training, serving, LLM models, AI apps, and common frameworks.

Latest featured examples:

| Task | Examples |
|----------|----------|
| Training | [Verl](https://docs.skypilot.co/en/latest/examples/training/verl.html), [Finetune Llama 4](https://docs.skypilot.co/en/latest/examples/training/llama-4-finetuning.html), [TorchTitan](https://docs.skypilot.co/en/latest/examples/training/torchtitan.html), [PyTorch](https://docs.skypilot.co/en/latest/getting-started/tutorial.html), [DeepSpeed](https://docs.skypilot.co/en/latest/examples/training/deepspeed.html), [NeMo](https://docs.skypilot.co/en/latest/examples/training/nemo.html), [Ray](https://docs.skypilot.co/en/latest/examples/training/ray.html), [Unsloth](https://docs.skypilot.co/en/latest/examples/training/unsloth.html), [Jax/TPU](https://docs.skypilot.co/en/latest/examples/training/tpu.html), [OpenRLHF](https://docs.skypilot.co/en/latest/examples/training/openrlhf.html) |
| Serving | [vLLM](https://docs.skypilot.co/en/latest/examples/serving/vllm.html), [SGLang](https://docs.skypilot.co/en/latest/examples/serving/sglang.html), [Ollama](https://docs.skypilot.co/en/latest/examples/serving/ollama.html) |
| Models | [DeepSeek-R1](https://docs.skypilot.co/en/latest/examples/models/deepseek-r1.html), [Llama 4](https://docs.skypilot.co/en/latest/examples/models/llama-4.html), [Llama 3](https://docs.skypilot.co/en/latest/examples/models/llama-3.html), [CodeLlama](https://docs.skypilot.co/en/latest/examples/models/codellama.html), [Qwen](https://docs.skypilot.co/en/latest/examples/models/qwen.html), [Kimi-K2](https://docs.skypilot.co/en/latest/examples/models/kimi-k2.html), [Kimi-K2-Thinking](https://docs.skypilot.co/en/latest/examples/models/kimi-k2-thinking.html), [Mixtral](https://docs.skypilot.co/en/latest/examples/models/mixtral.html) |
| AI apps | [RAG](https://docs.skypilot.co/en/latest/examples/applications/rag.html), [vector databases](https://docs.skypilot.co/en/latest/examples/applications/vector_database.html) (ChromaDB, CLIP) |
| Common frameworks | [Airflow](https://docs.skypilot.co/en/latest/examples/frameworks/airflow.html), [Jupyter](https://docs.skypilot.co/en/latest/examples/frameworks/jupyter.html), [marimo](https://docs.skypilot.co/en/latest/examples/frameworks/marimo.html)  |

Source files can be found in [`llm/`](https://github.com/skypilot-org/skypilot/tree/master/llm) and [`examples/`](https://github.com/skypilot-org/skypilot/tree/master/examples).

## More information
To learn more, see [SkyPilot Overview](https://docs.skypilot.co/en/latest/overview.html), [SkyPilot docs](https://docs.skypilot.co/en/latest/), and [SkyPilot blog](https://blog.skypilot.co/).

SkyPilot adopters: [Testimonials and Case Studies](https://blog.skypilot.co/case-studies/)

Partners and integrations: [Community Spotlights](https://blog.skypilot.co/community/)

Follow updates:
- [Slack](http://slack.skypilot.co)
- [X / Twitter](https://twitter.com/skypilot_org)
- [LinkedIn](https://www.linkedin.com/company/skypilot-oss/)
- [SkyPilot Blog](https://blog.skypilot.co/) ([Introductory blog post](https://blog.skypilot.co/introducing-skypilot/))

Read the research:
- [SkyPilot paper](https://www.usenix.org/system/files/nsdi23-yang-zongheng.pdf) and [talk](https://www.usenix.org/conference/nsdi23/presentation/yang-zongheng) (NSDI 2023)
- [Sky Computing whitepaper](https://arxiv.org/abs/2205.07147)
- [Sky Computing vision paper](https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s02-stoica.pdf) (HotOS 2021)
- [SkyServe: AI serving across regions and clouds](https://arxiv.org/pdf/2411.01438) (EuroSys 2025)
- [Managed jobs spot instance policy](https://www.usenix.org/conference/nsdi24/presentation/wu-zhanghao)  (NSDI 2024)

SkyPilot was initially started at the [Sky Computing Lab](https://sky.cs.berkeley.edu) at UC Berkeley and has since gained many industry contributors. To read about the project's origin and vision, see [Concept: Sky Computing](https://docs.skypilot.co/en/latest/sky-computing.html).

## Questions and feedback
We are excited to hear your feedback:
* For issues and feature requests, please [open a GitHub issue](https://github.com/skypilot-org/skypilot/issues/new).
* For questions, please use [GitHub Discussions](https://github.com/skypilot-org/skypilot/discussions).

For general discussions, join us on the [SkyPilot Slack](http://slack.skypilot.co).

## Contributing
We welcome all contributions to the project! See [CONTRIBUTING](CONTRIBUTING.md) for how to get involved.
