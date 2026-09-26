# BobGuard — Failsafe Verification Report

**Project:** BobGuard — Agentic UAV Failsafe Verification System  
**Built with:** IBM Bob  
**Scope:** Software-only state-machine simulator. No real UAV is controlled.

---

## 1. System Overview

The simulated UAV cycles through five states:

| State | Description |
|---|---|
| `NORMAL` | Nominal flight |
| `LOITER` | Holding position (awaiting recovery) |
| `RETURN_HOME` | Autonomous return to launch point |
| `LAND` | Safe terminal landing |
| `TERMINATED` | Kill-switch activated (terminal) |

Three failure types can be injected independently or simultaneously:

- `communication_loss` — ground-link dropped
- `gps_loss` — GPS navigation unavailable
- `critical_battery` — battery below safe threshold

---

## 2. Safety Requirements

| ID | Requirement |
|---|---|
| R1 | `communication_loss` → `NORMAL` → `LOITER` |
| R2 | Comm restored + battery safe → `LOITER` → `NORMAL` |
| R3 | `critical_battery` must eventually lead to `LAND` |
| R4 | `critical_battery` has higher priority than `LOITER` |
| R5 | `gps_loss` must prevent `RETURN_HOME` |
| R6 | No failure combination may permanently strand UAV in `LOITER` |
| R7 | Every failure scenario must eventually reach `NORMAL`, `LAND`, or `TERMINATED` |

---

## 3. Detected Failures (BEFORE)

### Test Run — Initial State Machine

| # | Scenario | Requirement | Result | Final State | Expected |
|---|---|---|---|---|---|
| 1 | R1_comm_loss_transitions_to_loiter | R1 | **PASS** | LOITER | LOITER |
| 2 | R2_comm_restored_returns_to_normal | R2 | **PASS** | NORMAL | NORMAL |
| 3 | R3_critical_battery_leads_to_land | R3 | **PASS** | LAND | LAND |
| 4 | R4_critical_battery_overrides_loiter | R4 | **PASS** | LAND | LAND |
| 5 | R4b_comm_loss_then_critical_battery_lands | R4 | **PASS** | LAND | LAND |
| 6 | R5_gps_loss_blocks_return_home | R5 | **FAIL** | RETURN_HOME | LOITER |
| 7 | R5b_gps_loss_during_return_home | R5 | **PASS** | LOITER | LOITER |
| 8 | R6_comm_and_gps_loss_not_stuck_in_loiter | R6 | **PASS** | NORMAL | NORMAL |
| 9 | R7_all_failures_reach_safe_terminal | R7 | **PASS** | LAND | LAND |
| 10 | R7b_return_home_critical_battery_must_land | R7 | **FAIL** | RETURN_HOME | LAND |

**BEFORE: 8/10 passed (80%) — 2 failures**

### Unsafe States Observed

| Scenario | Unsafe Observation |
|---|---|
| R5_gps_loss_blocks_return_home | UAV entered `RETURN_HOME` while GPS was unavailable — navigation without GPS is unsafe |
| R7b_return_home_critical_battery_must_land | UAV remained in `RETURN_HOME` with `critical_battery` active — will crash before landing |

---

## 4. Root Cause Analysis

### BUG-3 — `critical_battery` not handled when UAV is in `RETURN_HOME`

**Location:** `_evaluate()` in `uav_failsafe.py`

```python
# BEFORE (buggy)
if ctx.critical_battery:
    if self.state in (State.NORMAL, State.LOITER):   # RETURN_HOME missing!
        self.state = State.LAND
```

The `critical_battery` branch only covered `NORMAL` and `LOITER`. If the UAV was in `RETURN_HOME` when battery went critical, no transition fired and it remained in `RETURN_HOME` indefinitely.

**Violated:** R3 (critical battery must eventually lead to LAND), R7 (must reach safe terminal).

---

### BUG-4 — `command_return_home()` had no GPS guard

**Location:** `command_return_home()` in `uav_failsafe.py`

```python
# BEFORE (buggy)
def command_return_home(self):
    if self.state in self.TERMINAL_STATES:
        return
    # No gps_loss check — operator could force RETURN_HOME with no GPS
    self.state = State.RETURN_HOME
```

The `_evaluate()` method correctly caught a *spontaneous* GPS-loss event while already in `RETURN_HOME`, but an explicit operator command bypassed this guard entirely. The GPS check was missing from the command handler.

**Violated:** R5 (GPS loss must prevent RETURN_HOME).

---

### BUG-5 (discovered via regression) — premature `NORMAL` restoration when `gps_loss` still active

**Location:** "All failures cleared" branch of `_evaluate()`

```python
# BEFORE (buggy)
if self.state == State.LOITER:       # no check for remaining failures
    self.state = State.NORMAL
```

When `communication_loss` was restored while `gps_loss` was still active, the machine fell through to this branch and transitioned to `NORMAL`, briefly passing through an unsafe state (GPS navigation unavailable but UAV in NORMAL flight).

**Violated:** R6 (no failure combination should leave UAV in a bad intermediate state).

---

## 5. Modifications Made

All changes were **minimal and surgical** — no rewrite of uninvolved logic.

### Fix 1 — Add `RETURN_HOME` to `critical_battery` handler (BUG-3)

**File:** `bobguard/uav_failsafe.py`, `_evaluate()`

```python
# AFTER (fixed)
if ctx.critical_battery:
    if self.state in (State.NORMAL, State.LOITER, State.RETURN_HOME):
        self.state = State.LAND
        self._record("transition->LAND")
    return
```

### Fix 2 — Add `gps_loss` guard to `command_return_home()` (BUG-4)

**File:** `bobguard/uav_failsafe.py`, `command_return_home()`

```python
# AFTER (fixed)
def command_return_home(self):
    if self.state in self.TERMINAL_STATES:
        return
    if self.ctx.gps_loss:
        self.state = State.LOITER
        self._record("cmd->RETURN_HOME blocked(gps_loss)->LOITER")
        return
    self.state = State.RETURN_HOME
    self._record("cmd->RETURN_HOME")
```

### Fix 3 — Guard NORMAL restoration against remaining active failures (BUG-5)

**File:** `bobguard/uav_failsafe.py`, `_evaluate()` — "All failures cleared" branch

```python
# AFTER (fixed)
if self.state == State.LOITER and not ctx.gps_loss and not ctx.critical_battery:
    self.state = State.NORMAL
    self._record("transition->NORMAL(restored)")
```

---

## 6. Generated Regression Tests (Simultaneous Failures)

12 new scenarios were added in `bobguard/regression_scenarios.py`:

| ID | Scenario | Failures Combined | Requirement |
|---|---|---|---|
| REG1 | Simultaneous comm+gps loss, then restore | comm_loss + gps_loss | R6+R7 |
| REG2 | Simultaneous comm loss + critical battery | comm_loss + critical_battery | R4+R3 |
| REG3 | Simultaneous gps loss + critical battery | gps_loss + critical_battery | R3+R5 |
| REG4 | All three failures simultaneously | all three | R3+R4+R5+R7 |
| REG5 | RETURN_HOME → gps loss → critical battery | gps_loss + critical_battery | R3+R5 |
| REG6 | Comm restored, GPS still lost → stays LOITER | comm_loss + gps_loss (partial) | R6 |
| REG7 | GPS loss blocks RTH, then critical battery | gps_loss + critical_battery | R3+R5 |
| REG8 | Terminate from LOITER (kill-switch) | comm_loss | R7 |
| REG9 | No transition from LAND terminal | critical_battery + comm_loss | R7 |
| REG10 | No transition from TERMINATED terminal | terminate + critical_battery | R7 |
| REG11 | Battery critical, comm restored, stays LAND | comm_loss + critical_battery | R3+R7 |
| REG12 | GPS loss then restore → returns to NORMAL | gps_loss | R7 |

---

## 7. Before / After Results

### Original Scenarios (10 tests)

| Metric | BEFORE | AFTER |
|---|---|---|
| Tests passed | 8 / 10 | **10 / 10** |
| Pass rate | 80% | **100%** |
| Failed scenarios | R5_gps_loss_blocks_return_home, R7b_return_home_critical_battery_must_land | *none* |
| Unsafe states observed | RETURN_HOME (×2) | *none* |

### Regression Scenarios (12 tests — new)

| Metric | AFTER |
|---|---|
| Tests passed | **12 / 12** |
| Pass rate | **100%** |
| Failed scenarios | *none* |
| Unsafe states observed | *none* |

### Edge-Case Scenarios (13 tests — new)

| Metric | AFTER |
|---|---|
| Tests passed | **13 / 13** |
| Pass rate | **100%** |
| Failed scenarios | *none* |
| Unsafe states observed | *none* |

### Combination-Generated Scenarios (26 tests — auto-generated)

| Metric | AFTER |
|---|---|
| Tests passed | **26 / 26** |
| Pass rate | **100%** |
| Failed scenarios | *none* |
| Unsafe states observed | *none* |

### Combined (Final)

| Metric | BEFORE | AFTER |
|---|---|---|
| Total tests | 10 | **61** |
| Tests passed | 8 | **61** |
| Pass rate | **80%** | **100%** |
| Critical violations | — | **0** |
| High violations | — | **0** |
| Low diagnostics | — | **6** (expected operational notes) |
| Bugs detected | 3 (BUG-3, BUG-4, BUG-5) | **0 remaining** |
| Lines changed | — | **6 lines changed** |

---

## 8. File Structure

```
bobguard/
  __init__.py
  uav_failsafe.py              # State machine (fixed)
  scenarios.py                 # Original 10 test scenarios
  regression_scenarios.py      # 12 regression + 13 edge-case scenarios
  combination_generator.py     # Auto-generates 26 failure-combination scenarios
  tracer.py                    # TracingStateMachine with full state history
  violation_detector.py        # Safety violation detection and severity classification
  report_writer.py             # Verification report writer
  verify.py                    # Full verification suite entry point
  mutations.py                 # 5 realistic mutation definitions
  mutation_runner.py           # Mutation injection, probing, and restoration
  mutation_report_writer.py    # Mutation report writer
  mutate.py                    # Mutation testing entry point
  test_runner.py               # Legacy scenario executor
  run_all_tests.py             # Legacy full-suite entry point

bobguard_report.md             # Development narrative report (this file)
bobguard_verification_report.md  # Full scenario-by-scenario verification report
bobguard_mutation_report.md    # Mutation testing report
```

---

*Generated by IBM Bob — BobGuard Hackathon Project*
