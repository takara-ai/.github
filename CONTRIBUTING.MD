# Contributing to TAKARA.AI Projects

## Commit Message Standards

- **Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):**
  - Example: `feat: add new upscaling method`
  - Example: `fix: correct edge detection bug`
  - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, etc.
- All commit messages are checked by our CI. PRs with non-conforming commits will fail.

## Pull Request Process

- **Do NOT push directly to `main`.**
- Always create a new branch for your changes and open a Pull Request (PR).
- Use the PR template to describe what was changed and why.
- Ensure your PR is up-to-date with the latest `main` branch before requesting review.
- All PRs must pass the linter and commit message checks before merging.

## Code Quality

- We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting Python code.
- The linter runs automatically on every PR and push.
- **Your code must pass Ruff checks before merging.**

### Running Ruff Locally

1. Install Ruff:
   ```bash
   pip install ruff
   ```
2. To check your code:
   ```bash
   ruff check src/
   ```
3. To auto-format your code:
   ```bash
   ruff format src/
   ```

**Key Ruff settings:**
- Line length: 88
- Target Python: 3.12
- Enabled rules: errors, flakes, bugbear, import-sort, type-checking, annotation
- Long lines (`E501`) are ignored

## Code Review

- Write clear, descriptive PR titles and descriptions.
- Reference related issues or discussions if applicable.
- Be responsive to review feedback and update your PR as needed.
- Keep PRs focused and small when possible.

## Questions?

If you have any questions, contact jordan@takara.ai
