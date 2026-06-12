# Contributing

Want to send a PR? Cool. Here's the flow.

## Before you start

- **Open an issue first** if the change is non-trivial. I don't want you
  to spend a weekend on something I'd have asked you to do differently.
- Read the code that's already there. I try to keep it boring and
  consistent. If you're adding a new pattern, it should fit.
- Look at the README for how to install / run / test. Use the lockfile
  that's checked in; don't regenerate it.

## Local checks

Run whatever the project has: `pnpm test`, `pytest`, `cargo test`, etc.
If linter / formatter configs are checked in, run them too. CI will
catch what you missed, but a green push is faster than a red one.

### Testing workflow

This project uses multiple testing layers:

1. **Unit tests** (Vitest):

   ```bash
   pnpm test              # Run unit tests
   pnpm test:coverage     # Run with coverage report
   ```

2. **E2E tests** (Playwright):

   ```bash
   pnpm test:e2e          # Run E2E tests
   pnpm test:e2e:ui       # Run with Playwright UI mode
   pnpm test:e2e:report   # View test report
   ```

3. **Type checking**:

   ```bash
   pnpm type-check        # TypeScript type checking
   ```

4. **Linting and formatting**:
   ```bash
   pnpm lint              # ESLint
   pnpm format:check      # Check Prettier formatting
   pnpm format            # Auto-fix formatting
   ```

**Important**: Run all checks before submitting a PR:

```bash
pnpm lint && pnpm type-check && pnpm test && pnpm test:e2e
```

### Accessibility requirements

All UI changes must maintain WCAG 2.1 AA compliance:

- Use semantic HTML elements
- Include proper ARIA labels where needed
- Ensure keyboard navigation works
- Test with screen readers (VoiceOver, NVDA, JAWS)
- Verify color contrast ratios meet standards

### Performance considerations

- Keep bundle size minimal (check with `pnpm analyze`)
- Use React.memo for expensive components
- Implement lazy loading for images and heavy components
- Test Core Web Vitals (LCP, FID, CLS)

## Commit messages

I don't enforce Conventional Commits. Subject, blank line, body, done.
If a commit fixes an issue, mention the issue number. Don't bother with
emoji or "WIP" prefixes.

## Pull requests

- Fill the PR template. One paragraph in the body is fine; screenshots
  help for UI.
- Keep the diff small. Squash before merging unless the history matters.
- I'll review roughly in order of arrival. If CI is green and the change
  does what the description says, I'll merge. I might push back on
  architecture; that's not personal.
- Don't commit secrets, generated build output, large binaries, or
  someone else's code without a license.

## What I won't merge

- Drive-by refactors that don't fix a real problem.
- New dependencies for trivial reasons.
- Anything that breaks the existing API without a heads-up first.

## License

By contributing, you agree your contribution is licensed under the same
license as the rest of the project. See [`LICENSE`](./LICENSE).
