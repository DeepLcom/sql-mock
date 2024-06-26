# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.2]

**Full Changelog**: <https://github.com/DeepLcom/sql-mock/compare/v0.6.1...v0.6.2>

### Fixed

* Remove unnecessary `print` statement leading to test failures

## [0.6.1]

**Full Changelog**: <https://github.com/DeepLcom/sql-mock/compare/v0.6.0...v0.6.1>

### Fixed

* Add default target path for dbt
* Improve replacement of tables (also taking into account missing alias)
* Do not require mocks for ARRAY JOIN clause arguments

## [0.6.0]

**Full Changelog**: <https://github.com/DeepLcom/sql-mock/compare/v0.5.4...v0.6.0>

### Added

* New BigQuery column types
* Allow cte mocks

### Changed

* ColumnMock nullable by default

### Breaking Changes

* Path to dbt project.yml file is provided instead of manifest.json
* Array types use other ColumnMock classes as inner type
* Consistent naming of TableMock classes:
  * BaseMockTable -> BaseTableMock
  * BigQueryMockTable -> BigQueryTableMock
  * RedshiftMockTable -> RedshiftTableMock
  * SnowflakeMockTable -> SnowflakeTableMock

### Fixed

* Failing on mixed None values <https://github.com/DeepLcom/sql-mock/issues/34>

## [0.5.4]

**Full Changelog**: <https://github.com/DeepLcom/sql-mock/compare/v0.5.3...v0.5.4>

### Added

### Changed

* Clickhouse: Remove numpy dependency

### Fixed

## [0.5.3]

**Full Changelog**: <https://github.com/DeepLcom/sql-mock/compare/v0.5.2...v0.5.3>

### Added

* Clickhouse: Support for secure connections

### Changed

### Fixed

## [0.5.2]

**Full Changelog**: <https://github.com/DeepLcom/sql-mock/compare/v0.5.1...v0.5.2>

### Added

### Changed

### Fixed

* Removed usage of chdb since it turned out it sometimes does not return results

## [0.5.1]

**Full Changelog**: <https://github.com/DeepLcom/sql-mock/compare/v0.5.0...v0.5.1>

### Added

### Changed

* Use chdb to fully mock the Clickhouse connection

### Fixed

* Fixed generation of CTE names from references with hyphens
* Fixed query paths if dbt project is in subdirectory

## [0.5.0]

**Full Changelog**: <https://github.com/DeepLcom/sql-mock/compare/v0.4.0...v0.5.0>

### Added

* Support for Redshift
* Support for Snowflake

## [0.4.0]

### Added

* You can now provide default mocks in table_meta by @Somtom in <https://github.com/DeepLcom/sql-mock/pull/19>
* Add array column types by @Somtom in <https://github.com/DeepLcom/sql-mock/pull/22>
* Use sqlglot for table ref replace by @Somtom in <https://github.com/DeepLcom/sql-mock/pull/24>
* Error handling improvements by @Somtom in <https://github.com/DeepLcom/sql-mock/pull/25>
* Add dbt support by @Somtom in <https://github.com/DeepLcom/sql-mock/pull/26>

### Changed

* Update SQL glot to 20.5.0 by @Somtom in <https://github.com/DeepLcom/sql-mock/pull/27>

### Fixed

* Fixed quickstart docs by @Somtom in <https://github.com/DeepLcom/sql-mock/pull/20>

## [0.3.1]

### Fixed

* MockTable classes now have a `_sql_dialect` attribute that is used with `sglglot` for more reliable dialect conversions

## [0.3.0]

**Full Changelog**: <https://github.com/DeepLcom/sql-mock/compare/v0.2.0...v0.3.0>

### Added

* Now you can also pass a `query` to the `table_meta`. The `query_path` will overwrite a `query` in case both are provided
* New method `assert_cte_equal` that allows to check the output of a specific CTE in the query you want to test.
* Added documentation page

### Changed

* The `_get_results` method now accepts a `query` instead of needing to load the query within the method. In case you created custom Mock Table classes, you need to take this into account.

## [0.2.0]

**Full Changelog**: <https://github.com/DeepLcom/sql-mock/compare/v0.1.2...v0.2.0>

### Added

* Possibility to pass the `query_path` in the `table_meta` decorator. This allows to specify the query of a model in a single place instead of always needing to pass it in the `from_mocks` method. The provided query can still be overwritten in `from_mocks` if necessary. @Somtom in <https://github.com/DeepLcom/sql-mock/pull/11>
* Improved readme and separated contribution guidelines by @Somtom in <https://github.com/DeepLcom/sql-mock/pull/9>

### Changed

* Using `_sql_mock_meta` and `_sql_mock_data` attributes on `BaseMockTable` to decrease that chance of interference with the model's column names. By @Somtom in <https://github.com/DeepLcom/sql-mock/pull/10>

## [0.1.2] - 2023-10-26

Initial version.

[Unreleased]: https://github.com/DeepLcom/sql-mock/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/DeepLcom/sql-mock/releases/tag/v0.6.0
[0.5.4]: https://github.com/DeepLcom/sql-mock/releases/tag/v0.5.4
[0.5.3]: https://github.com/DeepLcom/sql-mock/releases/tag/v0.5.3
[0.5.2]: https://github.com/DeepLcom/sql-mock/releases/tag/v0.5.2
[0.5.1]: https://github.com/DeepLcom/sql-mock/releases/tag/v0.5.1
[0.5.0]: https://github.com/DeepLcom/sql-mock/releases/tag/v0.5.0
[0.4.0]: https://github.com/DeepLcom/sql-mock/releases/tag/v0.4.0
[0.3.1]: https://github.com/DeepLcom/sql-mock/releases/tag/v0.3.1
[0.3.0]: https://github.com/DeepLcom/sql-mock/releases/tag/v0.3.0
[0.2.0]: https://github.com/DeepLcom/sql-mock/releases/tag/v0.2.0
[0.1.2]: https://github.com/DeepLcom/sql-mock/releases/tag/v0.1.2
