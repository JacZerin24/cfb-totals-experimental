# OddsPapi Phase 1–2 implementation (November 19, 2026)

## Verified
- Production repository's existing OddsPapi account and NCAA market API authenticated.
- A prior read-only probe retrieved 69 fixtures, 609 full-game total markets and 1,218 priced outcome nodes (one bookmaker). The endpoint was confirmed, **but over/under outcome key names and provider quote timestamps were not verified**. A subsequent schema probe hit HTTP 429.
- Synthetic conversion tests passed in GitHub Actions run 43956464507.

## Added
- `research/convert_oddspapi_quotes.py`: conservative conversion, requiring explicit `over`/`under` keys and validated pre-kickoff timestamps; never guesses numeric outcome IDs.
- `research/capture_oddspapi.py`: bounded account/markets/odds requests, quota reserve, selected bookmaker, no raw response logging; writes AES-GCM-encrypted daily snapshots only.
- `.github/workflows/experimental-odds-capture.yml`: isolated scheduled Thu/Fri/Sat 15:13/21:13 UTC capture plus manual trigger; tests first, commits encrypted snapshots only. No production model/website writes.

## Required one-time configuration
Add **two secrets to this experimental repository** under Settings > Secrets and variables > Actions:
1. `ODDSPAPI_API_KEY`: the existing OddsPapi API key (copy securely from provider, do not paste in chat).
2. `ODDS_ARCHIVE_ENCRYPTION_KEY`: a long, randomly generated, securely backed-up secret (at least 32 random bytes encoded as hex). Loss of this key makes archived quotes unrecoverable. Do not rotate without a migration.

The production repository's Actions secrets **do not automatically transfer** to the experimental repository. With either secret absent, the workflow intentionally skips capture. Quote data is encrypted because this repository is public. Verify provider license permits storage of encrypted raw odds data before enabling.

## Remaining validation gate
- Verify actual provider outcome keys map correctly to over/under. If they are numeric, add mapping based on explicit, documented outcome metadata and tests; **never infer from position**.
- Verify market quote timestamps and provider update fields. `observed_utc` is collection time, not necessarily provider quote time.
- Validate live extraction yields >0 paired valid prices before treating capture as operational.
- Archive IDs are OddsPapi fixture IDs, **not CFBD game IDs**; a reviewed crosswalk is needed before model evaluation.
- Run workflow and confirm encrypted files appear; monitor quota and CI results. No real quote capture has been certified until this happens.

No betting or ROI claims are made.
