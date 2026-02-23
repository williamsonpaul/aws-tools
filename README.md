# Acronym Creator

A robust Python CLI tool demonstrating comprehensive CI/CD best practices, security controls, and automated quality gates.

[![CI](https://github.com/reaandrew/acronymcreator/actions/workflows/ci.yml/badge.svg)](https://github.com/reaandrew/acronymcreator/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen)](https://github.com/reaandrew/acronymcreator)
[![Code Quality](https://img.shields.io/badge/code%20quality-A-brightgreen)](https://sonarcloud.io/dashboard?id=reaandrew_acronymcreator)

## Purpose

This repository serves dual purposes:

1. **Security & CI/CD Template**: Demonstrates enterprise-grade development workflows with multi-layer secret detection, automated testing, and quality gates
2. **Functional CLI Tool**: A feature-rich acronym generator built with Python Click framework

Perfect for teams implementing secure development practices or developers learning robust CI/CD patterns.

---

## Table of Contents

- [Quick Start](#quick-start)
- [CLI Usage & Examples](#cli-usage--examples)
- [Features](#features)
- [Architecture](#architecture)
- [Development](#development)
- [CI/CD Pipeline](#cicd-pipeline)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/reaandrew/acronymcreator.git
cd acronymcreator

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install with development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install --install-hooks
pre-commit install --hook-type commit-msg
```

### Basic Usage

```bash
# Generate a simple acronym
acronymcreator "Hello World"
# Output: HW

# Get help
acronymcreator --help

# Check version
acronymcreator --version
```

---

## CLI Usage & Examples

The `acronymcreator` command provides flexible acronym generation with multiple options and output formats.

### Basic Acronym Generation

**Feature**: Generate acronyms by taking the first letter of each significant word (articles and common words excluded by default)

```bash
# Simple phrase
$ acronymcreator "Hello World"
HW

# Technical terms
$ acronymcreator "Application Programming Interface"
API

# Excludes articles automatically
$ acronymcreator "The Quick Brown Fox"
QBF

# Multiple word phrase
$ acronymcreator "Portable Document Format"
PDF

# With special characters (automatically cleaned)
$ acronymcreator "Really Simple Syndication!"
RSS
```

### Including Articles and Common Words

**Feature**: Use `--include-articles` to include articles (a, an, the) and common words (and, or, but, in, on, at, to, for, of, with, by, from, etc.) in the acronym

```bash
# Default behavior (excludes articles)
$ acronymcreator "The Quick Brown Fox"
QBF

# Include articles
$ acronymcreator "The Quick Brown Fox" --include-articles
TQBF

# Real-world example
$ acronymcreator "Frequently Asked Questions"
FAQ

$ acronymcreator "Frequently Asked Questions" --include-articles
FAQ
# (No difference - no articles in phrase)

# With prepositions
$ acronymcreator "Point of Sale"
PS

$ acronymcreator "Point of Sale" --include-articles
POS
```

### Lowercase Output

**Feature**: Use `--lowercase` to generate lowercase acronyms instead of the default uppercase

```bash
# Default uppercase
$ acronymcreator "Hello World"
HW

# Lowercase output
$ acronymcreator "Hello World" --lowercase
hw

# Useful for programming identifiers
$ acronymcreator "User Interface Component" --lowercase
uic

# Combined with other options
$ acronymcreator "The Quick Brown Fox" --include-articles --lowercase
tqbf
```

### Limiting Number of Words

**Feature**: Use `--max-words N` to limit the acronym to the first N words, useful for long phrases

```bash
# Long phrase, all words
$ acronymcreator "One Two Three Four Five Six"
OTTTFS

# Limit to first 3 words
$ acronymcreator "One Two Three Four Five Six" --max-words 3
OTT

# Real-world example
$ acronymcreator "North Atlantic Treaty Organization" --max-words 4
NATO

# Combined with articles
$ acronymcreator "The United States of America" --max-words 3
US
# (Only processes "The United States", excludes "The")

$ acronymcreator "The United States of America" --max-words 3 --include-articles
TUS
```

### Minimum Word Length Filter

**Feature**: Use `--min-length N` to exclude words shorter than N characters (default is 2)

```bash
# Default (min-length 2)
$ acronymcreator "A Big Red Car"
BRC

# Increase minimum to 3 characters
$ acronymcreator "A Big Red Car" --min-length 3
BRC
# (Same result - 'A' already excluded)

# With articles included
$ acronymcreator "A Big Red Car" --include-articles
ABRC

$ acronymcreator "A Big Red Car" --include-articles --min-length 3
BRC
# ('A' excluded due to length)

# Practical example
$ acronymcreator "To Be Or Not To Be" --include-articles --min-length 3
Not
# (Only 'Not' is 3+ characters)
```

### JSON Output Format

**Feature**: Use `--format json` to get structured output with metadata, perfect for scripting and integrations

```bash
# Default text format
$ acronymcreator "Hello World"
HW

# JSON format with metadata
$ acronymcreator "Hello World" --format json
{
  "phrase": "Hello World",
  "acronym": "HW",
  "options": {
    "include_articles": false,
    "min_word_length": 2,
    "max_words": null,
    "lowercase": false
  }
}

# JSON with all options
$ acronymcreator "The Quick Brown Fox" --include-articles --max-words 3 --lowercase --format json
{
  "phrase": "The Quick Brown Fox",
  "acronym": "tqb",
  "options": {
    "include_articles": true,
    "min_word_length": 2,
    "max_words": 3,
    "lowercase": true
  }
}
```

### YAML Output Format

**Feature**: Use `--format yaml` to get human-readable structured output, ideal for configuration management and documentation

```bash
# Default text format
$ acronymcreator "Hello World"
HW

# YAML format with metadata
$ acronymcreator "Hello World" --format yaml
acronym: HW
options:
  include_articles: false
  lowercase: false
  max_words: null
  min_word_length: 2
phrase: Hello World

# YAML with all options
$ acronymcreator "The Quick Brown Fox" --include-articles --max-words 3 --lowercase --format yaml
acronym: tqb
options:
  include_articles: true
  lowercase: true
  max_words: 3
  min_word_length: 2
phrase: The Quick Brown Fox

# Real-world use case: Generating configuration files
$ acronymcreator "Database Management System" --format yaml > dbms-config.yaml
$ cat dbms-config.yaml
acronym: DMS
options:
  include_articles: false
  lowercase: false
  max_words: null
  min_word_length: 2
phrase: Database Management System
```

### CSV Output Format

**Feature**: Use `--format csv` to get structured tabular output, perfect for spreadsheets and data analysis tools

```bash
# Default text format
$ acronymcreator "Hello World"
HW

# CSV format with header and data row
$ acronymcreator "Hello World" --format csv
phrase,acronym,include_articles,min_word_length,max_words,lowercase
Hello World,HW,false,2,,false

# CSV with include-articles option
$ acronymcreator "The Quick Brown Fox" --include-articles --format csv
phrase,acronym,include_articles,min_word_length,max_words,lowercase
The Quick Brown Fox,TQBF,true,2,,false

# CSV with lowercase option
$ acronymcreator "The Quick Brown Fox" --include-articles --lowercase --format csv
phrase,acronym,include_articles,min_word_length,max_words,lowercase
The Quick Brown Fox,tqbf,true,2,,true

# CSV with all options
$ acronymcreator "The Quick Brown Fox Jumps" --include-articles --lowercase --min-length 3 --max-words 3 --format csv
phrase,acronym,include_articles,min_word_length,max_words,lowercase
"The Quick Brown Fox Jumps",tqb,true,3,3,true

# Real-world use case: Export to file for spreadsheet analysis
$ acronymcreator "Database Management System" --format csv > acronyms.csv
$ cat acronyms.csv
phrase,acronym,include_articles,min_word_length,max_words,lowercase
Database Management System,DMS,false,2,,false

# Batch processing multiple phrases into CSV
$ echo "phrase,acronym,include_articles,min_word_length,max_words,lowercase" > batch_acronyms.csv
$ for phrase in "Hello World" "Foo Bar Baz" "Quick Brown Fox"; do
    acronymcreator "$phrase" --format csv | tail -n 1 >> batch_acronyms.csv
  done
$ cat batch_acronyms.csv
phrase,acronym,include_articles,min_word_length,max_words,lowercase
Hello World,HW,false,2,,false
Foo Bar Baz,FBB,false,2,,false
Quick Brown Fox,QBF,false,2,,false
```

**CSV Features**:
- Standard RFC 4180 compliant CSV format
- Proper quoting and escaping of special characters
- Compatible with Excel, Google Sheets, pandas, R, and other data tools
- Header row included for easy data import
- Empty cells for optional fields (like `max_words` when not specified)

### TSV Output Format

**Feature**: Use `--format tsv` to get tab-separated values output, ideal for data analysis tools and database imports

```bash
# Default text format
$ acronymcreator "Hello World"
HW

# TSV format with header and data row
$ acronymcreator "Hello World" --format tsv
phrase	acronym	include_articles	min_word_length	max_words	lowercase
Hello World	HW	false	2		false

# TSV with include-articles option
$ acronymcreator "The Quick Brown Fox" --include-articles --format tsv
phrase	acronym	include_articles	min_word_length	max_words	lowercase
The Quick Brown Fox	TQBF	true	2		false

# TSV with lowercase option
$ acronymcreator "The Quick Brown Fox" --include-articles --lowercase --format tsv
phrase	acronym	include_articles	min_word_length	max_words	lowercase
The Quick Brown Fox	tqbf	true	2		true

# TSV with all options
$ acronymcreator "The Quick Brown Fox Jumps" --include-articles --lowercase --min-length 3 --max-words 3 --format tsv
phrase	acronym	include_articles	min_word_length	max_words	lowercase
The Quick Brown Fox Jumps	tqb	true	3	3	true

# Real-world use case: Export to file for data analysis
$ acronymcreator "Database Management System" --format tsv > acronyms.tsv
$ cat acronyms.tsv
phrase	acronym	include_articles	min_word_length	max_words	lowercase
Database Management System	DMS	false	2		false

# Batch processing multiple phrases into TSV
$ echo -e "phrase\tacronym\tinclude_articles\tmin_word_length\tmax_words\tlowercase" > batch_acronyms.tsv
$ for phrase in "Hello World" "Foo Bar Baz" "Quick Brown Fox"; do
    acronymcreator "$phrase" --format tsv | tail -n 1 >> batch_acronyms.tsv
  done
$ cat batch_acronyms.tsv
phrase	acronym	include_articles	min_word_length	max_words	lowercase
Hello World	HW	false	2		false
Foo Bar Baz	FBB	false	2		false
Quick Brown Fox	QBF	false	2		false

# Import into pandas (Python)
$ python3 -c "import pandas as pd; df = pd.read_csv('acronyms.tsv', sep='\t'); print(df)"
                        phrase acronym  include_articles  min_word_length max_words  lowercase
0  Database Management System     DMS             false                2       NaN      false
```

**TSV Features**:
- Tab-separated values format for data interchange
- Proper escaping of special characters including tabs and quotes
- Compatible with databases, data warehousing tools, and SQL imports
- Works seamlessly with pandas, R, Excel, and other data analysis tools
- Handles data containing commas better than CSV format
- Header row included for easy data import
- Empty cells for optional fields (like `max_words` when not specified)
- Ideal for batch processing and data pipelines

### TOML Output Format

**Feature**: Use `--format toml` to get human-readable configuration format output, ideal for modern Python projects and configuration management

```bash
# Default text format
$ acronymcreator "Hello World"
HW

# TOML format
$ acronymcreator "Hello World" --format toml
phrase = "Hello World"
acronym = "HW"
include_articles = false
min_word_length = 2
max_words = ""
lowercase = false

# TOML with include-articles option
$ acronymcreator "The Quick Brown Fox" --include-articles --format toml
phrase = "The Quick Brown Fox"
acronym = "TQBF"
include_articles = true
min_word_length = 2
max_words = ""
lowercase = false

# TOML with lowercase option
$ acronymcreator "Hello World" --lowercase --format toml
phrase = "Hello World"
acronym = "hw"
include_articles = false
min_word_length = 2
max_words = ""
lowercase = true

# TOML with all options
$ acronymcreator "The Quick Brown Fox Jumps" --include-articles --lowercase --min-length 3 --max-words 3 --format toml
phrase = "The Quick Brown Fox Jumps"
acronym = "tqb"
include_articles = true
min_word_length = 3
max_words = 3
lowercase = true

# Real-world use case: Generate configuration files
$ acronymcreator "Database Management System" --format toml > dbms-config.toml
$ cat dbms-config.toml
phrase = "Database Management System"
acronym = "DMS"
include_articles = false
min_word_length = 2
max_words = ""
lowercase = false
```

**TOML Features**:
- Human-readable configuration format
- Strong typing (booleans as `true`/`false`, integers as numbers)
- Compatible with Python projects (`pyproject.toml`, `poetry`, etc.)
- Proper escaping of special characters
- Flat key-value structure for simple acronym data
- Native support in Python 3.11+ (`tomllib`) for reading

### Combining Multiple Options

**Feature**: All options can be combined for precise control over acronym generation

```bash
# Lowercase acronym from first 4 words, including articles
$ acronymcreator "The Lord of the Rings" --include-articles --max-words 4 --lowercase
tlot

# Filter short words, limit to 3 words
$ acronymcreator "A Very Long Description Of Something" --min-length 4 --max-words 3
VLD

# JSON output with custom filtering
$ acronymcreator "International Business Machines" --max-words 3 --lowercase --format json
{
  "phrase": "International Business Machines",
  "acronym": "ibm",
  "options": {
    "include_articles": false,
    "min_word_length": 2,
    "max_words": 3,
    "lowercase": true
  }
}

# CSV output with custom filtering
$ acronymcreator "International Business Machines" --max-words 3 --lowercase --format csv
phrase,acronym,include_articles,min_word_length,max_words,lowercase
International Business Machines,ibm,false,2,3,true
```

### Real-World Examples

```bash
# Technology acronyms
$ acronymcreator "Hypertext Markup Language"
HTML

$ acronymcreator "Cascading Style Sheets"
CSS

$ acronymcreator "JavaScript Object Notation"
JSON

$ acronymcreator "Structured Query Language"
SQL

# Organizations
$ acronymcreator "National Aeronautics and Space Administration"
NASA

$ acronymcreator "North Atlantic Treaty Organization"
NATO

# Business terms
$ acronymcreator "Chief Executive Officer"
CEO

$ acronymcreator "Return on Investment"
ROI

$ acronymcreator "Key Performance Indicator"
KPI

# Create lowercase variable names
$ acronymcreator "User Interface Controller" --lowercase
uic

$ acronymcreator "Database Connection Pool" --lowercase
dcp
```

### Error Handling

```bash
# Empty phrase (no valid words after filtering)
$ acronymcreator "a an the" --min-length 10
Error: No acronym could be generated from the given phrase.

# Special characters only
$ acronymcreator "!@#$%"
Error: No acronym could be generated from the given phrase.
```

### Shell Scripting Examples

```bash
# Store acronym in variable
ACRONYM=$(acronymcreator "Application Programming Interface")
echo "The acronym is: $ACRONYM"
# Output: The acronym is: API

# Process multiple phrases
for phrase in "Hello World" "Foo Bar Baz" "Quick Brown Fox"; do
  echo "$phrase -> $(acronymcreator "$phrase")"
done
# Output:
# Hello World -> HW
# Foo Bar Baz -> FBB
# Quick Brown Fox -> QBF

# JSON parsing with jq
acronymcreator "Hello World" --format json | jq -r '.acronym'
# Output: HW

# Conditional processing
if acronymcreator "Test Phrase" --lowercase | grep -q "tp"; then
  echo "Acronym contains 'tp'"
fi
```

---

## Features

### 🔒 Comprehensive Security & Quality Guardrails

#### Multi-Layer Secret Protection
- **Pre-commit GitGuardian**: Scans staged changes before commits
- **CI Repository History Scan**: Scans entire git history for secrets
- **Blocks pipeline on detection**: Prevents secrets from reaching production

#### Code Quality Enforcement
- **Black Code Formatting**: Consistent Python code style
- **Flake8 Linting**: PEP 8 compliance and code quality checks
- **Test Coverage**: 80% minimum threshold enforced at commit and CI
- **SonarCloud Analysis**: Code quality, security, and technical debt assessment
- **Semgrep Security**: Static analysis for security vulnerabilities

#### Commit Standards
- **Conventional Commits**: Enforced format for automated versioning
- **Pre-commit Validation**: All quality checks run before commit acceptance
- **CI Re-validation**: Clean environment re-runs of all quality checks

### 🚀 Six-Stage CI/CD Pipeline

1. **Lint and Test**: Pre-commit hooks + comprehensive testing with coverage reports
2. **GitGuardian History Scan**: Full repository secret detection across all commits
3. **SonarCloud**: Code quality analysis with quality gate enforcement (main branch only)
4. **Semgrep**: Security vulnerability static analysis (parallel with SonarCloud)
5. **Build**: Package validation and artifact generation
6. **Release**: Automated semantic versioning and GitHub releases (main branch only)

### 🧪 Professional Python Package

- **Click CLI Framework**: Professional command-line interface with rich options
- **Comprehensive Testing**: Unit tests with pytest and 97% coverage
- **Package Structure**: Standard Python package with proper entry points
- **Development Tools**: Pre-commit hooks, linting, and automated formatting

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
acronymcreator/
├── src/acronymcreator/          # Source code
│   ├── __init__.py              # Package initialization
│   ├── cli.py                   # Click CLI interface
│   └── core.py                  # Core acronym logic
├── tests/                       # Test suite
│   ├── test_acronym_creator.py  # Core logic tests
│   └── test_cli.py              # CLI tests
├── .github/workflows/           # CI/CD pipelines
│   ├── ci.yml                   # Main CI pipeline (6 stages)
│   └── auto-fix-ci.yml          # Auto-fix workflow
├── .claude/agents/              # Claude Code specialized agents
├── .pre-commit-config.yaml      # Pre-commit hook definitions
├── lefthook.yml                 # Alternative hook manager
├── pyproject.toml               # Package configuration
├── .coveragerc                  # Coverage settings
├── pytest-precommit.ini         # Pytest configuration
├── sonar-project.properties     # SonarCloud configuration
└── .releaserc.json              # Semantic-release config
```

---

## Development

### Setting Up Development Environment

```bash
# 1. Clone repository
git clone https://github.com/reaandrew/acronymcreator.git
cd acronymcreator

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install with dev dependencies
pip install -e ".[dev]"

# 4. Install pre-commit hooks
pre-commit install --install-hooks
pre-commit install --hook-type commit-msg

# 5. Set environment variables
export GITGUARDIAN_API_KEY=your_api_key_here
export PATH="$(pwd)/venv/bin:$PATH"

# 6. Verify setup
pre-commit run --all-files
```

### Running Tests

```bash
# Activate environment
source venv/bin/activate
export PATH="$(pwd)/venv/bin:$PATH"

# Run all tests with coverage
python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Run specific test file
python -m pytest tests/test_acronym_creator.py -v

# Run specific test
python -m pytest tests/test_cli.py::test_basic_usage -v

# Generate HTML coverage report
python -m pytest --cov=src --cov-report=html
open htmlcov/index.html

# Run tests in watch mode (requires pytest-watch)
pip install pytest-watch
ptw
```

### Development Workflow

```bash
# 1. Set up environment (every terminal session)
source venv/bin/activate
export PATH="$(pwd)/venv/bin:$PATH"

# 2. Create feature branch
git checkout -b feat/new-feature

# 3. Make changes and add tests (maintain 80% coverage)

# 4. Run pre-commit checks
pre-commit run --all-files

# 5. Commit with conventional format
git add .
git commit -m "feat: add new acronym generation feature"

# 6. If hooks auto-fix files, stage and amend
git status  # Check for modified files
git add .
git commit --amend --no-edit

# 7. Push to remote
git push origin feat/new-feature

# 8. Create pull request
gh pr create --title "feat: add new feature" --body "Description"
```

### Pre-commit Hooks

This project uses **both lefthook and pre-commit** hook managers:

**Hooks run automatically on commit**:
- ✅ Black code formatting (auto-fixes)
- ✅ Flake8 linting
- ✅ GitGuardian secret scanning
- ✅ Test coverage (80% minimum)
- ✅ Conventional commit format validation
- ✅ Trailing whitespace removal (auto-fixes)
- ✅ End-of-file fixes (auto-fixes)
- ✅ YAML syntax validation

**Manual hook execution**:
```bash
# Run all hooks
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run pytest --all-files
pre-commit run ggshield --all-files
```

### Adding New Features

1. **Write tests first** (TDD approach):
   ```bash
   # Add test to tests/test_acronym_creator.py
   def test_new_feature(self):
       # Test implementation
       pass
   ```

2. **Implement feature** in `src/acronymcreator/core.py` or `cli.py`

3. **Ensure coverage ≥ 80%**:
   ```bash
   python -m pytest --cov=src --cov-report=term-missing
   ```

4. **Run all quality checks**:
   ```bash
   pre-commit run --all-files
   ```

5. **Commit with conventional format**:
   ```bash
   git commit -m "feat: add syllable-based acronym generation"
   ```

---

## CI/CD Pipeline

### Pipeline Stages

The CI pipeline runs automatically on every push and pull request:

#### 1. Lint and Test (≈1-2 minutes)
- Re-runs all pre-commit hooks in clean environment
- Validates hooks weren't bypassed with `--no-verify`
- Runs comprehensive test suite with coverage
- Generates coverage artifacts for downstream stages

#### 2. GitGuardian Repository History Scan (≈1-3 minutes)
- Scans **entire git history** with `ggshield secret scan repo .`
- Catches secrets in deleted files or old commits
- Prevents secrets from ever entering the repository

#### 3. SonarCloud Quality Gate (≈2-3 minutes, main branch only)
- Code quality analysis (maintainability rating)
- Security vulnerability detection
- Code coverage verification (≥80%)
- Technical debt assessment
- Blocks merge if quality gate fails

#### 4. Semgrep Security Analysis (≈1-2 minutes)
- Static analysis for security vulnerabilities
- Runs in parallel with SonarCloud
- Checks for common security anti-patterns

#### 5. Build (≈30 seconds)
- Validates package builds correctly
- Generates distribution artifacts
- Verifies all dependencies are declared

#### 6. Release (≈1 minute, main branch only)
- Analyzes conventional commits since last release
- Calculates semantic version number
- Generates changelog from commit history
- Creates GitHub release with git tag

### Semantic Versioning

Automated version calculation based on [Conventional Commits](https://www.conventionalcommits.org/):

| Commit Type | Version Bump | Example |
|-------------|--------------|---------|
| `feat:` | Minor | 1.0.0 → 1.1.0 |
| `fix:` | Patch | 1.0.0 → 1.0.1 |
| `feat!:` or `BREAKING CHANGE:` | Major | 1.0.0 → 2.0.0 |
| `docs:`, `style:`, `refactor:`, `test:`, `build:`, `ci:`, `chore:` | None | No release |

**Example commits**:
```bash
git commit -m "feat: add syllable-based acronym generation"
# → Version 0.1.0 to 0.2.0

git commit -m "fix: resolve case sensitivity issue in article filtering"
# → Version 0.1.0 to 0.1.1

git commit -m "feat!: change CLI argument structure

BREAKING CHANGE: --include-articles now requires explicit boolean value"
# → Version 0.1.0 to 1.0.0
```

### Monitoring CI Status

```bash
# View recent CI runs
gh run list --limit 5

# View specific run details
gh run view <run-id>

# View logs for failed run
gh run view <run-id> --log

# Re-run failed jobs
gh run rerun <run-id>

# Watch current run
gh run watch
```

---

## Configuration

### Key Configuration Files

| File | Purpose | Critical Settings |
|------|---------|------------------|
| `lefthook.yml` | Primary git hooks (requires tools in PATH) | black, flake8, pytest, gitguardian |
| `.pre-commit-config.yaml` | Alternative hooks with isolated environments | Same as lefthook but managed |
| `.coveragerc` | Coverage configuration | `fail_under = 80`, `data_file = /tmp/...` |
| `pytest-precommit.ini` | Pytest configuration for hooks | Coverage settings, test paths |
| `pyproject.toml` | Python package configuration | Dependencies, entry points, pytest/coverage |
| `.github/workflows/ci.yml` | CI/CD pipeline | 6-stage pipeline definition |
| `sonar-project.properties` | SonarCloud configuration | Quality gate, coverage paths |
| `.releaserc.json` | Semantic-release configuration | Versioning rules, changelog format |

### Environment Variables

**Local Development**:
```bash
export GITGUARDIAN_API_KEY=your_api_key_here  # Required for ggshield
export PATH="$(pwd)/venv/bin:$PATH"           # Required for lefthook
```

**CI/CD (GitHub Secrets)**:
- `GITGUARDIAN_API_KEY`: GitGuardian API key for secret scanning
- `SONAR_TOKEN`: SonarCloud integration token
- `SEMGREP_APP_TOKEN`: Semgrep security analysis token
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions

### Coverage Configuration

Coverage enforced at **three levels**:

1. **Pre-commit hook**: Blocks commits <80% coverage
2. **CI pipeline**: Re-validates in clean environment
3. **SonarCloud**: Quality gate requires ≥80%

**Configuration files**:
- `.coveragerc`: Main config with `data_file = /tmp/.coverage_precommit`
- Branch coverage enabled for comprehensive testing
- Exclusion patterns for common non-testable code

---

## Troubleshooting

### Common Issues

#### "flake8: not found" or "black: not found"

**Cause**: Lefthook can't find tools because venv is not in PATH

**Solution**:
```bash
source venv/bin/activate
export PATH="$(pwd)/venv/bin:$PATH"
git commit ...
```

#### Pre-commit Hooks Fail After Clean Install

**Cause**: Pre-commit environments not installed

**Solution**:
```bash
pre-commit install --install-hooks
pre-commit run --all-files
```

#### Coverage Below 80%

**Solution**:
```bash
# Generate detailed coverage report
python -m pytest --cov=src --cov-report=term-missing

# Identify missing lines and add tests
# Coverage must be ≥80% to commit
```

#### GitGuardian API Key Not Set

**Cause**: `GITGUARDIAN_API_KEY` environment variable not set

**Solution**:
```bash
# Get API key from GitGuardian dashboard
export GITGUARDIAN_API_KEY=your_api_key_here

# Persist in shell profile
echo 'export GITGUARDIAN_API_KEY=your_api_key_here' >> ~/.bashrc
source ~/.bashrc
```

#### SonarCloud Quality Gate Fails

**Check CI Logs**: Look for "Check Quality Gate Status" step

**Common failures**:
```bash
# Coverage below 80%
# → Add more tests

# Security hotspots not reviewed
# → Review in SonarCloud UI (cannot be auto-fixed)

# Code smells
# → Refactor per SonarCloud recommendations

# Duplicated code >3%
# → Extract common code into functions
```

#### Commit Message Rejected

**Cause**: Commit doesn't follow conventional format

**Solution**:
```bash
# Valid formats
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug"
git commit -m "docs: update README"

# Invalid
git commit -m "Added new feature"  # ❌ Wrong tense
git commit -m "feature: add thing"  # ❌ Wrong type
```

### Getting Help

```bash
# CLI help
acronymcreator --help

# View configuration
cat pyproject.toml
cat .coveragerc
cat lefthook.yml

# Check hook status
pre-commit run --all-files

# Verify environment
which python
which black
which flake8
python --version
```

---

## Contributing

We welcome contributions! Please follow these guidelines:

### Contribution Workflow

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feat/amazing-feature`
3. **Make changes with tests** (maintain ≥80% coverage)
4. **Run quality checks**: `pre-commit run --all-files`
5. **Commit with conventional format**: `git commit -m "feat: add amazing feature"`
6. **Push to fork**: `git push origin feat/amazing-feature`
7. **Create Pull Request**

### Requirements for PR Acceptance

- ✅ All CI pipeline stages pass
- ✅ Test coverage ≥ 80%
- ✅ No GitGuardian secrets detected
- ✅ SonarCloud quality gate passes
- ✅ Conventional commit format
- ✅ Code formatted with Black
- ✅ No Flake8 violations

### Code Style

This project uses:
- **Black** for code formatting (automatic)
- **Flake8** for linting
- **Pytest** for testing
- **Type hints** encouraged but not required

### Testing Guidelines

```python
# Write descriptive test names
def test_create_acronym_excludes_articles_by_default(self):
    """Test that articles are excluded unless explicitly included."""
    pass

# Aim for comprehensive coverage
def test_edge_case_empty_phrase(self):
    """Test handling of empty input."""
    pass

# Use fixtures for common setup
@pytest.fixture
def acronym_creator():
    return AcronymCreator()
```

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Acknowledgments

Built with:
- [Click](https://click.palletsprojects.com/) - Command line interface framework
- [GitGuardian](https://www.gitguardian.com/) - Secret detection
- [SonarCloud](https://sonarcloud.io/) - Code quality analysis
- [Semantic Release](https://semantic-release.gitbook.io/) - Automated versioning
- [Pre-commit](https://pre-commit.com/) - Git hook management
- [Lefthook](https://github.com/evilmartians/lefthook) - Fast git hooks

---

## Related Resources

- [CLAUDE.md](CLAUDE.md) - Detailed development guide for Claude Code
- [BLOG.md](BLOG.md) - Blog post about "Automated Guard Rails for Vibe Coding"
- [Conventional Commits](https://www.conventionalcommits.org/) - Commit message specification
- [GitGuardian Documentation](https://docs.gitguardian.com/) - Secret scanning setup
- [SonarCloud Documentation](https://docs.sonarcloud.io/) - Quality gate configuration
