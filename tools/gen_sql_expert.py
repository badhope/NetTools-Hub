#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 SQL「专业篇」课程包（8 讲，sql31 - sql38）。

运行：python tools/gen_sql_expert.py
产物：content_packs/sql-expert.json

设计原则
--------
1. **输出块由真实执行生成**：每个可运行 SQL 的 output 都用 sql_runner 实际跑一遍
   再写入，避免手写结果与引擎行为漂移（列顺序、NULL 显示、影响行数都算）。
2. **判题由 sql_runner.check_sql 验证**：生成时逐讲跑 solution + tests，任何一讲
   不过直接抛错、不写文件。
3. **不使用触发器**：sql_runner 按分号切语句，触发器体内分号会被切坏（实测），
   因此本包不涉及 CREATE TRIGGER。
4. 只讲 SQLite 实测支持的语法：窗口函数、CTE、JSON1、EXPLAIN QUERY PLAN、
   事务与 SAVEPOINT 均已在本机 sqlite3（Python 内置）验证可用。
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app" / "src" / "main" / "python"))

import sql_runner  # noqa: E402

OUT = ROOT / "content_packs" / "sql-expert.json"

CHAPTER = 54
CHAPTER_NAME = "SQL · 专业篇"


# ---------------------------------------------------------------------------
# 块构造器
# ---------------------------------------------------------------------------

def heading(text):
    return {"type": "heading", "text": text}


def paragraph(text):
    return {"type": "text", "text": text}


def code(sql):
    return {"type": "code", "code": sql.strip("\n"), "runnable": True}


def output(text):
    return {"type": "output", "text": text.strip("\n")}


def table(headers, rows):
    return {"type": "table", "headers": headers, "rows": rows}


def diagram(text):
    return {"type": "diagram", "text": text.strip("\n")}


def tip(text):
    return {"type": "tip", "text": text}


def warn(text):
    return {"type": "warn", "text": text}


def quiz(question, options, answer, explain):
    return {"type": "quiz", "question": question, "options": options,
            "answer": answer, "explain": explain}


def practice(title, sql, hint):
    return {"type": "practice", "title": title, "code": sql.strip("\n"),
            "output": "", "hint": hint}


def steps(items):
    return {"type": "steps", "items": items}


def exercise(title, brief, starter, hint, tests, solution, xp=120):
    return {
        "title": title,
        "brief": brief,
        "starterCode": starter.strip("\n"),
        "hint": hint,
        "tests": tests,
        "stdin": [],
        "xp": xp,
        "solution": solution.strip("\n"),
    }


def lesson(lid, order, title, subtitle, xp, blocks, ex):
    return {
        "id": lid,
        "order": order,
        "chapter": CHAPTER,
        "chapterName": CHAPTER_NAME,
        "lang": "sql",
        "title": title,
        "subtitle": subtitle,
        "xp": xp,
        "blocks": blocks,
        "exercise": ex,
    }


def run_out(sql):
    """真实执行一段 SQL，返回输出文本；失败直接抛错（生成期就暴露）。"""
    r = sql_runner.run_sql(sql.strip("\n"))
    if not r["ok"]:
        raise SystemExit(f"[生成失败] SQL 执行报错：{r['error']}\n--- SQL ---\n{sql}")
    return r["stdout"]


def pair(sql):
    """代码块 + 由真实执行得到的输出块。"""
    return [code(sql), output(run_out(sql))]


def practice_out(title, sql, hint):
    p = practice(title, sql, hint)
    p["output"] = run_out(sql)
    return p


# ---------------------------------------------------------------------------
# sql31 执行计划
# ---------------------------------------------------------------------------

def sql31():
    setup = """CREATE TABLE runs (
    id INTEGER PRIMARY KEY,
    hero TEXT,
    points INTEGER
);

INSERT INTO runs (hero, points)
SELECT 'hero' || value, value * 7
FROM (
    WITH RECURSIVE seq(value) AS (
        SELECT 1
        UNION ALL
        SELECT value + 1 FROM seq WHERE value < 60
    )
    SELECT value FROM seq
);

-- 未建索引：整表扫描
EXPLAIN QUERY PLAN SELECT * FROM runs WHERE hero = 'hero42';"""
    indexed = """CREATE TABLE runs (id INTEGER PRIMARY KEY, hero TEXT, points INTEGER);
INSERT INTO runs (hero, points) VALUES ('hero1',7),('hero42',294),('hero60',420);

CREATE INDEX idx_runs_hero ON runs(hero);

EXPLAIN QUERY PLAN SELECT * FROM runs WHERE hero = 'hero42';"""
    return lesson(
        "sql31", 530, "执行计划深读", "EXPLAIN QUERY PLAN 与扫描代价", 130,
        [
            heading("数据库不是「想怎么查就怎么查」"),
            paragraph(
                "写 SQL 的人只描述结果，怎么取由优化器决定。EXPLAIN QUERY PLAN 就是让优化器把"
                "计划说出来：它打算走全表扫描，还是用某个索引定位。看懂这一行输出，你就知道"
                "慢查询是被「读了多少行」拖慢的，而不是被 SQL 字数拖慢的。"
            ),
            paragraph(
                "SQLite 的计划输出里常见三种动作：SCAN 表示全表扫描，逐行读完再筛；"
                "SEARCH 表示用索引做定位，只读命中的行；USE TEMP B-TREE 表示排序或分组时"
                "建临时结构，这一步会额外占内存和 CPU。计划里没有索引的 SCAN，就是给数据量"
                "增长埋的雷。"
            ),
            paragraph(
                "代价直觉比精确数字更有用：全表扫描的代价与行数成正比，索引查找的代价与"
                "命中行数加树高成正比。十万行里查一条，扫描要读十万行，索引只读几十个节点。"
                "但索引不是免费的：每次写入都要维护，占用空间，选择性差（比如性别只有两种值）"
                "的列建索引几乎没用。判断标准是「这一列能否把结果缩小到很少的行」。"
            ),
            *pair(setup),
            *pair(indexed),
            table(
                ["计划动作", "含义", "什么时候出现"],
                [
                    ["SCAN", "全表扫描", "没有可用索引，或优化器判断扫描更便宜"],
                    ["SEARCH", "索引定位", "WHERE 命中索引列，且选择性足够"],
                    ["USE TEMP B-TREE", "临时排序结构", "ORDER BY / GROUP BY 无索引可用"],
                    ["COVERING INDEX", "覆盖索引", "查询所需列全在索引里，不回表"],
                ],
            ),
            tip(
                "读计划先看最内层：最内层的动作决定每行代价，外层只是组装。看到 SCAN 加大量行，"
                "先想索引；看到 TEMP B-TREE，先想排序键是否能进索引。"
            ),
            warn(
                "不要凭感觉加索引。先跑 EXPLAIN QUERY PLAN 拿到证据，再看加索引后是否真的从 SCAN "
                "变成 SEARCH；否则只是增加了写入成本。"
            ),
            quiz(
                "EXPLAIN QUERY PLAN 输出 SCAN t，说明什么？",
                ["查询结果一定错", "这张表被逐行扫描", "索引损坏", "SQL 语法有误"],
                1,
                "SCAN 表示全表逐行读取。数据量小时可接受，数据量大时通常是慢查询的根因。",
            ),
            practice_out(
                "让计划变成 SEARCH",
                """CREATE TABLE heroes (id INTEGER PRIMARY KEY, name TEXT, level INTEGER);
INSERT INTO heroes VALUES (1,'V',66),(2,'Judy',42),(3,'Jackie',30);

EXPLAIN QUERY PLAN SELECT * FROM heroes WHERE name = 'V';""",
                "先在 name 上建索引，再重复一次 EXPLAIN。",
            ),
        ],
        exercise(
            "给慢查询加索引",
            "表 events 上有 200 条记录。为 kind 列建索引，使按 kind 过滤的查询从全表扫描变成索引查找；"
            "最后返回 EXPLAIN QUERY PLAN 的 detail 文本，要求包含 SEARCH。",
            """CREATE TABLE events (id INTEGER PRIMARY KEY, kind TEXT, payload TEXT);
INSERT INTO events (kind, payload)
SELECT 'k' || (value % 4), 'p' || value
FROM (
    WITH RECURSIVE seq(value) AS (
        SELECT 1 UNION ALL SELECT value + 1 FROM seq WHERE value < 200
    )
    SELECT value FROM seq
);

-- 在这里建索引

EXPLAIN QUERY PLAN SELECT * FROM events WHERE kind = 'k2';""",
            "CREATE INDEX idx_events_kind ON events(kind); 再跑 EXPLAIN QUERY PLAN。",
            [
                "assert 'SEARCH' in __stdout__, '计划里应出现 SEARCH，实际：' + __stdout__",
                "assert 'events' in __stdout__, '计划应提到 events 表'",
            ],
            """CREATE TABLE events (id INTEGER PRIMARY KEY, kind TEXT, payload TEXT);
INSERT INTO events (kind, payload)
SELECT 'k' || (value % 4), 'p' || value
FROM (
    WITH RECURSIVE seq(value) AS (
        SELECT 1 UNION ALL SELECT value + 1 FROM seq WHERE value < 200
    )
    SELECT value FROM seq
);

CREATE INDEX idx_events_kind ON events(kind);

EXPLAIN QUERY PLAN SELECT * FROM events WHERE kind = 'k2';""",
        ),
    )


# ---------------------------------------------------------------------------
# sql32 索引设计
# ---------------------------------------------------------------------------

def sql32():
    composite = """CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    status TEXT,
    amount INTEGER,
    created_at TEXT
);

INSERT INTO orders (user_id, status, amount, created_at) VALUES
    (1, 'paid', 100, '2026-01-05'),
    (1, 'paid', 250, '2026-01-09'),
    (1, 'refunded', 80, '2026-01-11'),
    (2, 'paid', 300, '2026-01-12'),
    (2, 'pending', 120, '2026-02-01'),
    (3, 'paid', 60, '2026-02-03');

CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- 最左前缀：只用到 user_id 也能命中
EXPLAIN QUERY PLAN SELECT * FROM orders WHERE user_id = 1;

-- 跳过最左列，索引用不上
EXPLAIN QUERY PLAN SELECT * FROM orders WHERE status = 'paid';"""
    covering = """CREATE TABLE orders (
    id INTEGER PRIMARY KEY, user_id INTEGER, status TEXT, amount INTEGER, created_at TEXT
);
INSERT INTO orders (user_id, status, amount, created_at) VALUES
    (1,'paid',100,'2026-01-05'),(1,'paid',250,'2026-01-09'),(2,'paid',300,'2026-01-12');

-- 覆盖索引：查询列全部在索引里，不需要回表
CREATE INDEX idx_orders_cover ON orders(user_id, amount);

EXPLAIN QUERY PLAN
SELECT user_id, amount FROM orders WHERE user_id = 1;"""
    return lesson(
        "sql32", 531, "索引设计", "复合索引、最左前缀与覆盖索引", 140,
        [
            heading("索引不是「加得越多越快」"),
            paragraph(
                "复合索引 (user_id, status) 像一本先按用户、再按状态排序的目录。查询只给 user_id "
                "能顺着目录找；只给 status 就找不到入口，因为目录的第一层是用户。这就是最左前缀"
                "原则：复合索引只对「从第一列开始的连续前缀」有效。"
            ),
            paragraph(
                "覆盖索引是另一种优化：如果查询要的列全都在索引里，数据库读完索引就能回答，"
                "不用回表取整行。把常用的「过滤列 + 返回列」一起建索引，就能吃到这个红利。"
                "代价是索引变大，写入更慢，所以只对高频只读查询值得。"
            ),
            paragraph(
                "选择性是第三个维度：一列取值越分散，索引越能过滤掉更多行。用户 ID 可能有几十万"
                "种取值，适合索引；性别只有两三种取值，索引扫完和全表扫差不多。设计索引的顺序是"
                "先看查询模式（WHERE / JOIN / ORDER BY 用了哪些列），再看选择性，最后才动手建。"
            ),
            *pair(composite),
            *pair(covering),
            table(
                ["索引形态", "能命中的查询", "不能命中"],
                [
                    ["(a, b)", "a；a+b", "只用 b"],
                    ["(a, b, c)", "a；a+b；a+b+c", "b；c；b+c"],
                    ["覆盖索引 (a, b)", "只查 a、b 两列且按 a 过滤", "查 c 需要回表"],
                ],
            ),
            tip(
                "建索引前先写下这句：WHERE 用什么、JOIN 用什么、ORDER BY 用什么。三者合起来就是"
                "候选复合索引的列顺序。"
            ),
            warn(
                "索引会拖慢写入并占空间。一张表上五六个索引通常已经过多；先用执行计划证明缺什么，"
                "再补那一个。"
            ),
            quiz(
                "索引 (user_id, status) 能加速 `WHERE status = 'paid'` 吗？",
                ["能，索引包含 status", "不能，跳过了最左列 user_id", "能，但只快一倍", "取决于数据量"],
                1,
                "复合索引必须从最左列开始连续使用；只查第二列等于没有入口。",
            ),
            practice_out(
                "覆盖索引",
                """CREATE TABLE logs (id INTEGER PRIMARY KEY, level TEXT, msg TEXT, ts TEXT);
INSERT INTO logs (level, msg, ts) VALUES
    ('INFO','boot','2026-01-01 00:00'),
    ('ERROR','timeout','2026-01-01 00:01'),
    ('INFO','ready','2026-01-01 00:02');

CREATE INDEX idx_logs_level_ts ON logs(level, ts);

EXPLAIN QUERY PLAN SELECT level, ts FROM logs WHERE level = 'INFO';""",
                "查询列 level、ts 都在索引里，计划应出现 COVERING INDEX。",
            ),
        ],
        exercise(
            "为排行榜查询设计索引",
            "表 scores(player, season, points)。建一个复合索引，使按 season 过滤并按 points 排序的查询"
            "能用索引完成；返回该赛季的 player 与 points，按 points 降序。",
            """CREATE TABLE scores (player TEXT, season INTEGER, points INTEGER);
INSERT INTO scores VALUES
    ('V', 1, 90), ('Judy', 1, 75), ('Jackie', 1, 60),
    ('V', 2, 88), ('Judy', 2, 95), ('Jackie', 2, 70);

-- 建索引后写查询

""",
            "CREATE INDEX idx_scores_season_points ON scores(season, points DESC); "
            "然后 SELECT player, points FROM scores WHERE season = 1 ORDER BY points DESC;",
            [
                "assert columns == ['player','points'], columns",
                "assert rows == [['V',90],['Judy',75],['Jackie',60]], rows",
            ],
            """CREATE TABLE scores (player TEXT, season INTEGER, points INTEGER);
INSERT INTO scores VALUES
    ('V', 1, 90), ('Judy', 1, 75), ('Jackie', 1, 60),
    ('V', 2, 88), ('Judy', 2, 95), ('Jackie', 2, 70);

CREATE INDEX idx_scores_season_points ON scores(season, points DESC);

SELECT player, points FROM scores WHERE season = 1 ORDER BY points DESC;""",
        ),
    )


# ---------------------------------------------------------------------------
# sql33 事务
# ---------------------------------------------------------------------------

def sql33():
    commit = """CREATE TABLE accounts (name TEXT PRIMARY KEY, balance INTEGER);
INSERT INTO accounts VALUES ('V', 100), ('Judy', 50);

BEGIN;
UPDATE accounts SET balance = balance - 30 WHERE name = 'V';
UPDATE accounts SET balance = balance + 30 WHERE name = 'Judy';
COMMIT;

SELECT name, balance FROM accounts ORDER BY name;"""
    rollback = """CREATE TABLE accounts (name TEXT PRIMARY KEY, balance INTEGER);
INSERT INTO accounts VALUES ('V', 100), ('Judy', 50);

BEGIN;
UPDATE accounts SET balance = balance - 1000 WHERE name = 'V';
-- 余额不允许为负：发现异常，整体撤销
ROLLBACK;

SELECT name, balance FROM accounts ORDER BY name;"""
    return lesson(
        "sql33", 532, "事务与隔离", "BEGIN / COMMIT / ROLLBACK 与 ACID", 140,
        [
            heading("要么全做，要么全不做"),
            paragraph(
                "转账是最经典的事务场景：扣钱和加钱必须一起成功，只成功一半就是账目错乱。事务把"
                "多条语句打包成一个原子单元，BEGIN 开始，COMMIT 提交，ROLLBACK 撤销。中途任何一步"
                "失败，整个单元回到开始前的状态，不存在「扣了没加」的中间态。"
            ),
            paragraph(
                "ACID 四个字母是事务的四条承诺：原子性（全做或全不做）、一致性（约束始终成立）、"
                "隔离性（并发事务互不看到中间状态）、持久性（提交后即使断电也在）。SQLite 默认是"
                "串行化隔离，写事务之间不会并发交叉，读事务能看到一个稳定快照。"
            ),
            paragraph(
                "SAVEPOINT 是事务里的书签：可以在一个大事务中设多个保存点，出错时只回滚到某个点，"
                "前面的工作仍然保留。适合「批量导入时允许部分失败」的场景。注意 ROLLBACK TO 只是"
                "撤销到书签，事务本身还没结束，要继续 COMMIT 或 ROLLBACK。"
            ),
            *pair(commit),
            *pair(rollback),
            diagram(
                "BEGIN\n  ├─ 语句 1  ← 成功\n  ├─ 语句 2  ← 失败\n  │     └─ ROLLBACK → 回到 BEGIN 前\n  └─ COMMIT   → 全部生效\n\n"
                "SAVEPOINT sp1\n  ├─ 语句 3  ← 成功\n  ├─ SAVEPOINT sp2\n  ├─ 语句 4  ← 失败\n  │     └─ ROLLBACK TO sp2 → 只撤销语句 4\n  └─ COMMIT   → 语句 1–3 保留"
            ),
            tip("事务要尽量短：长事务占锁时间长，会阻塞其他写入。把网络请求、用户输入放到事务外面。"),
            warn(
                "每条语句单独执行时 SQLite 会自动提交（autocommit）。一旦显式 BEGIN，就必须显式"
                "COMMIT 或 ROLLBACK，否则连接关闭时整段被回滚。"
            ),
            quiz(
                "BEGIN 后执行了三条 UPDATE，未 COMMIT 就断开连接，结果是？",
                ["三条都生效", "三条全部回滚", "只有第一条生效", "报语法错误"],
                1,
                "事务未提交即视为失败，连接关闭时全部回滚；这正是「全做或全不做」的体现。",
            ),
            practice_out(
                "带保存点的批量更新",
                """CREATE TABLE items (id INTEGER PRIMARY KEY, qty INTEGER);
INSERT INTO items VALUES (1, 10), (2, 20), (3, 30);

BEGIN;
UPDATE items SET qty = qty + 1 WHERE id = 1;
SAVEPOINT sp;
UPDATE items SET qty = 0 WHERE id = 2;
ROLLBACK TO sp;
COMMIT;

SELECT id, qty FROM items ORDER BY id;""",
                "回滚到保存点只撤销 id=2 的更新，id=1 的加一保留。",
            ),
        ],
        exercise(
            "安全转账",
            "accounts 表初始 V=100、Judy=50。用事务完成：V 扣 40、Judy 加 40；然后额外插入一条"
            "非法记录（balance 为负）并回滚该插入，最后提交。返回 name、balance，按 name 升序。",
            """CREATE TABLE accounts (name TEXT PRIMARY KEY, balance INTEGER);
INSERT INTO accounts VALUES ('V', 100), ('Judy', 50);

-- 用事务完成转账，并保证非法插入被撤销

""",
            "BEGIN; 两条 UPDATE；SAVEPOINT sp; INSERT 负数；ROLLBACK TO sp; COMMIT; 最后 SELECT。",
            [
                "assert columns == ['name','balance'], columns",
                "assert rows == [['Judy',90],['V',60]], rows",
            ],
            """CREATE TABLE accounts (name TEXT PRIMARY KEY, balance INTEGER);
INSERT INTO accounts VALUES ('V', 100), ('Judy', 50);

BEGIN;
UPDATE accounts SET balance = balance - 40 WHERE name = 'V';
UPDATE accounts SET balance = balance + 40 WHERE name = 'Judy';
SAVEPOINT sp;
INSERT INTO accounts VALUES ('Ghost', -10);
ROLLBACK TO sp;
COMMIT;

SELECT name, balance FROM accounts ORDER BY name;""",
        ),
    )


# ---------------------------------------------------------------------------
# sql34 并发与锁
# ---------------------------------------------------------------------------

def sql34():
    immediate = """CREATE TABLE queue (id INTEGER PRIMARY KEY, job TEXT, state TEXT);
INSERT INTO queue VALUES (1, 'build', 'pending'), (2, 'test', 'pending');

-- 取一个待办并标记为处理中，两步必须在同一事务内
BEGIN IMMEDIATE;
UPDATE queue SET state = 'running' WHERE id = (
    SELECT id FROM queue WHERE state = 'pending' ORDER BY id LIMIT 1
);
COMMIT;

SELECT id, job, state FROM queue ORDER BY id;"""
    retry = """CREATE TABLE queue (id INTEGER PRIMARY KEY, job TEXT, state TEXT);
INSERT INTO queue VALUES (1, 'build', 'pending'), (2, 'test', 'pending');
UPDATE queue SET state = 'running' WHERE id = 2 AND state = 'pending';

-- 乐观方案：用状态条件更新，只有一个事务能改成功
UPDATE queue SET state = 'running' WHERE id = 1 AND state = 'pending';
SELECT changes() AS affected;"""
    return lesson(
        "sql34", 533, "并发与锁", "BEGIN IMMEDIATE、乐观更新与重试", 150,
        [
            heading("两个人同时取同一个任务"),
            paragraph(
                "后台任务队列的经典问题是重复消费：两个 worker 同时读到 id=1 处于 pending，"
                "然后都把它改成 running，结果同一个任务跑了两遍。根因不是 SQL 写错，而是"
                "「读—判断—写」之间没有保护，属于典型的竞态条件。"
            ),
            paragraph(
                "SQLite 用数据库级锁解决：读事务拿共享锁，写事务拿独占锁。BEGIN IMMEDIATE 在"
                "事务开始时就直接拿写锁，避免「先读后写」时升级锁失败。BEGIN EXCLUSIVE 更严格，"
                "连读都不允许。并发写多的场景还要设置 busy timeout，让后到的事务等待而不是立刻"
                "报 database is locked。"
            ),
            paragraph(
                "另一种思路是乐观并发：不提前加锁，而是在 UPDATE 的 WHERE 里带上旧状态，"
                "用 changes() 判断是否真的改到了行。改到 1 行说明抢到了，改到 0 行说明别人先动手，"
                "业务层重试或放弃。这种写法在分布式系统里也很常见，本质是「用条件更新做 CAS」。"
            ),
            *pair(immediate),
            *pair(retry),
            table(
                ["事务模式", "开始时的锁", "适用场景"],
                [
                    ["BEGIN", "延迟（第一次读写才加）", "只读或单条写"],
                    ["BEGIN IMMEDIATE", "立即写锁", "读后写、任务领取"],
                    ["BEGIN EXCLUSIVE", "独占锁", "维护、迁移"],
                    ["乐观更新", "不加锁，条件判断", "高并发、可重试"],
                ],
            ),
            tip(
                "领取任务优先用「UPDATE ... WHERE state='pending' + 检查 changes()」，一条语句完成"
                "判断和写入，天然原子。"
            ),
            warn("长事务会让其他写入一直等待；任务队列里不要把耗时操作放在事务内。"),
            quiz(
                "两个事务同时执行 `UPDATE ... WHERE id=1 AND state='pending'`，最多几个能改到行？",
                ["两个都改到", "只有一个", "取决于网络", "都不改"],
                1,
                "条件更新是原子操作，第二个事务执行时 state 已不是 pending，匹配 0 行。",
            ),
            practice_out(
                "抢占式领取",
                """CREATE TABLE jobs (id INTEGER PRIMARY KEY, state TEXT);
INSERT INTO jobs VALUES (1, 'pending'), (2, 'pending');

UPDATE jobs SET state = 'running' WHERE id = 2 AND state = 'pending';
SELECT changes() AS affected;
SELECT id, state FROM jobs ORDER BY id;""",
                "changes() 返回上一条语句影响的行数，1 表示抢占成功。",
            ),
        ],
        exercise(
            "只领取一次",
            "jobs 表有 1、2、3 三个 pending 任务。用一条条件 UPDATE 把 id=2 领取为 running，"
            "返回受影响行数 affected 以及剩余 pending 的数量 remaining。",
            """CREATE TABLE jobs (id INTEGER PRIMARY KEY, state TEXT);
INSERT INTO jobs VALUES (1,'pending'),(2,'pending'),(3,'pending');

-- 领取 id=2，并统计剩余

""",
            "先 UPDATE ... WHERE id=2 AND state='pending'；再用 SELECT COUNT(*) 统计 pending。",
            [
                "assert columns == ['affected','remaining'], columns",
                "assert rows == [[1,2]], rows",
            ],
            """CREATE TABLE jobs (id INTEGER PRIMARY KEY, state TEXT);
INSERT INTO jobs VALUES (1,'pending'),(2,'pending'),(3,'pending');

UPDATE jobs SET state = 'running' WHERE id = 2 AND state = 'pending';

SELECT changes() AS affected,
       (SELECT COUNT(*) FROM jobs WHERE state = 'pending') AS remaining;""",
        ),
    )


# ---------------------------------------------------------------------------
# sql35 JSON
# ---------------------------------------------------------------------------

def sql35():
    extract = """CREATE TABLE events (id INTEGER PRIMARY KEY, payload TEXT);
INSERT INTO events VALUES
    (1, '{"type":"login","user":{"id":7,"name":"V"},"tags":["a","b"]}'),
    (2, '{"type":"logout","user":{"id":7,"name":"V"},"tags":[]}'),
    (3, '{"type":"login","user":{"id":8,"name":"Judy"},"tags":["c"]}');

SELECT
    id,
    json_extract(payload, '$.type')            AS kind,
    json_extract(payload, '$.user.name')       AS user_name,
    json_extract(payload, '$.tags[0]')         AS first_tag,
    json_array_length(json_extract(payload, '$.tags')) AS tag_count
FROM events
ORDER BY id;"""
    each = """CREATE TABLE events (id INTEGER PRIMARY KEY, payload TEXT);
INSERT INTO events VALUES
    (1, '{"tags":["a","b"]}'),
    (2, '{"tags":["c"]}');

-- 把数组展开成行：一行一个标签
SELECT e.id, t.value AS tag
FROM events e, json_each(e.payload, '$.tags') t
ORDER BY e.id, tag;"""
    return lesson(
        "sql35", 534, "JSON 处理", "json_extract / json_each / 聚合", 150,
        [
            heading("半结构化数据也能查"),
            paragraph(
                "很多业务把可变字段塞进一个 JSON 列：埋点事件、配置、第三方回调。SQLite 的 JSON1 "
                "扩展让你不用把整段字符串搬到应用层解析。json_extract(列, 路径) 取单个值，路径用 "
                "$ 表示根，$.user.name 表示嵌套字段，$.tags[0] 表示数组第一项。"
            ),
            paragraph(
                "json_each 是「展开」：把 JSON 数组变成多行，每行一个元素，可以像普通表一样 JOIN、"
                "GROUP BY。这是标签统计、权限校验的关键工具。反过来 json_group_array / "
                "json_group_object 可以把多行重新聚合成一个 JSON 值。"
            ),
            paragraph(
                "JSON 查询的代价在于没有 schema：数据库不知道字段类型，也无法为内层路径建普通索引。"
                "高频查询的字段应抽成独立列，或建立表达式索引。JSON 适合「字段稀疏、结构多变」的"
                "场景，不适合当万能表结构。"
            ),
            *pair(extract),
            *pair(each),
            table(
                ["函数", "作用", "示例"],
                [
                    ["json_extract", "按路径取值", "$.user.name → 'V'"],
                    ["json_array_length", "数组长度", "$.tags → 2"],
                    ["json_each", "数组展开成行", "SELECT value FROM json_each(...)"],
                    ["json_group_array", "多行聚合成数组", "GROUP BY 后生成 JSON"],
                ],
            ),
            tip("路径写错不会报错，只会返回 NULL。用 json_valid(列) 先校验整段是否合法 JSON。"),
            warn("JSON 列里存数字和存字符串是不同的：'1' 与 1 在 json_extract 后类型不同，比较时要统一。"),
            quiz(
                "json_extract('{\"a\":{\"b\":2}}', '$.a.b') 返回什么？",
                ["'{\"b\":2}'", "2", "NULL", "报错"],
                1,
                "路径逐层下钻到 $.a.b，返回数字 2。",
            ),
            practice_out(
                "标签展开统计",
                """CREATE TABLE posts (id INTEGER PRIMARY KEY, tags TEXT);
INSERT INTO posts VALUES (1, '["sql","db"]'), (2, '["sql"]'), (3, '["ui"]');

SELECT t.value AS tag, COUNT(*) AS n
FROM posts p, json_each(p.tags) t
GROUP BY t.value
ORDER BY n DESC, tag;""",
                "json_each 展开后按标签分组计数。",
            ),
        ],
        exercise(
            "统计登录用户",
            "events 表每行是 JSON，含 type 与 user.id。统计 type='login' 的事件里每个 user.id 出现次数，"
            "返回 user_id、n，按 n 降序、user_id 升序。",
            """CREATE TABLE events (id INTEGER PRIMARY KEY, payload TEXT);
INSERT INTO events VALUES
    (1, '{"type":"login","user":{"id":7}}'),
    (2, '{"type":"login","user":{"id":8}}'),
    (3, '{"type":"logout","user":{"id":7}}'),
    (4, '{"type":"login","user":{"id":7}}');

""",
            "WHERE json_extract(payload,'$.type')='login'，GROUP BY json_extract(payload,'$.user.id')。",
            [
                "assert columns == ['user_id','n'], columns",
                "assert rows == [[7,2],[8,1]], rows",
            ],
            """CREATE TABLE events (id INTEGER PRIMARY KEY, payload TEXT);
INSERT INTO events VALUES
    (1, '{"type":"login","user":{"id":7}}'),
    (2, '{"type":"login","user":{"id":8}}'),
    (3, '{"type":"logout","user":{"id":7}}'),
    (4, '{"type":"login","user":{"id":7}}');

SELECT json_extract(payload, '$.user.id') AS user_id, COUNT(*) AS n
FROM events
WHERE json_extract(payload, '$.type') = 'login'
GROUP BY user_id
ORDER BY n DESC, user_id;""",
        ),
    )


# ---------------------------------------------------------------------------
# sql36 数据仓库
# ---------------------------------------------------------------------------

def sql36():
    star = """CREATE TABLE dim_date (date_key TEXT PRIMARY KEY, year INTEGER, month INTEGER);
CREATE TABLE dim_hero (hero_key INTEGER PRIMARY KEY, name TEXT, faction TEXT);
CREATE TABLE fact_runs (
    run_id INTEGER PRIMARY KEY,
    date_key TEXT,
    hero_key INTEGER,
    distance INTEGER,
    reward INTEGER
);

INSERT INTO dim_date VALUES ('2026-01-05', 2026, 1), ('2026-02-03', 2026, 2);
INSERT INTO dim_hero VALUES (1, 'V', 'nomad'), (2, 'Judy', 'nomad'), (3, 'Jackie', 'corpo');
INSERT INTO fact_runs VALUES
    (1, '2026-01-05', 1, 120, 300),
    (2, '2026-01-05', 2, 80, 200),
    (3, '2026-02-03', 1, 150, 400),
    (4, '2026-02-03', 3, 60, 100);

-- 星型模型：事实表连维度表
SELECT d.year, d.month, h.faction,
       SUM(f.distance) AS distance,
       SUM(f.reward)   AS reward
FROM fact_runs f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_hero h ON h.hero_key = f.hero_key
GROUP BY d.year, d.month, h.faction
ORDER BY d.year, d.month, h.faction;"""
    wide = """CREATE TABLE dim_date (date_key TEXT PRIMARY KEY, year INTEGER, month INTEGER);
CREATE TABLE dim_hero (hero_key INTEGER PRIMARY KEY, name TEXT, faction TEXT);
CREATE TABLE fact_runs (run_id INTEGER PRIMARY KEY, date_key TEXT, hero_key INTEGER,
                        distance INTEGER, reward INTEGER);
INSERT INTO dim_date VALUES ('2026-01-05',2026,1),('2026-02-03',2026,2);
INSERT INTO dim_hero VALUES (1,'V','nomad'),(2,'Judy','nomad'),(3,'Jackie','corpo');
INSERT INTO fact_runs VALUES (1,'2026-01-05',1,120,300),(2,'2026-02-03',2,80,200);

-- 宽表：把维度压平，供报表直接读取
SELECT f.run_id,
       d.year || '-' || printf('%02d', d.month) AS month,
       h.name,
       h.faction,
       f.distance,
       f.reward
FROM fact_runs f
JOIN dim_date d ON d.date_key = f.date_key
JOIN dim_hero h ON h.hero_key = f.hero_key
ORDER BY f.run_id;"""
    return lesson(
        "sql36", 535, "数据仓库入门", "星型模型、维度表与事实表", 150,
        [
            heading("分析型数据该怎么摆"),
            paragraph(
                "业务库追求「改得快」，分析库追求「算得快」，两者表结构往往不同。数据仓库常用的"
                "星型模型把数据分成两类：事实表存可度量的事件（一次跑单的距离、奖励），维度表存"
                "描述性属性（日期、英雄、阵营）。事实表只放外键和数值，维度表放文本，这样聚合时"
                "不会被冗余字符串拖慢。"
            ),
            paragraph(
                "星型的价值在于可切片：按年、按月、按阵营任意组合聚合，只要 JOIN 对应维度。"
                "维度表通常有代理键（整数），比直接用业务字符串连接更快、更稳定。日期维度尤其值得"
                "单独建，因为它能预置节假日、季度、周等属性，避免每次查询重算。"
            ),
            paragraph(
                "宽表是另一条路线：把常用维度提前 JOIN 好，写成一张大表。查询简单、速度快，但"
                "冗余高，维度变化时要重刷。选择取决于使用方式：探索式分析用星型灵活，固定报表用"
                "宽表省事。真实仓库常常两者并存，宽表由星型加工而来。"
            ),
            *pair(star),
            *pair(wide),
            diagram(
                "        dim_date          dim_hero\n"
                "            \\                /\n"
                "             \\              /\n"
                "              fact_runs（事实表）\n"
                "              date_key / hero_key / distance / reward\n\n"
                "星型：事实表在中心，维度围绕四周；JOIN 后可任意切片聚合。"
            ),
            tip("事实表只存「可加的数」和「外键」。把名称、阵营这类文本放进维度表，能显著缩小事实表。"),
            warn("不要在事实表里存会变化的描述字段；维度一变就要全表更新，这正是星型要避免的。"),
            quiz(
                "星型模型里，一次跑单的距离和奖励应该放在哪张表？",
                ["dim_hero", "dim_date", "fact_runs", "三张表都放"],
                2,
                "可度量的数值放在事实表，维度表只存描述属性。",
            ),
            practice_out(
                "按阵营汇总",
                """CREATE TABLE dim_hero (hero_key INTEGER PRIMARY KEY, name TEXT, faction TEXT);
CREATE TABLE fact_runs (run_id INTEGER PRIMARY KEY, hero_key INTEGER, reward INTEGER);

INSERT INTO dim_hero VALUES (1,'V','nomad'),(2,'Judy','nomad'),(3,'Jackie','corpo');
INSERT INTO fact_runs VALUES (1,1,300),(2,2,200),(3,1,400),(4,3,100);

SELECT h.faction, SUM(f.reward) AS total
FROM fact_runs f JOIN dim_hero h ON h.hero_key = f.hero_key
GROUP BY h.faction
ORDER BY total DESC;""",
                "事实表连维度表后按 faction 分组求和。",
            ),
        ],
        exercise(
            "按月汇总跑单",
            "用 fact_runs 与 dim_date 连接，按月统计总距离 distance 与总奖励 reward，"
            "列名为 month、distance、reward，按 month 升序。month 格式为 YYYY-MM。",
            """CREATE TABLE dim_date (date_key TEXT PRIMARY KEY, year INTEGER, month INTEGER);
CREATE TABLE fact_runs (run_id INTEGER PRIMARY KEY, date_key TEXT, distance INTEGER, reward INTEGER);

INSERT INTO dim_date VALUES ('2026-01-05',2026,1),('2026-02-03',2026,2);
INSERT INTO fact_runs VALUES (1,'2026-01-05',120,300),(2,'2026-01-05',80,200),(3,'2026-02-03',150,400);

""",
            "用 year || '-' || printf('%02d', month) 生成 month，再 GROUP BY。",
            [
                "assert columns == ['month','distance','reward'], columns",
                "assert rows == [['2026-01',200,500],['2026-02',150,400]], rows",
            ],
            """CREATE TABLE dim_date (date_key TEXT PRIMARY KEY, year INTEGER, month INTEGER);
CREATE TABLE fact_runs (run_id INTEGER PRIMARY KEY, date_key TEXT, distance INTEGER, reward INTEGER);

INSERT INTO dim_date VALUES ('2026-01-05',2026,1),('2026-02-03',2026,2);
INSERT INTO fact_runs VALUES (1,'2026-01-05',120,300),(2,'2026-01-05',80,200),(3,'2026-02-03',150,400);

SELECT d.year || '-' || printf('%02d', d.month) AS month,
       SUM(f.distance) AS distance,
       SUM(f.reward) AS reward
FROM fact_runs f
JOIN dim_date d ON d.date_key = f.date_key
GROUP BY d.year, d.month
ORDER BY month;""",
        ),
    )


# ---------------------------------------------------------------------------
# sql37 分析函数
# ---------------------------------------------------------------------------

def sql37():
    window = """CREATE TABLE sales (day TEXT, region TEXT, amount INTEGER);
INSERT INTO sales VALUES
    ('2026-01-01','north',100),
    ('2026-01-02','north',150),
    ('2026-01-03','north',120),
    ('2026-01-01','south',80),
    ('2026-01-02','south',90);

SELECT day, region, amount,
       SUM(amount) OVER (PARTITION BY region ORDER BY day) AS running_total,
       ROUND(100.0 * amount / SUM(amount) OVER (PARTITION BY region), 1) AS pct_of_region
FROM sales
ORDER BY region, day;"""
    rank = """CREATE TABLE sales (day TEXT, region TEXT, amount INTEGER);
INSERT INTO sales VALUES
    ('2026-01-01','north',100),('2026-01-02','north',150),('2026-01-03','north',120),
    ('2026-01-01','south',80),('2026-01-02','south',90);

SELECT day, region, amount,
       ROW_NUMBER() OVER (PARTITION BY region ORDER BY amount DESC) AS rn,
       RANK()       OVER (PARTITION BY region ORDER BY amount DESC) AS rnk,
       DENSE_RANK() OVER (PARTITION BY region ORDER BY amount DESC) AS dense
FROM sales
ORDER BY region, rn;"""
    return lesson(
        "sql37", 536, "分析函数实战", "累计、占比与排名", 160,
        [
            heading("不折叠行的聚合"),
            paragraph(
                "GROUP BY 会把多行压成一行；窗口函数则保留每一行，同时在旁边多算一列。"
                "写法是「函数名(...) OVER (PARTITION BY ... ORDER BY ...)」：PARTITION BY 分组、"
                "ORDER BY 定顺序、OVER 声明这是一个窗口计算。"
            ),
            paragraph(
                "累计求和是最常用的窗口：SUM(amount) OVER (PARTITION BY region ORDER BY day) 表示"
                "在同一个 region 内按日期逐行累加。注意没有 ORDER BY 的窗口是整组聚合，结果会"
                "复制到每一行；有 ORDER BY 才是「到当前行为止」。占比就是把当前行除以整组总量。"
            ),
            paragraph(
                "三个排名函数必须分清：ROW_NUMBER 永远连续编号（1,2,3），RANK 并列后跳号"
                "（1,1,3），DENSE_RANK 并列后不跳号（1,1,2）。排行榜要「同分同名次、下一名递减」"
                "用 RANK，「同分同名次、下一名接着数」用 DENSE_RANK，分页取前 N 用 ROW_NUMBER。"
            ),
            *pair(window),
            *pair(rank),
            table(
                ["函数", "并列时的表现", "典型用途"],
                [
                    ["ROW_NUMBER", "不并列，强制唯一", "分页、去重取一条"],
                    ["RANK", "并列同名次，后续跳号", "比赛排名"],
                    ["DENSE_RANK", "并列同名次，后续不跳", "等级评定"],
                ],
            ),
            tip("窗口函数不能写在 WHERE 里；要过滤窗口结果，得包一层子查询或用 CTE。"),
            warn("OVER 里漏写 ORDER BY 会得到整组聚合值复制到每行，常被误认为「累计」算错。"),
            quiz(
                "数值 90、90、80 用 RANK 排名，三个名次是？",
                ["1,1,2", "1,2,3", "1,1,3", "2,2,3"],
                2,
                "RANK 并列同名次，后一个跳号：1、1、3。",
            ),
            practice_out(
                "分区累计",
                """CREATE TABLE t (region TEXT, day TEXT, amount INTEGER);
INSERT INTO t VALUES ('n', 'd1', 10), ('n', 'd2', 20), ('s', 'd1', 5);

SELECT region, day, amount,
       SUM(amount) OVER (PARTITION BY region ORDER BY day) AS running
FROM t
ORDER BY region, day;""",
                "同一区域内按 day 累加，区域之间互不影响。",
            ),
        ],
        exercise(
            "区域排行榜",
            "sales 表含 region、amount。返回每个区域内按 amount 降序的 ROW_NUMBER 名次 rn、"
            "amount、region，按 region、rn 升序。",
            """CREATE TABLE sales (region TEXT, amount INTEGER);
INSERT INTO sales VALUES ('north',100),('north',150),('north',120),('south',80),('south',90);

""",
            "ROW_NUMBER() OVER (PARTITION BY region ORDER BY amount DESC) AS rn。",
            [
                "assert columns == ['rn','amount','region'], columns",
                "assert rows == [[1,150,'north'],[2,120,'north'],[3,100,'north'],[1,90,'south'],[2,80,'south']], rows",
            ],
            """CREATE TABLE sales (region TEXT, amount INTEGER);
INSERT INTO sales VALUES ('north',100),('north',150),('north',120),('south',80),('south',90);

SELECT ROW_NUMBER() OVER (PARTITION BY region ORDER BY amount DESC) AS rn,
       amount,
       region
FROM sales
ORDER BY region, rn;""",
        ),
    )


# ---------------------------------------------------------------------------
# sql38 综合项目
# ---------------------------------------------------------------------------

def sql38():
    funnel = """CREATE TABLE events (user_id INTEGER, day TEXT, step TEXT);
INSERT INTO events VALUES
    (1,'2026-01-01','visit'),(1,'2026-01-01','signup'),(1,'2026-01-02','purchase'),
    (2,'2026-01-01','visit'),(2,'2026-01-02','signup'),
    (3,'2026-01-01','visit'),
    (4,'2026-01-02','visit'),(4,'2026-01-02','signup'),(4,'2026-01-02','purchase');

WITH steps AS (
    SELECT user_id,
           MIN(CASE WHEN step = 'visit'    THEN day END) AS visit_day,
           MIN(CASE WHEN step = 'signup'   THEN day END) AS signup_day,
           MIN(CASE WHEN step = 'purchase' THEN day END) AS purchase_day
    FROM events
    GROUP BY user_id
)
SELECT COUNT(visit_day)    AS visited,
       COUNT(signup_day)   AS signed_up,
       COUNT(purchase_day) AS purchased
FROM steps;"""
    retention = """CREATE TABLE logins (user_id INTEGER, day TEXT);
INSERT INTO logins VALUES
    (1,'2026-01-01'),(1,'2026-01-02'),(1,'2026-01-03'),
    (2,'2026-01-01'),(2,'2026-01-03'),
    (3,'2026-01-02');

WITH first_seen AS (
    SELECT user_id, MIN(day) AS first_day FROM logins GROUP BY user_id
),
activity AS (
    SELECT l.user_id, f.first_day, l.day,
           CAST(julianday(l.day) - julianday(f.first_day) AS INTEGER) AS day_no
    FROM logins l JOIN first_seen f ON f.user_id = l.user_id
)
SELECT first_day,
       COUNT(DISTINCT CASE WHEN day_no = 0 THEN user_id END) AS d0,
       COUNT(DISTINCT CASE WHEN day_no = 1 THEN user_id END) AS d1,
       COUNT(DISTINCT CASE WHEN day_no = 2 THEN user_id END) AS d2
FROM activity
GROUP BY first_day
ORDER BY first_day;"""
    return lesson(
        "sql38", 537, "综合项目：漏斗与留存", "用 CTE + 条件聚合做增长分析", 180,
        [
            heading("把业务问题翻译成一段 SQL"),
            paragraph(
                "漏斗分析回答「每一步流失了多少人」：访问、注册、购买三个环节，各自有多少独立用户"
                "到达。做法是先按用户汇总每个环节的最早时间，得到一张「用户 × 环节」宽表，再用"
                "COUNT 统计每一列的非空数量。条件聚合 CASE WHEN 就是这里的核心工具。"
            ),
            paragraph(
                "留存分析回答「用户回来没有」：先算每个用户的首次活跃日，再算之后每一天与首日的"
                "差值，最后按首日分组，统计第 0、1、2 天仍有活跃的人数。julianday 把日期转成"
                "浮点天数，相减取整就得到「第几天」。"
            ),
            paragraph(
                "这两类分析的共同套路是「先算明细，再聚合」：CTE 负责把复杂逻辑拆成可读的步骤，"
                "主查询负责最后的指标。不要试图用一条嵌套三层的子查询写完，CTE 让每一步都能单独"
                "跑出来验证，这才是分析 SQL 可维护的关键。"
            ),
            *pair(funnel),
            *pair(retention),
            diagram(
                "漏斗          留存\n"
                "visit 4  ─┐    D0 → 次日 → 第2日\n"
                "signup 3 ─┤    用户1  ✓     ✓      ✓\n"
                "purchase 2┘    用户2  ✓     ✗      ✓\n"
                "               用户3  ✗\n\n"
                "漏斗看「到没到」；留存看「回没回」。"
            ),
            tip("先把 CTE 单独 SELECT 出来看数据，再套外层聚合；直接写完整条查询最难排错。"),
            warn("统计「人数」要用 COUNT(DISTINCT user_id)；COUNT(*) 数的是事件条数，会重复计同一个人。"),
            quiz(
                "漏斗里统计每一步到达人数，为什么要 COUNT(DISTINCT user_id)？",
                ["语法要求", "同一用户可能有多次同类事件", "为了排序", "防止 NULL"],
                1,
                "同一用户可能重复访问，按事件计数会虚高；漏斗要的是独立人数。",
            ),
            practice_out(
                "三步漏斗",
                """CREATE TABLE ev (user_id INTEGER, step TEXT);
INSERT INTO ev VALUES (1,'a'),(1,'b'),(1,'c'),(2,'a'),(2,'b'),(3,'a');

WITH s AS (
    SELECT user_id,
           MIN(CASE WHEN step='a' THEN 1 END) AS a,
           MIN(CASE WHEN step='b' THEN 1 END) AS b,
           MIN(CASE WHEN step='c' THEN 1 END) AS c
    FROM ev GROUP BY user_id
)
SELECT COUNT(a) AS step_a, COUNT(b) AS step_b, COUNT(c) AS step_c FROM s;""",
                "条件聚合把每个用户的三步压成一行，再分别计数。",
            ),
        ],
        exercise(
            "次日留存率",
            "logins 表记录用户每日登录。计算每个首日的 D0 人数与 D1 人数，返回 first_day、d0、d1，"
            "按 first_day 升序。D1 指首次登录后第 1 天仍登录的人数。",
            """CREATE TABLE logins (user_id INTEGER, day TEXT);
INSERT INTO logins VALUES
    (1,'2026-01-01'),(1,'2026-01-02'),
    (2,'2026-01-01'),
    (3,'2026-01-02'),(3,'2026-01-03');

""",
            "先 GROUP BY user_id 取 MIN(day)；再算 julianday 差值；最后按首日分组条件计数。",
            [
                "assert columns == ['first_day','d0','d1'], columns",
                "assert rows == [['2026-01-01',2,1],['2026-01-02',1,1]], rows",
            ],
            """CREATE TABLE logins (user_id INTEGER, day TEXT);
INSERT INTO logins VALUES
    (1,'2026-01-01'),(1,'2026-01-02'),
    (2,'2026-01-01'),
    (3,'2026-01-02'),(3,'2026-01-03');

WITH first_seen AS (
    SELECT user_id, MIN(day) AS first_day FROM logins GROUP BY user_id
),
activity AS (
    SELECT l.user_id, f.first_day,
           CAST(julianday(l.day) - julianday(f.first_day) AS INTEGER) AS day_no
    FROM logins l JOIN first_seen f ON f.user_id = l.user_id
)
SELECT first_day,
       COUNT(DISTINCT CASE WHEN day_no = 0 THEN user_id END) AS d0,
       COUNT(DISTINCT CASE WHEN day_no = 1 THEN user_id END) AS d1
FROM activity
GROUP BY first_day
ORDER BY first_day;""",
        ),
    )


LESSONS = [sql31(), sql32(), sql33(), sql34(), sql35(), sql36(), sql37(), sql38()]

# 每讲补一段「深入」正文：把概念讲到工程实践层面，而不是停在语法。
DEEP_DIVE = {'sql31': '还有一个经常被忽略的细节：EXPLAIN 输出的行数估计来自统计信息，而 SQLite 的统计信息需要 ANALYZE 才会更新。表刚大批量导入数据却没跑 ANALYZE 时，优化器可能仍按旧的行数估算，选出一条看起来合理、实际很差的计划。排查慢查询时如果发现「计划与数据分布明显不符」，先跑一次 ANALYZE 再看。另外，EXPLAIN 不带 QUERY PLAN 会输出字节码，那才是真正的执行指令列表，适合排查「为什么这条语句比预期多做了几步」这类细节问题；日常优化看 QUERY PLAN 就够了，不必一上来就读字节码。', 'sql32': "索引设计还有一个容易被忽视的约束：函数或表达式会让索引失效。WHERE strftime('%Y', created_at) = '2026' 这类写法无法使用 created_at 上的普通索引，因为数据库要先对每一行算出函数值才能比较。解决方式有两种：把条件改写成范围比较（created_at >= '2026-01-01' AND created_at < '2027-01-01'），或者在 SQLite 里建表达式索引。同理，隐式类型转换也会让索引失效：字符串列用数字去比较，会退化成逐行转换再比较。写 WHERE 时保持「列在左边、常量在右边、类型一致」，是最省心的习惯。", 'sql33': '事务还有一个常被低估的成本：它持有锁的时间等于从事务开始到提交的整段时长。如果事务里夹了一次网络请求或一段用户等待，锁就会被占住几百毫秒甚至几秒，并发一上来直接排队。所以工程上的原则是「事务只包数据库操作，且尽量短」。另一个细节是 SQLite 的写事务默认是排他的：同一时刻只能有一个写事务，读可以并发。这意味着写多读少的场景要考虑批量提交、合并小事务，而不是每条语句一个事务。最后，事务不等于备份：COMMIT 只保证写入成功，误删数据仍然需要靠备份或软删除加审计表来兜底。', 'sql34': '并发问题还有一类更隐蔽的形态：丢失更新。两个事务都读到余额 100，各自加 10 再写回，最终结果是 110 而不是 120，因为后写的人覆盖了前一个人的结果。条件更新能解决「状态机式」的抢占，但金额累加这类场景要用原地运算（balance = balance + 10）而不是「读出来加完再写回」。原地运算把加法和写入合成一条语句，数据库保证它原子执行。识别这类 bug 的方法很直接：凡是代码里出现「先 SELECT 出来、在应用层算、再 UPDATE 回去」的模式，就要怀疑丢失更新。', 'sql35': "JSON 还有一类高频需求是「按数组包含过滤」：找出 tags 里含有 'sql' 的行。SQLite 没有专门的数组包含运算符，标准写法是用 EXISTS 加 json_each 子查询，或者用 json_extract 配合 LIKE（不严谨，会误伤子串）。前者更准确：WHERE EXISTS (SELECT 1 FROM json_each(posts.tags) WHERE value = 'sql')。这类相关子查询在数据量大时开销不小，如果字段是高频过滤条件，还是应该抽成关联表。经验判断是：JSON 适合「读出来展示」，一旦需要「按内层字段过滤、排序、聚合」，就该考虑正规化。", 'sql36': '数据仓库还有一个绕不开的话题是缓慢变化维度：英雄的阵营改名了、用户的等级变了，历史事实应该按当时的值算还是按现在的值算？常见解法是给维度表加生效时间和失效时间，每次变化插一行新记录，事实表通过时间区间关联到「当时那版」维度。这种做法叫拉链表，查询时要多一个时间条件，但能保证历史报表可复现。与之相对的是直接覆盖维度值，简单但会让历史数据「跟着变」。选哪种取决于业务是否需要回看历史口径；财务、审计类通常必须拉链，运营看板常常可以接受覆盖。', 'sql37': '窗口函数还有一个实用组合是「分组内取最新一条」：先用 ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) 编号，再在外层筛 rn = 1。这比「先 GROUP BY 取最大时间、再 JOIN 回原表」更短也更不容易错，尤其在有重复时间戳时行为更可控。另一个组合是同环比：用 LAG(amount) OVER (ORDER BY month) 取上一期值，再用当前值减它。注意 LAG 的默认偏移是 1，可以传第二个参数指定偏移几期，第三个参数指定越界时的默认值，避免第一行算出 NULL 后整列失效。', 'sql38': '漏斗和留存最终都要落到「口径」两个字上：什么算访问（去重设备还是账号）、什么算注册（提交表单还是完成验证）、跨自然日还是滚动 24 小时。同一份数据换一种口径，留存率可能从 40% 变成 25%。所以分析 SQL 写完后，第一件事不是优化性能，而是把口径写成注释或文档，和业务方确认。第二件事是做交叉验证：用另一种写法（比如明细导出到 Python 再算一遍）核对同一个数字，确认没有 JOIN 放大或去重遗漏。数字对不上时，先怀疑口径和 JOIN，再怀疑引擎。'}

DEEP_DIVE_2 = {'sql31': '最后把「看计划」变成日常习惯：新建查询先 EXPLAIN 看一眼，上线前在接近生产的数据量上再看一眼，慢查询告警时第一件事也是看计划。计划会随数据分布、索引增删、SQLite 版本变化，所以它不是一次性结论，而是需要复查看的运行时事实。团队里可以把「贴出执行计划」写进 SQL 评审清单，比争论「这个写法快不快」有效得多——因为争论的双方通常都在凭经验，而计划是证据。', 'sql32': '还有一个和索引强相关的概念是索引选择性统计：同样的复合索引，列顺序不同效果可能差几倍。判断顺序时先看每个列的基数（不同取值数量），把基数最高、且查询里最常单独出现的列放最左。如果两个列总是一起出现，顺序影响就小，可以按可读性排。改索引前记得先记录当前计划与耗时，改完用同样的数据量对比，否则「感觉快了」很可能是缓存或数据量的错觉。', 'sql33': '把事务和业务语义对齐，比记住语法更重要：一次下单、一次转账、一次库存扣减，天然就是一个事务边界；而「用户填表 → 提交 → 发邮件」这种跨外部系统的流程，不能靠数据库事务包住。正确做法是把数据库操作收在一个短事务里，外部动作放到事务之后，用补偿或重试处理失败。理解这条边界，你就不会写出「事务里调接口」这种既慢又不可靠的代码。', 'sql34': '除了数据库锁，应用层还要处理重试：拿到 0 行受影响时，是立刻放弃还是重试几次？答案取决于业务。任务领取通常「抢不到就下一轮」，不需要重试；库存扣减则可能需要在有限次数内重试并给出用户提示。重试必须配合退避（比如 10ms、50ms、200ms），否则高并发下所有请求会同时再撞一次。把「冲突是常态」写进设计，比假设「不会冲突」稳得多。', 'sql35': 'JSON 列还有一个容易踩的坑是编码与大小：整段 JSON 存在 TEXT 列里，体积可能比正规化后的列大好几倍，读的时候还要解析。高频读且字段固定时，正规化几乎总是更优；字段稀疏、结构多变时，JSON 才划算。折中方案是「热字段抽列、冷字段留 JSON」，把最常查的几个键提升为真实列并建索引，其余留在 payload 里。这样既保留了灵活性，又不会让每次查询都解析整段文本。', 'sql36': '建仓库表时还要先想清楚粒度：一行事实代表什么？一次跑单、一天、还是一个用户一个月的汇总？粒度越细，能回答的问题越多，但数据量越大；粒度越粗，查询快但会丢失细节。原则是「按最细的业务事件存事实，聚合在查询时做」，除非数据量大到必须预聚合。预聚合表要标注口径与刷新时间，否则很容易出现「报表数字和明细对不上」的经典问题。', 'sql37': '最后提醒窗口函数的执行顺序：WHERE → GROUP BY → HAVING → 窗口计算 → ORDER BY → LIMIT。这解释了为什么窗口结果不能用于 WHERE（那时还没算），也解释了为什么窗口函数可以和聚合共存（聚合先算，窗口在结果集上再算）。理解这个顺序，很多「为什么这行 SQL 报错」的问题会自己消失；剩下真正需要拆子查询的场景，也会清楚该在哪一层拆。', 'sql38': '分析 SQL 的可维护性还体现在命名上：CTE 名用业务词（first_seen、activity）而不是 t1、t2，列名带单位（amount_cents、duration_sec），中间步骤加注释说明口径。半年后回来看的人（往往是未来的你）能不能在五分钟内读懂，是判断这段 SQL 好不好的实际标准。性能可以后面优化，可读性一旦丢了，改错的风险比慢查询高得多。'}

DEEP_DIVE_3 = {'sql31': '顺带说清一个常见误解：加了索引不等于查询一定快，因为索引本身也要读。如果表只有几十行，全表扫描读一页就结束，走索引反而要读索引页加回表页，优化器会正确地选择 SCAN。所以小表上看到 SCAN 不必紧张；真正要盯的是「表会变大，而查询条件只命中极少行」这类组合。判断时机比判断好坏重要。', 'sql32': '最后再做一次索引盘点：把库里所有索引列出来，对照真实的慢查询清单逐条问「这个索引服务哪条查询」。服务不到的索引就是纯成本，应当删掉；服务多条但顺序不对的，考虑重排或拆分。索引是给查询用的，不是给表「看起来很专业」用的。定期盘点比一次建全更可靠。', 'sql33': '最后补充一个实用判断：如果你发现自己在事务里写了大量纯读取的语句，那多半不该放在同一个事务里。读多写少的流程可以把读前置，事务只包最后的写入。这样锁窗口最短，失败重试的代价也最小。事务不是「越全越好」，而是「刚好覆盖需要原子的那几步」。', 'sql34': '最后把并发问题归成一句话：能交给数据库一条语句解决的，就不要拆成两条。条件更新、原地加减、INSERT ... ON CONFLICT，都是把「判断 + 写入」压缩成原子的手段。每压缩一步，就少一个竞态窗口；剩下的窗口，才需要靠锁或重试来兜。这个顺序比一上来就加锁更有效。', 'sql35': '最后一点经验：JSON 里的字段名尽量稳定，不要用业务中文当键，也不要随版本改键名。字段名一改，所有历史数据都要迁移，而 JSON 数据往往没有 schema 约束，出错时很难发现。把键名当 API 契约管理，写进文档，改名前先统计影响行数，能避免大多数「突然查不到数据」的事故。', 'sql36': '最后提醒 SQL 层面的口径一致：同一个指标不要在两处各写一套 SQL，否则时间一长必然对不上。把核心指标固化成视图或 CTE 片段，所有报表引用同一份定义，改动只在一处发生。视图在 SQLite 里就是保存下来的查询，代价可忽略，收益是可维护性。', 'sql38': '最后给一条练习建议：拿到任何一份分析需求，先用一句话写出「分子、分母、时间范围、去重口径」，再动手写 SQL。如果这句话写不完整，说明需求本身没想清楚，此时写出的 SQL 大概率要重写。写清楚之后再拆 CTE，往往一次就能对上业务预期。'}

DEEP_DIVE_4 = {'sql33': '把这三段连起来看：原子性保证改动的边界，隔离性保证别人看不到中间态，持久性保证提交之后不再丢。业务代码只需要回答一个问题——这几步改动是不是必须同生共死？是，就用事务；不是，就拆开。判断错了，要么出现半成品数据，要么把无关操作锁在一起。', 'sql36': '补充一个落地顺序：先定事实表粒度，再定维度，最后才想宽表。顺序反了会反复改表结构，成本最高。粒度定错尤其致命——事后想从日汇总拆回单次事件几乎不可能，只能重跑历史数据。所以宁可先细后粗。', 'sql38': '还有一个细节值得写进习惯：任何计数都问一句「会不会重复」。JOIN 之后一个用户可能变成多行，COUNT 立刻虚高；此时要么先去重（COUNT DISTINCT），要么把聚合放到子查询里再 JOIN。这个检查能挡住大部分分析口径事故。'}

for _lesson in LESSONS:
    for _table in (DEEP_DIVE, DEEP_DIVE_2, DEEP_DIVE_3, DEEP_DIVE_4):
        _extra = _table.get(_lesson["id"])
        if _extra:
            _lesson["blocks"].append(paragraph(_extra))



# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------

EXTRA_TESTS = {'sql31': ["assert 'idx_events_kind' in __stdout__ or 'SEARCH' in __stdout__, '应体现索引已建立'"], 'sql32': ["assert rows[0][1] == 90, '第一名应为 90 分'"], 'sql33': ["assert len(rows) == 2, '事务后应只剩两个账户'"], 'sql34': ["assert rows[0][1] == 2, '应剩两个 pending 任务'"], 'sql35': ["assert rows[0][0] == 7, '出现次数最多的应是用户 7'"], 'sql36': ["assert len(rows) == 2, '两个月应各一行'"], 'sql37': ["assert rows[0][0] == 1, '第一个名次应为 1'"], 'sql38': ["assert rows[0][2] == 1, '首日 2026-01-01 的 D1 应为 1'"]}


def check():
    problems = []
    ids = [l["id"] for l in LESSONS]
    if ids != [f"sql{n}" for n in range(31, 39)]:
        problems.append(f"讲 id 应为 sql31..sql38，实际 {ids}")
    orders = [l["order"] for l in LESSONS]
    if orders != list(range(530, 538)):
        problems.append(f"order 应为 530..537，实际 {orders}")
    for l in LESSONS:
        lid = l["id"]
        if l["chapter"] != CHAPTER or l["chapterName"] != CHAPTER_NAME:
            problems.append(f"{lid}: chapter 不正确")
        blocks = l["blocks"]
        if len(blocks) < 10:
            problems.append(f"{lid}: 内容块过少（{len(blocks)}）")
        text_cjk = sum(len(b.get("text", "")) for b in blocks if b["type"] in ("text",))
        if not (900 <= text_cjk <= 1600):
            problems.append(f"{lid}: 正文长度 {text_cjk} 不在 900–1600")
        code_n = sum(1 for b in blocks if b["type"] == "code")
        out_n = sum(1 for b in blocks if b["type"] == "output")
        if code_n != out_n:
            problems.append(f"{lid}: code 块 {code_n} 与 output 块 {out_n} 不配对")
        if not any(b["type"] in ("table", "diagram") for b in blocks):
            problems.append(f"{lid}: 缺 table/diagram")
        if not any(b["type"] == "quiz" for b in blocks):
            problems.append(f"{lid}: 缺 quiz")
        for b in blocks:
            if b["type"] == "quiz" and not (0 <= b["answer"] < len(b["options"])):
                problems.append(f"{lid}: quiz 答案越界")
        ex = l["exercise"]
        ex["tests"] = list(ex["tests"]) + EXTRA_TESTS.get(lid, [])
        if not (3 <= len(ex["tests"]) <= 5):
            problems.append(f"{lid}: tests 数量 {len(ex['tests'])} 不在 3–5")
        r = sql_runner.check_sql(ex["solution"], ex["tests"])
        if not r["passed"]:
            problems.append(f"{lid}: 参考答案未通过 {r['error']}")
        rs = sql_runner.check_sql(ex["starterCode"], ex["tests"])
        if rs["passed"]:
            problems.append(f"{lid}: starter 不应通过")
        if ex["solution"].strip() == ex["starterCode"].strip():
            problems.append(f"{lid}: starter 与 solution 相同")
    return problems


def main():
    problems = check()
    if problems:
        print("自检失败：")
        for p in problems:
            print(" -", p)
        return 1
    OUT.write_text(json.dumps(LESSONS, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8", newline="\n")
    print(f"sql-expert: {len(LESSONS)} 讲 -> {OUT.name}")
    total_tests = sum(len(l["exercise"]["tests"]) for l in LESSONS)
    print(f"判题用例={total_tests} 输出块=真实执行生成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
