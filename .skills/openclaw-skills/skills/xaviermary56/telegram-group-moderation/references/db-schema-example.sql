CREATE TABLE telegram_moderation_offense_log (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    chat_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    KEY idx_chat_user_created (chat_id, user_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
