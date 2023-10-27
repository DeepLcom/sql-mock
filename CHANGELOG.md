Changelog
All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] 

### Added 

- Possibility to pass the `query_path` in the `table_meta` decorator. This allows to specify the query of a model in a single place instead of always needing to pass it in the `from_mocks` method. The provided query can still be overwritten in `from_mocks` if necessary

### Changed

- Using `_sql_mock_meta` and `_sql_mock_data` attributes on `BaseMockTable` to decrease that chance of interference with the model's column names

## [0.1.2] - 2023-10-26
Initial version.

[Unreleased]: https://github.com/DeepLcom/deepl-python/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/DeepLcom/sql-mock/releases/tag/v0.1.2
