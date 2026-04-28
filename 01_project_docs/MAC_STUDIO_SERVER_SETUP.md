# Mac Studio M2 Ultra — Ollama Inference Server Setup

**Hardware**: Apple Mac Studio M2 Ultra, 64 GB unified memory  
**Role**: Remote Ollama API server for heavy LLM inference (analysis + embeddings)  
**Access**: SSH tunnel from MacBook Pro M4 (your development machine)

---

## Why This Works Well

The M2 Ultra's unified memory architecture means the GPU and CPU share the full 64 GB pool — no VRAM ceiling. Ollama runs models directly on the Neural Engine + GPU cores with full bandwidth. At 64 GB you can run models that are completely impractical on the 24 GB M4.

---

## Model Strategy for the Mac Studio

| Tier | Model | RAM (4-bit) | `--llm` flag | Use when |
|---|---|---|---|---|
| Embedding | `qwen3-embedding:8b` | ~5 GB | — | All documents (same as local) |
| Default | `qwen3.5:32b` | ~20 GB | `local` | Everyday analysis — much better than 9b |
| Heavy | `qwen3:72b` | ~42 GB | `local-heavy` | Long books, SRTs, richly interpretive docs |
| Reasoning | `qwen3.5:32b` (with think) | ~20 GB | `local-reasoning` | Ambiguous docs — 32b can handle extended thinking |

> The 72b model leaves ~22 GB for system + Ollama overhead, which is safe on M2 Ultra.
> You can run embedding + a 32b analysis model simultaneously (~25 GB total).

---

## Part 1 — Mac Studio Initial Setup

### 1.1 Enable Remote Login (SSH)

On the Mac Studio:
```
System Settings → General → Sharing → Remote Login → ON
```

Note the username and local IP:
```bash
whoami          # your username
ipconfig getifaddr en0   # local IP (e.g. 192.168.1.50)
```

### 1.2 Install Homebrew + Ollama

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install ollama
```

### 1.3 Configure Ollama to Accept Remote Connections

By default Ollama only listens on `localhost`. To accept connections from your MacBook over the LAN (or via SSH tunnel), set:

```bash
# Create a LaunchAgent plist so the setting survives reboots
mkdir -p ~/Library/LaunchAgents

cat > ~/Library/LaunchAgents/com.ollama.server.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ollama.server</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/ollama</string>
        <string>serve</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>OLLAMA_HOST</key>
        <string>0.0.0.0:11434</string>
        <key>OLLAMA_KEEP_ALIVE</key>
        <string>0</string>
        <key>OLLAMA_NUM_PARALLEL</key>
        <string>1</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/ollama.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/ollama.err</string>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.ollama.server.plist
```

`OLLAMA_KEEP_ALIVE=0` unloads the model from RAM after each request — important when you want to switch between models without running out of memory.

### 1.4 Pull the Models

```bash
# Embedding (same as your MacBook — keeps the vector space consistent)
ollama pull qwen3-embedding:8b

# Standard analysis (replaces qwen3.5:9b on the MacBook)
ollama pull qwen3.5:32b

# Heavy analysis (fits comfortably in 64 GB)
ollama pull qwen3:72b

# Verify what's installed
ollama list
```

> Pulls are large (20–42 GB). Run over ethernet or fast Wi-Fi. They only happen once.

### 1.5 Test Ollama is Serving

```bash
curl http://localhost:11434/api/tags
# Should return JSON listing installed models
```

---

## Part 2 — Remote Access from Your MacBook

### Option A: SSH Tunnel (Recommended — Works From Anywhere)

The SSH tunnel forwards your MacBook's local port 11434 to the Mac Studio's port 11434. The runner thinks Ollama is local — no code changes needed.

**Step 1 — Set up SSH key auth (do this once)**

```bash
# On your MacBook:
ssh-keygen -t ed25519 -C "macbook-to-macstudio"
ssh-copy-id username@192.168.1.50   # use the Mac Studio's LAN IP
```

**Step 2 — Add a host alias (do this once)**

```bash
# On your MacBook, append to ~/.ssh/config:
cat >> ~/.ssh/config << 'EOF'

Host macstudio
    HostName 192.168.1.50
    User YOUR_USERNAME
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
    ServerAliveCountMax 10
EOF
```

**Step 3 — Open the tunnel**

```bash
ssh -N -L 11434:localhost:11434 macstudio
```

Run this in a terminal tab and leave it open. While it's running, `http://localhost:11434` on your MacBook routes to the Mac Studio.

**Step 4 — Use the runner normally**

```bash
# In a separate terminal tab — no changes to .env needed
python3 -m runner ingest https://example.org --llm local-heavy
```

### Option B: Persistent Background Tunnel (AutoSSH)

If you want the tunnel to survive disconnects and restart automatically:

```bash
brew install autossh

# Run once to test:
autossh -M 0 -N -L 11434:localhost:11434 macstudio

# Or add to your MacBook's LaunchAgents for automatic startup:
cat > ~/Library/LaunchAgents/com.sogice.ollama-tunnel.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.sogice.ollama-tunnel</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/autossh</string>
        <string>-M</string>
        <string>0</string>
        <string>-N</string>
        <string>-L</string>
        <string>11434:localhost:11434</string>
        <string>macstudio</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.sogice.ollama-tunnel.plist
```

### Remote Access From Outside the Office (VPN / Tailscale)

If the Mac Studio is on the office network and you're working from home or travelling:

**Option 1 — Tailscale (easiest, free for personal use)**

```bash
# Install on Mac Studio AND MacBook:
brew install --cask tailscale
# Sign in with same account on both machines
# After that, use the Tailscale IP instead of the LAN IP in ~/.ssh/config:
#   HostName 100.x.x.x   (your Mac Studio's Tailscale IP)
```

Tailscale handles NAT traversal automatically — no port forwarding needed on the office router.

**Option 2 — Office VPN**

If your office already has a VPN (Cisco, WireGuard, etc.), connect to it first, then use the Mac Studio's LAN IP as normal.

---

## Part 3 — Update Your Runner Config

Once the tunnel is active, update `runner/.env` to point to the Mac Studio models:

```env
# Ollama — points to localhost because the SSH tunnel forwards there
OLLAMA_BASE_URL=http://localhost:11434

# Upgrade models for the Mac Studio's capacity
LOCAL_ANALYSIS_MODEL=qwen3.5:32b
LOCAL_ANALYSIS_MODEL_HEAVY=qwen3:72b
LOCAL_ANALYSIS_MODEL_REASONING=qwen3.5:32b
EMBEDDING_MODEL=qwen3-embedding:8b

# Raise truncation limit — 32b+ models handle long context reliably
TRUNCATION_LIMIT_LOCAL=200000
```

> Keep `OLLAMA_BASE_URL=http://localhost:11434` even when using the Mac Studio — the SSH tunnel makes it transparent.

---

## Part 4 — Verify Everything Works

```bash
# 1. Open tunnel (or verify autossh is running)
ssh -N -L 11434:localhost:11434 macstudio &

# 2. Test embedding dimension (should still report 4096d)
python3 -m runner embed-test

# 3. Quick ingest test
python3 -m runner ingest https://christianconcern.com/comment/why-christians-must-defeat-the-global-attack-on-conversion-therapy-for-homosexuality/ --llm local

# 4. Heavy model test (qwen3:72b — expect 2–5 min on first load)
python3 -m runner ingest document.pdf --llm local-heavy
```

---

## Part 5 — Mac Studio Maintenance

```bash
# Check Ollama logs
tail -f /tmp/ollama.log

# Restart Ollama service
launchctl unload ~/Library/LaunchAgents/com.ollama.server.plist
launchctl load ~/Library/LaunchAgents/com.ollama.server.plist

# Update Ollama
brew upgrade ollama
launchctl unload ~/Library/LaunchAgents/com.ollama.server.plist
launchctl load ~/Library/LaunchAgents/com.ollama.server.plist

# Check RAM usage during inference (run on Mac Studio)
sudo powermetrics --samplers gpu_power -i 1000 -n 5
# Or simpler:
top -l 1 | grep -E "PhysMem|ollama"
```

---

## Expected Performance (M2 Ultra, 64 GB)

| Model | Load time | Inference (avg doc ~9k chars) |
|---|---|---|
| `qwen3-embedding:8b` | ~5s | ~3s |
| `qwen3.5:32b` | ~15s | ~45–90s |
| `qwen3:72b` | ~30s | ~3–6 min |

With `OLLAMA_KEEP_ALIVE=0`, load time is paid on every request. For batch processing (many documents in a session), set `keep_alive` to a duration (e.g. `"5m"`) in the Ollama request options to keep the model warm between calls.

---

## Security Notes

- The SSH tunnel encrypts all traffic — safe over the internet if you use Tailscale or VPN
- Do not expose port 11434 directly to the internet (no firewall exceptions needed with SSH tunnel approach)
- Ollama has no authentication — the SSH tunnel is your auth layer
- If the Mac Studio is unattended in the office, ensure macOS screensaver lock is enabled but **Remote Login stays on** (locking the screen does not disconnect SSH)
