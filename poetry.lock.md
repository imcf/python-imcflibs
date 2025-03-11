## Updating `poetry.lock` 🎭🔐

Every time dependencies in `pyproject.toml` have been modified (e.g. when
pulling in a newer version of the [`imcf-fiji-mocks`][1] package), [Poetry's
lockfile][2] has to be updated (otherwise the build workflow will start to
fail, complaining about the outdated file).

To do so, it's not sufficient to simply call `poetry lock --no-update` but
rather the Poetry wrapper script has to be used like this:

```bash
scripts/run-poetry.sh lock --no-update
```

[1]: https://pypi.org/project/imcf-fiji-mocks
[2]: https://python-poetry.org/docs/basic-usage/#committing-your-poetrylock-file-to-version-control
