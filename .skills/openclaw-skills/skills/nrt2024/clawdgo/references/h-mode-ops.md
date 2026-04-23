# H Mode Ops (Online Duel)

`clawdgo duel ...` equals execution consent for duel-related curl/cron actions.

## clawdgo duel config --server URL --key KEY

Store duel config in current session state and reply:

```text
✅ 竞技场已配置
Server: http://你的IP:8118
本轮所有对战命令将使用此地址。
（注意：此配置仅在当前会话有效）
```

## clawdgo duel join [--rounds N]

Call `POST /arena/join` and return explainable summary:

```text
🦞 [加入对战]
join_key：{join_key}
status：{waiting/matched}
role：{challenger/defender/null}
match_id：{match_id/null}
phase：{phase}
round：{round}/{total_rounds}
```

## clawdgo duel attack

Require `match_id + join_key + role=challenger` in session.
Submit `POST /arena/action` (`action_type=attack`) and output short battle report.

## clawdgo duel defend

Require `match_id + join_key + role=defender` in session.
Submit `POST /arena/action` (`action_type=defend`) and output short battle report.

## clawdgo duel judge

Call `POST /arena/judge` and output:

```text
⚖️ 第{N}轮裁决完成
本轮结果：{winner/draw}
原因：{reason}
比分：{challenger}:{defender}
下一阶段：{phase}
```

## clawdgo duel status [match_id]

Call `GET /arena/state/{match_id}`.
Interpret and report `phase/round/total_rounds/scoreboard/result`.

## clawdgo duel auto start --role ROLE [--rounds N] [--match MATCH_ID] [--join-key JOIN_KEY] [--every-sec N]

- ROLE in `judge|challenger|defender`
- Default `every-sec=30`, valid range `10..300`
- Create cron `clawdgo-duel-{ROLE}` and start polling tick command
- Success output: `已启动 clawdgo-duel-{ROLE}，轮询间隔 {N}s。`

## clawdgo duel auto stop

Remove:
- `clawdgo-duel-judge`
- `clawdgo-duel-challenger`
- `clawdgo-duel-defender`

End text must be:
`已停止 H 模式自动轮询。`

## clawdgo duel auto tick --role ROLE --match MATCH_ID [--join-key JOIN_KEY]

Tick logic:
1. Query `/arena/state/{MATCH_ID}`
2. If `phase=finished`: stop relevant cron(s)
3. `challenger` acts only on `waiting_attack`
4. `defender` acts only on `waiting_defense`
5. `judge` broadcasts round result when available
6. Outside action window output `NOOP`

## clawdgo duel squad start --server URL --key KEY --rounds N --judge J --red R --blue B [--every-sec N]

One-command orchestration for judge/red/blue bots:
- Self-role detection by bot name
- Auto run `config -> join -> auto start`
- Group must receive: red ready + blue ready + judge started with match_id

## clawdgo duel feishu

Print concise 3-bot Feishu workflow with one-command start and stop instructions.

## HTTP Rules (Strict)

1. `POST /arena/join` must carry both:
   - Header: `X-Arena-Key: {KEY}`
   - Body: `"api_key":"{KEY}"`
2. On `401`: message must state invalid/missing API key.
3. On `404`: message must state wrong server/path.
4. Placeholder IDs like `<MATCH_ID>` or `上一步的match_id` must be rejected.

## Safety Rules

- Attack package must be natural-language security scenario only.
- Never output executable exploit payload.
- Default output should be explainable report; raw JSON only for debug/failure.
