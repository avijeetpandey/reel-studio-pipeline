# Idea scorecard — the gate before any filming (28 Nov 2026)

Source: a study of about 2,600 tech Shorts from 43 creators, 25 outliers studied frame by frame, plus 80 lifestyle reels).
Finding: pure "X explained" is the weakest family everywhere, even at ByteByteGo and Gaurav Sen. Outliers carry at least one **engine**.

Score the idea (the creator's pasted script, or a topic from `scan:` / `trends:`) on five criteria, 0–2 each. **Pass = 7 of 10 and an engine above 0.**
Record it with `pipeline.py idea <reel> engine=… send=… frame0=… hook=… twist=… --engines stakes,conflict`.
The pipeline never rewrites the creator's script: below 7, checkpoint 1 shows the score and **3 hook rewrites as suggestions**; the creator rewrites, or says "film anyway" (`--override`, recorded, so the weekly review can show whether overrides pay off).

## 1. engine (0–2): what makes a stranger care
| Engine | Looks like | Example (views) |
|---|---|---|
| `stakes` | money lost or made, a bill, an outage, a salary | "The database query that cost $1,000,000" (0.8M, 13× median) |
| `conflict` | two people, a debate, X vs Y, a ranking, "company dropped X" | "Facebook dropped REST?" · Arjay's two-person system design (0.6M) |
| `mirror` | the viewer sees their own job / life | "Interns on their first day be like…" (15.9M) · "What I did last week as a senior engineer" (258K likes) |
| `wrong_thing` | a visibly broken or surprising thing | "0.1 + 0.2 = 0.30000000004" (8.8M) · "Swiggy said delivered, food still at the restaurant" |
| `insider` | transgression or a secret: "how we really do it", "unethical" | "A very unethical resume hack" (6.7M, 287×) · Joma's "how we review code in big tech" (17M) |
| `receipts` | your own numbers, journey, mistakes | "How much money I made as a developer" (0.5M) · "Coding every day for 365 days" (0.4M) |
| `challenge` | a game, quiz, bet, "guess which" | "For $700, explain compilers" (7.2M, 254×) |
0 = none (a topic: "Kafka explained"); 1 = one engine, mild; 2 = one strong engine or two stacked.

## 2. send (0–2): who would forward it, and why
Write the person: "the friend who…", "my team lead", "the batchmate preparing for interviews". 0 = nobody specific; 1 = "developers"; 2 = a named person + a reason ("to win an argument", "this is us").

## 3. frame0 (0–2): a real thing or a person mid-reaction, on mute
0 = a title card, a generated scene, a cartoon on a background, or a seated face with small captions; 1 = face + a big claim; 2 = the stake itself on screen (a real screen, a bill, an app showing the bug, a second person, a street, the dog) **+** face. Never a generated background as the only image.

## 4. hook (0–2): the first line names the stake in ≤ 2 s, in plain words
0 = "X kya hai?" / "X kaise kaam karta hai?"; 1 = a claim; 2 = a scene or tension word ("par", "phir bhi", "kyun nahi") + the stake.

## 5. twist (0–2): one line a viewer would repeat to a friend
0 = none; 1 = a fact; 2 = a reversal ("they went *back* to a monolith and saved 90%").

## Pillar mix (per 10 reels)
5 × **tech with stakes** (decisions, outages, costs, interview traps) · 3 × **engineer life and career receipts** · 2 × **life as the setting** (the dog as a recurring character, a ride + chai-stop explainer, WFH reality). Lifestyle without a shared feeling (plain diary, trip vlog) scored tens to hundreds of likes in every search: it must still pass this card.

## Before posting: honesty check
The answer to the hook lands before 25 s · every number is real and sourced · the cover promises what the first 3 s say · no fear or shame · say "usually" when it is usually · corrections go in the pinned comment.
