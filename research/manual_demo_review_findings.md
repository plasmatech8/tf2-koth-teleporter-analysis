# Manual demo review findings

These labels record the user's visual review of the SourceTV scenes. They are tactical interpretations, not facts inferred by the automated screen. SourceTV has no team voice comms; the user later supplied voice-call context from a separate recording for the Medic scene.

## Rapid-death and control scenes

| Demo / tick | Automated observation | Manual classification | Consequence or remaining uncertainty |
|---|---|---|---|
| 1485728 Product, 5601 | Demo used L1 and died 2.07 s later with no damage. | Clear use during a known reset; enemy Soldier was already near the exit. | Harmful misuse. The Demo lost the 1v1. The user estimates roughly four seconds of incremental regroup delay because Heavy was already due four seconds earlier; verify against the exact planned departure before treating four seconds as final. |
| 1489376 Ashville, 63522 | Heavy used L2 with all seven other non-Spy teammates near spawn and died 0.80 s later. | Clear known-reset use. Heavy had waited by the entrance and chose to take it. | Harmful outcome. A possible lobby-Soldier call could explain an intentional surprise attempt, so describe it as a bad gamble rather than proven confusion. |
| 1494495 Ashville, 58505 | Demo died 1.97 s after L1 use with no damage. | Likely attempted continuation or Medic rescue, rather than a clear misuse. Medic, Heavy and Pyro were still in or near lobby; any reset call appears late. | Exclude from confirmed rollout-misuse count. |
| 1469910 Product, 16645 | Heavy died 2.12 s after use but dealt 253 damage. | Ambiguous coordination. Several teammates remained forward; the Heavy waited for and used the tele, then traded with Pyro. | Do not count as clear misuse. The trade had value, although a full reset before the final 30 seconds may have been preferable. |
| 1485728 Product, 74880 | Engineer died 2.76 s after use with no damage. | Team was already moving to staging; Engineer used the exit about 2-3 seconds before the area was secured. | Reopening-timing error, not use during a closed reset. |
| 1486538 Product, 65430 | Engineer died 3.25 s after use and dealt 78 damage. Soldier used L2 at tick 65022, died at 65379 after jumping onto point alone, and Engineer used L3 at 65430. Medic and Heavy had recently respawned and were moving out. | Near-reset transition into a continued fight. Only Sniper was initially forward, but respawns produced even players or player advantage and the team moved out. Engineer used the route before the area was secure. | Premature and punished, but not a confirmed closed-reset misuse. The exact reset/continue call remains unknown. |
| 1494495 Ashville, 35921 | Demo survived about 122 s after a reset-like use. | Clear unsafe use during a known reset that happened to go unpunished. Sniper watched lobby and Soldier nearly killed him. | Shows why a death-only measure undercounts unsafe uses. |

### Separate active-fight reference

The Heavy-on-rock/Medic-beam scene belongs to **1485728 Product**, not the 1486538 event above. Engineer used L3 at tick **64995 / 16:14.92**; around tick **65190**, Heavy and Medic were holding rock. Engineer was sniped while running up at tick **65337**, 5.13 seconds after the ride. The audit marked the use as neither a strict nor broad reset candidate. This is an active-fight reference, not an automated false-positive screen.

## August 22 Ashville destruction scene

Demo 1496366, L3 destroyed at tick 98650.

- The destruction was caused by the reset policy.
- By tick 100000-100228, the team had settled on bats for a sac. The position-based reopening screen is tactically reasonable at that moment.
- The sac became a successful fight, followed by an apparent reset for an advantage Uber push.
- The earlier Heavy/Pyro overlap was likely useful. The recorded front had roughly one-player disadvantage; two earlier arrivals would have changed that local margin to roughly one-player advantage while the enemy pressured point. Their arrival timing was close to the decisive pressure.
- The later Sniper saving was not useful: the team rotated to bats, and the Sniper's walking arrival coincided with the team finishing that staging movement.
- The Engineer supported the intervening fight and died. He had no practical rebuild window until the next lobby reset unless he avoided that death.
- Near the final overtime attempt, an earlier Pyro could plausibly have added airblast and cap-time value, but that is a separate late return and should not be merged automatically with the earlier fight.

The raw route model's 33.93 p.s is therefore too broad to call observed useful combat presence. The Heavy/Pyro overlap of about 3.6-3.9 seconds is the clearest useful counterfactual. Other riders need their own tactical deadlines.

## September 6 Product scenes

- Tick 35978 destruction: no useful active-tele return was identified during the immediate sac/reset action. A later L2 could have helped separated Demo/Engineer returns and perhaps Sniper, but the recording does not show a missed decisive arrival.
- Tick 92367 destruction: the sac converted into a dry fight after the enemy Medic dropped. Engineer/Pyro could have returned sooner, but the team already controlled the space and won with little further fighting. Earlier Soldier/Demo returns would mainly add crit heals and insurance against a counter-sac that never occurred.
- Tick 114586 destruction: Scout/Demo could not have affected the final contest because the fight was already won before their possible arrival.
- Tick 64520 destruction: retained tele might have offered an alternate touch or distraction while the team was stuffed at the grass door, but it was unlikely to change the result. The Engineer was not expected to lead the contest.

## Newly supplied September 9 scenes

| Demo / tick | Automated observation | Manual classification or status |
|---|---|---|
| 1503848 Ashville, 125874 at 31:28.11 | Medic used L1 with three other non-Spy teammates near spawn and four dead; died 3.36 s later with no damage. | Clear premature use during preparation for a fast dry push. No reset was called: Medic intended to reunite on bats, mistook the remaining Pyro/front-line activity and teammates beginning to roll out as evidence that the route was secure, then immediately acknowledged the mistake. The death lost little charge but probably delayed the push by several seconds; the exact marginal delay is unresolved. |
| 1503854 Product, 51642 at 12:54.63 | Sniper used L1 during a strict positional screen with three others near spawn and two dead; survived 31.86 s. | Not manually reviewed. Exclude it from confirmed evidence rather than assume either misuse or safety. |

Lower-priority new rapid-death screens are 1503848 Ashville tick 27322 (Heavy, 3.18 s, 85 damage, broad screen only) and tick 105949 (Engineer, 4.05 s, no reset screen), plus 1503854 Product ticks 9346 (Sniper, 4.74 s) and 53649 (Engineer, 4.41 s). These should not be treated as reset mistakes without visual evidence.
