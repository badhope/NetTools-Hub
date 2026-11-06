#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 SQL 30 讲课程包（基础 / 核心 / 进阶）。

运行：python tools/gen_sql_curriculum.py
产物：content_packs/sql-basics.json、sql-core.json、sql-advanced.json

每讲的 output 块不是手写的：demo() 会把同一段 SQL 送进
app/src/main/python/sql_runner.py 真实执行，取最后一条语句的结果集渲染成
制表符分隔的表格文本。这样课程内容与 SQLite 实际行为不会漂移。
"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app" / "src" / "main" / "python"))

import sql_runner  # noqa: E402

HAN = re.compile(r"[\u4e00-\u9fff]")


def render_last(sql):
    result = sql_runner._execute(sql)
    if not result["ok"]:
        raise RuntimeError("示例执行失败：%s\n%s" % (result["error"], sql))
    last = result["last"]
    if last is None:
        raise RuntimeError("示例没有结果集：%s" % sql)
    lines = ["\t".join(last["columns"])]
    for row in last["rows"]:
        lines.append("\t".join("NULL" if v is None else str(v) for v in row))
    return "\n".join(lines)


def heading(text):
    return {"type": "heading", "text": text}


def para(text):
    return {"type": "text", "text": text}


def demo(sql):
    return [
        {"type": "code", "code": sql, "runnable": True},
        {"type": "output", "text": render_last(sql)},
    ]


def reading(sql):
    return [{"type": "code", "code": sql, "runnable": False}]


def table(headers, rows):
    return {"type": "table", "headers": headers, "rows": rows}


def diagram(text):
    return {"type": "diagram", "text": text}


def tip(text):
    return {"type": "tip", "text": text}


def warn(text):
    return {"type": "warn", "text": text}


def quiz(question, options, answer, explain):
    return {
        "type": "quiz",
        "question": question,
        "options": options,
        "answer": answer,
        "explain": explain,
    }


def exercise(title, brief, starter, hint, tests, solution, xp):
    return {
        "title": title,
        "brief": brief,
        "starterCode": starter,
        "hint": hint,
        "tests": tests,
        "stdin": [],
        "xp": xp,
        "solution": solution,
    }


CONTINUATION_HEADS = (
    "它", "这", "那", "其", "该", "此", "因此", "所以", "不过", "但", "而", "也", "还",
    "另外", "同时", "于是", "然而", "并且", "后者", "前者", "两者", "三者",
)


def merge_paras(paras):
    """把叙述按句子边界切成 3 段，优先在「话题起始句」处断段。"""
    text = "".join(paras)
    sentences = [s for s in re.split(r"(?<=。)", text) if s]
    if len(sentences) <= 3:
        return sentences or [text]

    total = sum(len(s) for s in sentences)
    target = total / 3.0

    def boundary_score(index, group_index):
        """index 处断段的代价：离目标长度越远越差，续接词开头更差。"""
        head = sentences[index]
        length = sum(len(s) for s in sentences[:index])
        distance = abs(length - target * (group_index + 1))
        penalty = 0
        if head.startswith(CONTINUATION_HEADS):
            penalty = 60
        return distance + penalty

    cuts = []
    start_index = 0
    for group_index in range(2):
        remaining_groups = 2 - group_index
        candidates = list(range(start_index + 1, len(sentences) - remaining_groups + 1))
        if not candidates:
            break
        best = min(candidates, key=lambda i: boundary_score(i, group_index))
        cuts.append(best)
        start_index = best

    groups = []
    prev = 0
    for cut in cuts:
        groups.append("".join(sentences[prev:cut]))
        prev = cut
    groups.append("".join(sentences[prev:]))
    return groups


def mk(spec):
    blocks = [heading(spec["head"])]
    blocks.extend(para(p) for p in merge_paras(spec["paras"]))
    if spec.get("before"):
        blocks.extend(spec["before"])
    blocks.extend(demo(spec["demo"]))
    mid = spec["mid"]
    if isinstance(mid, list):
        blocks.extend(mid)
    else:
        blocks.append(mid)
    if spec.get("demo2"):
        blocks.extend(demo(spec["demo2"]))
    if spec.get("after"):
        blocks.extend(spec["after"])
    blocks.append(tip(spec["tip"]))
    blocks.append(warn(spec["warn"]))
    blocks.append(quiz(*spec["quiz"]))
    return {
        "id": spec["id"],
        "order": spec["order"],
        "chapter": spec["chapter"],
        "chapterName": spec["chapterName"],
        "lang": "sql",
        "title": spec["title"],
        "subtitle": spec["subtitle"],
        "xp": spec["xp"],
        "blocks": blocks,
        "exercise": spec["ex"],
    }


def prose_len(item):
    total = 0
    for b in item["blocks"]:
        t = b.get("type")
        if t in ("heading", "text", "tip", "warn"):
            total += len(HAN.findall(b["text"]))
        elif t == "quiz":
            total += len(HAN.findall(b["question"]))
            total += len(HAN.findall(b["explain"]))
            total += sum(len(HAN.findall(o)) for o in b["options"])
        elif t == "table":
            total += sum(len(HAN.findall(h)) for h in b["headers"])
            total += sum(len(HAN.findall(c)) for r in b["rows"] for c in r)
    return total


BASICS = "SQL · 基础篇"
CORE = "SQL · 核心篇"
ADVANCED = "SQL · 进阶篇"

PLAYERS = (
    "CREATE TABLE players (\n"
    "  id INTEGER PRIMARY KEY,\n"
    "  name TEXT NOT NULL,\n"
    "  region TEXT,\n"
    "  level INTEGER\n"
    ");\n"
)
PLAYERS_DATA = (
    "INSERT INTO players VALUES\n"
    "  (1, 'V', 'Neon', 66),\n"
    "  (2, 'Judy', 'Neon', 42),\n"
    "  (3, 'Jackie', 'Watson', 30),\n"
    "  (4, 'Rogue', 'Watson', 12);\n"
)
MATCHES = (
    "CREATE TABLE matches (\n"
    "  id INTEGER PRIMARY KEY,\n"
    "  player TEXT,\n"
    "  mode TEXT,\n"
    "  score INTEGER\n"
    ");\n"
)
MATCHES_DATA = (
    "INSERT INTO matches VALUES\n"
    "  (1, 'V', 'ranked', 88),\n"
    "  (2, 'Judy', 'ranked', 95),\n"
    "  (3, 'Jackie', 'casual', 72),\n"
    "  (4, 'V', 'casual', 60),\n"
    "  (5, 'Rogue', 'ranked', 45);\n"
)


def basics_01_05():
    return [
        mk({
            "id": "sql01", "order": 500, "chapter": 51, "chapterName": BASICS,
            "title": "第一次查询", "subtitle": "SELECT 与 FROM", "xp": 60,
            "head": "数据库开口说话",
            "paras": [
                "SQL 是结构化查询语言。它和 Python 这类过程式语言的工作方式不同：你只描述想要什么结果，"
                "由数据库负责决定怎么扫描、怎么过滤、怎么返回，具体执行路径交给查询优化器安排。一条最基础的"
                "查询由 SELECT 和 FROM 两个子句组成，SELECT 决定返回哪些列，FROM 决定从哪张表取数据。"
                "课程使用 SQLite 内存数据库，每次运行都从零开始建表，上一次运行留下的数据不会影响下一次，"
                "因此可以放心反复试验，不用担心把环境弄坏，也不用在每次练习前写清理脚本。",

                "列名直接写在 SELECT 后面，多个列用逗号分隔，书写顺序就是结果里的列顺序。写 SELECT name, level "
                "得到两列；写 SELECT level, name 得到的两列顺序相反，这一点在做报表时很重要，导出文件的列序"
                "往往由 SELECT 列表决定。星号可以表示全部列，适合临时查看表结构，正式查询里最好显式列出需要的列，"
                "这样别人能一眼看出结果包含什么，也不会因为表结构变化而多出意外的字段。FROM 后面接表名，"
                "表必须先存在，所以示例先建表、再写入数据、最后查询，三步构成一个完整脚本，顺序颠倒就会报"
                "「no such table」错误。",

                "SQL 语句以分号结尾，一条脚本里可以按顺序写多条语句，数据库会依次执行。关键字大小写不敏感，"
                "SELECT 和 select 完全等价，但团队通常约定关键字大写、表名与列名小写，读起来层次更清楚。"
                "初学者最容易犯的错误是漏写 FROM，或者把表名写在 SELECT 后面；记住顺序口诀「先选列，再选表」，"
                "即 SELECT 列表在前、FROM 表名在后，就不会写反。列名和表名不要用保留字，例如 order、group、"
                "select，真要用必须加引号，不如一开始就换个名字，省掉后面所有麻烦。写查询时先想清楚要哪些列、"
                "来自哪张表，再考虑过滤和排序，顺序理清了，语句自然就写顺了。",

                "从数据组织的角度看，一张表就是若干行与若干列组成的二维结构，每一行代表一条记录，每一列代表"
                "一个属性。列有类型，SQLite 常用 INTEGER 存整数、TEXT 存文本、REAL 存浮点数，虽然它允许"
                "动态类型、同一列可以混放不同种类，但建表时写清类型是给读代码的人看的契约，也能让工具"
                "正确推导结果。id 这类标识列习惯用 INTEGER 并设为主键，名字、地区用 TEXT，等级、分数用"
                "INTEGER。把这些基础概念记牢，后面学约束、连接、索引时才知道每一步在保护什么。",

                "最后养成一个习惯：每写一条查询，先在纸上或注释里用一句中文说清它要回答什么问题，"
                "例如「列出所有玩家及其等级」。如果这句话说不出来，说明需求还没想清楚，写出来的 SQL 大概率"
                "会返工。查询写完后，用小数据集手工推演一遍预期结果，再和数据库返回的行数、列名对比，"
                "差异出现时先查列名是否拼错、表是否连对、条件是否被 AND 与 OR 的优先级改写。这样的自查"
                "能挡掉大部分低级错误，也让后续调试有明确的对照物，而不是靠猜。",

                "还有一点值得提前说明：本课程所有示例都在内存库中执行，脚本里写的 CREATE TABLE "
                "和 INSERT 会在同一次运行内生效，运行结束数据库即被销毁。这意味着你不必担心"
                "「练习会不会污染环境」，可以大胆修改数值、增删列、故意写错看报错。"
                "学习 SQL 最有效的方式就是不断做小实验：改一个条件、看结果差几行；"
                "换一种连接方式、看列数怎么变。每一次动手验证，都会比读一遍讲解留下更深的印象。",
            ],
            "demo": PLAYERS + PLAYERS_DATA + "\nSELECT name, level FROM players;",
            "mid": table(
                ["子句", "作用", "示例"],
                [
                    ["SELECT", "选择要返回的列", "SELECT name, level"],
                    ["FROM", "指定数据来源的表", "FROM players"],
                    ["AS", "给列或表起别名", "SELECT name AS player"],
                    [":", "结束一条语句", "SELECT * FROM players;"],
                ],
            ),
            "demo2": PLAYERS
            + "INSERT INTO players VALUES (1, 'V', 'Neon', 66), (2, 'Judy', 'Neon', 42);\n"
            "\nSELECT id, name, level FROM players;\n-- 等价写法：SELECT * FROM players;",
            "tip": "给列起别名用 AS，别名只在结果集中生效，不会改表结构。别名含空格或中文时用双引号包起来，"
                   "例如 AS \"玩家等级\"，这样导出的表头也好读。",
            "warn": "SELECT * 会返回全部列。表后来新增大字段时，旧查询也会把它们带出来，既浪费带宽又可能暴露"
                    "不该展示的数据，生产查询应显式列名。",
            "quiz": (
                "要从 players 表只取出 name 和 level 两列，正确写法是？",
                [
                    "SELECT players FROM name, level",
                    "SELECT name, level FROM players",
                    "FROM players SELECT name, level",
                    "SELECT name AND level FROM players",
                ],
                1,
                "列在前、表在后：SELECT 列 FROM 表，多个列用逗号分隔。",
            ),
            "ex": exercise(
                "取出玩家名单",
                "从 players 表取出 name 与 level 两列，按 id 升序排列。",
                PLAYERS + PLAYERS_DATA + "\n-- 在这里写查询：取出 name 与 level\n",
                "SELECT name, level FROM players ORDER BY id;",
                [
                    "assert columns == ['name', 'level'], columns",
                    "assert rows == [['V', 66], ['Judy', 42], ['Jackie', 30], ['Rogue', 12]], rows",
                    "assert len(rows) == 4, rows",
                ],
                PLAYERS + PLAYERS_DATA + "\nSELECT name, level FROM players ORDER BY id;\n",
                80,
            ),
        }),
        mk({
            "id": "sql02", "order": 501, "chapter": 51, "chapterName": BASICS,
            "title": "按条件挑行", "subtitle": "WHERE 与比较运算", "xp": 70,
            "head": "只留下符合条件的行",
            "paras": [
                "WHERE 子句在 FROM 之后执行，对每一行做一次判断：条件为真就保留，为假或为 NULL 就丢弃。"
                "最基本的条件是列与值的比较，支持等于、不等于、大于、小于、大于等于、小于等于。数字直接写，"
                "字符串必须用单引号包起来，日期在 SQLite 里通常也写成 ISO 格式的字符串，例如 '2024-03-15'。"
                "一行数据是否进入结果集，完全取决于条件表达式的布尔值，而不取决于它排在第几行，这也是"
                "声明式语言和手写循环筛选最本质的区别：你定义规则，数据库负责逐行套用。",

                "多个条件用 AND、OR、NOT 组合。AND 要求两边都为真，OR 只要一边为真，NOT 取反。AND 的优先级"
                "高于 OR，混用时要加括号。例如 mode = 'ranked' OR mode = 'duo' AND score > 80 会先算后半段，"
                "实际含义和直觉不同；写成 (mode = 'ranked' OR mode = 'duo') AND score > 80 才清楚。"
                "括号不会降低性能，却能消除歧义，复杂条件建议一行写一个条件、用括号分组，让阅读者不必"
                "在脑子里背优先级表。条件写得越清楚，后面排查「为什么少了某一行」时就越省力。",

                "BETWEEN a AND b 等价于列大于等于 a 且小于等于 b，包含两端；IN (值一, 值二) 等价于一串 OR "
                "比较，适合枚举几个固定值。LIKE 做模式匹配，百分号代表任意长度字符，下划线代表单个字符。"
                "WHERE 只过滤行，不改变返回的列，也不会去重，去重是 DISTINCT 的职责，分组统计是 GROUP BY 的"
                "职责。把每个子句的职责分清楚，写复杂查询时才不会互相打架，结果不符合预期时也能快速判断"
                "问题出在筛选、分组还是排序环节。先写最小的 WHERE 验证命中几行，再逐步加条件，是排查"
                "筛选问题的通用方法。",

                "还有一个容易被忽略的细节：文本比较默认区分大小写。SQLite 的 = 与 LIKE 对 ASCII 字母的大小写"
                "敏感度并不相同，= 区分大小写，LIKE 默认不区分，这种不一致在跨数据库迁移时经常引发问题。"
                "需要忽略大小写时，可以统一用 LOWER(列) = LOWER(值)，或者在建表时给列加 COLLATE NOCASE。"
                "数值与文本混用时，SQLite 会按类型亲和性做转换，'10' 与 10 比较往往相等，但换到其他数据库"
                "就会报类型错误，所以列类型要前后一致，不要一会儿存数字一会儿存字符串。日期同理，"
                "统一存成 YYYY-MM-DD 的文本，比较和排序才符合预期。",

                "练习时可以把 WHERE 当成一个筛子来理解：数据从表中流出，每行经过筛孔，条件为真的留下，"
                "其余落下。想验证筛孔是否合适，最简单的办法是先用 SELECT * 加同样的 WHERE 看完整行，"
                "确认留下的记录确实符合业务判断，再把列裁剪成需要的那几列。很多看似「SQL 写错」的问题，"
                "其实是条件本身写错，比如把「大于」写成「大于等于」，把「或」写成「与」，或者漏掉一个"
                "括号导致优先级变化。逐条对照业务描述检查这些边界，比盲目改语法有效得多。",

                "最后补充一个常用组合：WHERE 加 IN 做多值筛选。游戏运营经常要查「这几个地区的玩家」，"
                "写 region IN ('Neon', 'Watson', 'Arasaka') 比串三个 OR 简洁得多，也不容易漏括号。"
                "IN 的列表里可以混放数字和字符串，但类型要统一，混用会让优化器放弃索引。"
                "列表过长时（超过几百项）应改用临时表或 JOIN，避免 SQL 文本膨胀、解析变慢。",
            ],
            "demo": MATCHES + MATCHES_DATA + "\nSELECT player, score\nFROM matches\n"
                                             "WHERE mode = 'ranked' AND score >= 80\nORDER BY score DESC;",
            "mid": table(
                ["运算符", "含义", "示例"],
                [
                    ["=", "等于", "mode = 'ranked'"],
                    ["<> / !=", "不等于", "mode <> 'casual'"],
                    [">= / <=", "大于等于 / 小于等于", "score >= 80"],
                    ["BETWEEN", "闭区间", "score BETWEEN 60 AND 90"],
                    ["IN", "属于列表", "mode IN ('ranked', 'duo')"],
                    ["LIKE", "模式匹配", "name LIKE 'J%'"],
                ],
            ),
            "demo2": MATCHES + MATCHES_DATA + "\nSELECT player, mode, score\nFROM matches\n"
                                               "WHERE score BETWEEN 70 AND 90\n  AND mode IN ('ranked', 'casual')\n"
                                               "ORDER BY score;",
            "tip": "字符串常量用单引号，双引号在标准 SQL 里是标识符。SQLite 对双引号比较宽容，但换到 PostgreSQL "
                   "或 MySQL 严格模式就会报错，从一开始就养成单引号的习惯。",
            "warn": "条件里写 name = NULL 永远不成立，因为 NULL 表示未知，任何与它的比较结果还是 NULL。"
                    "判断空值必须用 IS NULL 或 IS NOT NULL，这一点在 NULL 那一讲会展开。",
            "quiz": (
                "WHERE score BETWEEN 60 AND 90 会保留哪些行？",
                [
                    "60 到 90 之间，不含 60 和 90",
                    "60 到 90 之间，含 60 和 90",
                    "只保留 60 和 90 两行",
                    "所有大于 90 的行",
                ],
                1,
                "BETWEEN 是闭区间，等价于 score >= 60 AND score <= 90。",
            ),
            "ex": exercise(
                "筛选高等级玩家",
                "从 players 表选出 level 大于等于 30 且 region 为 'Neon' 的玩家 name，按 level 从高到低排列。",
                PLAYERS + PLAYERS_DATA + "\n-- 在这里写查询\n",
                "SELECT name FROM players WHERE level >= 30 AND region = 'Neon' ORDER BY level DESC;",
                [
                    "assert columns == ['name'], columns",
                    "assert rows == [['V'], ['Judy']], rows",
                    "assert len(rows) == 2, rows",
                ],
                PLAYERS + PLAYERS_DATA
                + "\nSELECT name FROM players\nWHERE level >= 30 AND region = 'Neon'\nORDER BY level DESC;\n",
                90,
            ),
        }),
        mk({
            "id": "sql03", "order": 502, "chapter": 51, "chapterName": BASICS,
            "title": "排序与截断", "subtitle": "ORDER BY 与 LIMIT", "xp": 70,
            "head": "让结果按规则排队",
            "paras": [
                "ORDER BY 决定结果行的顺序，写在 WHERE 之后。默认是 ASC 升序，从小到大；加 DESC 变成降序。"
                "可以按多列排序，先按第一列排，第一列相同再按第二列排，例如 ORDER BY score DESC, id ASC。"
                "多列排序是保证结果稳定的关键：只按分数排序时，同分的行谁前谁后由数据库决定，换一台机器、"
                "换一个版本都可能变，而分页和「取前三名」这类需求恰恰要求顺序确定，否则同一条记录可能"
                "在相邻两页各出现一次，也可能一次都不出现。",

                "LIMIT n 只返回前 n 行，OFFSET m 跳过前 m 行，它们写在语句最后，常用来做分页：第一页 "
                "LIMIT 10 OFFSET 0，第二页 LIMIT 10 OFFSET 10。分页必须配合确定的排序，否则翻页时同一条记录"
                "可能出现两次或一次都不出现，因为每次查询的底层顺序并不保证一致。数据量大时 OFFSET 越深越慢，"
                "数据库仍要先数过前面所有行，深度翻页通常要改成「记住上一页最后一条的键值」的游标方式，"
                "把 OFFSET 换成 WHERE id > 上一页最后一个 id，这样每页都能直接跳到起点附近。",

                "SQLite 里 NULL 在排序中被视为最小值：升序时排在最前，降序时排在最后。如果业务上希望空值永远"
                "垫底，可以加 NULLS LAST，或者用 CASE WHEN 列 IS NULL THEN 1 ELSE 0 END 先排一个标记列。"
                "排序发生在 SELECT 之后，所以 ORDER BY 里可以使用 SELECT 中定义的别名，这一点和 WHERE 不同，"
                "WHERE 不能引用别名，因为那时 SELECT 还没有求值。理解这个求值顺序，能解释很多「别名不生效」"
                "的疑问，也能解释为什么 HAVING 可以引用聚合别名而 WHERE 不行。记住大致顺序：FROM、WHERE、"
                "GROUP BY、HAVING、SELECT、ORDER BY、LIMIT。",

                "分页还有两个实用细节。第一，LIMIT 后面的数字必须是常量或参数，不能是列名，也不能用表达式"
                "动态拼进 SQL 字符串，那会带来注入风险，正确做法是使用参数占位符。第二，总数与当前页往往"
                "需要两条查询：一条 SELECT COUNT(*) 算总数，一条带 LIMIT OFFSET 取数据，前端据此渲染页码。"
                "如果数据经常变化，两次查询之间可能插入新行，页码会轻微漂移，这在社交信息流里可以接受，"
                "但在对账类场景里要改用快照或游标，保证翻页过程看到的是同一批数据。",

                "排序还有一个常被忽略的代价：如果排序的列上没有索引，数据库需要把整个结果集读进内存再排，"
                "数据量大时会写临时文件，速度明显下降。生产环境里高频的排行榜查询通常会在排序键上建索引，"
                "或者把排名结果预计算成一张表定时刷新。作为初学者，先把语义写对，再考虑性能；但心里要清楚"
                "ORDER BY 不是免费的，看到慢查询时它是第一个值得检查的子句。同理，LIMIT 只有在排序确定"
                "且能提前终止扫描时才是真正的优化，否则它只是截断了输出，底层仍可能扫完所有行。"
                "真正要提速，还是得让排序键上有可用的索引，或者缩小参与排序的数据量。",

                "另外，ORDER BY 与 GROUP BY 同时出现时，排序发生在分组之后，作用于每组一行。"
                "如果想按聚合值排序，直接写 ORDER BY COUNT(*) 或 ORDER BY 别名即可，不需要再套子查询。"
                "排序键可以是表达式，例如 ORDER BY ABS(score - 60)，表示离 60 分越近越靠前，"
                "这类用法在推荐和匹配场景里很实用。只要保证表达式在每一行上有唯一确定的值，"
                "排序结果就是稳定的，不会因为执行计划变化而抖动。",
            ],            "demo": "CREATE TABLE matches (\n  id INTEGER PRIMARY KEY,\n  player TEXT,\n  score INTEGER\n);\n"
                    "INSERT INTO matches VALUES\n  (1, 'V', 90),\n  (2, 'Judy', 90),\n"
                    "  (3, 'Jackie', 75),\n  (4, 'Rogue', 60);\n\n"
                    "SELECT player, score\nFROM matches\nORDER BY score DESC, id ASC\nLIMIT 3;",
            "mid": table(
                ["写法", "含义", "说明"],
                [
                    ["ORDER BY score", "按分数升序", "默认 ASC"],
                    ["ORDER BY score DESC", "按分数降序", "大在前"],
                    ["ORDER BY score DESC, id", "多列排序", "分数相同按 id 升序"],
                    ["LIMIT 3", "只取前三行", "必须搭配排序才有意义"],
                    ["LIMIT 2 OFFSET 2", "跳过两行取两行", "分页常用"],
                ],
            ),
            "demo2": "CREATE TABLE matches (\n  id INTEGER PRIMARY KEY,\n  player TEXT,\n  score INTEGER\n);\n"
                     "INSERT INTO matches VALUES\n  (1, 'V', 90),\n  (2, 'Judy', 90),\n"
                     "  (3, 'Jackie', 75),\n  (4, 'Rogue', 60);\n\n"
                     "SELECT player, score\nFROM matches\nORDER BY score DESC, id ASC\nLIMIT 2 OFFSET 2;",
            "tip": "ORDER BY 可以写列名、别名、列序号或表达式。列序号 ORDER BY 2 DESC 虽然短，但别人改 SELECT "
                   "列表时极易排错，团队代码里建议直接写列名或别名。",
            "warn": "不带 ORDER BY 的 LIMIT 3 只是「随便三行」，不是「前三名」。SQL 不保证默认顺序，"
                    "同一条语句执行两次也可能拿到不同结果。",
            "quiz": (
                "ORDER BY score DESC, id ASC 的含义是？",
                [
                    "先按 id 升序，再按 score 降序",
                    "先按 score 降序，分数相同再按 id 升序",
                    "按 score 与 id 的和排序",
                    "只按 score 降序，id 不参与",
                ],
                1,
                "多列排序从左到右依次生效，第一列相同时才比较第二列。",
            ),
            "ex": exercise(
                "分数榜前三",
                "从 matches 表取出 player 与 score，按 score 降序、id 升序取前 3 行。",
                "CREATE TABLE matches (id INTEGER PRIMARY KEY, player TEXT, score INTEGER);\n"
                "INSERT INTO matches VALUES\n  (1, 'V', 90),\n  (2, 'Judy', 90),\n"
                "  (3, 'Jackie', 75),\n  (4, 'Rogue', 60),\n  (5, 'Echo', 75);\n\n-- 在这里写查询\n",
                "SELECT player, score FROM matches ORDER BY score DESC, id ASC LIMIT 3;",
                [
                    "assert columns == ['player', 'score'], columns",
                    "assert rows == [['V', 90], ['Judy', 90], ['Jackie', 75]], rows",
                    "assert len(rows) == 3, rows",
                ],
                "CREATE TABLE matches (id INTEGER PRIMARY KEY, player TEXT, score INTEGER);\n"
                "INSERT INTO matches VALUES\n  (1, 'V', 90),\n  (2, 'Judy', 90),\n"
                "  (3, 'Jackie', 75),\n  (4, 'Rogue', 60),\n  (5, 'Echo', 75);\n\n"
                "SELECT player, score\nFROM matches\nORDER BY score DESC, id ASC\nLIMIT 3;\n",
                90,
            ),
        }),
        mk({
            "id": "sql04", "order": 503, "chapter": 51, "chapterName": BASICS,
            "title": "去掉重复", "subtitle": "DISTINCT 与组合去重", "xp": 70,
            "head": "一列值只留一份",
            "paras": [
                "DISTINCT 紧跟在 SELECT 后面，作用是把结果集中完全相同的行合并成一行。注意它作用于整行，"
                "不是只作用于第一列。SELECT DISTINCT player, mode 会把「玩家加模式」这个组合去重：同一个玩家"
                "在 ranked 和 casual 各出现一次，两条都会保留；只有玩家和模式都相同才算重复。理解这一点，"
                "能避免绝大多数「为什么去重没生效」的困惑，也能解释为什么加了 DISTINCT 行数还是比预期多，"
                "因为多出来的行在另一列上并不相同，数据库认为它们本来就是两条不同的记录。",

                "DISTINCT 和 GROUP BY 都能去重，区别在目的：DISTINCT 只想拿到不重复的值，GROUP BY 是为了"
                "分组做聚合。SELECT DISTINCT mode FROM matches 与 SELECT mode FROM matches GROUP BY mode "
                "结果相同，但后者还能同时算 COUNT(*)、SUM(score)。如果只想去重，DISTINCT 语义更直接；"
                "如果还要统计，用 GROUP BY，不要为了去重硬凑分组。反过来，用 DISTINCT 去重后再算聚合，"
                "往往说明你把两件事混在了同一条查询里，应该拆开或改用分组，否则结果会依赖去重前后的行数，"
                "很难验证正确性。",

                "COUNT(DISTINCT 列) 统计一列里不重复的非 NULL 值个数，和 COUNT(*) 完全不同。例如有 100 场"
                "比赛、20 个玩家，COUNT(*) 是 100，COUNT(DISTINCT player_id) 是 20。DISTINCT 会带来排序"
                "或哈希开销，数据量大时比普通查询慢，但它通常比在应用层拉回全部数据再手工去重高效得多，"
                "因为数据库只传回需要的那几行，网络与内存都省了。判断该不该去重，先问「业务上两行算不算"
                "同一件事」，再去决定按哪几列组合。去重条件写错，往往是需求没拆清楚，而不是 SQL 写错了。",

                "实际工作里更常见的情形是「按某列去重后取整行」。比如每位玩家只保留分数最高的一场，"
                "直接 SELECT DISTINCT player, score 并不能做到，因为它仍然按组合判断。正确做法是用 GROUP BY "
                "配合 MAX(score)，或者用窗口函数给每组编号再筛出第一行，后者还能带回整行所有列。"
                "这一讲先把 DISTINCT 的基本语义吃透，等学到窗口函数时，你会发现很多去重需求本质上是"
                "分组排序问题。另外要记住 DISTINCT 对 NULL 的处理：多个 NULL 被视为同一个值，只保留一条，"
                "这和 WHERE 里 NULL 不等于任何值并不矛盾，是两个不同层面的规则。",

                "最后提醒一个工程习惯：不要在业务查询里依赖 DISTINCT 掩盖连接错误。两表连接条件写错时，"
                "常会出现大量重复行，有人顺手加个 DISTINCT 让结果「看起来正常」，实际上数据已经被笛卡尔积"
                "放大，统计口径全错。正确顺序是先验证连接键是否唯一、连接后行数是否符合预期，再决定是否"
                "需要去重。去重是业务语义的一部分，不是修复查询的万能补丁。把这一点想明白，后面学 JOIN 和"
                "聚合时就能少走很多弯路，也更容易向同事解释你的查询为什么这么写。",

                "从实现角度看，DISTINCT 通常要对结果排序或建哈希表才能发现重复，因此它和 ORDER BY 常常"
                "共享同一份排序结果，写在一起时数据库有机会只排一次。但如果 SELECT 的列很多、行数很大，"
                "这份临时结构可能落到磁盘上，查询就会明显变慢。遇到这种情况，先确认是否真的需要整行去重，"
                "能否改成按主键分组，或者把去重放到应用层按业务键处理。判断标准不是「哪种写法更高级」，"
                "而是「哪种写法用更少的中间数据回答了同一个问题」。",
            ],
            "demo": "CREATE TABLE matches (\n  id INTEGER PRIMARY KEY,\n  player TEXT,\n  mode TEXT\n);\n"
                    "INSERT INTO matches VALUES\n  (1, 'V', 'ranked'),\n  (2, 'Judy', 'ranked'),\n"
                    "  (3, 'V', 'casual'),\n  (4, 'Jackie', 'duo'),\n  (5, 'Judy', 'duo');\n\n"
                    "SELECT DISTINCT mode FROM matches ORDER BY mode;",
            "mid": table(
                ["写法", "结果", "说明"],
                [
                    ["DISTINCT mode", "casual, duo, ranked", "一列去重"],
                    ["DISTINCT player, mode", "五行组合去重", "整行比较"],
                    ["COUNT(DISTINCT player)", "3", "不重复玩家数"],
                    ["GROUP BY mode", "分组", "可同时聚合"],
                ],
            ),
            "demo2": "CREATE TABLE matches (\n  id INTEGER PRIMARY KEY,\n  player TEXT,\n  mode TEXT\n);\n"
                     "INSERT INTO matches VALUES\n  (1, 'V', 'ranked'),\n  (2, 'Judy', 'ranked'),\n"
                     "  (3, 'V', 'casual'),\n  (4, 'Jackie', 'duo'),\n  (5, 'Judy', 'duo');\n\n"
                     "SELECT DISTINCT player, mode\nFROM matches\nORDER BY player, mode;",
            "tip": "DISTINCT 不是函数，不能写成 DISTINCT(player)。它修饰的是整个 SELECT 列表，"
                   "写 SELECT DISTINCT a, b 是对 (a, b) 组合去重。",
            "warn": "DISTINCT 和 ORDER BY 一起用时，ORDER BY 的列应当出现在 SELECT 列表里，否则不同数据库的"
                    "行为不一致，PostgreSQL 会直接报错。",
            "quiz": (
                "SELECT DISTINCT player, mode 去重的最小单位是？",
                ["player 一列", "mode 一列", "player 与 mode 组成的整行", "所有列加 id"],
                2,
                "DISTINCT 作用于整个选择列表，多列时按组合判断重复。",
            ),
            "ex": exercise(
                "买过高价商品的玩家",
                "从 purchases 表选出 price 大于等于 50 的玩家 player，去重后按字母升序。",
                "CREATE TABLE purchases (id INTEGER PRIMARY KEY, player TEXT, item TEXT, price INTEGER);\n"
                "INSERT INTO purchases VALUES\n  (1, 'V', 'skin', 80),\n  (2, 'V', 'skin', 80),\n"
                "  (3, 'Judy', 'mount', 120),\n  (4, 'Jackie', 'emote', 20),\n  (5, 'Rogue', 'mount', 50);\n\n"
                "-- 在这里写查询\n",
                "SELECT DISTINCT player FROM purchases WHERE price >= 50 ORDER BY player;",
                [
                    "assert columns == ['player'], columns",
                    "assert rows == [['Judy'], ['Rogue'], ['V']], rows",
                    "assert len(rows) == 3, rows",
                ],
                "CREATE TABLE purchases (id INTEGER PRIMARY KEY, player TEXT, item TEXT, price INTEGER);\n"
                "INSERT INTO purchases VALUES\n  (1, 'V', 'skin', 80),\n  (2, 'V', 'skin', 80),\n"
                "  (3, 'Judy', 'mount', 120),\n  (4, 'Jackie', 'emote', 20),\n  (5, 'Rogue', 'mount', 50);\n\n"
                "SELECT DISTINCT player\nFROM purchases\nWHERE price >= 50\nORDER BY player;\n",
                90,
            ),
        }),
        mk({
            "id": "sql05", "order": 504, "chapter": 51, "chapterName": BASICS,
            "title": "算式与比较", "subtitle": "算术与比较运算符", "xp": 80,
            "head": "在查询里做计算",
            "paras": [
                "SELECT 的列表里可以写表达式，不只是列名。加、减、乘、除、取余都能用，还可以用括号控制优先级。"
                "表达式的结果会作为新列返回，列名通常是表达式原文，建议用 AS 起一个可读的别名。例如 "
                "hits * 100.0 / shots AS accuracy 把命中数换算成百分比，结果列就叫 accuracy，前端拿到"
                "数据时不需要再猜这一列是什么意思，导出报表时也不会出现一列名为「hits * 100.0 / shots」"
                "的奇怪表头。计算尽量放在 SQL 里做，能利用数据库的向量化执行，比拉回应用层逐行算更快。",

                "SQLite 的整数除法会截断小数：7 / 2 得到 3，不是 3.5。想要小数结果，至少让一边变成浮点数，"
                "写成 7.0 / 2 或 CAST(7 AS REAL) / 2。这个坑在算比率、平均值时特别常见：hits / shots "
                "很可能直接得到 0，正确写法是 hits * 1.0 / shots。乘 100.0 既完成百分比换算，也顺手把类型"
                "提升为浮点，是教学代码里最常用的技巧之一。另一种稳妥写法是 CAST(表达式 AS REAL)，"
                "意图更明确，团队代码里更容易被审阅者看懂，也不依赖字面量的小数点写法。",

                "比较运算符返回的是布尔值，SQLite 用 1 表示真、0 表示假。所以 SELECT 5 > 3 会返回一行一列，"
                "值是 1。比较可以出现在 WHERE 里，也可以出现在 SELECT 里做标记列，例如 SELECT score >= 80 "
                "AS is_high FROM matches。算术和比较可以嵌套，但要注意 NULL：任何运算只要碰到 NULL，"
                "结果就是 NULL，不会自动当 0 处理，需要兜底时用 COALESCE 包一层，例如 COALESCE(bonus, 0) "
                "加 salary，才能避免整行结果为 NULL。数值精度也要留意，浮点运算可能出现 0.30000000000000004，"
                "展示前用 ROUND 控制小数位，比较金额时尽量用整数分而不是浮点元。",

                "表达式还能和 CASE WHEN 搭配做条件计算，例如用 CASE WHEN score >= 80 THEN 1 ELSE 0 END "
                "统计高分场次；这在后续聚合篇里会大量出现。运算符也有类型规则：字符串相加在 SQLite 里会"
                "被当成数字转换，'a' + 1 得到 1，因为 'a' 转数字失败被当作 0，这种隐式转换既不直观也容易"
                "埋雷，拼接字符串请用 || 而不是 +。写表达式时多问一句「这一列是什么类型、结果是什么类型」，"
                "能避免大量只在特定数据上才暴露的问题。",

                "如果你只记住一句话，记住这个：SQL 里的每个表达式都有类型，类型决定运算规则和比较结果。"
                "整数除整数得整数，字符串拼字符串得字符串，NULL 参与运算得 NULL。把这三条刻进肌肉记忆，"
                "再去看那些看似诡异的输出，大多能立刻找到解释。练习时不妨故意写几个错误表达式，观察"
                "SQLite 返回什么，例如 '5' + 5、NULL + 1、1 / 0，亲手验证过一遍，比读十遍文档印象更深。"
                "这种低成本试探是掌握一门查询语言最快的方式，也符合本课程「每一次运行都从干净内存库开始」"
                "的设计初衷。",

                "表达式写多了会发现一个规律：SQL 的运算符优先级和数学课基本一致，乘除先于加减，比较先于"
                "逻辑运算，括号可以覆盖一切。真正需要额外记忆的只有 AND 与 OR 的高低关系，以及 || 这个"
                "字符串拼接符号。把不熟悉的部分用括号包起来，不仅避免歧义，也让代码审查时一眼看出作者的"
                "意图。宁可多写两层括号，也不要让读代码的人去查优先级表。",

                "补一个类型细节：SQLite 的动态类型允许同一列混放整数、文本和 NULL，但混放会让比较和排序的行为变得难以预测。例如文本 '10' 和整数 9 比较时，SQLite 会按类型亲和性转换，结果可能是 10 > 9，也可能是字典序的 '10' < '9'，取决于列的声明类型。建表时声明 INTEGER 就只存整数，声明 TEXT 就只存文本，这种自律比任何技巧都重要。",
            ],
            "demo": "CREATE TABLE stats (\n  player TEXT,\n  shots INTEGER,\n  hits INTEGER\n);\n"
                    "INSERT INTO stats VALUES\n  ('V', 50, 40),\n  ('Judy', 40, 30),\n  ('Jackie', 25, 10);\n\n"
                    "SELECT player,\n       hits * 100.0 / shots AS accuracy\nFROM stats\n"
                    "ORDER BY accuracy DESC;",
            "mid": table(
                ["运算符", "含义", "注意"],
                [
                    ["+ - * /", "四则运算", "整数相除会截断"],
                    ["%", "取余", "7 % 2 = 1"],
                    ["= <> !=", "等于 / 不等于", "NULL 比较要用 IS"],
                    ["> < >= <=", "大小比较", "返回 1 或 0"],
                    ["AND OR NOT", "逻辑组合", "AND 优先于 OR"],
                ],
            ),
            "demo2": "SELECT 7 / 2 AS int_div,\n       7 % 2 AS remainder,\n       7.0 / 2 AS real_div,\n"
                     "       10 BETWEEN 5 AND 15 AS in_range,\n       'V' <> 'Judy' AS not_equal;",
            "tip": "SELECT 里可以直接算常量，用来验证表达式语义。写完复杂公式先单独 SELECT 一次看结果，"
                   "比直接塞进大查询里排查快得多。",
            "warn": "整数除法截断是 SQLite 的既定行为，不是 bug。比率类计算务必先转浮点，否则 1 / 3 得到 0，"
                    "后续再乘任何数都还是 0。",
            "quiz": (
                "SELECT 7 / 2 在 SQLite 中返回什么？",
                ["3.5", "3", "4", "NULL"],
                1,
                "两个整数相除会截断小数部分，返回 3；要小数请写 7.0 / 2。",
            ),
            "ex": exercise(
                "计算命中率",
                "从 stats 表计算每位玩家的命中率：hits * 100.0 / shots，保留一位小数，列名为 name 与 accuracy，"
                "按 accuracy 降序排列。",
                "CREATE TABLE stats (name TEXT, shots INTEGER, hits INTEGER);\n"
                "INSERT INTO stats VALUES\n  ('V', 50, 40),\n  ('Judy', 40, 30),\n  ('Jackie', 25, 10);\n\n"
                "-- 在这里写查询\n",
                "SELECT name, ROUND(hits * 100.0 / shots, 1) AS accuracy FROM stats ORDER BY accuracy DESC;",
                [
                    "assert columns == ['name', 'accuracy'], columns",
                    "assert rows == [['V', 80.0], ['Judy', 75.0], ['Jackie', 40.0]], rows",
                    "assert len(rows) == 3, rows",
                ],
                "CREATE TABLE stats (name TEXT, shots INTEGER, hits INTEGER);\n"
                "INSERT INTO stats VALUES\n  ('V', 50, 40),\n  ('Judy', 40, 30),\n  ('Jackie', 25, 10);\n\n"
                "SELECT name,\n       ROUND(hits * 100.0 / shots, 1) AS accuracy\nFROM stats\n"
                "ORDER BY accuracy DESC;\n",
                100,
            ),
        }),
    ]


def basics_06_10():
    return [
        mk({
            "id": "sql06", "order": 505, "chapter": 51, "chapterName": BASICS,
            "title": "空值的脾气", "subtitle": "NULL 与 IS NULL", "xp": 90,
            "head": "NULL 不是零，也不是空串",
            "paras": [
                "NULL 表示「这个值未知或不存在」，它既不是数字 0，也不是空字符串。0 是一个确定的数值，"
                "空串是一个长度为零的文本，而 NULL 是「没有值」这个状态本身。这个区别在业务上非常重要："
                "成绩为 0 说明考生考了 0 分，成绩为 NULL 说明这场考试没有记录，两者在统计平均分时的处理"
                "完全不同。建表时凡是业务上不允许缺失的列，都应该加 NOT NULL 约束，把「必须有值」这件事"
                "交给数据库守住，而不是指望每个写入方都记得填。",

                "NULL 最反直觉的地方是它遵循三值逻辑：真、假、未知。任何值与 NULL 做比较，结果都是未知，"
                "而不是真或假。因此 WHERE score = NULL 永远筛不出任何行，WHERE score <> NULL 同样一行都"
                "筛不出，正确写法是 WHERE score IS NULL 或 WHERE score IS NOT NULL。判断两个值是否相等也"
                "不能用 =，要用 IS，例如 NULL IS NULL 返回 1。把 NULL 想成「还没填写的空格」，你就能理解"
                "为什么它和任何东西比较都得不到确定答案。",

                "三值逻辑还会影响 AND 与 OR。真 OR 未知得到真，假 AND 未知得到假，只有结果无法确定时才返回"
                "未知。这意味着 WHERE 里某个条件为 NULL 时，整行可能被过滤掉，哪怕另一个条件已经为真。"
                "排查「明明有数据却查不到」的问题时，先检查条件里有没有可空列参与了比较，再决定用 IS NULL "
                "还是 COALESCE 兜底。COALESCE(a, b, c) 返回第一个非 NULL 的参数，常用于给空值准备默认值；"
                "IFNULL(a, b) 是它的两参数版本，NULLIF(a, b) 则在两值相等时返回 NULL，可用来把哨兵值"
                "转成真正的空值。",

                "聚合函数对 NULL 的处理也值得单独记住：COUNT(*) 数的是行数，包含 NULL；COUNT(列) 只数该列"
                "非 NULL 的行；SUM、AVG、MIN、MAX 都会跳过 NULL，若所有值都是 NULL，结果就是 NULL。"
                "空表上 COUNT 返回 0，而 SUM 返回 NULL，这个差异经常让报表出现空白单元格。排序时 NULL 被"
                "当作最小值，DISTINCT 则把多个 NULL 视为同一个值只保留一条。把这些规则集中记一遍，比每次"
                "遇到问题再猜要高效得多。",

                "工程上还要区分「空字符串」和 NULL。很多前端表单提交空输入时会传来 ''，如果后端直接写库，"
                "这一列就是有值的空串，IS NULL 判断不到，统计非空数量时又会被算进去。稳妥做法是在写入前"
                "统一清洗：空串转 NULL，或者明确禁止空串并用 CHECK (col <> '') 约束。同理，数字 0 和 "
                "NULL 混用会让平均值失真，日期列用 '0000-00-00' 当哨兵值也会让排序和区间查询出错。"
                "在表设计阶段约定「缺失就用 NULL，不要用魔法值」，比事后写一堆特判要省事得多。",

                "最后说说外键列上的 NULL。子表里表示「暂无关联」时，外键列通常允许 NULL，例如玩家还没有"
                "战队，team_id 就是 NULL。这时连接查询要特别小心：INNER JOIN 会把这类行整个丢掉，"
                "LEFT JOIN 才能保留，而 WHERE team_id = 3 又会把 NULL 行再次过滤掉，必须写成 "
                "WHERE team_id = 3 OR team_id IS NULL。NULL 的每个细节单独看都简单，组合起来就容易出错，"
                "所以本讲的重点不是背规则，而是建立「先问这一列能不能为空」的思维习惯。",

                "还有一个实用函数是 NULLIF(a, b)，两个值相等时返回 NULL，否则返回 a。它可以用来避免除零错误：SUM(x) / NULLIF(COUNT(*), 0) 在表为空时返回 NULL 而不是报错。在报表里这比先判断行数再决定是否相除更简洁，也更适合放进视图或 CTE。把 COALESCE 和 NULLIF 这对搭档记住，大多数空值相关的边界都能优雅处理。",
            ],
            "demo": "CREATE TABLE players (\n  id INTEGER PRIMARY KEY,\n  name TEXT NOT NULL,\n"
                    "  sponsor_id INTEGER,\n  score INTEGER\n);\n"
                    "INSERT INTO players VALUES\n  (1, 'V', NULL, 90),\n  (2, 'Judy', 1, NULL),\n"
                    "  (3, 'Jackie', 1, 75),\n  (4, 'Rogue', NULL, NULL);\n\n"
                    "SELECT COUNT(*) AS total,\n       COUNT(sponsor_id) AS with_sponsor,\n"
                    "       COUNT(score) AS with_score\nFROM players;",
            "mid": table(
                ["表达式", "结果", "说明"],
                [
                    ["NULL = NULL", "NULL", "比较结果未知"],
                    ["NULL IS NULL", "1", "判断空值用 IS"],
                    ["COALESCE(NULL, 5)", "5", "取第一个非 NULL"],
                    ["COUNT(*)", "行数", "包含 NULL 行"],
                    ["SUM(x)", "跳过 NULL", "全空时返回 NULL"],
                ],
            ),
            "demo2": "CREATE TABLE players (\n  id INTEGER PRIMARY KEY,\n  name TEXT NOT NULL,\n"
                     "  sponsor_id INTEGER,\n  score INTEGER\n);\n"
                     "INSERT INTO players VALUES\n  (1, 'V', NULL, 90),\n  (2, 'Judy', 1, NULL),\n"
                     "  (3, 'Jackie', 1, 75),\n  (4, 'Rogue', NULL, NULL);\n\n"
                     "SELECT name, COALESCE(score, 0) AS score_or_zero\nFROM players\n"
                     "WHERE score IS NULL\nORDER BY id;",
            "tip": "给列设置默认值时写 DEFAULT 0，而不是允许 NULL 再在查询里到处 COALESCE。"
                   "能在建表阶段消除的空值，就不要留到查询阶段补救。",
            "warn": "NULL 参与算术运算的结果永远是 NULL：100 + NULL 是 NULL，不是 100。"
                    "做金额汇总时先 COALESCE 再相加，否则一条缺失记录会让整列合计变成空白。",
            "quiz": (
                "要筛选出 score 为空的行，正确的条件是？",
                ["WHERE score = NULL", "WHERE score IS NULL", "WHERE score = ''", "WHERE score <> NULL"],
                1,
                "NULL 表示未知，等号比较永远不成立，必须用 IS NULL 判断。",
            ),
            "ex": exercise(
                "为空值兜底",
                "从 players 表选出 sponsor_id 为空的玩家 name，并把他们的 score 用 0 兜底，"
                "输出 name 与 score，按 id 升序。",
                "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT, sponsor_id INTEGER, score INTEGER);\n"
                "INSERT INTO players VALUES\n  (1, 'V', NULL, 90),\n  (2, 'Judy', 1, NULL),\n"
                "  (3, 'Jackie', 1, 75),\n  (4, 'Rogue', NULL, NULL);\n\n-- 在这里写查询\n",
                "SELECT name, COALESCE(score, 0) AS score FROM players WHERE sponsor_id IS NULL ORDER BY id;",
                [
                    "assert columns == ['name', 'score'], columns",
                    "assert rows == [['V', 90], ['Rogue', 0]], rows",
                    "assert len(rows) == 2, rows",
                ],
                "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT, sponsor_id INTEGER, score INTEGER);\n"
                "INSERT INTO players VALUES\n  (1, 'V', NULL, 90),\n  (2, 'Judy', 1, NULL),\n"
                "  (3, 'Jackie', 1, 75),\n  (4, 'Rogue', NULL, NULL);\n\n"
                "SELECT name, COALESCE(score, 0) AS score\nFROM players\nWHERE sponsor_id IS NULL\nORDER BY id;\n",
                110,
            ),
        }),
        mk({
            "id": "sql07", "order": 506, "chapter": 51, "chapterName": BASICS,
            "title": "从行到数字", "subtitle": "COUNT / SUM / AVG / MIN / MAX", "xp": 80,
            "head": "聚合函数把多行压成一个值",
            "paras": [
                "聚合函数接收一组行，返回一个汇总值。最常用的五个是 COUNT 计数、SUM 求和、AVG 求平均、"
                "MIN 取最小、MAX 取最大。不加 GROUP BY 时，整张表被视为一个组，查询结果只有一行。"
                "例如 SELECT COUNT(*) FROM matches 返回比赛总场次，SELECT MAX(score) FROM matches 返回"
                "最高分。聚合让「逐行处理」变成「整体概括」，是报表、看板、对账场景最基础的工具，也是"
                "后面分组统计和窗口函数的起点。",

                "COUNT 有三种常见形态，必须分清楚：COUNT(*) 数所有行，包括含 NULL 的行；COUNT(列) 只数"
                "该列不为 NULL 的行；COUNT(DISTINCT 列) 先对非 NULL 值去重再计数。三者结果可能相差很大，"
                "写报表时选错会让口径完全变样。SUM 和 AVG 同样会跳过 NULL，AVG 的分母是非 NULL 的行数，"
                "不是总行数，所以「平均分」在有缺考记录时往往偏高。需要把空值当 0 参与计算时，先写 "
                "SUM(COALESCE(score, 0))，或者 AVG(COALESCE(score, 0))，把口径显式表达出来。",

                "MIN 和 MAX 不只用于数字，也能用于文本和日期：文本按字典序比较，ISO 格式的日期字符串按"
                "时间先后比较，因此 MAX(played_on) 可以直接取最近一场比赛日期。聚合结果是一行一列，不能"
                "和普通列随意混写：SELECT player, MAX(score) FROM matches 在 SQLite 里不会报错，但 player "
                "取的是哪一行并不确定，标准 SQL 会直接拒绝。正确做法是按 player 分组，或者用窗口函数"
                "把聚合值贴回每一行。这个坑在面试和真实项目里都非常常见。",

                "聚合和 WHERE 的配合也有顺序：WHERE 先把不满足条件的行去掉，聚合再对剩下的行计算。"
                "所以 WHERE 里写 COUNT(*) > 1 会报 misuse of aggregate，因为过滤发生在聚合之前，"
                "那时还没有聚合值。过滤聚合结果要用 HAVING，它在下一次课详细讲。空表上的行为也值得"
                "记牢：COUNT 返回 0，SUM、AVG、MIN、MAX 返回 NULL，报表代码要能处理这种空结果，"
                "而不是默认它一定返回数字。",

                "AVG 的口径尤其容易出错。假设三个玩家分数是 90、60、NULL，AVG(score) 得到 75，而如果"
                "把 NULL 当成 0 参与，平均分是 50，两种口径都可能有业务依据，但必须明确选一种并告知使用方。"
                "更隐蔽的是手工用 SUM 除以 COUNT(*)：分子跳过 NULL、分母包含全部行，算出来的平均值会偏低，"
                "这种错误在手工拼 SQL 的报表里非常常见。建议直接用 AVG，让数据库统一处理口径，"
                "需要特殊口径时再显式写 SUM(COALESCE(x, 0)) / COUNT(*)，并在注释里说明为什么这样算。",

                "聚合还能和 DISTINCT 组合，例如 COUNT(DISTINCT player) 统计去重玩家数，"
                "SUM(DISTINCT amount) 只对不重复金额求和。后者在业务上很少有意义，但语法合法，"
                "看到时要立刻意识到它的语义是「先去重再求和」。多列聚合可以写在同一行 SELECT 里，"
                "数据库只扫一遍数据就能算出所有指标，比分多条查询分别统计高效。做数据看板时，"
                "把同一张表的多个指标合并到一条查询，是降低数据库压力的常用手段。",

                "如果查询里同时出现 WHERE 和聚合，请按「先缩范围、再算指标」的思路组织。例如统计本周"
                "活跃玩家的平均分，应该先用 WHERE 限定日期区间，再 GROUP BY player 求 AVG，而不是"
                "先算全表平均再筛选。前者让数据库只处理一小部分行，后者白白计算了用不上的数据。"
                "这条原则在数据量变大后差别非常明显，也是慢查询优化最常调整的地方之一。养成先想"
                "「哪些行需要参与计算」的习惯，写出来的 SQL 通常既正确又高效。",
            ],
            "demo": "CREATE TABLE matches (\n  id INTEGER PRIMARY KEY,\n  player TEXT,\n  score INTEGER\n);\n"
                    "INSERT INTO matches VALUES\n  (1, 'V', 90),\n  (2, 'Judy', 80),\n"
                    "  (3, 'V', 70),\n  (4, 'Jackie', NULL),\n  (5, 'Judy', 60);\n\n"
                    "SELECT COUNT(*) AS matches,\n       COUNT(score) AS scored,\n"
                    "       SUM(score) AS total,\n       ROUND(AVG(score), 1) AS avg_score,\n"
                    "       MIN(score) AS low, MAX(score) AS high\nFROM matches;",
            "mid": table(
                ["函数", "作用", "对 NULL 的处理"],
                [
                    ["COUNT(*)", "统计行数", "包含 NULL 行"],
                    ["COUNT(列)", "统计非空值", "跳过 NULL"],
                    ["SUM(列)", "求和", "跳过 NULL，全空返回 NULL"],
                    ["AVG(列)", "求平均", "分母是非空行数"],
                    ["MIN / MAX", "极值", "跳过 NULL，可用于文本和日期"],
                ],
            ),
            "demo2": "CREATE TABLE empty_scores (player TEXT, score INTEGER);\n\n"
                     "SELECT COUNT(*) AS rows_count,\n       SUM(score) AS total,\n"
                     "       AVG(score) AS average,\n       MAX(score) AS best\nFROM empty_scores;",
            "tip": "AVG 返回浮点数，报表展示前用 ROUND(AVG(x), 1) 控制小数位。如果业务要求「四舍五入到整数」，"
                   "写 ROUND 而不是 CAST，CAST 是截断，会把 89.9 变成 89。",
            "warn": "聚合查询里混入非聚合列，在 SQLite 中不一定报错，但取值来自哪一行没有保证。"
                    "要么把该列放进 GROUP BY，要么改用窗口函数，不要依赖这种「碰巧对」的写法。",
            "quiz": (
                "表中有 5 行，其中 score 列有 2 行为 NULL，COUNT(score) 返回多少？",
                ["5", "3", "2", "NULL"],
                1,
                "COUNT(列) 只统计非 NULL 值，5 行里 2 行为空，所以返回 3。",
            ),
            "ex": exercise(
                "汇总比赛数据",
                "从 matches 表统计总场次 matches、有分数的场次 scored、总分 total 与平均分 avg_score"
                "（保留一位小数），列名依次为 matches、scored、total、avg_score。",
                "CREATE TABLE matches (id INTEGER PRIMARY KEY, player TEXT, score INTEGER);\n"
                "INSERT INTO matches VALUES\n  (1, 'V', 90),\n  (2, 'Judy', 80),\n"
                "  (3, 'V', 70),\n  (4, 'Jackie', NULL),\n  (5, 'Judy', 60);\n\n-- 在这里写查询\n",
                "SELECT COUNT(*) AS matches, COUNT(score) AS scored, SUM(score) AS total, "
                "ROUND(AVG(score), 1) AS avg_score FROM matches;",
                [
                    "assert columns == ['matches', 'scored', 'total', 'avg_score'], columns",
                    "assert rows == [[5, 4, 300, 75.0]], rows",
                    "assert len(rows) == 1, rows",
                ],
                "CREATE TABLE matches (id INTEGER PRIMARY KEY, player TEXT, score INTEGER);\n"
                "INSERT INTO matches VALUES\n  (1, 'V', 90),\n  (2, 'Judy', 80),\n"
                "  (3, 'V', 70),\n  (4, 'Jackie', NULL),\n  (5, 'Judy', 60);\n\n"
                "SELECT COUNT(*) AS matches,\n       COUNT(score) AS scored,\n"
                "       SUM(score) AS total,\n       ROUND(AVG(score), 1) AS avg_score\nFROM matches;\n",
                100,
            ),
        }),
        mk({
            "id": "sql08", "order": 507, "chapter": 51, "chapterName": BASICS,
            "title": "分组与筛选组", "subtitle": "GROUP BY 与 HAVING", "xp": 90,
            "head": "先分组，再统计",
            "paras": [
                "GROUP BY 把行按指定列的值分成若干组，每组内部的行共享同一个分组键，聚合函数对每组各算"
                "一次，最终每个组输出一行。SELECT player, COUNT(*) FROM matches GROUP BY player 得到"
                "每位玩家的比赛场次，而不是全表一个总数。分组键可以是一列，也可以是多个列的组合，"
                "例如按玩家和模式分组，就能得到「某人在某种模式下」的统计。分组键为 NULL 的行会自成"
                "一组，这一点在做用户画像时经常需要单独处理。",

                "SELECT 列表里的列有两种：分组键和聚合结果。任何没有包在聚合函数里的列，都应该出现在 "
                "GROUP BY 中，否则它的取值来自组内哪一行没有定义。SQLite 对此比较宽松，MySQL 旧版本甚至"
                "默认允许，但 PostgreSQL 会直接报错，标准 SQL 也要求如此。写代码时按最严格的标准要求自己，"
                "迁移数据库时才不会突然冒出一堆错误。如果确实需要组内某一行的其他列，正确工具是窗口函数"
                "或者「先排序再取第一行」的子查询，而不是赌数据库的实现细节。",

                "HAVING 用来过滤分组后的结果，语义上相当于对每组算完聚合后再判断一次。WHERE 过滤的是行，"
                "HAVING 过滤的是组，两者的执行顺序是 FROM、WHERE、GROUP BY、HAVING、SELECT、ORDER BY。"
                "所以 WHERE 里不能写聚合函数，HAVING 里可以。一个常见的组合是 WHERE 先限定时间范围，"
                "GROUP BY 再按玩家分组，HAVING 最后只保留场次达到阈值的组，这样能显著减少参与聚合的数据量。",

                "写分组查询时建议按固定模板组织：先确定「每组的定义」，再确定「每组要算什么」，最后确定"
                "「哪些组不要」。缺了最后一步，报表里常会出现只打过一场的玩家或金额极小的噪声分组。"
                "HAVING 的条件里可以直接引用 SELECT 中定义的聚合别名，SQLite 和 MySQL 都支持，PostgreSQL "
                "不支持，跨库代码最好重复写一遍聚合表达式。结果默认无序，需要稳定输出时补 ORDER BY，"
                "并且排序键最好包含分组键，避免同值组的顺序漂移。",

                "还有一个进阶技巧：GROUP BY 支持按表达式分组，例如按 SUBSTR(played_on, 1, 7) 分组成"
                "「年月」，就能做出月度报表；按 CASE WHEN 的结果分组，可以把分数分成 S、A、B 档再统计"
                "各档人数。分组键不要求是原始列，只要表达式在每一行上有确定值即可。不过表达式分组通常"
                "无法命中普通索引，数据量大时要考虑增加生成列或预计算字段。更重要的是，分组键一旦变化，"
                "结果行的含义就变了，所以改动分组逻辑时要同步更新报表口径文档。",

                "分组查询的调试方法也值得单独说：先用 SELECT player, COUNT(*) 看每组行数，确认没有意外的"
                "空组或重复；再加上 HAVING 观察被过滤掉的组；最后加 ORDER BY 检查排序是否符合预期。"
                "分步验证比一次性写完再看结果更容易定位问题。如果发现某位玩家的场次比实际多，八成是"
                "连接了另一张一对多的表导致行数被放大，这时要先把连接后的行数数清楚，再决定是否在聚合前"
                "去重。分组的本质是「先把行归堆」，堆分错了，后面算得再准也没有意义。",

                "最后提一个常见需求：统计「每个分组里满足某条件的行数」。写 SUM(CASE WHEN score >= 90 THEN 1 ELSE 0 END) 即可，也可以写 COUNT(CASE WHEN ... THEN 1 END)，两者结果相同。这类条件聚合能在一行里同时产出多个口径，是做转化率、留存率报表的核心手法。记得给每个聚合起清楚的别名，否则结果列会变成一长串表达式，交给前端或报表工具时没人看得懂。",
            ],
            "demo": "CREATE TABLE matches (\n  id INTEGER PRIMARY KEY,\n  player TEXT,\n  score INTEGER\n);\n"
                    "INSERT INTO matches VALUES\n  (1, 'V', 90),\n  (2, 'Judy', 80),\n  (3, 'V', 70),\n"
                    "  (4, 'Jackie', 60),\n  (5, 'Judy', 95);\n\n"
                    "SELECT player,\n       COUNT(*) AS games,\n       ROUND(AVG(score), 1) AS avg_score\n"
                    "FROM matches\nGROUP BY player\nORDER BY avg_score DESC;",
            "mid": table(
                ["子句", "作用对象", "执行时机"],
                [
                    ["WHERE", "单行", "分组之前"],
                    ["GROUP BY", "行到组", "过滤之后"],
                    ["HAVING", "分组结果", "聚合之后"],
                    ["ORDER BY", "最终结果", "最后排序"],
                ],
            ),
            "demo2": "CREATE TABLE matches (\n  id INTEGER PRIMARY KEY,\n  player TEXT,\n  score INTEGER\n);\n"
                     "INSERT INTO matches VALUES\n  (1, 'V', 90),\n  (2, 'Judy', 80),\n  (3, 'V', 70),\n"
                     "  (4, 'Jackie', 60),\n  (5, 'Judy', 95);\n\n"
                     "SELECT player, COUNT(*) AS games\nFROM matches\nGROUP BY player\n"
                     "HAVING COUNT(*) >= 2\nORDER BY games DESC, player;",
            "tip": "分组查询的结果行数等于分组数，不是原表行数。写之前先想清楚「一行的粒度是什么」，"
                   "是每位玩家、每天、还是每个玩家每天，粒度决定 GROUP BY 的列。",
            "warn": "WHERE 里写 COUNT(*) > 1 会报 misuse of aggregate。过滤聚合结果必须用 HAVING，"
                    "因为 WHERE 执行时还没有聚合值。",
            "quiz": (
                "要只保留比赛场次大于等于 2 的玩家，条件应该写在哪里？",
                ["WHERE COUNT(*) >= 2", "HAVING COUNT(*) >= 2", "ORDER BY COUNT(*) >= 2", "GROUP BY COUNT(*) >= 2"],
                1,
                "过滤分组后的聚合结果用 HAVING；WHERE 在聚合之前执行，不能引用聚合函数。",
            ),
            "ex": exercise(
                "活跃玩家",
                "从 matches 表按 player 分组，统计每人的场次 games 与平均分 avg_score（保留一位小数），"
                "只保留场次大于等于 2 的玩家，按 avg_score 降序。",
                "CREATE TABLE matches (id INTEGER PRIMARY KEY, player TEXT, score INTEGER);\n"
                "INSERT INTO matches VALUES\n  (1, 'V', 90),\n  (2, 'Judy', 80),\n  (3, 'V', 70),\n"
                "  (4, 'Jackie', 60),\n  (5, 'Judy', 95);\n\n-- 在这里写查询\n",
                "SELECT player, COUNT(*) AS games, ROUND(AVG(score), 1) AS avg_score FROM matches "
                "GROUP BY player HAVING COUNT(*) >= 2 ORDER BY avg_score DESC;",
                [
                    "assert columns == ['player', 'games', 'avg_score'], columns",
                    "assert rows == [['Judy', 2, 87.5], ['V', 2, 80.0]], rows",
                    "assert len(rows) == 2, rows",
                ],
                "CREATE TABLE matches (id INTEGER PRIMARY KEY, player TEXT, score INTEGER);\n"
                "INSERT INTO matches VALUES\n  (1, 'V', 90),\n  (2, 'Judy', 80),\n  (3, 'V', 70),\n"
                "  (4, 'Jackie', 60),\n  (5, 'Judy', 95);\n\n"
                "SELECT player,\n       COUNT(*) AS games,\n       ROUND(AVG(score), 1) AS avg_score\n"
                "FROM matches\nGROUP BY player\nHAVING COUNT(*) >= 2\nORDER BY avg_score DESC;\n",
                110,
            ),
        }),
        mk({
            "id": "sql09", "order": 508, "chapter": 51, "chapterName": BASICS,
            "title": "增删改数据", "subtitle": "INSERT / UPDATE / DELETE", "xp": 90,
            "head": "让数据发生变化",
            "paras": [
                "INSERT 负责新增行，最完整的写法是 INSERT INTO 表名 (列一, 列二) VALUES (值一, 值二)。"
                "列名列表可以省略，此时必须按建表时的列顺序提供全部列的值，一旦表结构变了，这种写法就会"
                "悄悄错位，所以生产代码建议总是写列名。一次插入多行用逗号分隔多组 VALUES，比循环执行多条"
                "INSERT 快得多，因为只需要一次解析、一次事务开销。配合 SELECT 还能把查询结果直接写入另一张表，"
                "这在数据归档和汇总表刷新时非常常用。",

                "UPDATE 修改已有行，语法是 UPDATE 表名 SET 列 = 新值 WHERE 条件。SET 后面可以同时写多列，"
                "用逗号分隔，所有列基于修改前的同一行计算；也可以用表达式更新，例如把分数整体上调百分之十。"
                "WHERE 是 UPDATE 的灵魂：漏写 WHERE 会更新全表，这是生产事故里最常见的一类。执行前先用"
                "同样的 WHERE 写一条 SELECT COUNT(*) 数一下会命中多少行，确认数量和预期一致再改成 UPDATE，"
                "这个习惯能挡掉绝大部分误操作。",

                "DELETE 删除行，语法是 DELETE FROM 表名 WHERE 条件，同样必须带条件。SQLite 没有 TRUNCATE，"
                "清空表就是 DELETE FROM 表名，它会逐行删除并写日志，大表上比 TRUNCATE 慢。删除前最好先"
                "备份或把数据复制到归档表，尤其是没有 WHERE 的删除。逻辑删除是常见替代方案：加一列 "
                "deleted_at，删除时写时间戳而不是真的删行，查询时过滤掉已删除记录，这样数据可恢复，"
                "也方便审计。物理删除与逻辑删除怎么选，取决于业务对可恢复性和存储成本的要求。",

                "这三类语句和查询有一个本质区别：它们改变数据库状态，而 SELECT 只读。执行之后，可以用"
                "SELECT 立刻验证结果是否符合预期，例如更新后查一下目标行的新值、删除后统计剩余行数。"
                "多条写操作如果必须一起成功，就要用事务包起来，这一部分在进阶篇展开。还要注意，写操作的"
                "返回值是受影响的行数，Python 的 sqlite3 通过 cursor.rowcount 拿到它，课程运行器会把它"
                "显示成 OK (n rows affected)，n 为 -1 表示该语句不返回行数，例如建表语句。",

                "INSERT 还有一个实用变体是 INSERT INTO ... SELECT，把一条查询的结果整批写入目标表，"
                "例如每晚把当天的订单汇总进日报表。它和普通 INSERT 一样受约束检查，违反唯一键会整批失败，"
                "批量导入前最好先确认源数据没有重复键。另一个常见需求是「不存在才插入」，可以用 "
                "INSERT OR IGNORE 配合唯一索引，或者写成 INSERT ... SELECT ... WHERE NOT EXISTS，"
                "后者的语义更明确，也方便在插入前做更复杂的判断。",

                "UPDATE 里还有一个容易忽略的点：SET 右侧的表达式如果引用本列，用的是修改前的值。"
                "所以 UPDATE t SET a = a + 1, b = a 中的 b 拿到的是旧的 a，而不是刚加完 1 的新值。"
                "需要基于新值继续计算时，要么拆成两条语句，要么在表达式里重复写完整公式。理解这一点，"
                "能避免很多「为什么更新后数据不对」的疑惑。至于 DELETE，执行前先确认是否有外键级联，"
                "删掉父表一行可能连带清空子表大量数据，这一类影响面必须在动手前查清楚。",

                "写入还有一个常被忽略的细节：UPDATE 和 DELETE 的 WHERE 条件如果涉及子查询，SQLite 会先算出子查询的结果集再逐行匹配，中途修改数据不会影响已经算好的集合。这意味着你可以安全地写 DELETE FROM t WHERE id IN (SELECT id FROM t WHERE ...)，不必担心边删边算导致漏行。但跨表删除时仍要确认外键级联的顺序，先删子表再删父表，或依赖级联，别指望数据库替你猜意图。",
            ],
            "demo": PLAYERS + PLAYERS_DATA
                    + "\nINSERT INTO players (name, region, level) VALUES ('Echo', 'Neon', 20);\n"
                    "UPDATE players SET level = level + 10 WHERE region = 'Neon';\n"
                    "SELECT name, region, level FROM players ORDER BY id;",
            "mid": table(
                ["语句", "作用", "关键点"],
                [
                    ["INSERT", "新增行", "写列名，多行用逗号分隔"],
                    ["UPDATE", "修改行", "必须带 WHERE，否则全表"],
                    ["DELETE", "删除行", "必须带 WHERE，先备份"],
                    ["SELECT", "只读验证", "写操作后立刻核对"],
                ],
            ),
            "demo2": PLAYERS + PLAYERS_DATA
                     + "\nDELETE FROM players WHERE level < 30;\n"
                     "SELECT COUNT(*) AS remaining FROM players;",
            "tip": "把 UPDATE 或 DELETE 的 WHERE 条件先放进 SELECT COUNT(*)，确认命中行数再执行，"
                   "是成本最低的安全检查。多花十秒，能避免一次通宵恢复数据。",
            "warn": "SQLite 默认自动提交：每条写语句执行完就生效。想「要么全成功要么全失败」，"
                    "必须显式写 BEGIN 与 COMMIT，把多条语句包进同一个事务。",
            "quiz": (
                "UPDATE players SET level = 10; 缺少 WHERE 会发生什么？",
                ["只更新第一行", "更新所有行", "报语法错误", "什么都不做"],
                1,
                "没有 WHERE 时 UPDATE 作用于整张表，所有行的 level 都会被改成 10。",
            ),
            "ex": exercise(
                "注册并升级",
                "向 players 表插入 name 为 'Echo'、region 为 'Neon'、level 为 20 的玩家，"
                "再把 Echo 的 level 改为 25，最后返回 name 与 level。",
                PLAYERS + PLAYERS_DATA + "\n-- 在这里写 INSERT / UPDATE / SELECT\n",
                "INSERT INTO players (name, region, level) VALUES ('Echo', 'Neon', 20); "
                "UPDATE players SET level = 25 WHERE name = 'Echo'; SELECT name, level FROM players WHERE name = 'Echo';",
                [
                    "assert columns == ['name', 'level'], columns",
                    "assert rows == [['Echo', 25]], rows",
                    "assert len(rows) == 1, rows",
                ],
                PLAYERS + PLAYERS_DATA
                + "\nINSERT INTO players (name, region, level) VALUES ('Echo', 'Neon', 20);\n"
                "UPDATE players SET level = 25 WHERE name = 'Echo';\n"
                "SELECT name, level FROM players WHERE name = 'Echo';\n",
                110,
            ),
        }),
        mk({
            "id": "sql10", "order": 509, "chapter": 51, "chapterName": BASICS,
            "title": "把规则写进表里", "subtitle": "主键与约束", "xp": 100,
            "head": "约束是数据库替你守的底线",
            "paras": [
                "主键 PRIMARY KEY 唯一标识一行，它有两个硬性要求：全表不重复、不能为 NULL。声明在 "
                "INTEGER 列上时，SQLite 会把这一列当作 rowid 的别名，插入 NULL 或省略该列会自动分配一个"
                "递增的整数，所以玩家 id 可以不用手写。复合主键用 PRIMARY KEY (列一, 列二) 声明，"
                "表示这两列的组合唯一，常见于关联表，例如「玩家 + 成就」的领取记录。主键不仅是约束，"
                "也是索引，按主键查找是数据库最快的访问路径之一。",

                "除了主键，还有几类常用约束。NOT NULL 要求列必须有值，防止写入方漏填；UNIQUE 保证列值"
                "不重复，可以为 NULL（多个 NULL 不算重复）；DEFAULT 指定省略该列时的默认值，例如等级默认 1、"
                "创建时间默认当前时间；CHECK 写一个布尔表达式，插入或更新时校验，例如 CHECK (level >= 0) "
                "拦住负数等级。约束在写入的那一刻生效，违反就报错并拒绝整条语句，不需要应用层再写一遍"
                "判断逻辑，也不会因为某个写入入口忘了校验而留下脏数据。",

                "约束冲突时可以指定应对策略：INSERT OR IGNORE 遇到唯一冲突就跳过这一行，适合批量导入时"
                "容忍重复；INSERT OR REPLACE 先删掉冲突的旧行再插入新行，语义是覆盖；INSERT OR ABORT 是"
                "默认行为，直接报错并回滚该语句。UPDATE 也有 OR 子句，用法类似。要注意 OR REPLACE 会"
                "真正删除旧行，如果其他表有外键引用它，可能触发级联删除，用之前要确认影响面。约束命名"
                "（CONSTRAINT 名字 CHECK ...）能让报错信息更可读，排查问题时能直接定位是哪条规则被违反。",

                "设计表时的一个实用原则是：能在数据库层表达的规则，就不要只写在应用层。应用可能有多个"
                "写入入口，脚本、后台、运营工具都会改数据，只有数据库约束是所有入口共享的最后一道防线。"
                "但约束也不是越多越好：每加一个 UNIQUE 就多一个索引，写入会变慢；CHECK 里的复杂子查询"
                "SQLite 并不支持。把「绝对不能错」的规则放进约束，把「业务流程」的校验留在应用层，"
                "两者分工明确，系统才好维护。建表时多花十分钟想清楚约束，能省掉后面几个月的脏数据清理。",

                "主键的选型也值得认真对待。用自增整数做主键最简单，索引小、插入快、比较高效；用业务字段"
                "做主键则要求它永不变化，例如身份证号、订单号，一旦业务规则调整就会牵动大量关联表。"
                "更稳妥的做法是内部用自增整数做主键，业务唯一键另加 UNIQUE 索引，两者分工。另外，"
                "复合主键适合纯关联表，但如果关联表本身还要被别的表引用，加一个独立 id 会更方便。"
                "选主键没有唯一正确答案，关键是让读写双方都清楚「这一列代表什么、能不能变」。",

                "最后用一句话总结这一讲：约束不是限制，而是契约。它把「数据必须满足什么」从口头约定变成"
                "数据库可执行的规则，让错误在写入的那一刻暴露，而不是在几个月后的报表里才被发现。"
                "练习时不妨故意违反一次 UNIQUE 和 CHECK，看看报错信息长什么样，再想想如果应用层忘了"
                "校验会有什么后果。亲手触发过约束，你对它的信任和使用就会自然很多。",
            ],
            "demo": "CREATE TABLE accounts (\n  id INTEGER PRIMARY KEY,\n  name TEXT NOT NULL UNIQUE,\n"
                    "  level INTEGER NOT NULL DEFAULT 1 CHECK (level >= 0),\n"
                    "  active INTEGER NOT NULL DEFAULT 1\n);\n"
                    "INSERT INTO accounts (name) VALUES ('V');\n"
                    "INSERT INTO accounts (name, level) VALUES ('Judy', 42);\n"
                    "INSERT OR IGNORE INTO accounts (name) VALUES ('V');\n"
                    "SELECT id, name, level, active FROM accounts ORDER BY id;",
            "mid": table(
                ["约束", "作用", "示例"],
                [
                    ["PRIMARY KEY", "唯一且非空", "id INTEGER PRIMARY KEY"],
                    ["NOT NULL", "禁止空值", "name TEXT NOT NULL"],
                    ["UNIQUE", "列值不重复", "name TEXT UNIQUE"],
                    ["DEFAULT", "省略时填默认值", "level INTEGER DEFAULT 1"],
                    ["CHECK", "写入时校验表达式", "CHECK (level >= 0)"],
                ],
            ),
            "demo2": "CREATE TABLE accounts (\n  id INTEGER PRIMARY KEY,\n  name TEXT NOT NULL UNIQUE,\n"
                     "  level INTEGER NOT NULL DEFAULT 1 CHECK (level >= 0)\n);\n"
                     "INSERT INTO accounts (name) VALUES ('V'), ('Judy');\n"
                     "UPDATE accounts SET level = level + 5 WHERE name = 'Judy';\n"
                     "SELECT name, level FROM accounts ORDER BY level DESC;",
            "tip": "INTEGER PRIMARY KEY 取当前最大 rowid 加一，删除末尾行后这个编号可能被再次分配。"
                   "要求编号永不复用时再写 AUTOINCREMENT，它会多维护一张内部表，有额外开销。",
            "warn": "UNIQUE 允许多个 NULL，因为 NULL 表示未知，两个未知不算相等。"
                    "如果业务要求「这一列必须唯一且不能为空」，要同时写 NOT NULL 和 UNIQUE。",
            "quiz": (
                "name TEXT UNIQUE 能否插入两条 name 为 NULL 的记录？",
                ["不能，UNIQUE 禁止 NULL", "可以，多个 NULL 不算重复", "只能插入一条", "取决于主键类型"],
                1,
                "UNIQUE 只约束非 NULL 值之间的唯一性，多个 NULL 被视为互不相等，可以共存。",
            ),
            "ex": exercise(
                "建立会员表",
                "创建 members 表：id 为 INTEGER PRIMARY KEY，name 为 TEXT NOT NULL UNIQUE，"
                "level 为 INTEGER NOT NULL DEFAULT 1 且 CHECK (level >= 0)。插入 name 为 'Rogue' 的会员"
                "（level 用默认值），再把它升级到 25，最后返回 name 与 level。",
                "CREATE TABLE members (\n  id INTEGER PRIMARY KEY,\n  name TEXT NOT NULL UNIQUE,\n"
                "  level INTEGER NOT NULL DEFAULT 1 CHECK (level >= 0)\n);\n\n-- 在这里写 INSERT / UPDATE / SELECT\n",
                "INSERT INTO members (name) VALUES ('Rogue'); UPDATE members SET level = 25 WHERE name = 'Rogue'; "
                "SELECT name, level FROM members;",
                [
                    "assert columns == ['name', 'level'], columns",
                    "assert rows == [['Rogue', 25]], rows",
                    "assert len(rows) == 1, rows",
                ],
                "CREATE TABLE members (\n  id INTEGER PRIMARY KEY,\n  name TEXT NOT NULL UNIQUE,\n"
                "  level INTEGER NOT NULL DEFAULT 1 CHECK (level >= 0)\n);\n\n"
                "INSERT INTO members (name) VALUES ('Rogue');\n"
                "UPDATE members SET level = 25 WHERE name = 'Rogue';\n"
                "SELECT name, level FROM members;\n",
                120,
            ),
        }),
    ]


def core_11_15():
    return [
        mk({
            "id": "sql11", "order": 510, "chapter": 52, "chapterName": CORE,
            "title": "两表配对", "subtitle": "INNER JOIN", "xp": 80,
            "head": "把两张表按关系拼起来",
            "paras": [
                "关系数据库的「关系」体现在表与表之间的关联上：玩家表存玩家信息，订单表存交易记录，"
                "订单通过 player_id 指向玩家。查询「谁买了什么」时，需要把两张表按这个外键拼在一起，"
                "这个动作就是 JOIN。INNER JOIN 是最常用的连接方式，它只保留两边都能匹配上的行："
                "玩家没有订单就不会出现，订单指向不存在的玩家也不会出现。写法和逗号连接不同，JOIN 让"
                "连接条件显式可见，是现代 SQL 的标准写法。",

                "连接语法是 FROM 表一 JOIN 表二 ON 条件。ON 后面写两表的配对规则，最常见的是 "
                "表二.外键 = 表一.主键，例如 ON o.player_id = p.id。ON 只负责配对，WHERE 负责过滤"
                "配对后的行，两者职责不同，虽然把条件写进 WHERE 有时结果一样，但语义上不要混用。"
                "连接时必须给表起短别名（p、o），并在所有列前加前缀，否则两张表有同名列（例如都有 id）"
                "时，SQLite 会报 ambiguous column name，或者悄悄取错列而不自知。",

                "JOIN 的执行顺序是逻辑上的：先按 ON 条件把两表的行两两配对，得到一张临时结果集，"
                "再用 WHERE 过滤、GROUP BY 分组、ORDER BY 排序。理解这一点非常重要：如果一对多关系下"
                "忘了聚合，结果行数会比左表多，金额会被重复计算。例如一个玩家有三笔订单，连接后他会"
                "出现三行，此时 SUM(o.amount) 才是他真正的总额，但如果同时连接另一张一对多的表，"
                "两张子表会互相放大行数，金额可能翻倍。遇到「合计对不上」的问题，先数连接后的行数。",

                "内连接还有一个容易被忽视的细节：NULL 不参与匹配。如果订单的 player_id 是 NULL，"
                "ON 条件 o.player_id = p.id 的结果是未知，这一行会被丢弃。所以「找出没有归属的订单」"
                "这类数据质量检查，不能靠 INNER JOIN，要用 LEFT JOIN 加 IS NULL，或者单独查 "
                "WHERE player_id IS NULL。把这些边界记牢，连接结果才可信，后续做统计时才不会莫名其妙"
                "少掉几行。",

                "还有一种自连接（SELF JOIN）值得了解：同一张表起两个别名互相连接，用来比较表内的行。"
                "例如找出与某位玩家同地区的其他人，可以写 FROM players a JOIN players b ON "
                "a.region = b.region AND a.id <> b.id。自连接本质上还是内连接，只是左右两边是同一张表，"
                "别名不可省略。它适合层级关系（员工与上级）和同伴比较这类场景，但写的时候要特别小心"
                "连接条件，漏掉 a.id <> b.id 会让每一行和自己配对，结果里出现大量无意义的自匹配。",

                "初学者还容易混淆「连接」和「并集」。连接是横向拼接列，把两张表的字段并到同一行；"
                "UNION 是纵向拼接行，把两张表结构相同的结果叠在一起。前者按 ON 条件配对，行数可能"
                "增加也可能减少；后者按列对齐，行数等于两边之和再去重。把这两个概念分清，遇到"
                "「要横向还是纵向」的需求时，就不会在 JOIN 和 UNION 之间犹豫。判断方法很简单："
                "需要更多列用 JOIN，需要更多行用 UNION。",

                "关于连接的最后一个提醒：on 条件里的列最好都有索引，尤其是被连接的大表。SQLite 里"
                "INTEGER PRIMARY KEY 自带索引，其他外键列需要显式建。没有索引时，数据库可能对每一行"
                "都做一次全表扫描，行数一多就会明显变慢。可以用 EXPLAIN QUERY PLAN 查看执行计划，"
                "出现 SCAN 就说明在扫全表。不过也不要盲目加索引，写入频繁的表索引越多越慢，"
                "先确认慢查询真的由连接引起，再针对性地加。",
            ],
            "demo": "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT, region TEXT);\n"
                    "CREATE TABLE orders (id INTEGER PRIMARY KEY, player_id INTEGER, amount INTEGER);\n"
                    "INSERT INTO players VALUES (1, 'V', 'Neon'), (2, 'Judy', 'Neon'), (3, 'Jackie', 'Watson');\n"
                    "INSERT INTO orders VALUES (1, 1, 100), (2, 1, 50), (3, 2, 80);\n\n"
                    "SELECT p.name, o.amount\nFROM players p\nJOIN orders o ON o.player_id = p.id\nORDER BY o.id;",
            "mid": table(
                ["写法", "保留哪些行", "典型用途"],
                [
                    ["INNER JOIN", "两边都匹配", "查有订单的玩家"],
                    ["LEFT JOIN", "左表全部 + 匹配的右表", "查所有玩家含无订单"],
                    ["CROSS JOIN", "两表笛卡尔积", "生成组合矩阵"],
                    ["ON", "配对规则", "o.player_id = p.id"],
                ],
            ),
            "demo2": "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT, region TEXT);\n"
                     "CREATE TABLE orders (id INTEGER PRIMARY KEY, player_id INTEGER, amount INTEGER);\n"
                     "INSERT INTO players VALUES (1, 'V', 'Neon'), (2, 'Judy', 'Neon'), (3, 'Jackie', 'Watson');\n"
                     "INSERT INTO orders VALUES (1, 1, 100), (2, 1, 50), (3, 2, 80);\n\n"
                     "SELECT p.name, COUNT(o.id) AS orders, COALESCE(SUM(o.amount), 0) AS total\n"
                     "FROM players p\nJOIN orders o ON o.player_id = p.id\nGROUP BY p.id\nORDER BY total DESC;",
            "tip": "连接条件的列类型最好一致，并且两边都建索引。SQLite 只有 INTEGER PRIMARY KEY 天然有索引，"
                   "订单表的 player_id 建议手动 CREATE INDEX，否则连接时可能退化成嵌套扫描。",
            "warn": "JOIN 后接 GROUP BY 时，如果被连接的表是一对多，SUM 会按连接后的行数累加。"
                    "如果还连接了第二张一对多表，两边的行会相乘，金额成倍放大，这是报表口径出错的高发区。",
            "quiz": (
                "players 有 3 人，orders 有 2 条分别属于其中 2 人，INNER JOIN 后返回几行？",
                ["3 行", "2 行", "6 行", "5 行"],
                1,
                "INNER JOIN 只保留两边都匹配的行，没有订单的那位玩家不会出现，结果是 2 行。",
            ),
            "ex": exercise(
                "玩家订单明细",
                "用 JOIN 连接 players 与 orders，输出玩家 name 与订单 amount，按订单 id 升序。",
                "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT);\n"
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, player_id INTEGER, amount INTEGER);\n"
                "INSERT INTO players VALUES (1, 'V'), (2, 'Judy'), (3, 'Jackie');\n"
                "INSERT INTO orders VALUES (1, 1, 100), (2, 1, 50), (3, 2, 80);\n\n-- 在这里写查询\n",
                "SELECT p.name, o.amount FROM players p JOIN orders o ON o.player_id = p.id ORDER BY o.id;",
                [
                    "assert columns == ['name', 'amount'], columns",
                    "assert rows == [['V', 100], ['V', 50], ['Judy', 80]], rows",
                    "assert len(rows) == 3, rows",
                ],
                "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT);\n"
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, player_id INTEGER, amount INTEGER);\n"
                "INSERT INTO players VALUES (1, 'V'), (2, 'Judy'), (3, 'Jackie');\n"
                "INSERT INTO orders VALUES (1, 1, 100), (2, 1, 50), (3, 2, 80);\n\n"
                "SELECT p.name, o.amount\nFROM players p\nJOIN orders o ON o.player_id = p.id\nORDER BY o.id;\n",
                100,
            ),
        }),
        mk({
            "id": "sql12", "order": 511, "chapter": 52, "chapterName": CORE,
            "title": "保留没匹配的行", "subtitle": "LEFT JOIN 与 RIGHT JOIN", "xp": 90,
            "head": "外连接解决「没有」的问题",
            "paras": [
                "INNER JOIN 会丢掉没有匹配的行，但很多业务问题恰恰要问「谁没有」。例如列出所有玩家"
                "及其消费总额，没有下过单的人也要显示为 0。LEFT JOIN 保留左表全部行，右表没有匹配时"
                "用 NULL 填充，配合 COALESCE(SUM(o.amount), 0) 就能把空值变成零。判断某个玩家有没有"
                "订单，也可以看连接后右表主键是否为 NULL，例如 WHERE o.id IS NULL，这比 NOT IN 更"
                "不容易踩空值陷阱。",

                "LEFT JOIN 和 INNER JOIN 的区别只在「不匹配的行怎么处理」，匹配上的行完全一样。所以"
                "把 INNER JOIN 改成 LEFT JOIN 通常不会让结果变少，只会变多。反过来，如果一个 LEFT JOIN "
                "的查询结果和 INNER JOIN 一样，说明右表在连接键上必然有匹配，这时要么是数据恰好完整，"
                "要么是 WHERE 里对右表列加了条件，把 NULL 行又过滤掉了。后一种情况是经典 bug：条件写"
                "在 WHERE 里会退化成内连接，必须挪到 ON 里才能保留左表全部行。",

                "RIGHT JOIN 是 LEFT JOIN 的镜像，保留右表全部行。SQLite 从 3.39 开始支持 RIGHT JOIN，"
                "早期版本不支持，需要用交换表顺序的 LEFT JOIN 来模拟。实际项目里 RIGHT JOIN 用得很少，"
                "因为把两张表换个位置写 LEFT JOIN 更直观，可读性也更好。建议统一约定：需要保留哪张表，"
                "就把哪张表放左边用 LEFT JOIN，团队里不用为方向争论，代码审查也更快。",

                "外连接还有个实用技巧：用 LEFT JOIN 做「差集」。找出从未下单的玩家，写 "
                "SELECT p.name FROM players p LEFT JOIN orders o ON o.player_id = p.id WHERE o.id IS NULL。"
                "它的语义清晰，性能通常也不错，而且不像 NOT IN 那样在子查询返回 NULL 时整体失效。"
                "如果连接键可能为 NULL，ON 条件里的等值比较不会匹配，这些行在 LEFT JOIN 里会保留下来，"
                "正好符合「没有归属」的定义。",

                "外连接还有一个容易忽略的细节：ON 条件可以不只是等值比较，也可以写范围条件或复合条件。"
                "例如把订单按金额区间关联到折扣档位，ON o.amount BETWEEN d.lo AND d.hi，这种非等值连接"
                "在 INNER JOIN 和 LEFT JOIN 里都成立，只是无法用普通索引加速，数据量大时要谨慎。"
                "如果 ON 里需要多条件，用 AND 连接，别用逗号；逗号写在 FROM 后面是隐式的交叉连接，"
                "和 JOIN 混用会让优先级难以判断，现代 SQL 里应完全避免。",

                "最后说一个判断连接方向的实用方法：先问「哪张表的行必须全部保留」，答案是哪张，"
                "哪张就放左边用 LEFT JOIN。如果两张都要保留，标准 SQL 的 FULL OUTER JOIN 可以做到，"
                "但 SQLite 不支持，需要用 LEFT JOIN 加 UNION 模拟。多数业务问题其实只需要单向保留，"
                "把方向想清楚，比记住语法更重要。连接写完后用 COUNT(*) 分别核对左表行数与结果行数，"
                "是验证外连接是否按预期保留行的最快方式。",

                "另外，连接列的类型一致性会直接影响索引使用。如果 players.id 是 INTEGER，而 "
                "orders.player_id 声明成 TEXT，SQLite 在比较时会做隐式转换，可能无法使用索引，"
                "大数据量下从毫秒级退化到秒级。建表时把外键列的类型写成与主键完全一致，"
                "是几乎零成本却常被忽略的优化。用 EXPLAIN QUERY PLAN 可以看到是否走了索引，"
                "看到 SCAN 就要警惕，看到 SEARCH ... USING INDEX 才说明命中了索引。",

                "关于 ON 与 WHERE 的取舍，可以用一句话记住：ON 决定「怎么配对」，WHERE 决定"
                "「配对后留哪些」。在 INNER JOIN 里两者可以互换，因为不匹配的行本来就要丢弃；"
                "在 OUTER JOIN 里则绝不能互换，条件写在 WHERE 会把补出来的 NULL 行筛掉。"
                "团队约定所有连接条件统一写在 ON 里，过滤条件统一写在 WHERE 里，代码审查时"
                "一眼就能看出意图，也不会因为换连接类型而悄悄改变语义。",

                "关于连接的性能，先建立两个直觉：小表连大表时，通常让小表做驱动表；连接列上有索引时，"
                "数据库可以只扫描匹配的行，而不是全表嵌套。SQLite 的优化器会根据统计信息自动选择顺序，"
                "但统计信息可能过时，必要时用 ANALYZE 更新。实际排查时打开 EXPLAIN QUERY PLAN，"
                "看到 SEARCH 说明用到了索引，看到 SCAN 说明在扫全表，再结合行数判断是否可接受。"
                "不要凭直觉给每条连接加索引，写多读少的表加了反而拖慢写入。",

                "另外别把「连接」和「子查询」对立起来看。同一条需求往往有三种写法：JOIN、IN、EXISTS。"
                "JOIN 会把右表字段带出来，适合需要展示明细的场景；IN 与 EXISTS 只做存在判断，"
                "不改变外层行数，适合筛选。选择时先看输出需要哪些列，再看是否需要保留未匹配行，"
                "最后才考虑性能。很多初学者一上来就纠结哪种更快，其实语义都没对齐，跑得再快也是"
                "错的。把需求翻译成「保留谁、带出什么、怎么配对」三句话，答案自然就出来了。",
            ],
            "demo": "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT);\n"
                    "CREATE TABLE orders (id INTEGER PRIMARY KEY, player_id INTEGER, amount INTEGER);\n"
                    "INSERT INTO players VALUES (1, 'V'), (2, 'Judy'), (3, 'Jackie');\n"
                    "INSERT INTO orders VALUES (1, 1, 100), (2, 2, 80);\n\n"
                    "SELECT p.name, COALESCE(SUM(o.amount), 0) AS total\nFROM players p\n"
                    "LEFT JOIN orders o ON o.player_id = p.id\nGROUP BY p.id\nORDER BY p.id;",
            "mid": table(
                ["连接", "左表不匹配", "右表不匹配"],
                [
                    ["INNER JOIN", "丢弃", "丢弃"],
                    ["LEFT JOIN", "保留，右表补 NULL", "丢弃"],
                    ["RIGHT JOIN", "丢弃", "保留，左表补 NULL"],
                    ["FULL JOIN", "保留", "保留（SQLite 不支持）"],
                ],
            ),
            "demo2": "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT);\n"
                     "CREATE TABLE orders (id INTEGER PRIMARY KEY, player_id INTEGER, amount INTEGER);\n"
                     "INSERT INTO players VALUES (1, 'V'), (2, 'Judy');\n"
                     "INSERT INTO orders VALUES (1, 1, 100), (2, 2, 80), (3, 9, 70);\n\n"
                     "SELECT o.id, p.name, o.amount\nFROM players p\nRIGHT JOIN orders o ON o.player_id = p.id\n"
                     "ORDER BY o.id;",
            "tip": "LEFT JOIN 后用 COUNT(o.id) 而不是 COUNT(*)，才能正确统计「匹配到的右表行数」。"
                   "COUNT(*) 会把补 NULL 的那一行也算进去，没有订单的玩家会显示 1。",
            "warn": "把右表的过滤条件写在 WHERE 里，会让 LEFT JOIN 退化为 INNER JOIN。"
                    "要保留左表全部行，条件必须写在 ON 子句里。",
            "quiz": (
                "LEFT JOIN 后统计每位玩家的订单数，应该用哪个写法？",
                ["COUNT(*)", "COUNT(o.id)", "COUNT(p.id)", "SUM(o.id)"],
                1,
                "COUNT(o.id) 只数右表非 NULL 的主键，没有订单的玩家得到 0，而 COUNT(*) 会算成 1。",
            ),
            "ex": exercise(
                "所有人的消费额",
                "用 LEFT JOIN 列出所有玩家的 name 与消费总额 total（没有订单记 0），按玩家 id 升序。",
                "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT);\n"
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, player_id INTEGER, amount INTEGER);\n"
                "INSERT INTO players VALUES (1, 'V'), (2, 'Judy'), (3, 'Jackie');\n"
                "INSERT INTO orders VALUES (1, 1, 100), (2, 2, 80);\n\n-- 在这里写查询\n",
                "SELECT p.name, COALESCE(SUM(o.amount), 0) AS total FROM players p "
                "LEFT JOIN orders o ON o.player_id = p.id GROUP BY p.id ORDER BY p.id;",
                [
                    "assert columns == ['name', 'total'], columns",
                    "assert rows == [['V', 100], ['Judy', 80], ['Jackie', 0]], rows",
                    "assert len(rows) == 3, rows",
                ],
                "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT);\n"
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, player_id INTEGER, amount INTEGER);\n"
                "INSERT INTO players VALUES (1, 'V'), (2, 'Judy'), (3, 'Jackie');\n"
                "INSERT INTO orders VALUES (1, 1, 100), (2, 2, 80);\n\n"
                "SELECT p.name, COALESCE(SUM(o.amount), 0) AS total\nFROM players p\n"
                "LEFT JOIN orders o ON o.player_id = p.id\nGROUP BY p.id\nORDER BY p.id;\n",
                110,
            ),
        }),
        mk({
            "id": "sql13", "order": 512, "chapter": 52, "chapterName": CORE,
            "title": "三表串联", "subtitle": "多表连接与连接顺序", "xp": 90,
            "head": "一条查询串起三张表",
            "paras": [
                "真实业务很少只查两张表。订单要关联玩家和商品：orders 存 player_id 与 product_id，"
                "players 提供姓名，products 提供名称与单价。三表连接的写法是把 JOIN 连续写下去，"
                "每一步用 ON 把新表接到已有的结果上：FROM orders o JOIN players p ON p.id = o.player_id "
                "JOIN products pr ON pr.id = o.product_id。连接顺序在逻辑上从左到右，优化器可能重排，"
                "但书写顺序决定了可读性，建议按「事实表在前、维度表在后」组织。",

                "多表连接最常见的问题是行数放大。如果 orders 到 players 是多对一，连接不会增加行数；"
                "但如果再连一张同样是一对多的表，例如订单明细，两边会形成笛卡尔积，一条订单会与多条"
                "明细组合，金额被重复累加。判断方法很简单：连接完先 SELECT COUNT(*) 看行数，和预期的"
                "事实表行数对比。若不一致，说明某条连接是一对多且没有被聚合。这时要么先聚合子表再连接，"
                "要么用子查询把明细汇总成一行。",

                "连接条件写错也是高频错误，尤其是把 ON 写成 WHERE 或者漏写。漏写 ON 会得到笛卡尔积，"
                "三张表各十行时结果是一千行，看起来像数据爆炸；把条件放到 WHERE 里在 INNER JOIN 下结果"
                "相同，但和 LEFT JOIN 混用时语义就变了。另一种隐蔽错误是连接键类型不一致，例如一边是 "
                "INTEGER、一边是 TEXT，SQLite 会做隐式转换，可能导致索引失效，查询变慢但不报错。"
                "建表时保持外键与主键类型一致，是最省事的预防手段。",

                "多表查询还要注意列名歧义。三张表都有 id 和 name 时，SELECT id 会直接报 ambiguous，"
                "必须写 p.id、pr.name。养成「所有列都带表别名前缀」的习惯，代码可读性会明显提升，"
                "以后增删表也不容易出错。如果真的需要输出同名列，用 AS 起不同别名，例如 p.name AS player、"
                "pr.name AS product，前端拿到结果时才能区分。连接写完后，先 SELECT * 看一眼原始组合，"
                "再逐步裁剪列和加聚合，是排查多表问题的有效路径。",

                "连接的另一条实用原则是「先聚合再连接」。当子表是一对多关系且外层只需要汇总值时，"
                "先在子查询里把子表压成每键一行，再与主表连接，可以避免行数放大导致的重复计算。"
                "例如先 SELECT player_id, SUM(amount) AS total FROM orders GROUP BY player_id 得到"
                "每人一行，再 LEFT JOIN players 取姓名，结果天然正确。这种写法比连接后直接 SUM 更"
                "不容易出错，尤其在连接三张以上表时，能显著降低推理难度。",

                "多表查询的结果列命名也值得规划。三张表都有 name 时，输出列必须起不同别名，"
                "否则前端拿到的 JSON 里会出现重复键，后一个覆盖前一个。建议约定命名规则："
                "主表字段保持原名，关联表的字段加前缀，例如 player_name、product_name。"
                "如果结果要直接给报表工具使用，列名最好用英文小写下划线，避免中文别名在导出时"
                "出现编码问题。这些细节不影响 SQL 是否能跑通，却决定了这份查询能不能被长期复用。",

                "最后一个实践建议：把连接查询拆成「先验证、再聚合」两步。第一步用 SELECT * 加少量"
                "LIMIT 看几行原始组合，确认玩家、商品、数量都对得上；第二步再加上 GROUP BY 和聚合。"
                "直接写完整查询再调试，往往要在一堆数字里猜是哪一步错了，而分步验证能把问题定位到"
                "具体的连接或条件上。这个习惯在多表场景里节省的时间，远超过多写一条查询的成本。",
            ],
            "demo": "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT);\n"
                    "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER);\n"
                    "CREATE TABLE orders (id INTEGER PRIMARY KEY, player_id INTEGER, product_id INTEGER, qty INTEGER);\n"
                    "INSERT INTO players VALUES (1, 'V'), (2, 'Judy'), (3, 'Jackie');\n"
                    "INSERT INTO products VALUES (10, 'skin', 80), (20, 'mount', 120), (30, 'emote', 20);\n"
                    "INSERT INTO orders VALUES (1, 1, 10, 2), (2, 1, 20, 1), (3, 2, 10, 1), (4, 3, 30, 5);\n\n"
                    "SELECT p.name, pr.name AS product, o.qty, o.qty * pr.price AS amount\n"
                    "FROM orders o\nJOIN players p ON p.id = o.player_id\n"
                    "JOIN products pr ON pr.id = o.product_id\nORDER BY o.id;",
            "mid": table(
                ["步骤", "连接", "得到什么"],
                [
                    ["1", "orders JOIN players", "订单 + 玩家姓名"],
                    ["2", "再 JOIN products", "订单 + 玩家 + 商品"],
                    ["3", "GROUP BY 玩家", "每人汇总"],
                    ["4", "ORDER BY total", "按金额排名"],
                ],
            ),
            "demo2": "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT);\n"
                     "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER);\n"
                     "CREATE TABLE orders (id INTEGER PRIMARY KEY, player_id INTEGER, product_id INTEGER, qty INTEGER);\n"
                     "INSERT INTO players VALUES (1, 'V'), (2, 'Judy'), (3, 'Jackie');\n"
                     "INSERT INTO products VALUES (10, 'skin', 80), (20, 'mount', 120), (30, 'emote', 20);\n"
                     "INSERT INTO orders VALUES (1, 1, 10, 2), (2, 1, 20, 1), (3, 2, 10, 1), (4, 3, 30, 5);\n\n"
                     "SELECT p.name, COUNT(DISTINCT o.product_id) AS kinds, SUM(o.qty * pr.price) AS total\n"
                     "FROM players p\nJOIN orders o ON o.player_id = p.id\n"
                     "JOIN products pr ON pr.id = o.product_id\nGROUP BY p.id\nORDER BY total DESC;",
            "tip": "多表查询先写 FROM 与所有 JOIN，把骨架搭好，再往 SELECT 里填列。"
                   "这样即使中途报错，也能快速判断是连接写错还是列名写错。",
            "warn": "连续连接两张一对多的表会产生笛卡尔积，行数和金额都可能成倍放大。"
                    "先用 COUNT(*) 核对行数，再决定是否需要先聚合子表。",
            "quiz": (
                "三表连接时漏写 ON 条件会发生什么？",
                ["报语法错误", "返回空结果", "产生笛卡尔积，行数暴增", "只返回第一张表的行"],
                2,
                "没有连接条件时，两表每一行都互相配对，行数是两边行数的乘积。",
            ),
            "ex": exercise(
                "每人消费汇总",
                "连接 players、orders、products，计算每位玩家的消费总额 total（qty * price 求和），"
                "输出 name 与 total，按 total 降序。",
                "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT);\n"
                "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER);\n"
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, player_id INTEGER, product_id INTEGER, qty INTEGER);\n"
                "INSERT INTO players VALUES (1, 'V'), (2, 'Judy'), (3, 'Jackie');\n"
                "INSERT INTO products VALUES (10, 'skin', 80), (20, 'mount', 120), (30, 'emote', 20);\n"
                "INSERT INTO orders VALUES (1, 1, 10, 2), (2, 1, 20, 1), (3, 2, 10, 1), (4, 3, 30, 5);\n\n"
                "-- 在这里写查询\n",
                "SELECT p.name, SUM(o.qty * pr.price) AS total FROM players p "
                "JOIN orders o ON o.player_id = p.id JOIN products pr ON pr.id = o.product_id "
                "GROUP BY p.id ORDER BY total DESC;",
                [
                    "assert columns == ['name', 'total'], columns",
                    "assert rows == [['V', 280], ['Jackie', 100], ['Judy', 80]], rows",
                    "assert len(rows) == 3, rows",
                ],
                "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT);\n"
                "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER);\n"
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, player_id INTEGER, product_id INTEGER, qty INTEGER);\n"
                "INSERT INTO players VALUES (1, 'V'), (2, 'Judy'), (3, 'Jackie');\n"
                "INSERT INTO products VALUES (10, 'skin', 80), (20, 'mount', 120), (30, 'emote', 20);\n"
                "INSERT INTO orders VALUES (1, 1, 10, 2), (2, 1, 20, 1), (3, 2, 10, 1), (4, 3, 30, 5);\n\n"
                "SELECT p.name, SUM(o.qty * pr.price) AS total\nFROM players p\n"
                "JOIN orders o ON o.player_id = p.id\nJOIN products pr ON pr.id = o.product_id\n"
                "GROUP BY p.id\nORDER BY total DESC;\n",
                110,
            ),
        }),
        mk({
            "id": "sql14", "order": 513, "chapter": 52, "chapterName": CORE,
            "title": "查询里嵌套查询", "subtitle": "标量子查询与派生表", "xp": 90,
            "head": "把一条查询的结果当成输入",
            "paras": [
                "子查询就是写在另一条语句内部的 SELECT。按返回形态分三类：标量子查询返回一行一列，"
                "可以当成一个值使用，例如 WHERE score > (SELECT AVG(score) FROM matches)，把全表平均分"
                "当作比较基准；行子查询返回一行多列；表子查询返回多行多列，通常放在 FROM 后面当成临时表，"
                "称为派生表。这三类的使用场景不同，混用会导致语法错误或语义偏差，先分清类型再动手。",

                "标量子查询最常用，也最容易出问题。它要求子查询最多返回一行，如果实际返回多行，"
                "SQLite 会取第一行而不报错，PostgreSQL 则直接报错。写 WHERE score = (SELECT score FROM "
                "matches WHERE player = 'V') 时，如果 V 有多条记录，结果就不可预测。稳妥做法是先用 "
                "SELECT COUNT(*) 确认子查询唯一，或者改用聚合（MAX、AVG）显式保证单行。标量子查询"
                "在外层每行都可能执行一次，数据量大时性能不如 JOIN，优化器有时能改写成连接，"
                "但不能完全指望，看到慢查询要检查执行计划。",

                "派生表写在 FROM 后面，必须给它起别名，例如 FROM (SELECT player, SUM(score) AS total "
                "FROM matches GROUP BY player) t。派生表在查询开始时物化成临时结果，外层可以像普通表"
                "一样过滤、排序、再连接。它的好处是能把「先聚合再筛选」的逻辑写得层次分明：内层算每人"
                "总分，外层筛选总分超过阈值的玩家。用 CTE 可以进一步把这个结构命名，可读性更好，"
                "进阶篇会专门讲。",

                "相关子查询是另一类：子查询里引用了外层的列，因此外层每行都要重新求值一次。"
                "例如 SELECT name FROM players p WHERE EXISTS (SELECT 1 FROM orders o WHERE "
                "o.player_id = p.id) 中，子查询依赖 p.id，无法一次性算完。相关子查询表达力强，"
                "适合「存在性」判断，但性能通常不如 JOIN，因为外层有多少行就要执行多少次。"
                "能用 JOIN 或 EXISTS 改写时优先改写，确实需要逐行计算时再用，并确保子查询里的"
                "关联列有索引。",

                "子查询还可以嵌套多层，例如 WHERE score > (SELECT AVG(score) FROM matches WHERE "
                "mode = (SELECT ...))，但层数越多越难读、越难优化。经验上超过两层就应该改用 CTE "
                "或拆成临时表，把每一步的结果命名，再组合。SQL 的可读性和可维护性往往比省几行代码"
                "更重要，尤其在团队协作中，一条让人看不懂的嵌套查询会在半年后变成无人敢改的黑盒。"
                "写子查询时保持「一层一个目的」的节奏，是控制复杂度最有效的办法。",

                "派生表还有一个限制：它不能引用同一层 FROM 里其他表的列，也不能像相关子查询那样"
                "逐行求值，因为派生表在逻辑上是先算完的一份独立结果。想实现「每行都跟一个动态集合"
                "比较」的效果，要么用相关子查询，要么用 JOIN 加窗口函数。理解派生表「先物化再使用」"
                "的特性，能帮你判断一段查询能否改写成派生表形式，也能解释为什么某些相关子查询无法"
                "简单替换成 FROM 子句。",

                "标量子查询还有一个常见用法是「取最新一条」：先用 MAX(id) 或 MAX(created_at) 找到目标行，"
                "再把它当条件。例如 SELECT * FROM orders WHERE id = (SELECT MAX(id) FROM orders)，"
                "就能拿到最后一笔订单。这种写法简单直观，但要求子查询结果唯一；如果业务上有并列第一，"
                "应该改用 ORDER BY ... LIMIT 1 或者窗口函数。别把「碰巧唯一」当成「必然唯一」，"
                "数据一变，查询就会返回意料之外的结果。",
            ],
            "demo": "CREATE TABLE matches (id INTEGER PRIMARY KEY, player TEXT, score INTEGER);\n"
                    "INSERT INTO matches VALUES (1, 'V', 90), (2, 'Judy', 80), (3, 'V', 70),\n"
                    "  (4, 'Jackie', 60), (5, 'Judy', 95);\n\n"
                    "SELECT player, score\nFROM matches\n"
                    "WHERE score > (SELECT AVG(score) FROM matches)\nORDER BY score DESC;",
            "mid": table(
                ["形态", "返回", "位置"],
                [
                    ["标量子查询", "一行一列", "WHERE / SELECT"],
                    ["行子查询", "一行多列", "与 IN 或比较符配合"],
                    ["表子查询", "多行多列", "FROM 后面（派生表）"],
                    ["相关子查询", "依赖外层列", "EXISTS / 标量位置"],
                ],
            ),
            "demo2": "CREATE TABLE matches (id INTEGER PRIMARY KEY, player TEXT, score INTEGER);\n"
                     "INSERT INTO matches VALUES (1, 'V', 90), (2, 'Judy', 80), (3, 'V', 70),\n"
                     "  (4, 'Jackie', 60), (5, 'Judy', 95);\n\n"
                     "SELECT t.player, t.total\nFROM (SELECT player, SUM(score) AS total\n"
                     "      FROM matches GROUP BY player) t\nWHERE t.total > 150\nORDER BY t.total DESC;",
            "tip": "派生表必须起别名，否则 SQLite 会报语法错误。别名不只是形式要求，"
                   "外层引用列时也要靠它区分来源，例如 t.total。",
            "warn": "标量子查询返回多行时，SQLite 不报错而是静默取第一行，这个行为极不可靠。"
                    "写之前用 COUNT(*) 确认唯一，或在子查询里加聚合函数保证单行。",
            "quiz": (
                "FROM (SELECT player, SUM(score) AS total FROM matches GROUP BY player) t 中，"
                "t 的作用是？",
                ["给子查询结果起别名，供外层引用", "给表起别名", "创建一个新表", "去重"],
                0,
                "派生表必须命名，t 是外层查询引用这份临时结果的名称。",
            ),
            "ex": exercise(
                "高于平均分的比赛",
                "从 matches 表选出 score 高于全表平均分的 player 与 score，按 score 降序。",
                "CREATE TABLE matches (id INTEGER PRIMARY KEY, player TEXT, score INTEGER);\n"
                "INSERT INTO matches VALUES (1, 'V', 90), (2, 'Judy', 80), (3, 'V', 70),\n"
                "  (4, 'Jackie', 60), (5, 'Judy', 95);\n\n-- 在这里写查询\n",
                "SELECT player, score FROM matches WHERE score > (SELECT AVG(score) FROM matches) ORDER BY score DESC;",
                [
                    "assert columns == ['player', 'score'], columns",
                    "assert rows == [['Judy', 95], ['V', 90], ['Judy', 80]], rows",
                    "assert len(rows) == 3, rows",
                ],
                "CREATE TABLE matches (id INTEGER PRIMARY KEY, player TEXT, score INTEGER);\n"
                "INSERT INTO matches VALUES (1, 'V', 90), (2, 'Judy', 80), (3, 'V', 70),\n"
                "  (4, 'Jackie', 60), (5, 'Judy', 95);\n\n"
                "SELECT player, score\nFROM matches\nWHERE score > (SELECT AVG(score) FROM matches)\n"
                "ORDER BY score DESC;\n",
                110,
            ),
        }),
        mk({
            "id": "sql15", "order": 514, "chapter": 52, "chapterName": CORE,
            "title": "在集合里找答案", "subtitle": "IN 与 EXISTS", "xp": 90,
            "head": "存在与不属于",
            "paras": [
                "IN 用来判断一个值是否落在某个集合里，集合可以是字面量列表，也可以是子查询的结果。"
                "SELECT name FROM players WHERE id IN (SELECT player_id FROM orders) 会列出所有下过单的"
                "玩家，语义直观，很多场景下优化器会把它改写成半连接，性能与 JOIN 相当。NOT IN 则是"
                "它的反面，用来找「不在集合里」的行，例如从未下单的玩家。IN 的写法简洁，但有两个"
                "必须记住的陷阱：子查询列必须只有一列，以及 NULL 会让 NOT IN 整体失效。",

                "NOT IN 的 NULL 陷阱值得单独解释。若子查询返回的集合里包含 NULL，x NOT IN (1, 2, NULL) "
                "等价于 x <> 1 AND x <> 2 AND x <> NULL，最后一项结果是未知，整个条件就永远不为真，"
                "查询返回空结果。这不是 bug，而是三值逻辑的必然结果。规避方法有三种：子查询里加 "
                "WHERE 列 IS NOT NULL；改用 NOT EXISTS；或者用 LEFT JOIN ... WHERE 右表.id IS NULL。"
                "生产代码里推荐后两种，语义清晰且不受空值影响。",

                "EXISTS 判断子查询是否至少返回一行，返回的是布尔值，不关心具体内容。它天然是相关子查询，"
                "常写成 EXISTS (SELECT 1 FROM orders o WHERE o.player_id = p.id)，其中 SELECT 1 只是"
                "占位，写 * 或任何列都不影响语义。EXISTS 在找到第一行匹配后就可以停止扫描，因此在"
                "「只关心有没有」的场景里通常比 IN 更高效，也不受 NULL 影响。NOT EXISTS 同理，"
                "用来找不存在关联记录的行，是 NOT IN 的稳妥替代。",

                "IN 和 EXISTS 怎么选？如果子查询结果集小且确定无 NULL，IN 更简洁；如果子查询依赖外层列、"
                "或者只关心存在性，EXISTS 更合适。JOIN 与它们的关系也值得理清：JOIN 会返回匹配的每一行，"
                "可能放大行数，而 IN 与 EXISTS 只做布尔判断，不会改变外层行数。需要输出右表的具体字段时"
                "用 JOIN，只需要判断「有没有」时用 IN 或 EXISTS。三种写法各有位置，不是互相替代的关系。",

                "最后比较一下性能直觉：IN 适合子查询结果集小的情况，数据库可以把集合装进内存逐个比对；"
                "EXISTS 适合外层行数少、内层有索引的情况，找到第一条匹配就停；JOIN 适合需要右表字段、"
                "或需要对右表做聚合的情况。优化器通常会把它们互相改写，所以「哪种更快」不能一概而论，"
                "必须以 EXPLAIN QUERY PLAN 的实际输出为准。写代码时先选语义最清楚的写法，再根据执行"
                "计划调优，而不是凭感觉猜哪种高级。",

                "再补充一个数据质量的用法：找出「有订单但玩家不存在」的脏数据，可以写 "
                "SELECT o.id FROM orders o LEFT JOIN players p ON p.id = o.player_id WHERE p.id IS NULL。"
                "这类反连接（anti-join）检查应该定期跑，尤其是在没有外键约束的库上。SQLite 默认不"
                "强制外键，删除玩家时订单可能变成孤儿记录，表面上看一切正常，统计时才发现金额对不上。"
                "把反连接检查写进数据巡检脚本，是低成本高回报的工程习惯。",

                "IN 还有一个实用写法是配合字面量做「白名单」过滤，例如 WHERE region IN ('Neon', 'Watson')，"
                "比写一串 OR 更简洁，也更容易让优化器识别。列表太长时要注意 SQL 语句长度限制，"
                "几百个值以上通常应该改成临时表或 JOIN 子查询。EXISTS 也可以用在 SELECT 列表里"
                "做标记列，返回 1 或 0，例如 EXISTS (SELECT 1 FROM orders o WHERE o.player_id = p.id) "
                "AS has_order，适合给每行打一个布尔标签，再交给业务层决定怎么展示。需要注意的是，NOT EXISTS 返回的布尔值在 SQLite 里是 1 或 0，不是 TRUE/FALSE 关键字，展示时可按业务需要再包一层 CASE。另外，子查询里忘记写关联条件会让 EXISTS 恒为真，查询结果变成全表，这类错误不会报错，只能靠核对行数发现。",
            ],
            "demo": "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT);\n"
                    "CREATE TABLE orders (id INTEGER PRIMARY KEY, player_id INTEGER, amount INTEGER);\n"
                    "INSERT INTO players VALUES (1, 'V'), (2, 'Judy'), (3, 'Jackie'), (4, 'Rogue');\n"
                    "INSERT INTO orders VALUES (1, 1, 100), (2, 2, 80);\n\n"
                    "SELECT name\nFROM players\nWHERE id IN (SELECT player_id FROM orders)\nORDER BY name;",
            "mid": table(
                ["写法", "语义", "注意"],
                [
                    ["IN (子查询)", "属于集合", "子查询只能返回一列"],
                    ["NOT IN", "不属于集合", "集合含 NULL 时结果为空"],
                    ["EXISTS", "至少存在一行", "只判断有无，不取值"],
                    ["NOT EXISTS", "不存在", "推荐替代 NOT IN"],
                ],
            ),
            "demo2": "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT);\n"
                     "CREATE TABLE orders (id INTEGER PRIMARY KEY, player_id INTEGER, amount INTEGER);\n"
                     "INSERT INTO players VALUES (1, 'V'), (2, 'Judy'), (3, 'Jackie'), (4, 'Rogue');\n"
                     "INSERT INTO orders VALUES (1, 1, 100), (2, 2, 80);\n\n"
                     "SELECT p.name\nFROM players p\nWHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.player_id = p.id)\n"
                     "ORDER BY p.name;",
            "tip": "EXISTS 里的 SELECT 列表写什么都不影响结果，习惯写 SELECT 1，向读者传达"
                   "「这里只关心有没有行，不关心值」。",
            "warn": "NOT IN 遇到子查询返回 NULL 会返回空结果，不是因为数据少，而是三值逻辑导致条件恒不为真。"
                    "跨库迁移时这个坑尤其常见，建议统一用 NOT EXISTS。",
            "quiz": (
                "子查询 SELECT player_id FROM orders 返回 (1, 2, NULL)，"
                "WHERE id NOT IN (该子查询) 的结果是？",
                ["返回 id 不等于 1 和 2 的行", "返回空结果", "报语法错误", "返回所有行"],
                1,
                "集合含 NULL 时，id <> NULL 结果为未知，整个 NOT IN 条件不成立，查询返回空。",
            ),
            "ex": exercise(
                "从未下单的玩家",
                "用 NOT EXISTS 找出没有任何订单的玩家 name，按字母升序。",
                "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT);\n"
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, player_id INTEGER, amount INTEGER);\n"
                "INSERT INTO players VALUES (1, 'V'), (2, 'Judy'), (3, 'Jackie'), (4, 'Rogue');\n"
                "INSERT INTO orders VALUES (1, 1, 100), (2, 2, 80);\n\n-- 在这里写查询\n",
                "SELECT p.name FROM players p WHERE NOT EXISTS "
                "(SELECT 1 FROM orders o WHERE o.player_id = p.id) ORDER BY p.name;",
                [
                    "assert columns == ['name'], columns",
                    "assert rows == [['Jackie'], ['Rogue']], rows",
                    "assert len(rows) == 2, rows",
                ],
                "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT);\n"
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, player_id INTEGER, amount INTEGER);\n"
                "INSERT INTO players VALUES (1, 'V'), (2, 'Judy'), (3, 'Jackie'), (4, 'Rogue');\n"
                "INSERT INTO orders VALUES (1, 1, 100), (2, 2, 80);\n\n"
                "SELECT p.name\nFROM players p\n"
                "WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.player_id = p.id)\nORDER BY p.name;\n",
                110,
            ),
        }),
    ]


def core_16_20():
    return [
        mk({
            "id": "sql16", "order": 515, "chapter": 52, "chapterName": CORE,
            "title": "条件表达式", "subtitle": "CASE WHEN", "xp": 90,
            "head": "在查询里写 if",
            "paras": [
                "CASE WHEN 是 SQL 里的条件表达式，写法是 CASE WHEN 条件 THEN 结果 WHEN 条件 THEN 结果 "
                "ELSE 默认值 END。它从上到下依次判断，命中第一个为真的分支就返回对应结果，后面的分支"
                "不再执行。这意味顺序很重要：判断分数等级时，必须先写 score >= 90 再写 score >= 80，"
                "否则 95 分会先命中 >= 80 的分支，被判成 A。把条件从严格到宽松排列，是写 CASE 的基本纪律。",

                "CASE 有两种形式。搜索形式如上，条件可以任意写，最常用；简单形式是 CASE 列 WHEN 值 "
                "THEN 结果 END，只做等值匹配，等价于一层层写列 = 值。简单形式只适合枚举映射，例如把"
                "地区代码翻译成中文名；一旦涉及范围判断或组合条件，就必须用搜索形式。如果所有条件都"
                "不满足又没写 ELSE，结果是 NULL，这经常导致报表出现空白，需要默认值时务必显式写 ELSE。",

                "CASE 最强大的用法是在聚合里做条件计数和条件求和。SUM(CASE WHEN score >= 90 THEN 1 "
                "ELSE 0 END) 统计高分场次，SUM(CASE WHEN mode = 'ranked' THEN amount ELSE 0 END) 只对"
                "排位赛金额求和。这相当于 SQL 版的透视表：一次扫描数据，同时算出多个口径的指标。"
                "比写多条 WHERE 不同的查询分别统计高效得多，也是数据看板最常见的写法之一。",

                "CASE 还能用在 ORDER BY 里做自定义排序，例如让特定状态排在最前：ORDER BY CASE status "
                "WHEN 'urgent' THEN 0 WHEN 'normal' THEN 1 ELSE 2 END。它也可以出现在 GROUP BY 里做分档"
                "统计，例如按分数段分组。注意 CASE 返回的所有分支类型应当一致，混合数字和文本会让"
                "结果类型变得难以预测。每个分支都写清楚、顺序排对、默认值补齐，CASE 就是查询里最灵活的"
                "控制结构。",

                "CASE 还能和 COUNT 组合出「条件计数」的另一种写法：COUNT(CASE WHEN score >= 90 THEN 1 "
                "END) 只统计满足条件的行，因为不满足时返回 NULL，而 COUNT 会跳过 NULL。它和 "
                "SUM(CASE WHEN ... THEN 1 ELSE 0 END) 结果相同，区别在于前者不写 ELSE、更简洁，"
                "后者语义更直白。团队里选一种统一使用即可，混着写会让审阅者多花时间确认两种写法"
                "是不是同一个意思。",

                "在真实报表里，CASE 常被用来做「分桶」。例如把订单金额分成小单、中单、大单三档，"
                "再按档位分组统计单量和总额，一行 SQL 就能产出完整的分布报表。分桶的边界要写清楚，"
                "避免出现 100 元既不算中单也不算大单的空档。写完后可以用" 
                "SELECT MIN(amount), MAX(amount), COUNT(*) 核对每档的范围与总数，确保没有记录被漏掉。"
                "这类验证习惯能把「看起来对」变成「确认对」，是数据工作里最值得培养的素养。",

                "CASE 还有一个常见的坑：在 WHERE 里对 CASE 结果做过滤时，必须把整个 CASE 表达式"
                "重复写一遍，因为 WHERE 不能引用 SELECT 里定义的别名。想避免重复，可以套一层派生表，"
                "把 CASE 的结果作为列输出，外层再按这个列过滤。这个技巧在复杂报表里很实用，"
                "也让 SQL 的分层结构更清晰：内层负责计算，外层负责筛选和排序，各司其职。",

                "简单 CASE 形式还有一个容易踩的坑：它做的是等值匹配，不会做类型转换以外的任何处理。"
                "CASE region WHEN 'neon' THEN '霓虹' ELSE '其他' END 对 'Neon' 不会命中，因为字符串比较"
                "区分大小写。如果数据来源不规范，要么先用 LOWER 统一，要么改用搜索形式写 "
                "WHEN LOWER(region) = 'neon'。看起来只是写法差异，实际决定了结果对不对，"
                "写完后用小样本验证一遍再上报表，是稳妥的做法。",
            ],
            "demo": "CREATE TABLE matches (id INTEGER PRIMARY KEY, player TEXT, score INTEGER);\n"
                    "INSERT INTO matches VALUES (1, 'V', 92), (2, 'Judy', 85), (3, 'Jackie', 71), (4, 'Rogue', 58);\n\n"
                    "SELECT player, score,\n"
                    "       CASE WHEN score >= 90 THEN 'S'\n"
                    "            WHEN score >= 80 THEN 'A'\n"
                    "            WHEN score >= 70 THEN 'B'\n"
                    "            ELSE 'C' END AS grade\n"
                    "FROM matches\nORDER BY score DESC;",
            "mid": table(
                ["写法", "用途", "示例"],
                [
                    ["CASE WHEN ... THEN ...", "范围判断", "score >= 90"],
                    ["CASE 列 WHEN 值", "等值映射", "CASE region WHEN 'Neon'"],
                    ["ELSE", "默认分支", "ELSE 'C'"],
                    ["聚合内 CASE", "条件统计", "SUM(CASE WHEN ... THEN 1 END)"],
                ],
            ),
            "demo2": "CREATE TABLE matches (id INTEGER PRIMARY KEY, player TEXT, score INTEGER);\n"
                     "INSERT INTO matches VALUES (1, 'V', 92), (2, 'Judy', 85), (3, 'Jackie', 71), (4, 'Rogue', 58);\n\n"
                     "SELECT SUM(CASE WHEN score >= 90 THEN 1 ELSE 0 END) AS s_count,\n"
                     "       SUM(CASE WHEN score >= 80 AND score < 90 THEN 1 ELSE 0 END) AS a_count,\n"
                     "       SUM(CASE WHEN score < 80 THEN 1 ELSE 0 END) AS rest\nFROM matches;",
            "tip": "把 CASE 的分支按条件从严格到宽松排列。判断 score >= 90 必须写在 score >= 80 前面，"
                   "否则第一个分支永远轮不到。",
            "warn": "忘写 ELSE 且所有条件都不满足时，CASE 返回 NULL，不是 0 也不是空串。"
                    "做数值汇总时这会污染 SUM，务必补上 ELSE 0。",
            "quiz": (
                "CASE WHEN score >= 80 THEN 'A' WHEN score >= 90 THEN 'S' ELSE 'B' END 对 score = 95 返回？",
                ["S", "A", "B", "NULL"],
                1,
                "分支从上到下判断，95 先命中 >= 80，返回 A；要得到 S 必须把 >= 90 写在前面。",
            ),
            "ex": exercise(
                "给分数分档",
                "从 matches 表按 score 分档：90 及以上为 'S'，80 到 89 为 'A'，70 到 79 为 'B'，"
                "其余为 'C'。输出 player、score、grade，按 score 降序。",
                "CREATE TABLE matches (id INTEGER PRIMARY KEY, player TEXT, score INTEGER);\n"
                "INSERT INTO matches VALUES (1, 'V', 92), (2, 'Judy', 85), (3, 'Jackie', 71), (4, 'Rogue', 58);\n\n"
                "-- 在这里写查询\n",
                "SELECT player, score, CASE WHEN score >= 90 THEN 'S' WHEN score >= 80 THEN 'A' "
                "WHEN score >= 70 THEN 'B' ELSE 'C' END AS grade FROM matches ORDER BY score DESC;",
                [
                    "assert columns == ['player', 'score', 'grade'], columns",
                    "assert rows == [['V', 92, 'S'], ['Judy', 85, 'A'], ['Jackie', 71, 'B'], ['Rogue', 58, 'C']], rows",
                    "assert len(rows) == 4, rows",
                ],
                "CREATE TABLE matches (id INTEGER PRIMARY KEY, player TEXT, score INTEGER);\n"
                "INSERT INTO matches VALUES (1, 'V', 92), (2, 'Judy', 85), (3, 'Jackie', 71), (4, 'Rogue', 58);\n\n"
                "SELECT player, score,\n"
                "       CASE WHEN score >= 90 THEN 'S'\n"
                "            WHEN score >= 80 THEN 'A'\n"
                "            WHEN score >= 70 THEN 'B'\n"
                "            ELSE 'C' END AS grade\n"
                "FROM matches\nORDER BY score DESC;\n",
                110,
            ),
        }),
        mk({
            "id": "sql17", "order": 516, "chapter": 52, "chapterName": CORE,
            "title": "文本处理", "subtitle": "字符串函数", "xp": 90,
            "head": "把名字改写成想要的样子",
            "paras": [
                "SQLite 的字符串函数覆盖了大多数日常需求：UPPER 转大写、LOWER 转小写、LENGTH 取长度、"
                "SUBSTR 截取子串、REPLACE 替换、TRIM 去首尾空格、INSTR 查子串位置、PRINTF 做格式化。"
                "这些函数可以直接用在 SELECT 列表、WHERE 条件、ORDER BY 里，也可以互相嵌套。字符串"
                "拼接用 || 运算符，而不是加号；'a' || 'b' 得到 'ab'，而 'a' + 'b' 会尝试把两边转成数字，"
                "得到 0。",

                "SUBSTR 的下标从 1 开始，这一点和 Python 从 0 开始不同，是从其他语言转过来最容易踩的坑。"
                "SUBSTR('neon', 2, 2) 返回 'eo'，表示从第 2 个字符开始取 2 个；如果只写两个参数，"
                "表示取到末尾。负数下标表示从末尾倒数，SUBSTR('neon', -2) 返回 'on'。LENGTH 对 TEXT "
                "返回字符数，对 BLOB 返回字节数，中文在 SQLite 里按字符计数，长度是 1 而不是 3，"
                "这一点比 MySQL 的字节语义更符合直觉。",

                "LIKE 和字符串函数常常配合使用：WHERE name LIKE 'J%' 找 J 开头的名字，'%son' 找 son 结尾，"
                "'%a%' 找包含 a 的名字。下划线 _ 匹配任意单个字符。LIKE 默认对 ASCII 大小写不敏感，"
                "但 = 是敏感的，这种不一致要心里有数；需要统一时用 LOWER(name) = LOWER('judy')。"
                "REPLACE 做全局替换，TRIM 默认去空格也可以指定字符。格式化用 PRINTF，"
                "例如 PRINTF('%03d', 7) 得到 '007'，拼接导出文件名时很好用。",

                "实际工程里，字符串清洗往往比查询本身更麻烦：前后空格、大小写不一致、全角半角混用、"
                "空串与 NULL 混杂。建议在写入时就做规范化，例如统一 TRIM 后存储、姓名首字母大写、"
                "地区代码统一大写，查询时就不用到处套函数。如果不得不在查询里清洗，尽量把函数作用在"
                "常量或小结果集上，避免对整列套函数导致索引失效。字符串函数很强大，但滥用会让查询"
                "难以维护，也会拖慢执行速度。",

                "再补充几个不常用但关键时刻很有用的函数。SUBSTR 与 INSTR 可以组合实现简单的解析，"
                "例如从 'player:V' 这样的字符串里取出冒号后面的部分：SUBSTR(s, INSTR(s, ':') + 1)。"
                "PRINTF 支持 %s、%d、%f、%.2f 等占位符，生成固定宽度的编号或两位小数非常方便。"
                "GROUP_CONCAT 把多行文本拼成一行，适合把一位玩家的所有成就名合成一个标签串，"
                "但它没有顺序保证，需要有序时得在子查询里先排序再聚合。",

                "字符串比较还有一个容易忽略的规则：SQLite 默认按字节序比较，'Z' 排在 'a' 前面，"
                "因为大写字母的编码更小。如果希望按照人类习惯忽略大小写排序，可以写 "
                "ORDER BY LOWER(name)，或者在建表时给列加 COLLATE NOCASE，让该列的默认比较"
                "不区分大小写。中文排序在 SQLite 里没有内置拼音规则，只能按 Unicode 码点排，"
                "需要拼音序时得借助外部字典或应用层排序，这一点在设计中文站点的搜索功能时要"
                "提前考虑，而不是等到上线后才发现顺序很怪。",

                "字符串函数还能做简单的脱敏与格式化。例如把手机号中间四位替换成星号，可以用 "
                "SUBSTR(phone, 1, 3) || '****' || SUBSTR(phone, 8)，输出时既不泄露完整号码，"
                "又能让用户辨认。生成用户名时可以 LOWER(REPLACE(name, ' ', '.'))，把空格换成点并统一"
                "小写。这些变换放在查询里做，好处是原始数据保持完整，展示层按需处理；缺点是每次查询"
                "都要计算，高频接口更适合在写入时生成一个派生列并加索引。还有一个容易忽略的点：LENGTH 对中文按字符计数，对 BLOB 按字节计数，判断长度时先确认列的类型。SUBSTR 的下标从 1 开始，越界时返回空串而不是报错，这会让错误悄悄变成空值，测试时要专门覆盖边界下标。",
            ],
            "demo": "SELECT UPPER('neon') AS upper_name,\n"
                    "       LOWER('NEON') AS lower_name,\n"
                    "       LENGTH('neon') AS len,\n"
                    "       SUBSTR('neon', 2, 2) AS part,\n"
                    "       REPLACE('a-b-c', '-', '/') AS replaced,\n"
                    "       TRIM('  x  ') AS trimmed,\n"
                    "       INSTR('neon', 'e') AS pos;",
            "mid": table(
                ["函数", "作用", "示例"],
                [
                    ["UPPER / LOWER", "大小写转换", "UPPER('neon') = 'NEON'"],
                    ["LENGTH", "字符数", "LENGTH('neon') = 4"],
                    ["SUBSTR", "截取，下标从 1 开始", "SUBSTR('neon', 2, 2) = 'eo'"],
                    ["REPLACE", "全局替换", "REPLACE('a-b', '-', '/') = 'a/b'"],
                    ["TRIM", "去首尾空格", "TRIM('  x  ') = 'x'"],
                    ["||", "字符串拼接", "'a' || 'b' = 'ab'"],
                ],
            ),
            "demo2": "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT);\n"
                     "INSERT INTO players VALUES (1, 'v'), (2, 'judy'), (3, 'jackie');\n\n"
                     "SELECT UPPER(name) AS name, LENGTH(name) AS len\nFROM players\n"
                     "WHERE name LIKE 'j%'\nORDER BY name;",
            "tip": "字符串拼接用 ||，不要用 +。SQLite 的 + 是算术加法，会把文本尝试转成数字，"
                   "拼接需求用加号很容易得到 0。",
            "warn": "对列套函数会让该列上的索引失效，例如 WHERE UPPER(name) = 'V' 无法使用 name 的普通索引。"
                    "高频查询可以考虑建表达式索引，或者写入时就统一大小写。",
            "quiz": (
                "SUBSTR('neon', 2, 2) 的返回值是？",
                ["'ne'", "'eo'", "'on'", "'e'"],
                1,
                "SQLite 的 SUBSTR 下标从 1 开始，从第 2 个字符取 2 个，得到 'eo'。",
            ),
            "ex": exercise(
                "规范化玩家名",
                "从 players 表选出 name 以 j 开头的玩家（不区分大小写），输出大写后的 name 与长度 len，"
                "按 name 升序。",
                "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT);\n"
                "INSERT INTO players VALUES (1, 'v'), (2, 'judy'), (3, 'jackie');\n\n-- 在这里写查询\n",
                "SELECT UPPER(name) AS name, LENGTH(name) AS len FROM players WHERE name LIKE 'j%' ORDER BY name;",
                [
                    "assert columns == ['name', 'len'], columns",
                    "assert rows == [['JACKIE', 6], ['JUDY', 4]], rows",
                    "assert len(rows) == 2, rows",
                ],
                "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT);\n"
                "INSERT INTO players VALUES (1, 'v'), (2, 'judy'), (3, 'jackie');\n\n"
                "SELECT UPPER(name) AS name, LENGTH(name) AS len\nFROM players\n"
                "WHERE name LIKE 'j%'\nORDER BY name;\n",
                110,
            ),
        }),
        mk({
            "id": "sql18", "order": 517, "chapter": 52, "chapterName": CORE,
            "title": "跟时间打交道", "subtitle": "日期与时间函数", "xp": 100,
            "head": "SQLite 用文本存日期",
            "paras": [
                "SQLite 没有独立的日期类型，日期和时间通常存成 TEXT，格式为 YYYY-MM-DD 或 "
                "YYYY-MM-DD HH:MM:SS；也可以存成 Unix 时间戳整数或 Julian 天数。存成 ISO 格式文本的"
                "好处是字典序等于时间序，比较和排序都能直接用字符串操作，肉眼也容易读。建表时把列"
                "声明为 TEXT，并在应用层保证格式统一，是 SQLite 项目最常见的做法。格式一旦混用，"
                "例如有的带时分秒有的不带，排序和区间查询就会出现意外结果。",

                "DATE 函数把时间值规整成 YYYY-MM-DD，TIME 返回时分秒，DATETIME 返回完整时间，"
                "JULIANDAY 返回 Julian 天数（浮点）。它们都支持修饰符，可以链式叠加：DATE('2024-03-15', "
                "'+1 month') 得到下个月同一天，再加 'start of month' 得到下个月第一天；'-7 days' 得到"
                "一周前；'weekday 1' 找到下一个周一。修饰符从左到右依次应用，顺序不同结果可能不同，"
                "写复杂日期计算时建议一步一步验证。",

                "STRFTIME 负责格式化，把日期转成想要的字符串：%Y 四位年、%m 两位月、%d 两位日、"
                "%H 小时、%M 分钟、%S 秒、%w 星期（0 是周日）、%j 一年中的第几天。按月汇总订单时，"
                "STRFTIME('%Y-%m', paid_on) 是最常用的分组键。反过来，如果只有年月字符串想补成完整日期，"
                "可以拼接 '-01' 再交给 DATE 处理。格式化符号区分大小写，%m 是月、%M 是分钟，"
                "写错不会报错但结果会出乎意料。",

                "时间区间查询要注意边界。查「2024 年 1 月」的数据，写 paid_on >= '2024-01-01' AND "
                "paid_on < '2024-02-01' 比用 BETWEEN '2024-01-01' AND '2024-01-31' 更稳妥，因为后者"
                "会漏掉 1 月 31 日带时分秒的记录。当前时间用 DATE('now')、DATETIME('now') 获取，"
                "注意它返回 UTC，需要本地时间时加 'localtime' 修饰符。跨时区业务最好统一存 UTC，"
                "展示时再按用户时区转换，避免夏令时和时区偏移带来的混乱。",

                "日期函数还可以做「距今多久」的计算：JULIANDAY('now') - JULIANDAY(created_at) 得到"
                "相差的天数，乘以 24 得到小时数。查「最近 7 天」的数据写 "
                "created_at >= DATE('now', '-7 days')，比在应用层算好日期再拼字符串更可靠，"
                "也不会受时区设置影响。需要注意的是 DATE('now') 只到天，如果要精确到分钟，"
                "用 DATETIME('now', '-7 days')。报表按天汇总时用前者，审计日志按秒比对时用后者。",

                "最后提醒：日期格式化会改变字符串，但不会改变底层存储。视图或查询里用 STRFTIME "
                "输出 '2024-01' 只影响展示，底表仍存完整的 '2024-01-05'。如果后续要按这个月做"
                "连接或比较，必须在外层重新解析，不能直接把 '2024-01' 当成日期用。养成「存储保持"
                "完整、展示才裁剪」的习惯，能避免大量难以追查的日期比较错误，也让数据在导出、"
                "迁移时保持可追溯。",

                "时间戳与文本的转换也要留意。如果数据库里存的是 Unix 时间戳整数，可以用 "
                "DATE(ts, 'unixepoch') 转成日期，加 'localtime' 再转本地时间；反过来用 "
                "STRFTIME('%s', 日期文本) 取回时间戳字符串，需要整数时再 CAST。两种存储方式"
                "各有取舍：文本可读性好、便于人工排查，整数比较快、没有格式歧义。同一个系统里"
                "只选一种，并在文档里写清楚，否则混用会让每条查询都要先判断这一列到底是什么格式。",

                "再补充一个跨月统计的写法。想按自然月分组且保证空月也出现在结果里，单纯 GROUP BY "
                "做不到，因为没有任何一行的月份是空的。这时需要一张日历表，或者用递归 CTE 生成"
                "月份序列再 LEFT JOIN 实际数据。数据看板里「本月零单」这类指标经常需要这种补零技巧，"
                "否则图表会缺一段柱子，看起来像系统故障。进阶篇的 CTE 会给出生成序列的具体写法，"
                "这里先建立「聚合结果需要补全维度」的意识。",
            ],
            "demo": "SELECT DATE('2024-03-15', '+1 month', 'start of month') AS next_month_start,\n"
                    "       DATE('2024-03-15', '-7 days') AS week_before,\n"
                    "       STRFTIME('%Y-%m', '2024-03-15') AS ym,\n"
                    "       STRFTIME('%w', '2024-03-15') AS weekday,\n"
                    "       JULIANDAY('2024-03-15') - JULIANDAY('2024-03-01') AS days;",
            "mid": table(
                ["函数", "返回", "示例"],
                [
                    ["DATE", "日期部分", "DATE('2024-03-15') = '2024-03-15'"],
                    ["DATETIME", "日期时间", "DATETIME('now')"],
                    ["STRFTIME", "格式化文本", "STRFTIME('%Y-%m', 日期)"],
                    ["JULIANDAY", "Julian 天数", "两个日期相减得天差"],
                    ["修饰符", "日期加减", "'+1 month' / '-7 days'"],
                ],
            ),
            "demo2": "CREATE TABLE orders (id INTEGER PRIMARY KEY, paid_on TEXT, amount INTEGER);\n"
                     "INSERT INTO orders VALUES (1, '2024-01-05', 100), (2, '2024-01-20', 50),\n"
                     "  (3, '2024-02-03', 80), (4, '2024-02-18', 120);\n\n"
                     "SELECT STRFTIME('%Y-%m', paid_on) AS month, SUM(amount) AS total\n"
                     "FROM orders\nGROUP BY month\nORDER BY month;",
            "tip": "日期统一存 YYYY-MM-DD 的 TEXT，必要时带 HH:MM:SS。不要存 '2024/3/5' 这种格式，"
                   "字典序会乱，字符串比较也不等于时间比较。",
            "warn": "BETWEEN '2024-01-01' AND '2024-01-31' 会漏掉 1 月 31 日当天带时分秒的记录。"
                    "查整月请用 >= 月初 AND < 下月月初 的左闭右开写法。",
            "quiz": (
                "要按月份汇总订单，最合适的分组表达式是？",
                ["GROUP BY paid_on", "GROUP BY STRFTIME('%Y-%m', paid_on)", "GROUP BY DATE(paid_on)", "GROUP BY YEAR(paid_on)"],
                1,
                "STRFTIME('%Y-%m', paid_on) 把日期截成 2024-01 这样的年月文本，正是按月分组需要的粒度。",
            ),
            "ex": exercise(
                "按月汇总",
                "从 orders 表按月份汇总金额，输出 month（YYYY-MM）与 total，按 month 升序。",
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, paid_on TEXT, amount INTEGER);\n"
                "INSERT INTO orders VALUES (1, '2024-01-05', 100), (2, '2024-01-20', 50),\n"
                "  (3, '2024-02-03', 80), (4, '2024-02-18', 120);\n\n-- 在这里写查询\n",
                "SELECT STRFTIME('%Y-%m', paid_on) AS month, SUM(amount) AS total FROM orders GROUP BY month ORDER BY month;",
                [
                    "assert columns == ['month', 'total'], columns",
                    "assert rows == [['2024-01', 150], ['2024-02', 200]], rows",
                    "assert len(rows) == 2, rows",
                ],
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, paid_on TEXT, amount INTEGER);\n"
                "INSERT INTO orders VALUES (1, '2024-01-05', 100), (2, '2024-01-20', 50),\n"
                "  (3, '2024-02-03', 80), (4, '2024-02-18', 120);\n\n"
                "SELECT STRFTIME('%Y-%m', paid_on) AS month, SUM(amount) AS total\n"
                "FROM orders\nGROUP BY month\nORDER BY month;\n",
                120,
            ),
        }),
        mk({
            "id": "sql19", "order": 518, "chapter": 52, "chapterName": CORE,
            "title": "集合运算", "subtitle": "UNION / INTERSECT / EXCEPT", "xp": 90,
            "head": "把两个结果集拼起来",
            "paras": [
                "集合运算把两条 SELECT 的结果当成集合来处理。UNION 取并集并自动去重，UNION ALL 取并集"
                "但保留重复且更快；INTERSECT 取交集，只保留两边都有的行；EXCEPT 取差集，保留在左边"
                "但不在右边的行。使用它们的前提是两条查询的列数相同、对应列的类型兼容，列名以第一条"
                "查询为准，ORDER BY 只能写在最后，作用于整个合并结果。",

                "UNION 去重意味着它要对结果排序或建哈希表，数据量大时开销明显；如果业务上确定两边"
                "不会有重复，或者重复本身有意义（例如统计所有流水，同一天两笔相同金额不能合并），"
                "就应该用 UNION ALL。经验法则是：默认写 UNION ALL，只有确实需要去重时才写 UNION。"
                "这个选择在日志分析里尤其重要，用错了会把真实的重复记录悄悄吃掉，导致统计结果偏小。",

                "INTERSECT 和 EXCEPT 在业务上分别对应「同时满足」和「只在一边」。例如找出两个赛季都"
                "上过场的玩家用 INTERSECT，找出只在第一个赛季出现的新玩家用 EXCEPT。它们同样会去重，"
                "而且对 NULL 的处理是把 NULL 视为相等，这一点和 = 比较不同：两个 NULL 在集合运算里"
                "算同一个元素，会被去重成一条。理解这个差别，才能正确解释结果行数。",

                "集合运算要求列的顺序和数量严格对齐，第一列对第一列、第二列对第二列，列名不参与匹配。"
                "如果两张表列顺序不同，必须显式写出对应的列名再合并，不能图省事写 SELECT *。"
                "合并后想区分数据来源，可以加一个常量列，例如 SELECT 'neon' AS source, name FROM neon "
                "UNION ALL SELECT 'watson', name FROM watson，这样结果里能看出每行来自哪张表。"
                "排序时如果要按来源分组，把这个常量列放进 ORDER BY 即可。",

                "集合运算的另一个常见用途是「合并多张结构相同的分表」。按季度拆分的 orders_2024q1、"
                "orders_2024q2 可以用 UNION ALL 拼成全年视图，再在视图上做统计。用 UNION ALL 而不是 "
                "UNION，是因为不同季度的订单 id 不会重复，去重只会白白增加排序开销。如果确实存在"
                "跨表重复，例如同一笔订单被重复导入，才需要 UNION 或在外层用 GROUP BY 去重。"
                "分表合并后最好加一列来源标记，方便回溯数据出自哪张表。",

                "最后一点：集合运算的优先级低于 ORDER BY 和 LIMIT，写多段合并时要用括号明确范围，"
                "例如 (SELECT ... LIMIT 5) UNION ALL (SELECT ... LIMIT 5)。如果只在最后写一个 "
                "LIMIT 5，它作用于合并后的整个结果，而不是每段各取 5 条。这个小差异在写「取各表"
                "前几名」的需求时经常出错，测试时用两组明显不同的数据就能一眼看出结果是否符合预期。",

                "集合运算还有一个语义细节：ORDER BY 只能出现在最后，且只能引用第一条 SELECT 的列名"
                "或列序号。如果两段查询的列名不同，例如第一段叫 name、第二段叫 player_name，"
                "排序时必须用第一段的名字或序号，用第二段的名字会报错。同理，WHERE 不能写在合并"
                "之后，想过滤合并结果只能套一层派生表或 CTE，在外层加条件。这些限制源于集合运算"
                "「先合并再处理」的语义，理解之后就不会写出语法正确但逻辑混乱的语句。实践时建议先分别验证两段查询的行数与内容，确认各自符合预期，再做集合运算；直接合并后调试，很难判断差异来自哪一段。这也是为什么复杂报表更推荐用 CTE：每一段都能独立运行、独立核对。",
            ],
            "demo": "CREATE TABLE neon (name TEXT);\nCREATE TABLE watson (name TEXT);\n"
                    "INSERT INTO neon VALUES ('V'), ('Judy'), ('Jackie');\n"
                    "INSERT INTO watson VALUES ('Judy'), ('Rogue');\n\n"
                    "SELECT name FROM neon\nUNION\nSELECT name FROM watson\nORDER BY name;",
            "mid": table(
                ["运算", "含义", "是否去重"],
                [
                    ["UNION", "并集", "去重"],
                    ["UNION ALL", "并集", "保留重复，更快"],
                    ["INTERSECT", "交集", "去重"],
                    ["EXCEPT", "差集（左减右）", "去重"],
                ],
            ),
            "demo2": "CREATE TABLE neon (name TEXT);\nCREATE TABLE watson (name TEXT);\n"
                     "INSERT INTO neon VALUES ('V'), ('Judy'), ('Jackie');\n"
                     "INSERT INTO watson VALUES ('Judy'), ('Rogue');\n\n"
                     "SELECT 'neon' AS source, name FROM neon\n"
                     "UNION ALL\nSELECT 'watson', name FROM watson\nORDER BY source, name;",
            "tip": "集合运算的列名取自第一条 SELECT。想统一列名，就在第一条查询里写 AS，"
                   "后面的查询不需要重复别名。",
            "warn": "UNION 会去重，把两笔金额相同但业务上独立的记录合并成一条。"
                    "统计流水、日志这类允许重复的数据时，必须用 UNION ALL。",
            "quiz": (
                "neon 有 V、Judy、Jackie，watson 有 Judy、Rogue，"
                "SELECT name FROM neon EXCEPT SELECT name FROM watson 返回？",
                ["V, Jackie", "Judy", "Rogue", "V, Judy, Jackie, Rogue"],
                0,
                "EXCEPT 保留在左表但不在右表的行，Judy 两边都有被排除，剩下 V 和 Jackie。",
            ),
            "ex": exercise(
                "两区玩家并集",
                "把 neon 与 watson 两张表的 name 合并，去重后按字母升序输出。",
                "CREATE TABLE neon (name TEXT);\nCREATE TABLE watson (name TEXT);\n"
                "INSERT INTO neon VALUES ('V'), ('Judy'), ('Jackie');\n"
                "INSERT INTO watson VALUES ('Judy'), ('Rogue');\n\n-- 在这里写查询\n",
                "SELECT name FROM neon UNION SELECT name FROM watson ORDER BY name;",
                [
                    "assert columns == ['name'], columns",
                    "assert rows == [['Jackie'], ['Judy'], ['Rogue'], ['V']], rows",
                    "assert len(rows) == 4, rows",
                ],
                "CREATE TABLE neon (name TEXT);\nCREATE TABLE watson (name TEXT);\n"
                "INSERT INTO neon VALUES ('V'), ('Judy'), ('Jackie');\n"
                "INSERT INTO watson VALUES ('Judy'), ('Rogue');\n\n"
                "SELECT name FROM neon\nUNION\nSELECT name FROM watson\nORDER BY name;\n",
                110,
            ),
        }),
        mk({
            "id": "sql20", "order": 519, "chapter": 52, "chapterName": CORE,
            "title": "把查询存起来", "subtitle": "视图 VIEW", "xp": 100,
            "head": "视图是一层命名好的查询",
            "paras": [
                "视图（VIEW）本质上是一条被命名并保存的 SELECT 语句，本身不存数据，每次查询视图时"
                "数据库都会重新执行它背后的 SQL。创建语法是 CREATE VIEW 视图名 AS SELECT ...。"
                "例如把「每位玩家的订单数与总额」这条聚合查询保存成 player_totals，之后就可以像查"
                "普通表一样 SELECT * FROM player_totals WHERE total >= 100。视图让复杂查询有了名字，"
                "复用和维护都更方便。",

                "视图的最大价值是封装复杂度与统一口径。多个报表都要算「有效订单金额」，如果每个地方"
                "各写一遍，规则一改就要全项目搜索替换；把它定义成视图，所有调用方自动跟着变，口径"
                "天然一致。视图还能起到权限隔离的作用：只把视图授权给分析人员，让他们看不到底表的"
                "敏感列，例如手机号、身份证号。这是一种轻量级的行级与列级安全手段。",

                "视图也有代价。它不存数据，每次查询都要重新计算，如果底层是复杂的三表聚合，"
                "视图会被反复执行，性能可能不如物化表。视图也不能带参数，想按玩家筛选只能在外部加 "
                "WHERE。SQLite 的视图默认是只读的，不能直接对视图 INSERT 或 UPDATE，需要写 INSTEAD OF "
                "触发器才能支持写入，这一点和某些数据库不同。另外，视图依赖底表结构，底表删列会导致"
                "视图查询报错，上线前要检查依赖关系。",

                "使用视图的经验是：把稳定的、多处复用的查询抽成视图，把一次性的探索查询留在脚本里。"
                "视图命名建议加前缀或后缀，例如 v_player_totals，和物理表区分开。视图里不要写 ORDER BY，"
                "因为外层的排序需求各不相同，内层排序既无意义也可能被优化器忽略。如果视图逻辑变复杂，"
                "可以在内部继续使用 CTE，但要注意嵌套层级，太深的视图链会让人难以追查数据来源。",

                "视图和表的另一个区别体现在结构变更上。给底表加一列，视图通常不受影响，因为它只"
                "选择自己需要的列；给底表删列或改名，视图会在下次查询时报错，但创建时不会校验，"
                "这类「延迟失败」很容易在上线后才暴露。做表结构迁移时，先查 sqlite_master 里所有"
                "视图的定义，确认没有依赖被删的列，再执行变更。把视图当代码看待，纳入版本管理和"
                "评审流程，是团队协作里更稳妥的做法。",

                "视图还能嵌套：在现有视图上再建视图。少量嵌套能提升复用，层级过深则会让执行计划"
                "变得难以分析，排查问题时需要一层层展开。经验上超过两层就考虑用 CTE 重写，"
                "把逻辑集中在一处而不是分散在多个视图里。视图是工具，不是架构，它的价值在于让"
                "重复的查询有统一出口，而不是把所有查询都包装成视图。保持克制，才能让视图真正"
                "降低维护成本。",

                "视图还能配合权限控制做数据隔离。SQLite 本身没有细粒度授权，但把数据同步到服务端"
                "数据库后，可以只给分析账号授予视图的 SELECT 权限，而不给底表权限，这样他们既能"
                "做统计又看不到原始敏感字段。视图里还可以预先过滤掉软删除的行，让所有调用方"
                "自动忽略 deleted_at 不为空的数据，避免每个报表都重复写过滤条件。把这类「公共"
                "约束」沉淀到视图，是让数据口径长期一致的低成本手段。",
            ],            "demo": "CREATE TABLE orders (id INTEGER PRIMARY KEY, player TEXT, amount INTEGER);\n"
                    "INSERT INTO orders VALUES (1, 'V', 100), (2, 'V', 50), (3, 'Judy', 80);\n\n"
                    "CREATE VIEW player_totals AS\n"
                    "SELECT player, COUNT(*) AS orders, SUM(amount) AS total\n"
                    "FROM orders\nGROUP BY player;\n\n"
                    "SELECT player, orders, total FROM player_totals ORDER BY total DESC;",
            "mid": table(
                ["特性", "视图", "表"],
                [
                    ["存储数据", "否，只存查询", "是"],
                    ["能否带参数", "否", "不适用"],
                    ["能否直接写入", "SQLite 默认只读", "可以"],
                    ["典型用途", "封装口径、权限隔离", "持久化业务数据"],
                ],
            ),
            "demo2": "CREATE TABLE orders (id INTEGER PRIMARY KEY, player TEXT, amount INTEGER);\n"
                     "INSERT INTO orders VALUES (1, 'V', 100), (2, 'V', 50), (3, 'Judy', 80);\n\n"
                     "CREATE VIEW player_totals AS\n"
                     "SELECT player, COUNT(*) AS orders, SUM(amount) AS total\n"
                     "FROM orders\nGROUP BY player;\n\n"
                     "SELECT player, total FROM player_totals WHERE total >= 100 ORDER BY total DESC;",
            "tip": "视图名加 v_ 前缀，和物理表区分。查看现有视图用 "
                   "SELECT name FROM sqlite_master WHERE type = 'view'。",
            "warn": "视图不缓存结果，每次查询都重新执行底层 SQL。高频访问的复杂视图应考虑物化成表并定时刷新，"
                    "否则可能成为性能瓶颈。",
            "quiz": (
                "关于视图，下列说法正确的是？",
                ["视图会物理存储查询结果", "视图本质是保存下来的 SELECT 语句", "视图可以带参数", "视图一定能更新"],
                1,
                "视图只保存查询定义，不存数据，每次访问时重新执行，因此也不支持参数。",
            ),
            "ex": exercise(
                "建立消费视图",
                "创建视图 player_totals，包含每位玩家的 player、订单数 orders、总额 total；"
                "然后从视图中选出 total 大于等于 100 的玩家，按 total 降序。",
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, player TEXT, amount INTEGER);\n"
                "INSERT INTO orders VALUES (1, 'V', 100), (2, 'V', 50), (3, 'Judy', 80);\n\n"
                "-- 在这里写 CREATE VIEW 与查询\n",
                "CREATE VIEW player_totals AS SELECT player, COUNT(*) AS orders, SUM(amount) AS total "
                "FROM orders GROUP BY player; SELECT player, total FROM player_totals WHERE total >= 100 ORDER BY total DESC;",
                [
                    "assert columns == ['player', 'total'], columns",
                    "assert rows == [['V', 150]], rows",
                    "assert len(rows) == 1, rows",
                ],
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, player TEXT, amount INTEGER);\n"
                "INSERT INTO orders VALUES (1, 'V', 100), (2, 'V', 50), (3, 'Judy', 80);\n\n"
                "CREATE VIEW player_totals AS\n"
                "SELECT player, COUNT(*) AS orders, SUM(amount) AS total\n"
                "FROM orders\nGROUP BY player;\n\n"
                "SELECT player, total FROM player_totals WHERE total >= 100 ORDER BY total DESC;\n",
                120,
            ),
        }),
    ]


def advanced_21_25():
    return [
        mk({
            "id": "sql21", "order": 520, "chapter": 53, "chapterName": ADVANCED,
            "title": "给查询起名字", "subtitle": "CTE（WITH）", "xp": 100,
            "head": "把中间结果写成一段",
            "paras": [
                "CTE（Common Table Expression，公共表表达式）用 WITH 开头，把一段查询命名后供后面的"
                "语句引用。写法是 WITH 名字 AS (SELECT ...) SELECT ... FROM 名字。它和派生表的作用类似，"
                "但结构更清晰：所有中间结果集中在开头定义，主查询读起来像在组合几个有名字的积木，"
                "而不是层层嵌套的括号。复杂报表用 CTE 重写后，可读性往往提升一个档次。",

                "CTE 可以是多个，用逗号分隔，后面的 CTE 能引用前面的 CTE。这让「分步计算」成为可能："
                "第一步算出每人总额，第二步算出全局平均，第三步挑出高于平均的人。每一步只做一件事，"
                "出错时容易定位是哪一层算错。CTE 默认只在当前语句内有效，不会像视图那样长期存在于"
                "数据库中，所以特别适合一次性的复杂分析。它也不会物化，多数情况下会被优化器内联，"
                "性能与直接写子查询接近。",

                "递归 CTE 需要加 RECURSIVE 关键字，结构由「锚点查询」和「递归查询」用 UNION ALL 连接。"
                "典型的例子是生成数字序列：WITH RECURSIVE seq(n) AS (SELECT 1 UNION ALL SELECT n + 1 "
                "FROM seq WHERE n < 5) SELECT n FROM seq。锚点提供第一行 1，递归部分不断加 1 直到条件"
                "不成立。生成日期序列、展开组织架构树、计算层级 BOM 都用这个套路。写递归时一定要有"
                "终止条件，否则会无限循环直到触发资源限制。",

                "CTE 的命名要能表达业务含义，例如 paid_orders、player_totals、monthly_sales，"
                "不要用 t1、t2 这种名字，否则读代码的人还得回头对照。多个 CTE 之间保持单向依赖，"
                "避免互相引用造成循环。如果一段 CTE 被多条语句复用、且逻辑稳定，可以升级成视图；"
                "如果只在一个报表里用一次，留在 WITH 里更合适。判断标准是复用范围与稳定性，"
                "而不是「哪种写法更高级」。",

                "CTE 还有一个常被忽略的好处：可以打断「重复计算」。如果一条查询里多次用到同一个"
                "聚合结果，写成子查询会让数据库执行两遍，写成 CTE 至少语义上只定义一次，"
                "可读性和维护性都更好。SQLite 目前不会主动物化 CTE，复杂场景下仍可能重复执行，"
                "但把逻辑集中在一处，依然让后续优化（例如改成临时表或视图）变得容易。"
                "先让结构清晰，再根据执行计划决定是否物化，是更稳妥的优化顺序。",

                "写多个 CTE 时，建议按依赖顺序从上到下排列，被引用的放前面，最终查询放最后。"
                "每个 CTE 只负责一个动作：过滤、聚合、排名、分层，不要在一个 CTE 里塞进三种逻辑。"
                "如果发现某个 CTE 超过二十行，通常说明它可以再拆。可读性不是玄学，"
                "而是让下一个人能在五分钟内看懂数据从哪来、经过了什么变换、最终输出了什么。"
                "这种结构化的写法，在排查数字对不上的问题时尤其有价值。",

                "递归 CTE 还有几个实际用途值得记住。生成连续日期可以用序列加 DATE 修饰符，"
                "补齐没有数据的空日；展开层级结构可以用 parent_id 自连接，配合 depth 字段标记层级，"
                "再加 WHERE depth < 5 防止无限递归；拆分逗号分隔的字符串可以用递归逐个截取。"
                "这些技巧的共同点是「用递归代替应用层循环」，把逻辑留在数据库里，减少数据传输。"
                "不过递归查询的性能随层数增长，深层级场景要评估是否该在应用层缓存结果。",
            ],
            "demo": "CREATE TABLE orders (id INTEGER PRIMARY KEY, player TEXT, amount INTEGER);\n"
                    "INSERT INTO orders VALUES (1, 'V', 100), (2, 'V', 50), (3, 'Judy', 80), (4, 'Jackie', 120);\n\n"
                    "WITH totals AS (\n"
                    "  SELECT player, SUM(amount) AS total\n"
                    "  FROM orders\n"
                    "  GROUP BY player\n"
                    ")\n"
                    "SELECT player, total\nFROM totals\nWHERE total > 90\nORDER BY total DESC;",
            "mid": table(
                ["要素", "作用", "示例"],
                [
                    ["WITH 名字 AS", "定义一个 CTE", "WITH totals AS (...)"],
                    ["多个 CTE", "逗号分隔，后者可引用前者", "WITH a AS (...), b AS (...)"],
                    ["RECURSIVE", "启用递归", "WITH RECURSIVE seq(n) AS (...)"],
                    ["引用", "像表一样使用", "SELECT * FROM totals"],
                ],
            ),
            "demo2": "WITH RECURSIVE seq(n) AS (\n"
                     "  SELECT 1\n"
                     "  UNION ALL\n"
                     "  SELECT n + 1 FROM seq WHERE n < 5\n"
                     ")\nSELECT n FROM seq;",
            "tip": "CTE 只在当前语句内有效，作用域结束后名字就消失。需要长期复用时改写成视图，"
                   "需要跨语句传递结果时用临时表。",
            "warn": "递归 CTE 必须有终止条件，否则会一直递归下去。调试时先把上限调小，"
                    "确认逻辑正确后再放开，别一上来就生成一百万行。",
            "quiz": (
                "WITH RECURSIVE seq(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM seq WHERE n < 5) "
                "会生成几行？",
                ["4 行", "5 行", "6 行", "无限行"],
                1,
                "从 1 开始，每次加 1，直到 n < 5 不成立，最终得到 1 到 5 共 5 行。",
            ),
            "ex": exercise(
                "高于平均的玩家",
                "用 CTE 先算出每位玩家的总额，再筛选出总额大于 90 的玩家，输出 player 与 total，"
                "按 total 降序。",
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, player TEXT, amount INTEGER);\n"
                "INSERT INTO orders VALUES (1, 'V', 100), (2, 'V', 50), (3, 'Judy', 80), (4, 'Jackie', 120);\n\n"
                "-- 在这里写 WITH 查询\n",
                "WITH totals AS (SELECT player, SUM(amount) AS total FROM orders GROUP BY player) "
                "SELECT player, total FROM totals WHERE total > 90 ORDER BY total DESC;",
                [
                    "assert columns == ['player', 'total'], columns",
                    "assert rows == [['V', 150], ['Jackie', 120]], rows",
                    "assert len(rows) == 2, rows",
                ],
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, player TEXT, amount INTEGER);\n"
                "INSERT INTO orders VALUES (1, 'V', 100), (2, 'V', 50), (3, 'Judy', 80), (4, 'Jackie', 120);\n\n"
                "WITH totals AS (\n"
                "  SELECT player, SUM(amount) AS total\n"
                "  FROM orders\n"
                "  GROUP BY player\n"
                ")\n"
                "SELECT player, total\nFROM totals\nWHERE total > 90\nORDER BY total DESC;\n",
                120,
            ),
        }),
        mk({
            "id": "sql22", "order": 521, "chapter": 53, "chapterName": ADVANCED,
            "title": "给行编号", "subtitle": "窗口函数 ROW_NUMBER / RANK", "xp": 110,
            "head": "不折叠行的聚合",
            "paras": [
                "窗口函数在保留原行的同时计算聚合或排名，语法是 函数() OVER (PARTITION BY 分组列 "
                "ORDER BY 排序列)。它和 GROUP BY 的区别很关键：GROUP BY 把多行压成一行，窗口函数"
                "则给每一行附加一个计算结果，行数不变。所以「给每位玩家的比赛按分数排名」这种需求，"
                "用窗口函数一行就能完成，用 GROUP BY 反而要绕一大圈。",

                "ROW_NUMBER、RANK、DENSE_RANK 都用来排名，差别在并列时怎么处理。ROW_NUMBER 严格按"
                "顺序编号，即使分数相同也编成 1、2、3，不会有并列；RANK 遇到并列会给相同名次，"
                "但跳过后续序号，例如 1、1、3；DENSE_RANK 同样并列同名次，但不跳号，例如 1、1、2。"
                "排行榜用 RANK 更符合直觉，取每组第一名用 ROW_NUMBER 更方便，选哪个取决于业务对"
                "并列的定义。",

                "PARTITION BY 决定分组范围，省略时整张表是一个窗口。窗口函数执行在 WHERE 和 "
                "GROUP BY 之后、ORDER BY 之前，所以不能写在 WHERE 里，必须套一层子查询或 CTE，"
                "在外层筛选排名。常见写法是 WITH ranked AS (SELECT ..., ROW_NUMBER() OVER (...) AS rn "
                "FROM ...) SELECT * FROM ranked WHERE rn = 1。这个模式几乎能解决所有「每组取前 N 条」"
                "的问题，是窗口函数最实用的套路。",

                "窗口函数还可以不写 ORDER BY，此时 OVER (PARTITION BY player) 表示在整个分组上算"
                "聚合，每一行都得到相同的组内合计或平均值。用它算占比特别方便：score * 100.0 / "
                "SUM(score) OVER (PARTITION BY player) 得到每场比赛在该玩家总分中的百分比。"
                "注意没有 ORDER BY 时默认窗口是整组，加了 ORDER BY 默认变成「从第一行到当前行」，"
                "结果会变成累计值，这个差异一定要分清，否则占比会算成累进比例。",

                "窗口函数还能和 CASE 组合做「组内分档」。例如 OVER (PARTITION BY player ORDER BY "
                "score DESC) 配合 ROW_NUMBER，再在外层用 CASE 把前三名标成主力、其余标成替补。"
                "这种写法比多次自连接清晰得多，也不容易漏行。要注意窗口函数的别名同样不能在"
                "同层 WHERE 里引用，必须套一层。理解「窗口在 SELECT 阶段计算」，就能明白为什么"
                "过滤排名要放到外层，而不是写在窗口定义旁边。",

                "最后对比一下 ROW_NUMBER 和 GROUP BY 的适用边界。要「每组一行汇总」用 GROUP BY；"
                "要「每行附加组内信息」用窗口函数；要「每组取前 N 行」用 ROW_NUMBER 加外层过滤。"
                "三者不是替代关系，而是三种不同的输出形态。判断标准是结果需要多少行："
                "行数变少用分组，行数不变用窗口，需要截取部分行用排名加过滤。把这个判断练成"
                "条件反射，遇到「每组第一名」「每人类内占比」这类问题时，就能立刻选对工具。",

                "排名还有一个常见需求是「取前百分之十」。SQLite 没有 PERCENT_RANK 之外的直接写法，"
                "但可以用 NTILE(10) OVER (ORDER BY score DESC) 把结果分成十桶，再取第一桶，"
                "近似得到前百分之十。NTILE 在行数不能整除时会尽量均分，桶大小可能相差一，"
                "业务上通常可以接受。如果要严格按分数阈值取，就先用子查询算出分位数，"
                "再筛选 score >= 阈值，两种做法各有适用场景。",

                "还要提醒一个常见误解：窗口函数不会改变行数，但会影响排序结果。多个窗口函数"
                "写在同一条 SELECT 里时，每个 OVER 子句可以有自己的 PARTITION BY 和 ORDER BY，"
                "互不干扰。例如同时按全局分数排名和按玩家内排名，就写两个不同的 OVER，"
                "然后在 ORDER BY 里决定最终展示顺序。理解了这一点，就能在一行里同时输出"
                "「总榜名次」和「组内名次」两类指标，而不必写两条查询再拼接。",
            ],
            "demo": "CREATE TABLE matches (id INTEGER PRIMARY KEY, player TEXT, score INTEGER);\n"
                    "INSERT INTO matches VALUES (1, 'V', 90), (2, 'Judy', 90), (3, 'Jackie', 80), (4, 'Rogue', 70);\n\n"
                    "SELECT player, score,\n"
                    "       ROW_NUMBER() OVER (ORDER BY score DESC) AS rn,\n"
                    "       RANK() OVER (ORDER BY score DESC) AS rnk,\n"
                    "       DENSE_RANK() OVER (ORDER BY score DESC) AS dense\n"
                    "FROM matches;",
            "mid": table(
                ["函数", "并列时", "示例结果"],
                [
                    ["ROW_NUMBER", "不并列，强制编号", "1, 2, 3, 4"],
                    ["RANK", "并列同名次，跳号", "1, 1, 3, 4"],
                    ["DENSE_RANK", "并列同名次，不跳号", "1, 1, 2, 3"],
                    ["NTILE(n)", "分成 n 桶", "按顺序均分"],
                ],
            ),
            "demo2": "CREATE TABLE matches (id INTEGER PRIMARY KEY, player TEXT, score INTEGER);\n"
                     "INSERT INTO matches VALUES (1, 'V', 90), (2, 'V', 80), (3, 'Judy', 90),\n"
                     "  (4, 'Judy', 70), (5, 'Jackie', 60);\n\n"
                     "SELECT player, score,\n"
                     "       ROW_NUMBER() OVER (PARTITION BY player ORDER BY score DESC) AS rn\n"
                     "FROM matches\nORDER BY player, rn;",
            "tip": "需要「每组第一名」时用 ROW_NUMBER 加外层 rn = 1，比 GROUP BY 加 MAX 更通用，"
                   "因为它能带回整行的其他列。",
            "warn": "窗口函数不能直接写在 WHERE 里，会报 misuse of window function。"
                    "必须先用 CTE 或子查询算出排名列，再在外层过滤。",
            "quiz": (
                "分数为 90、90、80 时，RANK() 给出的名次是？",
                ["1, 2, 3", "1, 1, 2", "1, 1, 3", "2, 2, 3"],
                2,
                "RANK 遇到并列给相同名次，但会跳过被占用的序号，所以是 1、1、3。",
            ),
            "ex": exercise(
                "玩家内排名",
                "对 matches 表按 player 分区、score 降序编号，输出 player、score、rn，"
                "按 player 升序、rn 升序。",
                "CREATE TABLE matches (id INTEGER PRIMARY KEY, player TEXT, score INTEGER);\n"
                "INSERT INTO matches VALUES (1, 'V', 90), (2, 'V', 80), (3, 'Judy', 90),\n"
                "  (4, 'Judy', 70), (5, 'Jackie', 60);\n\n-- 在这里写查询\n",
                "SELECT player, score, ROW_NUMBER() OVER (PARTITION BY player ORDER BY score DESC) AS rn "
                "FROM matches ORDER BY player, rn;",
                [
                    "assert columns == ['player', 'score', 'rn'], columns",
                    "assert rows == [['Jackie', 60, 1], ['Judy', 90, 1], ['Judy', 70, 2], "
                    "['V', 90, 1], ['V', 80, 2]], rows",
                    "assert len(rows) == 5, rows",
                ],
                "CREATE TABLE matches (id INTEGER PRIMARY KEY, player TEXT, score INTEGER);\n"
                "INSERT INTO matches VALUES (1, 'V', 90), (2, 'V', 80), (3, 'Judy', 90),\n"
                "  (4, 'Judy', 70), (5, 'Jackie', 60);\n\n"
                "SELECT player, score,\n"
                "       ROW_NUMBER() OVER (PARTITION BY player ORDER BY score DESC) AS rn\n"
                "FROM matches\nORDER BY player, rn;\n",
                120,
            ),
        }),
        mk({
            "id": "sql23", "order": 522, "chapter": 53, "chapterName": ADVANCED,
            "title": "累计与滑动", "subtitle": "窗口聚合与滑动窗口", "xp": 110,
            "head": "让每一行看到一段区间",
            "paras": [
                "窗口聚合把 SUM、AVG、COUNT、MIN、MAX 等函数作用在一个「窗口」上，而不是整张表。"
                "OVER (PARTITION BY player) 表示按玩家分组，每组内所有行共享同一个合计值；"
                "再加上 ORDER BY 后，窗口默认变成「从组内第一行到当前行」，得到的是累计值。"
                "这两种形态用途不同：前者用来算占比，后者用来算累计增长，写之前先想清楚要哪一种。",

                "滑动窗口用 ROWS BETWEEN 起始 AND 结束 精确指定范围。常见写法有 ROWS BETWEEN "
                "1 PRECEDING AND CURRENT ROW 表示「前一行到当前行」，用来算两日移动平均；"
                "ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW 表示从头累计；"
                "ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING 表示前后各两行的居中窗口。"
                "边界可以组合 PRECEDING、FOLLOWING、CURRENT ROW、UNBOUNDED，灵活度很高。",

                "LAG 和 LEAD 用来取前一行或后一行的值，做环比、同比、差值非常方便。"
                "LAG(v) OVER (ORDER BY d) 取上一行的 v，v - LAG(v) OVER (ORDER BY d) 得到与上一行的差，"
                "第一天没有上一行所以结果是 NULL，这符合业务直觉。LEAD 方向相反，取下一行。"
                "两者都可以带偏移量和默认值，例如 LAG(v, 7, 0) 取七天前的值，缺失时用 0 代替，"
                "避免结果里出现 NULL 影响后续计算。",

                "窗口函数的性能取决于排序与分区。PARTITION BY 和 ORDER BY 的列如果有索引，"
                "数据库可以避免额外排序；没有索引时会在内存或磁盘上建临时 B 树，数据量大时开销明显。"
                "另外，窗口函数在 WHERE 之后执行，想先过滤再开窗，就把过滤条件写进子查询，"
                "而不是指望窗口自己跳过不需要的行。理解执行顺序，才能写出既正确又高效的窗口查询。",

                "滑动窗口的典型业务场景是指标平滑。原始日活数据波动大，直接看曲线很难判断趋势，"
                "用 ROWS BETWEEN 6 PRECEDING AND CURRENT ROW 算七日均值，曲线会平滑很多，"
                "异常点也更容易识别。另一类是留存分析：对每个注册日，统计之后第 1 天、第 7 天"
                "仍有行为的用户数，需要按用户分组、按日期排序，再用 LEAD 取后续日期的状态。"
                "这些问题用普通聚合很难表达，窗口函数几乎是唯一清晰的解法。",

                "使用滑动窗口要特别注意分区与排序的组合。PARTITION BY 缺失时，窗口会跨越整个结果集，"
                "不同玩家的数据混在一起，累计值就失去意义。ORDER BY 缺失时，窗口是整组而非累计，"
                "滑动范围也无从谈起。两者都写清楚，再用 ROWS BETWEEN 精确限定，结果才可控。"
                "写完先用小数据集手算前两三行，和查询结果对照，比直接上大表调试快得多，"
                "也更容易发现边界值（第一行、最后一行）处理是否符合业务预期。",

                "窗口帧还有 RANGE 和 GROUPS 两种模式。ROWS 按物理行数计算，RANGE 按排序值的范围计算，"
                "例如 RANGE BETWEEN 7 PRECEDING AND CURRENT ROW 表示「当前值减 7 到当前值」的区间，"
                "遇到日期时更符合「最近七天」的业务语义。GROUPS 按并列值的组数计算，用得较少。"
                "默认帧在有无 ORDER BY 时不同，写复杂分析时建议总是显式写出 ROWS 或 RANGE，"
                "避免因为默认值变化导致结果悄悄改变。",

                "最后把几种窗口函数按用途归个类，方便日后查阅。排名类：ROW_NUMBER、RANK、"
                "DENSE_RANK、NTILE；偏移类：LAG、LEAD、FIRST_VALUE、LAST_VALUE、NTH_VALUE；"
                "聚合类：SUM、AVG、COUNT、MIN、MAX 加 OVER。这三类的共同点是都保留原始行，"
                "区别只在于返回什么。写分析查询时先想清楚要「名次」「前后值」还是「区间汇总」，"
                "再挑对应函数，比在文档里从头翻要快得多。还有一点要注意：窗口函数的 ORDER BY 只决定窗口内的顺序，不决定最终结果的顺序，想看排名还得在外层再写一次 ORDER BY。这个细节在调试排行报表时经常被忽略，结果数字对但顺序乱，容易误判成计算错误。",
            ],
            "demo": "CREATE TABLE daily (d TEXT, v INTEGER);\n"
                    "INSERT INTO daily VALUES ('d1', 10), ('d2', 20), ('d3', 30), ('d4', 40), ('d5', 50);\n\n"
                    "SELECT d, v,\n"
                    "       SUM(v) OVER (ORDER BY d ROWS BETWEEN 1 PRECEDING AND CURRENT ROW) AS rolling2,\n"
                    "       SUM(v) OVER (ORDER BY d ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running\n"
                    "FROM daily;",
            "mid": table(
                ["窗口写法", "范围", "典型用途"],
                [
                    ["PARTITION BY player", "整个分组", "算占比、组内合计"],
                    ["ORDER BY d", "从头到当前行", "累计值"],
                    ["1 PRECEDING AND CURRENT ROW", "前一行到当前行", "移动平均"],
                    ["UNBOUNDED PRECEDING", "从第一行开始", "累计求和"],
                ],
            ),
            "demo2": "CREATE TABLE daily (d TEXT, v INTEGER);\n"
                     "INSERT INTO daily VALUES ('d1', 10), ('d2', 20), ('d3', 30), ('d4', 40), ('d5', 50);\n\n"
                     "SELECT d, v,\n"
                     "       LAG(v) OVER (ORDER BY d) AS prev_v,\n"
                     "       v - LAG(v) OVER (ORDER BY d) AS diff,\n"
                     "       LEAD(v) OVER (ORDER BY d) AS next_v\n"
                     "FROM daily;",
            "tip": "算占比时用 OVER (PARTITION BY ...) 不带 ORDER BY，窗口是整组；"
                   "一旦加了 ORDER BY，默认就变成累计窗口，占比会算错。",
            "warn": "窗口函数的结果不能直接用于同一层的 WHERE。需要筛选累计值或排名时，"
                    "必须套一层子查询或 CTE，在外层加条件。",
            "quiz": (
                "SUM(v) OVER (ORDER BY d ROWS BETWEEN 1 PRECEDING AND CURRENT ROW) 计算的是？",
                ["从头到当前行的累计和", "当前行与前一行的和", "当前行与后一行的和", "整组的总和"],
                1,
                "窗口范围是前一行到当前行，共两行，因此得到两行滑动合计。",
            ),
            "ex": exercise(
                "两日累计",
                "对 daily 表按 d 升序计算两行滑动合计，输出 d、v、rolling2。",
                "CREATE TABLE daily (d TEXT, v INTEGER);\n"
                "INSERT INTO daily VALUES ('d1', 10), ('d2', 20), ('d3', 30), ('d4', 40), ('d5', 50);\n\n"
                "-- 在这里写查询\n",
                "SELECT d, v, SUM(v) OVER (ORDER BY d ROWS BETWEEN 1 PRECEDING AND CURRENT ROW) AS rolling2 FROM daily;",
                [
                    "assert columns == ['d', 'v', 'rolling2'], columns",
                    "assert rows == [['d1', 10, 10], ['d2', 20, 30], ['d3', 30, 50], "
                    "['d4', 40, 70], ['d5', 50, 90]], rows",
                    "assert len(rows) == 5, rows",
                ],
                "CREATE TABLE daily (d TEXT, v INTEGER);\n"
                "INSERT INTO daily VALUES ('d1', 10), ('d2', 20), ('d3', 30), ('d4', 40), ('d5', 50);\n\n"
                "SELECT d, v,\n"
                "       SUM(v) OVER (ORDER BY d ROWS BETWEEN 1 PRECEDING AND CURRENT ROW) AS rolling2\n"
                "FROM daily;\n",
                120,
            ),
        }),
        mk({
            "id": "sql24", "order": 523, "chapter": 53, "chapterName": ADVANCED,
            "title": "要么全成，要么全退", "subtitle": "事务 BEGIN / COMMIT / ROLLBACK", "xp": 110,
            "head": "事务保证一组操作的整体性",
            "paras": [
                "事务把多条写操作打包成一个原子单元：要么全部生效，要么全部不生效。最经典的例子是"
                "转账，从 A 扣钱和给 B 加钱必须一起成功，否则钱会凭空消失或凭空出现。SQLite 的写法是"
                "BEGIN 开启事务，COMMIT 提交，ROLLBACK 回滚。事务内的语句执行后并不立即对其他人可见，"
                "提交之后才真正落盘。",

                "事务满足 ACID 四个特性：原子性保证全成或全退；一致性保证约束不被破坏；隔离性保证"
                "并发事务互不干扰；持久性保证提交后的数据不会因为断电丢失。SQLite 默认是自动提交模式，"
                "每条语句自成一个事务，所以平时写单条 INSERT 不需要显式 BEGIN。一旦有多条写操作存在"
                "依赖关系，就必须手动开启事务，否则中途失败会留下半成品数据。",

                "ROLLBACK 会撤销事务内所有未提交的改动，包括 INSERT、UPDATE、DELETE 和建表。"
                "SAVEPOINT 可以在事务内部打一个标记，ROLLBACK TO 只回滚到标记处，之前的部分保留，"
                "适合做「部分失败不影响整体」的分段操作。RELEASE 释放标记。嵌套事务在 SQLite 里"
                "没有原生支持，但可以用多层 SAVEPOINT 模拟。事务越短越好，长时间持有写锁会阻塞"
                "其他连接，尤其在并发场景下要尽快提交。",

                "课程运行器基于 Python 的 sqlite3 模块，它会在 INSERT、UPDATE、DELETE 之前自动开启"
                "一个隐式事务。所以如果脚本先写了数据、再写 BEGIN，就会报「cannot start a transaction "
                "within a transaction」，因为此时已经有一个未结束的事务。解决办法有两个：把 BEGIN "
                "放到所有写操作之前，或者在 BEGIN 之前补一条 COMMIT 提交掉隐式事务。示例采用前者，"
                "先开事务再插入，逻辑最清楚。理解这个行为，能避免在练习时被看似莫名其妙的报错卡住。",

                "隔离级别也值得了解。SQLite 默认使用串行化隔离，写事务之间互斥，读操作不会被阻塞，"
                "但同一时间只允许一个写者。这对移动端和单机应用足够，但在高并发服务端就显得不够用，"
                "通常要换成 PostgreSQL 或 MySQL。其他数据库提供读已提交、可重复读等不同级别，"
                "级别越高一致性越强、并发度越低。选择时要结合业务：转账要求强一致，"
                "统计报表可以接受稍旧的快照。理解隔离级别的代价，才能做出合理的取舍。",

                "最后提醒：事务不是万能的。它保证数据库内部的一致性，却管不了外部系统。"
                "如果事务里还要发消息、调支付接口，可能出现「数据库提交成功但消息发送失败」的情况，"
                "这类跨系统一致性问题需要补偿机制或最终一致性方案。先把数据库事务用对，"
                "再考虑分布式场景，是新手上路最稳妥的顺序。别在一开始就追求完美的分布式事务，"
                "把单库的原子性写扎实，已经能解决绝大多数问题。",

                "再补充一个语句级与行级触发器的区别。默认 FOR EACH ROW，每一行触发一次；"
                "SQLite 实际上只支持行级触发器，语句级触发器在其他数据库里才有。行级触发器的"
                "性能与受影响行数成正比，批量更新十万行就会触发十万次，写批量导入时要估算这个开销。"
                "如果只是记录「某张表被改过」，用应用层统一记录往往比触发器更轻量。"
                "工具没有绝对好坏，关键是知道它的成本落在哪里。",
            ],
            "demo": "CREATE TABLE accounts (id INTEGER PRIMARY KEY, name TEXT, balance INTEGER);\n"
                    "BEGIN;\n"
                    "INSERT INTO accounts VALUES (1, 'V', 100), (2, 'Judy', 100);\n"
                    "UPDATE accounts SET balance = balance - 30 WHERE id = 1;\n"
                    "UPDATE accounts SET balance = balance + 30 WHERE id = 2;\n"
                    "COMMIT;\n"
                    "SELECT id, name, balance FROM accounts ORDER BY id;",
            "mid": table(
                ["语句", "作用", "结果"],
                [
                    ["BEGIN", "开启事务", "后续语句进入同一事务"],
                    ["COMMIT", "提交", "改动生效并落盘"],
                    ["ROLLBACK", "回滚", "撤销事务内所有改动"],
                    ["SAVEPOINT", "设置保存点", "可部分回滚"],
                ],
            ),
            "demo2": "CREATE TABLE log (id INTEGER PRIMARY KEY, msg TEXT);\n"
                     "BEGIN;\n"
                     "INSERT INTO log VALUES (1, 'start');\n"
                     "SAVEPOINT step1;\n"
                     "INSERT INTO log VALUES (2, 'step1');\n"
                     "ROLLBACK TO step1;\n"
                     "RELEASE step1;\n"
                     "COMMIT;\n"
                     "SELECT id, msg FROM log ORDER BY id;",
            "tip": "事务要尽量短。把网络请求、文件读写等耗时操作放在事务外面，"
                   "只把必须原子完成的数据库写操作包进来。",
            "warn": "忘记 COMMIT 会导致改动没有真正生效；忘记 ROLLBACK 会让失败的事务一直持有锁。"
                    "写脚本时成对出现，BEGIN 之后一定要有 COMMIT 或 ROLLBACK。",
            "quiz": (
                "BEGIN 之后执行了 INSERT，然后执行 ROLLBACK，数据会怎样？",
                ["保留", "被撤销", "部分保留", "自动提交"],
                1,
                "ROLLBACK 撤销事务内所有未提交的改动，INSERT 插入的行不会留在表中。",
            ),
            "ex": exercise(
                "原子转账",
                "创建 accounts 表并插入 (1, 'V', 100)、(2, 'Judy', 100)，在事务中把 30 从 1 号转到 2 号，"
                "提交后返回 id、name、balance，按 id 升序。",
                "CREATE TABLE accounts (id INTEGER PRIMARY KEY, name TEXT, balance INTEGER);\n\n"
                "-- 在这里写 BEGIN ... COMMIT 与查询\n",
                "BEGIN; INSERT INTO accounts VALUES (1, 'V', 100), (2, 'Judy', 100); "
                "UPDATE accounts SET balance = balance - 30 WHERE id = 1; "
                "UPDATE accounts SET balance = balance + 30 WHERE id = 2; COMMIT; "
                "SELECT id, name, balance FROM accounts ORDER BY id;",
                [
                    "assert columns == ['id', 'name', 'balance'], columns",
                    "assert rows == [[1, 'V', 70], [2, 'Judy', 130]], rows",
                    "assert len(rows) == 2, rows",
                ],
                "CREATE TABLE accounts (id INTEGER PRIMARY KEY, name TEXT, balance INTEGER);\n\n"
                "BEGIN;\n"
                "INSERT INTO accounts VALUES (1, 'V', 100), (2, 'Judy', 100);\n"
                "UPDATE accounts SET balance = balance - 30 WHERE id = 1;\n"
                "UPDATE accounts SET balance = balance + 30 WHERE id = 2;\n"
                "COMMIT;\n"
                "SELECT id, name, balance FROM accounts ORDER BY id;\n",
                120,
            ),
        }),
        mk({
            "id": "sql25", "order": 524, "chapter": 53, "chapterName": ADVANCED,
            "title": "让查询跑得更快", "subtitle": "索引与 EXPLAIN QUERY PLAN", "xp": 110,
            "head": "索引是数据的目录",
            "paras": [
                "索引是数据库为某一列（或几列）单独维护的有序结构，作用是快速定位行，避免全表扫描。"
                "没有索引时，查 WHERE level = 42 要从第一行读到第 N 行；有了索引，数据库可以在"
                "有序结构里直接跳到目标位置。代价是索引本身占空间，并且每次 INSERT、UPDATE、DELETE "
                "都要同步维护索引，所以索引不是越多越好，而是按查询模式有选择地建。",

                "建索引的语法是 CREATE INDEX 索引名 ON 表名(列名)，复合索引用 CREATE INDEX ... "
                "ON 表名(列一, 列二)。复合索引遵循最左前缀原则：索引 (a, b) 能加速 WHERE a = ? "
                "和 WHERE a = ? AND b = ?，但不能单独加速 WHERE b = ?。所以把选择性高、最常用的列"
                "放在最左边。主键 INTEGER PRIMARY KEY 自带索引，不需要重复创建；UNIQUE 约束也会"
                "自动建索引。索引名建议带表名和列名，例如 idx_orders_status，方便排查和删除。",

                "EXPLAIN QUERY PLAN 是 SQLite 提供的执行计划查看命令，输出一行行 detail，"
                "关键看两种词：SCAN 表示全表扫描，SEARCH 表示使用了索引定位。例如 "
                "SEARCH players USING INDEX idx_players_level (level=?) 说明查询命中了索引；"
                "如果看到 SCAN players，说明没有可用索引或优化器认为全表扫描更划算。"
                "小表上全表扫描可能反而更快，因为索引查找也有开销，所以不要看到 SCAN 就盲目加索引，"
                "要结合数据量和实际耗时判断。",

                "索引失效的常见原因有几种：对列套了函数，例如 WHERE UPPER(name) = 'V'；"
                "使用了前导通配符 LIKE '%son'；列类型与比较值类型不一致导致隐式转换；"
                "复合索引没有遵循最左前缀。另外，ORDER BY 的列如果有索引，可以避免额外排序；"
                "GROUP BY 同理。写查询时保持列「裸用」，把函数作用在常量上而不是列上，"
                "是保护索引最简单的一条纪律。",

                "还有几个实用细节。索引的区分度越高越有效：给性别这种只有两三个取值的列建索引，"
                "查询仍可能返回一半的行，优化器往往宁可直接全表扫描。索引名要唯一，同一张表上"
                "重复建相同定义的索引只会浪费空间。删除索引用 DROP INDEX 索引名，改表结构前"
                "先确认哪些索引会失效。SQLite 还支持部分索引，例如 CREATE INDEX ... WHERE status = "
                "'paid'，只为满足条件的行建索引，体积更小，适合数据分布极不均匀的场景。",

                "最后用一个实验收尾：同一张表、同一条查询，分别在无索引和有索引时执行 "
                "EXPLAIN QUERY PLAN，对比 SCAN 与 SEARCH 的差别。如果条件允许，再插入几万行数据"
                "比较实际耗时，你会直观看到索引的价值。但也要记住，索引不是免费的午餐，"
                "它让读变快的同时让写变慢。真正的优化永远是在读写之间找平衡，而不是"
                "无脑堆索引。理解这个权衡，比记住任何一条优化技巧都重要。",

                "顺便说说索引的维护成本如何估算。每次 INSERT 要往每个索引里插一条记录，"
                "UPDATE 如果改了索引列，等于删一条再插一条，DELETE 同理。一张表有五个索引，"
                "写入开销大约是不建索引时的数倍。写多读少的日志表、流水表，索引要精简；"
                "读多写少的配置表、维度表，可以适当多建。上线后通过慢查询日志持续观察，"
                "比一次性设计更可靠。索引是长期演进的东西，不是建表时拍脑袋决定的。补充一个诊断技巧：把 EXPLAIN QUERY PLAN 的输出贴进代码评审，让审查者一起看是 SCAN 还是 SEARCH，比口头说「我加了索引」有说服力。执行计划是客观证据，也是团队讨论性能时最省时间的共同语言。",
            ],
            "demo": "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT, level INTEGER);\n"
                    "INSERT INTO players VALUES (1, 'V', 66), (2, 'Judy', 42), (3, 'Jackie', 30);\n\n"
                    "EXPLAIN QUERY PLAN\nSELECT * FROM players WHERE level = 42;",
            "mid": table(
                ["命令 / 现象", "含义", "说明"],
                [
                    ["CREATE INDEX", "创建索引", "CREATE INDEX idx ON t(col)"],
                    ["SCAN", "全表扫描", "没有命中索引"],
                    ["SEARCH ... USING INDEX", "索引定位", "命中索引"],
                    ["USING TEMP B-TREE", "临时排序结构", "GROUP BY / ORDER BY 需要"],
                ],
            ),
            "demo2": "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT, level INTEGER);\n"
                     "INSERT INTO players VALUES (1, 'V', 66), (2, 'Judy', 42), (3, 'Jackie', 30);\n"
                     "CREATE INDEX idx_players_level ON players(level);\n\n"
                     "EXPLAIN QUERY PLAN\nSELECT * FROM players WHERE level = 42;",
            "tip": "看完执行计划再决定加不加索引。SCAN 不等于慢，SEARCH 也不等于快，"
                   "要结合表的大小和返回行数判断。",
            "warn": "对列使用函数会让索引失效，例如 WHERE UPPER(name) = 'V'。"
                    "把函数移到常量侧，或建表达式索引，才能继续利用索引。",
            "quiz": (
                "复合索引 (a, b) 能加速下面哪个查询？",
                ["WHERE b = 1", "WHERE a = 1", "WHERE a = 1 AND b = 2", "WHERE a + 1 = 2"],
                1,
                "复合索引遵循最左前缀，单独查 a 可以用，单独查 b 不行；a + 1 这种表达式也不行。",
            ),
            "ex": exercise(
                "给等级建索引",
                "在 players 表的 level 列上创建索引 idx_players_level，然后用 EXPLAIN QUERY PLAN "
                "查看 WHERE level = 42 的执行计划，输出 detail 列。",
                "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT, level INTEGER);\n"
                "INSERT INTO players VALUES (1, 'V', 66), (2, 'Judy', 42), (3, 'Jackie', 30);\n\n"
                "-- 在这里写 CREATE INDEX 与 EXPLAIN QUERY PLAN\n",
                "CREATE INDEX idx_players_level ON players(level); EXPLAIN QUERY PLAN SELECT * FROM players WHERE level = 42;",
                [
                    "assert columns == ['id', 'parent', 'notused', 'detail'], columns",
                    "assert len(rows) == 1, rows",
                    "assert 'idx_players_level' in rows[0][3], rows",
                ],
                "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT, level INTEGER);\n"
                "INSERT INTO players VALUES (1, 'V', 66), (2, 'Judy', 42), (3, 'Jackie', 30);\n\n"
                "CREATE INDEX idx_players_level ON players(level);\n"
                "EXPLAIN QUERY PLAN SELECT * FROM players WHERE level = 42;\n",
                120,
            ),
        }),
    ]


def advanced_26_30():
    return [
        mk({
            "id": "sql26", "order": 525, "chapter": 53, "chapterName": ADVANCED,
            "title": "让数据库自动记账", "subtitle": "触发器 TRIGGER", "xp": 120,
            "head": "在写入发生时自动执行",
            "paras": [
                "触发器（TRIGGER）是一段绑定在表上的逻辑，当指定的事件发生时由数据库自动执行。"
                "事件可以是 INSERT、UPDATE 或 DELETE，时机可以是 BEFORE 或 AFTER，粒度可以是"
                "每一行（FOR EACH ROW）或每条语句。典型用途包括：写审计日志、维护汇总表、"
                "自动填充时间戳、在删除前做校验。触发器把「必须一起发生」的副作用交给数据库，"
                "应用层即使漏写也不会留下不一致的数据。",

                "创建语法是 CREATE TRIGGER 名字 AFTER INSERT ON 表名 BEGIN 若干语句 END。"
                "触发器体内可以用 NEW 引用新行、OLD 引用旧行：INSERT 触发器只有 NEW，DELETE 只有 OLD，"
                "UPDATE 两者都有。例如 AFTER UPDATE ON players 时，NEW.level 是修改后的等级，"
                "OLD.level 是修改前的等级，把两者的差值写进流水表，就得到了完整的变更历史。"
                "WHEN 子句可以加额外条件，例如只在等级真的变化时才记录。",

                "触发器也有明确的代价。它隐式执行，调试时不容易发现逻辑从哪里来；一个表上的多个"
                "触发器可能互相影响，甚至形成递归；触发器里的错误会让外层语句整体失败。因此触发器"
                "适合做「简单、确定、与业务强绑定」的副作用，不适合承载复杂业务流程。团队里应该"
                "有触发器清单，记录每个触发器的用途和影响范围，避免多年后没人敢删也不敢改。",

                "本课程的判题运行器按分号切分语句，而触发器体内的语句也必须用分号分隔，切分后"
                "无法还原成一条完整的 CREATE TRIGGER。所以下面把触发器定义作为只读参考展示，"
                "再用等价的手写语句演示它产生的结果。真实项目里用 sqlite3 命令行或驱动执行"
                "整段脚本不受这个限制。理解触发器的语义比记住某一种执行方式更重要，"
                "本例的审计表结构和效果，就是触发器最典型的应用场景。",

                "触发器按触发时机分为 BEFORE 和 AFTER 两类。BEFORE 在写入真正发生前执行，"
                "可以修改 NEW 里的值，常用于自动补全字段，例如统一把 name 转成大写；"
                "AFTER 在写入完成后执行，用于记录日志、更新汇总表。想在写入前拦下非法数据，"
                "可以写 BEFORE INSERT 加 SELECT RAISE(ABORT, '原因')，这比只依赖 CHECK 约束"
                "灵活，能给出更具体的错误信息。不过约束能做到的事优先用约束，触发器是补充手段。",

                "还有一个常被用来做「软删除」的套路：给表加 deleted_at 列，写 AFTER UPDATE 触发器，"
                "当 deleted_at 从 NULL 变为非 NULL 时，把这一行复制进归档表。这样主表只保留活跃数据，"
                "查询更快，历史记录又完整保留。实现时要注意触发器自身不能再次触发表上的其他触发器，"
                "避免递归。设计触发器前先画出「哪些操作会触发、触发后改哪张表、会不会再触发」，"
                "这张图能帮你避开绝大多数隐式递归问题。",

                "如果必须使用触发器，建议配套三件事：给触发器写注释说明用途；在测试里覆盖"
                "触发与不触发两种路径；部署前用真实数据量估算性能影响。触发器最大的风险不是"
                "写错，而是被遗忘——半年后有人改表结构，不知道它还在默默执行，问题往往在上线后"
                "才暴露。把它当成代码而不是配置，纳入版本管理和评审，才能长期安全地使用。",
            ],
            "demo": "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT, level INTEGER);\n"
                    "CREATE TABLE level_audit (id INTEGER PRIMARY KEY, player_id INTEGER, old_level INTEGER, new_level INTEGER);\n"
                    "INSERT INTO players VALUES (1, 'V', 60), (2, 'Judy', 40);\n"
                    "UPDATE players SET level = 66 WHERE id = 1;\n"
                    "INSERT INTO level_audit (player_id, old_level, new_level) VALUES (1, 60, 66);\n"
                    "SELECT player_id, old_level, new_level FROM level_audit;",
            "mid": [
                diagram(
                    "AFTER UPDATE ON players\n"
                    "        │\n"
                    "        ├─ OLD：修改前的行（level = 60）\n"
                    "        └─ NEW：修改后的行（level = 66）\n"
                    "                │\n"
                    "                └─ WHEN OLD.level <> NEW.level 成立\n"
                    "                        │\n"
                    "                        └─ 写入 level_audit(player_id, old_level, new_level)"
                )
            ]
            + reading(
                "-- 参考写法：真实环境中由数据库自动执行\n"
                "CREATE TRIGGER trg_level_audit\n"
                "AFTER UPDATE OF level ON players\n"
                "FOR EACH ROW\n"
                "WHEN OLD.level <> NEW.level\n"
                "BEGIN\n"
                "  INSERT INTO level_audit (player_id, old_level, new_level)\n"
                "  VALUES (OLD.id, OLD.level, NEW.level);\n"
                "END;"
            ),
            "demo2": "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT, level INTEGER);\n"
                     "CREATE TABLE level_audit (id INTEGER PRIMARY KEY, player_id INTEGER, old_level INTEGER, new_level INTEGER);\n"
                     "INSERT INTO players VALUES (1, 'V', 60);\n"
                     "UPDATE players SET level = 66 WHERE id = 1;\n"
                     "INSERT INTO level_audit (player_id, old_level, new_level)\n"
                     "  SELECT id, 60, level FROM players WHERE id = 1;\n"
                     "SELECT p.name, a.old_level, a.new_level\n"
                     "FROM level_audit a JOIN players p ON p.id = a.player_id;",
            "tip": "触发器名建议带表名和事件，例如 trg_players_after_update，"
                   "排查问题时能从名字直接看出它挂在哪张表、什么时候触发。",
            "warn": "触发器是隐式执行的，应用层看不到调用点。表结构变更、批量导入、数据修复都会触发它，"
                    "上线前要确认这些路径不会产生意外的审计记录或汇总偏差。",
            "quiz": (
                "在 AFTER UPDATE 触发器中，OLD.level 表示？",
                ["修改后的等级", "修改前的等级", "NULL", "平均值"],
                1,
                "UPDATE 触发器同时拥有 OLD 与 NEW，OLD 是修改前的行，NEW 是修改后的行。",
            ),
            "ex": exercise(
                "记录等级变更",
                "players 表已有 (1, 'V', 60)。先把 V 的 level 改为 66，再向 level_audit 插入一条"
                "变更记录（player_id、old_level、new_level），最后联表返回 name、old_level、new_level。",
                "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT, level INTEGER);\n"
                "CREATE TABLE level_audit (id INTEGER PRIMARY KEY, player_id INTEGER, old_level INTEGER, new_level INTEGER);\n"
                "INSERT INTO players VALUES (1, 'V', 60);\n\n-- 在这里写 UPDATE、INSERT 与查询\n",
                "UPDATE players SET level = 66 WHERE id = 1; "
                "INSERT INTO level_audit (player_id, old_level, new_level) VALUES (1, 60, 66); "
                "SELECT p.name, a.old_level, a.new_level FROM level_audit a JOIN players p ON p.id = a.player_id;",
                [
                    "assert columns == ['name', 'old_level', 'new_level'], columns",
                    "assert rows == [['V', 60, 66]], rows",
                    "assert len(rows) == 1, rows",
                ],
                "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT, level INTEGER);\n"
                "CREATE TABLE level_audit (id INTEGER PRIMARY KEY, player_id INTEGER, old_level INTEGER, new_level INTEGER);\n"
                "INSERT INTO players VALUES (1, 'V', 60);\n\n"
                "UPDATE players SET level = 66 WHERE id = 1;\n"
                "INSERT INTO level_audit (player_id, old_level, new_level) VALUES (1, 60, 66);\n"
                "SELECT p.name, a.old_level, a.new_level\nFROM level_audit a\nJOIN players p ON p.id = a.player_id;\n",
                130,
            ),
        }),
        mk({
            "id": "sql27", "order": 526, "chapter": 53, "chapterName": ADVANCED,
            "title": "父子表的约定", "subtitle": "外键与级联", "xp": 110,
            "head": "让数据库检查引用完整性",
            "paras": [
                "外键（FOREIGN KEY）声明「这一列的值必须存在于另一张表的主键里」，用来维护父子表"
                "之间的引用完整性。例如 members.team_id REFERENCES teams(id) 表示队员所属的战队必须"
                "真实存在。外键拦住两类脏数据：插入一个不存在的 team_id，以及删除仍被引用的战队。"
                "没有外键时，这些错误只能靠应用层自觉，时间一长必然出现孤儿记录。",

                "SQLite 的外键默认不启用，必须在每个连接上执行 PRAGMA foreign_keys = ON 才会检查。"
                "这一点和大多数数据库不同，也是最容易踩的坑：建表时写了 REFERENCES，以为已经生效，"
                "实际插入非法数据却毫无反应。生产环境的连接池要在初始化语句里统一打开这个开关，"
                "并在监控里确认它确实为开。否则外键只是写在建表语句里的注释，没有任何约束力。",

                "级联行为用 ON DELETE 和 ON UPDATE 指定。ON DELETE CASCADE 表示父行删除时子行自动"
                "删除，适合「订单删除则订单明细一起删除」这种强归属关系；ON DELETE SET NULL 表示"
                "子行的外键置空，适合「战队解散但队员保留」；ON DELETE RESTRICT 直接拒绝删除，"
                "适合必须手工处理的场景；NO ACTION 是默认值，效果类似 RESTRICT 但检查时机略有不同。"
                "选哪种取决于业务语义，尤其是删除操作，必须先想清楚子数据该跟着走还是该保留。",

                "外键列建议建索引。SQLite 不会自动为外键列创建索引，而级联删除、按父键查子表都需要"
                "快速定位子行，没有索引时每次都要全表扫描。复合外键的顺序要与被引用列的顺序一致。"
                "另外，外键约束会增加写入开销，批量导入大量数据时可以临时关闭检查，导入完成后"
                "再打开并跑一次完整性检查，但这是一把双刃剑，必须确保导入的数据本身是干净的。",

                "建表时还可以用 DEFERRABLE 控制外键检查时机，默认是立即检查，每条语句结束就验证；"
                "设为 DEFERRABLE INITIALLY DEFERRED 后，检查推迟到事务提交时，适合「先插父行再插子行"
                "但顺序交叉」的复杂迁移。SQLite 支持这个语法，不过日常业务里很少需要，"
                "了解即可。更重要的是养成习惯：只要表之间有引用关系，就把外键和索引一起写上，"
                "并在连接初始化时打开 PRAGMA foreign_keys，三件事缺一不可。",

                "上线前建议跑一次完整性检查：PRAGMA foreign_key_check 会列出所有违反外键的存量数据。"
                "老系统往往在没有外键的年代积累了孤儿记录，直接加约束会失败，必须先把脏数据清洗掉。"
                "清洗时先备份，再逐条确认是删除还是补父行，不要图快用一条 DELETE 全清。"
                "数据完整性是长期工程，靠的是约束、索引、巡检三件套一起到位，而不是某一次运动式的清理。",

                "外键在 SQLite 里还有一些行为细节。PRAGMA foreign_keys 是连接级设置，"
                "断开重连后需要重新打开，所以不能只在初始化脚本里写一次就以为万事大吉，"
                "连接池的每条新连接都要执行。另外，修改表结构时（例如重建表）外键检查可能"
                "短暂失效，迁移脚本要在事务里完成，并在结束后跑 foreign_key_check 验证。"
                "把这些边界写进运维手册，比事后救火省心得多。还有一种常见误区：以为加外键就自动有了索引。实际上外键只约束取值，不创建索引，级联删除时若子表没有索引，每一行父记录删除都要全表扫描子表，数据量大时会慢得离谱。外键与索引要成对设计。",
            ],
            "demo": "CREATE TABLE teams (id INTEGER PRIMARY KEY, name TEXT);\n"
                    "CREATE TABLE members (id INTEGER PRIMARY KEY, name TEXT,\n"
                    "  team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE);\n"
                    "PRAGMA foreign_keys = ON;\n"
                    "INSERT INTO teams VALUES (1, 'Neon');\n"
                    "INSERT INTO members VALUES (1, 'V', 1), (2, 'Judy', 1), (3, 'Jackie', NULL);\n"
                    "DELETE FROM teams WHERE id = 1;\n"
                    "SELECT COUNT(*) AS members_left FROM members;",
            "mid": table(
                ["级联选项", "父行删除时", "适用场景"],
                [
                    ["CASCADE", "子行一起删除", "强归属，如订单与明细"],
                    ["SET NULL", "子行外键置空", "弱归属，如战队与队员"],
                    ["RESTRICT", "拒绝删除", "必须人工处理"],
                    ["NO ACTION", "默认，拒绝删除", "同 RESTRICT"],
                ],
            ),
            "demo2": "CREATE TABLE teams (id INTEGER PRIMARY KEY, name TEXT);\n"
                     "CREATE TABLE members (id INTEGER PRIMARY KEY, name TEXT,\n"
                     "  team_id INTEGER REFERENCES teams(id));\n"
                     "PRAGMA foreign_keys = ON;\n"
                     "INSERT INTO teams VALUES (1, 'Neon');\n"
                     "INSERT INTO members VALUES (1, 'V', 1);\n"
                     "SELECT m.name AS member, t.name AS team\n"
                     "FROM members m\nJOIN teams t ON t.id = m.team_id;",
            "tip": "外键列一定要手动建索引。SQLite 不会自动为 REFERENCES 列创建索引，"
                   "级联删除时没有索引会退化成全表扫描。",
            "warn": "SQLite 的外键默认关闭，必须执行 PRAGMA foreign_keys = ON。"
                    "不打开时 REFERENCES 只是文档，不会拦截任何非法写入。",
            "quiz": (
                "ON DELETE CASCADE 的作用是？",
                ["禁止删除父行", "删除父行时子行外键置空", "删除父行时子行一起删除", "删除子行时父行一起删除"],
                2,
                "CASCADE 表示级联删除，父行被删时引用它的子行会自动删除。",
            ),
            "ex": exercise(
                "解散战队",
                "创建 teams 与 members（team_id 带 ON DELETE CASCADE），开启外键，插入战队 Neon 与"
                "两名队员，删除战队后统计 remaining 队员数。",
                "CREATE TABLE teams (id INTEGER PRIMARY KEY, name TEXT);\n"
                "CREATE TABLE members (id INTEGER PRIMARY KEY, name TEXT,\n"
                "  team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE);\n"
                "PRAGMA foreign_keys = ON;\n\n-- 在这里写插入、删除与统计\n",
                "INSERT INTO teams VALUES (1, 'Neon'); INSERT INTO members VALUES (1, 'V', 1), (2, 'Judy', 1); "
                "DELETE FROM teams WHERE id = 1; SELECT COUNT(*) AS remaining FROM members;",
                [
                    "assert columns == ['remaining'], columns",
                    "assert rows == [[0]], rows",
                    "assert len(rows) == 1, rows",
                ],
                "CREATE TABLE teams (id INTEGER PRIMARY KEY, name TEXT);\n"
                "CREATE TABLE members (id INTEGER PRIMARY KEY, name TEXT,\n"
                "  team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE);\n"
                "PRAGMA foreign_keys = ON;\n\n"
                "INSERT INTO teams VALUES (1, 'Neon');\n"
                "INSERT INTO members VALUES (1, 'V', 1), (2, 'Judy', 1);\n"
                "DELETE FROM teams WHERE id = 1;\n"
                "SELECT COUNT(*) AS remaining FROM members;\n",
                120,
            ),
        }),
        mk({
            "id": "sql28", "order": 527, "chapter": 53, "chapterName": ADVANCED,
            "title": "拆表的分寸", "subtitle": "数据库范式", "xp": 110,
            "head": "为什么要把数据拆开",
            "paras": [
                "范式是拆表时要遵守的一组规则，目的是消除冗余与更新异常。第一范式要求每个字段都是"
                "原子值，不能再拆，例如不能把「V, Judy」塞进一个 players 字段；第二范式要求非主键"
                "字段完全依赖整个主键，不能只依赖复合主键的一部分；第三范式要求非主键字段之间不能"
                "互相依赖，例如订单表里存了 player_region，而 region 其实只依赖 player，就违反了"
                "第三范式。",

                "违反范式会带来三类问题。插入异常：想新增一个还没有订单的玩家，却因为订单表必须"
                "有订单号而插不进去。更新异常：同一个玩家的地区在十条订单里重复存储，改地址要改十行，"
                "漏一行就出现矛盾。删除异常：删掉最后一条订单，顺带把这个玩家的信息也弄丢了。"
                "把数据拆成 players、orders、products 三张表，各存各的事实，上述问题自然消失。",

                "范式不是越严格越好。分析型场景里，报表需要频繁连接多张表，每次查询都 JOIN 五六张表"
                "会很慢，这时会故意做反范式：把常用的汇总值冗余到一张宽表里，或者把维度字段直接"
                "复制进事实表。反范式用空间和一致性维护成本，换取查询速度。取舍标准是读写比例、"
                "数据量和一致性要求，而不是「范式高就更专业」。OLTP 系统倾向规范化，OLAP 系统"
                "可以接受适度冗余。",

                "落地时的经验是：先按第三范式设计，把实体和关系拆清楚，保证单一事实只存一处；"
                "出现明确的性能瓶颈后，再有针对性地引入冗余，并为冗余字段写清楚同步机制，"
                "例如触发器、定时任务或应用层双写。没有同步机制的冗余就是定时炸弹，"
                "短期看起来没问题，长期一定出现对不上的数据。范式是设计的起点，不是终点，"
                "能解释每一次冗余的理由，才算真正掌握了它。",

                "一个具体的拆表示例：把 orders_bad 里的 player 和 player_region 抽到 players 表，"
                "把 product 和 price 抽到 products 表，orders 只保留 player_id、product_id、qty。"
                "这样玩家改名只改一行，商品调价只改一行，订单表体积也明显变小。查询时用两次 JOIN "
                "还原明细，虽然多写了几行 SQL，但换来了数据的一致性和可维护性。"
                "拆表的收益通常在数据量增长、需求变化时才会显现，短期看像是「多此一举」，"
                "长期看却是最省事的做法。",

                "范式理论里还有第四、第五范式，处理多值依赖和连接依赖，日常业务几乎用不到。"
                "对大多数应用来说，把第三范式理解透、用扎实，已经足够设计出健康的表结构。"
                "真正需要警惕的是「一张表包打天下」的诱惑：字段越加越多，含义越来越杂，"
                "最后没人说得清哪一列代表什么。看到这种表，就是该拆的信号。"
                "拆表不是为了让图好看，而是为了让每个字段只有一个来源、一个含义、一个负责人。",

                "最后给一个判断是否该拆表的实用测试：想象要修改某个事实，需要更新几行？"
                "如果答案是「一行」，说明这个事实只存了一处，符合规范化；如果是「多行」或者"
                "「不知道有几行」，就说明存在冗余，需要拆表或建立同步机制。这个测试不需要背范式"
                "定义，任何业务人员都能理解，也适合在需求评审时快速识别模型问题。设计的本质是"
                "让每个事实只有一个家，剩下的规则都是这句话的推论。",
            ],
            "demo": "CREATE TABLE orders_bad (\n"
                    "  id INTEGER PRIMARY KEY,\n  player TEXT,\n  player_region TEXT,\n"
                    "  product TEXT,\n  price INTEGER\n);\n"
                    "INSERT INTO orders_bad VALUES (1, 'V', 'Neon', 'skin', 80);\n"
                    "INSERT INTO orders_bad VALUES (2, 'V', 'Neon', 'mount', 120);\n"
                    "SELECT player, player_region, COUNT(*) AS orders\nFROM orders_bad\nGROUP BY player, player_region;",
            "mid": table(
                ["范式", "要求", "反例"],
                [
                    ["1NF", "字段原子、不可再分", "把多个玩家塞进一列"],
                    ["2NF", "非主键完全依赖整个主键", "复合主键只依赖其中一部分"],
                    ["3NF", "非主键之间不互相依赖", "订单表存玩家地区"],
                    ["反范式", "有意冗余换性能", "宽表预存汇总值"],
                ],
            ),
            "demo2": "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT, region TEXT);\n"
                     "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER);\n"
                     "CREATE TABLE orders (id INTEGER PRIMARY KEY, player_id INTEGER, product_id INTEGER, qty INTEGER);\n"
                     "INSERT INTO players VALUES (1, 'V', 'Neon');\n"
                     "INSERT INTO products VALUES (10, 'skin', 80);\n"
                     "INSERT INTO orders VALUES (1, 1, 10, 2);\n"
                     "SELECT o.id, p.name AS player, p.region, pr.name AS product, o.qty * pr.price AS amount\n"
                     "FROM orders o\nJOIN players p ON p.id = o.player_id\n"
                     "JOIN products pr ON pr.id = o.product_id;",
            "tip": "第三范式的判断口诀：每个非主键字段都必须直接依赖主键，依赖主键之外的字段就说明拆得不够。",
            "warn": "反范式不是随意复制字段。每一处冗余都必须有明确的同步机制，否则迟早出现两份数据对不上的情况。",
            "quiz": (
                "订单表里存了玩家地区，而地区只依赖玩家，这违反了第几范式？",
                ["第一范式", "第二范式", "第三范式", "不属于范式问题"],
                2,
                "非主键字段之间互相依赖（地区依赖玩家而非订单），属于第三范式要消除的传递依赖。",
            ),
            "ex": exercise(
                "规范化的订单明细",
                "用 players、products、orders 三张表还原订单明细，输出订单 id、玩家 name、商品 name、"
                "金额 amount（qty * price），按订单 id 升序。",
                "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT);\n"
                "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER);\n"
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, player_id INTEGER, product_id INTEGER, qty INTEGER);\n"
                "INSERT INTO players VALUES (1, 'V'), (2, 'Judy');\n"
                "INSERT INTO products VALUES (10, 'skin', 80), (20, 'mount', 120);\n"
                "INSERT INTO orders VALUES (1, 1, 10, 2), (2, 2, 20, 1);\n\n-- 在这里写查询\n",
                "SELECT o.id, p.name AS name, pr.name AS product, o.qty * pr.price AS amount "
                "FROM orders o JOIN players p ON p.id = o.player_id JOIN products pr ON pr.id = o.product_id "
                "ORDER BY o.id;",
                [
                    "assert columns == ['id', 'name', 'product', 'amount'], columns",
                    "assert rows == [[1, 'V', 'skin', 160], [2, 'Judy', 'mount', 120]], rows",
                    "assert len(rows) == 2, rows",
                ],
                "CREATE TABLE players (id INTEGER PRIMARY KEY, name TEXT);\n"
                "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER);\n"
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, player_id INTEGER, product_id INTEGER, qty INTEGER);\n"
                "INSERT INTO players VALUES (1, 'V'), (2, 'Judy');\n"
                "INSERT INTO products VALUES (10, 'skin', 80), (20, 'mount', 120);\n"
                "INSERT INTO orders VALUES (1, 1, 10, 2), (2, 2, 20, 1);\n\n"
                "SELECT o.id, p.name AS name, pr.name AS product, o.qty * pr.price AS amount\n"
                "FROM orders o\nJOIN players p ON p.id = o.player_id\n"
                "JOIN products pr ON pr.id = o.product_id\nORDER BY o.id;\n",
                120,
            ),
        }),
    ]


def advanced_29_30():
    return [
        mk({
            "id": "sql29", "order": 528, "chapter": 53, "chapterName": ADVANCED,
            "title": "慢查询怎么救", "subtitle": "查询优化", "xp": 120,
            "head": "先看执行计划，再动手改",
            "paras": [
                "优化查询的第一步不是改 SQL，而是搞清楚它慢在哪里。SQLite 提供 EXPLAIN QUERY PLAN，"
                "输出每个步骤的扫描方式：SCAN 表示全表扫描，SEARCH 表示用索引定位，USE TEMP B-TREE "
                "表示为了排序或分组建了临时结构。看到 SCAN 一张十万行的表，基本可以确定瓶颈；"
                "看到 USE TEMP B-TREE FOR ORDER BY，说明排序没有索引支撑，数据量大时会落磁盘。",

                "最常见的优化手段是补索引。WHERE 里等值过滤的列、JOIN 的连接键、ORDER BY 的排序列，"
                "都是候选。复合索引要按「等值在前、范围在后、排序列最后」的顺序设计，例如 "
                "WHERE status = ? AND paid_on >= ? ORDER BY amount 更适合 (status, paid_on, amount)。"
                "还要注意覆盖索引：如果查询需要的列都在索引里，数据库可以只读索引不读表，"
                "执行计划会显示 USING COVERING INDEX，速度通常快很多。",

                "第二类手段是改写查询。把 SELECT * 改成只取需要的列，能减少读取与传输；"
                "把 WHERE 里的函数移到常量侧，让列保持裸用；把 OR 条件改写成 UNION ALL；"
                "用 EXISTS 替代 IN 处理可能含 NULL 的子查询；大 OFFSET 分页改成游标。"
                "这些改动的共同点是减少参与计算的数据量，而不是单纯「写得更高深」。"
                "改写前先备份原始 SQL 与执行计划，改完用同样的数据对比耗时，否则无法证明优化有效。",

                "第三类手段是调整数据组织方式：把频繁计算的汇总结果物化成表并定时刷新；"
                "把大表按时间分区；把冷数据归档到历史表。这些属于架构层面的优化，成本更高，"
                "通常在单条 SQL 已经优化到头之后才考虑。优化的优先级应该是：先确认瓶颈，"
                "再看索引，再看 SQL 写法，最后才动结构。跳过头两步直接上架构改造，"
                "往往花了大力气却没解决真正的问题。",

                "除了索引，SQLite 还有一些参数会影响查询速度。PRAGMA cache_size 控制页缓存大小，"
                "内存充足时可以适当调大，减少磁盘读取；PRAGMA journal_mode = WAL 改善并发读写；"
                "PRAGMA synchronous = NORMAL 在持久性与写入速度之间折中。移动端应用通常保持默认即可，"
                "服务端需要根据负载调优。调参前一定要有基准测试，记录调整前后的耗时，"
                "否则很容易凭感觉改出一堆参数，最后说不清哪一项真正起了作用。",

                "最后强调一个反直觉的事实：性能优化中最常见的收益来自「减少数据量」，"
                "而不是「换更快的写法」。加一个 WHERE 条件把扫描行数从百万降到千，"
                "比任何索引技巧都有效；只 SELECT 需要的列，比 SELECT * 再丢弃快得多；"
                "先把过滤做完再连接，比连接完再过滤省下大量中间结果。写查询时养成"
                "「先缩小范围、再做计算」的顺序，很多性能问题在写的那一刻就避免了。",

                "最后给一份可执行的优化清单：一，确认慢的是哪条 SQL，用真实数据量复现；"
                "二，看 EXPLAIN QUERY PLAN，定位 SCAN 还是 TEMP B-TREE；三，检查过滤列与连接列"
                "是否有合适索引；四，检查是否有函数包裹列、前导通配符、隐式类型转换；"
                "五，尝试改写并对比耗时；六，记录优化前后的数据，写进变更说明。"
                "这六步不需要高深技巧，但能覆盖绝大多数常见问题。优化最怕的是凭感觉改，"
                "改完不知道有没有变快，也不知道为什么变快。记录时至少写清三样：原始 SQL、执行计划摘要、优化前后耗时，这样下次遇到同类问题可以直接复用结论，而不是从头再猜一遍。",
            ],
            "demo": "CREATE TABLE orders (id INTEGER PRIMARY KEY, player TEXT, amount INTEGER, status TEXT);\n"
                    "INSERT INTO orders VALUES (1, 'V', 100, 'paid'), (2, 'Judy', 80, 'paid'), (3, 'V', 50, 'refund');\n\n"
                    "EXPLAIN QUERY PLAN\nSELECT player, SUM(amount)\nFROM orders\n"
                    "WHERE status = 'paid'\nGROUP BY player;",
            "mid": table(
                ["现象", "含义", "对策"],
                [
                    ["SCAN 大表", "全表扫描", "在过滤列上建索引"],
                    ["USE TEMP B-TREE", "排序/分组无索引", "给 ORDER BY / GROUP BY 列建索引"],
                    ["SEARCH ... INDEX", "命中索引", "保持，注意是否覆盖"],
                    ["COVERING INDEX", "覆盖索引", "只读索引，通常更快"],
                ],
            ),
            "demo2": "CREATE TABLE orders (id INTEGER PRIMARY KEY, player TEXT, amount INTEGER, status TEXT);\n"
                     "INSERT INTO orders VALUES (1, 'V', 100, 'paid'), (2, 'Judy', 80, 'paid'), (3, 'V', 50, 'refund');\n"
                     "CREATE INDEX idx_orders_status_player ON orders(status, player, amount);\n\n"
                     "EXPLAIN QUERY PLAN\nSELECT player, SUM(amount)\nFROM orders\n"
                     "WHERE status = 'paid'\nGROUP BY player;",
            "tip": "复合索引顺序按「等值列、范围列、排序列」排列，并且让查询需要的列尽量都落在索引里，"
                   "才有机会用到覆盖索引。",
            "warn": "不要看到 SCAN 就立刻加索引。小表全表扫描往往比走索引更快，"
                    "索引还会拖慢写入。先看数据量，再看执行计划，最后做对比测试。",
            "quiz": (
                "执行计划里出现 USING COVERING INDEX 说明？",
                ["查询失败", "只读索引就能得到结果", "使用了临时表", "没有使用索引"],
                1,
                "覆盖索引表示查询需要的列都在索引里，数据库无需回表读取原始数据。",
            ),
            "ex": exercise(
                "给状态建复合索引",
                "在 orders 表上创建复合索引 idx_orders_status_player，覆盖 status、player、amount，"
                "然后查看 WHERE status = 'paid' GROUP BY player 的执行计划，输出 detail 列。",
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, player TEXT, amount INTEGER, status TEXT);\n"
                "INSERT INTO orders VALUES (1, 'V', 100, 'paid'), (2, 'Judy', 80, 'paid'), (3, 'V', 50, 'refund');\n\n"
                "-- 在这里写 CREATE INDEX 与 EXPLAIN QUERY PLAN\n",
                "CREATE INDEX idx_orders_status_player ON orders(status, player, amount); "
                "EXPLAIN QUERY PLAN SELECT player, SUM(amount) FROM orders WHERE status = 'paid' GROUP BY player;",
                [
                    "assert columns == ['id', 'parent', 'notused', 'detail'], columns",
                    "assert len(rows) == 1, rows",
                    "assert 'COVERING INDEX' in rows[0][3], rows",
                ],
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, player TEXT, amount INTEGER, status TEXT);\n"
                "INSERT INTO orders VALUES (1, 'V', 100, 'paid'), (2, 'Judy', 80, 'paid'), (3, 'V', 50, 'refund');\n\n"
                "CREATE INDEX idx_orders_status_player ON orders(status, player, amount);\n"
                "EXPLAIN QUERY PLAN\nSELECT player, SUM(amount)\nFROM orders\n"
                "WHERE status = 'paid'\nGROUP BY player;\n",
                130,
            ),
        }),
        mk({
            "id": "sql30", "order": 529, "chapter": 53, "chapterName": ADVANCED,
            "title": "综合项目：运营分析", "subtitle": "电商与游戏运营指标", "xp": 140,
            "head": "把前面学的拼成一份报表",
            "paras": [
                "这一讲不再引入新语法，而是把 30 讲的内容组合成一份真实报表。场景是游戏内商城："
                "orders 表记录每笔订单的玩家、商品、数量、单价与支付日期。运营想知道三件事："
                "每月收入与订单量、每位玩家的消费排名、以及高价值玩家的特征。三个问题分别对应"
                "分组聚合、窗口排名与条件统计，正好覆盖 core 与 advanced 两篇的核心技能。",

                "第一步按月汇总。用 STRFTIME('%Y-%m', paid_on) 把日期截成月份作为分组键，"
                "COUNT(*) 算订单数，SUM(qty * price) 算收入，ROUND 控制小数位，最后按月份排序。"
                "这一步的关键是明确「一行代表什么」：一行是一个自然月，所以 GROUP BY 只能用月份，"
                "不能把玩家也放进去，否则就变成每月每人的粒度。粒度想清楚了，后面的指标才不会重复计数。",

                "第二步给玩家排名。用 SUM(qty * price) 按玩家聚合出总额，再用 RANK() OVER "
                "(ORDER BY SUM(qty * price) DESC) 给排名。SQLite 允许在窗口函数的 ORDER BY 里"
                "直接写聚合表达式，因为窗口计算发生在分组之后。如果想同时保留每位玩家的订单数，"
                "加一个 COUNT(*) 即可。排名用 RANK 而不是 ROW_NUMBER，是为了让消费相同的玩家并列，"
                "这更符合运营榜单的直觉。",

                "第三步做用户分层。用 CASE WHEN 把消费额分成高价值、中价值、普通三档，"
                "再用 GROUP BY 档位统计人数与总收入。这样一张表就能回答「高价值用户贡献了多少收入」。"
                "真实项目里还会把这些查询固化成视图或定时任务，配上日期参数，形成日报、周报。"
                "写报表时始终记住两条：口径要写清楚，边界要验证。用 SUM 核对总数、用 COUNT 核对行数，"
                "让每一个数字都能被追溯，这份报表才值得信任。",

                "如果继续扩展，这份报表还能加入留存与复购指标。留存要看「注册后第 N 天是否活跃」，"
                "需要用户表和每日活跃表按日期差连接；复购要看「同一玩家是否有两次以上购买」，"
                "用 GROUP BY player HAVING COUNT(*) >= 2。这些指标的计算逻辑各异，但底层技能"
                "仍是本课程反复练习的几件事：连接、分组、条件统计、窗口排名。把基础打牢，"
                "新指标只是换一种组合方式，不需要从头学起。",

                "如果要把这份报表产品化，下一步通常是加日期参数与缓存。给查询加上起止日期，"
                "让运营能选月份；把结果写进汇总表，每天凌晨刷新一次，避免每次打开页面都重算。"
                "这些工程手段不改变 SQL 的语义，却决定了报表能不能在真实业务里用起来。"
                "写 SQL 只是数据工作的第一半，另一半是让结果稳定、可追溯、可交付。"
                "把这两半都做好，才算真正掌握了这门课。",

                "课程到这里就结束了。回看 30 讲，从最基础的 SELECT 到综合报表，核心概念其实不多："
                "行与列的筛选、聚合与分组、表与表的连接、子查询与 CTE、窗口与事务。真正难的不是"
                "记住语法，而是把业务问题翻译成这些操作，并且能验证结果是否正确。建议你找一份"
                "自己熟悉的数据，从「每月汇总」开始写起，逐步加维度、加排名、加对比，"
                "每写一条就用 COUNT 和 SUM 交叉核对。练到能独立完成一份运营报表，这门课的目标"
                "就达到了。",
            ],
            "demo": "CREATE TABLE orders (id INTEGER PRIMARY KEY, player TEXT, product TEXT,\n"
                    "  qty INTEGER, price REAL, paid_on TEXT);\n"
                    "INSERT INTO orders VALUES\n"
                    "  (1, 'V', 'skin', 2, 80, '2024-01-05'),\n"
                    "  (2, 'V', 'mount', 1, 120, '2024-01-18'),\n"
                    "  (3, 'Judy', 'skin', 1, 80, '2024-02-02'),\n"
                    "  (4, 'Judy', 'emote', 5, 20, '2024-02-20'),\n"
                    "  (5, 'Jackie', 'mount', 1, 120, '2024-03-01');\n\n"
                    "SELECT STRFTIME('%Y-%m', paid_on) AS month,\n"
                    "       COUNT(*) AS orders,\n"
                    "       ROUND(SUM(qty * price), 2) AS revenue\n"
                    "FROM orders\nGROUP BY month\nORDER BY month;",
            "mid": table(
                ["指标", "写法", "说明"],
                [
                    ["月收入", "SUM(qty * price)", "按 STRFTIME 月份分组"],
                    ["订单数", "COUNT(*)", "一行一单"],
                    ["玩家排名", "RANK() OVER (ORDER BY SUM(...) DESC)", "并列同名次"],
                    ["用户分层", "CASE WHEN 总额 >= 阈值", "高/中/普通三档"],
                ],
            ),
            "demo2": "CREATE TABLE orders (id INTEGER PRIMARY KEY, player TEXT, product TEXT,\n"
                     "  qty INTEGER, price REAL, paid_on TEXT);\n"
                     "INSERT INTO orders VALUES\n"
                     "  (1, 'V', 'skin', 2, 80, '2024-01-05'),\n"
                     "  (2, 'V', 'mount', 1, 120, '2024-01-18'),\n"
                     "  (3, 'Judy', 'skin', 1, 80, '2024-02-02'),\n"
                     "  (4, 'Judy', 'emote', 5, 20, '2024-02-20'),\n"
                     "  (5, 'Jackie', 'mount', 1, 120, '2024-03-01');\n\n"
                     "SELECT player,\n"
                     "       ROUND(SUM(qty * price), 2) AS total,\n"
                     "       RANK() OVER (ORDER BY SUM(qty * price) DESC) AS rnk\n"
                     "FROM orders\nGROUP BY player\nORDER BY rnk;",
            "tip": "报表里的每个数字都要能被另一条查询验证。总收入用 SELECT SUM(qty*price) 单独核对，"
                   "总订单数用 COUNT(*) 核对，两个口径对得上，报表才可信。",
            "warn": "分组粒度决定指标含义。按月汇总时不要再按玩家分组，否则「月收入」会变成"
                    "「每人每月收入」，加总后可能重复计算，汇报时口径就错了。",
            "quiz": (
                "要按自然月统计收入，正确的分组键是？",
                ["GROUP BY paid_on", "GROUP BY STRFTIME('%Y-%m', paid_on)", "GROUP BY player", "GROUP BY qty"],
                1,
                "STRFTIME('%Y-%m', paid_on) 把日期截成年月，同一月的订单会归入同一组。",
            ),
            "ex": exercise(
                "月度运营报表",
                "从 orders 表按自然月统计 month、orders（订单数）、revenue（收入，保留两位小数），"
                "按 month 升序输出。",
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, player TEXT, product TEXT,\n"
                "  qty INTEGER, price REAL, paid_on TEXT);\n"
                "INSERT INTO orders VALUES\n"
                "  (1, 'V', 'skin', 2, 80, '2024-01-05'),\n"
                "  (2, 'V', 'mount', 1, 120, '2024-01-18'),\n"
                "  (3, 'Judy', 'skin', 1, 80, '2024-02-02'),\n"
                "  (4, 'Judy', 'emote', 5, 20, '2024-02-20'),\n"
                "  (5, 'Jackie', 'mount', 1, 120, '2024-03-01');\n\n-- 在这里写查询\n",
                "SELECT STRFTIME('%Y-%m', paid_on) AS month, COUNT(*) AS orders, "
                "ROUND(SUM(qty * price), 2) AS revenue FROM orders GROUP BY month ORDER BY month;",
                [
                    "assert columns == ['month', 'orders', 'revenue'], columns",
                    "assert rows == [['2024-01', 2, 280.0], ['2024-02', 2, 180.0], ['2024-03', 1, 120.0]], rows",
                    "assert len(rows) == 3, rows",
                ],
                "CREATE TABLE orders (id INTEGER PRIMARY KEY, player TEXT, product TEXT,\n"
                "  qty INTEGER, price REAL, paid_on TEXT);\n"
                "INSERT INTO orders VALUES\n"
                "  (1, 'V', 'skin', 2, 80, '2024-01-05'),\n"
                "  (2, 'V', 'mount', 1, 120, '2024-01-18'),\n"
                "  (3, 'Judy', 'skin', 1, 80, '2024-02-02'),\n"
                "  (4, 'Judy', 'emote', 5, 20, '2024-02-20'),\n"
                "  (5, 'Jackie', 'mount', 1, 120, '2024-03-01');\n\n"
                "SELECT STRFTIME('%Y-%m', paid_on) AS month,\n"
                "       COUNT(*) AS orders,\n"
                "       ROUND(SUM(qty * price), 2) AS revenue\n"
                "FROM orders\nGROUP BY month\nORDER BY month;\n",
                140,
            ),
        }),
    ]


# === MORE ===


def basics_pack():
    return basics_01_05() + basics_06_10()


def core_pack():
    return core_11_15() + core_16_20()


def advanced_pack():
    return advanced_21_25() + advanced_26_30() + advanced_29_30()


def main():
    packs = {
        "sql-basics.json": basics_pack(),
        "sql-core.json": core_pack(),
        "sql-advanced.json": advanced_pack(),
    }
    for name, lessons in packs.items():
        if not lessons:
            print("skip empty", name)
            continue
        for item in lessons:
            n = prose_len(item)
            if not 900 <= n <= 1600:
                print("WARN %s prose=%d" % (item["id"], n))
        path = ROOT / "content_packs" / name
        path.write_text(
            json.dumps(lessons, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print("wrote", name, len(lessons), "lessons")


if __name__ == "__main__":
    main()
