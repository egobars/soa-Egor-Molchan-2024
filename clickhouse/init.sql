CREATE DATABASE IF NOT EXISTS snet_statistics;
CREATE TABLE IF NOT EXISTS snet_statistics.stats
(
    `id` Int32,
    `post_id` Int32,
    `user_id` Int32 NULL,
    `type` String
)
ENGINE = MergeTree
PRIMARY KEY (id);