CREATE DATABASE IF NOT EXISTS snet;
CREATE TABLE IF NOT EXISTS snet.posts_stats
(
    `post_id` Int32,
    `user_id` Int32,
    `type` String
)
ENGINE = MergeTree
ORDER BY (post_id)
PARTITION BY (post_id);

CREATE TABLE IF NOT EXISTS snet.authors_stats
(
    `author` String,
    `user_id` Int32,
    `post_id` Int32
)
ENGINE = MergeTree
ORDER BY (author)
PARTITION BY (author);