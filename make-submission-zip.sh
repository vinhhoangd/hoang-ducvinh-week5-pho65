#!/bin/bash
# Rebuild the Week 5 submission ZIP. Run from week5-student-starter/.
# Excludes: SQLite ledger, .git/, caches, .DS_Store, and anything token-shaped.
# The ngrok authtoken and SSH private key live outside the project and are
# never included.
set -e
cd "$(dirname "$0")"
F=hoang-ducvinh-week5-pho65-crm
STAGE=$(mktemp -d)
cp -R project-workspace "$STAGE/$F"
rm -rf "$STAGE/$F/.git" "$STAGE/$F/docker/inventory-data"
mkdir -p "$STAGE/$F/docker/inventory-data"
# ADI501-only templates: this is an ADI201 team (Steps 0-9 only).
rm -f "$STAGE/$F/evidence/roi-risk-memo.md" "$STAGE/$F/evidence/stakeholder-support.md" \
      "$STAGE/$F/evidence/build-vs-buy.md" "$STAGE/$F/evidence/pilot-memo.md"
find "$STAGE/$F" \( -name ".DS_Store" -o -name "__pycache__" -o -name "*.pyc" -o -name ".venv" -o -name "*.db" -o -name "ngrok.yml" -o -name "*.pem" -o -name ".env" \) -prune -exec rm -rf {} +
if grep -rqE "BEGIN [A-Z ]*PRIVATE ""KEY" "$STAGE/$F"; then echo "STOP: private key material found"; exit 1; fi
rm -f "$F.zip"
(cd "$STAGE" && zip -r -X -q "$OLDPWD/$F.zip" "$F")
rm -rf "$STAGE"
echo "Created $F.zip"
unzip -l "$F.zip" | tail -1
