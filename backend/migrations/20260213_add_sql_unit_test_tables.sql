CREATE TABLE sql_test_cases (
    id INT IDENTITY(1,1) PRIMARY KEY,
    proc_full_name NVARCHAR(256) NOT NULL,
    name NVARCHAR(200) NOT NULL,
    description NVARCHAR(MAX) NULL,
    params_json NVARCHAR(MAX) NULL,
    setup_sql NVARCHAR(MAX) NULL,
    act_sql NVARCHAR(MAX) NULL,
    assertion_type NVARCHAR(50) NOT NULL,
    assert_sql NVARCHAR(MAX) NULL,
    actual_schema_sql NVARCHAR(MAX) NULL,
    expected_schema_sql NVARCHAR(MAX) NULL,
    openjson_with_clause NVARCHAR(MAX) NULL,
    baseline_exists BIT NOT NULL DEFAULT 0,
    status NVARCHAR(20) NOT NULL DEFAULT 'draft',
    last_run_at DATETIME2 NULL,
    last_duration_ms INT NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE sql_test_runs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    test_case_id INT NOT NULL,
    status NVARCHAR(10) NOT NULL,
    duration_ms INT NOT NULL,
    diff_preview_json NVARCHAR(MAX) NULL,
    log_text NVARCHAR(MAX) NULL,
    actual_output_json NVARCHAR(MAX) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT fk_sql_test_runs_test_case FOREIGN KEY (test_case_id) REFERENCES sql_test_cases(id)
);

CREATE TABLE sql_test_baselines (
    id INT IDENTITY(1,1) PRIMARY KEY,
    test_case_id INT NOT NULL UNIQUE,
    baseline_json NVARCHAR(MAX) NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT fk_sql_test_baselines_test_case FOREIGN KEY (test_case_id) REFERENCES sql_test_cases(id)
);
