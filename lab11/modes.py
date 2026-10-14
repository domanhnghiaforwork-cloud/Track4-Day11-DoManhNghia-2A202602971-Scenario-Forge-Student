"""Part D: name the failure. TODO 8."""
from __future__ import annotations

from avsim import core


def label_mode(R: core.Rollout, k: int, event: dict, contact_type) -> str:
    """TODO 8. Name the kind of failure behind one ego failure event (a collision, or a crosswalk block). Return one of:

      'crosswalk_block' - the other party is the crossing pedestrian P1: the ego stopped with its body on the
                        crosswalk in P1's way (event["kind"] == "block"), or hit P1
      'rear_ended' - something ran into the ego from behind (use contact_type(R, k, event) == 'rear')
      'bus_bypass' - the ego hit C2 while C2 was squeezing past the stopped bus: at contact C2 is at x < 112 m
                     and slower than 6 m/s
      'cut_in'     - the ego hit C2 in any other situation
      'other'      - anything else
    Check in that order. Positions and speeds at contact: R.F[k, event["f"], core.IX["C2"]] (x is column 0, v is 4).
    """
    other = event["b"] if event["a"] == "ego" else event["a"]

    # 1. crosswalk_block
    if other == "P1":
        return "crosswalk_block"

    # 2. rear_ended
    if contact_type(R, k, event) == "rear":
        return "rear_ended"

    # 3. bus_bypass & 4. cut_in
    if other == "C2":
        f = event["f"]
        c2_idx = core.IX["C2"]
        x_c2 = R.F[k, f, c2_idx, 0]
        v_c2 = R.F[k, f, c2_idx, 4]
        if x_c2 < 112.0 and v_c2 < 6.0:
            return "bus_bypass"
        return "cut_in"

    # 5. other
    return "other"

