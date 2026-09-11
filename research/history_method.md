# Historical audit method and limits

## Coverage and reproducibility

The local download step used direct demos.tf links from the private match archive, retrieved demos.tf API metadata, checked the actual map, and ran the Rust extractor. Two separately supplied demos were then added directly to the local manifest. There are 48 listed IDs. ID 1492212 actually identifies Upward and was excluded. ID 1489380 parsed but has no active round and was excluded from play-time/incident denominators. The supplied September 6 Product recording was reused after its repeat download timed out. In total, 47 KOTH files parsed, 46 contributed active rounds.

Some recordings are parts of the same match. The unit in the tables is a recording, not necessarily a distinct scrim. No January–April demos were located through log-only entries. Metadata, originals and raw extracted snapshots/events are in `history/`.

The Engineer is identified by a locally supplied Steam3 account ID, set through the `TF2_ENGINEER_STEAM_ID` environment variable. The identifier itself is intentionally omitted from the public repository. User IDs and team colours are looked up separately in every recording. Opponent uses of the same network are excluded from friendly counts: nine such events were found and accounted for during verification.

`history_audit.mjs` reads event ticks and approximately 0.24-second position/building snapshots. Demo time is tick × 0.015. Recorded pause intervals are removed from active playing duration and death-delay measurements. Each `teamplay_round_active` is paired with its first subsequent round win; bonus/admin wins without a new active round are not counted as extra overlapping rounds.

`history_verify.mjs` checks death-event totals against the parser's independent summary, accounts for every friendly/opponent tele event on this network in active rounds, checks non-overlapping round intervals and incident consistency. All 45 parsed KOTH files passed.

## Incident screen

Actual spawn events provide median spawn centres for each team. A player's horizontal location is projected onto the line joining the two spawn centres: 0 means own spawn, 0.5 roughly the map midpoint, 1 enemy spawn. This coordinate is not a route distance or visibility test.

A reset episode starts after at least five non-Spy roles are dead, at least 20 seconds into an active round, with at least seven non-Spy roles represented. It ends when three non-Spy players move at least 35% across the map, or expires after prolonged inactivity. An isolated survivor or Spy alone cannot end it.

A strict candidate is an actual non-Spy use of this Engineer's tele:

- During a recent reset episode, within 45 seconds of the last low-alive state.
- With at least three other living non-Spy teammates near spawn. “Near” is less than 20% across the map or within 600 units of the entrance.
- With at least five other non-Spy teammates near spawn or dead in total.

This screen includes walking rollouts as well as stationary regrouping. It does not infer a spoken “do not tele” call. Hiding players can remain forward without invalidating the screen. It can still misclassify intentional sacrifices, rescues or last contests. It can miss smaller resets, errors after the spatial reset has ended, or unusual positions.

Version 4 also records an **active-Medic context signal** without rewriting the raw strict/broad screen. It checks whether another living Medic is outside the immediate spawn centre, moving away from spawn over the preceding 1.5 seconds, close to another living non-Spy teammate, and accompanied by recent friendly combat. This signal identifies scenes that deserve an active-fight qualification; it is not proof that the route was safe. An after-wipe rollout can also contain a Medic moving forward, so the raw candidate and the context signal are retained separately for audit and manual classification.

The broader screen drops the requirement for three other living teammates near spawn. Before the policy it flags 135 uses, including 17 deaths within five seconds, versus the stricter 39 uses and five deaths. The broad results include legitimate desperate contests and are not all mistakes. Across every non-Spy tele use before the policy, regardless of reset state, 46 were followed by death within five seconds; counting all 46 as rollout mistakes would be wrong.

Death delays use the next real death before a respawn, within the same round. A null delay means no qualifying death before that boundary. “Damage in ten seconds” includes event damage, not a complete measure of usefulness; building damage and damage from persistent projectiles can occur without the player being physically present.

The before/after boundary uses the supplied chronology: August 18 Ashville is separate, August 18 Product and subsequent recordings are after. This is not a randomised comparison. Opponents, roster/mercs, maps, tele availability and team behaviour vary. A decrease in flagged incidents cannot be attributed entirely to deletion. Manual review also shows that a single binary `candidate` label is inadequate: a scene may be a closed-reset misuse, a legitimate continuation, an attempted rescue, a route reopened a few seconds too early, or an intentional gamble.

## Post-rollout cost scenarios

`history_cost.mjs` examines the twelve post-policy recordings. It starts only from a manually destroyed exit that previously belonged to an operational pair, and stops at the next observed operational pair or round end. Construction-state destructions are not counted as an additional destroyed usable connection.

Reopening requires three or four living non-Spy players at least 35% across the map for two seconds. The stricter variant requires this support to remain present during the two seconds immediately before each modelled tele use. This can reject a safe exit when few teammates remain alive, and can accept an unsafe exit despite several teammates being forward. It is a sensitivity test, not a safety classifier.

Only genuine death-to-respawn returns occurring after reopening are eligible. This includes a late respawn from a death before reopening: transport is only credited after the rollout-exclusion period has ended. Players who already spawned before reopening are omitted even if they could wait near the entrance. The preliminary commentary's ~30–52 player-seconds used the narrower requirement that the death itself occurred after reopening. The final main table includes late spawns after recovery, giving ~61–67 under the maintained-ground variants.

Travel uses the supplied approximate main-route measurements, 0.6 seconds transfer, and ordinary class-speed scaling. Engineer, Pyro, Sniper, Medic and Heavy are included. Loadout movement effects, healing-dependent speed and individual route choices are not reconstructed. Soldier, Demoman, Scout and Spy are excluded from this cost model, but not from incident screening except Spy. The surviving tele's recorded level determines the shared queue, with 10.6/5.6/3.6-second model cycles. Other excluded classes competing for slots are not simulated.

The alternative always allows walking. At every retained tele level, a rider waits no more than one second at the entrance; longer queues are rejected even when waiting would still beat walking. Candidate arrivals that are not earlier than walking are also rejected. Saved time is clipped by the recorded next death, observed restoration and round end. Attack-only time is clipped at our next capture and requires the enemy to own the point at respawn. Restoration clipping deliberately ends the comparison there; an arrival advantage already established could persist beyond restoration. Building effort and later consequences are omitted.

The model holds later observed deaths fixed even though earlier arrivals could change them. It assumes the retained exit survives and that players use it appropriately. Accordingly these are **potential earlier-presence seconds**, not observed extra combat seconds, rigorous lower/upper bounds, local numerical-advantage windows, or estimated extra wins. The spatial reopening state can also remain open across a later reset, route change or staging phase. Manual review must therefore give each candidate ride its own tactical deadline; a single ground-recovery threshold cannot do this reliably.

## What would be required for a stronger answer?

To count actual hypothetical +1/+2 windows, annotate safe reopening and meaningful fight participation for both teams, then choose a counterfactual travel model by class/route. The numerical margin would be friendly relevant players minus enemy relevant players at each time; earlier arrival only creates a positive margin when that difference crosses above zero. There is no single objective position boundary that works for Sniper sightlines, Medic healing, sentries, jumping classes and flanks.

Comms/video review of the short candidate list can establish intended resets and sacrificial uses. It still cannot establish how an unplayed fight would have ended. A future comparison that records closed/open calls and actual errors could estimate policy outcomes more directly.
