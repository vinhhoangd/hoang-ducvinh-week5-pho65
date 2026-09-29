FROM debian:bookworm-slim

# Minimal Linux + OpenSSH server container for the Pho65 "remote ops" scenario.
# Purpose-built for teaching: real SSH connection, real key-based auth, real
# diagnosis of network/auth/app-logic failures. Not hardened for production use
# (this is a local, fabricated-credential teaching environment only).

RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-server sudo curl && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /var/run/sshd

# Non-root SSH user for the "café ops assistant" role.
# Fabricated account, local-only, no real credentials.
RUN useradd -m -s /bin/bash pho65user && \
    mkdir -p /home/pho65user/.ssh && \
    chmod 700 /home/pho65user/.ssh && \
    touch /home/pho65user/.ssh/authorized_keys && \
    chmod 600 /home/pho65user/.ssh/authorized_keys && \
    chown -R pho65user:pho65user /home/pho65user/.ssh

# sshd_config: key-based auth only (no password auth), no root login.
# PasswordAuthentication is disabled on purpose so the ONLY way in is the
# student's own generated key -- this is what makes the seeded auth failure
# (Stage 2: wrong/stale public key installed) meaningful and diagnosable.
COPY sshd_config /etc/ssh/sshd_config

# authorized_keys starts EMPTY in the clean baseline image. The student's
# public key is installed at container start time (see entrypoint.sh) from
# a mounted file at /keys/authorized_keys, so the same image works for both
# the clean baseline and the instructor-seeded (wrong-key) override.
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22

ENTRYPOINT ["/entrypoint.sh"]
