# Release Checklist

Please ensure the following steps have been taken before publishing a new release:

## Versioning

- [ ] The version has been bumped in `pyproject.toml` in accordance with [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Documentation

- [ ] The documentation has been updated by running `make build-docs-github`.

## Changelog

- [ ] The "Unreleased" entries in the Changelog have been moved to the new version.
- [ ] The new version section in the Changelog has been updated with a summary of changes.
- [ ] The references at the bottom of the Changelog have been adjusted.

Once all these steps have been completed, you can publish the new release.
