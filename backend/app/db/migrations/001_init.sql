-- 系统元数据表
CREATE TABLE IF NOT EXISTS sys_sessions (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL DEFAULT '新对话',
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sys_messages (
    id                TEXT PRIMARY KEY,
    session_id        TEXT NOT NULL REFERENCES sys_sessions(id) ON DELETE CASCADE,
    role              TEXT NOT NULL,
    content           TEXT NOT NULL,
    sql_query         TEXT,
    query_result_json TEXT,
    chart_spec_json   TEXT,
    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sys_session_summaries (
    session_id  TEXT PRIMARY KEY REFERENCES sys_sessions(id) ON DELETE CASCADE,
    summary     TEXT NOT NULL,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 业务分析表
CREATE TABLE IF NOT EXISTS biz_orders (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    product    TEXT NOT NULL,
    category   TEXT NOT NULL,
    amount     REAL NOT NULL,
    quantity   INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    region     TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_biz_orders_category ON biz_orders(category);
CREATE INDEX IF NOT EXISTS idx_biz_orders_region ON biz_orders(region);
CREATE INDEX IF NOT EXISTS idx_biz_orders_order_date ON biz_orders(order_date);
