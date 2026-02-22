# Dev Notes: Mac Environment Fixes (February 20, 2026)

This project was created by GenAI-Logic in the standard configuration — where the project sits as a child of the GenAI-Logic Manager directory (which owns the `venv`). This project instead lives in iCloud Drive at a path with spaces. Three config files needed fixes.

---

## Fix 1 — `.env`: Remove bash-style variable substitution

**Problem:** The generated `.env` used variable references in an attempt to make `VIRTUAL_ENV`, `PATH`, and `PYTHONPATH` portable:

```dotenv
APILOGICPROJECT_APILOGICSERVERHOME=..
VIRTUAL_ENV=%APILOGICPROJECT_APILOGICSERVERHOME/venv
PATH=%APILOGICPROJECT_APILOGICSERVERHOME/venv/bin:$PATH
PYTHONPATH=%APILOGICPROJECT_APILOGICSERVERHOME/venv/lib/python3.13/site-packages
```

`.env` files are **not** shell scripts. VS Code's Python extension and `python-dotenv` both treat the file as a flat `KEY=VALUE` store — variable references are passed as literal strings, not expanded. On Mac this overrides `PATH` with the garbage literal `%APILOGICPROJECT_APILOGICSERVERHOME/venv/bin:$PATH`, breaking the shell.

**Fix:** Replace with plain absolute values. `APILOGICPROJECT_APILOGICSERVERHOME` is required by the server; `VIRTUAL_ENV`/`PATH`/`PYTHONPATH` are not needed here because VS Code's interpreter selection manages the venv.

```dotenv
# VS Code environment file — read by the Python extension before launch.
# This is NOT a bash script. Variable substitution does not work here.
# Do NOT set VIRTUAL_ENV, PATH, or PYTHONPATH — VS Code manages the venv
# via the Python interpreter selection. For terminal use, activate the venv
# with run.sh (Mac/Linux) or run.ps1 (Windows) before running the server.

APILOGICPROJECT_APILOGICSERVERHOME=/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer
```

**Note for Windows users:** Change `APILOGICPROJECT_APILOGICSERVERHOME` to the Windows path of the Manager. Leave `VIRTUAL_ENV`, `PATH`, and `PYTHONPATH` absent — VS Code's interpreter selection handles those.

---

## Fix 2 — `.vscode/settings.json`: Remove custom terminal profile

**Problem:** `settings.json` defined a custom `"venv"` terminal profile for macOS and Linux that ran:

```jsonc
"args": ["-c", "source ${workspaceFolder}/.vscode/venv_init.sh && exec zsh --no-rcs"]
```

VS Code expands `${workspaceFolder}` before passing the string to zsh's `-c` flag. The expanded path is:

```
/Users/val/Library/Mobile Documents/com~apple~CloudDocs/GenAI-Logic/...
```

The `/bin/zsh -c` invocation does **not** quote the expanded value, so zsh splits the path at the first space (`Mobile Documents`). The `source` command receives `/Users/val/Library/Mobile` as a filename, fails immediately, and the terminal window never opens.

**Fix:** Remove the `"terminal.integrated.profiles.osx"`, `"terminal.integrated.profiles.linux"`, `"terminal.integrated.defaultProfile.osx"`, and `"terminal.integrated.defaultProfile.linux"` entries entirely. The `"python.terminal.activateEnvironment": true` setting (already present) tells the Python extension to activate the selected venv in every new terminal — the custom profile was redundant.

**Also updated:** `"python.defaultInterpreterPath"` from the relative path:
```
"${workspaceFolder}/../venv/bin/python"
```
to the absolute path of the Manager's venv:
```
"/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/venv/bin/python"
```
The relative path assumed this project lives one level below the Manager. It does not.

---

## Fix 3 — `.vscode/launch.json`: Pin interpreter in the ApiLogicServer launch config

**Problem:** Even after updating `settings.json`, VS Code's debugpy launch uses the interpreter from the workspace interpreter picker, which is cached separately from `python.defaultInterpreterPath`. If the picker still shows the wrong Python, F5 fails at `import flask_sqlalchemy` on line 42 of `api_logic_server_run.py` because the system Python has none of the project packages.

**Fix:** Add the `"python"` key directly to the `ApiLogicServer` launch configuration:

```jsonc
{
    "name": "ApiLogicServer",
    "type": "debugpy",
    "python": "/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/ApiLogicServer/venv/bin/python",
    "cwd": "${workspaceFolder}",
    ...
}
```

The `"python"` key in a debugpy launch entry overrides the workspace interpreter selection entirely. F5 uses the correct venv regardless of what the interpreter picker shows.

---

## Summary

| File | Change | Root cause |
|------|--------|------------|
| `.env` | Removed bash variable substitution; set absolute path for `APILOGICPROJECT_APILOGICSERVERHOME` | `.env` is not a shell script; variable references are literal strings |
| `.vscode/settings.json` | Removed custom terminal profile; updated interpreter path to absolute | Space in workspace path broke `source` inside zsh `-c` string |
| `.vscode/launch.json` | Added `"python"` key pinning the venv interpreter | Interpreter picker cached wrong Python; `"python"` key in launch config overrides it |

---

## Portability note

Fixes 2 and 3 embed an absolute Mac path. For a Windows colleague sharing this project:

- Set `APILOGICPROJECT_APILOGICSERVERHOME` in `.env` to the Windows Manager path
- Update `"python.defaultInterpreterPath"` in `settings.json` to the Windows venv path (e.g., `C:\...\venv\Scripts\python.exe`)
- Update `"python"` in `launch.json` to the same Windows path

If the project were restructured to sit one level below the Manager (the standard GenAI-Logic layout), all three would use `${workspaceFolder}/../venv/...` and would work on any OS without path edits.
