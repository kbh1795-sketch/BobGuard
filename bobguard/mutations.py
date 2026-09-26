"""
BobGuard — Mutation Definitions
=================================
Each mutation is a dataclass that:
  - describes the injected bug
  - supplies a mutant_evaluate / mutant_command_return_home replacement
  - lists expected violation types that BobGuard should detect

All mutants are plain functions that accept (self) — compatible with
UAVStateMachine's instance methods.  They are swapped in/out at the
class level by the mutation runner (no file modifications).

Mutations
---------
M1  Critical battery priority failure
    comm_loss LOITER transition ignores critical_battery — UAV loiters
    on empty battery instead of landing.

M2  Unsafe Return-To-Home
    command_return_home() removes the gps_loss guard — UAV may navigate
    without GPS.

M3  Lost-link recovery bug
    When comm_loss is still active, LOITER → NORMAL transition fires
    anyway, letting the UAV fly without a ground link.

M4  LOITER ↔ RETURN_HOME loop
    Under gps_loss + comm_loss the machine alternates between LOITER and
    RETURN_HOME indefinitely, never reaching a safe terminal.

M5  Battery threshold boundary bug
    The critical_battery branch is silently dropped for NORMAL state,
    meaning a UAV in NORMAL flight on critical battery never lands.
"""

from dataclasses import dataclass
from typing import Callable
from bobguard.uav_failsafe import State


# ---------------------------------------------------------------------------
# Helpers shared by mutant bodies
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# M1 — Critical battery priority failure
#
# Bug: inside the communication_loss branch the LOITER→LAND transition is
# removed, so a critical battery while loitering goes unhandled.
# The UAV stays airborne on empty battery.
# ---------------------------------------------------------------------------

def _m1_evaluate(self) -> None:
    ctx = self.ctx
    if ctx.communication_loss:
        if self.state == State.NORMAL:
            self.state = State.LOITER
            self._record("transition->LOITER")
        # MUTATION: critical_battery check inside LOITER branch REMOVED
        # elif self.state == State.LOITER:
        #     if ctx.critical_battery:
        #         self.state = State.LAND
        return

    if ctx.critical_battery:
        if self.state in (State.NORMAL, State.LOITER, State.RETURN_HOME):
            self.state = State.LAND
            self._record("transition->LAND")
        return

    if ctx.gps_loss:
        if self.state == State.RETURN_HOME:
            self.state = State.LOITER
            self._record("transition->LOITER(gps_loss)")
        return

    if self.state == State.LOITER and not ctx.gps_loss and not ctx.critical_battery:
        self.state = State.NORMAL
        self._record("transition->NORMAL(restored)")


# ---------------------------------------------------------------------------
# M2 — Unsafe Return-To-Home (GPS guard removed from command handler)
# ---------------------------------------------------------------------------

def _m2_command_return_home(self) -> None:
    if self.state in self.TERMINAL_STATES:
        return
    # MUTATION: gps_loss guard REMOVED — allows RTH without GPS
    self.state = State.RETURN_HOME
    self._record("cmd->RETURN_HOME")


# ---------------------------------------------------------------------------
# M3 — Lost-link recovery bug
#
# Bug: the NORMAL restoration branch ignores whether communication_loss is
# still active, so the UAV transitions back to NORMAL mid-comm-loss.
# ---------------------------------------------------------------------------

def _m3_evaluate(self) -> None:
    ctx = self.ctx
    if ctx.communication_loss:
        if self.state == State.NORMAL:
            self.state = State.LOITER
            self._record("transition->LOITER")
        elif self.state == State.LOITER:
            if ctx.critical_battery:
                self.state = State.LAND
                self._record("transition->LAND")
        return

    if ctx.critical_battery:
        if self.state in (State.NORMAL, State.LOITER, State.RETURN_HOME):
            self.state = State.LAND
            self._record("transition->LAND")
        return

    if ctx.gps_loss:
        if self.state == State.RETURN_HOME:
            self.state = State.LOITER
            self._record("transition->LOITER(gps_loss)")
        return

    # MUTATION: guard removed — restores NORMAL even with comm_loss still set
    if self.state == State.LOITER:          # <-- missing: and not ctx.communication_loss
        self.state = State.NORMAL
        self._record("transition->NORMAL(restored-MUTANT)")


# ---------------------------------------------------------------------------
# M4 — LOITER ↔ RETURN_HOME infinite loop
#
# Bug: under simultaneous comm_loss + gps_loss:
#   - comm_loss block sends NORMAL → LOITER
#   - gps_loss block (reached because of return ordering bug) sends
#     LOITER → RETURN_HOME  (inverted direction of the gps guard)
#   The two triggers ping-pong the state, never reaching a terminal.
#   We simulate this as a single evaluate that creates the dangerous state.
# ---------------------------------------------------------------------------

def _m4_evaluate(self) -> None:
    ctx = self.ctx
    if ctx.communication_loss:
        if self.state == State.NORMAL:
            self.state = State.LOITER
            self._record("transition->LOITER")
        elif self.state == State.LOITER:
            if ctx.critical_battery:
                self.state = State.LAND
                self._record("transition->LAND")
        return

    if ctx.critical_battery:
        if self.state in (State.NORMAL, State.LOITER, State.RETURN_HOME):
            self.state = State.LAND
            self._record("transition->LAND")
        return

    if ctx.gps_loss:
        # MUTATION: direction inverted — LOITER pushed into RETURN_HOME
        # instead of RETURN_HOME pushed back to LOITER.
        if self.state == State.LOITER:
            self.state = State.RETURN_HOME
            self._record("transition->RETURN_HOME(MUTANT-gps_loss)")
        return

    if self.state == State.LOITER and not ctx.gps_loss and not ctx.critical_battery:
        self.state = State.NORMAL
        self._record("transition->NORMAL(restored)")


# ---------------------------------------------------------------------------
# M5 — Battery threshold boundary bug
#
# Bug: critical_battery from NORMAL state is silently skipped — only LOITER
# and RETURN_HOME trigger the landing sequence.  A UAV in normal flight on
# critical battery never lands autonomously.
# ---------------------------------------------------------------------------

def _m5_evaluate(self) -> None:
    ctx = self.ctx
    if ctx.communication_loss:
        if self.state == State.NORMAL:
            self.state = State.LOITER
            self._record("transition->LOITER")
        elif self.state == State.LOITER:
            if ctx.critical_battery:
                self.state = State.LAND
                self._record("transition->LAND")
        return

    if ctx.critical_battery:
        # MUTATION: NORMAL excluded — boundary check misses normal-flight state
        if self.state in (State.LOITER, State.RETURN_HOME):   # State.NORMAL removed
            self.state = State.LAND
            self._record("transition->LAND")
        return

    if ctx.gps_loss:
        if self.state == State.RETURN_HOME:
            self.state = State.LOITER
            self._record("transition->LOITER(gps_loss)")
        return

    if self.state == State.LOITER and not ctx.gps_loss and not ctx.critical_battery:
        self.state = State.NORMAL
        self._record("transition->NORMAL(restored)")


# ---------------------------------------------------------------------------
# Mutation registry
# ---------------------------------------------------------------------------

@dataclass
class Mutation:
    id: str                       # e.g. "M1"
    name: str                     # short label
    description: str              # what the bug does
    requirement_violated: str     # R-tag(s)
    patch_target: str             # "_evaluate" | "command_return_home"
    mutant_fn: Callable           # replacement method
    expected_violations: list[str]  # violation_type strings BobGuard should raise
    expected_severities: list[str]  # acceptable severity values


MUTATIONS: list[Mutation] = [
    Mutation(
        id="M1",
        name="Critical battery priority failure",
        description=(
            "Removes the LOITER→LAND transition when critical_battery fires "
            "during a communication loss event. UAV stays airborne on empty battery."
        ),
        requirement_violated="R3, R4",
        patch_target="_evaluate",
        mutant_fn=_m1_evaluate,
        expected_violations=["AIRBORNE_CRITICAL_BATT", "STUCK_IN_LOITER"],
        expected_severities=["CRITICAL", "HIGH"],
    ),
    Mutation(
        id="M2",
        name="Unsafe Return-To-Home",
        description=(
            "Removes the gps_loss guard from command_return_home(), allowing "
            "the operator to command autonomous navigation without GPS."
        ),
        requirement_violated="R5",
        patch_target="command_return_home",
        mutant_fn=_m2_command_return_home,
        expected_violations=["RETURN_HOME_WITHOUT_GPS", "FORBIDDEN_STATE_VISITED"],
        expected_severities=["CRITICAL"],
    ),
    Mutation(
        id="M3",
        name="Lost-link recovery bug",
        description=(
            "Removes the communication_loss guard from the LOITER→NORMAL "
            "restoration branch. UAV returns to NORMAL flight while the ground "
            "link is still down."
        ),
        requirement_violated="R2, R6",
        patch_target="_evaluate",
        mutant_fn=_m3_evaluate,
        expected_violations=["UNEXPECTED_TRANSITION", "NO_SAFE_TERMINAL"],
        expected_severities=["CRITICAL", "HIGH"],
    ),
    Mutation(
        id="M4",
        name="LOITER/RETURN_HOME loop",
        description=(
            "Inverts the GPS-loss guard direction: instead of RETURN_HOME→LOITER, "
            "the mutant pushes LOITER→RETURN_HOME under gps_loss, creating an "
            "unsafe navigation state after comm is restored."
        ),
        requirement_violated="R5, R7",
        patch_target="_evaluate",
        mutant_fn=_m4_evaluate,
        expected_violations=["RETURN_HOME_WITHOUT_GPS", "FORBIDDEN_STATE_VISITED",
                             "NO_SAFE_TERMINAL", "STUCK_IN_LOITER"],
        expected_severities=["CRITICAL", "HIGH"],
    ),
    Mutation(
        id="M5",
        name="Battery threshold boundary bug",
        description=(
            "Excludes State.NORMAL from the critical_battery landing branch. "
            "A UAV in normal flight with critical battery never transitions to LAND."
        ),
        requirement_violated="R3, R7",
        patch_target="_evaluate",
        mutant_fn=_m5_evaluate,
        expected_violations=["AIRBORNE_CRITICAL_BATT"],
        expected_severities=["CRITICAL"],
    ),
]
