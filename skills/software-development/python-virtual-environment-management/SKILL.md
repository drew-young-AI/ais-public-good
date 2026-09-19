---
name: python-virtual-environment-management
type: skill
category: software-development
description: "Manage Python venvs: locate, pip freeze, requirements."
version: 1.0.0
trigger: When you need to work with Python virtual environments for dependency management, environment reproduction, or package installation.
---

# Python Virtual Environment Management

Manage Python virtual environments, including creating venvs, installing dependencies, generating requirements.txt, and handling path encoding issues.

## Why This Skill
Python virtual environments are essential for isolating project dependencies and ensuring reproducible builds. This skill provides reliable workflows for creating, managing, and exporting environment specifications, with special attention to handling filesystem paths that may have encoding or display issues.

## Steps

### 1. Locate the Virtual Environment
When working with a venv path that may have encoding issues (displaying as replacement characters like ������������ ���������� ���������� ��������):
- Search the filesystem for directories matching the expected pattern
- Look for directories containing both "venv" and the project name in their path
- Verify the location by checking for expected venv structure (bin/pip, pyvenv.cfg, etc.)

```bash
# Example search strategy (adapt paths as needed)
find /base/search/path -type d -name "venv" | grep project_identifier
```

### 2. Verify the Pip Executable
Once you've located the venv directory:
- Check for pip at `<venv_path>/bin/pip`
- If not found, try `<venv_path>/bin/pip3`
- Confirm the executable exists and is readable

### 3. Generate Requirements.txt
To create a requirements.txt file from an existing venv:
- Run `<venv_path>/bin/pip freeze` to get the package list
- Capture the output and write it to `<project_path>/requirements.txt`
- Verify the file was created successfully

```bash
# Example command
~/Project/project_name/venv/bin/pip freeze > ~/Project/project_name/requirements.txt
```

### 4. Handle Path Encoding Issues
When paths display with encoding issues (replacement characters):
- Do not rely on the displayed/path-as-shown value
- Use filesystem search to locate the actual directory
- Verify locations by checking for expected files rather than trusting path strings
- Consider normalizing paths early in your workflow if encoding issues persist

## Pitfalls to Avoid
- Assuming paths display correctly in all contexts (especially with non-ASCII characters)
- Using hardcoded paths without verification
- Forgetting to activate the venv when running pip directly (use the full path to pip instead)
- Not verifying that pip freeze output was successfully written to requirements.txt
- Overlooking that different projects may use different Python versions or venv locations

## Verification
After generating requirements.txt:
- Confirm the file exists at the expected location
- Check that it contains package specifications (not empty)
- Optionally, compare against known expected packages for the project
- Ensure no error messages appeared during pip freeze execution

## Related Techniques
- To create a new venv: `python -m venv <path>/venv`
- To install from requirements.txt: `<venv_path>/bin/pip install -r requirements.txt`
- To list installed packages: `<venv_path>/bin/pip list`