# Intelligent Search Command (Prometra v1.7.0)

Prometra v1.7.0 introduces the **Intelligent Search Engine** (`prometra search QUERY`), providing sub-150ms instant querying across all recorded development activity (Filesystem events, Git commits, AI prompts, AI responses, Tool invocations, Connectors, Session lifecycle) stored in your local SQLite database.

## Basic Usage

```bash
# Search for a file or keyword
prometra search "hello.py"

# Search for commit messages or git events
prometra search "git"

# Search for code logic or prompts
prometra search "authentication"
prometra search "jwt"
```

## Supported CLI Options

| Flag / Option | Description | Example |
| --- | --- | --- |
| `QUERY` | Search keyword or phrase (case-insensitive) | `prometra search "auth"` |
| `--type`, `-t` | Filter by category (`filesystem`, `git`, `ai`, `session`) | `prometra search "auth" --type git` |
| `--session`, `-s` | Filter events within a specific session ID | `prometra search "README" --session sess-123` |
| `--today` | Filter events recorded today | `prometra search "error" --today` |
| `--week` | Filter events recorded within the last 7 days | `prometra search "api" --week` |
| `--since` | Filter events starting from a specific date (`YYYY-MM-DD`) | `prometra search "jwt" --since 2026-07-01` |
| `--until` | Filter events up to a specific date (`YYYY-MM-DD`) | `prometra search "jwt" --until 2026-07-22` |
| `--limit`, `-l` | Limit the maximum number of search results returned | `prometra search "hello" --limit 10` |
| `--json` | Output results as structured JSON | `prometra search "jwt" --json` |
| `--markdown` | Output results as Markdown tables | `prometra search "README" --markdown` |
| `--export` | Export search results to a file (`.md`, `.json`) | `prometra search "auth" --export search_results.md` |

## Performance & Security

- **Parameterized SQL Queries**: All queries execute using safe parameterized SQL to completely eliminate SQL injection risks.
- **Sub-150ms Latency**: Designed and benchmarked to search 100,000+ timeline events in under 150 ms.
- **Rich Terminal UI**: Displays execution time, total result count, applied filter tags, and bold yellow keyword text highlighting.
