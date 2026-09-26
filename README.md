# BobGuard

**Agentic UAV Failsafe Verification with IBM Bob**

BobGuard is a software-only verification tool for UAV failsafe logic. It uses IBM Bob to analyze failsafe state machines, generate combined failure scenarios, detect unsafe transitions, repair implementation defects, and validate the repaired system through regression and mutation testing.

## Problem

UAV failsafe logic must remain correct even when multiple failures occur simultaneously.

Examples include:

- Communication loss
- GPS loss
- Critical battery
- Conflicting recovery conditions
- Unsafe Return-to-Home behavior

A failsafe implementation may behave correctly for individual failures but become unsafe when several conditions interact.

For example:

```text
NORMAL
  ↓ Communication Loss
LOITER
  ↓ Critical Battery
LOITER
```

The UAV remains airborne even though the battery is critical.

BobGuard is designed to detect these implementation-level safety defects automatically.

## Solution

BobGuard creates an automated verification workflow around a UAV failsafe state machine.

```text
UAV Failsafe Implementation
            ↓
        IBM Bob
            ↓
   Requirement Analysis
            ↓
Failure Combination Generation
            ↓
 State Transition Tracing
            ↓
 Safety Violation Detection
            ↓
      Root Cause Analysis
            ↓
        Code Repair
            ↓
 Regression + Mutation Testing
```

The project does not control a real UAV. It verifies software behavior against explicitly defined failsafe safety requirements.

## Safety Requirements

BobGuard currently verifies requirements including:

- Communication loss triggers a safe contingency state.
- Critical battery has priority over loiter behavior.
- Critical battery eventually results in landing.
- Return-to-Home is not allowed when GPS navigation is unavailable.
- Active failures cannot be bypassed by returning to NORMAL.
- Failure combinations must not create infinite unsafe loops.
- Every scenario must reach an acceptable safe state.

## Project Structure

```text
bobguard/
├── uav_failsafe.py
├── scenarios.py
├── regression_scenarios.py
├── combination_generator.py
├── tracer.py
├── violation_detector.py
├── report_writer.py
├── verify.py
├── mutations.py
├── mutation_runner.py
├── mutation_report_writer.py
├── mutate.py
├── test_runner.py
└── run_all_tests.py

bobguard_report.md
bobguard_verification_report.md
bobguard_mutation_report.md
bob_sessions/
```

## Automated Failure Generation

BobGuard automatically generates meaningful combinations of UAV failures instead of relying only on manually written test cases.

The current verification suite evaluates:

- Individual failures
- Sequential failures
- Simultaneous failures
- Recovery behavior
- Boundary conditions
- Invalid state transitions

A total of **61 verification scenarios** are currently executed.

## State Transition Tracing

Every scenario records its state evolution.

Example:

```text
NORMAL
→ communication_loss
→ LOITER
→ critical_battery
→ LAND
```

This allows BobGuard to identify not only whether a test failed, but also where the unsafe transition occurred.

## Safety Violation Detection

BobGuard detects several classes of unsafe behavior, including:

```text
STUCK_IN_LOITER
RETURN_HOME_WITHOUT_GPS
AIRBORNE_CRITICAL_BATT
NO_SAFE_TERMINAL
FORBIDDEN_STATE_VISITED
UNEXPECTED_TRANSITION
```

Detected violations are classified by severity:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

## Defects Found During Development

IBM Bob identified and repaired three defects in the original failsafe implementation.

| Bug | Description | Fix |
|---|---|---|
| BUG-3 | Critical battery in RETURN_HOME was ignored | Added critical-battery handling to RETURN_HOME |
| BUG-4 | RETURN_HOME could be commanded without GPS | Added GPS availability guard |
| BUG-5 | NORMAL recovery could bypass active failures | Added active-failure checks before recovery |

Only minimal modifications were made to the original implementation.

## Verification Results

### Before Repair

```text
Original scenarios: 8 / 10 PASS
Pass rate:          80%
Unsafe states:      2
```

### After Repair

```text
Original tests:     10 / 10 PASS
Regression tests:   12 / 12 PASS
Edge-case tests:    13 / 13 PASS
Combination tests:  26 / 26 PASS
Full verification:  61 / 61 PASS
Critical violations: 0
High violations:     0
Low diagnostics:     6  (expected LOITER-with-active-failure operational notes)
Unsafe states:       0
```

## Mutation Testing

Passing tests alone does not demonstrate that a verification system can discover unknown defects.

BobGuard therefore includes mutation testing.

Five realistic defects were injected into the verified implementation.

| Mutation | Injected defect | Detected |
|---|---|---|
| M1 | Critical battery priority failure | YES |
| M2 | Return-to-Home without GPS | YES |
| M3 | Lost-link recovery bug | YES |
| M4 | LOITER / RETURN_HOME loop | YES |
| M5 | Battery threshold boundary error | YES |

Result:

```text
Injected mutations:      5
Detected mutations:      5
Missed mutations:        0
Mutation Detection Rate: 100%

Original suite after mutation testing:
61 / 61 PASS
```

The original implementation is restored after every mutation test.

## Example Workflow

A developer provides a UAV failsafe implementation.

IBM Bob can then:

```text
1. Read the failsafe implementation
2. Understand the defined safety requirements
3. Execute existing tests
4. Identify failing state transitions
5. Determine root causes
6. Repair the implementation
7. Generate additional regression tests
8. Generate failure combinations
9. Trace state transitions
10. Detect safety violations
11. Run mutation testing
12. Produce a verification report
```

## Why IBM Bob?

BobGuard uses IBM Bob as an agentic software engineering environment rather than only as a code-generation assistant.

Bob was used to:

- Analyze the existing implementation
- Diagnose state-machine defects
- Modify code
- Generate regression tests
- Extend the verification architecture
- Generate failure combinations
- Implement transition tracing
- Build safety violation detection
- Create mutation testing
- Generate verification reports

This demonstrates how an agentic development system can assist with safety-oriented robotics software engineering.

## Reports

BobGuard automatically generates human-readable reports containing:

- Tested scenario
- Injected failures
- State transition trace
- Safety violation
- Severity
- PASS / FAIL result
- Recommended fix

Generated reports include:

```text
bobguard_report.md
bobguard_verification_report.md
bobguard_mutation_report.md
```

## Running BobGuard

Run the complete verification suite:

```bash
python -m bobguard.verify
```

Run mutation testing:

```bash
python -m bobguard.mutate
```

Example output:

```text
BobGuard Verification
---------------------
Scenarios tested:   61
Passed:             61
Failed:             0
Critical violations:0
High violations:    0
Safe-state coverage:73%
```

Mutation validation:

```text
Injected mutations:      5
Detected mutations:      5
Mutation Detection Rate: 100%

RESULT:
ALL MUTATIONS DETECTED.
ORIGINAL SUITE INTACT.
```

## Scope and Limitations

BobGuard is currently a software-level proof of concept.

It does **not** claim to prove the complete safety of a real UAV.

The current implementation verifies defined software requirements against a simplified UAV failsafe state machine.

Future extensions could integrate:

- PX4
- ArduPilot
- ROS 2
- Hardware-in-the-loop simulation
- Software-in-the-loop simulation
- Formal verification
- Real flight logs
- Fault injection frameworks

## Hackathon Result

BobGuard demonstrates a complete agentic verification workflow:

```text
Requirements
    ↓
Failure Generation
    ↓
Execution
    ↓
Violation Detection
    ↓
Diagnosis
    ↓
Repair
    ↓
Regression Testing
    ↓
Mutation Validation
```

**61/61 verification scenarios passed after repair.**

**5/5 injected defects were independently detected.**

The result shows how IBM Bob can be used to transform manual UAV failsafe debugging into a repeatable software verification workflow.
