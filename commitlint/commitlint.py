#!/usr/bin/env python3
import os, sys, re, subprocess

# Minimal Conventional Commits header linter with GitHub Actions annotations.
# Header format: type(scope)?: subject
# Focus: type/class, scope, subject (header only). No body/footer parsing.

ALLOWED_TYPES_DEFAULT = "feat,fix,docs,style,refactor,perf,test,build,ci,chore,revert"

def read_env_list(name, default=None):
    raw = os.environ.get(name)
    if raw is None:
        raw = default
    if raw is None or raw.strip() == "":
        return None
    return [x.strip() for x in raw.split(",") if x.strip()]

def get_git_commits(range_spec=None, limit=None):
    # returns list of (sha, subject)
    fmt = "%H%x00%s"
    args = ["git", "log", "--no-merges", f"--pretty=format:{fmt}"]
    if range_spec:
        args.append(range_spec)
    if limit:
        args.extend(["-n", str(limit)])
    try:
        out = subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(f"::warning title=commitlint::Could not read git log ({e}). Falling back to HEAD", file=sys.stderr)
        try:
            out = subprocess.check_output(["git", "log", "--no-merges", f"--pretty=format:{fmt}", "-n", "1"], text=True)
        except Exception:
            return []
    commits = []
    for line in out.splitlines():
        if not line.strip():
            continue
        try:
            sha, subject = line.split("\x00", 1)
        except ValueError:
            continue
        commits.append((sha.strip(), subject.strip()))
    return commits

def infer_range_from_github_env():
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    base_ref = os.environ.get("GITHUB_BASE_REF", "")
    if event_name.startswith("pull_request") and base_ref:
        return f"origin/{base_ref}..HEAD"
    return None

def lint_subject(subject, allowed_types, allowed_scopes, require_scope, require_scope_except, max_subject, allow_capital_subject):
    # Regex:
    # type: lowercase letters
    # optional scope: allow a-z0-9, '-', '.', '/'; no spaces; at least 1 char
    # optional '!'
    # ': ' then subject
    m = re.match(r'^([a-z]+)(?:\(([a-z0-9][a-z0-9./-]*?)\))?(\!)?: (.+)$', subject)
    errors = []
    if not m:
        errors.append("format must be 'type(scope)?: subject' with lowercase type and a space after colon")
        return errors
    ctype, scope, bang, sub = m.groups()
    if allowed_types and ctype not in allowed_types:
        errors.append(f"type '{ctype}' is not allowed. Allowed: {', '.join(allowed_types)}")
    if require_scope and not scope and (not require_scope_except or ctype not in require_scope_except):
        errors.append("scope is required but missing")
    if scope and allowed_scopes is not None and scope not in allowed_scopes:
        errors.append(f"scope '{scope}' is not in allowed list: {', '.join(allowed_scopes)}")
    if not sub or sub.strip() == "":
        errors.append("subject must not be empty")
    if len(sub) > max_subject:
        errors.append(f"subject too long ({len(sub)} > {max_subject})")
    if sub.endswith("."):
        errors.append("subject must not end with a period")
    if not allow_capital_subject and sub and sub[0].isupper():
        errors.append("subject should start lowercase (imperative mood)")
    return errors

def main(argv):
    # Skip for Release Please bot if desired
    if os.environ.get("SKIP_FOR_BOT", "true").lower() in ("1","true","yes","on"):
        actor = os.environ.get("GITHUB_ACTOR", "")
        if actor == "release-please[bot]":
            print("::notice title=commitlint::Skipping for release-please[bot].")
            return 0

    allowed_types = read_env_list("TYPES", ALLOWED_TYPES_DEFAULT)
    allowed_scopes = read_env_list("SCOPES", None)  # None = allow any scope
    require_scope = os.environ.get("REQUIRE_SCOPE", "false").lower() in ("1","true","yes","on")
    require_scope_except = read_env_list("REQUIRE_SCOPE_EXCEPT_TYPES", "revert")
    allow_capital_subject = os.environ.get("ALLOW_CAPITAL_SUBJECT", "false").lower() in ("1","true","yes","on")
    try:
        max_subject = int(os.environ.get("MAX_SUBJECT", "72"))
    except ValueError:
        max_subject = 72

    # Range selection
    range_spec = None
    if len(argv) >= 2 and argv[1] == "--range" and len(argv) >= 3:
        range_spec = argv[2]
    else:
        range_spec = infer_range_from_github_env()

    commits = get_git_commits(range_spec=range_spec, limit=200)
    if not commits:
        print("::warning title=commitlint::No commits found to lint.")
        return 0

    error_count = 0
    for sha, subj in commits:
        errs = lint_subject(subj, allowed_types, allowed_scopes, require_scope, require_scope_except, max_subject, allow_capital_subject)
        if errs:
            error_count += len(errs)
            short = sha[:7]
            for msg in errs:
                print(f"::error title=commit {short}::{msg} | '{subj}'")
    if error_count > 0:
        print(f"::group::Commit lint summary")
        print(f"Found {error_count} errors across {len(commits)} commit(s).")
        print("::endgroup::")
        return 1
    else:
        print("All commit subjects comply with rules.")
        return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
