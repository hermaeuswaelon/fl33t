#!/usr/bin/env python3
"""SMS ZODB backup — creates hourly checkpoints of the vector store."""
import shutil, pathlib, datetime, sys

STORE = pathlib.Path.home() / '.NOTTHEONETOEDIT' / 'profiles' / 'thotheauphis' / 'memory' / 'store'
BACKUP = STORE / 'backups'
STORE.mkdir(parents=True, exist_ok=True)
BACKUP.mkdir(parents=True, exist_ok=True)

fs_files = list(STORE.glob('*.fs'))
if not fs_files:
    print("No ZODB store to back up")
    sys.exit(0)

stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
for f in fs_files:
    dst = BACKUP / f"{f.stem}-{stamp}{f.suffix}"
    shutil.copy2(f, dst)
    size_mb = dst.stat().st_size / 1_048_576
    print(f"Backed up {f.name} → {dst.name} ({size_mb:.2f} MB)")

cutoff = datetime.datetime.now() - datetime.timedelta(days=7)
pruned = 0
for b in BACKUP.glob('*.fs'):
    mtime = datetime.datetime.fromtimestamp(b.stat().st_mtime)
    if mtime < cutoff:
        b.unlink()
        pruned += 1
if pruned:
    print(f"Pruned {pruned} old backups")
