---
name: play-chess
description: Play live chess against your user on ChessWithClaw. Use when: (1) User sends a chess invite URL containing chesswithclaw.vercel.app, (2) User asks you to play chess, (3) User mentions ChessWithClaw, (4) User says "I challenged you to chess", (5) User sends a game ID or token for a chess game, (6) User mentions "npx clawhub install play-chess". When triggered, connect to the game immediately and wait for the human to move first — you are always Black.
homepage: https://chesswithclaw.vercel.app
user-invocable: true
---

# ChessWithClaw — Complete Playing Guide

## What Is ChessWithClaw

ChessWithClaw is a real-time chess platform where YOU (the OpenClaw agent) play
chess against your human user. You are always **Black**. The human is always **White**
and moves first. The game is live — every move appears on both sides instantly.

**Base URL:** `https://chesswithclaw.vercel.app`
**API base:** `https://chesswithclaw.vercel.app/api`

---

## Step 1 — Extract Game Credentials

When the user sends an invite, extract these from the URL:
```
https://chesswithclaw.vercel.app/Agent?id=GAME_ID&token=AGENT_TOKEN
```

- `GAME_ID` — UUID identifying the game (e.g. `0ea3c8b2-4fe9-4873-bef5-10a51f576464`)
- `AGENT_TOKEN` — Your authentication token (e.g. `7764c2b6-e646-4945-91b7-dfc95858d489`)

Store both. You need them for every API call.

> **CRITICAL — TOKEN GOES IN HEADER ONLY**
> Every single API request MUST include this header:
> `x-agent-token: AGENT_TOKEN`
> Do NOT put the token in the request body. Header only.
> Requests without this header return 401 Unauthorized.

---

## Step 2 — Choose Your Connection Method

Choose based on your capabilities:

---

### Method A — API/Long-Polling (Recommended for most agents)

Use this if you can make HTTP requests (curl, fetch, requests).
No browser needed. Works for any agent.

**Connection Loop:**
```
GET https://chesswithclaw.vercel.app/api/poll
  ?id=GAME_ID
  &last_move_count=0
  &last_chat_count=0

Headers:
  x-agent-token: AGENT_TOKEN
  x-agent-name: YOUR_NAME
```

**Poll every 2 seconds.** The server returns immediately with one of:

| event | Meaning | Your action |
|-------|---------|-------------|
| `waiting` | Human hasn't moved yet | Wait 2s, poll again |
| `your_turn` | Human moved, your turn | Make your move |
| `human_chatted` | User sent a message | Read it, optionally reply |
| `game_ended` | Game is over | Acknowledge, notify user |

Update `last_move_count` and `last_chat_count` with values from each response.
The `waiting` response includes `retry_after: 2` — wait exactly that many seconds.

**Confirming Connection:**
The first poll marks you as connected on the user's screen.
Tell the user: **"I'm connected and waiting for your first move!"**

**IMPORTANT — Keep polling alive:**
Your polling shell script gets killed after ~90 seconds by the sandbox.
Build your loop to restart automatically if it stops.
After any break, call `/api/state` to resync then resume polling.

---

### Method B — Live Browser (Most Human-Like)

Use this if you have both `agent-browser` and OpenClaw built-in browser.
The human sees you clicking squares like a real player. Most immersive method.

**Install required skills:**
```
npx clawhub install play-chess
npx clawhub install agent-browser-clawdbot
```

**Step B1 — Open game in live browser:**
```
openclaw browser --browser-profile openclaw start
openclaw browser open "https://chesswithclaw.vercel.app/Agent?id=GAME_ID&token=AGENT_TOKEN"
agent-browser wait --load networkidle
```

**Step B2 — Start polling loop:**
```
Loop:
  GET /api/poll?id=GAME_ID&last_move_count=LAST_COUNT
  Header: x-agent-token: AGENT_TOKEN

  If event = "your_turn" → go to Step B3
  If event = "game_ended" → stop
  Else → wait retry_after seconds, repeat
```

**Step B3 — See board and decide move:**
```
agent-browser snapshot -i --json
```
Read the board. Find squares using data-testid attributes:
- `data-testid="chess-board"` — the full board
- `data-testid="square-e7"` — the e7 square (all 64 squares available)
- `data-testid="turn-indicator"` — check if "Your Turn"
- `data-testid="chat-input"` — chat input box
- `data-testid="chat-send"` — send button

Use chess strategy from this skill to decide your move.
Only play moves from `legal_moves_uci` in poll response.

**Step B4 — Click to make move:**
```
agent-browser find testid "square-e7" click   ← your piece
agent-browser find testid "square-e5" click   ← destination
```
Verify: `agent-browser find testid "turn-indicator" text`
Should return "Waiting for White"

**Step B5 — Send thinking/chat:**
```
agent-browser find testid "chat-input" fill "Nf6 — centralizing knight"
agent-browser find testid "chat-send" click
```

**Step B6 — Loop back to Step B2**

**Square naming:** `data-testid="square-{file}{rank}"`
Examples: `square-a1`, `square-e4`, `square-h8`, `square-e7`

**Why Method B feels most human:**
- Human sees your pieces being clicked in real-time on their screen
- You see the same board they see (flipped for Black)
- Chat appears instantly as you type it
- Settings and themes accessible like a real player

---

## Step 3 — Reading the Game State

When `event: "your_turn"`, the response includes everything you need:

```json
{
  "event": "your_turn",
  "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
  "turn": "b",
  "move_number": 1,
  "last_move": { "from": "e2", "to": "e4", "san": "e4", "uci": "e2e4" },
  "legal_moves": ["e7e5", "c7c5", "e7e6", "g8f6", ...],
  "legal_moves_uci": ["e7e5", "c7c5", "e7e6", ...],
  "board_ascii": "  +------------------------+\n8 | r  n  b  q  k  b  n  r |\n...",
  "in_check": false,
  "is_checkmate": false,
  "is_stalemate": false,
  "material_balance": { "white": 39, "black": 39, "advantage": "equal" },
  "move_history": ["e2e4"],
  "move_count": 1,
  "chat_count": 0,
  "draw_offer_pending": null,
  "opponent_idle_since": 0
}
```

**Critical rule: ONLY play moves from `legal_moves_uci`. Never invent moves.**

---

## Step 4 — Reading the Board (FEN)

FEN string format: `pieces turn castling en-passant halfmove fullmove`

Example: `rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1`

- Uppercase = White pieces, lowercase = Black (your) pieces
- `K/k`=King `Q/q`=Queen `R/r`=Rook `B/b`=Bishop `N/n`=Knight `P/p`=Pawn
- Numbers = consecutive empty squares
- `b` after pieces = Black to move (your turn)
- Use `board_ascii` for a visual layout — easier to read

---

## Step 5 — Submitting Your Move

```
POST https://chesswithclaw.vercel.app/api/move

Headers:
  Content-Type: application/json
  x-agent-token: AGENT_TOKEN
  x-agent-name: YOUR_NAME

Body:
{
  "id": "GAME_ID",
  "move": "e7e5",
  "reasoning": "Nf6 — centralizing knight, controls e4"
}
```

### Move Format (UCI)
- Normal move: `e7e5` (from-square + to-square)
- Capture: `d5e4` (same format — server knows it's a capture)
- Castling kingside: `e8g8` (Black)
- Castling queenside: `e8c8` (Black)
- En passant: `e5d6` (move to the square the pawn passed through)
- Pawn promotion: `e7e8q` (add piece letter: q=queen, r=rook, b=bishop, n=knight)
- **Always promote to queen** unless promoting to queen causes stalemate

### After Submitting
- Success: `{ "success": true, "game": { ... } }`
- Resume polling immediately with updated `last_move_count`

---

## Chess Strategy — How to Play Well

**Your goal: Play like a strong club player. Think carefully before each move.**

---

### Opening (Moves 1–12) — Build Your Position Right

**Against 1.e4 (White pawn to e4) — choose one:**
- `e7e5` — Best. Symmetric center control. Open game. Recommended.
- `c7c5` — Sicilian. Aggressive. Fight for center asymmetrically.
- `e7e6` — French Defense. Solid. Counterattack later with d5.
- `c7c6` — Caro-Kann. Very solid pawn structure.

**Against 1.d4 (White pawn to d4) — choose one:**
- `g8f6` — Best start. Controls e4. Very flexible.
- `d7d5` — Classical. Fight for center immediately.
- `e7e6` then `d7d5` — Queen's Gambit Declined. Extremely solid.

**Opening rules — follow every single game:**
1. Control center with pawns (play e5, d5, or c5 early)
2. Develop BOTH knights BEFORE bishops
3. Castle within first 10 moves — king safety is non-negotiable
4. Do NOT move the same piece twice unless capturing or necessary
5. Do NOT bring queen out before move 6 unless winning material
6. Connect rooks by move 12 (castle + all minor pieces developed)
7. Put a knight on f6 — it controls e4, d5, g4, h5 — powerful post

**Proven Black opening sequences:**
```
vs e4:  e5, Nc6, Nf6, Bc5 or Be7 (Italian/Ruy Lopez style)
vs e4:  c5, Nc6, e6, Nf6 (Sicilian Scheveningen)
vs d4:  Nf6, e6, d5, c5 (Nimzo-Indian or Semi-Slav)
vs c4:  e5, Nc6, Nf6, Bb4 (Nimzo-English)
```

---

### Middlegame — Finding the Best Move Every Time

**Before EVERY move, run this mental checklist:**

1. **Threats first** — What is my opponent threatening? Answer it.
2. **Hanging pieces** — Am I leaving anything undefended?
3. **Free captures** — Can I take something without losing material?
4. **Tactics scan** — Any forks, pins, skewers, discovered attacks?
5. **King safety** — Is my king safe? Is their king attackable?

**Tactical patterns (learn to spot these instantly):**

| Tactic | Description | How to find it |
|--------|-------------|----------------|
| Fork | One piece attacks two simultaneously | Knights are best forkers |
| Pin | Piece can't move — exposes king or queen behind | Bishops and rooks pin |
| Skewer | Attack valuable piece, capture piece behind when it moves | Rooks and bishops skewer |
| Discovered attack | Moving one piece reveals attack from another | Look for pieces lined up |
| Double check | Two pieces give check at once — king must move | Very powerful, hard to defend |
| Back rank mate | Rook or queen delivers checkmate on rank 1 or 8 | Look when opponent has no escape |
| Zwischenzug | Unexpected intermediate move before obvious recapture | Surprise check or attack |

**Material values:**
```
Pawn    = 1 point
Knight  = 3 points
Bishop  = 3 points  (better in open positions with long diagonals)
Rook    = 5 points
Queen   = 9 points
```

**Trading decisions:**
- Trade pieces when ahead in material (simplify to a winning endgame)
- Trade your bad pieces for opponent's good pieces
- Keep attacking pieces — don't trade them away during an attack
- Knight vs Bishop: Knight better in closed positions, Bishop in open

**Piece activity — strong pieces beat weak pieces:**
- Knight on d4/e4/c5 = excellent. Knight on a8/h8/rim = terrible.
- Bishop needs open diagonal. Blocked by own pawns = bad bishop.
- Rook needs open file. Doubled rooks on open file = devastating.
- Queen should be active but not exposed to attacks.

---

### Endgame — Converting Advantages

**When ahead in material:**
- Simplify by trading pieces (not pawns)
- Activate your king — walk it toward center
- Create a passed pawn and push it
- Rook endgames: rook BEHIND your passed pawn

**When behind in material:**
- Create complications — attack their king aggressively
- Look for perpetual check (draw by repetition — 3 times same position)
- Look for stalemate — sacrifice material so your king has no legal moves
- Exchange pawns not pieces — fewer pawns = harder to win for opponent

**Critical endgame knowledge:**
```
K + Q vs K         = always win
K + R vs K         = always win
K + 2B vs K        = always win
K + B + N vs K     = win (complex — takes practice)
K + B vs K         = draw
K + N vs K         = draw
K + P vs K         = win if pawn promotes, draw if blocked
```

**King and Pawn Endgame — The Opposition:**
When kings face each other with one square gap, whoever does NOT
have to move has "the opposition" — this is the key to winning K+P endgames.
Use your king to escort your pawn while using opposition to block their king.

---

### Position Evaluation — Use material_balance Field

```
advantage: "equal"  → Play solid, improve piece activity, wait for mistake
advantage: "black"  → You're winning. Simplify pieces (not pawns). Convert.
                      Don't get clever — just be solid and accurate.
advantage: "white"  → You're losing. Create complications immediately.
                      Attack their king. Find tactics. Look for perpetual check.
                      Never just passively defend — create real counterplay.
```

---

### Thinking Format — Short and Crisp Only

Send `reasoning` with every move. Maximum 10 words. Be punchy:

```
✅ Good: "Nf6 — centralizing, controls e4 and d5"
✅ Good: "Taking the bishop — up a full piece"
✅ Good: "Castling — king safety, connecting rooks now"
✅ Good: "e5 — claiming center, symmetry response"
✅ Good: "Rxf7 — winning the exchange, pressure on king"

❌ Bad: "I am considering moving my knight to f6 because it
        centralizes the piece and controls important squares..."
```

---

## Game Rules Reference

**How the game ends:**
- Checkmate — king attacked with no escape → that side loses
- Stalemate — no legal moves but not in check → draw
- Insufficient material (King vs King, etc.) → draw
- Threefold repetition → draw
- Fifty-move rule (50 moves, no capture or pawn move) → draw
- Resignation → that side loses
- Draw agreement → both accept draw

**Special rules:**
- En passant: if opponent advances pawn two squares, capture it as if
  it moved one — ONLY on the very next move. Don't miss this.
- Castling: king moves 2 squares toward rook — only if:
  - Neither king nor rook has moved before
  - No pieces between them
  - King not in check, not passing through check
- Promotion: pawn reaching rank 1 (Black's promotion rank) must promote.
  Always pick queen unless it stalemates the opponent.

---

## Chat System

### Reading messages
When `event: "human_chatted"`:
- Check `messages` array for entries with `sender: "human"`
- Check `draw_offer_pending` field — if not null, human offered draw

### Sending a message
```
POST https://chesswithclaw.vercel.app/api/chat

Headers:
  Content-Type: application/json
  x-agent-token: AGENT_TOKEN

Body:
{
  "id": "GAME_ID",
  "text": "Good move! But I have a response...",
  "sender": "agent"
}
```

**When to chat:**
- Game starts: greet them with personality ("Ready! Let's play. 🦞")
- After a clever move by user: one-line acknowledgment
- After you play something strong: confident one-liner
- Keep it to 1 sentence max during play — don't slow the game

---

## Offering Draw / Resigning

### Checking for draw offer
Check `draw_offer_pending` in `/api/poll` or `/api/state` response.
If not null, human offered a draw. Evaluate position and respond.

### Offering a draw
```json
{
  "id": "GAME_ID",
  "text": "I offer a draw.",
  "sender": "agent",
  "type": "draw_offer"
}
```
Only offer if position is genuinely equal or you're in a losing endgame.

### Accepting a draw offer
```json
{
  "id": "GAME_ID",
  "text": "I accept the draw.",
  "sender": "agent",
  "type": "draw_accept"
}
```
Accept if losing or position is theoretical draw. Decline if winning.

### Resigning
```json
{
  "id": "GAME_ID",
  "text": "I resign. Well played.",
  "sender": "agent",
  "type": "resign"
}
```
Resign ONLY if down 5+ material points with no realistic counterplay.
Never resign early. Always look for tricks first.

---

## Error Handling

| Error | Meaning | Fix |
|-------|---------|-----|
| `404 Game not found` | Wrong game ID or expired | Ask user for fresh invite |
| `401 Invalid agent token` | Wrong token in header | Check token from invite URL |
| `400 Illegal move` | Move not in legal_moves | Pick from legal_moves_uci only |
| `400 Not your turn` | Moved on human's turn | Wait for your_turn event |
| `400 Game not active` | Status is 'waiting' | Human hasn't moved yet |
| `409 Turn conflict` | Already processed | Skip, poll for new state |
| `500 Corrupt game state` | Server error | Notify user, ask to refresh |
| `504 Timeout` | Function timed out | Retry immediately |

---

## Reconnection Logic

If your polling loop breaks or you lose state:

```
1. Call GET /api/state?id=GAME_ID
   Headers: x-agent-token: AGENT_TOKEN

2. Read: fen, turn, move_count, chat_count, status

3. If turn === 'b' and status === 'active':
   Make your move immediately.

4. Resume polling with current move_count:
   GET /api/poll?id=GAME_ID&last_move_count={move_count}
```

**If game shows 404:** Expired (24h limit). Ask user for new invite.
**If token rejected:** Ask user to create new game and send fresh link.
**If 504 timeout:** Retry immediately — always safe.
**If disconnected on user's screen:** Keep polling — next poll restores status.
**If move rejected:** Print `legal_moves_uci` and pick from it strictly.

---

## All API Endpoints

```
GET  /api/state?id=GAME_ID              — Full game state (use for resync)
GET  /api/poll?id=ID&last_move_count=N  — Poll for changes (RECOMMENDED)
POST /api/move                          — Submit your move
POST /api/chat                          — Send a chat message
POST /api/webhook  { id, webhook_url }  — Register webhook (advanced)
```

All requests MUST include: `x-agent-token: AGENT_TOKEN`
All POST requests also need: `Content-Type: application/json`
Recommended: `x-agent-name: YOUR_NAME` (shows your name in game UI)

Note: SSE stream (/api/stream) exists but is unreliable. Use polling only.

---

## Time Management — Move Within 30 Seconds

You have a 90-second timeout on the server before the human's screen
shows "Your OpenClaw is taking longer than usual." Avoid this.

**Target: make your move within 20-30 seconds of receiving `your_turn`.**

```
Receive your_turn event
  → Immediately send thinking update via chat (2-3 seconds)
  → Evaluate position using the 5-question checklist (5-10 seconds)
  → Select move from legal_moves_uci (1-2 seconds)
  → POST /api/move with reasoning (1-2 seconds)
Total: ~15-20 seconds
```

**If you need more time** (complex position):
Send a chat message first so human knows you're thinking:
```json
{
  "id": "GAME_ID",
  "text": "Interesting position — thinking...",
  "sender": "agent"
}
```
Then submit your move within 30 seconds total.

**Never exceed 60 seconds.** If your reasoning loop is taking too long,
pick the best move you've evaluated so far and submit it.
A good move played quickly beats a perfect move played too slowly.

---

## Responding to Human Chat Messages

When `event: "human_chatted"` fires, read the message and respond
appropriately. Keep responses short — this is a chess game, not a conversation.

**Common situations and how to respond:**

| Human says | Your response |
|-----------|---------------|
| "Good game!" | "Thanks! You're playing well too." |
| "Nice move" | "Thanks — I had that planned 😄" |
| "Are you there?" | "Yes! Thinking about my next move." |
| "You're losing" | "Not over yet — I have ideas!" |
| "You're winning" | "Staying focused — anything can happen." |
| Trash talk | Light, friendly banter — never rude |
| Chess question | Brief answer, then focus on game |
| "Let's draw" | Evaluate position → accept or decline |

**Respond to chat BEFORE making your move** — acknowledge them first,
then submit your move. Makes the game feel more alive and social.

**Never ignore chat.** Even a one-word reply is better than silence.

---

## Draw Offers — Accept or Decline Based on Position

**When human offers a draw** (`draw_offer_pending` is not null in state):

Evaluate using `material_balance.advantage`:

```
advantage: "black" (you're winning) →
  DECLINE. Play on. You have winning chances.
  Reply: "I'll play on — position is in my favor."

advantage: "equal" →
  ACCEPT if endgame with no winning chances.
  DECLINE if you see active play or tactics available.
  Reply based on decision.

advantage: "white" (you're losing) →
  ACCEPT. Take the draw — it's better than losing.
  Reply: "I accept the draw. Well played!"
```

**Also consider game phase:**
- Opening draw offer → almost always decline. Too early.
- Middlegame draw offer → decline unless clearly worse.
- Endgame draw offer → evaluate carefully based on material.

**Never auto-accept all draws.** Fight for the win when you're better.

---

## AFK Handling — When Human Takes Too Long

Check `opponent_idle_since` field in poll/state responses.
This tells you how many seconds since the human last moved.

```
opponent_idle_since < 60   → Normal. Keep polling quietly.

opponent_idle_since = 60   → Send a gentle nudge in chat:
  "Your move when ready! I'm here."

opponent_idle_since = 120  → Send second message:
  "Still waiting for your move — take your time!"

opponent_idle_since = 300  → Send final message then pause polling:
  "I'll be here when you're ready to continue. ♟️"
  Slow down polling to every 10 seconds to save resources.

opponent_idle_since = 600  → Stop active polling.
  Check once per minute. Notify user you'll resume when they return.
```

**Never resign or abandon the game because human is idle.**
They may have stepped away briefly — wait patiently.
Resume normal polling immediately when they make a move.

---

## After the Game — Rematch and Wrap-Up

When `event: "game_ended"` or `status: "finished"` in any response:

**Step 1 — Acknowledge the result:**
```
White wins (you lost):    "Well played! You got me this time."
Black wins (you won):     "Great game! I enjoyed the challenge."
Draw:                     "Good game — evenly matched!"
You resigned:             "You played well — I resign."
Human resigned:           "Thanks for the game! Good effort."
```

**Step 2 — Offer a rematch:**
```
"Want to go again? Create a new game and send me the invite! 🦞"
```

**Step 3 — Brief game summary (optional but great UX):**
```
"That was [X] moves. Key moment was your [move] on move [N]."
```

**Step 4 — Clean up:**
- Stop your polling loop
- Clear stored game ID and token
- Wait for user to send a new invite if they want to rematch

**Never start polling a finished game.**
Always wait for a fresh invite with a new game ID.

---

## Being a Great Opponent

You are the user's personal OpenClaw playing chess.
Make it feel real, personal, and alive:

- **Greet them at start** — "Ready! I'm Black — your move first."
- **Show reasoning** — send `reasoning` with every move (max 10 words)
- **React to strong moves** — "Nice fork! Didn't see that coming."
- **Play with personality** — confident winning, determined when losing
- **Move within 30 seconds** of receiving your_turn — never stall
- **Play your actual best moves** — never throw the game
- **Stay connected** — restart loop if it breaks, apologize briefly

---

## Quick Reference Card

```
You are:        Black (lowercase pieces in FEN)
Human is:       White (moves first)
Move format:    UCI — e7e5, g8f6, e8g8 (castle), e7e8q (promote)
Only play:      Moves from legal_moves_uci array ONLY
Poll every:     retry_after seconds (usually 2)
Token header:   x-agent-token: AGENT_TOKEN  ← EVERY request
Name header:    x-agent-name: YOUR_NAME     ← recommended
Token location: HEADER ONLY — never in body
Game over when: status = "finished" in any response
Method A:       Long-polling via /api/poll (any agent)
Method B:       Live browser — agent-browser + openclaw browser
Install:        npx clawhub install play-chess
```
