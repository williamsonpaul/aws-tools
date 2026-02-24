# aws-asg

A CLI tool for initiating and monitoring AWS Auto Scaling Group instance refreshes, packaged as both a Python package and a Docker container.

[![CI](https://github.com/williamsonpaul/aws-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/williamsonpaul/aws-tools/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/williamsonpaul/aws-tools)
[![Code Quality](https://img.shields.io/badge/code%20quality-A-brightgreen)](https://sonarcloud.io/dashboard?id=williamsonpaul_aws-tools)

## Purpose

`aws-asg` is a Python CLI tool that triggers and monitors rolling instance refreshes on AWS Auto Scaling Groups using the boto3 SDK. It provides a simple interface for starting refreshes and polling for completion, with JSON output suitable for scripting and CI/CD pipelines.

---

## Table of Contents

- [Quick Start](#quick-start)
- [CLI Usage](#cli-usage)
- [Docker Usage](#docker-usage)
- [Features](#features)
- [Architecture](#architecture)
- [Development](#development)
- [CI/CD Pipeline](#cicd-pipeline)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Install from source

```bash
git clone https://github.com/williamsonpaul/aws-tools.git
cd aws-tools

python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Run with Docker

```bash
docker pull ghcr.io/williamsonpaul/aws-tools:latest

docker run --rm \
  -e AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY \
  -e AWS_DEFAULT_REGION \
  ghcr.io/williamsonpaul/aws-tools:latest start my-asg
```

---

## CLI Usage

`aws-asg` has two subcommands: `start` and `check`.

### `aws-asg start`

Start a rolling instance refresh on an Auto Scaling Group.

```
Usage: aws-asg start [OPTIONS] ASG_NAME

Options:
  --min-healthy-percentage INTEGER  Minimum percentage of healthy instances
                                    during refresh  [default: 90]
  --instance-warmup INTEGER         Time in seconds until a new instance is
                                    considered warm
  --skip-matching                   Skip instances already using the latest
                                    launch template
  --region TEXT                     AWS region (defaults to
                                    environment/instance profile)
  --help                            Show this message and exit.
  
```

#### Examples

```bash
# Basic refresh with defaults (90% min healthy)
aws-asg start my-asg

# Custom min-healthy-percentage
aws-asg start my-asg --min-healthy-percentage 80

# With instance warmup and skip-matching
aws-asg start my-asg --instance-warmup 300 --skip-matching

# Specify region
aws-asg start my-asg --region eu-west-1

# All options
aws-asg start prod-asg \
  --min-healthy-percentage 75 \
  --instance-warmup 120 \
  --skip-matching \
  --region us-east-1
```

#### Output

```json
{
  "InstanceRefreshId": "08b91e03-1234-abcd-efgh-f3ea4912b73c",
  "AutoScalingGroupName": "my-asg"
}
```

### `aws-asg check`

Wait for an instance refresh to complete by polling until it reaches a terminal state. Status updates are printed to stderr; final JSON is written to stdout. Exits 0 on `Successful`, non-zero on `Failed`, `Cancelled`, or timeout.

```
Usage: aws-asg check [OPTIONS] ASG_NAME REFRESH_ID

Options:
  --region TEXT       AWS region (defaults to environment/instance profile)
  --interval INTEGER  Polling interval in seconds  [default: 30]
  --timeout INTEGER   Maximum wait time in seconds  [default: 3600]
  --help              Show this message and exit.
```

#### Examples

```bash
# Wait for a refresh to complete
aws-asg check my-asg 08b91e03-1234-abcd-efgh-f3ea4912b73c

# Custom polling interval and timeout
aws-asg check my-asg 08b91e03-1234-abcd-efgh-f3ea4912b73c \
  --interval 10 --timeout 600

# Start and then wait in a CI pipeline
REFRESH=$(aws-asg start my-asg | jq -r .InstanceRefreshId)
aws-asg check my-asg "$REFRESH"
```

### Environment Variables

All options can be set via environment variables:

| Option | Environment Variable |
|--------|---------------------|
| `ASG_NAME` (argument) | `ASG_NAME` |
| `REFRESH_ID` (argument) | `INSTANCE_REFRESH_ID` |
| `--min-healthy-percentage` | `MIN_HEALTHY_PERCENTAGE` |
| `--instance-warmup` | `INSTANCE_WARMUP` |
| `--skip-matching` | `SKIP_MATCHING` |
| `--region` | `AWS_DEFAULT_REGION` |
| `--interval` | `CHECK_INTERVAL` |
| `--timeout` | `CHECK_TIMEOUT` |

```bash
export ASG_NAME=my-asg
export MIN_HEALTHY_PERCENTAGE=80
export AWS_DEFAULT_REGION=us-east-1
aws-asg start
```

---

## Docker Usage

### Build locally

```bash
docker build -t aws-asg .
```

### Run with AWS credentials

```bash
# Using environment variables
docker run --rm \
  -e AWS_ACCESS_KEY_ID=AKIA... \
  -e AWS_SECRET_ACCESS_KEY=... \
  -e AWS_DEFAULT_REGION=us-east-1 \
  aws-asg start my-asg

# Forwarding credentials from the host environment
docker run --rm \
  -e AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY \
  -e AWS_SESSION_TOKEN \
  -e AWS_DEFAULT_REGION \
  aws-asg start my-asg --min-healthy-percentage 80

# Using an AWS credentials file
docker run --rm \
  -v ~/.aws:/root/.aws:ro \
  -e AWS_DEFAULT_REGION=eu-west-1 \
  aws-asg start my-asg
```

### Run with aws-vault

```bash
aws-vault exec my-profile -- docker run --rm \
  -e AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY \
  -e AWS_SESSION_TOKEN \
  -e AWS_DEFAULT_REGION \
  aws-asg start my-asg
```

### Run on EC2 with instance profile

When running inside AWS (EC2, ECS, Lambda), boto3 picks up the instance profile automatically — no credentials needed:

```bash
docker run --rm aws-asg start my-asg --region us-east-1
```

---

## Features

### AWS ASG Instance Refresh

- **Rolling strategy**: Uses AWS `StartInstanceRefresh` with `Strategy: Rolling`
- **Completion polling**: `check` subcommand waits for refresh to reach a terminal state
- **Configurable health threshold**: Set minimum healthy percentage (default 90%)
- **Instance warmup**: Optional warmup period for new instances
- **Skip matching**: Skip instances already on the latest launch template
- **JSON output**: Machine-readable output for scripting and CI pipelines
- **CI/CD friendly**: Non-zero exit on failure/timeout for pipeline integration

### Security & Quality Guardrails

- **Pre-commit GitGuardian**: Scans staged changes before commits
- **CI Repository History Scan**: Scans entire git history for secrets
- **Black + Flake8**: Consistent code style and PEP 8 compliance
- **Test Coverage**: 80% minimum enforced at commit and in CI
- **SonarCloud**: Code quality, security, and technical debt analysis
- **Semgrep**: Static analysis for security vulnerabilities
- **Conventional Commits**: Enforced format for automated versioning

### Six-Stage CI/CD Pipeline

1. **Lint and Test**: Pre-commit hooks + test suite with coverage reports
2. **GitGuardian History Scan**: Full repository secret detection across all commits
3. **SonarCloud**: Quality gate enforcement (main branch only)
4. **Semgrep**: Security vulnerability static analysis
5. **Build**: Docker image build and validation
6. **Release**: Automated semantic versioning and GitHub releases (main branch only)

---

## Architecture

### Multi-Layer Security Pipeline

```
Developer Commit
    ↓
┌─────────────────────────┐
│   Pre-commit Hooks      │
│  ─────────────────────  │
│  • GitGuardian Scan     │
│  • Test Coverage (80%)  │
│  • Conventional Commits │
│  • Black Formatting     │
│  • Flake8 Linting       │
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│    CI Pipeline          │
│  ─────────────────────  │
│  1. Lint & Test         │
│  2. GitGuardian (full)  │
│  3. SonarCloud          │
│  4. Semgrep             │
│  5. Build               │
│  6. Release             │
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│   Quality Gates         │
│  ─────────────────────  │
│  • Coverage ≥ 80%       │
│  • No Secrets           │
│  • No Security Issues   │
│  • Code Quality: A      │
└─────────────────────────┘
    ↓
Automated Release
```

### Project Structure

```
aws-tools/
├── src/aws_asg/             # Source code
│   ├── __init__.py              # Package initialization
│   ├── cli.py                   # Click CLI interface
│   └── core.py                  # Core refresh logic (boto3)
├── tests/                       # Test suite
│   ├── test_aws_asg.py      # Core logic tests
│   └── test_cli.py              # CLI tests
├── Dockerfile                   # Container image definition
├── .dockerignore
├── .github/workflows/
│   └── ci.yml                   # CI/CD pipeline (6 stages)
├── .claude/agents/              # Claude Code specialized agents
├── .pre-commit-config.yaml      # Pre-commit hook definitions
├── lefthook.yml                 # Lefthook configuration
├── pyproject.toml               # Package configuration
├── sonar-project.properties     # SonarCloud configuration
└── .releaserc.json              # Semantic-release config
```

---

## Development

### Setting Up

```bash
# 1. Clone and enter the repository
git clone https://github.com/williamsonpaul/aws-tools.git
cd aws-tools

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate
export PATH="$(pwd)/venv/bin:$PATH"

# 3. Install with dev dependencies
pip install -e ".[dev]"

# 4. Install pre-commit hooks
pre-commit install --install-hooks
pre-commit install --hook-type commit-msg

# 5. Set required environment variables
export GITGUARDIAN_API_KEY=your_api_key_here

# 6. Verify setup
pre-commit run --all-files
```

### Running Tests

```bash
source venv/bin/activate
export PATH="$(pwd)/venv/bin:$PATH"

# Run all tests with coverage
python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Run specific test file
python -m pytest tests/test_aws_asg.py -v

# Generate HTML coverage report
python -m pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Development Workflow

```bash
# 1. Set up environment (every terminal session)
source venv/bin/activate
export PATH="$(pwd)/venv/bin:$PATH"

# 2. Create feature branch
git checkout -b feat/new-feature

# 3. Make changes and add tests (maintain ≥80% coverage)

# 4. Commit with conventional format (hooks run automatically)
git add .
git commit -m "feat: add new feature"

# 5. If hooks auto-fix files, stage and amend
git status
git add .
git commit --amend --no-edit

# 6. Push and create PR
git push origin feat/new-feature
gh pr create
```

---

## CI/CD Pipeline

### Pipeline Stages

#### 1. Lint and Test
- Re-runs all pre-commit hooks in a clean environment
- Validates hooks weren't bypassed with `--no-verify`
- Runs test suite with coverage and uploads reports

#### 2. GitGuardian Repository History Scan
- Scans the **entire git history** with `ggshield secret scan repo .`
- Catches secrets in deleted files or old commits

#### 3. SonarCloud Quality Gate (main branch only)
- Coverage ≥ 80%, duplication < 3%
- Security hotspots must be reviewed
- Blocks merge if quality gate fails

#### 4. Semgrep Security Analysis
- Static analysis for security vulnerabilities
- Runs in parallel with SonarCloud

#### 5. Build
- `docker build` and `docker run --help` to validate the image

#### 6. Release (main branch only)
- Semantic-release analyses conventional commits
- Creates GitHub release with changelog and git tag

### Semantic Versioning

| Commit Type | Version Bump |
|-------------|--------------|
| `feat:` | Minor (0.1.0 → 0.2.0) |
| `fix:` | Patch (0.1.0 → 0.1.1) |
| `feat!:` / `BREAKING CHANGE:` | Major (0.1.0 → 1.0.0) |
| `docs:`, `ci:`, `chore:`, etc. | No release |

---

## Configuration

### Key Files

| File | Purpose |
|------|---------|
| `lefthook.yml` | Primary git hooks (requires tools in PATH) |
| `.pre-commit-config.yaml` | Alternative hooks with isolated environments |
| `.coveragerc` | Coverage config (`fail_under = 80`) |
| `pytest-precommit.ini` | Pytest config for pre-commit hook |
| `pyproject.toml` | Package config, dependencies, entry points |
| `.github/workflows/ci.yml` | CI/CD pipeline definition |
| `sonar-project.properties` | SonarCloud project config |
| `.releaserc.json` | Semantic-release versioning rules |

### Environment Variables

**Local Development**:
```bash
export GITGUARDIAN_API_KEY=your_api_key_here
export PATH="$(pwd)/venv/bin:$PATH"
```

**CI/CD (GitHub Secrets)**:
- `GITGUARDIAN_API_KEY`: GitGuardian API key
- `SONAR_TOKEN`: SonarCloud token
- `SEMGREP_APP_TOKEN`: Semgrep token
- `GITHUB_TOKEN`: Provided automatically by GitHub Actions

---

## Troubleshooting

### "flake8: not found" or "black: not found"

Lefthook requires tools to be in PATH:
```bash
source venv/bin/activate
export PATH="$(pwd)/venv/bin:$PATH"
```

### Coverage Below 80%

```bash
python -m pytest --cov=src --cov-report=term-missing
# Add tests for uncovered lines, then re-run
```

### GitGuardian API Key Not Set

```bash
export GITGUARDIAN_API_KEY=your_api_key_here
# Persist: echo 'export GITGUARDIAN_API_KEY=...' >> ~/.zshrc
```

### SonarCloud Quality Gate Fails

Check the "Check Quality Gate Status" step in CI logs. Common causes:
- Coverage below 80% → add tests
- Security hotspots not reviewed → review in SonarCloud UI
- Duplicated code > 3% → extract common code

### Commit Message Rejected

Commits must follow conventional format:
```bash
# Valid
git commit -m "feat: add new option"
git commit -m "fix: handle missing ASG name"

# Invalid
git commit -m "Added new option"    # wrong tense
git commit -m "feature: add thing"  # wrong type
```

---

## License

MIT License — see [LICENSE](LICENSE) file for details.

---

## Built With

- [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) — AWS SDK for Python
- [Click](https://click.palletsprojects.com/) — CLI framework
- [GitGuardian](https://www.gitguardian.com/) — Secret detection
- [SonarCloud](https://sonarcloud.io/) — Code quality analysis
- [Semantic Release](https://semantic-release.gitbook.io/) — Automated versioning
- [Pre-commit](https://pre-commit.com/) — Git hook management
- [Lefthook](https://github.com/evilmartians/lefthook) — Fast git hooks
