import json
import sqlite3
import time
import traceback

DEFAULT_TIMEOUT = 8.0
MAX_OUTPUT = 1_048_576
MAX_ROWS = 200

_DENIED_ACTIONS = {
    getattr(sqlite3, "SQLITE_ATTACH", 24),
    getattr(sqlite3, "SQLITE_DETACH", 25),
}


def _authorizer(action, arg1, arg2, dbname, source):
    if action in _DENIED_ACTIONS:
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK


def _split_statements(sql):
    """按分号切分语句，忽略字符串与 -- 行注释中的分号。"""
    statements = []
    buf = []
    quote = None
    i = 0
    while i < len(sql):
        ch = sql[i]
        if quote:
            buf.append(ch)
            if ch == quote:
                if i + 1 < len(sql) and sql[i + 1] == quote:
                    buf.append(sql[i + 1])
                    i += 2
                    continue
                quote = None
            i += 1
            continue
        if ch in ("'", '"'):
            quote = ch
            buf.append(ch)
            i += 1
            continue
        if ch == "-" and i + 1 < len(sql) and sql[i + 1] == "-":
            while i < len(sql) and sql[i] != "\n":
                i += 1
            continue
        if ch == ";":
            text = "".join(buf).strip()
            if text:
                statements.append(text)
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    tail = "".join(buf).strip()
    if tail:
        statements.append(tail)
    return statements


def _format_table(cursor):
    columns = [d[0] for d in cursor.description or []]
    rows = cursor.fetchmany(MAX_ROWS)
    lines = ["\t".join(columns)] if columns else []
    for row in rows:
        lines.append("\t".join("NULL" if v is None else str(v) for v in row))
    return columns, rows, "\n".join(lines)


def _execute(sql):
    started = time.perf_counter()
    # isolation_level=None 关闭 Python 的隐式事务管理：否则 sqlite3 会在每条语句前
    # 自动 BEGIN，用户写的 BEGIN / COMMIT / ROLLBACK 会直接报
    # 「cannot start a transaction within a transaction」。
    # 关闭后行为与 sqlite3 命令行一致，事务控制权完全交给 SQL 本身。
    conn = sqlite3.connect(":memory:", isolation_level=None)
    conn.set_authorizer(_authorizer)
    out = []
    error = None
    last = None
    try:
        for statement in _split_statements(sql):
            cursor = conn.execute(statement)
            if cursor.description:
                columns, rows, text = _format_table(cursor)
                last = {
                    "columns": columns,
                    "rows": [[None if v is None else v for v in row] for row in rows],
                }
                out.append(text)
            else:
                out.append("OK (%d rows affected)" % cursor.rowcount)
        conn.commit()
    except BaseException:  # aqg: top-level boundary
        try:
            conn.rollback()  # 未提交的事务在报错时必须撤销，避免半成品状态
        except Exception:
            pass
        etype, evalue, tb = __import__("sys").exc_info()
        trimmed = tb.tb_next if tb is not None else None
        error = {
            "type": getattr(etype, "__name__", "Error"),
            "message": str(evalue),
            "traceback": "".join(traceback.format_exception(etype, evalue, trimmed)).strip(),
        }
    finally:
        conn.close()
    text = "\n".join(out)
    if len(text) > MAX_OUTPUT:
        text = "[输出过长已截断]\n" + text[-MAX_OUTPUT:]
    return {
        "ok": error is None,
        "stdout": text,
        "stderr": "",
        "error": error,
        "duration_ms": int((time.perf_counter() - started) * 1000),
        "last": last,
    }


def run_sql(sql):
    core = _execute(sql)
    return {
        "ok": core["ok"],
        "stdout": core["stdout"],
        "stderr": core["stderr"],
        "error": core["error"],
        "duration_ms": core["duration_ms"],
        "variables": [],
    }


def check_sql(sql, tests):
    core = _execute(sql)
    if core["error"] is not None:
        return {
            "ok": False,
            "passed": False,
            "stdout": core["stdout"],
            "stderr": "",
            "test_output": "",
            "error": core["error"],
            "duration_ms": core["duration_ms"],
            "variables": [],
        }
    namespace = {
        "__name__": "__main__",
        "__stdout__": core["stdout"],
        "last": core["last"],
        "columns": core["last"]["columns"] if core["last"] else [],
        "rows": core["last"]["rows"] if core["last"] else [],
    }
    failures = []
    for index, test in enumerate(tests, start=1):
        try:
            exec(compile(test, "<sql-test-%d>" % index, "exec"), namespace)
        except AssertionError as exc:
            failures.append(str(exc) or "断言未通过")
        except BaseException:  # aqg: top-level boundary
            etype, evalue, _tb = __import__("sys").exc_info()
            failures.append("%s: %s" % (getattr(etype, "__name__", "Error"), evalue))
    passed = not failures
    message = "" if passed else "共 %d 个用例，%d 个未通过；首个失败：%s" % (
        len(tests), len(failures), failures[0]
    )
    return {
        "ok": True,
        "passed": passed,
        "stdout": core["stdout"],
        "stderr": "",
        "test_output": "",
        "error": None if passed else {"type": "TestFailed", "message": message, "traceback": ""},
        "duration_ms": core["duration_ms"],
        "variables": [],
    }


def run_sql_json(payload_json):
    payload = json.loads(payload_json)
    return json.dumps(run_sql(payload.get("code", "")), ensure_ascii=False)


def check_sql_json(payload_json):
    payload = json.loads(payload_json)
    return json.dumps(
        check_sql(payload.get("code", ""), payload.get("tests") or []), ensure_ascii=False
    )


def info_json():
    return json.dumps({"sqlite_version": sqlite3.sqlite_version, "platform": "sqlite3"})
