---
name: agentic-task-orchestration
description: Complete blueprint for autonomous task execution in git worktrees, test verification, CI pipeline monitoring, automated PR creation, review, and safe backlog merging.
compatibility: Agentic coding assistants executing multi-task feature catalogs.
metadata:
  category: workflow-orchestration
  tags: [git-worktree, task-execution, ci-cd, gh-cli, pr-review, autonomous-merge]
---

# Agentic Task Orchestration, CI Monitoring, & Autonomous PR Merging Skill

This skill documents the exact workflow required to autonomously orchestrate task specifications from `.agents/tasks/`, execute them in isolated git worktrees, enforce full test coverage and linting standards, monitor GitHub Actions CI pipelines, diagnose failures, and safely merge Pull Requests to clear the repository backlog.

---

## 🎯 Core Operating Principles

1. **Worktree Isolation**: Never perform task implementation directly on the `main` branch. Always spawn an isolated git worktree under `.worktrees/task-<id>`.
2. **Empirical Verification Before Commit**: Never declare success or commit code without executing test suites (`uv run pytest`) and lint checks (`uv run ruff check .`).
3. **CI Line Length & Format Compliance**: Always format code using `uv run ruff format .` and ensure lines are strictly under the configured `line-length` limit (default: 100 characters).
4. **Secret Fallback Guard in CI**: Ensure GitHub workflows use `${{ secrets.ADMIN_PAT || secrets.GITHUB_TOKEN }}` so CI builds never fail on missing repository secrets.
5. **Clean Backlog Clearance**: Merge feature PRs via squash merge (`gh pr merge <pr-number> --squash --delete-branch`), pull updated `main`, re-verify test suites, and close superseded Dependabot PRs.

---

## 🔄 Phase 1: Git Worktree Setup & Isolated Task Execution

### 1. Worktree Creation
```bash
# Create feature branch and isolated worktree workspace
git worktree add -b feature/task-<id>-<slug> .worktrees/task-<id> main

# Install development virtual environment inside worktree
cd .worktrees/task-<id>
uv pip install -e ".[dev]"
```

### 2. Implementation & Code Quality Checks
- Build backend routes (`app/routes/`), services (`app/services/`), models (`app/models/`), and schemas (`app/schemas/`).
- Run code formatters and linters:
  ```bash
  uv run ruff check . --fix
  uv run ruff format .
  ```

### 3. Comprehensive Unit & Integration Testing
- Write test cases in `app/tests/test_<feature>.py`.
- Execute test runner:
  ```bash
  uv run pytest app/tests/test_<feature>.py
  uv run pytest  # Verify zero regressions across full test suite
  ```

---

## 📤 Phase 2: Task Status Update, Commit, & PR Creation

### 1. Update Task Specification Status
In both `.worktrees/task-<id>/.agents/tasks/task-<id>-*.md` and `.agents/tasks/task-<id>-*.md`, change status:
```markdown
## Status
Completed (Verified 100% Test Coverage)
```

### 2. Git Commit & Push
```bash
git add .
git commit -m "feat(task-<id>): <concise descriptive summary>"
git push -u origin feature/task-<id>-<slug>
```

### 3. Create Pull Request
```bash
gh pr create \
  --title "feat(task-<id>): <Task Title>" \
  --body "## Overview
Implements Task <id>: <Title>.

### Changes
- Summary of backend modifications.

### Acceptance Criteria Verification
- [x] Verified 100% test coverage with pytest.
- [x] Passed ruff linting and formatting."
```

### 4. Worktree Cleanup
```bash
git worktree remove --force .worktrees/task-<id>
```

---

## 🕵️ Phase 3: Autonomous CI Monitoring & Error Diagnosis

### 1. Check CI Pipeline Status
```bash
# List PR checks
gh pr checks <pr-number>

# List recent workflow runs
gh run list --limit 10
```

### 2. Inspect CI Failures
If a CI run fails, extract exact failure logs immediately:
```bash
gh run view <run-id> --log-failed
```

### 3. Common CI Failure Patterns & Remediation
- **Ruff `E501` Line Too Long**: Wrap docstrings and split long multiline strings. Re-run `uv run ruff format .`.
- **Missing Token (`Input required and not supplied: token`)**: Ensure workflow YAML uses `${{ secrets.ADMIN_PAT || secrets.GITHUB_TOKEN }}`.

---

## 🔀 Phase 4: Autonomous PR Merging & Backlog Clearance

### 1. Merge Feature Pull Requests
Once all CI checks (`Backend Lint & Pytest`, `Production Docker Image Build`) pass green:
```bash
gh pr merge <pr-number> --squash --delete-branch
```

### 2. Synchronize Local Main Branch
```bash
git checkout main
git pull --rebase origin main
```

### 3. Handle Dependabot & Superseded PRs
- For passing Dependabot PRs: merge via `gh pr merge <pr-number> --squash --delete-branch`.
- For superseded or conflicting Dependabot PRs: close with `gh pr close <pr-number> -c "Superseded by main updates"`.

### 4. Final Backlog & Health Verification
```bash
# Verify 0 open PRs remain
gh pr list --state open

# Verify main branch health
uv run ruff check .
uv run pytest
```
