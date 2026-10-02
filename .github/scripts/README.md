# 📜 Changelog

DotCtl uses Git tags to maintain versioned changelogs. Each release is tied to a Git tag (e.g., `v1.1.0`), and commits between tags are grouped automatically.

## 🧾 Manual vs Generated Changelog

You can maintain the changelog in two ways:

- **Manual (recommended for releases):** curated, clean, user-facing notes
- **Generated (for reference/debugging):** derived from Git history

---

## 🚀 Generate Changelog Automatically

DotCtl includes helper scripts to generate changelog files from Git history.

### 1. Tag-based changelog (recommended)

```sh
./changelog_by_tag.sh > CHANGELOG.generated.md
```

This groups commits under each Git tag:

- `v1.0.0`
- `v1.0.1`
- etc.

Best for release history.

---

### 2. Full commit history changelog

```sh
./changelog.sh > CHANGELOG.full.md
```

Generates a linear commit-based log using:

- commit hash
- date
- message

Useful for debugging or audit trails.

---

## 🧪 Alternative Git Commands

You can also generate changelog data manually using Git:

```sh
git log --pretty=format:"%h | %ad | %s" --date=short
```

```sh
git log --merges --oneline
```

```sh
git log --decorate --pretty=format:"%h | %ad | %d | %s" --date=short
```

---

## 📌 Versioning Strategy

DotCtl follows **semantic versioning**:

```txt
MAJOR.MINOR.PATCH
```

- **PATCH** → bug fixes (1.1.0 → 1.1.1)
- **MINOR** → new features (1.1.0 → 1.2.0)
- **MAJOR** → breaking changes (1.1.0 → 2.0.0)

Example:

- `v1.0.x` → initial stable feature set
- `v1.1.0` → new commands like `status`, `diff`
- `v2.0.0` → breaking CLI or config changes

---

## 📅 Date in Changelog?

Dates are optional but recommended for releases:

- Helps track release timeline
- Useful for users consuming releases via GitHub

Format:

```txt
# v1.1.0 - 2026-05-23
```

If you prefer minimal style, you can omit dates and rely on Git tags alone.

---

## 📦 Recommended Practice

For best results:

- Keep **CHANGELOG.md manually curated**
- Use scripts only to **generate drafts**
- Only include **user-facing changes**
- Avoid commit noise (WIP, refactors, internal changes)

---

If you want next step, I can also help you turn this into:

- GitHub Release automation (auto changelog per tag)
- or a Python CLI command: `dotctl changelog`
