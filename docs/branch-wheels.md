# Publishing branch wheels

1. Merge a PR into `ellm-0.12.0`. Each push to this branch automatically runs
   **Actions → Publish Branch Wheel** for the triggering commit.
2. Wait for the workflow to finish in **Actions**.
3. Open the new GitHub release under **Releases**, marked **Latest**, and download the wheel.
   Install it with `python -m pip install --upgrade /path/to/skypilot-*.whl`.
4. Edit the release on GitHub to add your notes.

The wheel does not include the dashboard. Its filename contains the branch version
and UTC build date plus a per-day counter, for example:

```text
skypilot-0.12.0+ellm.20260929.1-py3-none-any.whl
```

The base version comes from the `ellm-<version>` branch name. Each build reserves
a unique `wheel-<version>+ellm.YYYYMMDD.N` tag.

When moving to a new version branch, update the `on.push.branches` filter in
`.github/workflows/publish-branch-wheel.yml` and the branch name in this guide.
