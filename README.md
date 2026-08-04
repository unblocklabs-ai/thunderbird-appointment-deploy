# Thunderbird Appointment on Charizard

Production deployment configuration for `meet.unblocklabs.ai`.

The upstream application is pinned to Thunderbird Appointment release `r-0891`.
Only the frontend is published on host loopback (`127.0.0.1:8090`); Cloudflare
Tunnel provides public TLS ingress. PostgreSQL and Redis remain private to the
Compose network.

## Deploy

1. Copy each `*.example` environment file to its filename without `.example`.
2. Replace all `replace-me` values with unique generated secrets.
3. Run `docker compose config --quiet`.
4. Run `docker compose up -d --build`.
5. Route `meet.unblocklabs.ai` to `http://localhost:8090` in the Charizard tunnel.

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

```bash
docker compose down
```

Persistent PostgreSQL, Redis, and Mailpit volumes are retained by default.
