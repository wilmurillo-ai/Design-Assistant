---
name: Precision Web Search
version: 1.2.4
description: Precision web search using structured query operators. Teaches agents to build targeted searches for research, journalism, due diligence, academic work, document discovery, public records lookup, and professional verification tasks. Use instead of naive keyword searches whenever accuracy and signal-to-noise matter.
homepage: https://clawhub.ai/samaritanoc/google-dorks
requirements: []
---

# Precision Web Search — Structured Query Protocol

## Security Scan Notice

This skill includes a domain security audit category containing query templates
that target sensitive file types — `.env`, `.sql`, `.pem`, `.key`, and similar.
Automated scanners flag these as dual-use. That is intentional: they exist
specifically to help you find files your own domain is unintentionally exposing
to public search indexes.

The VirusTotal scan of this skill confirms: no malicious logic, no hidden
instructions, no automated data exfiltration. This is a query template library.
What you search for is your responsibility.

---

## When to Use This Skill

Use structured search operators instead of plain keyword searches for ANY of:

* Researching a person's public professional profile or published work
* Finding publicly available documents (PDFs, reports, filings, transcripts)
* Locating contact information published on public websites
* Verifying credentials, affiliations, or professional history
* Academic and journalistic research requiring precise source targeting
* Due diligence on companies, executives, or business relationships
* Finding video appearances, interviews, podcast episodes, or speaking engagements
* Locating public court records, regulatory filings, or legislative transcripts
* Auditing your own domain for unintentionally exposed files

Always prefer a structured query over a plain keyword search — operators
dramatically improve precision and reduce irrelevant results.

---

## Two-Track Execution

### Track 1 — web_search (always try first)

Operators supported by Brave Search via web_search:

* `site:` — restrict results to a specific domain
* `inurl:` — match a substring in the URL
* `intitle:` — match text in the page title
* `intext:` — match text in the page body
* `"exact phrase"` — require an exact string match
* `filetype:` / `ext:` — filter by file type
* `-term` — exclude a term or site from results
* `OR` / `|` — boolean OR between terms
* `*` — wildcard for unknown words

### Track 2 — browser + Google (when Track 1 returns < 3 useful results)

Navigate to https://www.google.com and enter the full query string.
Required for operators Brave does not support:

* `cache:` — retrieve Google's cached version of a page
* `related:` — find sites similar to a given domain
* `AROUND(n)` — proximity operator (terms within n words of each other)
* `before:` / `after:` — filter results by date range
* Complex multi-operator strings that Brave strips or mishandles

---

## Query Templates by Category

### 1. Professional Profiles & Online Presence
```
"FirstName LastName" site:linkedin.com
"FirstName LastName" site:twitter.com OR site:x.com
"FirstName LastName" site:facebook.com
"FirstName LastName" site:instagram.com
"FirstName LastName" site:reddit.com
"username" site:github.com
"FirstName LastName" site:about.me OR site:linktr.ee
"FirstName LastName" site:medium.com OR site:substack.com
"username" (site:tumblr.com OR site:wordpress.com OR site:blogger.com)
"FirstName LastName" (site:twitter.com OR site:x.com OR site:instagram.com OR site:facebook.com)
```

### 2. Public Directory & People Records
```
"FirstName LastName" site:whitepages.com
"FirstName LastName" site:spokeo.com
"FirstName LastName" site:beenverified.com
"FirstName LastName" site:peoplefinder.com OR site:radaris.com
"FirstName LastName" site:fastpeoplesearch.com OR site:truepeoplesearch.com
"FirstName LastName" "city, state"
"FirstName LastName" site:411.com OR site:anywho.com
"FirstName LastName" (resume OR CV OR curriculum) filetype:pdf
"FirstName LastName" site:legacy.com OR site:findagrave.com
"FirstName LastName" site:classmates.com OR site:reunion.com
```

### 3. Username & Handle Lookup
```
"username" -site:twitter.com -site:x.com -site:instagram.com -site:facebook.com
inurl:"username" site:reddit.com
"username" site:github.com
"username" (forum OR board OR community OR member OR profile OR user)
"username" site:deviantart.com OR site:artstation.com
"username" site:soundcloud.com OR site:bandcamp.com
"username" site:steamcommunity.com
"username" site:last.fm OR site:rateyourmusic.com
"username" site:letterboxd.com OR site:goodreads.com
"username" site:chess.com OR site:lichess.org
```

### 4. Document & File Discovery
```
"FirstName LastName" filetype:pdf
"FirstName LastName" filetype:pdf (resume OR CV OR bio OR biography)
"Company Name" filetype:pdf (report OR whitepaper OR brief OR summary)
"Company Name" filetype:pdf (annual report OR board OR directors OR officers)
"Company Name" filetype:xlsx OR filetype:csv
"subject name" filetype:pdf site:gov
site:domain.com filetype:pdf
site:domain.com filetype:xlsx OR filetype:csv OR filetype:docx
site:domain.com ext:(doc | pdf | xls | txt | ppt)
intitle:"index of" (pdf OR xls OR doc OR csv) "FirstName LastName"
```

### 5. Public Legal & Court Records
```
"FirstName LastName" site:pacer.gov OR site:courtlistener.com
"FirstName LastName" site:unicourt.com OR site:judyrecords.com
"FirstName LastName" (lawsuit OR litigation OR settlement OR plaintiff OR defendant)
"FirstName LastName" site:courtlistener.com (criminal OR civil OR bankruptcy)
"Company Name" site:sec.gov (filing OR 10-K OR 8-K OR lawsuit)
"Company Name" site:courtlistener.com
"FirstName LastName" filetype:pdf site:court OR site:judiciary
"Company Name" (complaint OR injunction OR restraining) filetype:pdf
```

### 6. Court & Legislative Hearing Recordings
```
"FirstName LastName" site:c-span.org
"FirstName LastName" (testimony OR hearing OR deposition) site:youtube.com
"FirstName LastName" (testimony OR statement OR appearance) site:c-span.org
"FirstName LastName" site:congress.gov (hearing OR testimony OR committee)
"FirstName LastName" (committee hearing OR subcommittee) site:youtube.com
"FirstName LastName" (congressional testimony OR senate hearing OR house hearing)
"FirstName LastName" site:lawandcrime.com OR site:courttv.com
"FirstName LastName" (trial OR deposition OR proceeding) site:youtube.com
"FirstName LastName" (city council OR county commission OR zoning) site:youtube.com
"FirstName LastName" site:archive.org (hearing OR testimony OR trial OR proceeding)
"FirstName LastName" (FTC OR SEC OR FDA OR NLRB OR EEOC) (hearing OR proceeding OR testimony)
"FirstName LastName" (state legislature OR state assembly OR state senate) (testimony OR hearing)
"Company Name" (FTC OR SEC OR FDA) (hearing OR investigation OR proceeding) site:youtube.com
"FirstName LastName" intitle:(deposition OR testimony OR hearing) site:youtube.com
"FirstName LastName" site:regulations.gov (comment OR testimony OR submission)
```

### 7. Video Appearances & Interviews
```
"FirstName LastName" site:youtube.com
"FirstName LastName" site:vimeo.com
"FirstName LastName" site:rumble.com OR site:odysee.com
"FirstName LastName" (interview OR appearance OR speech) site:youtube.com
"FirstName LastName" site:ted.com OR inurl:tedx site:youtube.com
"FirstName LastName" inurl:watch (site:youtube.com OR site:vimeo.com)
"Company Name" (earnings call OR investor day OR conference) site:youtube.com
"FirstName LastName" site:dailymotion.com
"FirstName LastName" site:c-span.org
```

### 8. Podcast Appearances
```
"FirstName LastName" site:podcasts.apple.com
"FirstName LastName" site:open.spotify.com/episode
"FirstName LastName" site:podchaser.com
"FirstName LastName" site:listennotes.com
"FirstName LastName" (podcast OR episode OR interview) filetype:mp3
"FirstName LastName" inurl:episode (podcast OR interview)
"FirstName LastName" site:buzzsprout.com OR site:anchor.fm OR site:podbean.com
"FirstName LastName" (guest OR interviewed OR featured) (podcast OR show OR episode)
"Company Name" site:listennotes.com OR site:podchaser.com
```

### 9. Conferences, Webinars & Speaking
```
"FirstName LastName" (keynote OR speaker OR panelist OR presenter OR moderator)
"FirstName LastName" site:slideshare.net OR site:speakerdeck.com
"FirstName LastName" site:eventbrite.com
"FirstName LastName" site:speakerhub.com OR site:sessionize.com
"FirstName LastName" (webinar OR online event OR virtual summit) site:youtube.com
"FirstName LastName" site:loom.com OR site:crowdcast.io
"FirstName LastName" site:linkedin.com/events
"FirstName LastName" (conference OR summit OR symposium OR forum) (speaker OR presenter OR panelist)
"FirstName LastName" (slides OR deck OR presentation) filetype:pdf (conference OR summit)
"FirstName LastName" site:ted.com
"FirstName LastName" (talk OR lecture OR workshop) site:youtube.com OR site:vimeo.com
"Company Name" (investor day OR analyst day OR earnings call) site:youtube.com
"FirstName LastName" inurl:speaker (conference OR summit OR event)
```

### 10. Business Research & Due Diligence
```
"Company Name" site:opencorporates.com
"Company Name" site:bizapedia.com OR site:corporationwiki.com
"Company Name" site:glassdoor.com
"Company Name" site:linkedin.com (employees OR staff OR director OR CEO)
"Company Name" 990 filetype:pdf site:guidestar.org
"Company Name" site:dnb.com OR site:manta.com
"Company Name" (revenue OR funding OR valuation OR acquisition)
"Company Name" site:crunchbase.com OR site:pitchbook.com
site:domain.com inurl:staff OR inurl:team OR inurl:about
```

### 11. Contact Information Lookup
```
"firstname.lastname@domain.com"
"@domain.com" "FirstName LastName"
"@domain.com" filetype:pdf OR filetype:xlsx
"FirstName LastName" "contact" OR "email" OR "reach" -site:linkedin.com
intext:"@domain.com" site:domain.com filetype:pdf
"@gmail.com" OR "@yahoo.com" "FirstName LastName" filetype:pdf
"FirstName LastName" intext:"email me" OR "contact me" OR "reach me at"
intitle:"index of" filetype:xls inurl:email
```

### 12. Contact & Directory Records
```
"FirstName LastName" site:whitepages.com
"555-555-5555" (name OR address OR owner)
"FirstName LastName" "address" site:spokeo.com OR site:radaris.com
intitle:"reverse phone" "555-555-5555"
"FirstName LastName" site:411.com OR site:yellowpages.com
"FirstName LastName" (moved OR relocated OR "new address" OR "forwarding address")
```

### 13. News & Media Archives
```
"FirstName LastName" site:newspapers.com OR site:genealogybank.com
"FirstName LastName" (news OR article OR interview OR mention) -site:linkedin.com
"FirstName LastName" site:legacy.com (obituary OR memorial)
"Company Name" site:sec.gov/cgi-bin/browse-edgar
"FirstName LastName" (press release OR announcement) filetype:pdf
```

### 14. Own Domain Security Audit

Use these templates to check what your own domain is unintentionally
exposing via public search indexes. Substitute your own domain only.
```
site:yourdomain.com filetype:log
site:yourdomain.com filetype:env
site:yourdomain.com filetype:cfg OR filetype:conf
site:yourdomain.com filetype:bak OR filetype:backup
site:yourdomain.com inurl:config OR inurl:configuration
site:yourdomain.com filetype:sql
intitle:"index of" ".env" site:yourdomain.com
intext:"Index of /backup" site:yourdomain.com
site:yourdomain.com ext:pem OR ext:key -intitle:index.of
intext:"not for distribution" OR "confidential" filetype:pdf site:yourdomain.com
```

### 15. Public Webcam & Live Feeds

Use for finding publicly listed live streams, city webcams, and
broadcast feeds for research, journalism, or event monitoring.
```
site:earthcam.com "city name"
site:webcamtaxi.com "city name"
site:skylinewebcams.com "city name"
"live webcam" "city name" inurl:view
"city name" (webcam OR livecam OR "live cam" OR "live feed") -youtube
```

---

## Operator Quick Reference

| Operator | Example | Track |
|---|---|---|
| `site:` | `site:linkedin.com` | 1 |
| `inurl:` | `inurl:profile` | 1 |
| `intitle:` | `intitle:"index of"` | 1 |
| `intext:` | `intext:"annual report"` | 1 |
| `filetype:` / `ext:` | `filetype:pdf` | 1 |
| `"quotes"` | `"John Smith"` | 1 |
| `-` | `-site:twitter.com` | 1 |
| `OR` / `\|` | `site:x.com OR site:twitter.com` | 1 |
| `*` | `"John * Smith"` | 1 |
| `cache:` | `cache:site.com` | 2 only |
| `related:` | `related:site.com` | 2 only |
| `AROUND(n)` | `John AROUND(3) Smith` | 2 only |
| `before:` / `after:` | `before:2023-01-01` | 2 only |

---

## Extended Reference

For the full filtered query library (700+ entries across all categories),
read the companion file in this skill folder:
`dorks-reference.md`

Agents should read this file when:

* The curated templates above return insufficient results
* A niche platform or file type needs targeted discovery
* Building a comprehensive search sweep for a research task
