# Roomturn project workflow

## GitHub is the durable project record

- Repository: `novus77/zhuanjian`. Canonical development branch: `dev`.
- The user explicitly authorized uploading completed assets/content and continuing to record and upload subsequent project work. After an authorized asset or content task, update the asset catalog and dated development log, validate, commit with `type(scope): summary`, and push the completed work to this repository. No additional routine upload confirmation is needed. Report the commit/release link and any actual failure.
- Base new branches/worktrees on `origin/dev`. Branch names contain at most three hyphen-separated words, without slashes or type prefixes. Never force-push or rewrite published history.
- This initial consolidation retained the pre-existing `main` history and created `dev` from it. The desktop checkout now contains the complete Unity source. Do not silently work only in an older external worktree and leave newer assets unarchived.

## Sources, generated assets, and deliveries

- Keep editable `.blend` sources, original Lux3D outputs, cleaned exports, textures, Unity Assets/Packages/ProjectSettings, design documents, generation parameters/task IDs, and verification results in Git.
- Use Git LFS according to `.gitattributes`. Keep Unity `.meta` files paired with their assets. Do not edit generated models merely to make an upload pass.
- Do not commit Unity Library/Temp/Logs/UserSettings/Builds, dependencies, `.blend1` backups, local databases, credentials, or expiring signed URLs.
- Offline preview directories and executable builds are reproducible delivery artifacts. Package them as versioned GitHub Release assets, with SHA-256 checksums and a release index. Keep source provenance and inspection records in the repository.
- Run `python3 tools/repository_archive.py update` after creating or revising assets/content. Run `python3 tools/repository_archive.py check` before committing and pushing. Update `docs/development-log.md` with what changed, source/task IDs, files, verification and outstanding work.
- Verify successful remote Git and LFS upload; a local commit alone does not fulfill the user's archive request. For a milestone delivery, verify release asset names/sizes/checksums and add the release to `docs/releases.md`.
- Never change visibility or billing settings, upload secrets, manufacture verification results, or claim a failed/blocked upload succeeded.

## Verification and implementation boundaries

- Unity project: `unity/Roomturn`, editor version pinned in ProjectSettings/ProjectVersion.txt. Run tests from that project, not repository root.
- Use real production components for gameplay tests. Preserve the actual four-door observation geometry and independently movable hatch, horn, drawer and door axes.
- The original Three.js prototype is historical. Do not replace Unity Web with a visual mock.
- Only describe browser interactions and performance actually observed. A successful build does not prove browser acceptance.
- No Changesets. Follow the milestone release workflow documented in `docs/github-workflow.md`.
