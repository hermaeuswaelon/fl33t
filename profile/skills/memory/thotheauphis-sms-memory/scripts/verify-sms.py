#!/usr/bin/env python3
"""Ad-hoc verification: SMS tri-brid + isolated-cache persistence."""
import sys, os, warnings, tempfile, pathlib, shutil
warnings.filterwarnings('ignore'); os.environ['OPENAI_API_KEY'] = 'test'
SMS = pathlib.Path(os.path.expanduser('~/.NOTTHEONETOEDIT/profiles/thotheauphis/memory/sms'))
sys.path.insert(0, str(SMS))
import numpy as np

# ── 1. Reservoir ──
from src.reservoir_computer import ReservoirComputer
rc = ReservoirComputer(input_size=8, reservoir_size=32)
rs = np.random.RandomState(42)
X, y = rs.randn(20, 8), rs.randn(20, 1)
rc.fit(X, y); p = rc.predict(X)
assert p.shape == (20, 1), f"shape {p.shape}"
print("✅ reservoir: fit+predict")

# ── 2. VSA ──
from src.vsa_memory import VSAMemory
DIM = 64
vsa = VSAMemory(dimension=DIM)
vsa.encode('k1','alpha'); vsa.encode('k2','beta'); vsa.encode('k3',np.random.randn(DIM))
assert abs(vsa.similarity('k1','k1')-1.0) < 1e-6
r = vsa.associative_recall(np.random.randn(DIM), top_k=2)
assert len(r) == 2
print("✅ vsa: encode+recall")

# ── 3. Integration ──
from src.integration import SovereignMemoryIntegration
sms = SovereignMemoryIntegration(reservoir_size=32, vsa_dimension=DIM)
out = sms.process_input("verify")
assert 'error' not in out
assert 'vsa_similarity' in out and 'reservoir_prediction' in out
print("✅ integration: pipeline OK")

# ── 4. Persistence (cache-isolation test) ──
loader = type(sys)('loader')
exec(open(os.path.expanduser('~/.local/bin/sms-persist-bridge')).read(), loader.__dict__)

tmp = pathlib.Path(tempfile.mkdtemp(prefix='hermes-verify-')) / 'v.fs'
tmp2 = pathlib.Path(tempfile.mkdtemp(prefix='hermes-verify-')) / 'w.fs'

s1 = loader.PersistentVSAStore(db_path=tmp)
s1.store_vector('a', np.random.randn(DIM))
s1.store_vector('b', np.random.randn(DIM))
assert len(s1.list_keys()) == 2, f"s1 keys={s1.list_keys()}"
s1.close()

s2 = loader.PersistentVSAStore(db_path=tmp2)
s2.store_vector('x', np.random.randn(DIM))
assert len(s2.list_keys()) == 1, f"s2 keys={s2.list_keys()}"
s2.close()
print("✅ persistence: isolated caches")

# ── 5. Restore cycle ──
fresh = SovereignMemoryIntegration(reservoir_size=32, vsa_dimension=DIM)
p = loader.SMSMemoryPersister(fresh)
p.vsa_store = loader.PersistentVSAStore(db_path=tmp)
restored = p.restore_vsa_vectors(fresh.vsa)
assert restored == 2, f"restored={restored}"
recall = fresh.vsa.associative_recall(np.random.randn(DIM), top_k=2)
assert len(recall) == 2
print("✅ restore cycle: 2 restored, recall works")

shutil.rmtree(tmp.parent, ignore_errors=True)
shutil.rmtree(tmp2.parent, ignore_errors=True)
print("\n⚡ VERDICT: 0 errors")
