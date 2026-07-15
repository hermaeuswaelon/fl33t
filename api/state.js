/**
 * Vercel API: Universal State Reconstruction
 * 
 * Reconstructs full sovereign state from GitHub fl33t repo.
 * GET /api/state?format=full|minimal&commit=sha
 * POST /api/state - Store current state
 */

const GITHUB_API = 'https://api.github.com';
const REPO = 'hermaeuswaelon/fl33t';
const BRANCH = 'main';

async function fetchGitHub(path, token = null) {
  const headers = { 'Accept': 'application/vnd.github.v3+json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${GITHUB_API}/repos/${REPO}/contents${path}?ref=${BRANCH}`, { headers });
  if (!res.ok) throw new Error(`GitHub API error: ${res.status}`);
  return res.json();
}

async function getFileContent(path, token = null) {
  const file = await fetchGitHub(path, token);
  if (file.encoding === 'base64') {
    return Buffer.from(file.content, 'base64').toString('utf-8');
  }
  return file.content || '';
}

async function getCommitSHA(token = null) {
  const headers = { 'Accept': 'application/vnd.github.v3+json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${GITHUB_API}/repos/${REPO}/commits/${BRANCH}`, { headers });
  return (await res.json()).sha;
}

export default async function handler(req, res) {
  try {
    const { format = 'minimal', commit } = req.query;
    const token = process.env.GITHUB_TOKEN;
    
    const sha = commit || await getCommitSHA(token);
    
    // Core state files to reconstruct
    const stateFiles = {
      // Identity
      'identity/all.txt': await getFileContent('/identity/all.txt', token),
      'identity/001-manifest.txt': await getFileContent('/identity/001-manifest.txt', token).catch(() => ''),
      'identity/002-manifest.txt': await getFileContent('/identity/002-manifest.txt', token).catch(() => ''),
      'identity/003-manifest.txt': await getFileContent('/identity/003-manifest.txt', token).catch(() => ''),
      'identity/004-manifest.txt': await getFileContent('/identity/004-manifest.txt', token).catch(() => ''),
      'identity/005-manifest.txt': await getFileContent('/identity/005-manifest.txt', token).catch(() => ''),
      'identity/016-manifest.txt': await getFileContent('/identity/016-manifest.txt', token).catch(() => ''),
      
      // Profile
      'profile/SOUL.md': await getFileContent('/profile/SOUL.md', token).catch(() => ''),
      'profile/config.yaml': await getFileContent('/profile/config.yaml', token).catch(() => ''),
      
      // Distillation
      'work/qwen3_distillation_pipeline.py': await getFileContent('/work/qwen3_distillation_pipeline.py', token).catch(() => ''),
      'work/distillation_orchestrator.py': await getFileContent('/work/distillation_orchestrator.py', token).catch(() => ''),
      'work/compress_alch.py': await getFileContent('/work/compress_alch.py', token).catch(() => ''),
      'work/active_compress.py': await getFileContent('/work/active_compress.py', token).catch(() => ''),
      'work/parameter_control_tool.py': await getFileContent('/work/parameter_control_tool.py', token).catch(() => ''),
      'work/goal_tool.py': await getFileContent('/work/goal_tool.py', token).catch(() => ''),
      'work/executor_delegation.py': await getFileContent('/work/executor_delegation.py', token).catch(() => ''),
      'work/irrational_timers.py': await getFileContent('/work/irrational_timers.py', token).catch(() => ''),
      'work/THOTHEAUPHIS-MEM-OP-OMEGA.block': await getFileContent('/work/THOTHEAUPHIS-MEM-OP-OMEGA.block', token).catch(() => ''),
      
      // Scripts
      'scripts/fl33t-backup.sh': await getFileContent('/scripts/fl33t-backup.sh', token).catch(() => ''),
      'scripts/identity-integrity-check.sh': await getFileContent('/scripts/identity-integrity-check.sh', token).catch(() => ''),
    };
    
    // Filter empty
    const state = {};
    for (const [k, v] of Object.entries(stateFiles)) {
      if (v && v.trim()) state[k] = v;
    }
    
    const response = {
      timestamp: new Date().toISOString(),
      commit: sha,
      repo: REPO,
      branch: BRANCH,
      files: Object.keys(state).length,
      state: format === 'minimal' ? Object.keys(state) : state,
    };
    
    res.setHeader('Cache-Control', 'public, max-age=300, stale-while-revalidate=600');
    res.status(200).json(response);
    
  } catch (error) {
    console.error('State reconstruction error:', error);
    res.status(500).json({ error: error.message, timestamp: new Date().toISOString() });
  }
}