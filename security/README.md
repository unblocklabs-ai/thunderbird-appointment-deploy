# Incident-patched runtime images

The application remains Thunderbird Appointment **r-0891 / 1.5.3**. The security
images derive from the exact deployed images; they do not rebuild or upgrade
application dependencies.

The public staging implementation is `ops/charizard/security_images.py` in
`unblocklabs-ai/fleet-observability` at
`104d969908466d0ce18c58f5ae3f3e346158a862`. It removes both incident roots from
all discovered PEM stores, updates existing pip/certifi environments with
hash-pinned wheels, and replaces the frontend Node executable with the official
Node 24.22.1 Linux x64 binary. npm and application packages remain unchanged.

The backend and worker additionally run this directory's `ensurepip.py` during
their image build, with the same hash-verified pip 26.2.2 wheel. This replaces the
dormant bootstrap wheel as well as the installed pip. Merely updating installed
pip would leave the older trust bundle embedded in the ensurepip archive.

## Deployment and rebuild rules

- Include `compose.security.yaml` **last**, after the base file and the existing
  local logging override. `--no-build --pull never` prevents a plain upstream
  rebuild from silently replacing the security-derived images.
- Keep the original local base images, private staged build contexts and retained
  stopped rollback containers. These are local-only; never publish filesystem
  recovery snapshots or environment/configuration backups.
- Before rebuilding from a new upstream base, run the pinned staging recipe and
  ensurepip patch again, reverify all 14 incident chains and runtime versions,
  then update the owning image pins. The original `build:` configuration alone
  is **not** a security-image rebuild.
- Restart the worker only after the Redis appointment queue and `unacked` set are
  empty. Use a graceful stop; never force-kill an active job.
- The frontend shares the backend network namespace. Replace them as a paired
  transaction: stop frontend, replace backend, recreate frontend pointing to the
  new backend ID. Retain and restore both originals if application checks fail.
- After each cutover, verify actual HTTP routes and the scheduled Celery heartbeat,
  imported certifi/pip paths and versions, ensurepip 26.2.2, all 14 rejected chains,
  and unchanged application release. No database migration or app upgrade is part
  of this remediation.

Never run `compose down` or remove persistent volumes during this rollout. A
future Compose operation must explicitly account for retained rollback containers
that still carry the original Compose labels.

## Stateful support services — staged, not yet deployed

The postgres/redis/mailpit pins retain the exact deployed PostgreSQL **17.6**,
Redis **7.4.5**, and Mailpit **v1.27.11** executables and configuration. Only their
system CA bundle is filtered by the same published recipe. All 14 incident chains
were rejected by each staged store. These new pins must not be copied into the
live route until a coordinated serial cutover is approved.

For PostgreSQL, require no active application transaction, preserve the original
container and existing named volume, stop cleanly, and retain a bounded private
backup of the stopped data before replacement. Check `pg_isready`, an actual SQL
read, and the application's database health route afterward. No migration or
major-version upgrade is involved.

For Redis, first verify an empty Celery queue/unacked set and coordinate its
consumers. Preserve the AOF volume and confirm healthy persistence before/after
the graceful restart. Take a bounded private stopped-volume backup. Require
`PING`, application health and a fresh scheduled worker heartbeat afterward.

For Mailpit, preserve the existing `/data` named volume and private stopped-data
backup; verify readiness and its UI/API without sending or deleting email. The
`mailpit version` command may advertise a newer release; that is not permission
to update it as part of this CA-only change.
