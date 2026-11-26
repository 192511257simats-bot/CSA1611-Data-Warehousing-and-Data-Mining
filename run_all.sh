#!/usr/bin/env bash
# Re-generates every output (txt, png, csv, arff) from the repository root.
# Needs: Python 3.9+ (pip install -r requirements.txt) and R 4.x (Rscript).
set -u
cd "$(dirname "$0")"
for d in day1 day2 day3 day4/assignment day4/exercises day5; do mkdir -p $d/output; done
for f in day1/q*.R day2/q*.R day4/exercises/q*.R; do
  echo "running $f"; Rscript "$f" > "$(dirname $f)/output/$(basename ${f%.R}).txt" 2>&1 || echo "  !! FAILED $f"
done
for f in day3/q*.py day4/assignment/q*.py day4/exercises/q*.py day5/q*.py; do
  echo "running $f"; python3 "$f" > "$(dirname $f)/output/$(basename ${f%.py}).txt" 2>&1 || echo "  !! FAILED $f"
done
echo "done - open the output/ folder next to each script"
