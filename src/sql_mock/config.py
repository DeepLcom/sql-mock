class SQLMockConfig:
    _dbt_project_path = None

    @classmethod
    def set_dbt_project_path(cls, path: str):
        cls._dbt_project_path = path

    @classmethod
    def get_dbt_project_path(cls):
        if cls._dbt_project_path is None:
            raise ValueError("DBT project path is not set. Please set it using set_dbt_project_path()")
        return cls._dbt_project_path
