```ad-info
title: ExploitContext Overview

Use `ExploitContext` to centralize configuration, session, and metadata across stages of your exploit.

- `from_args()` builds it from CLI arguments
- `from_file()` restores saved state
- `ctx.web_url()` / `ctx.api_url()` return usable base URLs
- `ctx.save()` persists current state to disk
- Ideal for chaining exploit phases cleanly

```

```ad-tip
title: Using .env for Config

If you prefer not to pass long CLI arguments, load variables from a `.env` file using `dotenv_values()`.

- Keys like `TARGET_IP`, `PROXY`, `LISTENING_PORT`
- Can be parsed and cast into types manually
- Combine with defaults for resilience
- Use `parse_config()` to simplify validation
```

```ad-note
title: Logging Strategy

Build a minimal logger early in your PoC for audit trails and debugging:

- Log to both console and `logs/poc.log`
- Use severity levels: DEBUG, INFO, ERROR
- Include timestamps and exploit stage info
- Optional: support JSON output for replayability
```

```ad-example
title: IdentityGenerator Integration

Use a reusable identity provider to generate unique accounts across labs:

- Randomized usernames, emails, and passwords
- Optional: enforce complexity (`low`, `medium`, `high`)
- Can include phone, address, UUID, etc.
- Save to `user.json` for later reuse
```