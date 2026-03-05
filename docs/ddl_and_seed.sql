-- ============================================================
-- 用户表、部门表 DDL（MySQL 8），与 app/models 一致
-- 用户表、部门表可放在同一库或不同库，按需在对应库执行
-- ============================================================

-- -----------------------------
-- 1. 部门表 department（建议先建，用户表可引用 department_id）
-- -----------------------------
CREATE TABLE IF NOT EXISTS `department` (
    `id`         INT          NOT NULL AUTO_INCREMENT,
    `name`       VARCHAR(100) NOT NULL,
    `created_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------
-- 2. 用户表 user
-- -----------------------------
CREATE TABLE IF NOT EXISTS `user` (
    `id`            INT          NOT NULL AUTO_INCREMENT,
    `email`         VARCHAR(255) NOT NULL,
    `name`          VARCHAR(100) NOT NULL,
    `department_id` INT          NULL,
    `created_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_user_email` (`email`),
    KEY `ix_user_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 测试数据
-- ============================================================

-- 部门数据（先插部门，再插用户）
INSERT INTO `department` (`id`, `name`) VALUES
(1, '技术部'),
(2, '产品部'),
(3, '运营部')
ON DUPLICATE KEY UPDATE `name` = VALUES(`name`);

-- 用户数据（department_id 对应上面部门）
INSERT INTO `user` (`id`, `email`, `name`, `department_id`) VALUES
(1, 'zhangsan@example.com', '张三', 1),
(2, 'lisi@example.com', '李四', 1),
(3, 'wangwu@example.com', '王五', 2),
(4, 'zhaoliu@example.com', '赵六', 2),
(5, 'sunqi@example.com', '孙七', NULL)
ON DUPLICATE KEY UPDATE
    `email`         = VALUES(`email`),
    `name`          = VALUES(`name`),
    `department_id` = VALUES(`department_id`),
    `updated_at`    = CURRENT_TIMESTAMP;
