# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

`aws-asg` is a Go CLI tool that triggers and monitors rolling instance refreshes on AWS Auto Scaling Groups. It outputs JSON suitable for scripting and CI/CD pipelines.

- **`main.go`** — cobra CLI (`start` and `check` subcommands)
- **`refresh.go`** — core AWS logic (aws-sdk-go-v2)
- **`refresh_test.go`** — unit tests (≥80% coverage required)

## Development Environment Setup

```bash
# 1. Install Go (1.23+)
brew install go   # macOS, or https://go.dev/dl/

# 2. Install Python tools for pre-commit and GitGuardian
pip install -r requirements-dev.txt

# 3. Install pre-commit hooks
pre-commit install --install-hooks
pre-commit install --hook-type commit-msg

# 4. Set required environment variables
export GITGUARDIAN_API_KEY=your_api_key_here

# 5. Verify setup
go build .
go test -race ./...
pre-commit run --all-files
```

## Testing Commands

```bash
# Run all tests with race detector
go test -race ./...

# Run with coverage report (80% minimum required)
go test -race -coverprofile=coverage.out ./...
go tool cover -func=coverage.out

# Run a specific test
go test -run TestStartRefresh_Success ./...

# Run all pre-commit hooks
pre-commit run --all-files
```

## CRITICAL Git Workflow Rules

**⚠️ NEVER BYPASS PRE-COMMIT HOOKS ⚠️**

1. **NEVER** use `git commit --no-verify`
2. **IF HOOKS FAIL** — fix all issues before retrying
3. **CHECK `git status`** after a failed commit — hooks may have modified files
4. **STAGE ANY CHANGES** made by hooks before re-committing
5. **ONLY PUSH** after ALL checks pass

### Correct Workflow

```bash
git add <files>
git commit -m "feat: add new feature"  # hooks run automatically

# If hooks modify files:
git status      # check for modifications
git add .       # stage hook fixes
git commit --amend --no-edit

# Verify before pushing
pre-commit run --all-files
git push
```

### Coverage Below 80%

```bash
go test -race -coverprofile=coverage.out ./...
go tool cover -func=coverage.out
# Add tests for uncovered lines, then re-run
```

## Architecture Overview

### Dual Hook System

**Lefthook** (`lefthook.yml`): fast parallel execution of `go vet`, `go test -race`, GitGuardian, yaml-check.

**Pre-commit** (`.pre-commit-config.yaml`): same checks in isolated environments; fallback if lefthook isn't installed.

Both must pass for a commit to succeed.

### CI/CD Pipeline (6 Stages)

1. **lint-and-test** — `go vet` + `go test -race -coverprofile=coverage.out`, pre-commit hooks
2. **gitguardian-scan** — full history scan with `ggshield secret scan repo .`
3. **sonarcloud** — quality gate (≥80% coverage, <3% duplication) — main branch only
4. **semgrep** — static security analysis
5. **build** — `docker build` + smoke test
6. **release** — semantic-release creates GitHub release + git tag — main branch only

### Secret Detection (Two-Layer)

- **Pre-commit**: `ggshield secret scan pre-commit` — staged changes only, fast
- **CI full scan**: `ggshield secret scan repo .` — entire history, catches bypassed commits

## Environment Variables

**Local Development**:
```bash
export GITGUARDIAN_API_KEY=your_api_key_here
```

**CI/CD (GitHub Secrets)**:
- `GITGUARDIAN_API_KEY` — GitGuardian secret scanning
- `SONAR_TOKEN` — SonarCloud integration
- `SEMGREP_APP_TOKEN` — Semgrep security analysis
- `GITHUB_TOKEN` — provided automatically by GitHub Actions

## SonarCloud MCP Integration

This project has SonarQube MCP server enabled (`.claude/settings.json`). You can query it directly:

```
Show me the quality gate status for this project
Give me a table of issues by severity
Show details for issue <issue-key>
Mark issue <issue-key> as false positive
```

## Conventional Commits (Enforced)

```
<type>(<scope>): <description>
```

| Type | Version bump |
|------|-------------|
| `feat:` | Minor (1.0.0 → 1.1.0) |
| `fix:` | Patch (1.0.0 → 1.0.1) |
| `feat!:` / `BREAKING CHANGE:` | Major (1.0.0 → 2.0.0) |
| `docs:`, `ci:`, `chore:`, etc. | No release |

## Claude Code Agents

Specialized agents in `.claude/agents/` for common tasks:

- **pre-push-validator** — MANDATORY validation before git push (use proactively)
- **precommit-validator** — validates all pre-commit hooks pass
- **secret-prescanner** — GitGuardian secret detection before commits
- **coverage-guardian** — ensures 80% test coverage
- **sonar-preflight** — predicts SonarCloud quality gate results
- **commit-formatter** — generates conventional commit messages
- **ci-failure-analyzer** — analyzes CI failures without making changes
- **workflow-debugger** — debugs GitHub Actions issues
- **release-notes** — generates release notes from commits

## Key Configuration Files

| File | Purpose |
|------|---------|
| `lefthook.yml` | Primary git hooks (`go vet`, `go test`, GitGuardian) |
| `.pre-commit-config.yaml` | Alternative hooks with isolated environments |
| `go.mod` / `go.sum` | Go module and dependency checksums |
| `.github/workflows/ci.yml` | CI/CD pipeline (6 stages) |
| `sonar-project.properties` | SonarCloud project config |
| `.releaserc.json` | Semantic-release versioning rules |

## Troubleshooting

### GitGuardian API Key Not Set

```bash
export GITGUARDIAN_API_KEY=your_api_key_here
```

### SonarCloud Quality Gate Fails

Check the "Check Quality Gate Status" step in CI logs. Common causes:
- Coverage below 80% → add tests
- Security hotspots not reviewed → review in SonarCloud UI
- Duplicated code > 3% → extract common code

### GitGuardian Scan Taking Too Long in CI

Full history scan is expected to take 1–3 minutes. Cannot be skipped — it's comprehensive security.

## Release Process

Fully automated on merge to `main`:

1. semantic-release analyses conventional commits since last release
2. Calculates version bump from commit types
3. Generates changelog and creates GitHub release with git tag
