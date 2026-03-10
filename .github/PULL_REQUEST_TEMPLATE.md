## Summary

<!-- What does this PR add or fix? -->

## Checklist

### For new ratios
- [ ] Formula string on the function (`fn.formula = "..."`)
- [ ] Description string on the function (`fn.description = "..."`)
- [ ] Citation added to `docs/CITATIONS.md`
- [ ] Returns `None` / `null` on division by zero (never `NaN` or exception)
- [ ] Pure function — no side effects, no I/O
- [ ] Exported from the top-level `__init__.py` / `index.ts`
- [ ] At least one test added

### For bug fixes
- [ ] Test that reproduces the bug added
- [ ] Fix verified against the test

### For fetchers
- [ ] Network calls are in `fetchers/` only — not in core
- [ ] Added to `[fetchers]` extras in `pyproject.toml` / optional deps in `package.json`
- [ ] Rate limits documented in module docstring

### Both languages
- [ ] Python implementation added/updated
- [ ] TypeScript implementation added/updated (or issue opened to track)

## Test results

```
pytest python/tests/ -v
# paste output
```

## Notes for reviewer

<!-- Anything unusual about the implementation, edge cases to verify, etc. -->
