import sys

# def log_time(label, duration, source=None):
#     prefix = f"[{source}] " if source else ""
#     sys.stderr.write(f"{prefix}{label} {duration:.4f} seconds\n")
#     sys.stderr.flush()  # Ensure immediate output



"""
timing_logger.py
----------------
Provides two levels of timing support:

1. log_time()      — unchanged, writes immediately to stderr (console/log)
2. record_time()   — accumulates rows keyed by (scenario_id, description_type)
3. set_context()   — call once per file in batch_generate_gm before invoking AMG
4. flush_to_csv()  — call once at the end of the batch to write everything out

Typical call flow
-----------------
batch_generate_gm.py:
    timing_logger.set_context(sid, dtype)
    state = run_initial_from_description(...)   # internally calls record_time()
    ...
    timing_logger.flush_to_csv("timing_results.csv")

AMG_with_langgraph.py  (replace log_time calls with record_time where timing matters):
    from IM.timing_logger import log_time, record_time
    record_time("reasoner", duration)
    record_time("amg_gen",  duration)
"""

import sys
import csv
import os
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# Module-level state  (acts like a lightweight singleton)
# ─────────────────────────────────────────────────────────────────────────────

_current_scenario:         Optional[str] = None
_current_description_type: Optional[str] = None

# Each entry: {"scenario_id", "description_type", "reasoner_time_s",
#              "amg_gen_time_s", "total_time_s"}
_timing_rows: list[dict] = []

# Tracks the in-progress row so partial times can be accumulated
_active_row: Optional[dict] = None


# ─────────────────────────────────────────────────────────────────────────────
# 1. Original stderr logger — UNCHANGED
# ─────────────────────────────────────────────────────────────────────────────

def log_time(label: str, duration: float, source: Optional[str] = None) -> None:
    """Write a timing line to stderr immediately (existing behaviour)."""
    prefix = f"[{source}] " if source else ""
    sys.stderr.write(f"{prefix}{label} {duration:.4f} seconds\n")
    sys.stderr.flush()


# ─────────────────────────────────────────────────────────────────────────────
# 2. Context setter — call once per file in the batch loop
# ─────────────────────────────────────────────────────────────────────────────

def set_context(scenario_id: str, description_type: str) -> None:
    """
    Set the current scenario and description type.
    Creates a fresh in-progress row for this file.

    Call this in batch_generate_gm.py just before run_initial_from_description().
    """
    global _current_scenario, _current_description_type, _active_row

    _current_scenario         = str(scenario_id).strip()
    _current_description_type = str(description_type).strip().lower()

    _active_row = {
        "scenario_id":       _current_scenario,
        "description_type":  _current_description_type,
        "reasoner_time_s":   None,
        "amg_gen_time_s":    None,
        "total_time_s":      None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. record_time — call from AMG_with_langgraph inside each node
# ─────────────────────────────────────────────────────────────────────────────

_LABEL_MAP = {
    # Keys that AMG_with_langgraph uses          → CSV column
    "reasoner":  "reasoner_time_s",
    "amg_gen":   "amg_gen_time_s",
    "amg":       "amg_gen_time_s",     # alias
}

def record_time(label: str, duration: float, source: Optional[str] = None) -> None:
    """
    Store a named duration into the active timing row AND write to stderr.

    label must be one of: 'reasoner', 'amg_gen' (or alias 'amg').
    Falls back to log_time-only behaviour for any unrecognised label.

    Args:
        label    : timing category ('reasoner' | 'amg_gen')
        duration : elapsed seconds (float)
        source   : optional source tag for the stderr line
    """
    global _active_row

    # Always mirror to stderr so existing log behaviour is preserved
    log_time(label, duration, source)

    col = _LABEL_MAP.get(label.lower().strip())
    if col is None or _active_row is None:
        # Unknown label or context not set — just log, don't crash
        return

    _active_row[col] = round(duration, 4)

    # Recompute total whenever both timings are available
    r = _active_row.get("reasoner_time_s")
    a = _active_row.get("amg_gen_time_s")
    if r is not None and a is not None:
        _active_row["total_time_s"] = round(r + a, 4)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Commit active row — call after run_initial_from_description() returns
# ─────────────────────────────────────────────────────────────────────────────

def commit_row() -> None:
    """
    Push the current active row into the accumulated list.
    Call this in batch_generate_gm.py right after run_initial_from_description()
    succeeds (or in the except block for failed rows).
    """
    global _active_row
    if _active_row is not None:
        _timing_rows.append(dict(_active_row))
        _active_row = None


# ─────────────────────────────────────────────────────────────────────────────
# 5. flush_to_csv — call once at the end of run_batch()
# ─────────────────────────────────────────────────────────────────────────────

CSV_HEADERS = [
    "scenario_id",
    "description_type",
    "reasoner_time_s",
    "amg_gen_time_s",
    "total_time_s",
]

def flush_to_csv(output_path: str, append: bool = False) -> None:
    """
    Write all accumulated timing rows to a CSV file.

    Args:
        output_path : full path to the output .csv file
        append      : if True and file exists, append rows without rewriting header
    """
    if not _timing_rows:
        sys.stderr.write("[timing_logger] No timing rows to flush.\n")
        return

    mode        = "a" if append and os.path.exists(output_path) else "w"
    write_header = not (append and os.path.exists(output_path))

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with open(output_path, mode, newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_HEADERS, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        writer.writerows(_timing_rows)

    sys.stderr.write(
        f"[timing_logger] Flushed {len(_timing_rows)} rows → {output_path}\n"
    )
    _timing_rows.clear()