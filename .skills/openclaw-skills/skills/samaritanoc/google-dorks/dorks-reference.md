# Precision Web Search — Extended Query Library

Filtered and categorized from: Sundowndev, clarketm/stevenswafford, TUXCMD
Excluded: SQLi, LFI, RFI, XSS, parameter fuzzing, CMS exploits, warez, dead platforms,
credential harvesting, device targeting, breach/paste discovery
Purpose: Research, journalism, due diligence, document discovery, public records,
professional verification, academic work, corporate research

---

## OPERATOR REFERENCE

| Filter | Description |
|---|---|
| `allintext:` | All keywords in body text |
| `intext:` | Keyword in body text |
| `inurl:` | Keyword in URL |
| `allinurl:` | All keywords in URL |
| `intitle:` | Keyword in page title |
| `allintitle:` | All keywords in page title |
| `site:` | Restrict to domain |
| `filetype:` | File extension filter |
| `link:` | Pages linking to URL |
| `before:` / `after:` | Date range (YYYY-MM-DD) — Track 2 |
| `related:` | Similar pages — Track 2 |
| `cache:` | Google cached version — Track 2 |
| `inanchor:` | Keyword in anchor text |
| `AROUND(n)` | Proximity operator — Track 2 |

---

## SECTION 1 — IDENTITY & PEOPLE SEARCH

### People Search Aggregators
"FirstName LastName" site:whitepages.com
"FirstName LastName" site:spokeo.com
"FirstName LastName" site:beenverified.com
"FirstName LastName" site:intelius.com
"FirstName LastName" site:peoplefinder.com
"FirstName LastName" site:radaris.com
"FirstName LastName" site:fastpeoplesearch.com
"FirstName LastName" site:truepeoplesearch.com
"FirstName LastName" site:411.com
"FirstName LastName" site:anywho.com
"FirstName LastName" site:zabasearch.com
"FirstName LastName" site:pipl.com
"FirstName LastName" site:peekyou.com
"FirstName LastName" site:addresses.com
"FirstName LastName" site:addresssearch.com
"FirstName LastName" site:usphonebook.com
"FirstName LastName" site:smartbackgroundchecks.com
"FirstName LastName" site:publicrecords.com

### Death, Genealogy & Historical Records
"FirstName LastName" site:legacy.com
"FirstName LastName" site:findagrave.com
"FirstName LastName" site:ancestry.com
"FirstName LastName" site:familytreenow.com
"FirstName LastName" site:classmates.com
"FirstName LastName" (obituary OR memorial OR "passed away")
"FirstName LastName" site:newspapers.com (obituary)

### Voter & Political Records
"FirstName LastName" site:voterrecords.com
"FirstName LastName" (voter OR "registered voter" OR "party affiliation")
"FirstName LastName" site:followthemoney.org
"FirstName LastName" site:fec.gov
"FirstName LastName" site:opensecrets.org (donor OR contribution)

---

## SECTION 2 — SOCIAL MEDIA & PLATFORMS

### Major Platforms
"FirstName LastName" site:linkedin.com
"FirstName LastName" site:twitter.com
"FirstName LastName" site:x.com
"FirstName LastName" site:facebook.com
"FirstName LastName" site:instagram.com
"FirstName LastName" site:tiktok.com
"FirstName LastName" site:reddit.com
"FirstName LastName" site:youtube.com
"FirstName LastName" site:pinterest.com
"FirstName LastName" site:snapchat.com

### Blogs & Publishing
"FirstName LastName" site:medium.com
"FirstName LastName" site:substack.com
"FirstName LastName" site:wordpress.com
"FirstName LastName" site:blogger.com
"FirstName LastName" site:tumblr.com
"FirstName LastName" site:ghost.io
"FirstName LastName" site:livejournal.com

### Creator & Portfolio Platforms
"FirstName LastName" site:patreon.com
"FirstName LastName" site:ko-fi.com
"FirstName LastName" site:buymeacoffee.com
"FirstName LastName" site:deviantart.com
"FirstName LastName" site:artstation.com
"FirstName LastName" site:behance.net
"FirstName LastName" site:dribbble.com
"FirstName LastName" site:500px.com
"FirstName LastName" site:flickr.com

### Developer & Tech
"username" site:github.com
"username" site:gitlab.com
"username" site:bitbucket.org
"username" site:stackoverflow.com
"username" site:news.ycombinator.com
"FirstName LastName" site:producthunt.com
"FirstName LastName" site:devpost.com

### Music & Entertainment
"username" site:soundcloud.com
"username" site:bandcamp.com
"username" site:last.fm
"username" site:spotify.com
"username" site:rateyourmusic.com
"username" site:letterboxd.com
"username" site:goodreads.com
"username" site:twitch.tv
"username" site:kick.com

### Gaming & Hobbies
"username" site:steamcommunity.com
"username" site:chess.com
"username" site:lichess.org
"username" site:boardgamegeek.com
"username" site:myanimelist.net
"username" site:anilist.co

### Dating Platforms
"username" site:pof.com
"username" site:match.com
"username" site:okcupid.com
"username" site:zoosk.com
"username" site:eharmony.com
"username" site:hinge.co
"username" site:bumble.com
"username" site:tinder.com
"FirstName LastName" inurl:profile (site:pof.com OR site:okcupid.com OR site:match.com)

### Link Aggregators & Identity Hubs
"FirstName LastName" site:about.me
"FirstName LastName" site:linktr.ee
"FirstName LastName" site:bento.me
"FirstName LastName" site:carrd.co
"FirstName LastName" site:bio.link
"FirstName LastName" site:manylink.co

---

## SECTION 3 — VIDEO, PODCAST, WEBINAR & CONFERENCE

### Video Platforms
"FirstName LastName" site:youtube.com
"FirstName LastName" site:vimeo.com
"FirstName LastName" site:rumble.com
"FirstName LastName" site:odysee.com
"FirstName LastName" site:dailymotion.com
"FirstName LastName" (interview OR appearance OR speech OR talk) site:youtube.com
"FirstName LastName" inurl:watch site:youtube.com
"FirstName LastName" site:ted.com
"FirstName LastName" inurl:tedx site:youtube.com
"Company Name" (earnings call OR investor day OR analyst day) site:youtube.com
"FirstName LastName" site:c-span.org

### Podcast Platforms
"FirstName LastName" site:podcasts.apple.com
"FirstName LastName" site:open.spotify.com/episode
"FirstName LastName" site:podchaser.com
"FirstName LastName" site:listennotes.com
"FirstName LastName" site:buzzsprout.com
"FirstName LastName" site:anchor.fm
"FirstName LastName" site:podbean.com
"FirstName LastName" site:transistor.fm
"FirstName LastName" site:simplecast.com
"FirstName LastName" (guest OR interviewed OR featured) (podcast OR show OR episode)
"FirstName LastName" (podcast OR episode OR interview) filetype:mp3

### Webinars & Live Events
"FirstName LastName" site:eventbrite.com
"FirstName LastName" (webinar OR online event OR virtual summit) site:youtube.com
"FirstName LastName" site:crowdcast.io
"FirstName LastName" site:loom.com
"FirstName LastName" site:zoom.us (recording OR webinar)
"FirstName LastName" site:hopin.com OR site:airmeet.com
"FirstName LastName" site:linkedin.com/events
"FirstName LastName" (webinar OR virtual event OR online summit) (recording OR replay OR archive)

### Conference & Speaking
"FirstName LastName" (keynote OR speaker OR panelist OR presenter OR moderator)
"FirstName LastName" site:slideshare.net
"FirstName LastName" site:speakerdeck.com
"FirstName LastName" site:speakerhub.com
"FirstName LastName" site:sessionize.com
"FirstName LastName" (conference OR summit OR symposium OR forum) (speaker OR presenter OR panelist)
"FirstName LastName" (slides OR deck OR presentation) filetype:pdf (conference OR summit)
"FirstName LastName" inurl:speaker (conference OR summit OR event)
"FirstName LastName" (talk OR lecture OR workshop) site:youtube.com OR site:vimeo.com
"FirstName LastName" (bio OR biography) (speaker OR presenter) (conference OR summit)

---

## SECTION 4 — COURT, LEGAL & LEGISLATIVE RECORDINGS

### Court Records & Filings
"FirstName LastName" site:courtlistener.com
"FirstName LastName" site:pacer.gov
"FirstName LastName" site:unicourt.com
"FirstName LastName" site:judyrecords.com
"FirstName LastName" site:docketalarm.com
"FirstName LastName" (plaintiff OR defendant OR petitioner OR respondent)
"FirstName LastName" (lawsuit OR litigation OR settlement OR judgment OR lien)
"FirstName LastName" (arrested OR charged OR indicted OR convicted OR sentenced)
"FirstName LastName" (criminal OR civil OR bankruptcy OR probate OR divorce) filetype:pdf
"Company Name" site:courtlistener.com
"Company Name" (lawsuit OR suit OR complaint OR class action)
"FirstName LastName" (restraining order OR protective order OR TRO)

### Court Hearing Recordings
"FirstName LastName" (trial OR hearing OR proceeding OR deposition) site:youtube.com
"FirstName LastName" site:lawandcrime.com
"FirstName LastName" site:courttv.com
"FirstName LastName" (trial recording OR court video) site:youtube.com
"FirstName LastName" site:archive.org (hearing OR trial OR proceeding)
"Company Name" (trial OR hearing OR proceeding) site:youtube.com

### Congressional & Federal Legislative
"FirstName LastName" site:c-span.org
"FirstName LastName" (testimony OR statement) site:c-span.org
"FirstName LastName" site:congress.gov (hearing OR testimony OR committee)
"FirstName LastName" (congressional testimony OR senate hearing OR house hearing)
"FirstName LastName" (committee hearing OR subcommittee hearing) site:youtube.com
"FirstName LastName" (congressional testimony OR committee appearance) filetype:pdf
"Company Name" (congressional hearing OR committee testimony) site:c-span.org
"Company Name" (congressional hearing OR senate OR house committee) site:youtube.com

### State & Local Legislative
"FirstName LastName" (state legislature OR state assembly OR state senate) (testimony OR hearing)
"FirstName LastName" (city council OR county commission OR board of supervisors) site:youtube.com
"FirstName LastName" (city council OR county commission OR zoning board) (testimony OR statement)
"FirstName LastName" (public comment OR public hearing) site:youtube.com
"Company Name" (city council OR county OR municipal) (hearing OR approval OR permit) site:youtube.com

### Administrative & Regulatory Proceedings
"FirstName LastName" (FTC OR SEC OR FDA OR NLRB OR EEOC) (hearing OR proceeding OR testimony)
"FirstName LastName" site:regulations.gov (comment OR testimony OR submission)
"Company Name" (FTC OR SEC OR FDA OR NLRB) (hearing OR proceeding) site:youtube.com
"FirstName LastName" (administrative hearing OR regulatory proceeding) filetype:pdf
"Company Name" site:ftc.gov (complaint OR consent order OR hearing)
"Company Name" site:sec.gov (hearing OR proceeding OR order)

---

## SECTION 5 — DOCUMENT & FILE DISCOVERY

### General Documents
"FirstName LastName" filetype:pdf
"Company Name" filetype:pdf
"FirstName LastName" filetype:doc OR filetype:docx
"Company Name" filetype:xls OR filetype:xlsx
"Company Name" filetype:csv
"FirstName LastName" filetype:ppt OR filetype:pptx
site:domain.com ext:(pdf | doc | xls | txt | csv | ppt)
intitle:"index of" (pdf OR xls OR doc OR csv) "subject name"

### Resumes & Professional Bios
"FirstName LastName" (resume OR CV OR "curriculum vitae") filetype:pdf
"FirstName LastName" (bio OR biography OR profile) filetype:pdf
"FirstName LastName" inurl:resume filetype:pdf

### Government & Regulatory Documents
"FirstName LastName" filetype:pdf site:gov
"Company Name" filetype:pdf site:gov
"FirstName LastName" site:regulations.gov
"Company Name" site:govinfo.gov
"Company Name" site:ftc.gov (complaint OR order OR settlement)
"Company Name" site:cfpb.gov
"Company Name" site:osha.gov
"FirstName LastName" site:hhs.gov OR site:cms.gov

### Financial & SEC Filings
"Company Name" site:sec.gov
"FirstName LastName" site:sec.gov (insider OR director OR officer)
"Company Name" site:sec.gov (10-K OR 10-Q OR 8-K OR proxy)
"Company Name" filetype:pdf (annual report OR quarterly report)
"FirstName LastName" site:finra.org
"FirstName LastName" site:brokercheck.finra.org
"Company Name" site:fdic.gov OR site:occ.gov

### Nonprofit & Tax Records
"Organization Name" 990 filetype:pdf site:guidestar.org
"Organization Name" site:propublica.org/nonprofits
"Organization Name" 990 filetype:pdf site:irs.gov
"FirstName LastName" (trustee OR director OR officer) site:guidestar.org

---

## SECTION 6 — CORPORATE & BUSINESS INTEL

### Registration & Corporate Records
"Company Name" site:opencorporates.com
"Company Name" site:bizapedia.com
"Company Name" site:corporationwiki.com
"Company Name" site:dnb.com
"Company Name" site:manta.com
"Company Name" site:businesswire.com OR site:prnewswire.com
"FirstName LastName" (CEO OR CFO OR COO OR CTO OR director OR founder) site:linkedin.com

### Competitive & Market Intelligence
"Company Name" site:glassdoor.com
"Company Name" site:crunchbase.com
"Company Name" site:pitchbook.com
"Company Name" (funding OR investment OR acquisition OR merger OR IPO)
"Company Name" site:owler.com
"Company Name" site:zoominfo.com
"Company Name" (patent OR trademark) site:patents.google.com
"Company Name" site:similarweb.com

---

## SECTION 7 — EMAIL & CONTACT DISCOVERY
"firstname.lastname@domain.com"
"@domain.com" "FirstName LastName"
"@domain.com" filetype:pdf
"@domain.com" filetype:xlsx OR filetype:csv
intext:"@domain.com" inurl:contact OR inurl:staff OR inurl:team
"FirstName LastName" "email" -site:linkedin.com filetype:pdf
"@gmail.com" "FirstName LastName" filetype:pdf
site:domain.com intext:email filetype:txt
intitle:"index of" filetype:xls inurl:email
"contact" "email" "FirstName LastName" -site:linkedin.com
intext:"mailto:" "FirstName LastName" site:domain.com

---

## SECTION 8 — OWN DOMAIN SECURITY AUDIT

Use these queries against your own domain only to identify
unintentionally exposed files in public search indexes.

### Config & Environment Files
site:yourdomain.com filetype:env
site:yourdomain.com filetype:cfg OR filetype:conf
site:yourdomain.com filetype:ini
site:yourdomain.com inurl:config
intitle:"index of" ".env" site:yourdomain.com

### Backup & Log Files
site:yourdomain.com filetype:log
site:yourdomain.com filetype:bak OR filetype:backup
site:yourdomain.com inurl:backup
intitle:"index of" ".log" site:yourdomain.com

### Database Files
site:yourdomain.com filetype:sql
intext:"phpMyAdmin" "running on" inurl:"main.php"

### Exposed Keys & Certificates
site:yourdomain.com ext:pem
site:yourdomain.com ext:key

### Sensitive Documents
intext:"not for distribution" OR "confidential" filetype:pdf site:yourdomain.com
intext:"Index of /backup" site:yourdomain.com

---

## SECTION 9 — CACHED & ARCHIVED CONTENT
cache:url.com (Track 2 only)
"FirstName LastName" site:web.archive.org
"username" site:web.archive.org
site:web.archive.org "domain.com"
site:cachedview.nl "subject"
"FirstName LastName" site:archive.ph OR site:archive.today
site:archive.ph "domain.com"
related:domain.com (Track 2 only)

---

## SECTION 10 — PHONE & ADDRESS
"555-555-5555" (name OR address OR owner OR carrier)
"FirstName LastName" site:whitepages.com (phone OR address)
"FirstName LastName" site:411.com
"FirstName LastName" site:yellowpages.com
"555-555-5555" site:truecaller.com
"555-555-5555" (reverse lookup OR carrier OR owner)
"FirstName LastName" (moved OR relocated OR "forwarding address")

---

## SECTION 11 — PUBLIC WEBCAM & LIVE FEEDS

Publicly listed broadcast feeds for research, journalism, or event monitoring.
site:earthcam.com "city name"
site:webcamtaxi.com "city name"
site:skylinewebcams.com "city name"
"live webcam" "city name" inurl:view
"city name" (webcam OR livecam OR "live cam" OR "live feed") -youtube

---

## SECTION 12 — ADVANCED COMBINATION SWEEPS

### Identity Sweep
"FirstName LastName" (site:twitter.com OR site:x.com OR site:instagram.com OR site:facebook.com OR site:tiktok.com OR site:linkedin.com)
"username" (site:reddit.com OR site:github.com OR site:twitter.com OR site:instagram.com)

### Video & Media Sweep
"FirstName LastName" (site:youtube.com OR site:vimeo.com OR site:c-span.org OR site:ted.com)
"FirstName LastName" (site:podchaser.com OR site:listennotes.com OR site:podcasts.apple.com)
"FirstName LastName" (keynote OR speaker OR panelist OR presenter) (site:slideshare.net OR site:speakerdeck.com OR site:sessionize.com)

### Court & Legislative Sweep
"FirstName LastName" (site:courtlistener.com OR site:unicourt.com OR site:judyrecords.com OR site:pacer.gov)
"FirstName LastName" (testimony OR hearing OR proceeding) (site:c-span.org OR site:congress.gov OR site:youtube.com)
"FirstName LastName" (lawsuit OR arrested OR charged OR convicted OR bankrupt OR lien OR judgment)

### Document Sweep
"FirstName LastName" (filetype:pdf OR filetype:doc OR filetype:xls) (resume OR bio OR profile OR contract)
site:domain.com ext:(pdf | xls | csv | doc | txt)

### Own Domain Audit Sweep
site:yourdomain.com (inurl:backup OR inurl:config)
site:yourdomain.com (filetype:log OR filetype:sql OR filetype:env OR filetype:bak OR filetype:cfg)
