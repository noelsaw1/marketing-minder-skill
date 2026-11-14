# Recipe: Ahrefs data in Insightful Pipe

Use this recipe when the user wants Ahrefs metrics in Insightful Pipe through a generic REST API connector. First check the integrations actually offered in their workspace; prefer a suitable native connector when available. This is a preparation guide, not a shipped OpenAPI converter or a guarantee that a connector has been activated.

## What was observed

The 2026-11-14 setup session reported a 524,288-byte manifest limit, a 200-value enum cap, OpenAPI compatibility errors and invalid enum defaults. Those are historical observations, not current provider contracts. The full-spec size, endpoint count, native-integration count and UI labels can change. Check the current connector's validation result instead of copying old counts.

The earlier inline sanitizer was removed after QA showed it silently omitted required endpoints/unresolved references and could turn an integer enum into a string. Changing the `openapi` version field does not convert a schema. There is no validated generated manifest bundled in this repository.

## Choose the queries

Start from the current [Ahrefs API documentation](https://docs.ahrefs.com/en/api/docs/introduction) and its linked OpenAPI specification. Confirm endpoint availability, required parameters, response fields and account entitlement for the intended queries. These six paths are the original candidate set, not a promise they all exist in a later specification:

| Candidate GET path | Intended use |
|---|---|
| `/site-explorer/metrics` | Domain traffic overview |
| `/site-explorer/domain-rating` | Domain rating |
| `/site-explorer/organic-keywords` | Ranking queries |
| `/site-explorer/top-pages` | Organic landing pages |
| `/site-explorer/backlinks-stats` | Backlink overview |
| `/keywords-explorer/overview` | Keyword research |

Include only the queries the business needs. Do not expose write operations as part of this read-only integration. API calls can consume units; agree the test query and limits before running one. Ahrefs documents [free test queries and usage considerations](https://docs.ahrefs.com/en/api/docs/introduction).

## Prepare and validate a compatible manifest

Use a provider-supplied compatible subset or a schema-aware conversion process appropriate to the connector's supported OpenAPI version. If neither is available, stop with the specific validation error; do not claim the old snippet solves it.

1. Resolve the business folder using `skills/marketing-manager/SKILL.md`, confirm `brands/` is gitignored, and use `brands/<business-slug>/ahrefs-openapi.json`. Preserve an existing working manifest before replacement. Record upstream URL/retrieval date and selected endpoints beside the local artifact. Keep credentials out of every manifest and report.
2. Require every selected path and GET operation to exist. Missing operations must be reported, not silently filtered out. Preserve operation parameters, response schemas and relevant security declarations; check operation-level overrides as well as global security.
3. Resolve all references, including nested dependencies and any external references, using the source's reference rules. Unresolved references stop preparation. Preserve original types and constraints. If a documented connector limit requires narrowing an enum, explicitly document that loss of validation and keep upstream value restrictions available to the caller; never turn every large enum into a string.
4. Validate the resulting document against its declared version and supported connector dialect. In particular, newer JSON Schema constructs are not made OpenAPI 3.0-compatible by replacing a version string or deleting `examples`. Consult the [OpenAPI 3.0.3 specification](https://spec.openapis.org/oas/v3.0.3) if that is the required target. Record validator/version, result and remaining limitations.
5. Measure the actual saved UTF-8 file (`wc -c < brands/<business-slug>/ahrefs-openapi.json`, replacing the placeholder). Compare with the connector's current byte limit. A compact in-memory serialization does not establish the size of an indented file. No “under 100 KB” guarantee applies.
6. Preview in the connector and confirm all selected GET endpoints, authentication and parameters are recognized. An accepted preview is not proof of correct API results. Any later functional test must use the agreed query/allowance and record its outcome without tokens or private response data in this repo.

## Prepare the connection; user activates

Follow `skills/marketing-manager/SKILL.md` → Connect accounts in another tool. The user handles account selection, consent and secrets. Never ask them to paste an API key into chat, write it to source, or include it in an issue/PR.

In the observed UI: Connected accounts → Add integration → REST API; name the connection Ahrefs; use Bearer-token authentication as required by the current API documentation. The user enters their key in the tool's secret field. Paste/upload only the validated manifest, then inspect the endpoint preview. If previewing would itself send API requests, first confirm it is within the agreed query allowance.

Leave **Save & activate** to the user under the parent skill's connection protocol. Report what was prepared, any validation failures and whether activation is still pending. Verify activation from the resulting UI before reporting it as active.

## Alternative: direct Ahrefs MCP

If the user only needs Ahrefs data in their AI client, consult the current [official Ahrefs MCP setup](https://docs.ahrefs.com/en/mcp/docs/introduction) and the guide for their client. Prefer that documented route over maintaining a custom REST manifest when it meets the need. The user completes the authorization; do not install configurations or connect accounts merely because this recipe was read.

Public documentation checked 2026-11-14. This QA pass did not access an Ahrefs account or validate a live Insightful Pipe connection.
