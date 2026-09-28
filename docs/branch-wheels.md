# Publishing branch wheels

1. Open **Actions → Publish Branch Wheel → Run workflow**.
2. Set **Source branch to build** to your branch, e.g. `ellm-0.12.0`, and run it.
3. Open the new GitHub prerelease under **Releases** and download the wheel.
   Install it with `python -m pip install --upgrade /path/to/skypilot-*.whl`.
4. Edit the release on GitHub to add your notes.

The wheel does not include the dashboard. Its filename contains the branch version
and UTC build date, for example:

```text
skypilot-0.12.0+ellm.20260926-py3-none-any.whl
```

`ellm-<version>` branches use the version in the branch name; other branches use
the base version from `sky/__init__.py`. Each version can publish once per UTC day.
