from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `tortoise_notes` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `title` VARCHAR(200) NOT NULL,
    `content` LONGTEXT,
    `created_at` DATETIME(6) NOT NULL
) CHARACTER SET utf8mb4 COMMENT='演示用记事本表，展示 Tortoise 与 MySQL 的基本 CRUD。';
CREATE TABLE IF NOT EXISTS `tortoise_products` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(20) NOT NULL,
    `sku` VARCHAR(20) NOT NULL,
    `status` INT NOT NULL,
    `description` LONGTEXT,
    `price` DECIMAL(10,2) NOT NULL,
    `stock` INT NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    `updated_at` DATETIME(6) NOT NULL
) CHARACTER SET utf8mb4 COMMENT='产品模型';
CREATE TABLE IF NOT EXISTS `tortoise_users` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `email` VARCHAR(20) NOT NULL,
    `username` VARCHAR(20) NOT NULL,
    `password_hash` VARCHAR(200) NOT NULL,
    `status` INT NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    `updated_at` DATETIME(6) NOT NULL,
    KEY `idx_tortoise_us_email_d155d3` (`email`)
) CHARACTER SET utf8mb4 COMMENT='用户模型';
CREATE TABLE IF NOT EXISTS `tortoise_orders` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `order_no` VARCHAR(20) NOT NULL,
    `status` INT NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    `updated_at` DATETIME(6) NOT NULL,
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_tortoise_tortoise_45c4f7b9` FOREIGN KEY (`user_id`) REFERENCES `tortoise_users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='订单模型';
CREATE TABLE IF NOT EXISTS `tortoise_order_items` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `quantity` INT NOT NULL,
    `price` DECIMAL(10,2) NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    `updated_at` DATETIME(6) NOT NULL,
    `order_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    UNIQUE KEY `uid_tortoise_or_order_i_ac304f` (`order_id`, `product_id`),
    CONSTRAINT `fk_tortoise_tortoise_e5733375` FOREIGN KEY (`order_id`) REFERENCES `tortoise_orders` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_tortoise_tortoise_ae607268` FOREIGN KEY (`product_id`) REFERENCES `tortoise_products` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='订单产品模型';
CREATE TABLE IF NOT EXISTS `tortoise_user_profiles` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `profile_data` JSON NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    `updated_at` DATETIME(6) NOT NULL,
    `user_id` INT NOT NULL UNIQUE,
    CONSTRAINT `fk_tortoise_tortoise_64a591bb` FOREIGN KEY (`user_id`) REFERENCES `tortoise_users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='用户配置模型';
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
)
