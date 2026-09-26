# BobGuard — Mutation Testing Report

> **Built with IBM Bob** — Agentic UAV Failsafe Verification System  
> Mutation testing validates that BobGuard actively detects previously
> unseen defects, not just a passing implementation.

---

## Summary

| Metric | Value |
|--------|-------|
| Injected mutations | 5 |
| Detected mutations | 5 |
| Missed mutations | 0 |
| Mutation Detection Rate | **100%** |
| Original suite (post-mutation) | 61/61 PASS |

---

## Mutation Detection Table

| Mutation | Bug Description | Detected? | Triggering Scenario | Violation | Severity |
|----------|----------------|-----------|--------------------|-----------|----------|
| **M1** — Critical battery priority failure | Removes the LOITER→LAND transition when critical_battery fir… | **YES** | `R4_critical_battery_overrides_loiter` | STUCK_IN_LOITER, UNEXPECTED_TRANSITION | CRITICAL, HIGH |
| **M2** — Unsafe Return-To-Home | Removes the gps_loss guard from command_return_home(), allow… | **YES** | `R5_gps_loss_blocks_return_home` | NO_SAFE_TERMINAL, UNEXPECTED_TRANSITION, FORBIDDEN_STATE_VISITED | CRITICAL, HIGH |
| **M3** — Lost-link recovery bug | Removes the communication_loss guard from the LOITER→NORMAL … | **YES** | `COMB_inject__communication_loss` | STUCK_IN_LOITER | HIGH |
| **M4** — LOITER/RETURN_HOME loop | Inverts the GPS-loss guard direction: instead of RETURN_HOME… | **YES** | `R5b_gps_loss_during_return_home` | NO_SAFE_TERMINAL, UNEXPECTED_TRANSITION | HIGH |
| **M5** — Battery threshold boundary bug | Excludes State.NORMAL from the critical_battery landing bran… | **YES** | `R3_critical_battery_leads_to_land` | UNEXPECTED_TRANSITION | CRITICAL |

---

## Detailed Mutation Results

### M1 — Critical battery priority failure  `[DETECTED]`

| Field | Detail |
|-------|--------|
| Mutation ID | `M1` |
| Status | **DETECTED** |
| Requirement violated | R3, R4 |
| Patched method | `UAVStateMachine._evaluate()` |
| Expected violations | AIRBORNE_CRITICAL_BATT, STUCK_IN_LOITER |
| Expected severities | CRITICAL, HIGH |

**Bug description:**  
Removes the LOITER→LAND transition when critical_battery fires during a communication loss event. UAV stays airborne on empty battery.

**First triggering scenario:** `R4_critical_battery_overrides_loiter`

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
```

**Violations detected:** STUCK_IN_LOITER, UNEXPECTED_TRANSITION  
**Severities:** CRITICAL, HIGH  
**Final state:** `LOITER`

**Additional triggering scenarios** (14 more):

- `R4b_comm_loss_then_critical_battery_lands` — violations: STUCK_IN_LOITER, UNEXPECTED_TRANSITION
- `R7_all_failures_reach_safe_terminal` — violations: STUCK_IN_LOITER, UNEXPECTED_TRANSITION
- `REG2_simultaneous_comm_loss_and_critical_battery` — violations: STUCK_IN_LOITER, UNEXPECTED_TRANSITION
- `REG4_all_three_failures_simultaneously` — violations: STUCK_IN_LOITER, UNEXPECTED_TRANSITION
- `COMB_inject__communication_loss` — violations: STUCK_IN_LOITER

---

### M2 — Unsafe Return-To-Home  `[DETECTED]`

| Field | Detail |
|-------|--------|
| Mutation ID | `M2` |
| Status | **DETECTED** |
| Requirement violated | R5 |
| Patched method | `UAVStateMachine.command_return_home()` |
| Expected violations | RETURN_HOME_WITHOUT_GPS, FORBIDDEN_STATE_VISITED |
| Expected severities | CRITICAL |

**Bug description:**  
Removes the gps_loss guard from command_return_home(), allowing the operator to command autonomous navigation without GPS.

**First triggering scenario:** `R5_gps_loss_blocks_return_home`

**State Transition Trace:**

```
  NORMAL
    -> [cmd=return_home] -> RETURN_HOME  (active: gps_loss)
```

**Violations detected:** NO_SAFE_TERMINAL, UNEXPECTED_TRANSITION, FORBIDDEN_STATE_VISITED  
**Severities:** CRITICAL, HIGH  
**Final state:** `RETURN_HOME`

**Additional triggering scenarios** (2 more):

- `REG7_gps_loss_blocks_rth_then_critical_battery_lands` — violations: RETURN_HOME_WITHOUT_GPS, FORBIDDEN_STATE_VISITED
- `COMB_rth_with_gps_loss` — violations: NO_SAFE_TERMINAL, UNEXPECTED_TRANSITION, FORBIDDEN_STATE_VISITED

---

### M3 — Lost-link recovery bug  `[DETECTED]`

| Field | Detail |
|-------|--------|
| Mutation ID | `M3` |
| Status | **DETECTED** |
| Requirement violated | R2, R6 |
| Patched method | `UAVStateMachine._evaluate()` |
| Expected violations | UNEXPECTED_TRANSITION, NO_SAFE_TERMINAL |
| Expected severities | CRITICAL, HIGH |

**Bug description:**  
Removes the communication_loss guard from the LOITER→NORMAL restoration branch. UAV returns to NORMAL flight while the ground link is still down.

**First triggering scenario:** `COMB_inject__communication_loss`

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
```

**Violations detected:** STUCK_IN_LOITER  
**Severities:** HIGH  
**Final state:** `LOITER`

**Additional triggering scenarios** (5 more):

- `COMB_inject__communication_loss_AND_gps_loss` — violations: STUCK_IN_LOITER
- `COMB_partial_restore__inject_communication_loss_AND_gps_loss__restore_communication_loss` — violations: STUCK_IN_LOITER
- `COMB_partial_restore__inject_communication_loss_AND_gps_loss__restore_gps_loss` — violations: STUCK_IN_LOITER
- `COMB_order__communication_loss__THEN__gps_loss` — violations: STUCK_IN_LOITER
- `COMB_order__gps_loss__THEN__communication_loss` — violations: STUCK_IN_LOITER

---

### M4 — LOITER/RETURN_HOME loop  `[DETECTED]`

| Field | Detail |
|-------|--------|
| Mutation ID | `M4` |
| Status | **DETECTED** |
| Requirement violated | R5, R7 |
| Patched method | `UAVStateMachine._evaluate()` |
| Expected violations | RETURN_HOME_WITHOUT_GPS, FORBIDDEN_STATE_VISITED, NO_SAFE_TERMINAL, STUCK_IN_LOITER |
| Expected severities | CRITICAL, HIGH |

**Bug description:**  
Inverts the GPS-loss guard direction: instead of RETURN_HOME→LOITER, the mutant pushes LOITER→RETURN_HOME under gps_loss, creating an unsafe navigation state after comm is restored.

**First triggering scenario:** `R5b_gps_loss_during_return_home`

**State Transition Trace:**

```
  NORMAL
    -> [cmd=return_home] -> RETURN_HOME  (active: none)
```

**Violations detected:** NO_SAFE_TERMINAL, UNEXPECTED_TRANSITION  
**Severities:** HIGH  
**Final state:** `RETURN_HOME`

**Additional triggering scenarios** (9 more):

- `R6_comm_and_gps_loss_not_stuck_in_loiter` — violations: RETURN_HOME_WITHOUT_GPS, NO_SAFE_TERMINAL, UNEXPECTED_TRANSITION
- `REG6_comm_restored_gps_still_lost_stays_loiter` — violations: NO_SAFE_TERMINAL, UNEXPECTED_TRANSITION, FORBIDDEN_STATE_VISITED
- `COMB_inject__communication_loss` — violations: STUCK_IN_LOITER
- `COMB_inject__communication_loss_AND_gps_loss` — violations: STUCK_IN_LOITER
- `COMB_restore_all__communication_loss_AND_gps_loss` — violations: RETURN_HOME_WITHOUT_GPS, NO_SAFE_TERMINAL, UNEXPECTED_TRANSITION, FORBIDDEN_STATE_VISITED

---

### M5 — Battery threshold boundary bug  `[DETECTED]`

| Field | Detail |
|-------|--------|
| Mutation ID | `M5` |
| Status | **DETECTED** |
| Requirement violated | R3, R7 |
| Patched method | `UAVStateMachine._evaluate()` |
| Expected violations | AIRBORNE_CRITICAL_BATT |
| Expected severities | CRITICAL |

**Bug description:**  
Excludes State.NORMAL from the critical_battery landing branch. A UAV in normal flight with critical battery never transitions to LAND.

**First triggering scenario:** `R3_critical_battery_leads_to_land`

**State Transition Trace:**

```
  NORMAL
    (no transitions)
```

**Violations detected:** UNEXPECTED_TRANSITION  
**Severities:** CRITICAL  
**Final state:** `NORMAL`

**Additional triggering scenarios** (9 more):

- `REG3_simultaneous_gps_loss_and_critical_battery` — violations: UNEXPECTED_TRANSITION
- `REG9_no_transition_from_land_terminal` — violations: STUCK_IN_LOITER, UNEXPECTED_TRANSITION, FORBIDDEN_STATE_VISITED
- `COMB_inject__critical_battery` — violations: AIRBORNE_CRITICAL_BATT
- `COMB_inject__gps_loss_AND_critical_battery` — violations: AIRBORNE_CRITICAL_BATT
- `COMB_partial_restore__inject_gps_loss_AND_critical_battery__restore_gps_loss` — violations: AIRBORNE_CRITICAL_BATT

---

## Original Implementation Verification (Post-Mutation)

After all mutations were tested, the original unmodified implementation
was run through the full scenario suite to confirm zero regressions.

| Metric | Value |
|--------|-------|
| Scenarios run | 61 |
| Passed | 61 |
| Failed | 0 |
| Status | **PASS** |

---

## Interpretation

A **100% Mutation Detection Rate** means BobGuard does not merely
pass a correct implementation — it actively discovers every class of
realistic UAV failsafe defect injected by the mutation suite.

Each detected mutation corresponds to a real-world failure mode:

| Mutation | Real-World Risk |
|----------|-----------------|
| M1 | UAV loiters until battery exhaustion → uncontrolled crash |
| M2 | Autonomous navigation without GPS → loss of vehicle / collision |
| M3 | UAV resumes flight with no ground link → unrecoverable loss |
| M4 | Stuck in unsafe navigation state → collision or out-of-bounds |
| M5 | Silent battery drain in normal flight → crash without warning |

---

*Generated by IBM Bob — BobGuard Mutation Testing Workflow*