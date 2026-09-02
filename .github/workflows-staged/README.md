# Staged workflows

`ci.yml` in this directory is the project CI workflow. It is parked here rather than in
`.github/workflows/` for one reason: the owner's `gh` OAuth token currently carries the scopes
`gist, read:org, repo` and **not** `workflow`. GitHub rejects any push that touches
`.github/workflows/` from a token without that scope, with
`refusing to allow an OAuth App to create or update workflow`.

To activate CI, the repository owner runs:

```bash
gh auth refresh -h github.com -s repo,workflow
```

That opens a browser flow. Then, on a `chore/*` branch:

```bash
mkdir -p .github/workflows
git mv .github/workflows-staged/ci.yml .github/workflows/ci.yml
git rm .github/workflows-staged/README.md
git commit -m "ci: activate the CI workflow"
```

Open the PR, merge it, and let CI run once on `develop` so all four check contexts report. Only
then add the required status checks to the ruleset:

```bash
gh api "repos/:owner/:repo/commits/develop/status" -q '.statuses[].context'
RULESET_ID=$(gh api "repos/:owner/:repo/rulesets" -q '.[] | select(.name=="protected-branches") | .id')
gh api -X PUT "repos/:owner/:repo/rulesets/$RULESET_ID" --input .github/ruleset.json
```

`.github/ruleset.json` already contains the four required contexts (`lint-api`, `test-api`,
`lint-web`, `test-web`). The ruleset currently applied to the repository is
`.github/ruleset-no-checks.json`, which is the same thing minus the status-check rule -- because a
required check that has never reported blocks every pull request indefinitely.

The two job-name lists must stay in sync: renaming a CI job without updating
`.github/ruleset.json` silently blocks all merges.
