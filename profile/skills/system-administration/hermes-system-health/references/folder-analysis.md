# Folder Structure Analysis Reference

## Techniques for Investigating Unknown Directories

### Inode + Device Analysis (detect bind mounts, symlinks, copies)

```bash
# Same inode → same file (hardlink or same dir)
# Same device + different inode → different dir on same filesystem
# Different device → different filesystem/mount

stat --format="%i %d" /path/to/A /path/to/B
```

**Interpretation:**
- Same `%i` (inode) → it's the same directory entry (hardlink)
- Same `%d` (device) + different `%i` → separate directories on same filesystem
- Different `%d` → different mount point or filesystem

### Check for Symlinks

```bash
readlink -f /path/to/item      # Resolve full symlink chain (empty if not a link)
find /path -maxdepth 0 -type l  # Is it a symlink?
```

### Check for Bind Mounts

```bash
mount | grep <name>             # Direct mount check
# Or compare device numbers — same device for different paths suggests bind mount
```

### Directory Contents Comparison

```bash
# Quick structure scan
find /path -maxdepth 2 -type d | sort

# Count subdirectories (31 links = 30 subdirs + . and ..)
stat --format="%h" /path        # Link count = number of entries + 2
```

## Common Hermes Folder Patterns

| Path | Meaning | How to Identify |
|---|---|---|
| `.NOTTHEONETOEDIT` | Backup/snapshot copy of `~/.hermes/` | Contains SOUL.md, active_profile, skills/ |
| `ORGANIZED_FILES/` | Organized archive copies | Often contains dated/suffixed copies |
| `projects/hermes-upgrades/` | Upgrade work in progress | Has UPGRADES.md, INTEGRATION_AUDIT.md |
| `.hermes/profiles/<name>/` | Live Hermes profile | Has full config.yaml, memory/, skills/ |
| `.local/state/hermes/` | Hermes state cache | Smaller, cache-like contents |

## Identifying a Hermes Home Directory

A Hermes `$HERMES_HOME` directory contains at minimum:
- `SOUL.md` — agent identity prompt
- `active_profile` — text file with profile name
- `config.yaml` — configuration
- `skills/` — installed skills
- `memory/` — memory store if used
