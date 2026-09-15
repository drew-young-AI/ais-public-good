# Path Encoding Workaround for Non-ASCII Directory Names

## Issue Encountered
When working with directories containing non-ASCII characters (specifically Chinese characters like �� 鉛防護衣), the filesystem paths may display incorrectly in tool outputs, showing replacement characters (��) instead of the actual characters. This can cause commands using these displayed paths to fail.

## Resolution Strategy
1. **Do not rely on displayed paths**: When paths show encoding issues, ignore the visual representation
2. **Use filesystem search**: Locate directories using search patterns rather than trusting displayed paths
3. **Verify by structure**: Confirm locations by checking for expected files/directories (e.g., venv/bin/pip)
4. **Normalize early**: Consider normalizing paths at the start of your workflow if possible

## Example Workflow from Session
1. User requested: create requirements.txt in `~/Project/��鉛防護衣/dicom_annotator/venv`
2. Displayed path showed: `~/Project/������鉛防護衣/dicom_annotator/venv` (with replacement characters)
3. Direct commands using displayed path failed: "No such file or directory"
4. Solution: 
   - Used `find` to locate actual venv directory: `find ~/Project -name "venv" -type d`
   - Filtered for the specific project: `grep dicom_annotator`
   - Verified pip executable existed at the found location
   - Executed pip freeze using the verified path
   - Wrote output to requirements.txt

## Commands That Worked
```bash
# Find the actual venv directory despite display issues
find ~/Project -name "venv" -type d | grep dicom_annotator

# Verify the pip executable
ls -la ~/Project/��鉛防護衣/dicom_annotator/venv/bin/pip

# Generate requirements.txt
~/Project/��鉛防護衣/dicom_annotator/venv/bin/pip freeze > ~/Project/��鉛防護衣/dicom_annotator/requirements.txt
```

## Prevention
- When possible, avoid creating directories with non-ASCII names in automation workflows
- If working with existing non-ASCII paths, implement path verification steps
- Consider creating aliases or symlinks with ASCII-only names for automation access