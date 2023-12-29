class SQLMockConfig:
    _dbt_manifest_path = None

    @classmethod
    def set_dbt_manifest_path(cls, path: str):
        cls._dbt_manifest_path = path

    @classmethod
    def get_dbt_manifest_path(cls):
        if cls._dbt_manifest_path is None:
            raise ValueError("DBT manifest path is not set. Please set it using set_dbt_manifest_path()")
        return cls._dbt_manifest_path
