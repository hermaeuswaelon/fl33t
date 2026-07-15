# Phone Document Location Guide

## Where to Look
- **Home directory**: `~/tsh-1.txt` through `~/tsh-5.txt`
- **Project directories**: Check under `projects/` or any subfolder where the files may have been stored.
- **Archive locations**: Some files may be in `~/Desktop/Archive/` or similar locations.

## Common Paths
- `~/tsh-1.txt`
- `~/tsh-2.txt`
- `~/tsh-3.txt`
- `~/tsh-4.txt`
- `~/tsh-5.txt`

## Search Tips
- Use `search_files` with pattern `tsh-*.txt` to locate all relevant files.
- If the file is not found in the home directory, expand the search to subdirectories (e.g., `projects/`, `Desktop/`, `Archive/`).

## Example Search Command
```bash
search_files pattern='tsh-*.txt' target='files' path='~'
```

## Verification
- Confirm the file exists and is readable.
- Check file size and line count to anticipate large-file handling.