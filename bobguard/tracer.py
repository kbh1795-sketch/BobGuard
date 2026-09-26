"""
BobGuard — State Transition Tracer
=====================================
Wraps UAVStateMachine to record a structured, human-readable trace of every
state transition that occurs during scenario execution.

Trace format (per-event):
    TraceEvent(
        step_index  : int,
        trigger     : str,     # e.g. "failure=gps_loss", "cmd->RETURN_HOME"
        from_state  : State,
        to_state    : State,
        active_flags: dict,    # snapshot of ctx at the moment of transition
    )

The full trace can be rendered as a readable arrow chain, e.g.:

    NORMAL
      -> [failure=communication_loss] -> LOITER
      -> [failure=critical_battery]   -> LAND
"""

from dataclasses import dataclass, field
from typing import Optional
from bobguard.uav_failsafe import UAVStateMachine, State, UAVContext


@dataclass
class TraceEvent:
    step_index: int
    trigger: str
    from_state: State
    to_state: State
    active_flags: dict  # {"communication_loss": bool, "gps_loss": bool, "critical_battery": bool}


class TracingStateMachine(UAVStateMachine):
    """
    UAVStateMachine subclass that intercepts every state change and records
    a structured TraceEvent.  The public interface is identical to the base
    class so it can be dropped into any existing test runner.
    """

    def __init__(self):
        super().__init__()
        self.trace: list[TraceEvent] = []
        self._step_index: int = 0
        self._pending_trigger: str = ""
        self._pre_state: Optional[State] = None

    # ------------------------------------------------------------------
    # Override the two mutation points so we can capture before/after
    # ------------------------------------------------------------------

    def _record(self, event: str):
        """Called by base class after every state change / event."""
        super()._record(event)
        # If the state changed since _pre_state was captured, emit a TraceEvent
        if self._pre_state is not None and self._pre_state != self.state:
            self.trace.append(TraceEvent(
                step_index=self._step_index,
                trigger=self._pending_trigger,
                from_state=self._pre_state,
                to_state=self.state,
                active_flags=self._flags_snapshot(),
            ))
            self._pre_state = self.state  # update so chained changes are caught

    def _flags_snapshot(self) -> dict:
        return {
            "communication_loss": self.ctx.communication_loss,
            "gps_loss": self.ctx.gps_loss,
            "critical_battery": self.ctx.critical_battery,
        }

    # ------------------------------------------------------------------
    # Wrap every public action to set up trigger context
    # ------------------------------------------------------------------

    def apply_failure(self, failure: str):
        self._step_index += 1
        self._pending_trigger = f"failure={failure}"
        self._pre_state = self.state
        super().apply_failure(failure)

    def restore(self, failure: str):
        self._step_index += 1
        self._pending_trigger = f"restore={failure}"
        self._pre_state = self.state
        super().restore(failure)

    def command_return_home(self):
        self._step_index += 1
        self._pending_trigger = "cmd=return_home"
        self._pre_state = self.state
        super().command_return_home()

    def command_land(self):
        self._step_index += 1
        self._pending_trigger = "cmd=land"
        self._pre_state = self.state
        super().command_land()

    def command_terminate(self):
        self._step_index += 1
        self._pending_trigger = "cmd=terminate"
        self._pre_state = self.state
        super().command_terminate()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render_trace(self) -> str:
        """Return a multi-line human-readable transition chain."""
        lines = [f"  NORMAL"]
        for ev in self.trace:
            flag_str = ", ".join(
                k for k, v in ev.active_flags.items() if v
            ) or "none"
            lines.append(
                f"    -> [{ev.trigger}] -> {ev.to_state.value}"
                f"  (active: {flag_str})"
            )
        if not self.trace:
            lines.append("    (no transitions)")
        return "\n".join(lines)
