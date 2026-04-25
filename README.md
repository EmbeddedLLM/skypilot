---

<h2>🍴 EmbeddedLLM Fork</h2>

<p>
  This is a downstream fork of <a href="https://github.com/skypilot-org/skypilot">skypilot-org/skypilot</a> maintained by <a href="https://github.com/EmbeddedLLM">EmbeddedLLM</a>.
  It tracks upstream releases and stacks a small set of custom patches on top.
</p>

<table>
  <tr><td><b>Upstream version</b></td><td><code>0.12.0</code></td></tr>
  <tr><td><b>Branch</b></td><td><code>ellm-0.12.0</code></td></tr>
  <tr><td><b>Image</b></td><td><code>ghcr.io/embeddedllm/skypilot:0.12.0</code></td></tr>
  <tr><td><b>Upstream repo</b></td><td><a href="https://github.com/skypilot-org/skypilot">skypilot-org/skypilot</a></td></tr>
</table>

<h3>🐳 Image Tags</h3>

<table>
  <thead>
    <tr><th>Tag</th><th>Meaning</th></tr>
  </thead>
  <tbody>
    <tr><td><code>0.12.0</code></td><td>Stable, production-ready build based on upstream 0.12.0</td></tr>
    <tr><td><code>0.12.0-dev</code></td><td>Development build off <code>ellm-0.12.0</code> branch, not yet stable</td></tr>
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
        Allows a single Kubernetes API server to schedule workloads across nodes with
        different GPU types (e.g. NVIDIA + AMD). GPU resource key is resolved per-node
        from <code>skypilot.co/gpu</code> node labels instead of a single cluster-wide key.
        <code>get_node_accelerator_count</code> checks both <code>nvidia.com/gpu</code>
        and <code>amd.com/gpu</code> resource keys.
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
  </tbody>
</table>

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
# Resolve any conflicts if upstream changed the same files

# 4. Push new branch
git push origin ellm-{new_version}
```

> After creating the new branch, update this README: bump **Upstream version**, **Branch**, **Image**, and the commit hashes in the patch table. Build and push the new image as `ghcr.io/embeddedllm/skypilot:{new_version}`.

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
