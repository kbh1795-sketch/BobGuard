"""
BobGuard — UAV Failsafe State Machine
======================================
Simulates UAV failsafe logic without controlling real hardware.

States:   NORMAL, LOITER, RETURN_HOME, LAND, TERMINATED
Failures: communication_loss, gps_loss, critical_battery
"""

from enum import Enum, auto
from dataclasses import dataclass, field


class State(str, Enum):
    NORMAL = "NORMAL"
    LOITER = "LOITER"
    RETURN_HOME = "RETURN_HOME"
    LAND = "LAND"
    TERMINATED = "TERMINATED"


@dataclass
class UAVContext:
    """Mutable snapshot of active failure flags."""
    communication_loss: bool = False
    gps_loss: bool = False
    critical_battery: bool = False


class UAVStateMachine:
    """
    Intentionally buggy implementation for BobGuard diagnosis.

    Known design intent (safety requirements):
        R1. communication_loss  → NORMAL  → LOITER
        R2. comm restored + battery safe → LOITER → NORMAL
        R3. critical_battery must eventually lead to LAND
        R4. critical_battery has higher priority than LOITER
        R5. gps_loss prevents RETURN_HOME
        R6. No failure combination leaves UAV stuck in LOITER forever
        R7. Every scenario eventually reaches NORMAL, LAND, or TERMINATED
        R8. If communication is lost while already in RETURN_HOME:
              - GPS available   → RETURN_HOME may continue (no forced exit)
              - GPS unavailable → RETURN_HOME must not continue → LOITER
    """

    # Terminal states — no further transitions allowed
    TERMINAL_STATES = {State.LAND, State.TERMINATED}

    def __init__(self):
        self.state: State = State.NORMAL
        self.ctx: UAVContext = UAVContext()
        self.history: list[str] = []

    def _record(self, event: str):
        entry = f"{self.state.value}: {event}"
        self.history.append(entry)

    def apply_failure(self, failure: str):
        """Apply a failure flag and re-evaluate state."""
        if self.state in self.TERMINAL_STATES:
            return

        if failure == "communication_loss":
            self.ctx.communication_loss = True
        elif failure == "gps_loss":
            self.ctx.gps_loss = True
        elif failure == "critical_battery":
            self.ctx.critical_battery = True
        else:
            raise ValueError(f"Unknown failure: {failure}")

        self._record(f"failure={failure}")
        self._evaluate()

    def restore(self, failure: str):
        """Clear a failure flag and re-evaluate state."""
        if self.state in self.TERMINAL_STATES:
            return

        if failure == "communication_loss":
            self.ctx.communication_loss = False
        elif failure == "gps_loss":
            self.ctx.gps_loss = False
        elif failure == "critical_battery":
            self.ctx.critical_battery = False
        else:
            raise ValueError(f"Unknown failure: {failure}")

        self._record(f"restored={failure}")
        self._evaluate()

    def _evaluate(self):
        """
        BUG-SEEDED transition logic.
        Several requirements are intentionally violated here.
        """
        ctx = self.ctx

        # BUG-1 (violates R4): critical_battery check is only done inside
        # the LOITER branch, so transitioning from NORMAL with critical_battery
        # goes to LOITER first instead of directly to LAND.
        if ctx.communication_loss:
            if self.state == State.NORMAL:
                self.state = State.LOITER
                self._record("transition→LOITER")
                # BUG: does NOT re-evaluate critical_battery here

            elif self.state == State.LOITER:
                if ctx.critical_battery:
                    self.state = State.LAND
                    self._record("transition→LAND")

            elif self.state == State.RETURN_HOME:
                # R8: comm_loss during RETURN_HOME — only abort if GPS also lost.
                if ctx.gps_loss:
                    self.state = State.LOITER
                    self._record("transition→LOITER(comm_loss+gps_loss during RTH)")
                # else: GPS available → RETURN_HOME may continue (R8)

            # BUG-2 (violates R6): if both communication_loss AND gps_loss are
            # active there is no path out of LOITER — the restore() of
            # communication_loss falls into the else branch below which only
            # checks RETURN_HOME path, never escaping LOITER.
            return

        # No communication loss:
        if ctx.critical_battery:
            # FIX BUG-3: critical battery must lead to LAND from any state,
            # including RETURN_HOME (satisfies R3 and R7).
            if self.state in (State.NORMAL, State.LOITER, State.RETURN_HOME):
                self.state = State.LAND
                self._record("transition->LAND")
            return

        if ctx.gps_loss:
            # BUG-4 (violates R5 partially): gps_loss should block
            # RETURN_HOME, but the machine can still be commanded into
            # RETURN_HOME from outside; _evaluate only covers the
            # spontaneous transition, not an explicit command call.
            if self.state == State.RETURN_HOME:
                self.state = State.LOITER
                self._record("transition→LOITER(gps_loss)")
            return

        # All failures cleared — only return to NORMAL when every flag is off.
        # FIX: guard against gps_loss still being active (satisfies R6).
        if self.state == State.LOITER and not ctx.gps_loss and not ctx.critical_battery:
            # R2 — restore to NORMAL when comms are back and all flags clear
            self.state = State.NORMAL
            self._record("transition->NORMAL(restored)")

    def command_return_home(self):
        """Operator command to initiate return-to-home."""
        if self.state in self.TERMINAL_STATES:
            return
        # FIX BUG-4: block RETURN_HOME when GPS is unavailable (satisfies R5).
        if self.ctx.gps_loss:
            self.state = State.LOITER
            self._record("cmd->RETURN_HOME blocked(gps_loss)->LOITER")
            return
        self.state = State.RETURN_HOME
        self._record("cmd->RETURN_HOME")

    def command_land(self):
        """Operator command to land immediately."""
        if self.state in self.TERMINAL_STATES:
            return
        self.state = State.LAND
        self._record("cmd→LAND")

    def command_terminate(self):
        """Operator command to terminate (kill-switch)."""
        self.state = State.TERMINATED
        self._record("cmd→TERMINATED")
