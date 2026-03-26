#!/usr/bin/env python3
"""
Extract game stats JSON from Unity session logs.
Searches for "Experience Stats Uploaded" in output_log_*.txt files,
extracts the JSON block that follows, and saves each as a separate file.
"""

import os
import re
import json
import glob

SESSION_LOG_DIR = os.path.join(os.path.dirname(__file__), "session-log")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")

def extract_stats_from_file(filepath):
    """Extract the stats JSON from a single log file."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Find "Experience Stats Uploaded" then capture the JSON block that follows
    marker = "Experience Stats Uploaded."
    idx = content.find(marker)
    if idx == -1:
        return None

    # Find the opening brace after the marker
    json_start = content.find("{", idx)
    if json_start == -1:
        return None

    # Track braces to find the complete JSON object
    depth = 0
    json_end = json_start
    for i in range(json_start, len(content)):
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
            if depth == 0:
                json_end = i + 1
                break

    json_str = content[json_start:json_end]

    # The log format may have a trailing pipe on the last line — clean it
    json_str = json_str.rstrip().rstrip("|")

    try:
        data = json.loads(json_str)
        return data
    except json.JSONDecodeError as e:
        print(f"  JSON parse error in {filepath}: {e}")
        return None


def extract_timestamp_from_file(filepath, marker="Experience Stats Uploaded"):
    """Extract the log timestamp from the line containing the marker."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if marker in line:
                # Timestamp is at the start of the line: 2026-03-26T15:39:06.2274521+08:00|...
                ts_match = re.match(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})", line)
                if ts_match:
                    return ts_match.group(1)
    return None


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    log_files = sorted(glob.glob(os.path.join(SESSION_LOG_DIR, "**", "output_log_*.txt"), recursive=True))
    print(f"Found {len(log_files)} log files to scan")

    extracted = 0
    for filepath in log_files:
        data = extract_stats_from_file(filepath)
        if data is None:
            continue

        # Skip low-score test sessions (automated bot runs)
        team = data.get("stats", {}).get("team", [{}])[0]
        team_name = team.get("name", "")
        score = team.get("score", 0)
        if score < 30000:
            continue

        # Build output filename from the log filename
        # e.g. output_log_sbvrdev-260326-T4-151445.txt -> sbvrdev-260326-T4-151445.json
        basename = os.path.basename(filepath)
        session_id = basename.replace("output_log_", "").replace(".txt", "")

        # Add timestamp to the data for reference
        timestamp = extract_timestamp_from_file(filepath)
        if timestamp:
            data["_extracted"] = {
                "source": basename,
                "timestamp": timestamp,
                "session_id": session_id
            }

        output_path = os.path.join(OUTPUT_DIR, f"{session_id}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        extracted += 1
        print(f"  [{extracted}] {session_id} — {team_name}: {score:,}")

    print(f"\nDone! Extracted {extracted} sessions to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
