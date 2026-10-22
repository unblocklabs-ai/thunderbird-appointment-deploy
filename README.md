# Thunderbird Appointment on Charizard

Production deployment configuration for `meet.unblocklabs.ai`.

The upstream application is pinned to Thunderbird Appointment release `r-0891`.
Only the frontend is published on host loopback (`127.0.0.1:8090`); Cloudflare
Tunnel provides public TLS ingress. PostgreSQL and Redis remain private to the
Compose network.

## Deploy

1. Copy each `*.example` environment file to its filename without `.example`.
2. Replace all `replace-me` values with unique generated secrets.
3. For the original upstream build, run `docker compose config --quiet` and
   `docker compose build`. This is a base image, not a patched production image.
4. Apply and verify the [security runtime overlay](security/README.md), then run
   the explicit route below. Keep the existing local logging override intact.
5. Route `meet.unblocklabs.ai` to `http://localhost:8090` in the Charizard tunnel.

The current Charizard security deployment route is:

```bash
docker compose -f compose.yaml -f compose.override.yaml -f compose.security.yaml config --quiet
docker compose -f compose.yaml -f compose.override.yaml -f compose.security.yaml up -d --no-build --pull never
```

Do not run this broad `up` during the serial security cutover: retained rollback
containers have Compose labels. Use the reviewed per-service transaction and
preserve originals until rollout acceptance is complete. The patched images are
local-only, so a new host requires the documented rebuild recipe first.

## Verify

```bash
docker compose ps
curl -fsS http://127.0.0.1:8090/
curl -fsS https://meet.unblocklabs.ai/
curl -fsS https://meet.unblocklabs.ai/config.js
curl -fsS -X POST https://meet.unblocklabs.ai/api/v1/can-login \
  -H 'Content-Type: application/json' \
  --data '{"email":"healthcheck@unblocklabs.ai"}'
```

## Rollback

Restore the retained original container(s), their restart policy, and the backed
up Compose route. Backend and frontend must be restored together because the
frontend shares the backend network namespace. Do not run `compose down` or
delete PostgreSQL, Redis, or Mailpit volumes.
