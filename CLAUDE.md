# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This repository demonstrates GitGuardian integration in CI/CD workflows to prevent secrets from entering codebases. It's designed as a template/example for teams implementing robust secret detection and automated release processes. The functional component is a Python CLI acronym generator built with Click.

**Documentation Files**:
- `/BLOG.md` - Main blog post about "Automated Guard Rails for Vibe Coding"
- `/README.md` - Complete project documentation with architecture diagrams

## Development Environment Setup

```bash
# CRITICAL: This project uses BOTH lefthook AND pre-commit hooks
# lefthook requires tools (black, flake8, pytest) available in PATH
# pre-commit manages its own isolated environments

# 1. Create and activate virtual environment (REQUIRED)
python3 -m venv venv
source venv/bin/activate

# 2. Install project with ALL dev dependencies
pip install -e ".[dev]"

# 3. Install pre-commit hook environments
pre-commit install --install-hooks
pre-commit install --hook-type commit-msg

# 4. Verify setup - ALL hooks must pass
export PATH="$(pwd)/venv/bin:$PATH"  # Ensure lefthook finds tools
pre-commit run --all-files
```

**PATH Configuration**: Lefthook hooks (black, flake8, pytest) require tools in PATH. Always export the venv bin directory to PATH before git operations:
```bash
export PATH="/path/to/venv/bin:$PATH"
```

## Testing Commands

```bash
# ALWAYS activate venv and set PATH first
source venv/bin/activate
export PATH="$(pwd)/venv/bin:$PATH"

# Run tests with coverage (80% minimum required)
python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Run specific test file
python -m pytest tests/test_acronym_creator.py -v

# Run specific test function
python -m pytest tests/test_acronym_creator.py::TestAcronymCreator::test_basic_acronym -v

# View coverage HTML report
python -m pytest --cov=src --cov-report=html
open htmlcov/index.html

# Run all pre-commit hooks (includes coverage check)
pre-commit run --all-files

# Run specific hook
pre-commit run pytest --all-files
pre-commit run black --all-files
```

## CRITICAL Git Workflow Rules

**⚠️ NEVER BYPASS PRE-COMMIT HOOKS ⚠️**

This project has BOTH lefthook and pre-commit hooks that MUST pass before pushing:

### Mandatory Pre-commit Workflow

1. **ALWAYS** ensure venv is activated and in PATH before committing
2. **NEVER** use `git commit --no-verify` - this bypasses critical security and quality checks
3. **IF HOOKS FAIL** - STOP IMMEDIATELY and fix all issues
4. **CHECK `git status`** - hooks may auto-fix files (black formatting, trailing whitespace)
5. **STAGE AUTO-FIXES** - `git add .` any files modified by hooks
6. **ONLY PUSH** after ALL checks pass

### Correct Workflow Example

```bash
# Set up environment
source venv/bin/activate
export PATH="$(pwd)/venv/bin:$PATH"

# Make changes and commit
git add .
git commit -m "feat: add new feature"  # Hooks run automatically

# If hooks modify files (e.g., black formatting):
git status  # Check for modified files
git add .   # Stage auto-fixes
git commit --amend --no-edit  # Include fixes in commit

# Verify all hooks pass before pushing
pre-commit run --all-files
git push
```

### Hook Failure Recovery

**Tools Not Found (flake8, black, pytest)**:
```bash
# Ensure venv is activated and in PATH
source venv/bin/activate
export PATH="$(pwd)/venv/bin:$PATH"

# Verify tools are installed
which black flake8 pytest

# If missing, reinstall dev dependencies
pip install -e ".[dev]"
```

**Coverage Below 80%**:
```bash
# Generate detailed coverage report
python -m pytest --cov=src --cov-report=term-missing

# Add tests for uncovered lines
# Re-run until coverage ≥ 80%
```

## Architecture Overview

### Dual Hook System

This project uses **both lefthook and pre-commit**:

**Lefthook** (`lefthook.yml`):
- Fast, parallel hook execution
- Runs black, flake8, pytest, gitguardian, yaml-check
- Requires tools in PATH (venv/bin)
- Used by default when installed

**Pre-commit** (`.pre-commit-config.yaml`):
- Manages isolated hook environments
- Same hooks as lefthook but in isolated environments
- Fallback if lefthook not available

Both systems run the same checks - either must pass for commits to succeed.

### CI/CD Pipeline (5 Sequential Stages)

1. **lint-and-test**: Re-runs all pre-commit checks in clean environment
   - Validates hooks weren't bypassed with `--no-verify`
   - Generates coverage artifacts for SonarCloud
   - Ensures reproducible builds

2. **gitguardian-scan**: Full repository history scan
   - Scans **entire git history** with `ggshield secret scan repo .`
   - Catches secrets in deleted files or old commits
   - Slower than pre-commit scan but comprehensive

3. **sonarcloud**: Code quality gate (main branch only)
   - Requires ≥80% coverage, <3% duplication
   - Security hotspots must be reviewed
   - Blocks merge if quality gate fails

4. **semgrep**: Security analysis
   - Static analysis for security vulnerabilities
   - Runs in parallel with sonarcloud

5. **build**: Package validation
   - Verifies package builds correctly
   - Generates distribution artifacts

6. **release**: Automated versioning (main branch only)
   - Analyzes conventional commits
   - Creates GitHub releases with changelogs

### Test Coverage Enforcement (80% Minimum)

Coverage enforced at **three levels**:

1. **Pre-commit hook**: Blocks commits <80% coverage
2. **CI pipeline**: Re-validates coverage in clean environment
3. **SonarCloud**: Quality gate requires ≥80% coverage

**Configuration**:
- `.coveragerc`: Main config with `data_file = /tmp/.coverage_precommit` (prevents repo modifications)
- `pytest-precommit.ini`: Pytest config for pre-commit hook
- `pyproject.toml`: Package-level coverage settings

### Secret Detection (Two-Layer)

**Layer 1 - Pre-commit** (`ggshield secret scan pre-commit`):
- Scans **staged changes only**
- Fast feedback before commit
- Blocks commit if secrets found

**Layer 2 - CI Full Scan** (`ggshield secret scan repo .`):
- Scans **entire repository history**
- Catches bypassed commits (`--no-verify`)
- Detects secrets in deleted files or old commits

## Environment Variables

**Local Development**:
```bash
export GITGUARDIAN_API_KEY=your_api_key_here  # Required for ggshield
export PATH="$(pwd)/venv/bin:$PATH"           # Required for lefthook
```

**CI/CD (GitHub Secrets)**:
- `GITGUARDIAN_API_KEY`: GitGuardian API for secret scanning
- `SONAR_TOKEN`: SonarCloud integration
- `SEMGREP_APP_TOKEN`: Semgrep security analysis

## SonarCloud MCP Integration

This project has SonarQube MCP server enabled (`.claude/settings.json`). Available MCP tools:

```bash
# Get quality gate status
Show me the quality gate status for this project

# Search for issues
Give me a table of issues by severity

# View specific issues
Show details for issue <issue-key>

# Change issue status
Mark issue <issue-key> as false positive
```

**Common SonarCloud Issues**:
- **Security hotspots not reviewed**: Review in SonarCloud UI, cannot be auto-fixed
- **Coverage below 80%**: Add tests to increase coverage
- **Code smells**: Refactor code per SonarCloud recommendations

## Conventional Commits (Enforced)

Commit format enforced by hooks (commit-msg stage):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:
- `feat:` → Minor version bump (0.1.0 → 0.2.0)
- `fix:` → Patch version bump (0.1.0 → 0.1.1)
- `feat!:` or `BREAKING CHANGE:` → Major version bump (0.1.0 → 1.0.0)
- `docs:`, `style:`, `refactor:`, `test:`, `build:`, `ci:`, `chore:`, `revert:` → No release

**Examples**:
```bash
git commit -m "feat: add syllable-based acronym generation"
git commit -m "fix: resolve unused parameter warning in core.py"
git commit -m "feat!: change CLI argument structure

BREAKING CHANGE: --include-articles flag now requires explicit boolean value"
```

## Claude Code Agents

Specialized agents in `.claude/agents/` for common tasks:

- **pre-push-validator**: MANDATORY validation before git push (use proactively)
- **precommit-validator**: Validates all pre-commit hooks pass
- **secret-prescanner**: GitGuardian secret detection before commits
- **coverage-guardian**: Ensures 80% test coverage
- **sonar-preflight**: Predicts SonarCloud quality gate results
- **commit-formatter**: Generates conventional commit messages
- **ci-failure-analyzer**: Analyzes CI failures without making changes
- **workflow-debugger**: Debugs GitHub Actions issues
- **release-notes**: Generates release notes from commits

## Key Configuration Files

| File | Purpose | Critical Settings |
|------|---------|------------------|
| `lefthook.yml` | Primary git hooks (requires tools in PATH) | black, flake8, pytest, gitguardian |
| `.pre-commit-config.yaml` | Alternative hooks with isolated environments | Same as lefthook but managed |
| `.coveragerc` | Coverage config | `fail_under = 80`, `data_file = /tmp/...` |
| `pytest-precommit.ini` | Pytest config for hooks | Coverage settings, test paths |
| `pyproject.toml` | Python package config | Dependencies, entry points, pytest/coverage |
| `.github/workflows/ci.yml` | CI/CD pipeline | 5-stage pipeline definition |
| `sonar-project.properties` | SonarCloud config | Quality gate, coverage paths |
| `.releaserc.json` | Semantic-release config | Versioning rules, changelog |

## Troubleshooting

### "flake8: not found" or "black: not found"

**Cause**: Lefthook can't find tools because venv not in PATH

**Fix**:
```bash
source venv/bin/activate
export PATH="$(pwd)/venv/bin:$PATH"
git commit ...
```

### Pre-commit Hooks Pass but Still Get Errors

**Cause**: Lefthook runs first and may fail even if pre-commit would pass

**Fix**: Ensure both hook systems can find tools:
```bash
# Install pre-commit environments
pre-commit install --install-hooks

# Ensure venv tools in PATH for lefthook
export PATH="$(pwd)/venv/bin:$PATH"
```

### Coverage Failures in CI but Passes Locally

**Cause**: Different coverage configurations or missing test files

**Fix**:
```bash
# Use exact CI command locally
python -B -m pytest -c pytest-precommit.ini -p no:cacheprovider

# Check for .gitignore'd test files
git status --ignored
```

### GitGuardian Scan Taking Too Long in CI

**Cause**: Full history scan (`ggshield secret scan repo .`) scans all commits

**Expected**: 1-3 minutes for typical repositories. This is comprehensive security and cannot be skipped.

### SonarCloud Quality Gate Fails

**Check CI Logs**: "Check Quality Gate Status" step shows detailed failures

**Common Issues**:
```bash
# Security hotspots not reviewed (cannot auto-fix)
# → Review in SonarCloud UI

# Coverage below 80%
python -m pytest --cov=src --cov-report=term-missing
# → Add tests

# Code smells
# → Refactor per SonarCloud recommendations
```

## Release Process

Fully automated - no manual intervention required:

1. Merge to `main` triggers semantic-release
2. Analyzes commits since last release
3. Calculates version from commit types
4. Generates changelog
5. Creates GitHub release with git tag

**Manual Release Trigger** (if needed):
```bash
# Trigger release workflow manually
gh workflow run release
```
