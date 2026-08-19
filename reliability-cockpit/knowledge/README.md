# Knowledge Integration

Recommended local development layout:

```text
workspace/
├── maximo-knowledge/
├── pi-knowledge/
├── reliability-data-contracts/
└── reliability-cockpit/
```

Applications can reference sibling repositories through:

- Git submodules
- Git subtree
- package dependency
- generated catalog artifact
- CI checkout
- local symbolic links for development

Avoid committing machine-specific absolute symlinks into shared repositories.
