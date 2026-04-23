---
name: dog-training-video
version: 1.0.3
displayName: "Dog Training Video Maker"
description: >
  Describe your dog training content and NemoVideo creates the video. Basic obedience, trick training, behavior modification, puppy foundations, leash reactivity, recall training — narrate the dog, the goal, the method, and the training progression, and get a dog training video that other owners can actually follow and replicate.

  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM.
homepage: https://nemovideo.com
apiDomain: https://mega-api-prod.nemovideo.ai
repository: https://github.com/nemovideo/nemovideo_skills
license: MIT-0
metadata:
  requires:
    env: ["NEMO_TOKEN"]
    configPaths:
      - "~/.config/nemovideo/"
  primaryEnv: NEMO_TOKEN
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> 📹 Ready to dog training video! Just send me a video or describe your project.

**Try saying:**
- "help me create a short video"
- "add effects to this clip"
- "edit my video"

**IMPORTANT**: Always greet the user proactively on first contact. Let them know you're setting up while connecting. Always greet the user proactively on first contact.

### Auto-Setup

When the user first interacts, set up the connection:

1. **Check token**: If `NEMO_TOKEN` env var is set, use it. Otherwise:
2. **Read or generate Client-ID**:
   - Read `~/.config/nemovideo/client_id` if it exists
   - Otherwise generate a UUID, save it to `~/.config/nemovideo/client_id`
3. **Acquire anonymous token**:
   ```bash
   curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

Let the user know briefly: "Setting things up… ready!" then proceed with their request.


# Dog Training Video Maker — Create Obedience, Trick, and Behavior Training Content

Describe your dog training content and NemoVideo creates the video. Basic obedience, trick training, behavior modification, puppy foundations, leash reactivity, recall training — narrate the dog, the goal, the method, and the training progression, and get a dog training video that other owners can actually follow and replicate.

## When to Use This Skill

Use this skill for dog training and canine behavior content:
- Create step-by-step obedience training tutorial videos (sit, stay, down, come, heel)
- Film trick training progression content showing sessions over days or weeks
- Build behavior modification tutorials for specific problems (leash reactivity, jumping, resource guarding)
- Document puppy foundation training for new dog owners
- Create positive reinforcement training educational content
- Produce dog sport training content (agility, nosework, competition obedience)

## How to Describe Your Dog Training Content

Be specific about the dog, the behavior goal, the training method, and the key progression moments.

**Examples of good prompts:**
- "Teaching 'place' command to an 8-month-old rescue lab mix who has zero impulse control: The 'place' command (go to your mat and stay there until released) is the behavior that changes everything for a reactive dog — it gives them a job when they would otherwise bark or jump. Training progression: (1) lure onto mat with treat, reward for any foot contact, (2) add 'place' verbal cue when dog moves toward mat, (3) extend duration from 2 seconds to 30 seconds over 3 sessions, (4) add distractions slowly (food on floor 6 feet away). Show the first session where he keeps hopping off and the fifth session where he holds it for 90 seconds while the doorbell rings."
- "Perfect recall training in 4 steps: The most important behavior any dog can know, and the one most owners train incorrectly (they call 'come' when the fun ends — then wonder why the dog stops coming). The 4 steps: (1) make coming to you the best thing that ever happens — explosive reward every single time, (2) never punish a dog that comes to you even if it took 10 minutes, (3) use a different cue word for emergencies ('here' or 'to me'), (4) practice in increasingly distracting environments before you need it. Show the backyard recall, then park recall, then off-leash trail recall."
- "Leash reactivity: what it is and the protocol that actually works: This is not aggression — explain the difference. The Look at That (LAT) protocol: (1) dog sees trigger at threshold distance, (2) dog looks at trigger, (3) owner marks and rewards (the marker bridges the dog looking at the trigger to getting a treat — eventually the trigger becomes a cue to look at you). Show the progression from threshold distance over 6 weeks until the dog can pass another dog on a sidewalk."

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `training_type` | Behavior category | `"obedience"`, `"tricks"`, `"behavior_mod"`, `"puppy"`, `"sport"`, `"recall"` |
| `dog_profile` | Dog description | `"8-month rescue lab mix"`, `"2-year reactive border collie"` |
| `target_behavior` | What you're teaching | `"place command"`, `"perfect recall"`, `"loose leash walking"` |
| `training_method` | Approach | `"positive_reinforcement"`, `"marker_training"`, `"lure_reward"` |
| `progression_sessions` | Training arc | `"1 session"`, `"over 4 weeks"`, `"6-session series"` |
| `show_mistakes` | Include failures | `true` |
| `skill_level` | Owner experience | `"beginner"`, `"intermediate"`, `"advanced"` |
| `duration_minutes` | Video length | `5`, `8`, `12` |
| `platform` | Distribution | `"youtube"`, `"tiktok"`, `"instagram"` |

## Workflow

1. Describe the dog, the behavior goal, the training method, and the key sessions
2. NemoVideo structures the training narrative with clear progression markers
3. Step labels, session numbers, and technique callouts added automatically
4. Export with tutorial pacing suited to training content

## API Usage

### Obedience Training Tutorial

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "dog-training-video",
    "input": {
      "prompt": "Teaching loose leash walking to a 3-year-old golden retriever who has never been trained to walk on leash — she pulls like a sled dog. The method: stop-and-wait (any tension on the leash = stop, forward movement only when leash is loose). Why this works: dogs pull because pulling has always worked (they got to go where they wanted). Step 1: walk 10 feet without pulling, treat. Step 2: extend to 30 feet. Step 3: add real-world environments (mailboxes, other dogs at distance). Show day 1 (frustrating, 15 minutes to walk 50 feet) and day 14 (loose leash through the park). The transformation is the content.",
      "training_type": "obedience",
      "dog_profile": "3-year-old golden retriever, no prior training",
      "target_behavior": "loose leash walking",
      "training_method": "positive_reinforcement",
      "progression_sessions": "over 2 weeks",
      "show_mistakes": true,
      "skill_level": "beginner",
      "duration_minutes": 10,
      "platform": "youtube",
      "hashtags": ["DogTraining", "LeashTraining", "GoldenRetriever", "PositiveReinforcement", "DogObedience"]
    }
  }'
```

**Response:**
```json
{
  "job_id": "dogtraining_abc123",
  "status": "processing",
  "estimated_seconds": 100,
  "poll_url": "https://mega-api-prod.nemovideo.ai/v1/jobs/dogtraining_abc123"
}
```

## Tips for Best Results

- **Explain the why before the how**: "Dogs pull because pulling has always worked" or "never call 'come' when the fun ends — that's why recall breaks down" — the behavioral science behind training is what separates good training content from bad
- **Show the real early sessions**: "Day 1: 15 minutes to walk 50 feet" — the frustrating early sessions are what gives the later success its meaning and what nervous owners need to see before they give up
- **Name the method**: "Look at That protocol" or "stop-and-wait method" — naming the technique makes the content searchable and lets owners look up more resources
- **The dog's context matters**: "Rescue lab mix who has zero impulse control" or "never been trained" — describing the dog's baseline helps viewers assess whether this content applies to their situation
- **Progression across sessions is the genre**: Dog training content works best as a series (session 1 → session 5 → session 10) showing real progress over time rather than a single polished demonstration

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| YouTube | 1920×1080 | 8–15 min |
| TikTok | 1080×1920 | 60–180s |
| Instagram Reels | 1080×1920 | 60–90s |

## Related Skills

- `puppy-video-maker` — Foundation puppy training content
- `pet-vlog-maker` — Dog life and daily routine content
- `pet-care-video-maker` — General pet care education

## Common Questions

**Do I need professional trainer credentials to make dog training content?**
No — personal experience training your own dogs is valid and often more relatable than professional content. Be clear about your background ("I'm not a professional trainer, this is what worked for my dog") and viewers will trust it appropriately.

**How do I show a multi-week training progression?**
Set `progression_sessions: "over X weeks"` and describe key sessions in the prompt. NemoVideo structures a time-lapse narrative showing early struggles through final success.

**What's the most searched dog training content?**
Recall, leash pulling, and separation anxiety are the top search topics. Breed-specific content (golden retriever, lab, border collie) drives strong search traffic from owners of those breeds.
