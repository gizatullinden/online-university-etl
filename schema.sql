CREATE TABLE code_attempts (
    user_id TEXT NOT NULL,
    oauth_consumer_key TEXT,
    lis_result_sourcedid TEXT,
    lis_outcome_service_url TEXT,
    is_correct BOOLEAN,
    attempt_type TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);