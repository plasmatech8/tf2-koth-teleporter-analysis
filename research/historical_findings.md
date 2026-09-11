# Historical teleporter findings

9 September 2026. Read this before the longer original report.

**The evidence supports both a real reinforcement benefit and a real, occasional rollout mistake. It does not establish which blanket policy wins more fights.**

Two corrections are now part of the analysis:

- **After-wipe rollout: zero permitted tele benefit.** Retention only becomes useful after ground is retaken. All cost scenarios below exclude respawns before the position-based reopening time.
- **Product round-three contest:** the Engineer expected the power classes to contest via concrete first and intended to follow. The upgrading sequence is not evidence that he should have led the contest, or that deleting the tele caused the loss. That case is withdrawn as a headline example.

## How often did the mistake happen?

I screened **46 recordings with active rounds**, containing **1,934 friendly uses of your teleporter**, from the directly linked May–September Product/Ashville demos, including the two newly supplied recordings. This is not every match since January: earlier entries mostly contain log links without direct demo links.

| Recorded quantity | Before Aug 18 | Aug 18 Ashville | After that match |
|---|---:|---:|---:|
| Recordings with active rounds | 33 | 1 | 12 |
| Active playing time, excluding recorded pauses | 11 h 27 min | 20 min | 4 h 21 min |
| Friendly tele uses, including Spy | 1,391 | 27 | 516 |
| Non-Spy tele uses | 1,315 | 24 | 487 |
| Uses flagged during regrouping/rollout | **39** | **2** | **3** |
| Flagged uses followed by death within 5 seconds | **5** | **1** | **1** |
| Flagged uses followed by death within 10 seconds | **8** | **1** | **1** |
| Your manually detonated exits | 1 | 0 | 48 |

The 5-second deaths are included in the 10-second total. “Flagged” means a reproducible position/death screen, **not a verified comms violation**. The screen requires a recent loss of at least five non-Spy players, at least three *other* non-Spy teammates near spawn, and at least five others near spawn or dead. Surviving Spies and isolated forward players do not automatically end the reset. Exact definitions and exclusions are in [the method](history_method.md); the tactical labels are in [the manual review findings](manual_demo_review_findings.md).

Manual review now gives a better answer than the raw screen. Among the six older rapid-death scenes, two were clear harmful uses during a known reset; one was a route used two or three seconds before staging was secured; one was an attempted Medic rescue; one was an ambiguous continuation that produced a useful trade; and one was a near-reset that became a continued fight, with a punished use before the route was secure. A seventh reviewed scene was a clear unsafe reset use that survived. The newer Medic scene was a third clear harmful or premature use during preparation for a fast dry push. The mistake was occasional, but a death-only count both overcounts false positives and misses unpunished unsafe uses.

The version-4 audit preserves a separate active-Medic context signal. Ten of the 44 strict positional screens occurred while another living Medic was moving away from spawn with a nearby teammate and recent combat was still occurring. This is a review flag, not an automatic acquittal: a prohibited after-wipe rollout can show the same pattern. Product demo 1486538 at tick 65430 receives that context flag. Here it reflects recently respawned players moving out after a near-reset turned into a continued fight; it does not by itself prove that the route was secure.

The separate Heavy-on-rock/Medic-beam scene is Product demo 1485728: Engineer used L3 at **tick 64995 / 16:14.92**, Heavy and Medic were visibly holding rock around tick **65190**, and Engineer was sniped while running up at tick **65337**, 5.13 seconds after the ride. The audit correctly treated this as neither a strict nor broad reset candidate. It should not be used to classify the August 1 tick 65430 event.

Across the pre-policy recordings, five flagged rapid deaths means roughly **one per 2 h 17 min of recorded play**. This is a descriptive frequency, not the probability of a mistake after a wipe. A denominator of all tele uses includes many perfectly ordinary defensive reinforcements.

## Specific incidents worth watching

All times are SourceTV demo times, not offsets into a separate POV video.

| Demo | Tele use | What the recording establishes |
|---|---|---|
| [July 30 Product](https://demos.tf/1485728) | **1:24.02**, tick 5601 | Demoman uses tele; three other non-Spy players near spawn and four dead. Dies to Soldier **2.07 s later**, with no damage dealt after teleporting. |
| [August 7 Ashville](https://demos.tf/1489376) | **15:52.83**, tick 63522 | Heavy uses tele while **all seven other non-Spy teammates are near spawn**. Enemy Heavy kills him **0.80 s later**. He deals 23 damage. This is the strongest clear positional example of going ahead of the reset. |
| [August 18 Ashville](https://demos.tf/1494495) | **14:37.57**, tick 58505 | Demoman uses tele; four other non-Spy teammates near spawn and two dead. Dies to enemy Demoman **1.97 s later**, dealing no damage. Enemy Demoman destroys the exit another 3.53 s later. |

The August 18 rapid-death scene was likely an attempted Medic rescue or continuation, rather than a clear reset misuse. The Demoman respawned at **14:52.38**, exactly alongside the already-dead Medic. His death-to-respawn absence was **12.84 seconds**, but **it did not extend the Medic's wait in spawn**.

The same match has an earlier flagged Demoman tele at **8:58.81** where he survives another **122 seconds**. Manual review identifies it as an unsafe reset use that happened to survive: Sniper watched lobby and Soldier nearly killed him. A misuse and a death are different counts.

The newly supplied Ashville demo adds a reviewed priority scene at **31:28.11 / tick 125874**: Medic uses L1 while most teammates are dead or only beginning to roll out, intends to reunite on bats for a fast dry push, immediately acknowledges the mistake, and dies 3.36 seconds later. The death loses little charge but probably delays the push by several seconds; the exact marginal delay remains unresolved. The Product demo adds a contrasting strict scene at **12:54.63 / tick 51642** where Sniper survives 31.86 seconds. That scene remains unclassified and is excluded from confirmed evidence.

There are **no recorded manual tele detonations by you in the August 18 Ashville demo**. That does not contradict a verbal instruction being given then; it means I cannot locate the policy switch by a detonation event in that recording. The next Product recording does contain detonations.

## How much reinforcement advantage was potentially lost?

The simple per-player number remains useful:

| One safe, unqueued Engineer-speed reinforcement | Product | Ashville main/shutter route |
|---|---:|---:|
| Approximate travel saving from tele | **5.4 s** | **6.4 s** |
| Extra presence if all that time is useful | **5.4 player-seconds** | **6.4 player-seconds** |

Those are based on your approximate route measurements plus a 0.6-second transfer allowance. Queueing reduces them. These are not precise measurements of combat contribution.

I also screened **all twelve post-policy recordings**, including **42 destructions of an operational connection**. The model starts considering respawns only after several non-Spy teammates have moved back up. It includes a shared queue and the walking alternative, and restricts classes to Engineer, Heavy, Pyro, Sniper and Medic; Scout, Soldier, Demo and Spy need different route/role treatment.

| Position-based reopening rule | Potential earlier arrivals while attacking | Potential extra player-seconds before capture |
|---|---:|---:|
| At least four teammates forward, maintained immediately before use | **13** | **~64** |
| At least three teammates forward, maintained immediately before use | **14** | **~70** |
| Reopen once four have moved up; assume exit stays usable afterward | 24 | ~114 |
| Reopen once three have moved up; assume exit stays usable afterward | 25 | ~120 |

**These are scenario results, not a measured loss of 61–67 seconds of actual player advantage, and not confidence bounds.** Positions do not prove exit safety or useful firing opportunities. Retained exits might be destroyed by the enemy. On the other hand, this model omits some classes, players already alive when ground is recovered, Engineer building costs and benefits continuing beyond observed restoration. The actual benefit can fall outside these figures in either direction.

The main scale suggested by this model is **roughly a dozen later reinforcement opportunities across twelve recordings**, not an advantage lost on every respawn after every wipe. Manual review shows that the position threshold can stay open across a later reset, route change or staging phase, so each ride needs its own tactical deadline before being called useful combat presence.

## A better deletion-cost example: August 22 Ashville

In [this demo](https://demos.tf/1496366), the level-3 connection was destroyed at **24:39.75**, tick 98650, and returned at **26:47.58**. The four-player ground-recovery screen becomes satisfied at **25:03.42**. Later respawns include:

| Class | Actual respawn | Modelled travel saving, with shared queue |
|---|---:|---:|
| Heavy | 26:07.02 | ~8.5 s |
| Pyro | 26:11.03 | ~6.2 s |
| Engineer | 26:19.04 | ~6.4 s |
| Sniper | 26:31.05 | ~6.4 s |

These four returns contribute **~27.5 potential player-seconds** in the model. An earlier Pyro return in the same gap brings the case total to **~34**. The enemy connection was operational at all four listed respawns, though it was level 1 and therefore had a much longer queue cycle.

Manual review narrows that raw total. The Heavy/Pyro overlap was probably useful: the recorded front was roughly -1 during enemy pressure, and two earlier arrivals would have changed it to roughly +1 for about **3.6-3.9 seconds**. The later Sniper saving was not useful because the team changed route to bats and his walking arrival coincided with the team's staging. The ~34 p·s figure should therefore remain a candidate-screen total, not a claim of ~34 useful combat player-seconds.

There is also actual position evidence: Heavy reached the map's `y = 1000` line **15.36 seconds after spawning**. Pyro crossed it in **9.68 seconds**. This difference is why Engineer-speed timings should not be treated as exact timings for every class. The line is a reproducible location, not a definition of when combat starts. The Engineer dealt damage immediately after respawning through a surviving sentry, so “first damage after spawn” cannot measure his personal arrival.

## What I would conclude

1. **Your mechanical argument is sound:** after safe ground recovery, losing a 5–6-second travel saving can consume most of the attacker's average return-time lead.
2. **“It hardly ever happens, if at all” needs narrowing:** it is uncommon across the full history, but there are repeated, concrete regrouping tele deaths.
3. **My earlier deletion-cost examples were too broad for your rollout rule.** A rebuilding gap overlapping a push does not establish useful reinforcements were lost. The August 22 sequence is better evidence.
4. **The data do not establish a fight-win percentage or prove either blanket policy optimal.** A retained player might miss, die immediately, protect Medic, or secure the point. The demos contain only the action actually taken.

The strongest policy argument is to preserve a surviving exit **when it has a realistic use after ground recovery**, with a clear closed/open call. The strongest argument for deletion is a specific reset where an unwanted use could disrupt the next action and the exit has little likely value afterward. These recordings give examples on both sides; they do not support treating every wipe as equally expensive or every retained tele as harmless.

For judging one fight, write the result as **“player X could return about Y seconds earlier, during this particular window.”** Add those seconds across players to measure presence. Do not translate them into “Y% more likely to win,” or add earlier arrival, uptime and extra lives as separate benefits.

Full [tele-use table](history/tele_uses.csv), [candidate incidents](history/candidates.csv), [cost scenarios](history/cost_scenarios.json), and [verification results](history/verification.json) are retained for review.
