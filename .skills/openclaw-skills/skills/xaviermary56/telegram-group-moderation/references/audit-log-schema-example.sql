CREATE TABLE telegram_moderation_audit_log (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    trace_id VARCHAR(64) NOT NULL,
    chat_id BIGINT NOT NULL,
    message_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    username VARCHAR(128) NOT NULL DEFAULT '',
    audit_status VARCHAR(16) NOT NULL,
    risk_level VARCHAR(16) NOT NULL,
    action VARCHAR(64) NOT NULL,
    reason VARCHAR(255) NOT NULL DEFAULT '',
    offense_count INT NOT NULL DEFAULT 0,
    action_result VARCHAR(32) NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uniq_trace_id (trace_id),
    KEY idx_chat_message (chat_id, message_id),
    KEY idx_user_created (user_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
