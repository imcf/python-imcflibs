# Development And Contributing Instructions

## Making a new release via Maven

To create a new release, clone the [scijava-scripts][gh_scijava-scripts] repo
(e.g. in `/opt/imagej/`) and run the `release-version.sh` helper:

```bash
BASE_DIR=/opt
mkdir -pv "$BASE_DIR"
cd "$BASE_DIR"
git clone https://github.com/scijava/scijava-scripts
cd -

RELEASE_SCRIPT="$BASE_DIR/scijava-scripts/release-version.sh"

##############     ONLY FOR PRE-RELEASES     ##############
PRE_RELEASE="1.5.0.a17"  # <-- adjust this to the desired version
EXTRA_FLAGS="--skip-branch-check --skip-version-check $PRE_RELEASE"
##############     ONLY FOR PRE-RELEASES     ##############

$RELEASE_SCRIPT --skip-push --skip-gpg --skip-license-update $EXTRA_FLAGS
```

**IMPORTANT 1**: after the release has been built, the corresponding tag needs
to be pushed to github, e.g. like this:

```bash
RELEASE_TAG=$(git tag -l "python-imcflibs-*" | tail -n 1)
git push origin $RELEASE_TAG
```

**IMPORTANT 2**: in case a **pre-releaes** was created, the last commit needs to
be discarded as the *release-script* places a wrong version / snapshot
combination in the `pom.xml`:

```bash
git reset --hard HEAD~1
```

## Build & Deploy with Maven using VS Code

Building and deploying the package can be greatly simplified using "tasks" in
[Visual Studio Code][www_vscode]. By adding the following settings to the
`.vscode/tasks.json` file, you can simply press `Ctrl+Shift+B` in VS Code and
select the *deploy* task for running Maven and have the resulting JAR file being
placed in `/opt/fiji-packaging/Fiji.app/jars/` (adjust to your path as
necessary):

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "verify",
            "type": "shell",
            "command": "mvn -B verify",
            "group": "build"
        },
        {
            "label": "test",
            "type": "shell",
            "command": "mvn -B test",
            "group": "test"
        },
        {
            "label": "deploy",
            "type": "shell",
            "command": "mvn -Dscijava.app.directory=/opt/fiji-packaging/Fiji.app",
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "problemMatcher": []
        }
    ]
}
```

## Linting Python 2.7 with VS Code

For being able to lint the old Python code properly, you'll need to set up an
appropriate *virtualenv* with `pylint` being installed.

Using [`fish`][www_fish] and [virtualfish][www_vf], this can be done as follows:

```fish
vf new -p python2.7 py2-imcf-fiji-packages
pip install pylint
```

Then simply point your VS Code to the newly created venv and run the linting.

[gh_scijava-scripts]: https://github.com/scijava/scijava-scripts
[www_vscode]: https://code.visualstudio.com/
[www_fish]: https://fishshell.com/
[www_vf]: https://virtualfish.readthedocs.io/en/latest/
