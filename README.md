<h2>🍴 EmbeddedLLM Fork</h2>

<p>
  This is a downstream fork of <a href="https://github.com/skypilot-org/skypilot">skypilot-org/skypilot</a> maintained by <a href="https://github.com/EmbeddedLLM">EmbeddedLLM</a>.
  It tracks upstream releases and stacks a small set of custom patches on top.
</p>

<table>
  <tr><td><b>Upstream version</b></td><td><code>0.14.3</code></td></tr>
  <tr><td><b>Branch</b></td><td><code>ellm-0.14.3</code></td></tr>
  <tr><td><b>Image</b></td><td><code>ghcr.io/embeddedllm/skypilot:v0.14.3</code></td></tr>
  <tr><td><b>Upstream repo</b></td><td><a href="https://github.com/skypilot-org/skypilot">skypilot-org/skypilot</a></td></tr>
  <tr><td><b>Previous branch</b></td><td><code>ellm-0.12.0</code> (kept as a rollback point)</td></tr>
</table>

<h3>📦 Branch Wheels</h3>

Every push to `ellm-0.14.3` runs **Actions → Publish Branch Wheel**, which
builds a wheel for the pushed commit and publishes it as a GitHub release
marked **Latest**. Add release notes manually on GitHub. See the
[publishing guide](docs/branch-wheels.md).

<h3>🐳 Image Tags</h3>

<table>
  <thead>
    <tr><th>Tag</th><th>Meaning</th></tr>
  </thead>
  <tbody>
    <tr><td><code>v0.14.3</code></td><td>Stable, production-ready build based on upstream v0.14.3</td></tr>
    <tr><td><code>v0.14.3-dev</code></td><td>Development build off <code>ellm-0.14.3</code> branch, not yet stable</td></tr>
  </tbody>
</table>

<h3>🔧 Custom Patches</h3>

The patches below were ported from `ellm-0.12.0` onto upstream `v0.14.3`.
Multi-commit topics were squashed into one commit each; every commit message
lists the original `ellm-0.12.0` hashes and how the port differs from them.

<table>
  <thead>
    <tr>
      <th>Patch</th>
      <th>Commit</th>
      <th>Ported from</th>
      <th>Files Changed</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>[Kubernetes] Fix podip endpoint in HA mode</b></td>
      <td><code>47fbd4f</code><br>(format fix <code>04d12b1</code>)</td>
      <td><code>f3b4561</code></td>
      <td><code>sky/provision/kubernetes/network.py</code></td>
      <td>
        In HA mode the serve controller runs as a Deployment, so its pod has a
        random name suffix and the expected <code>{cluster}-head</code> pod never
        exists; the endpoint came back as <code>http://None</code>.
        <code>_query_ports_for_podip</code> now finds the head pod by label
        selector, which works in both HA and non-HA modes.
      </td>
    </tr>
    <tr>
      <td><b>[CLI] Allow Click 8.2.1 and newer 8.x releases</b></td>
      <td><code>5408b11</code></td>
      <td><code>44d09ea</code></td>
      <td><code>sky/setup_files/dependencies.py</code></td>
      <td>
        Replaces <code>click &gt;= 7.0, &lt; 8.2.0</code> with
        <code>click &gt;= 7.0, != 8.2.0, &lt; 9.0.0</code>, keeping the exclusion
        for the 8.2.0 flag parsing bug.<br>
        <em>Note: upstream 0.14.3 pins <code>click&lt;8.3.0</code> on the cluster
        side because Click 8.3 breaks the Ray CLI; this client-side range is
        wider than that.</em>
      </td>
    </tr>
    <tr>
      <td><b>[Serve] Raise per-controller service capacity for k8s workloads</b></td>
      <td><code>cffc582</code></td>
      <td><code>c6f8f23</code></td>
      <td>
        <code>sky/utils/controller_utils.py</code><br>
        <code>tests/unit_tests/test_sky/server/test_config.py</code>
      </td>
      <td>
        Upstream reserves about 2.1 GB per service on the serve controller, which
        caps an 8 GB controller at 2 services. Lowers
        <code>LAUNCHES_PER_SERVICE</code> from 4 to 2 and sizes the controller's
        local API server workers at 0.25 GB
        (<code>SERVE_LOCAL_API_LONG_WORKER_MEM_GB</code>) instead of 0.4 GB,
        without touching the central API server's worker sizing. The lower worker
        memory also applies to pools, which raises pool capacity as well.
      </td>
    </tr>
    <tr>
      <td><b>Pin uv pip to runtime venv's Python via <code>--python</code> flag</b></td>
      <td><code>bd1fec4</code></td>
      <td><code>78fe751</code></td>
      <td>
        <code>sky/skylet/constants.py</code><br>
        <code>sky/templates/kubernetes-ray.yml.j2</code><br>
        <code>sky/adaptors/oci.py</code><br>
        <code>tests/unit_tests/test_sky/test_ray_version_per_cluster.py</code>
      </td>
      <td>
        uv can ignore <code>VIRTUAL_ENV</code> on images that ship a Python at a
        non-standard prefix (e.g. ROCm images with <code>/opt/python</code> in
        <code>PATH</code>), installing into the wrong interpreter or failing to
        find a Ray wheel. Every <code>uv pip install/uninstall/list</code> and
        <code>uv run</code> that targets the SkyPilot runtime venv now passes
        <code>--python &lt;venv&gt;/bin/python</code>.
      </td>
    </tr>
    <tr>
      <td><b>[Kubernetes] Support mixed NVIDIA + AMD GPU clusters</b></td>
      <td><code>9e4b044</code></td>
      <td>
        <code>493fb1f</code>, <code>9cd2668</code>, <code>e9581a9</code>,
        <code>f65b71f</code>, <code>57c8ba2</code>, <code>37a0b54</code>,
        <code>b35db4a</code>, <code>d05ad3c</code>
      </td>
      <td>
        <code>sky/provision/kubernetes/utils.py</code><br>
        <code>sky/provision/kubernetes/instance.py</code><br>
        <code>sky/catalog/kubernetes_catalog.py</code><br>
        <code>sky/clouds/kubernetes.py</code><br>
        <code>sky/utils/gpu_names.py</code><br>
        <code>sky/client/cli/command.py</code><br>
        <code>scripts/test_amd_labels_fedora.py</code><br>
        <code>scripts/validate_gpu_resource_key.py</code>
      </td>
      <td>
        Upstream picks one GPU resource key and one label formatter per cluster.
        This patch makes both per node and per pod, so NVIDIA and AMD nodes work
        in the same cluster with no extra configuration:
        <ul>
          <li><b>AMD detection</b>: <code>AMDGPULabelFormatter</code> reads the
            <a href="https://github.com/ROCm/k8s-device-plugin">AMD device plugin</a>
            label <code>amd.com/gpu.product-name = &lt;NAME&gt;</code>, so
            <code>sky gpus label</code> is not needed on AMD nodes. Adds 33 AMD
            canonical GPU names.</li>
          <li><b>Per-node detection</b>: <code>sky gpus list</code>, per-node
            status, label lookup and CPU-only node avoidance try every registered
            formatter on each node.</li>
          <li><b>Resource key</b>: derived from the matched label key
            (<code>amd.com/*</code> → <code>amd.com/gpu</code>, any other GPU
            label → <code>nvidia.com/gpu</code>) instead of the cluster default.</li>
          <li><b>Pod handling</b>: GPU tolerations, scheduling error messages and
            status GPU counts read the key from the pod's own limits or
            requests.</li>
          <li><b>Node affinity</b>: label values are coerced to strings.</li>
        </ul>
        Each node must expose exactly one GPU type; the AMD device plugin's
        suffix label format (multi-GPU-type nodes) is not supported.<br>
        <em>Limitations: <code>CUSTOM_GPU_RESOURCE_KEY</code> is ignored in pod
        GPU detection, unlabeled-node detection and status GPU counts.</em>
      </td>
    </tr>
    <tr>
      <td><b>[Kubernetes] Add Intel GPU discovery and resource selection</b></td>
      <td><code>183183b</code></td>
      <td>
        <code>5420c46</code>, <code>bb8cbc9</code>, <code>0e986b2</code>,
        <code>f579438</code>
      </td>
      <td>
        <code>sky/provision/kubernetes/utils.py</code><br>
        <code>sky/clouds/kubernetes.py</code><br>
        <code>docs/source/reference/kubernetes/intel-gpu.rst</code><br>
        <code>docs/source/compute/gpus.rst</code>
      </td>
      <td>
        Adds <code>IntelGPULabelFormatter</code> for the NFD product label
        <code>gpu.intel.com/product</code> (e.g. <code>Arc_Pro_B60</code> →
        <code>Intel-Arc-Pro-B60</code>) and the <code>gpu.intel.com/xe</code>
        resource key. Pods matched by the Intel label request that key. Only the
        xe driver is supported. See the Intel GPU guide under
        <code>docs/source/reference/kubernetes/</code>.
      </td>
    </tr>
    <tr>
      <td><b>[Kubernetes] Accept PEP 585 <code>dict[K, V]</code> type strings in pod_config validator</b></td>
      <td><code>3ef5c8a</code></td>
      <td><code>827ff42</code></td>
      <td><code>sky/provision/kubernetes/utils.py</code></td>
      <td>
        <code>kubernetes</code> client 36+ declares map fields as
        <code>dict[str, str]</code> instead of <code>dict(str, str)</code>, which
        made the pod_config validator fail with <code>ModuleNotFoundError</code>.
        The validator accepts both forms. Upstream 0.14.3 pins
        <code>kubernetes&lt;36</code>, so this is a safety net for environments
        that have a newer client installed anyway.
      </td>
    </tr>
    <tr>
      <td><b>[Kubernetes] Sync files with tar over kubectl exec; fix exec stream hangs</b></td>
      <td><code>0e5ec26</code><br>(debug opt-in <code>06ac042</code>)</td>
      <td>
        <code>0e764fe</code>, <code>d5731f4</code>, <code>e3237a7</code>,
        <code>502df1c</code>, <code>4f1c887</code>, <code>175e866</code>
      </td>
      <td>
        <code>sky/utils/command_runner.py</code><br>
        <code>sky/utils/kubernetes/rsync_helper.sh</code><br>
        <code>sky/templates/kubernetes-ray.yml.j2</code><br>
        <code>tests/unit_tests/test_sky/utils/test_command_runner.py</code>
      </td>
      <td>
        On Ubuntu 26 / kernel 6.8+ hosts, rsync 3.4.x over
        <code>kubectl exec</code> deadlocks at session teardown and leaves the
        SkyServe controller stuck at <em>Preparing SkyPilot runtime</em>.
        <ul>
          <li><code>KubernetesCommandRunner.rsync</code> streams
            <code>tar -c | kubectl exec -i -- tar -x</code> instead (or the
            reverse for downloads). Ignore files go through
            <code>--exclude-ignore</code>; a file source is renamed to the target
            path with <code>tar --transform</code>. The upstream
            <code>timeout</code> argument is honoured.</li>
          <li>SPDY transport is forced for kubectl exec
            (<code>KUBECTL_REMOTE_COMMAND_WEBSOCKETS=false</code>).</li>
          <li><code>rsync_helper.sh</code> waits for rsync and runs the transfer
            in two separate exec calls.</li>
          <li><code>setup_commands</code> uses <code>tail -f --pid=$$</code> so an
            orphaned tail cannot hold the exec stream open after setup
            finishes.</li>
        </ul>
        <em>Notes: set <code>SKYPILOT_DEBUG_TAR_RSYNC=1</code> on the API
        server to log each sync's tar pipeline with the
        <code>[TAR-RSYNC-DEBUG]</code> tag (off by default; it was always on
        in <code>ellm-0.12.0</code>). The tar path may not honour
        <code>!</code> negation patterns in <code>.skyignore</code>, which
        upstream supports in its rsync path.</em>
      </td>
    </tr>
    <tr>
      <td><b>[Serve] Keep reused replicas routable on count-only updates</b></td>
      <td><code>c322f1b</code></td>
      <td><code>7f89638</code>, <code>6444f96</code></td>
      <td><code>sky/serve/replica_managers.py</code></td>
      <td>
        A <code>sky serve update</code> that changes only the
        <code>service:</code> section (e.g. <code>replicas: 1 → 2</code>) reuses
        running replicas by relabelling them to the new version, but
        <code>active_versions</code> was only refreshed by the next prober pass,
        so the load balancer returned <code>503 No ready replicas</code> for up
        to one sync interval. <code>update_version</code> now refreshes
        <code>active_versions</code> right after the relabel. The prober also
        re-reads the stored version before writing its snapshot back, so a
        relabel that lands mid-probe is not reverted.
      </td>
    </tr>
    <tr>
      <td><b>[CI] Publish branch wheels to GitHub Releases</b></td>
      <td><code>d24209c</code></td>
      <td>
        <code>b43391c</code>, <code>64919e5</code>, <code>12bd32c</code>,
        <code>6ef650c</code>
      </td>
      <td>
        <code>.github/workflows/publish-branch-wheel.yml</code><br>
        <code>docs/branch-wheels.md</code>
      </td>
      <td>
        Each push to <code>ellm-0.14.3</code> reserves a unique
        <code>wheel-0.14.3+ellm.YYYYMMDD.N</code> tag, builds the wheel and
        publishes it as a regular release marked Latest. The wheel does not
        include the dashboard.
      </td>
    </tr>
  </tbody>
</table>

**Not carried over from `ellm-0.12.0`**

| `ellm-0.12.0` commit | Why it is not on this branch |
|---|---|
| `69b0a69`, `d9be189` (`kubernetes` client bounds) | Upstream 0.14.3 already pins `kubernetes>=20.0.0,!=32.0.0,<36.0.0`. |
| `62d4dc6` (pin temporary bootstrap SkyPilot to 0.14.2) | The pin kept PyPI 0.14.3, whose Ray patches target Ray 2.56.1, away from the old branch's Ray 2.9.3. This branch is 0.14.3 and uses Ray 2.56.1, so the bootstrap install is left unpinned as in upstream. |
| `ed93406` (keep npm bundled with Node 20) | Upstream 0.14.3 no longer runs `npm install -g npm@latest` in the Dockerfile. |
| `a98a541` (remove FastAPI `prefix` argument) | Upstream 0.14.3 already creates the app without it. |
| `32e4e61` (forensic `set -x` trace in `setup_commands`) | Debug-only tracing; the `tail --pid` fix it helped find is ported. |
| `82fc2fb` (removes `test_serve_replica_versions.py`) | The test was added and removed on `ellm-0.12.0`; neither commit is needed. |
| `acf0dbc`, `4f1df76` (conda/venv self-heal and its revert) | Net zero. |

<h3>🛠️ Development Workflow</h3>

Never commit directly to `ellm-{version}`. Create a feature branch off it, then open a PR back into it.

```bash
# 1. Branch off the active version branch
git checkout ellm-0.14.3
git checkout -b feat/my-feature

# 2. Make changes, commit
git add <files>
git commit -m "[Area] Description"
git push origin feat/my-feature

# 3. Open a PR → target ellm-0.14.3 (not master)
gh pr create --base ellm-0.14.3 --title "..." --body "..."
```

Build and push a dev image to test before merging:
```bash
docker buildx build --push --platform linux/amd64 \
  -t ghcr.io/embeddedllm/skypilot:v0.14.3-dev \
  -f Dockerfile .
```

Once the PR is merged and validated, promote to stable:
```bash
docker tag ghcr.io/embeddedllm/skypilot:v0.14.3-dev ghcr.io/embeddedllm/skypilot:v0.14.3
docker push ghcr.io/embeddedllm/skypilot:v0.14.3
```

**Deploying with Helm**

The Helm chart is pinned to the same upstream version. Always specify `--version` explicitly:
```bash
helm upgrade --install $RELEASE_NAME skypilot/skypilot \
  --version 0.14.3 \
  --namespace $NAMESPACE \
  --create-namespace \
  --set apiService.image=ghcr.io/embeddedllm/skypilot:v0.14.3 \
  --set ingress.authCredentials=$AUTH_STRING
```

> When moving to a new upstream version (e.g. `v0.15.0`), update **both** `--version` and `--set apiService.image` together. The Helm chart version must always match the image version.

<h3>⬆️ Updating to a New Upstream Version</h3>

Each upstream version gets its own branch (`ellm-0.12.0`, `ellm-0.14.3`, ...). Old branches are kept as rollback points.

```bash
# 1. Fetch the upstream release tag (one-time: add the remote)
git remote add upstream https://github.com/skypilot-org/skypilot
git fetch upstream refs/tags/v{new_version}:refs/tags/v{new_version}

# 2. Create the new branch from the release tag
git checkout -b ellm-{new_version} v{new_version}

# 3. Cherry-pick the custom patches, in order (hashes from the table above)
git cherry-pick 47fbd4f  # Fix podip endpoint in HA mode
git cherry-pick 04d12b1  # Format the HA pod IP lookup
git cherry-pick 5408b11  # Allow Click 8.2.1+ while excluding 8.2.0 and 9.x
git cherry-pick cffc582  # Raise per-controller service capacity for k8s
git cherry-pick bd1fec4  # Pin uv pip to runtime venv via --python
git cherry-pick 9e4b044  # Mixed NVIDIA + AMD GPU clusters
git cherry-pick 183183b  # Intel GPU discovery (depends on 9e4b044)
git cherry-pick 3ef5c8a  # Accept PEP 585 dict[K, V] in pod_config validator
git cherry-pick 0e5ec26  # tar over kubectl exec; exec stream hang fixes
git cherry-pick 06ac042  # Make tar-rsync debug logging opt-in (depends on 0e5ec26)
git cherry-pick c322f1b  # Keep reused serve replicas routable
git cherry-pick d24209c  # Publish branch wheels
# Resolve any conflicts if upstream changed the same files, and check first
# whether upstream has absorbed a patch (see "Not carried over" above).

# 4. Push new branch
git push origin ellm-{new_version}
```

> After creating the new branch, update this README (**Upstream version**, **Branch**, **Image**, and the commit hashes in the patch table), the branch filter in `.github/workflows/publish-branch-wheel.yml` and the branch name in `docs/branch-wheels.md`. Build and push the new image as `ghcr.io/embeddedllm/skypilot:v{new_version}`.

---


<p align="center">
  <a href="https://skypilot.ai/#gh-light-mode-only">
    <img alt="SkyPilot" src="https://raw.githubusercontent.com/skypilot-org/skypilot/master/docs/source/images/skypilot-wide-light-1k.png" width=55%>
  </a>
  <a href="https://skypilot.ai/#gh-dark-mode-only">
    <img alt="SkyPilot" src="https://raw.githubusercontent.com/skypilot-org/skypilot/master/docs/source/images/skypilot-wide-dark-1k.png" width=55%>
  </a>
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
    Manage all your AI compute
</h3>

SkyPilot is a system to run, manage, and scale AI workloads on any AI infrastructure.

SkyPilot gives **AI teams** a simple interface to run jobs on any infra.
**Infra teams** get a unified control plane to manage any AI compute — with advanced scheduling, scaling, and orchestration.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./docs/source/images/skypilot-abstractions-long-2-dark.png">
  <img src="./docs/source/images/skypilot-abstractions-long-2.png" alt="SkyPilot Abstractions">
</picture>

-----

:fire: *News* :fire:
- [Oct 2026] **SkyPilot's scheduler bumps NVL72 training throughput by 14%**: [**blog**](https://skypilot.ai/blog/grace-blackwell-needs-a-new-scheduler)
- [Oct 2026] **Post-training a 4B model with RL to fly the Tesla Roadster 21% better than GPT-6 Astra**: [**blog**](https://skypilot.ai/blog/flying-roadster-rl)
- [Sep 2026] **RL is Everything, Everywhere, All at Once**: [**blog**](https://skypilot.ai/blog/rl-everything)
- [Sep 2026] **SkyPilot Agent Sessions**: Mission Control for Coding Agents, on Your Infrastructure: [**blog**](https://skypilot.ai/blog/agent-sessions)
- [Jul 2026] **Serving Kimi K3 on your own GPUs with SkyPilot**: [**blog**](https://skypilot.ai/blog/kimi-k3)
- [Jul 2026] **Run AI workloads on any cloud, store on Hugging Face**, no egress fees to worry about: [**Hugging Face blog**](https://huggingface.co/blog/skypilot-hf-storage)
- [Jun 2026] **SkyPilot Endpoints**: production-ready inference on every cluster you own: [**blog**](https://skypilot.ai/blog/skypilot-endpoints)
- [Jun 2026] **Announcing SkyPilot Sandboxes**: run untrusted, LLM-generated code on the Kubernetes clusters you already own. [**Learn more**](https://skypilot.ai/blog/sandboxes), [**join early access**](https://forms.gle/o4keAryXsVazNjyGA)
- [May 2026] **How Multiverse doubled their GPU utilization with SkyPilot**: [**case study**](https://multiversecomputing.com/papers/2x-gpu-utilization-same-hardware-discover-our-efficiency-playbook)
- [Apr 2026] Introducing **GPU Compass**: One dashboard to browse, compare pricing, and launch across every GPU cloud. Try it at [**gpus.skypilot.co**](https://gpus.skypilot.co).
- [Apr 2026] **Research-Driven Agents**: Agents read arxiv papers before coding, landed 5 llama.cpp kernel fusions and +15% faster flash attention in ~3 hours for ~$29: [**blog**](https://skypilot.ai/blog/research-driven-agents), [**HackerNews**](https://news.ycombinator.com/item?id=47706141)
- [Mar 2026] **Scaling Karpathy's Autoresearch**: Autoresearch runs 1 experiment at a time. We gave it 16 GPUs and let it run in parallel: [**blog**](https://skypilot.ai/blog/scaling-autoresearch), [**HackerNews**](https://news.ycombinator.com/item?id=47442435)
- [Mar 2026] **How H Company Unlocked Online RL and Unified their AI Platform**: [**case study**](https://hcompany.ai/unlocking-online-rl-skypilot)

## Overview

SkyPilot **is easy to use for AI users**:
- Quickly spin up compute on your own infra
- Environment and job as code — simple and portable
- Easy job management: queue, run, and auto-recover many jobs

SkyPilot **makes Kubernetes easy for AI & Infra teams**:

- Slurm-like ease of use, cloud-native robustness
- Local dev experience on K8s: SSH into pods, sync code, or connect IDE
- Turbocharge your clusters: gang scheduling, multi-cluster, and scaling

SkyPilot **unifies multiple clusters, clouds, and hardware**:
- One interface to use reserved GPUs, Kubernetes clusters, Slurm clusters, or 20+ clouds
- [Flexible provisioning](https://docs.skypilot.co/en/latest/examples/auto-failover.html) of GPUs, TPUs, CPUs, with smart failover
- [Team deployment](https://docs.skypilot.co/en/latest/reference/api-server/api-server.html) and resource sharing

SkyPilot **maximizes GPU fleet utilization**:
* Autostop: automatic cleanup of idle resources
* Binpacking: workload binpacking on shared clusters
* Intelligent scheduler: automatically schedule on the most available infra

SkyPilot supports your existing GPU, TPU, and CPU workloads, with no code changes.

Install with uv ([also supported](https://docs.skypilot.co/en/latest/getting-started/installation.html): pip, nightly, from source)
```bash
# Choose your clouds:
uv pip install "skypilot[kubernetes,aws,gcp,azure,oci,nebius,lambda,runpod,fluidstack,paperspace,cudo,ibm,scp,seeweb,shadeform,verda]"
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

[Install SkyPilot](https://docs.skypilot.co/en/latest/getting-started/installation.html) in 1 minute. Then, launch your first cluster in 2 minutes in [Quickstart](https://docs.skypilot.co/en/latest/getting-started/quickstart.html).

SkyPilot is BYOC: Everything is launched within your cloud accounts, VPCs, and clusters.

## Benefits of SkyPilot on Kubernetes

SkyPilot makes Kubernetes AI-native.

It turbocharges your existing Kubernetes clusters by **accelerating AI/ML velocity**:

- AI-friendly interface to launch jobs and deployments
- Much simplified interactive dev for K8s (SSH / sync code / connect IDE to pods)

...and **optimizing GPU scheduling, utilization, and scaling**:

- Advanced scheduling: Gang scheduling, multi-node jobs, and queueing
- Multi-cluster support: Bring all your clusters under one control plane
- Multi-cloud support: One consistent interface to manage many providers

See [SkyPilot vs Vanilla Kubernetes](https://docs.skypilot.co/en/latest/reference/kubernetes/skypilot-and-vanilla-k8s.html) and this [blog post](https://skypilot.ai/blog/ai-on-kubernetes) for more details.

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

## Learn more
To learn more, see [SkyPilot Overview](https://docs.skypilot.co/en/latest/overview.html), [SkyPilot docs](https://docs.skypilot.co/en/latest/), and [SkyPilot blog](https://skypilot.ai/blog).

SkyPilot adopters: [Testimonials and Case Studies](https://skypilot.ai/case-studies)

Follow updates:
- [Slack](http://slack.skypilot.co)
- [X](https://twitter.com/skypilot_org)
- [LinkedIn](https://www.linkedin.com/company/skypilot-oss/)
- [YouTube](https://www.youtube.com/@skypilot-org)
- [SkyPilot Blog](https://skypilot.ai/blog)

## Questions and feedback
We are excited to hear your feedback:
* For issues and feature requests, please [open a GitHub issue](https://github.com/skypilot-org/skypilot/issues/new).
* For questions, please use [GitHub Discussions](https://github.com/skypilot-org/skypilot/discussions).

For general discussions, join us on the [SkyPilot Slack](http://slack.skypilot.co).

## Contributing
We welcome all contributions to the project! See [CONTRIBUTING](CONTRIBUTING.md) for how to get involved.

<img referrerpolicy="no-referrer-when-downgrade" src="https://static.scarf.sh/a.png?x-pxid=76c302d0-bd8d-4233-b7df-237d353375cd" />
