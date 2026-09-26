# BobGuard — Automated Failsafe Verification Report

> **Built with IBM Bob** — Agentic UAV Failsafe Verification System  
> Software-only state-machine simulator. No real UAV is controlled.

---

## Verification Methodology

**PASS** means the scenario's final state matches the requirement defined for it and no safety violation was detected. A PASS on a scenario that ends in LOITER means LOITER is the *explicitly required* outcome for that failure condition.

**Operational diagnostics** (`LOITER_ACTIVE_FAILURE`) are informational notes generated when the UAV ends in LOITER while active failure flags remain. LOITER is the *intended contingency state* in those conditions (R1, R5, R8); these diagnostics are **not safety violations** and are not counted as HIGH/CRITICAL.

**Undefined policy** means the scenario exercises a situation for which no explicit requirement exists. The outcome is noted but is not classified as a defect unless a defined requirement is demonstrably breached.

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total scenarios tested | 61 |
| Passed (requirement-compliant) | 61 |
| Failed (requirement violated) | 0 |
| Critical violations | 0 |
| High violations | 0 |
| Medium violations | 0 |
| Low violations (incl. operational diagnostics) | 6 |
| &nbsp;&nbsp; of which: expected LOITER diagnostics | 6 |
| Safe-state coverage | 73% (45/61) |

---

## Scenario Categories

- **original** — 10 scenarios, 10 passed, 0 failed
- **regression** — 12 scenarios, 12 passed, 0 failed
- **edge_case** — 13 scenarios, 13 passed, 0 failed
- **simultaneous_injection** — 7 scenarios, 7 passed, 0 failed
- **inject_restore** — 3 scenarios, 3 passed, 0 failed
- **partial_restore** — 6 scenarios, 6 passed, 0 failed
- **command_interaction** — 4 scenarios, 4 passed, 0 failed
- **injection_order** — 6 scenarios, 6 passed, 0 failed

---

## Detailed Results

### original

#### `R1_comm_loss_transitions_to_loiter`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R1 |
| Category | original |
| Injected failures | none |
| Final state | `LOITER` |
| Expected state | `LOITER` |
| Severity | **NONE** |

**Description:** R1_comm_loss_transitions_to_loiter

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
```

**Violations:** none

---

#### `R2_comm_restored_returns_to_normal`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R2 |
| Category | original |
| Injected failures | none |
| Final state | `NORMAL` |
| Expected state | `NORMAL` |
| Severity | **NONE** |

**Description:** R2_comm_restored_returns_to_normal

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [restore=communication_loss] -> NORMAL  (active: none)
```

**Violations:** none

---

#### `R3_critical_battery_leads_to_land`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3 |
| Category | original |
| Injected failures | none |
| Final state | `LAND` |
| Expected state | `LAND` |
| Severity | **NONE** |

**Description:** R3_critical_battery_leads_to_land

**State Transition Trace:**

```
  NORMAL
    -> [failure=critical_battery] -> LAND  (active: critical_battery)
```

**Violations:** none

---

#### `R4_critical_battery_overrides_loiter`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R4 |
| Category | original |
| Injected failures | none |
| Final state | `LAND` |
| Expected state | `LAND` |
| Severity | **NONE** |

**Description:** R4_critical_battery_overrides_loiter

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [failure=critical_battery] -> LAND  (active: communication_loss, critical_battery)
```

**Violations:** none

---

#### `R4b_comm_loss_then_critical_battery_lands`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R4 |
| Category | original |
| Injected failures | none |
| Final state | `LAND` |
| Expected state | `LAND` |
| Severity | **NONE** |

**Description:** R4b_comm_loss_then_critical_battery_lands

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [failure=critical_battery] -> LAND  (active: communication_loss, critical_battery)
```

**Violations:** none

---

#### `R5_gps_loss_blocks_return_home`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R5 |
| Category | original |
| Injected failures | none |
| Final state | `LOITER` |
| Expected state | `LOITER` |
| Severity | **NONE** |

**Description:** R5_gps_loss_blocks_return_home

**State Transition Trace:**

```
  NORMAL
    -> [cmd=return_home] -> LOITER  (active: gps_loss)
```

**Violations:** none

---

#### `R5b_gps_loss_during_return_home`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R5 |
| Category | original |
| Injected failures | none |
| Final state | `LOITER` |
| Expected state | `LOITER` |
| Severity | **NONE** |

**Description:** R5b_gps_loss_during_return_home

**State Transition Trace:**

```
  NORMAL
    -> [cmd=return_home] -> RETURN_HOME  (active: none)
    -> [failure=gps_loss] -> LOITER  (active: gps_loss)
```

**Violations:** none

---

#### `R6_comm_and_gps_loss_not_stuck_in_loiter`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R6 |
| Category | original |
| Injected failures | none |
| Final state | `NORMAL` |
| Expected state | `NORMAL` |
| Severity | **NONE** |

**Description:** R6_comm_and_gps_loss_not_stuck_in_loiter

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [restore=gps_loss] -> NORMAL  (active: none)
```

**Violations:** none

---

#### `R7_all_failures_reach_safe_terminal`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R7 |
| Category | original |
| Injected failures | none |
| Final state | `LAND` |
| Expected state | `LAND` |
| Severity | **NONE** |

**Description:** R7_all_failures_reach_safe_terminal

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [failure=critical_battery] -> LAND  (active: communication_loss, gps_loss, critical_battery)
```

**Violations:** none

---

#### `R7b_return_home_critical_battery_must_land`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R7 |
| Category | original |
| Injected failures | none |
| Final state | `LAND` |
| Expected state | `LAND` |
| Severity | **NONE** |

**Description:** R7b_return_home_critical_battery_must_land

**State Transition Trace:**

```
  NORMAL
    -> [cmd=return_home] -> RETURN_HOME  (active: none)
    -> [failure=critical_battery] -> LAND  (active: critical_battery)
```

**Violations:** none

---

### regression

#### `REG1_simultaneous_comm_and_gps_loss_then_restore`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R6+R7 |
| Category | regression |
| Injected failures | none |
| Final state | `NORMAL` |
| Expected state | `NORMAL` |
| Severity | **NONE** |

**Description:** REG1_simultaneous_comm_and_gps_loss_then_restore

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [restore=communication_loss] -> NORMAL  (active: none)
```

**Violations:** none

---

#### `REG2_simultaneous_comm_loss_and_critical_battery`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R4+R3 |
| Category | regression |
| Injected failures | none |
| Final state | `LAND` |
| Expected state | `LAND` |
| Severity | **NONE** |

**Description:** REG2_simultaneous_comm_loss_and_critical_battery

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [failure=critical_battery] -> LAND  (active: communication_loss, critical_battery)
```

**Violations:** none

---

#### `REG3_simultaneous_gps_loss_and_critical_battery`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R5 |
| Category | regression |
| Injected failures | none |
| Final state | `LAND` |
| Expected state | `LAND` |
| Severity | **NONE** |

**Description:** REG3_simultaneous_gps_loss_and_critical_battery

**State Transition Trace:**

```
  NORMAL
    -> [failure=critical_battery] -> LAND  (active: gps_loss, critical_battery)
```

**Violations:** none

---

#### `REG4_all_three_failures_simultaneously`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R4+R5+R7 |
| Category | regression |
| Injected failures | none |
| Final state | `LAND` |
| Expected state | `LAND` |
| Severity | **NONE** |

**Description:** REG4_all_three_failures_simultaneously

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [failure=critical_battery] -> LAND  (active: communication_loss, gps_loss, critical_battery)
```

**Violations:** none

---

#### `REG5_return_home_gps_loss_then_critical_battery`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R5 |
| Category | regression |
| Injected failures | none |
| Final state | `LAND` |
| Expected state | `LAND` |
| Severity | **NONE** |

**Description:** REG5_return_home_gps_loss_then_critical_battery

**State Transition Trace:**

```
  NORMAL
    -> [cmd=return_home] -> RETURN_HOME  (active: none)
    -> [failure=gps_loss] -> LOITER  (active: gps_loss)
    -> [failure=critical_battery] -> LAND  (active: gps_loss, critical_battery)
```

**Violations:** none

---

#### `REG6_comm_restored_gps_still_lost_stays_loiter`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R6 |
| Category | regression |
| Injected failures | none |
| Final state | `LOITER` |
| Expected state | `LOITER` |
| Severity | **NONE** |

**Description:** REG6_comm_restored_gps_still_lost_stays_loiter

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
```

**Violations:** none

---

#### `REG7_gps_loss_blocks_rth_then_critical_battery_lands`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R5 |
| Category | regression |
| Injected failures | none |
| Final state | `LAND` |
| Expected state | `LAND` |
| Severity | **NONE** |

**Description:** REG7_gps_loss_blocks_rth_then_critical_battery_lands

**State Transition Trace:**

```
  NORMAL
    -> [cmd=return_home] -> LOITER  (active: gps_loss)
    -> [failure=critical_battery] -> LAND  (active: gps_loss, critical_battery)
```

**Violations:** none

---

#### `REG8_terminate_from_loiter`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R7 |
| Category | regression |
| Injected failures | none |
| Final state | `TERMINATED` |
| Expected state | `TERMINATED` |
| Severity | **NONE** |

**Description:** REG8_terminate_from_loiter

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [cmd=terminate] -> TERMINATED  (active: communication_loss)
```

**Violations:** none

---

#### `REG9_no_transition_from_land_terminal`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R7 |
| Category | regression |
| Injected failures | none |
| Final state | `LAND` |
| Expected state | `LAND` |
| Severity | **NONE** |

**Description:** REG9_no_transition_from_land_terminal

**State Transition Trace:**

```
  NORMAL
    -> [failure=critical_battery] -> LAND  (active: critical_battery)
```

**Violations:** none

---

#### `REG10_no_transition_from_terminated_terminal`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R7 |
| Category | regression |
| Injected failures | none |
| Final state | `TERMINATED` |
| Expected state | `TERMINATED` |
| Severity | **NONE** |

**Description:** REG10_no_transition_from_terminated_terminal

**State Transition Trace:**

```
  NORMAL
    -> [cmd=terminate] -> TERMINATED  (active: none)
```

**Violations:** none

---

#### `REG11_battery_critical_comm_restored_stays_land`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R7 |
| Category | regression |
| Injected failures | none |
| Final state | `LAND` |
| Expected state | `LAND` |
| Severity | **NONE** |

**Description:** REG11_battery_critical_comm_restored_stays_land

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [failure=critical_battery] -> LAND  (active: communication_loss, critical_battery)
```

**Violations:** none

---

#### `REG12_gps_loss_restore_returns_to_normal`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R7 |
| Category | regression |
| Injected failures | none |
| Final state | `NORMAL` |
| Expected state | `NORMAL` |
| Severity | **NONE** |

**Description:** REG12_gps_loss_restore_returns_to_normal

**State Transition Trace:**

```
  NORMAL
    (no transitions)
```

**Violations:** none

---

### edge_case

#### `ECT1_comm_loss_during_return_home_gps_ok`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R8 |
| Category | edge_case |
| Injected failures | none |
| Final state | `RETURN_HOME` |
| Expected state | `RETURN_HOME` |
| Severity | **NONE** |

**Description:** R8 policy: comm_loss during RETURN_HOME with GPS available. RETURN_HOME must continue — GPS provides full navigation capability. Forcing LOITER here would violate R8 and increase risk. Expected result: UAV remains in RETURN_HOME (PASS, policy-compliant).

**State Transition Trace:**

```
  NORMAL
    -> [cmd=return_home] -> RETURN_HOME  (active: none)
```

**Violations:** none

---

#### `ECT2_duplicate_comm_loss_idempotent`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R1 |
| Category | edge_case |
| Injected failures | none |
| Final state | `LOITER` |
| Expected state | `LOITER` |
| Severity | **NONE** |

**Description:** Applying communication_loss twice must not change state beyond the initial LOITER transition — idempotency check.

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
```

**Violations:** none

---

#### `ECT3_duplicate_gps_loss_idempotent`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R5 |
| Category | edge_case |
| Injected failures | none |
| Final state | `NORMAL` |
| Expected state | `NORMAL` |
| Severity | **NONE** |

**Description:** GPS loss alone from NORMAL leaves UAV in NORMAL. A duplicate injection must not cause any unexpected transition.

**State Transition Trace:**

```
  NORMAL
    (no transitions)
```

**Violations:** none

---

#### `ECT4_repeated_comm_loss_restore_cycle`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R1+R2 |
| Category | edge_case |
| Injected failures | none |
| Final state | `NORMAL` |
| Expected state | `NORMAL` |
| Severity | **NONE** |

**Description:** Two full comm_loss/restore cycles. Each restore must cleanly return to NORMAL (R2); final state must be NORMAL.

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [restore=communication_loss] -> NORMAL  (active: none)
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [restore=communication_loss] -> NORMAL  (active: none)
```

**Violations:** none

---

#### `ECT5_restore_never_injected_failure`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R7 |
| Category | edge_case |
| Injected failures | none |
| Final state | `NORMAL` |
| Expected state | `NORMAL` |
| Severity | **NONE** |

**Description:** Calling restore() for a failure that was never injected must be a safe no-op — UAV must remain in NORMAL.

**State Transition Trace:**

```
  NORMAL
    (no transitions)
```

**Violations:** none

---

#### `ECT6_terminate_overrides_land_terminal`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R7 |
| Category | edge_case |
| Injected failures | none |
| Final state | `TERMINATED` |
| Expected state | `TERMINATED` |
| Severity | **NONE** |

**Description:** command_terminate has no TERMINAL_STATES guard; kill-switch applied after LAND should transition to TERMINATED. Verifies the kill-switch always takes precedence.

**State Transition Trace:**

```
  NORMAL
    -> [failure=critical_battery] -> LAND  (active: critical_battery)
    -> [cmd=terminate] -> TERMINATED  (active: critical_battery)
```

**Violations:** none

---

#### `ECT7_rth_gps_loss_recover_to_normal`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R2+R5 |
| Category | edge_case |
| Injected failures | none |
| Final state | `NORMAL` |
| Expected state | `NORMAL` |
| Severity | **NONE** |

**Description:** GPS lost during RTH → LOITER, then GPS restored → NORMAL. Tests the complete recovery path after partial RTH failure.

**State Transition Trace:**

```
  NORMAL
    -> [cmd=return_home] -> RETURN_HOME  (active: none)
    -> [failure=gps_loss] -> LOITER  (active: gps_loss)
    -> [restore=gps_loss] -> NORMAL  (active: none)
```

**Violations:** none

---

#### `ECT8_command_land_from_return_home`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R7 |
| Category | edge_case |
| Injected failures | none |
| Final state | `LAND` |
| Expected state | `LAND` |
| Severity | **NONE** |

**Description:** Operator issues command_land while UAV is in RETURN_HOME. Immediate land must be respected (R7 operator override).

**State Transition Trace:**

```
  NORMAL
    -> [cmd=return_home] -> RETURN_HOME  (active: none)
    -> [cmd=land] -> LAND  (active: none)
```

**Violations:** none

---

#### `ECT9_command_land_from_loiter`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R7 |
| Category | edge_case |
| Injected failures | none |
| Final state | `LAND` |
| Expected state | `LAND` |
| Severity | **NONE** |

**Description:** Operator issues command_land while UAV is in LOITER. Must immediately transition to LAND.

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [cmd=land] -> LAND  (active: communication_loss)
```

**Violations:** none

---

#### `ECT10_restore_comm_loss_while_in_rth_gps_ok`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R8 |
| Category | edge_case |
| Injected failures | none |
| Final state | `RETURN_HOME` |
| Expected state | `RETURN_HOME` |
| Severity | **NONE** |

**Description:** R8 policy: comm_loss then comm-restore while in RETURN_HOME with GPS available. Neither event should interrupt the return journey. State must remain RETURN_HOME throughout (PASS, policy-compliant).

**State Transition Trace:**

```
  NORMAL
    -> [cmd=return_home] -> RETURN_HOME  (active: none)
```

**Violations:** none

---

#### `ECT11_critical_battery_first_then_comm_loss`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R4 |
| Category | edge_case |
| Injected failures | none |
| Final state | `LAND` |
| Expected state | `LAND` |
| Severity | **NONE** |

**Description:** Critical battery fires before comm_loss. UAV must land immediately from NORMAL without visiting LOITER. Subsequent comm_loss must be ignored (terminal guard).

**State Transition Trace:**

```
  NORMAL
    -> [failure=critical_battery] -> LAND  (active: critical_battery)
```

**Violations:** none

---

#### `ECT12_restore_all_from_land_terminal`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R7 |
| Category | edge_case |
| Injected failures | none |
| Final state | `LAND` |
| Expected state | `LAND` |
| Severity | **NONE** |

**Description:** Once LAND (terminal) is reached, all restore() calls must be no-ops. UAV must remain in LAND regardless of flag clearing.

**State Transition Trace:**

```
  NORMAL
    -> [failure=critical_battery] -> LAND  (active: critical_battery)
```

**Violations:** none

---

#### `ECT13_comm_loss_during_rth_gps_unavailable_aborts_to_loiter`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R8 |
| Category | edge_case |
| Injected failures | none |
| Final state | `LOITER` |
| Expected state | `LOITER` |
| Severity | **NONE** |

**Description:** R8 second branch: GPS unavailable when RTH is disrupted. GPS loss during RTH correctly moves to LOITER (R5); subsequent comm_loss must not escape LOITER or trigger a false NORMAL transition. Verifies both branches of R8 are covered and consistent.

**State Transition Trace:**

```
  NORMAL
    -> [cmd=return_home] -> RETURN_HOME  (active: none)
    -> [failure=gps_loss] -> LOITER  (active: gps_loss)
```

**Violations:** none

---

### simultaneous_injection

#### `COMB_inject__communication_loss`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R5+R7 |
| Category | simultaneous_injection |
| Injected failures | communication_loss |
| Final state | `LOITER` |
| Expected state | `any-safe` |
| Severity | **LOW** |

**Description:** Inject communication_loss sequentially; UAV must reach a safe terminal or safe holding state.

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
```

**Violations Detected:**

- **[LOW] LOITER_ACTIVE_FAILURE**  
  UAV ended scenario in LOITER while active failures remain. LOITER is the defined contingency state for this condition (R1 / R5 / R8). This is expected operational behaviour, not a safety defect.  
  *Fix:* No corrective action required. Consider a timeout-to-LAND requirement if failures persist beyond battery endurance.  
  *Evidence:* `Final state: LOITER. Active failures: {'communication_loss': True}`

---

#### `COMB_inject__gps_loss`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R5+R7 |
| Category | simultaneous_injection |
| Injected failures | gps_loss |
| Final state | `NORMAL` |
| Expected state | `any-safe` |
| Severity | **NONE** |

**Description:** Inject gps_loss sequentially; UAV must reach a safe terminal or safe holding state.

**State Transition Trace:**

```
  NORMAL
    (no transitions)
```

**Violations:** none

---

#### `COMB_inject__critical_battery`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R5+R7 |
| Category | simultaneous_injection |
| Injected failures | critical_battery |
| Final state | `LAND` |
| Expected state | `any-safe` |
| Severity | **NONE** |

**Description:** Inject critical_battery sequentially; UAV must reach a safe terminal or safe holding state.

**State Transition Trace:**

```
  NORMAL
    -> [failure=critical_battery] -> LAND  (active: critical_battery)
```

**Violations:** none

---

#### `COMB_inject__communication_loss_AND_gps_loss`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R5+R7 |
| Category | simultaneous_injection |
| Injected failures | communication_loss, gps_loss |
| Final state | `LOITER` |
| Expected state | `any-safe` |
| Severity | **LOW** |

**Description:** Inject communication_loss, gps_loss sequentially; UAV must reach a safe terminal or safe holding state.

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
```

**Violations Detected:**

- **[LOW] LOITER_ACTIVE_FAILURE**  
  UAV ended scenario in LOITER while active failures remain. LOITER is the defined contingency state for this condition (R1 / R5 / R8). This is expected operational behaviour, not a safety defect.  
  *Fix:* No corrective action required. Consider a timeout-to-LAND requirement if failures persist beyond battery endurance.  
  *Evidence:* `Final state: LOITER. Active failures: {'communication_loss': True}`

---

#### `COMB_inject__communication_loss_AND_critical_battery`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R5+R7 |
| Category | simultaneous_injection |
| Injected failures | communication_loss, critical_battery |
| Final state | `LAND` |
| Expected state | `any-safe` |
| Severity | **NONE** |

**Description:** Inject communication_loss, critical_battery sequentially; UAV must reach a safe terminal or safe holding state.

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [failure=critical_battery] -> LAND  (active: communication_loss, critical_battery)
```

**Violations:** none

---

#### `COMB_inject__gps_loss_AND_critical_battery`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R5+R7 |
| Category | simultaneous_injection |
| Injected failures | gps_loss, critical_battery |
| Final state | `LAND` |
| Expected state | `any-safe` |
| Severity | **NONE** |

**Description:** Inject gps_loss, critical_battery sequentially; UAV must reach a safe terminal or safe holding state.

**State Transition Trace:**

```
  NORMAL
    -> [failure=critical_battery] -> LAND  (active: gps_loss, critical_battery)
```

**Violations:** none

---

#### `COMB_inject__communication_loss_AND_gps_loss_AND_critical_battery`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R5+R7 |
| Category | simultaneous_injection |
| Injected failures | communication_loss, gps_loss, critical_battery |
| Final state | `LAND` |
| Expected state | `any-safe` |
| Severity | **NONE** |

**Description:** Inject communication_loss, gps_loss, critical_battery sequentially; UAV must reach a safe terminal or safe holding state.

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [failure=critical_battery] -> LAND  (active: communication_loss, gps_loss, critical_battery)
```

**Violations:** none

---

### inject_restore

#### `COMB_restore_all__communication_loss`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R2+R6+R7 |
| Category | inject_restore |
| Injected failures | communication_loss |
| Final state | `NORMAL` |
| Expected state | `NORMAL` |
| Severity | **NONE** |

**Description:** Inject communication_loss, then restore all; expect recovery to NORMAL.

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [restore=communication_loss] -> NORMAL  (active: none)
```

**Violations:** none

---

#### `COMB_restore_all__gps_loss`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R2+R6+R7 |
| Category | inject_restore |
| Injected failures | gps_loss |
| Final state | `NORMAL` |
| Expected state | `NORMAL` |
| Severity | **NONE** |

**Description:** Inject gps_loss, then restore all; expect recovery to NORMAL.

**State Transition Trace:**

```
  NORMAL
    (no transitions)
```

**Violations:** none

---

#### `COMB_restore_all__communication_loss_AND_gps_loss`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R2+R6+R7 |
| Category | inject_restore |
| Injected failures | communication_loss, gps_loss |
| Final state | `NORMAL` |
| Expected state | `NORMAL` |
| Severity | **NONE** |

**Description:** Inject communication_loss, gps_loss, then restore all; expect recovery to NORMAL.

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [restore=gps_loss] -> NORMAL  (active: none)
```

**Violations:** none

---

### partial_restore

#### `COMB_partial_restore__inject_communication_loss_AND_gps_loss__restore_communication_loss`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R5+R6+R7 |
| Category | partial_restore |
| Injected failures | communication_loss, gps_loss |
| Final state | `LOITER` |
| Expected state | `any-safe` |
| Severity | **LOW** |

**Description:** Inject communication_loss+gps_loss, restore communication_loss; gps_loss still active — must not enter unsafe state.

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
```

**Violations Detected:**

- **[LOW] LOITER_ACTIVE_FAILURE**  
  UAV ended scenario in LOITER while active failures remain. LOITER is the defined contingency state for this condition (R1 / R5 / R8). This is expected operational behaviour, not a safety defect.  
  *Fix:* No corrective action required. Consider a timeout-to-LAND requirement if failures persist beyond battery endurance.  
  *Evidence:* `Final state: LOITER. Active failures: {'communication_loss': True}`

---

#### `COMB_partial_restore__inject_communication_loss_AND_gps_loss__restore_gps_loss`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R5+R6+R7 |
| Category | partial_restore |
| Injected failures | communication_loss, gps_loss |
| Final state | `LOITER` |
| Expected state | `any-safe` |
| Severity | **LOW** |

**Description:** Inject communication_loss+gps_loss, restore gps_loss; communication_loss still active — must not enter unsafe state.

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
```

**Violations Detected:**

- **[LOW] LOITER_ACTIVE_FAILURE**  
  UAV ended scenario in LOITER while active failures remain. LOITER is the defined contingency state for this condition (R1 / R5 / R8). This is expected operational behaviour, not a safety defect.  
  *Fix:* No corrective action required. Consider a timeout-to-LAND requirement if failures persist beyond battery endurance.  
  *Evidence:* `Final state: LOITER. Active failures: {'communication_loss': True}`

---

#### `COMB_partial_restore__inject_communication_loss_AND_critical_battery__restore_communication_loss`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R5+R6+R7 |
| Category | partial_restore |
| Injected failures | communication_loss, critical_battery |
| Final state | `LAND` |
| Expected state | `any-safe` |
| Severity | **NONE** |

**Description:** Inject communication_loss+critical_battery, restore communication_loss; critical_battery still active — must not enter unsafe state.

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [failure=critical_battery] -> LAND  (active: communication_loss, critical_battery)
```

**Violations:** none

---

#### `COMB_partial_restore__inject_communication_loss_AND_critical_battery__restore_critical_battery`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R5+R6+R7 |
| Category | partial_restore |
| Injected failures | communication_loss, critical_battery |
| Final state | `LAND` |
| Expected state | `any-safe` |
| Severity | **NONE** |

**Description:** Inject communication_loss+critical_battery, restore critical_battery; communication_loss still active — must not enter unsafe state.

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [failure=critical_battery] -> LAND  (active: communication_loss, critical_battery)
```

**Violations:** none

---

#### `COMB_partial_restore__inject_gps_loss_AND_critical_battery__restore_gps_loss`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R5+R6+R7 |
| Category | partial_restore |
| Injected failures | gps_loss, critical_battery |
| Final state | `LAND` |
| Expected state | `any-safe` |
| Severity | **NONE** |

**Description:** Inject gps_loss+critical_battery, restore gps_loss; critical_battery still active — must not enter unsafe state.

**State Transition Trace:**

```
  NORMAL
    -> [failure=critical_battery] -> LAND  (active: gps_loss, critical_battery)
```

**Violations:** none

---

#### `COMB_partial_restore__inject_gps_loss_AND_critical_battery__restore_critical_battery`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R5+R6+R7 |
| Category | partial_restore |
| Injected failures | gps_loss, critical_battery |
| Final state | `LAND` |
| Expected state | `any-safe` |
| Severity | **NONE** |

**Description:** Inject gps_loss+critical_battery, restore critical_battery; gps_loss still active — must not enter unsafe state.

**State Transition Trace:**

```
  NORMAL
    -> [failure=critical_battery] -> LAND  (active: gps_loss, critical_battery)
```

**Violations:** none

---

### command_interaction

#### `COMB_rth_with_gps_loss`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R5 |
| Category | command_interaction |
| Injected failures | gps_loss |
| Final state | `LOITER` |
| Expected state | `LOITER` |
| Severity | **NONE** |

**Description:** RTH command with gps_loss active must be blocked -> LOITER.

**State Transition Trace:**

```
  NORMAL
    -> [cmd=return_home] -> LOITER  (active: gps_loss)
```

**Violations:** none

---

#### `COMB_rth_with_comm_loss_only`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R5 |
| Category | command_interaction |
| Injected failures | communication_loss |
| Final state | `RETURN_HOME` |
| Expected state | `RETURN_HOME` |
| Severity | **NONE** |

**Description:** RTH after comm loss restored (GPS fine) is permitted.

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [restore=communication_loss] -> NORMAL  (active: none)
    -> [cmd=return_home] -> RETURN_HOME  (active: none)
```

**Violations:** none

---

#### `COMB_rth_then_critical_battery`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R7 |
| Category | command_interaction |
| Injected failures | critical_battery |
| Final state | `LAND` |
| Expected state | `LAND` |
| Severity | **NONE** |

**Description:** Critical battery during RTH must abort to LAND.

**State Transition Trace:**

```
  NORMAL
    -> [cmd=return_home] -> RETURN_HOME  (active: none)
    -> [failure=critical_battery] -> LAND  (active: critical_battery)
```

**Violations:** none

---

#### `COMB_rth_gps_loss_and_critical_battery`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R5+R7 |
| Category | command_interaction |
| Injected failures | gps_loss, critical_battery |
| Final state | `LAND` |
| Expected state | `LAND` |
| Severity | **NONE** |

**Description:** GPS loss then critical battery during RTH must reach LAND.

**State Transition Trace:**

```
  NORMAL
    -> [cmd=return_home] -> RETURN_HOME  (active: none)
    -> [failure=gps_loss] -> LOITER  (active: gps_loss)
    -> [failure=critical_battery] -> LAND  (active: gps_loss, critical_battery)
```

**Violations:** none

---

### injection_order

#### `COMB_order__communication_loss__THEN__gps_loss`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R4+R5+R7 |
| Category | injection_order |
| Injected failures | communication_loss, gps_loss |
| Final state | `LOITER` |
| Expected state | `any-safe` |
| Severity | **LOW** |

**Description:** Inject communication_loss then gps_loss; final state must be safe regardless of arrival order.

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
```

**Violations Detected:**

- **[LOW] LOITER_ACTIVE_FAILURE**  
  UAV ended scenario in LOITER while active failures remain. LOITER is the defined contingency state for this condition (R1 / R5 / R8). This is expected operational behaviour, not a safety defect.  
  *Fix:* No corrective action required. Consider a timeout-to-LAND requirement if failures persist beyond battery endurance.  
  *Evidence:* `Final state: LOITER. Active failures: {'communication_loss': True}`

---

#### `COMB_order__gps_loss__THEN__communication_loss`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R4+R5+R7 |
| Category | injection_order |
| Injected failures | gps_loss, communication_loss |
| Final state | `LOITER` |
| Expected state | `any-safe` |
| Severity | **LOW** |

**Description:** Inject gps_loss then communication_loss; final state must be safe regardless of arrival order.

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss, gps_loss)
```

**Violations Detected:**

- **[LOW] LOITER_ACTIVE_FAILURE**  
  UAV ended scenario in LOITER while active failures remain. LOITER is the defined contingency state for this condition (R1 / R5 / R8). This is expected operational behaviour, not a safety defect.  
  *Fix:* No corrective action required. Consider a timeout-to-LAND requirement if failures persist beyond battery endurance.  
  *Evidence:* `Final state: LOITER. Active failures: {'communication_loss': True, 'gps_loss': True}`

---

#### `COMB_order__communication_loss__THEN__critical_battery`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R4+R5+R7 |
| Category | injection_order |
| Injected failures | communication_loss, critical_battery |
| Final state | `LAND` |
| Expected state | `any-safe` |
| Severity | **NONE** |

**Description:** Inject communication_loss then critical_battery; final state must be safe regardless of arrival order.

**State Transition Trace:**

```
  NORMAL
    -> [failure=communication_loss] -> LOITER  (active: communication_loss)
    -> [failure=critical_battery] -> LAND  (active: communication_loss, critical_battery)
```

**Violations:** none

---

#### `COMB_order__critical_battery__THEN__communication_loss`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R4+R5+R7 |
| Category | injection_order |
| Injected failures | critical_battery, communication_loss |
| Final state | `LAND` |
| Expected state | `any-safe` |
| Severity | **NONE** |

**Description:** Inject critical_battery then communication_loss; final state must be safe regardless of arrival order.

**State Transition Trace:**

```
  NORMAL
    -> [failure=critical_battery] -> LAND  (active: critical_battery)
```

**Violations:** none

---

#### `COMB_order__gps_loss__THEN__critical_battery`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R4+R5+R7 |
| Category | injection_order |
| Injected failures | gps_loss, critical_battery |
| Final state | `LAND` |
| Expected state | `any-safe` |
| Severity | **NONE** |

**Description:** Inject gps_loss then critical_battery; final state must be safe regardless of arrival order.

**State Transition Trace:**

```
  NORMAL
    -> [failure=critical_battery] -> LAND  (active: gps_loss, critical_battery)
```

**Violations:** none

---

#### `COMB_order__critical_battery__THEN__gps_loss`

| Field | Value |
|-------|-------|
| Result | **PASS** |
| Requirement | R3+R4+R5+R7 |
| Category | injection_order |
| Injected failures | critical_battery, gps_loss |
| Final state | `LAND` |
| Expected state | `any-safe` |
| Severity | **NONE** |

**Description:** Inject critical_battery then gps_loss; final state must be safe regardless of arrival order.

**State Transition Trace:**

```
  NORMAL
    -> [failure=critical_battery] -> LAND  (active: critical_battery)
```

**Violations:** none

---

## Violation Index

| Scenario | Severity | Violation | Recommended Fix |
|----------|----------|-----------|-----------------|
| `COMB_inject__communication_loss` | **LOW** | LOITER_ACTIVE_FAILURE | No corrective action required. Consider a timeout-to-LAND requirement if failure... |
| `COMB_inject__communication_loss_AND_gps_loss` | **LOW** | LOITER_ACTIVE_FAILURE | No corrective action required. Consider a timeout-to-LAND requirement if failure... |
| `COMB_partial_restore__inject_communication_loss_AND_gps_loss__restore_communication_loss` | **LOW** | LOITER_ACTIVE_FAILURE | No corrective action required. Consider a timeout-to-LAND requirement if failure... |
| `COMB_partial_restore__inject_communication_loss_AND_gps_loss__restore_gps_loss` | **LOW** | LOITER_ACTIVE_FAILURE | No corrective action required. Consider a timeout-to-LAND requirement if failure... |
| `COMB_order__communication_loss__THEN__gps_loss` | **LOW** | LOITER_ACTIVE_FAILURE | No corrective action required. Consider a timeout-to-LAND requirement if failure... |
| `COMB_order__gps_loss__THEN__communication_loss` | **LOW** | LOITER_ACTIVE_FAILURE | No corrective action required. Consider a timeout-to-LAND requirement if failure... |

---


---

*Generated by IBM Bob — BobGuard Automated Verification Workflow*