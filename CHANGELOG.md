Changelog
All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] 

### Added 

### Changed

## [0.4.0] 

### Added 
* You can now provide default mocks in table_meta by @Somtom in https://github.com/DeepLcom/sql-mock/pull/19
* Add array column types by @Somtom in https://github.com/DeepLcom/sql-mock/pull/22
* Use sqlglot for table ref replace by @Somtom in https://github.com/DeepLcom/sql-mock/pull/24
* Error handling improvements by @Somtom in https://github.com/DeepLcom/sql-mock/pull/25
* Add dbt support by @Somtom in https://github.com/DeepLcom/sql-mock/pull/26

### Changed
* Update SQL glot to 20.5.0 by @Somtom in https://github.com/DeepLcom/sql-mock/pull/27

### Fixed
* Fixed quickstart docs by @Somtom in https://github.com/DeepLcom/sql-mock/pull/20


## [0.3.1] 

### Fixed 
- MockTable classes now have a `_sql_dialect` attribute that is used with `sglglot` for more reliable dialect conversions


## [0.3.0] 

**Full Changelog**: https://github.com/DeepLcom/sql-mock/compare/v0.2.0...v0.3.0

### Added 
* Now you can also pass a `query` to the `table_meta`. The `query_path` will overwrite a `query` in case both are provided
* New method `assert_cte_equal` that allows to check the output of a specific CTE in the query you want to test.
* Added documentation page 

### Changed

* The `_get_results` method now accepts a `query` instead of needing to load the query within the method. In case you created custom Mock Table classes, you need to take this into account.


## [0.2.0] 

**Full Changelog**: https://github.com/DeepLcom/sql-mock/compare/v0.1.2...v0.2.0

### Added 

* Possibility to pass the `query_path` in the `table_meta` decorator. This allows to specify the query of a model in a single place instead of always needing to pass it in the `from_mocks` method. The provided query can still be overwritten in `from_mocks` if necessary. @Somtom in https://github.com/DeepLcom/sql-mock/pull/11
* Improved readme and separated contribution guidelines by @Somtom in https://github.com/DeepLcom/sql-mock/pull/9


### Changed

* Using `_sql_mock_meta` and `_sql_mock_data` attributes on `BaseMockTable` to decrease that chance of interference with the model's column names. By @Somtom in https://github.com/DeepLcom/sql-mock/pull/10

## [0.1.2] - 2023-10-26
Initial version.

[Unreleased]: https://github.com/DeepLcom/sql-mock/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/DeepLcom/sql-mock/releases/tag/v0.4.0
[0.3.1]: https://github.com/DeepLcom/sql-mock/releases/tag/v0.3.1
[0.3.0]: https://github.com/DeepLcom/sql-mock/releases/tag/v0.3.0
[0.2.0]: https://github.com/DeepLcom/sql-mock/releases/tag/v0.2.0
[0.1.2]: https://github.com/DeepLcom/sql-mock/releases/tag/v0.1.2
