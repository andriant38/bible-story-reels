"""Count A/B votes for a POV-series part from pasted comments.

Usage: python engine/tally_votes.py comments_ig.txt comments_tiktok.txt ...

File format: one comment per line, as "username: comment text".
Lines without "username:" each count as a separate anonymous voter.
One account = one vote (its LAST A/B comment counts, per file order).
A vote is a standalone letter A or B, e.g. "A", "a!", "pilih B 🙏", "B dong".
A comment mentioning both A and B is ignored.
"""
import re
import sys

VOTE = re.compile(r"(?<![A-Za-z])([AaBb])(?![A-Za-z])")


def main(paths):
    votes, anon = {}, 0
    for path in paths:
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            user, _, text = line.partition(":") if ":" in line else ("", "", line)
            found = {m.upper() for m in VOTE.findall(text)}
            if len(found) != 1:
                continue
            key = f"{path}:{user.strip().lower()}" if user.strip() else f"anon{(anon := anon + 1)}"
            votes[key] = found.pop()
    a = sum(v == "A" for v in votes.values())
    b = sum(v == "B" for v in votes.values())
    total = a + b
    if not total:
        sys.exit("no votes found")
    print(f"A: {a} ({a * 100 / total:.0f}%)")
    print(f"B: {b} ({b * 100 / total:.0f}%)")
    print("Winner:", "A" if a > b else "B" if b > a else "TIE (see series doc tie rule)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
