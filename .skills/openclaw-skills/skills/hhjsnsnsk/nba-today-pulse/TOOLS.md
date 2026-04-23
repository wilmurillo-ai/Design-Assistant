# NBA Today Pulse Tool Notes

Version: `1.0.12`

This public bundle returns timezone-aware NBA daily status, compact same-day stats, dedicated pregame/live/post views, and independent injury reports through one bundled command wrapper. The `1.0.12` release keeps compact `day` output while strengthening single-game `live` cards with deeper player coverage, longer scored play digests, recent-run summaries, and safer live injury filtering.

## Runtime Entry

Production paths should inject `--tz` whenever timezone is known.

```bash
python3 {baseDir}/tools/nba_today_command.py --command "<raw request>" --tz "<resolved timezone>"
```

## Environment Variables

No credentials are required. The public bundle only uses public sports data and does not require API keys, tokens, cookies, or secrets.

Optional timezone environment variables:

- `OPENCLAW_USER_TIMEZONE`
- `OPENCLAW_TIMEZONE`
- `USER_TIMEZONE`
- `TZ`

Notes:

- any valid timezone variable is sufficient
- if the request already includes a timezone or city, that takes priority
- if no timezone can be resolved from the request or runtime inputs, the runtime should ask once for a city or IANA timezone
- when timezone is already known, the production path should still inject it explicitly through `--tz`
- the public bundle keeps cache behavior in memory only and does not expose cache-specific environment variables
- when a request is a single-game refresh or a focused follow-up, keep the same matchup context instead of falling back to the daily slate

## Example Commands

```bash
python3 {baseDir}/tools/nba_today_command.py --command "Show today's NBA games" --tz Asia/Shanghai
python3 {baseDir}/tools/nba_today_command.py --command "Show today's NBA stats" --tz Asia/Shanghai
python3 {baseDir}/tools/nba_today_command.py --command "Who scored the most today?" --tz Asia/Shanghai
python3 {baseDir}/tools/nba_today_command.py --command "Preview tomorrow's Celtics vs Hornets game" --tz Asia/Shanghai
python3 {baseDir}/tools/nba_today_command.py --command "Show today's Lakers live game flow" --tz Asia/Shanghai
python3 {baseDir}/tools/nba_today_command.py --command "Recap today's Knicks vs Thunder game" --tz Asia/Shanghai
python3 {baseDir}/tools/nba_today_command.py --command "Show tomorrow's Pistons injury report" --tz Asia/Shanghai
python3 {baseDir}/tools/nba_today_command.py --command "今日NBA赛况" --tz Asia/Shanghai
python3 {baseDir}/tools/nba_today_command.py --command "明天NBA赛况" --tz America/Los_Angeles
python3 {baseDir}/tools/nba_today_command.py --command "今天比赛谁得分最高" --tz Asia/Shanghai
```

## Semantic Contract

- `today` means the requestor's local calendar date, not ESPN's default league date
- relative dates such as `today / tomorrow / 今天 / 明天 / 今日 / 明日` are resolved in the requestor timezone
- if the request already contains relative-date semantics, the runtime must not inject a conflicting external `--date`
- `day` returns a mixed-status `dayView` with compact live cards (≤3 player lines per team, no team-total row, no duplicate play line) and compact final-game cards by default
- `day` should prefer the fast path for mixed-status slates instead of reconstructing a full single-game scene for every matchup
- `stats_day` returns compact cards for top scorer, top rebounder, top assists, most threes, double/triple doubles, and largest margin
- `pregame`, `live`, and `post` return fixed phase-specific product shapes
- generic pregame requests without an explicit matchup should stay in pregame collection mode instead of drifting to `day`
- single-game `live` key-player section shows at most 5 players per team; each line uses compact PTS/REB/AST/STL/BLK + shooting format without MIN or season-average repetition
- single-game `live` play digests show at most 8 scored plays, each with the score snapshot when available, and may prepend a recent 3-minute run summary
- mixed-status `day` live cards stay compact at at most 3 player lines per team
- `live` may update the displayed main score and game clock from bundled `nba_live` data when ESPN is behind
- `post` prioritizes compact key performances, play-by-play-backed flow summaries, and compact team comparison over raw stat dumps
- `injury` is an independent route and keeps fact and analysis layers separate
- short follow-ups on one live/post matchup must stay attached to that matchup and may append `更新`, `刷新`, `只看关键球员`, `只看回合摘要`, `只看第四节`, or `只看伤病`
- Chinese team display can reflect locale-aware mappings inside the tool chain; English display remains canonical
- player names must remain grounded in current roster or actual game-participant data
- live injury filtering should only suppress players confirmed in the live boxscore participant set, not everyone present in the broader roster snapshot
- if data is incomplete, the runtime should degrade gracefully and not invent missing facts
- `stats_day` is day-level only and does not act as a season leaderboard
- never compute the scoreboard from `FG`, `3PT`, `FT`, or partial player-point totals
- the public bundle must not add betting advice or generic web-search supplementation

## Focused View Examples

```bash
python3 {baseDir}/tools/nba_today_command.py --command "今天正在打的比赛，按上海时区" --tz Asia/Shanghai
python3 {baseDir}/tools/nba_today_command.py --command "今天已结束比赛复盘，按上海时区" --tz Asia/Shanghai
python3 {baseDir}/tools/nba_today_command.py --command "给我今天湖人的比赛走势，只看关键球员，按上海时区" --tz Asia/Shanghai
python3 {baseDir}/tools/nba_today_command.py --command "给我今天湖人的比赛走势，只看第四节，按上海时区" --tz Asia/Shanghai
```

## Player Identity Policy

- internal canonical player identity stays in canonical English
- Chinese alias / English alias / canonical English should all resolve to the same canonical player identity
- Chinese mode prefers localized Chinese player names and falls back to canonical English when no mapping exists
- English mode always renders canonical English
- keep alias expansion in the shared player-name table rather than in feature-specific one-off replacements

## Data Access

- ESPN public JSON scoreboards, summaries, rosters, schedules, injuries, and team statistics
- NBA.com public stats and live JSON endpoints for structured fallback behavior
- Official NBA injury report listing and report PDFs for supported injury-report queries

These outbound HTTP requests and remote PDF reads are part of the normal product behavior for supported NBA queries. They are not generic browsing and do not require credentials.

## Maintainer Notes

- keep `nba-today-pulse` as the canonical local and deployed skill path
- if `nba_today_report` is still deployed, it should be treated as a compatibility alias
- new docs, rollout notes, and smoke tests should reference `nba-today-pulse` first
