# Quality & Linting Tools Setup Guide

This project uses multiple quality and linting tools to ensure code consistency and catch potential issues.

## Python Tools

### Installation
```bash
pip install -r dev-requirements.txt
```

### Available Tools

1. **Ruff** - Fast Python linter and formatter
   ```bash
   npm run lint:ruff         # Check code
   npm run lint:ruff:fix     # Auto-fix issues
   ruff format .             # Format code
   ```

2. **Mypy** - Static type checker
   ```bash
   npm run lint:mypy
   ```

3. **Vulture** - Find unused code
   ```bash
   npm run lint:vulture
   ```

4. **Bandit** - Security linter
   ```bash
   npm run lint:bandit
   ```

5. **Pylint** - Code analysis
   ```bash
   npm run lint:py
   ```

6. **Flake8** - Style guide enforcement
   ```bash
   npm run lint:flake8
   ```

7. **Semgrep** - Static analysis for security and code quality
   ```bash
   npm run lint:semgrep
   ```

8. **Pyupgrade** - Modernize Python syntax
   ```bash
   pyupgrade --py310-plus *.py
   ```

## JavaScript/Node Tools

### Installation
```bash
npm install
```

### Available Tools

1. **ESLint** - JavaScript linter
   ```bash
   npm run lint:js          # Check code
   npm run lint:js:fix      # Auto-fix issues
   ```

2. **Prettier** - Code formatter
   ```bash
   npm run format:prettier
   ```

3. **Biome** - All-in-one toolchain (alternative to Prettier + ESLint)
   ```bash
   npm run format:biome
   ```

4. **Oxlint** - JavaScript linter (alternative to ESLint)
   ```bash
   npm run lint:oxlint
   ```

5. **Knip** - Find unused files and dependencies
   ```bash
   npm run lint:knip
   ```

## Git Hooks (Husky)

Husky is configured to run quality checks before commits.

### Setup
```bash
npm run prepare    # Initialize Husky
```

### Pre-commit Hook
Automatically runs:
- ESLint (with auto-fix)
- Prettier (formatting)
- Ruff (Python linting with auto-fix)
- Pylint, Mypy, and Bandit (reporting only)

## Commands Summary

```bash
# Lint everything
npm run lint:all

# Format everything
npm run format:all

# Individual tools
npm run lint:js              # ESLint
npm run lint:py              # Pylint
npm run lint:ruff            # Ruff
npm run lint:mypy            # Mypy type checking
npm run lint:bandit          # Security scan
npm run lint:flake8          # Flake8 style
npm run lint:vulture         # Find dead code
npm run lint:semgrep         # Semgrep analysis
npm run lint:oxlint          # Oxlint
npm run lint:knip            # Find unused files

npm run format:prettier      # Format with Prettier
npm run format:biome         # Format with Biome
npm run lint:ruff:fix        # Auto-fix with Ruff
npm run lint:js:fix          # Auto-fix ESLint
```

## Configuration Files

- `.eslintrc.json` - ESLint configuration
- `.prettierrc.json` - Prettier configuration
- `biome.json` - Biome configuration
- `knip.json` - Knip configuration
- `oxlint.json` - Oxlint configuration
- `pyproject.toml` - Python tools configuration (Ruff, Mypy, Pylint)
- `.flake8` - Flake8 configuration
- `.bandit` - Bandit configuration
- `.semgrep.yml` - Semgrep rules
- `.husky/` - Git hooks

## Pre-commit Workflow

When you commit code:
1. ESLint automatically fixes fixable issues
2. Prettier auto-formats your code
3. Ruff checks and fixes Python code
4. Other tools run in reporting mode
5. If critical issues found, commit is blocked

## Quick Start

```bash
# Install all dependencies
npm install
pip install -r dev-requirements.txt

# Initialize Husky
npm run prepare

# Run all checks
npm run lint:all

# Format all code
npm run format:all

# Commit your code (pre-commit hooks will run automatically)
git commit -m "Your message"
```

## Troubleshooting

### Pre-commit hook not running
```bash
npx husky install
chmod +x .husky/pre-commit
```

### Skip pre-commit checks (use cautiously)
```bash
git commit --no-verify -m "Your message"
```

### Update dependencies
```bash
npm update
pip install --upgrade -r dev-requirements.txt
```
