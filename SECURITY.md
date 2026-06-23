# Security Policy

`shotplanner` is a local command-line planning tool. It does not generate images, call external APIs, or transmit project data.

## Reporting

For security-sensitive issues, avoid posting private prompts, config files, `records.json` contents, or local file paths publicly unless they are redacted.

If this repository has private vulnerability reporting enabled on GitHub, use that channel. Otherwise, open a minimal public issue that describes the problem without sensitive data and note that details can be shared privately.

## Scope

Security reports may include issues related to:

- unsafe file writing or path handling
- accidental exposure of local prompt/config data
- packaging or dependency concerns
- malformed input that causes unexpected behavior

General feature requests, prompt quality concerns, and workflow bugs should use the normal issue templates.
