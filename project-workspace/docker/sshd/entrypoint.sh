#!/bin/bash
set -e

# Generate SSH host keys on first boot (they must not be baked into the
# image so every deployment gets its own host identity, matching real
# server practice).
ssh-keygen -A

# Install the student's public key if one has been mounted at
# /keys/authorized_keys. This same entrypoint is used for both the clean
# baseline (correct key mounted) and the instructor-seeded Stage 2 failure
# (a stale/mismatched key mounted instead) -- only the mounted file differs.
if [ -f /keys/authorized_keys ]; then
  cp /keys/authorized_keys /home/pho65user/.ssh/authorized_keys
else
  : > /home/pho65user/.ssh/authorized_keys
fi
chown pho65user:pho65user /home/pho65user/.ssh/authorized_keys
chmod 600 /home/pho65user/.ssh/authorized_keys

echo "Pho65 SSH server container started. Listening on port 22 (internal)."
exec /usr/sbin/sshd -D -e
