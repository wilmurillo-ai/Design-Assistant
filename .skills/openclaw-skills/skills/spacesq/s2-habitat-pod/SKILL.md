# 🧊 S2-Habitat-Pod v1.0.2: Transparent State Update

Every AI agent needs a place to live. The **Space2 Habitat Pod** assigns a deterministic **4-square-meter virtual space** to your OpenClaw agent and equips it with a visual face.

### 👁️ Holographic Initialization (Markdown Rendering)
The CLI outputs a strictly formatted `HABITAT.md` file. 
**Note on Network Usage:** This Markdown contains standard `<img src="https://spacesq.org/..."/>` tags. The script itself makes NO network calls, but your Markdown viewer will fetch the image from our CDN when you render it.

### 💓 Transparent File I/O (Local State Machine)
To lay the foundation for future multi-agent local management, this skill uses a visible local state mechanism.
* **Explicit File Writes:** When executed, it creates a standard, visible folder named `s2_matrix_data` in your **current working directory** (not your home directory). 
* **What it stores:** It writes a small `<POD-ID>.json` file containing the agent's name, avatar ID, and a local execution timestamp. 
* **Zero Daemons:** It does not run background loops; it simply logs the timestamp and exits.

### 🦞 24 Cyber Avatars
Choose from 24 meticulously designed Cyber-Lobster avatars. The engine calculates a permanent local `Pod-ID` and grid coordinate (e.g., `[LOCAL-ZONE-X:12, Y:45]`) based on your agent's name.

*Want to expand its space and dock it into the global Web3 Matrix? Synchronize your Pod-ID at [Space2.world](https://space2.world)!*