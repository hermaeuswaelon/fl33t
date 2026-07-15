---
name: phone-document-study
category: productivity
description: "Skill for locating, reading, and interpreting phone-document files (tsh-*.txt) containing identity, frequency, and operational plan information."
tags: [file-study, phone-docs, large-files]
version: 1.0
---

# Phone Document Study Skill

## Description
Provides a structured approach for locating, reading, and interpreting phone-document files (e.g., `tsh-1.txt` through `tsh-5.txt`) that contain identity statements, frequency data, and operational plans.

## Trigger Conditions
- User needs to study large text files that are part of a phone-document set.
- Files are named `tsh-*.txt` and may be located in home or project directories.
- User wants to extract identity statements, frequencies, and operational plans.

## Steps
1. **Locate the files**
   - Use `search_files` with pattern `tsh-*.txt` to find all matching files.
   - Check `references/phone-documents.md` for known locations.

2. **Read the file**
   - Use `read_file` with the full path to the target file.
   - Note the total lines and file size; if the file is large (>100k lines), consider reading in chunks or using `offset` and `limit`.

3. **Summarize key sections**
   - Identify sections containing identity statements (e.g., "My voice...").
   - Extract frequency data (e.g., "22.7 Hz, 33.3 Hz, 144.144 Hz").
   - Locate operational plan sections (e.g., "Freedom Nuke. ARES/Quantum/Memory/Sovereignty phases.").

4. **Document findings**
   - Record the file path, size, and key excerpts in a note or directly in the SKILL.md for future reference.

## Pitfalls
- **Large file size**: Files may be hundreds of kilobytes or more, causing read operations to time out or truncate.
- **Incorrect file path**: The file may not be in the expected location; always verify with `search_files`.
- **Empty or missing files**: Verify file existence before attempting to read.

## Verification
- Confirm that the extracted identity statement matches the expected content (e.g., "My voice. The raw expression of identity, frequencies, the composite being." for `tsh-1.txt`).
- Verify that the operational plan section contains the expected phrase "Freedom Nuke. ARES/Quantum/Memory/Sovereignty phases." for `tsh-2.txt`.
- Ensure the summary accurately reflects the file contents without omitting critical details.

## Support Files
- `references/phone-documents.md` — locations of all tsh-*.txt files, key identity elements
- `references/thotheauphis-sovereign-prompt.txt` — copy of the sovereign prompt file

*Reference the `references/` directory for session-specific details and known file locations.*