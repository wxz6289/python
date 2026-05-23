-- RBAC + ACL 权限模型初始化（由 docker-compose 挂载到 MySQL 首次启动）

CREATE TABLE IF NOT EXISTS users (
    id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(64)     NOT NULL UNIQUE,
    password_hash VARCHAR(255)    NOT NULL,
    email         VARCHAR(128)    NULL,
    department    VARCHAR(64)     NULL COMMENT 'ABAC 属性: 部门',
    status        TINYINT         NOT NULL DEFAULT 1 COMMENT '1=active 0=disabled',
    created_at    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS roles (
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    code        VARCHAR(64)     NOT NULL UNIQUE,
    name        VARCHAR(128)    NOT NULL,
    description VARCHAR(255)    NULL,
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS permissions (
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    code        VARCHAR(128)    NOT NULL UNIQUE,
    resource    VARCHAR(64)     NOT NULL,
    action      VARCHAR(32)     NOT NULL,
    description VARCHAR(255)    NULL,
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_resource_action (resource, action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS user_roles (
    user_id BIGINT UNSIGNED NOT NULL,
    role_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (user_id, role_id),
    CONSTRAINT fk_ur_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_ur_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id       BIGINT UNSIGNED NOT NULL,
    permission_id BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    CONSTRAINT fk_rp_role FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    CONSTRAINT fk_rp_perm FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS acl_entries (
    id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    subject_type  ENUM('user', 'role') NOT NULL,
    subject_id    BIGINT UNSIGNED      NOT NULL,
    resource_type VARCHAR(64)          NOT NULL,
    resource_id   VARCHAR(128)         NOT NULL DEFAULT '*',
    action        VARCHAR(32)          NOT NULL,
    effect        ENUM('allow', 'deny') NOT NULL DEFAULT 'allow',
    conditions    JSON                 NULL,
    priority      INT                  NOT NULL DEFAULT 0,
    created_at    DATETIME             NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_acl_lookup (resource_type, resource_id, action),
    KEY idx_acl_subject (subject_type, subject_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id VARCHAR(128)    NOT NULL PRIMARY KEY,
    owner_id   BIGINT UNSIGNED NOT NULL,
    department VARCHAR(64)     NULL,
    created_at DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_chat_owner FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
