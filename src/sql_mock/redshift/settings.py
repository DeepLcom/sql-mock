from pydantic_settings import BaseSettings, SettingsConfigDict


class RedshiftSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SQL_MOCK_REDSHIFT_")
    access_key_id: str = None
    allow_db_user_override: bool = False
    app_name: str = None
    auth_profile: str = None
    auto_create: bool = False
    client_id: str = None
    client_secret: str = None
    cluster_identifier: str = None
    credentials_provider: str = None
    database: str = None
    database_metadata_current_db_only: bool = True
    db_groups: list = None
    db_user: str = None
    endpoint_url: str = None
    group_federation: bool = False
    host: str = None
    iam: bool = False
    iam_disable_cache: bool = False
    identity_namespace: str = None
    idp_response_timeout: int = 120
    idp_tenant: str = None
    listen_port: int = 7890
    login_url: str = None
    max_prepared_statements: int = 1000
    numeric_to_float: bool = False
    partner_sp_id: str = None
    password: str = None
    port: int = 5439
    preferred_role: str = None
    principal_arn: str = None
    profile: str = None
    provider_name: str = None
    region: str = None
    role_arn: str = None
    role_session_name: str = "jwt_redshift_session"
    scope: str = ""
    secret_access_key_id: str = None
    serverless_acct_id: str = None
    serverless_work_group: str = None
    session_token: str = None
    ssl: bool = True
    ssl_insecure: bool = True
    sslmode: str = "verify-ca"
    timeout: int = None
    token: str = None
    token_type: str = "ACCESS_TOKEN"
    user: str = None
    web_identity_token: str = None
