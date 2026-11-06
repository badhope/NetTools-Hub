#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 Lua 三套课程包（基础 / 核心 / 进阶），共 30 讲。

运行：python tools/gen_lua_curriculum.py
产物：content_packs/lua-basics.json、lua-core.json、lua-advanced.json

约束：目标运行时是 LuaJ 3.0.1（Lua 5.2 语义），沙箱只有
Base / Table / String / Math / Coroutine 五个库，没有 io / os / 文件查找器。
因此所有示例都必须能在这套子集里真实执行。
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKS = ROOT / "content_packs"


# ---------- 块构造器 ----------

def h(text):
    return {"type": "heading", "text": text}


def p(text):
    return {"type": "text", "text": text}


def code(src, out=None):
    blocks = [{"type": "code", "code": src, "runnable": True}]
    if out is not None:
        blocks.append({"type": "output", "text": out})
    return blocks


def tip(text):
    return {"type": "tip", "text": text}


def warn(text):
    return {"type": "warn", "text": text}


def table(headers, rows):
    return {"type": "table", "headers": headers, "rows": rows}


def quiz(question, options, answer, explain):
    return {
        "type": "quiz",
        "question": question,
        "options": options,
        "answer": answer,
        "explain": explain,
    }


def practice(title, src, out, hint):
    return {
        "type": "practice",
        "title": title,
        "code": src,
        "output": out,
        "hint": hint,
    }


def visualize(title, caption, frames):
    return {"type": "visualize", "title": title, "caption": caption, "frames": frames}


def frame(label, items, highlight):
    return {
        "label": label,
        "items": [{"name": k, "value": v} for k, v in items],
        "highlight": highlight,
    }


def exercise(title, brief, starter, hint, tests, solution, xp=90):
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


def lesson(id_, order, chapter, chapter_name, title, subtitle, xp, blocks, ex):
    return {
        "id": id_,
        "order": order,
        "chapter": chapter,
        "chapterName": chapter_name,
        "lang": "lua",
        "title": title,
        "subtitle": subtitle,
        "xp": xp,
        "blocks": merge_text(blocks),
        "exercise": ex,
    }


def merge_text(blocks, target=3):
    """把零散的 text 块合并成 target 段，保持段落分布与代码块交替的节奏。

    写作时按「一小段一个想法」拆开最舒服，但课程渲染要求每讲 2-3 段正文，
    所以生成阶段做一次归并：按字数均分成 target 组，放在首、中、末三个
    原始 text 块的位置上。
    """
    idx = [i for i, b in enumerate(blocks) if b.get("type") == "text"]
    if len(idx) <= target:
        return blocks

    texts = [blocks[i]["text"] for i in idx]
    total = sum(len(t) for t in texts)
    per = total / target
    groups, cur, acc = [], [], 0
    for t in texts:
        cur.append(t)
        acc += len(t)
        if acc >= per and len(groups) < target - 1:
            groups.append(cur)
            cur, acc = [], 0
    groups.append(cur)
    while len(groups) < target:
        groups.append([])
    groups = [g for g in groups if g][:target]

    anchors = [idx[0], idx[len(idx) // 2], idx[-1]]
    anchor_map = {}
    for k, a in enumerate(anchors[: len(groups)]):
        anchor_map[a] = k

    out, emitted = [], set()
    for i, b in enumerate(blocks):
        if i in anchor_map:
            k = anchor_map[i]
            if k not in emitted:
                out.append({"type": "text", "text": "\n\n".join(groups[k])})
                emitted.add(k)
        elif b.get("type") == "text":
            continue
        else:
            out.append(b)
    return out


BASIC = "Lua · 基础篇"
CORE = "Lua · 核心篇"
ADV = "Lua · 进阶篇"


# ---------- 基础篇 lua01 ~ lua10 ----------

def build_basics():
    items = []

    items.append(lesson(
        "lua01", 400, 41, BASIC, "第一次握手", "print() 与注释", 60,
        [
            h("让终端开口"),
            p("Lua 诞生于 1993 年的巴西里约热内卢天主教大学，最初是为了让 C 程序拥有一门轻量、易嵌入的脚本语言而设计的，名字在葡萄牙语里是「月亮」。整个解释器只有几百 KB，启动几乎瞬间完成，所以游戏引擎、Nginx、Redis、Wireshark 都把它当作扩展语言使用。它的设计哲学是「机制少而精」：语言本身只提供少量原语，复杂能力交给宿主程序和标准库，这让它既小又快，也让学习者能在几天内掌握全部语法骨架。"),
            p("这门课使用 LuaJ 3.0.1，语义对齐 Lua 5.2，全部代码都在你的设备上本地执行，不需要联网，也不会碰你的文件系统。第一讲先不追求语法完整，目标是让终端开口说话，并建立起「写一行、跑一行、看输出」的节奏。教材里的每个 output 块都是这段代码在真实 LuaJ 上跑出来的结果，你可以逐字对照；如果对不上，要么是代码被改过，要么是你对环境做了额外假设。这种「输出即证据」的习惯，比记住多少语法点都更有价值，因为它是你自己验证结论的能力。"),
            p("print 是最基础的输出函数：参数之间用逗号隔开，输出时会自动插入制表符，末尾再补一个换行。字符串可以用单引号或双引号包裹，两者完全等价，选择哪一种只取决于字符串内部是否含有引号。注释用两个连字符开头，从 -- 到行尾的内容都会被解释器忽略；如果要注释一整段，就用 --[[ 开头、]] 结尾，中间可以跨很多行，适合临时屏蔽一大块代码或写较长的说明。注释不影响运行结果，但它决定了三个月后你还读不读得懂自己写的代码，也决定了同事接手时要花多少时间。"),
            *code(
                r"""print('HELLO, night city')
print(1 + 2, 'lua', true)
-- 这一行是注释
--[[ 多行注释
     可以写很多行 ]]
print('done')""",
                "HELLO, night city\n3\tlua\ttrue\ndone",
            ),
            table(
                ["写法", "作用", "示例"],
                [
                    ["print(a, b)", "输出多个值，用制表符分隔", "print(1, 2) → 1\\t2"],
                    ["-- 注释", "单行注释", "-- 这里是说明"],
                    ["--[[ ... ]]", "多行注释", "整段说明文字"],
                    ["'text' / \"text\"", "字符串字面量", "两种引号等价"],
                    ["then ... end", "条件块", "if x then ... end"],
                ],
            ),
            p("Lua 没有花括号，代码块靠关键字收尾：条件用 then 开头、end 结尾，循环用 do 开头、end 结尾，函数用 function 开头、end 结尾。这种写法一开始会觉得啰嗦，但它让嵌套层级一眼可见，也不会出现括号不匹配却很难定位的问题。写代码时建议统一缩进两个空格，end 与它对应的开头关键字对齐，读起来会轻松很多。另一个初学阶段的高频问题是中文标点：中文引号、中文逗号、中文分号在 Lua 里都不是合法字符，报错往往指向一个看起来毫无问题的位置，遇到莫名其妙的语法错误先检查标点，再看引号是否成对。"),
            *code(
                r"""local city = 'Night City'
print('欢迎来到', city)
print('1 + 1 =', 1 + 1)
print(string.upper('lua'))""",
                "欢迎来到\tNight City\n1 + 1 =\t2\nLUA",
            ),
            p("这一讲的练习很简单，但请认真做：函数要返回字符串而不是打印字符串。返回值和打印是两件事，后面的判题全部通过比较返回值来判断对错，如果你在函数里 print 而没有 return，测试会拿到 nil，然后失败。养成「函数负责计算并返回，调用方决定怎么展示」的习惯，是从第一天就该建立的工程直觉。写完之后可以自己加几行 print 看看中间结果，再删掉，这种小步验证的方式会一直用到最后一讲。"),
            tip("print 用逗号分隔多个参数时，输出之间是制表符，不是空格。写 output 对照时不要把制表符写成空格，否则肉眼几乎看不出差别，判题却会对不上。"),
            quiz(
                "Lua 的单行注释符号是？",
                ["//", "#", "--", "/* */"],
                2,
                "Lua 单行注释是 --，多行注释是 --[[ ... ]]。// 和 /* */ 来自 C 系语言，在 Lua 里会直接报语法错误。",
            ),
        ],
        exercise(
            "打印入网代号",
            "实现 greet(name)：返回 'HELLO, ' 拼上 name 的字符串。",
            "function greet(name)\n  -- 返回 'HELLO, ' 拼上 name\n\nend\n\nprint(greet('v'))",
            "return 'HELLO, ' .. name —— Lua 字符串拼接用两个点。",
            [
                "assert(greet('v') == 'HELLO, v', 'greet(\"v\") 应为 HELLO, v')",
                "assert(greet('') == 'HELLO, ', '空名字也要能拼接')",
                "assert(greet('Night City') == 'HELLO, Night City', '包含空格的名字也要能拼接')",
            ],
            "function greet(name)\n  return 'HELLO, ' .. name\nend\n",
            80,
        ),
    ))

    items.append(lesson(
        "lua02", 401, 41, BASIC, "变量与类型", "local、number、string、boolean", 60,
        [
            h("值和类型"),
            p("Lua 的变量不需要声明，赋值即创建。默认情况下写下的变量是全局变量，加上 local 关键字才是局部变量。全局变量实际上挂在 _G 这张表上，任何一段代码都能读写；局部变量只在当前块里可见。工程上几乎总是应该用 local：它既避免不同模块互相污染，也让运行时的变量查找路径更短。一个文件加载进程序后，最理想的状态是只往全局写一个入口，其余全是 local，这样别人用你的文件时不会莫名其妙多出一堆全局名字，也不会在无意间覆盖你的函数。"),
            p("Lua 一共只有八种类型：nil、boolean、number、string、function、table、thread、userdata。number 只有一种，内部用双精度浮点数表示，所以 1 和 1.0 是同一个值，整数和浮点不区分。需要整数结果时用 math.floor 显式向下取整，不要指望除法自动截断。type 函数返回类型名的字符串，是调试和写判题时最常用的工具；它会返回 'nil' 这个字符串，而不是 nil 值本身，这一点在写断言时特别容易搞混，也解释了为什么 type(nil) == nil 永远是 false。"),
            p("number 和 string 之间会发生自动转换：字符串参与算术会被转成数字，数字参与拼接会被转成字符串。这种便利在快速脚本里很好用，但在工程代码里容易掩盖输入错误。更稳妥的习惯是显式调用 tonumber 和 tostring：转换失败时 tonumber 返回 nil，你可以立刻判断并给出提示，而不是让一个本应报错的值一路传到最深层才爆发。类型系统不会替你兜底，Lua 的哲学是「程序员知道自己在做什么」，代价是所有校验都要自己写，写完还要自己测，测试覆盖不到的地方就是线上事故的入口。"),
            p("还有一个容易忽略的点：nil 只能作为值存在，不能当作「空字符串」或「零」来用。做字符串拼接时，nil 会直接抛错；做算术时，nil 也会抛错。所以在把外部数据合并进配置表之前，先想清楚每个字段缺失时应该补什么默认值，是空串、0、false，还是保持 nil 表示「没配置」。把「缺失」和「默认值」这两种语义分开，是后面写配置、写模块时反复要用到的建模能力，越早建立越省事。"),
            *code(
                r"""local level = 66
local name = 'V'
local online = true
local nothing = nil
print(type(level), type(name), type(online), type(nothing))
print(type(type), type(print))""",
                "number\tstring\tboolean\tnil\nfunction\tfunction",
            ),
            table(
                ["类型", "说明", "例子"],
                [
                    ["nil", "空值，未赋值时的默认值", "local x = nil"],
                    ["boolean", "true / false", "local ok = true"],
                    ["number", "双精度浮点数，只有一种数字", "3.14 / 66"],
                    ["string", "不可变字节序列", "'abc'"],
                    ["function", "函数也是值", "print, function() end"],
                    ["table", "唯一的内置容器", "{}"],
                    ["thread", "协程对象", "coroutine.create(f)"],
                    ["userdata", "宿主语言对象，本沙箱不开放", "—"],
                ],
            ),
            p("判断一个值是什么类型，永远用 type(v) == 'number' 这样的写法，不要写 v == 'number'，后者拿值和字符串比较，结果永远是 false。判断是否为 nil 时可以直接写 v == nil，也可以用 not v，但要注意 not v 对 false 同样成立，两者语义并不相同。需要区分「没有值」和「值为假」时，必须显式比较 nil，这也是 Lua 里最常见的边界 bug 来源之一，尤其在配置合并、参数默认值、缓存命中这类场景里，一个 false 被当成缺失就会引发连锁错误，而且往往在很远的地方才表现出来。"),
            *code(
                r"""print(1 == 1.0)
print('10' + 5)
print('10' .. 5)
print(tonumber('3.5'), tonumber('abc'))
print(math.floor(7 / 2), 7 / 2)""",
                "true\n15\n105\n3.5\tnil\n3\t3.5",
            ),
            warn("'10' + 5 能跑通不代表应该这么写。输入来自用户或配置时，先用 tonumber 校验，失败就返回 nil 或报错，避免错误在几层调用之后才暴露。"),
            quiz(
                "表达式 type(nil) 的结果是？",
                ["'nil'", "nil", "'boolean'", "报错"],
                0,
                "type 返回的是字符串，所以 type(nil) 得到字符串 'nil'，注意它带引号，和值 nil 不是一回事。",
            ),
        ],
        exercise(
            "类型报告员",
            "实现 describe(v)：返回 v 的类型名；如果 v 是 nil，返回 'nil'。",
            "function describe(v)\n  \nend\n\nprint(describe(1))\nprint(describe('a'))",
            "直接 return type(v)。type 对 nil 也会返回字符串 'nil'。",
            [
                "assert(describe(1) == 'number', 'describe(1) 应为 number')",
                "assert(describe('a') == 'string', '字符串应为 string')",
                "assert(describe(true) == 'boolean', '布尔应为 boolean')",
                "assert(describe(nil) == 'nil', 'nil 的类型名应为 nil')",
            ],
            "function describe(v)\n  return type(v)\nend\n",
            80,
        ),
    ))

    items.append(lesson(
        "lua03", 402, 41, BASIC, "运算符", "算术、比较与逻辑", 70,
        [
            h("运算符与优先级"),
            p("算术运算符有 +、-、*、/、%、^ 六种。除法永远返回浮点数，7 / 2 得到 3.5；Lua 5.2 没有整除运算符，需要整数商时写 math.floor(a / b)。% 是取模，语义和数学上的余数一致：-7 % 3 得到 2，因为结果会和除数同号，这一点和 C 语言的 % 不同，从 C 转过来的人要特别注意。^ 是幂运算，2 ^ 10 得到 1024，指数可以是小数，2 ^ 0.5 就是开平方，负数指数表示取倒数，所以 2 ^ -1 等于 0.5。浮点数用双精度表示，0.1 + 0.2 在显示层会被格式化得看不出误差，但比较相等时仍要留出容差。"),
            p("比较运算符有 ==、~=、<、>、<=、>=，结果一定是 boolean。字符串按字节序比较，所以 'a' < 'b' 为真，'Z' < 'a' 也为真，因为大写字母的编码更小。== 比较的是值：数字比较数值，字符串比较内容，表比较引用——两个内容完全相同的表也不相等。判断不相等要用 ~=，不要写 !=，后者不是 Lua 的语法，会直接报语法错误；同样地，Lua 里也没有 === 这种严格相等运算符，因为数字只有一种类型，不存在「值相等但类型不同」的情况，字符串也不会被隐式转换成数字来比较。"),
            p("逻辑运算符 and、or、not 有一个容易忽略的细节：and 和 or 返回的是操作数本身，不是 boolean。a and b 在 a 为真时返回 b，否则返回 a；a or b 在 a 为真时返回 a，否则返回 b。这让 x = x or 0 成为设置默认值的常用写法，也让 f() and g() 可以当作「f 成功才执行 g」的简写。但要注意，如果 false 是合法值，or 会把它当成失败分支，此时应该显式判断 nil。not 总是返回 boolean，这一点和 and、or 不同，写条件时不要假设它们类型一致。"),
            p("实际工程里，运算符最容易出错的地方不是数学，而是边界。除数为 0 时 Lua 不会抛异常，而是返回 inf 或 nan，错误会一路传播到展示层；取模的符号规则和 C 不同，负数参与时结果可能和预期相反；比较浮点数是否相等几乎总是错的，应该比较差的绝对值。写完一个涉及除法的函数，至少测一遍除数为 0 的情况，看看是返回 0、返回 nil 还是抛错，把这个决定写进注释或文档，调用方才不会猜。"),
            *code(
                r"""print(7 + 3, 7 - 3, 7 * 3, 7 / 2)
print(7 % 3, -7 % 3, 7 % -3)
print(2 ^ 10, 2 ^ 0.5)
print(math.floor(7 / 2), math.floor(-7 / 2))""",
                "10\t4\t21\t3.5\n1\t2\t-2\n1024\t1.4142135\n3\t-4",
            ),
            table(
                ["类别", "运算符", "说明"],
                [
                    ["算术", "+ - * / % ^", "除法返回浮点，整除用 math.floor"],
                    ["比较", "== ~= < > <= >=", "结果是 boolean"],
                    ["逻辑", "and or not", "and/or 返回操作数，not 返回 boolean"],
                    ["拼接", "..", "任一侧是数字时会转成字符串"],
                    ["长度", "#", "字符串字节数或序列长度"],
                ],
            ),
            p("优先级从高到低大致是：^、一元运算符、* / %、+ -、..、比较、not、and、or。实际写代码时不必背这张表，拿不准就加括号，括号不会带来运行时开销，却能让意图一眼可见。还有一个词法陷阱：数字后面直接跟 .. 会被解析成小数点，所以 1..2 会报错，必须写成 1 .. 2，或者给数字加括号 (1)..'x'。同理，a - -b 中间要有空格，否则 -- 会被当成注释开头，后面的代码整段消失，而且不报错，这类静默错误比语法错误更难查。"),
            *code(
                r"""print(1 < 2, 2 <= 2, 'a' < 'b')
print(nil == false, 0 == false)
print(1 and 2, nil and 2, false or 'fallback')
local x = nil
print(x or 0)
print(2 + 3 * 4, (2 + 3) * 4)""",
                "true\ttrue\ttrue\nfalse\tfalse\n2\tnil\tfallback\n0\n14\t20",
            ),
            p("练习里用到了四舍五入到两位小数的写法，这个套路值得单独记一下：先乘以 100，把要保留的两位推到整数部分，加 0.5 完成四舍五入，再用 math.floor 截断，最后除以 100 还原量级。之所以不用 string.format 再 tonumber，是因为格式化涉及字符串解析，既慢又容易在边界上出意外；纯算术的版本行为稳定，也不会因为本地化设置改变小数点符号。代价是它只适合非负数，负数要改成减 0.5，或者先取绝对值再还原符号。理解这个推导过程，比背一行代码有用得多，遇到保留三位、保留到分、向上取整等变体时都能自己推出来。"),
            tip("x = x or default 只适合「nil 才取默认值」的场景。如果 false 是合法值，这个写法会把 false 也替换掉，应改用 if x == nil then x = default end。"),
            quiz(
                "表达式 7 / 2 的结果是？",
                ["3", "3.5", "4", "报错"],
                1,
                "Lua 的 / 永远做浮点除法，结果是 3.5。要整数商写 math.floor(7 / 2)，得到 3。",
            ),
        ],
        exercise(
            "平分账单",
            "实现 split_bill(total, people)：返回每人应付金额，保留两位小数；people 小于 1 时返回 0。用 math.floor(x * 100 + 0.5) / 100 做四舍五入。",
            "function split_bill(total, people)\n  \nend\n\nprint(split_bill(100, 3))",
            "先算 share = total / people，再用 math.floor(share * 100 + 0.5) / 100 保留两位。",
            [
                "assert(split_bill(100, 3) == 33.33, '100 分给 3 人应约为 33.33')",
                "assert(split_bill(90, 3) == 30, '整除时应得到 30')",
                "assert(split_bill(10, 4) == 2.5, '小数结果应保留')",
                "assert(split_bill(50, 0) == 0, '人数为 0 应返回 0')",
            ],
            "function split_bill(total, people)\n  if people < 1 then return 0 end\n  local share = total / people\n  return math.floor(share * 100 + 0.5) / 100\nend\n",
            90,
        ),
    ))

    items.append(lesson(
        "lua04", 403, 41, BASIC, "字符串", "不可变值与常用操作", 70,
        [
            h("字符串是不可变值"),
            p("Lua 的字符串是一串字节，不是字符数组。它不可变：所有看起来像修改的操作都会返回一个新串，原串保持不变。取长度用 #，拼接用两个点 ..，截取用 string.sub，查找用 string.find。字符串可以用单引号或双引号包裹，转义序列 \\n、\\t、\\\\ 在两种引号里都生效，写 Windows 路径时尤其要注意反斜杠需要写成两个。因为不可变，重复拼接大量字符串会产生很多临时对象，工程上更推荐先用 table 收集再 concat，一次性拼出结果，性能差距在循环里会非常明显。"),
            p("需要写多行文本时，用长括号 [[ ... ]] 包起来，里面的换行会原样保留，转义序列不生效。如果内容本身含有 ]]，可以用 [==[ ... ]==] 这种带等号的写法，等号数量只要不与内容冲突即可。长字符串在写 SQL、配置样例、说明文字时很方便，但它同样是一个值，可以参与拼接和比较，也可以直接 print 出来。注意长字符串开头的第一个换行会被保留，如果不想要它，把 [[ 和正文写在同一行，否则输出会多出一个空行，这种差一个换行的 bug 在拼接协议报文时特别常见。"),
            p("字符串可以用冒号语法调用 string 库的函数：s:upper() 等价于 string.upper(s)，冒号会把 s 自动作为第一个参数传进去。这是 Lua 面向对象风格的基础，后面学元表和模块时会反复用到。注意 s:sub(1, 3) 的下标从 1 开始，负数表示从末尾倒数，-1 是最后一个字节，-2 是倒数第二个；sub 的两个下标都是闭区间，超出范围会被自动裁剪，不会报错。find 成功时返回起止两个下标，失败返回 nil，所以判断「找没找到」要写 if s:find(x) then，而不是 if s:find(x) == 1。"),
            p("string.format 是最实用的格式化工具，%s 接字符串，%d 接整数，%03d 补前导零，%% 输出百分号。它的参数类型检查比 print 严格，%d 收到字符串会直接报错，这反而帮你更早发现类型问题。日常拼接短文本用 .. 就够了，只有需要对齐、补零时才用 format，两者不要混着写得太复杂，可读性会下降。注意这个运行时对精度修饰的支持不完整，想要两位小数要先用算术四舍五入，再交给 %s 输出。下一篇章讲 string 库时会把常用函数一次列全，这里先建立基本手感。"),
            *code(
                r"""local s = 'Night City'
print(#s)
print(s .. ' 2077')
print(s:upper())
print(s:sub(1, 5))
print(s:find('City'))""",
                "10\nNight City 2077\nNIGHT CITY\nNight\n7\t10",
            ),
            table(
                ["写法", "作用", "结果示例"],
                [
                    ["#s", "取字节长度", "#'Lua' → 3"],
                    ["a .. b", "拼接", "'Lua' .. '5.2' → 'Lua5.2'"],
                    ["s:sub(i, j)", "截取，下标从 1 开始", "('hello'):sub(2, 3) → 'el'"],
                    ["s:upper()", "转大写", "('lua'):upper() → 'LUA'"],
                    ["s:find(p)", "查找位置", "('hello'):find('l') → 3"],
                    ["s:rep(n)", "重复 n 次", "('ab'):rep(2) → 'abab'"],
                ],
            ),
            p("字符串比较使用 == 和 <，按字节逐个比较字典序。中文在 UTF-8 下占多个字节，所以 # 得到的是字节数而不是汉字个数，截取时也要小心不要切在半个字符上。本课程只处理 ASCII 文本，就是为了避开这个坑；真实项目里处理中文要引入专门的 UTF-8 库，或者干脆只在显示层处理，存储与传输层保持字节透明。string.find 默认按模式匹配，要找纯文本时把第四个参数设为 true，或者对特殊字符做转义，这一点在下一篇章讲模式匹配时会详细展开。"),
            *code(
                r"""print('a\tb\nc')
print([[第一行
第二行]])
print(string.rep('lua', 3))
print(string.format('%s v%d', 'Lua', 52))""",
                "a\tb\nc\n第一行\n第二行\nlualualua\nLua v52",
            ),
            p("这一讲练习的关键在于边界：长度 0、1、2 都要单独考虑，因为此时没有「中间部分」可以替换，随便套用公式就会得到负的重复次数，string.rep 会直接报错。写这类字符串函数时，先把所有可能的长度区间列出来，再决定每个区间怎么处理，最后才开始写代码。这个「先分类再实现」的习惯，比边写边试要快，也能避免测到最后一个用例才发现漏了一种情况。练完之后可以自己试着改写成只保留前两个字符、或者把中间换成指定符号，验证你是否真的理解了拼接与截取的下标关系。"),
            warn("数字后面直接跟 .. 会被词法分析成小数点，例如 1..2 会报错。正确写法是 1 .. 2，或者给数字加括号 (1)..'x'。"),
            quiz("表达式 #'Lua' 的值是？", ["2", "3", "4", "nil"], 1, "# 返回字符串的字节数，'Lua' 有三个 ASCII 字符，结果是 3。"),
        ],
        exercise(
            "遮罩中间字符",
            "实现 mask(s)：保留首尾字符，中间全部替换为 *；长度小于等于 2 时原样返回；空串返回空串。",
            "function mask(s)\n  \nend\n\nprint(mask('secret'))",
            "先判断 #s <= 2，再用 string.rep('*', #s - 2) 生成中间部分。",
            [
                "assert(mask('secret') == 's****t', 'secret 应变成 s****t')",
                "assert(mask('ab') == 'ab', '两个字符应原样返回')",
                "assert(mask('a') == 'a', '单个字符应原样返回')",
                "assert(mask('') == '', '空串应返回空串')",
            ],
            "function mask(s)\n  if #s <= 2 then return s end\n  return s:sub(1, 1) .. string.rep('*', #s - 2) .. s:sub(-1)\nend\n",
            90,
        ),
    ))

    items.append(lesson(
        "lua05", 404, 41, BASIC, "条件", "if / elseif / else 与真值", 70,
        [
            h("分支决定走向"),
            p("Lua 的条件语句写作 if 条件 then ... elseif 条件 then ... else ... end。每个分支以 then 开始，整条语句以一个 end 结束。elseif 是一个关键字，不能拆成 else if 两个词再省掉一个 end；如果确实要嵌套，就必须写完整的 if ... end，多一层缩进多一个 end。把最可能命中的条件放在前面，可以减少无谓的判断，也更容易读懂，这在权限判断、折扣计算这类多级规则里尤其明显。条件本身可以用括号分组，但不要为了「看起来像 C」而加多余的括号，Lua 的优先级已经足够清晰。"),
            p("Lua 的真值规则非常简单：只有 nil 和 false 是假，其他一切都是真。这一点和 Python、JavaScript 都不同——数字 0 是真，空字符串 '' 是真，字符串 'false' 也是真，空表 {} 同样是真。从其他语言转过来的人最常写的 bug 就是 if 0 then，以为不会进入分支，实际一定会进入，而且不会报任何错误，只能靠读代码或加打印才能发现。理解这条规则之后，很多看似奇怪的判断都能解释通，比如为什么 count or 0 能正常工作，而 count == 0 的判断却要单独写。"),
            p("条件表达式可以是任意值，不需要显式转换成 boolean。判断相等用 ==，判断不等用 ~=。比较时注意类型：1 == '1' 为假，Lua 不做跨类型比较，也不会像 JavaScript 那样做隐式转换。需要判断一个值「既不是 nil 也不是 false」时，直接写 if v then 就是最准确的写法，不需要再和 true 比较。判断「不是 nil」则要写 if v ~= nil then，因为 false 也满足 ~= nil，但通不过 if v then。这两种语义在不同场景下各有用途，写之前先想清楚你要防的是「没传」还是「传了假值」，否则默认值逻辑会悄悄出错。"),
            p("多分支判断要按范围从大到小或从小到大排列，避免前面的分支吃掉后面的情况。上面的 access 从高等级往低等级判断，所以 120 命中第一个分支，66 命中第二个，3 落到 else。如果把 level >= 50 放在最前面，120 就会被错误地判成 OPERATOR。这个顺序问题在成绩、权限、折扣率等场景里非常常见，写完条件后最好拿边界值走一遍：刚好等于阈值、刚好小于阈值、以及超出范围的极端值，三组数据都对了才算写对。"),
            *code(
                r"""local function access(level)
  if level >= 100 then
    return 'ROOT'
  elseif level >= 50 then
    return 'OPERATOR'
  else
    return 'GUEST'
  end
end
print(access(120), access(66), access(3))""",
                "ROOT\tOPERATOR\tGUEST",
            ),
            table(
                ["值", "if v then 的结果", "说明"],
                [
                    ["nil", "假", "空值"],
                    ["false", "假", "唯一的布尔假"],
                    ["0", "真", "数字零也是真"],
                    ["''", "真", "空字符串也是真"],
                    ["'false'", "真", "非空字符串都是真"],
                    ["{}", "真", "空表也是真"],
                ],
            ),
            p("条件写得多的时候，可以考虑用「提前返回」来扁平化结构：先判断非法输入直接 return，再判断主流程的几种情况，最后兜底。这样每个分支都很短，不需要在脑子里维护多层嵌套的括号关系。另一个常见做法是把判断条件抽成一个有名字的小函数，比如 can_access(user, level)，条件表达式本身变成一句自然的英文，读起来比一串 and or 清楚得多。命名是廉价的文档，尤其在条件复杂的业务代码里。"),
            *code(
                r"""local function truthy(v)
  if v then return 'true' else return 'false' end
end
print(truthy(0), truthy(''), truthy(false), truthy(nil))
print(0 == false, not 0, not nil)""",
                "true\ttrue\tfalse\tfalse\nfalse\tfalse\ttrue",
            ),
            p("还有一个细节值得记住：Lua 不允许在条件里声明变量，写 if local x = f() then 是语法错误，必须先声明并赋值，再在条件里判断。这个限制看起来无关紧要，但它逼着你把「求值」和「判断」分成两步，反而让代码更清晰。写完条件分支后，拿几个特殊值手动走一遍：nil、false、0、空字符串，看看每个分支是否符合预期。这四组数据能覆盖 Lua 真值规则里绝大多数坑，也能顺带验证你的默认值逻辑有没有把 false 误当成缺失。"),
            warn("不要写 if v == true then 来判断真值，这只对 boolean 成立。要判断「有值且不为 false」，直接写 if v then；要判断「不是 nil」，写 if v ~= nil then。"),
            quiz("执行 if 0 then print('yes') else print('no') end，输出是？", ["yes", "no", "报错", "什么都不输出"], 0, "Lua 里只有 nil 和 false 为假，数字 0 是真，所以进入 then 分支输出 yes。"),
        ],
        exercise(
            "等级判定",
            "实现 grade(score)：90 分及以上返回 'A'，60 分及以上返回 'B'，其余返回 'C'；score 不是数字时返回 'INVALID'。",
            "function grade(score)\n  \nend\n\nprint(grade(95))",
            "先用 type(score) ~= 'number' 拦住非法输入，再按从高到低判断。",
            [
                "assert(grade(95) == 'A', '95 应为 A')",
                "assert(grade(90) == 'A', '90 应为 A')",
                "assert(grade(60) == 'B', '60 应为 B')",
                "assert(grade(59) == 'C', '59 应为 C')",
                "assert(grade('90') == 'INVALID', '字符串应判为 INVALID')",
            ],
            "function grade(score)\n  if type(score) ~= 'number' then return 'INVALID' end\n  if score >= 90 then return 'A' end\n  if score >= 60 then return 'B' end\n  return 'C'\nend\n",
            90,
        ),
    ))

    items.append(lesson(
        "lua06", 405, 41, BASIC, "循环", "for / while / repeat", 70,
        [
            h("重复直到完成"),
            p("Lua 有三种循环。数值 for 写作 for i = 起始, 终止, 步长 do ... end，起始和终止都包含在内，步长可以省略（默认 1），也可以是负数。while 条件 do ... end 在每轮开始前检查条件。repeat ... until 条件则先执行一次循环体，再检查条件，所以循环体至少执行一次，这个差异在「必须先做一次」的场景里很关键，比如先读一次再判断是否继续。三种写法没有优劣，选最贴合语义的那一种，代码自然就清楚了，硬套某一种反而会把逻辑拧巴，让别人多花时间理解。"),
            p("循环变量在数值 for 里是局部变量，离开循环就不可见。循环次数在开始时就已经确定，循环体内修改 i 不会影响下一轮的值——它下一轮会被重新赋值。需要提前结束时用 break，它只会跳出最近的一层循环，嵌套循环里要跳出外层就得借助标志变量或把内层抽成函数。Lua 没有 continue，想跳过某些情况时把剩余逻辑包进 if 里，或者改用 while 手动控制，不要把代码写成难以理解的绕行结构。可读性比技巧重要，尤其是循环这种会反复执行的地方，一旦出错就要反复调试。"),
            p("写循环时要特别注意边界和终止条件。for i = 1, #t 是最常见的数组遍历写法，但 #t 在循环中如果表被修改会重新求值，容易出错；需要增删元素时先用 local n = #t 存下长度，或者改成从后往前遍历。死循环在沙箱里会被指令看门狗中断，但那是保护机制，不应该当作控制流程的手段。判断循环是否正确，可以拿 0 次、1 次、正好到边界、超过边界这四种输入各跑一遍，四种都通过，基本就能排除大部分差一错误，剩下的问题通常出在循环体内部的累加逻辑上。"),
            p("while 和 repeat 的区别只在第一次判断的位置。需要「先做再判断」的场景，比如累加直到超过阈值、反复尝试直到成功，repeat 更自然。但 repeat 的条件在循环体之后求值，循环体里定义的局部变量在 until 条件里仍然可见，这是它和 while 的一个重要差异，初学时容易忽略。另外，repeat 的条件是「继续循环的条件」取反——until k >= 7 的意思是「直到 k 大于等于 7 才停」，和 while k < 7 表达的是同一件事，别把方向写反，写反了循环要么一次都不跑，要么永远停不下来。"),
            *code(
                r"""local sum = 0
for i = 1, 10 do
  sum = sum + i
end
print('sum', sum)

for i = 10, 1, -3 do
  print('i', i)
end""",
                "sum\t55\ni\t10\ni\t7\ni\t4\ni\t1",
            ),
            table(
                ["循环", "写法", "适用场景"],
                [
                    ["数值 for", "for i = 1, n do ... end", "已知次数，按整数计数"],
                    ["泛型 for", "for k, v in pairs(t) do ... end", "遍历表或迭代器"],
                    ["while", "while cond do ... end", "次数未知，先判断后执行"],
                    ["repeat", "repeat ... until cond", "至少执行一次，直到条件成立"],
                    ["break", "break", "立即跳出最近一层循环"],
                ],
            ),
            p("还有一个实用技巧：循环里如果只需要值不需要下标，用 for _, v in ipairs(t) 把下标位写成下划线，是一种约定俗成的「我不关心这个变量」的信号。表是引用时，循环中修改元素会直接影响原表，如果调用方还要用原始数据，记得先复制。遇到「循环里套循环」且内层依赖外层变量时，先在本子上画出两层的取值范围，再动手写，比直接敲代码快得多，也少返工。"),
            *code(
                r"""local n = 0
while n < 3 do
  n = n + 1
end
print('while', n)

local k = 0
repeat
  k = k + 2
until k >= 7
print('repeat', k)

local found = nil
for i = 1, 100 do
  if i * i > 50 then
    found = i
    break
  end
end
print('found', found)""",
                "while\t3\nrepeat\t8\nfound\t8",
            ),
            tip("从 1 到 n 累加可以直接用公式 n * (n + 1) / 2，但初学阶段先用循环把过程写清楚，再考虑优化。"),
            quiz("for i = 10, 1, -3 do ... end 一共循环几次？", ["3", "4", "5", "无限"], 1, "取值依次是 10、7、4、1，共 4 次；步长为负时只要 i 不小于终止值就继续。"),
        ],
        exercise(
            "数位统计",
            "实现 count_digits(n)：返回非负整数 n 的十进制位数；n 为 0 时返回 1。",
            "function count_digits(n)\n  \nend\n\nprint(count_digits(1234))",
            "用 while 循环，每轮 n = math.floor(n / 10)，计数器加一，直到 n 变成 0。",
            [
                "assert(count_digits(0) == 1, '0 应算 1 位')",
                "assert(count_digits(7) == 1, '7 应算 1 位')",
                "assert(count_digits(1234) == 4, '1234 应算 4 位')",
                "assert(count_digits(100) == 3, '100 应算 3 位')",
            ],
            "function count_digits(n)\n  if n == 0 then return 1 end\n  local count = 0\n  while n > 0 do\n    count = count + 1\n    n = math.floor(n / 10)\n  end\n  return count\nend\n",
            90,
        ),
    ))

    items.append(lesson(
        "lua07", 406, 41, BASIC, "函数", "定义、参数与默认值", 80,
        [
            h("函数是值"),
            p("Lua 用 function 名字(参数) ... end 定义函数，也可以用匿名函数 function(x) ... end 直接写出一个值。函数是一等公民：可以赋给变量、放进表、作为参数传给另一个函数、作为返回值。这一点是后面闭包、函数式编程和元表的基础，值得从一开始就建立正确的心智模型，而不是把它当成别的语言里的「方法」来理解。换句话说，function 关键字只是「创建一个函数值并赋值给某个名字」的语法糖，名字本身并不特殊，随时可以被重新赋值，也可以同时指向两个名字。"),
            p("调用函数时，实参按位置对应形参。多传的参数会被忽略，少传的参数取 nil。利用这个特性可以写默认值：在函数体开头写 greeting = greeting or '你好'。但这个写法对 false 不友好，如果 false 是合法取值，应该写成 if greeting == nil then greeting = '你好' end。参数个数不匹配不会报错，所以边界检查要自己写；这也是 Lua 代码里常见的一类 bug——把参数顺序写反了，类型刚好都能算，结果悄悄算错，而且没有任何异常提示，只能靠测试覆盖，或者靠命名让顺序一目了然。"),
            p("函数可以返回任意多个值，用 return 一次返回，调用方用逗号接收。没有显式 return 的函数返回 nil。定义在表里的函数用冒号调用时会自动把表本身作为第一个参数，这就是方法。Lua 没有函数重载，同名函数后定义的会覆盖先定义的，所以复用要靠不同的名字或表字段来区分，而不是靠参数类型。函数体里 return 之后的代码不会执行，提前返回能让嵌套层级变浅，是 Lua 里很常见的写法，尤其在参数校验阶段先挡掉非法输入，主逻辑就能保持平整。"),
            p("把函数作为参数传递时，注意它本身是「值」而不是「调用结果」。写 apply(double, 5) 传的是函数本身，写 apply(double(), 5) 则会先调用 double 再把返回值传进去，通常不是你想要的结果。命名上把函数参数叫做 f、fn 或 callback，能让代码更易读，也方便区分它和普通数据参数。函数作为返回值时，它携带的外部局部变量会一起被保留下来，这就是下一篇章要展开的闭包机制的雏形，也是 Lua 实现模块私有状态的标准手法，后面会反复见到。"),
            *code(
                r"""local function add(a, b)
  return a + b
end
print(add(2, 3))

local double = function(x)
  return x * 2
end
print(double(21))

local function greet(name, greeting)
  greeting = greeting or '你好'
  return greeting .. '，' .. name
end
print(greet('V'))
print(greet('V', '欢迎'))""",
                "5\n42\n你好，V\n欢迎，V",
            ),
            table(
                ["写法", "说明", "示例"],
                [
                    ["function f() end", "具名函数", "function add(a, b)"],
                    ["local function f()", "局部具名函数", "只在当前块可见"],
                    ["local f = function()", "匿名函数赋给变量", "适合回调和工厂"],
                    ["t.method = function()", "表字段函数", "用 t.method() 调用"],
                    ["function t:m()", "方法简写", "等价于 t.m = function(self)"],
                    ["return a, b", "返回多个值", "local x, y = f()"],
                ],
            ),
            p("函数体不要写得太长。一个函数如果超过四五十行，通常说明它同时做了好几件事，可以按「校验、计算、组装输出」拆开。拆分之后每个函数都能单独测试，出错时也能快速定位是哪一段。Lua 没有模块系统内置的类型检查，函数的输入输出契约只能靠命名、注释和测试来保证，所以把函数切小、把边界写清楚，收益比在其他语言里更大。"),
            *code(
                r"""local function double(x)
  return x * 2
end
local function apply(f, x)
  return f(x)
end
print(apply(double, 5))
print(apply(function(x) return x * x end, 6))

local ops = {
  add = function(a, b) return a + b end,
  mul = function(a, b) return a * b end
}
print(ops.add(2, 3), ops.mul(2, 3))""",
                "10\n36\n5\t6",
            ),
            tip("局部函数要先声明再调用。写成 local function f() ... end 时，Lua 会自动把 f 声明为局部变量，所以函数体里可以递归调用自己。"),
            quiz("调用只接收两个参数的函数时多传了一个参数，会发生什么？", ["报错", "多余参数被忽略", "第二个参数变成 nil", "自动截断为两个"], 1, "Lua 不会因为参数个数不匹配报错，多余的实参被忽略，缺少的形参取 nil。"),
        ],
        exercise(
            "区间夹取",
            "实现 clamp(v, lo, hi)：把 v 限制在 [lo, hi] 之间；lo 默认 0，hi 默认 100。",
            "function clamp(v, lo, hi)\n  \nend\n\nprint(clamp(150))",
            "先用 lo = lo or 0、hi = hi or 100 补默认值，再依次判断 v < lo 和 v > hi。",
            [
                "assert(clamp(150) == 100, '超过上限应夹到 100')",
                "assert(clamp(-5) == 0, '低于下限应夹到 0')",
                "assert(clamp(50) == 50, '区间内应原样返回')",
                "assert(clamp(5, 10, 20) == 10, '自定义下限应生效')",
                "assert(clamp(30, 10, 20) == 20, '自定义上限应生效')",
            ],
            "function clamp(v, lo, hi)\n  lo = lo or 0\n  hi = hi or 100\n  if v < lo then return lo end\n  if v > hi then return hi end\n  return v\nend\n",
            100,
        ),
    ))

    items.append(lesson(
        "lua08", 407, 41, BASIC, "表（数组）", "从 1 开始的序列", 80,
        [
            h("从 1 开始的序列"),
            p("table 是 Lua 唯一的内置容器，它同时承担数组和字典两种角色。用 {10, 20, 30} 这样的构造式创建的是数组风格的表，元素自动获得 1、2、3 的下标。注意下标从 1 开始，这是 Lua 和大多数语言最显眼的差异，t[0] 永远是 nil。没有元素时用 {} 创建空表，之后用 table.insert 逐个添加。数组的边界由 # 返回，但只有连续序列才可靠，中间有空洞时结果不确定，这一点在删除元素之后尤其容易踩坑，因为删除会让后面的元素整体前移。"),
            p("取长度用 #t，它返回表的边界：对于连续的数组就是元素个数。table.insert 在末尾追加，也可以指定位置插入并把后面的元素整体后移；table.remove 删除末尾元素并返回它，也可以指定位置删除。table.concat 把数组元素用分隔符连成字符串，是输出数组最常用的方式，元素必须是字符串或数字，否则会报错。这几个函数覆盖了日常九成的数组操作，先记牢它们，再去看 table.sort 之类的排序函数，学习曲线会平缓很多，也不容易在边界上出错。"),
            p("表是引用类型。local b = a 只是让 b 指向同一张表，修改 b 的内容 a 也会看到。需要独立副本时必须显式复制，可以手写循环，也可以借助 table 库逐个搬运。判断两张表是否相等用 ==，比较的是引用而不是内容，所以内容完全相同的两张表也不相等。这个特性在传参时影响很大：函数内部修改表会影响调用方，除非你复制一份再改。想清楚「共享」还是「拷贝」，是写 Lua 时最基本的设计决策之一，也是很多隐蔽 bug 的源头。"),
            p("遍历数组用 ipairs，它从 1 开始按顺序返回下标和值，遇到 nil 就停止；遍历字典用 pairs，顺序不保证。二维表就是「表里装表」，grid[2][3] 先取第二行再取第三个元素。构造二维表时每一行的长度可以不同，Lua 不会做矩阵形状检查，越界访问只会得到 nil，所以真实项目里要自己维护行数列数。删除元素时从后往前遍历，可以避免下标错位导致漏删；如果一定要从前往后，删除后要把循环变量停在原地重新检查，否则会跳过紧挨着的那个元素。"),
            *code(
                r"""local t = {10, 20, 30}
print(#t, t[1], t[3])
table.insert(t, 40)
table.insert(t, 1, 5)
print(#t, t[1], t[5])
print(table.remove(t))
print(table.concat(t, ','))""",
                "3\t10\t30\n5\t5\t40\n40\n5,10,20,30",
            ),
            table(
                ["操作", "写法", "说明"],
                [
                    ["创建", "local t = {1, 2, 3}", "下标从 1 开始"],
                    ["取长度", "#t", "连续序列才可靠"],
                    ["追加", "table.insert(t, v)", "加到末尾"],
                    ["插入", "table.insert(t, i, v)", "插到位置 i，后面后移"],
                    ["删除", "table.remove(t [, i])", "返回被删除的元素"],
                    ["拼接", "table.concat(t, sep)", "元素必须是字符串或数字"],
                ],
            ),
            p("数组最常见的用途是批量处理和排序。table.sort 默认按升序排列，元素必须是同类型且可比较；要降序或按自定义规则排序时传第二个参数，一个返回 a 是否应排在 b 前面的函数。排序会直接修改原表，不想破坏原始顺序就先把元素复制一份。数字和字符串可以混排吗？不行，比较不同类型会抛错。真实数据里经常需要「按某个字段排序」，那就把每项包成表，再在比较函数里取字段，这是 Lua 里非常标准的写法。"),
            *code(
                r"""local a = {1, 2, 3}
local b = a
b[1] = 99
print(a[1], b[1])

local grid = {
  {1, 2, 3},
  {4, 5, 6}
}
print(#grid, #grid[1], grid[2][3])""",
                "99\t99\n2\t3\t6",
            ),
            warn("下标从 1 开始，不是 0。t[0] 不会报错，只会安静地返回 nil，这类 bug 往往要到很后面才暴露。"),
            quiz("local t = {10, 20, 30}，表达式 #t 的值是？", ["2", "3", "4", "nil"], 1, "构造式里有三个元素，下标 1 到 3，所以 #t 是 3。"),
        ],
        exercise(
            "偶数求和",
            "实现 sum_even(t)：返回数组 t 中所有偶数的和，空表返回 0。",
            "function sum_even(t)\n  \nend\n\nprint(sum_even({1,2,3,4}))",
            "用 ipairs 遍历，判断 v % 2 == 0 再累加。",
            [
                "assert(sum_even({1, 2, 3, 4}) == 6, '2 + 4 应为 6')",
                "assert(sum_even({}) == 0, '空表应为 0')",
                "assert(sum_even({2, 2}) == 4, '重复偶数应累加')",
                "assert(sum_even({1, 3}) == 0, '没有偶数应为 0')",
            ],
            "function sum_even(t)\n  local s = 0\n  for _, v in ipairs(t) do\n    if v % 2 == 0 then s = s + v end\n  end\n  return s\nend\n",
            100,
        ),
    ))

    items.append(lesson(
        "lua09", 408, 41, BASIC, "表（字典）", "键值映射与 pairs", 80,
        [
            h("键值映射"),
            p("同一个 table 也可以当字典用：{name = 'V', level = 66} 创建的是字符串键的表，等价于 {['name'] = 'V', ['level'] = 66}。访问时 hero.name 和 hero['level'] 两种写法都行，前者只是后者的语法糖。键必须是字符串或数字时才能用点号，含空格、连字符的键必须用方括号，否则会被解析成减法表达式。键也可以是数字、布尔甚至另一张表，但字符串键最常用，也最容易调试，所以设计数据结构时优先考虑字符串键，需要数字索引时再单独用数组。"),
            p("给一个键赋 nil 就等于删除这个键，因为 Lua 里「键不存在」和「键的值为 nil」是同一件事。判断键是否存在用 hero.name ~= nil，不要用 hero.name == false，后者会把 false 值误判成不存在。遍历字典用 pairs，它返回键和值，顺序由哈希实现决定，同一份数据在不同运行里可能不同，不能依赖。需要稳定顺序时，先把键收集到数组里，用 table.sort 排序，再按顺序访问，这是输出配置、生成报表时的标准做法，也是让测试结果可复现的前提。"),
            p("字典最常见的用途是计数和索引。统计词频时写 counts[w] = (counts[w] or 0) + 1，这一行同时完成了「取旧值、缺省为 0、加一、写回」四件事。注意括号不能省，否则 counts[w] or 0 + 1 会先算加法，整个表达式的结果就错了。需要按值排序输出时，把键值对收集成数组再排序，因为 pairs 本身不提供顺序，也不保证两次遍历顺序一致。缓存、索引、去重、分组这几类需求，本质上都是在字典上做文章，掌握这一讲，很多中等难度的题目都能拆开。"),
            p("字典的结构可以任意嵌套：值本身可以是表，表里再放表，这就构成了树和 JSON 风格的数据。读取深层字段时要考虑中间层可能为 nil，直接链式访问会抛「attempt to index a nil value」，稳妥的写法是逐层判断，或者写一个带默认值的取值函数。表作为键时比较的是引用，两个内容相同的表会被当成不同的键，这一点和字符串键的直觉不同，实际项目里很少这样用，真要用就得自己维护一个引用表，否则查不到自己刚放进去的东西。"),
            *code(
                r"""local hero = {name = 'V', level = 66, city = 'Night City'}
print(hero.name, hero['level'])
hero.level = 67
hero.job = 'netrunner'
print(hero.level, hero.job)

hero.city = nil
print(hero.city == nil)""",
                "V\t66\n67\tnetrunner\ntrue",
            ),
            table(
                ["写法", "含义", "示例"],
                [
                    ["hero.name", "点号访问字符串键", "等价于 hero['name']"],
                    ["hero['level']", "方括号访问", "键含特殊字符时必须用"],
                    ["hero.x = 1", "新增或修改", "键不存在就创建"],
                    ["hero.x = nil", "删除键", "之后 pairs 不再遍历到"],
                    ["pairs(hero)", "遍历全部键值", "顺序不保证"],
                    ["next(hero)", "取下一个键值对", "底层迭代函数"],
                ],
            ),
            p("判断「表里有没有数据」时，不要用 #t == 0，因为字典没有可靠的长度。正确写法是 next(t) == nil，next 返回第一个键值对，空表返回 nil。这个技巧在参数校验、缓存判空时很常用。另外，遍历过程中不要新增键，Lua 没有规定这种情况下会发生什么，实际表现可能漏遍历、也可能报错，稳妥的做法是先收集要改的键，遍历结束后再统一修改。"),
            *code(
                r"""local scores = {lua = 90, c = 80, sql = 70}
local keys = {}
for k in pairs(scores) do
  keys[#keys + 1] = k
end
table.sort(keys)
for _, k in ipairs(keys) do
  print(k, scores[k])
end""",
                "c\t80\nlua\t90\nsql\t70",
            ),
            p("把上面的排序输出拆开看，其实是两个经典套路的组合：先把无序的键收集成有序的数组，再按数组遍历。这个「收集、排序、访问」的三步模式，可以在任何需要稳定顺序的地方复用，比如生成配置文件的字段、输出排行榜、对比两次快照的差异。反过来，如果你的逻辑依赖 pairs 的顺序正确，那就是在依赖实现细节，换个 Lua 版本或换台机器就可能出错，测试也很难覆盖。判断标准很简单：代码里有没有对 pairs 结果做排序或收集，没有就说明你在赌运气。"),
            tip("统计词频的地道写法是 counts[w] = (counts[w] or 0) + 1。括号很关键，它保证先取旧值再做加法。"),
            quiz("读取一个不存在的键，得到的结果是？", ["0", "false", "nil", "报错"], 2, "Lua 里不存在的键返回 nil，不会自动创建，也不会报错。"),
        ],
        exercise(
            "词频统计",
            "实现 count_words(words)：words 是字符串数组，返回一个字典，键是单词，值是该单词出现的次数。",
            "function count_words(words)\n  \nend\n\nlocal r = count_words({'a', 'b', 'a'})\nprint(r.a, r.b)",
            "遍历数组，用 counts[w] = (counts[w] or 0) + 1 累加。",
            [
                "local r = count_words({'a', 'b', 'a'}); assert(r.a == 2, 'a 应出现 2 次')",
                "local r = count_words({'a', 'b', 'a'}); assert(r.b == 1, 'b 应出现 1 次')",
                "local r = count_words({}); assert(next(r) == nil, '空数组应返回空表')",
                "local r = count_words({'x'}); assert(r.x == 1, '单个单词应计为 1')",
            ],
            "function count_words(words)\n  local counts = {}\n  for _, w in ipairs(words) do\n    counts[w] = (counts[w] or 0) + 1\n  end\n  return counts\nend\n",
            100,
        ),
    ))

    items.append(lesson(
        "lua10", 409, 41, BASIC, "作用域与 local", "块、遮蔽与闭包预览", 90,
        [
            h("可见范围决定一切"),
            p("Lua 的作用域以块为单位：do ... end、if 分支、for 循环体、function 函数体都会创建新的作用域。用 local 声明的变量只在当前块及其嵌套块里可见，离开块就消失。没有 local 的赋值会写到全局表 _G 上，整个程序都能访问，也容易在不知不觉间互相覆盖。所以除了真正需要跨文件共享的入口函数，其他一律应该 local：文件顶层的辅助函数、常量、临时表，全都用局部变量。这条规则看起来琐碎，却是 Lua 项目可维护性的分水岭，也是代码评审时最该盯的一点。"),
            p("同名变量可以在内层块里遮蔽外层变量：内层的 local x 是全新的变量，赋值不会影响外层。这种机制让临时变量可以放心复用名字，但也会造成「改了却没生效」的困惑。读代码时先找最近的 local 声明，再看它属于哪个块，就能确定看到的是哪一个变量，调试作用域问题时按这个顺序排查最快。循环里的 local 尤其要注意：每次迭代都会创建新的变量，所以闭包捕获的是当轮的值，这一点和某些语言共享同一个循环变量的行为不同，写回调时要利用好它。"),
            p("局部变量还有一个关键特性：它会被闭包捕获。函数内部引用的外层 local 变量，在函数返回之后依然存在，这叫 upvalue。下面第二段代码里，bump 记住了 counter，每次调用都让同一个 counter 加一；而 scope_demo 里的 value 是函数内部的局部变量，函数返回后外部访问不到，所以打印出来是 nil。理解这一点，就理解了 Lua 为什么能在没有 class 的情况下实现状态封装，也理解了后面模块为什么要用一个表把所有私有状态包起来，再通过函数暴露有限的接口。"),
            p("工程上有一条简单规则：文件顶层的辅助函数、常量、临时表都用 local，这样加载这个文件不会往全局命名空间里塞任何东西。多个文件组合时，全局变量是最容易冲突的地方，而 local 把冲突范围限制在一个文件甚至一个块里，排查成本低得多。模块化的本质就是「用一个表把一组相关的 local 装起来，只暴露必要的字段」，下一篇章讲模块时会把这一套做法完整走一遍，包括怎么避免循环依赖、怎么让私有函数真正私有。"),
            *code(
                r"""local x = 10
do
  local x = 20
  print('inner', x)
end
print('outer', x)

function global_fn()
  return 'global'
end
print(global_fn(), type(global_fn))""",
                "inner\t20\nouter\t10\nglobal\tfunction",
            ),
            table(
                ["声明方式", "可见范围", "生命周期"],
                [
                    ["local x（块内）", "当前块及嵌套块", "离开块即释放"],
                    ["local x（函数内）", "整个函数体", "每次调用重新创建"],
                    ["x = 1（无 local）", "全局，_G 上", "直到被覆盖或置 nil"],
                    ["for 循环变量", "循环体内部", "每轮一个新变量"],
                    ["函数参数", "函数体内部", "每次调用重新绑定"],
                ],
            ),
            p("初学者常问：既然 local 这么好，为什么还要全局变量？答案是有些东西确实需要跨文件共享，比如入口函数、配置表、注册表。但这类共享应该显式设计、集中管理，而不是随手赋值。判断标准很简单：如果这个变量只在一个文件里用，就 local；如果确实要给别的文件用，就通过模块表显式导出，而不是挂在 _G 上。把所有隐式共享改成显式导出，代码的可追踪性会提升一个档次，也更容易做单元测试。"),
            *code(
                r"""local counter = 0
local function bump()
  counter = counter + 1
  return counter
end
print(bump(), bump(), bump())

local function scope_demo()
  local value = 'local'
  return value
end
print(scope_demo(), value)""",
                "1\t2\t3\nlocal\tnil",
            ),
            warn("在函数里忘记写 local 会创建全局变量，多个函数之间可能互相污染。课程里的练习函数必须写成全局函数，但函数内部使用的临时变量一律加 local。"),
            quiz("在 do ... end 块里声明 local x = 1，块结束后在块外访问 x，结果是？", ["1", "nil", "报错", "0"], 1, "local 只在块内可见，块结束后变量已经不存在，访问得到 nil（不会报错）。"),
        ],
        exercise(
            "计数器工厂",
            "实现 make_counter()：返回一个函数，每次调用返回递增的计数，从 1 开始；不同次调用 make_counter 得到的计数器互不影响。",
            "function make_counter()\n  \nend\n\nlocal c = make_counter()\nprint(c(), c())",
            "在 make_counter 里声明 local n = 0，返回一个匿名函数，函数体里让 n 加一并返回。",
            [
                "local c = make_counter(); assert(c() == 1, '第一次应为 1')",
                "local c = make_counter(); c(); assert(c() == 2, '第二次应为 2')",
                "local a, b = make_counter(), make_counter(); a(); assert(b() == 1, '两个计数器应互相独立')",
                "local c = make_counter(); c(); c(); assert(c() == 3, '连续调用应递增到 3')",
            ],
            "function make_counter()\n  local n = 0\n  return function()\n    n = n + 1\n    return n\n  end\nend\n",
            110,
        ),
    ))

    return items


def _core_11_15():
    items = []

    items.append(lesson(
        "lua11", 410, 42, CORE, "多返回值", "一次返回，多个接收", 70,
        [
            h("函数可以一次交回多个结果"),
            p("Lua 的函数天然支持多返回值，不需要打包成数组或对象。写法就是在 return 后面用逗号列出多个表达式，调用方也用逗号接收。最经典的例子是 divmod：一次返回商和余数，调用方写 local q, r = divmod(7, 2)，两个变量各拿一个值。这个特性在需要同时给出「结果和状态」「值和错误」时特别自然，省掉了很多临时结构体。比起其他语言里返回一个元组或对象再拆开，Lua 的写法更直接，运行时也不需要额外分配容器，尤其适合底层工具函数。"),
            p("多返回值在表达式里的展开规则有一条容易被忽略的边界：只有放在列表末尾的函数调用才会展开成多个值，放在中间或在括号里都会被截断成一个值。print(f(), 3) 只拿到 f 的第一个返回值，print((f())) 因为加了括号也只拿一个。表构造式 {f()} 是例外，它会把 f 的所有返回值依次填进去，但 {f(), 3} 又只保留第一个。记住「末尾才展开」这条规则，能避免大量诡异的调试时间，因为错误不会报，只是值悄悄少了一个。"),
            p("接收端也有细节：local a, b = f() 会按位置分配，多余的返回值被丢弃，不够的补 nil。如果只关心第二个返回值，可以写 local _, second = f()，下划线是约定俗成的占位符，不是特殊语法。函数作为实参传递时，前面的实参如果也是函数调用，只有最后一个会展开，其余都只取首值。这些规则不需要背，写几段小实验跑一遍，看到输出就理解了，而且比读文档记得牢。"),
            p("select 是配合多返回值使用的工具：select('#', ...) 返回参数个数，select(n, ...) 返回从第 n 个开始的所有参数，n 为负数时从末尾倒数。它在写可变参数函数时几乎是必备的，因为 # 对参数列表不适用。很多初学者会用 {...} 把参数打包成表再取长度，这在参数含 nil 时会丢信息，select('#', ...) 才是准确的口径。下一讲讲可变参数时会详细展开，这里先知道它和返回值计数有关即可。"),
            *code(
                r"""local function divmod(a, b)
  return math.floor(a / b), a % b
end
local q, r = divmod(7, 2)
print(q, r)

local function two()
  return 'A', 'B'
end
print(two(), 'C')
print((two()))
print(select('#', two()))""",
                "3\t1\nA\tC\nA\n2",
            ),
            table(
                ["写法", "结果", "说明"],
                [
                    ["local a, b = f()", "按位置接收", "多余的丢弃，不够补 nil"],
                    ["print(f(), 3)", "只取第一个返回值", "非末尾调用被截断"],
                    ["print((f()))", "只取第一个返回值", "括号强制单值"],
                    ["local t = {f()}", "全部填入表", "末尾调用会展开"],
                    ["local t = {f(), 3}", "只填第一个", "后面还有元素"],
                    ["select('#', f())", "返回值个数", "不受 nil 影响"],
                ],
            ),
            p("还有一类场景是「主结果 + 附加信息」。比如一个统计函数既返回总和，也返回最大值和最小值；一个解析函数既返回解析出的表，也返回剩余未消费的字符串。这种设计让调用方按需取用，不需要为了拿某个附带信息而重新遍历一遍。写这类函数时，把最重要的值放第一位，附加信息按重要性往后排，调用方只接第一个也不会出错。"),
            p("多返回值最实用的场景之一是「值 + 错误信息」。一个 parse 函数可以成功时返回结果和 nil，失败时返回 nil 和错误说明，调用方写 local value, err = parse(s)，先判断 value 是否为 nil 再决定后续流程。这和 pcall 的返回约定一致，也和很多 Lua 标准库的风格一致。比起抛异常，这种写法把错误处理放到调用方显式处理，不容易漏；比起返回一个带 ok 字段的表，它又更轻量，不需要额外的约定和字段命名。"),
            *code(
                r"""local function parse_int(s)
  local n = tonumber(s)
  if n == nil then
    return nil, '不是合法数字: ' .. s
  end
  return n, nil
end

local v, err = parse_int('42')
print(v, err)
local bad, msg = parse_int('abc')
print(bad, msg)""",
                "42\tnil\nnil\t不是合法数字: abc",
            ),
            tip("只想要第一个返回值时给调用加一层括号：(f())。这是 Lua 里强制「单值化」的标准写法，读别人代码时经常见到。"),
            quiz(
                "local function f() return 1, 2 end，print(f(), 3) 输出什么？",
                ["1 + tab + 2 + tab + 3", "1 + tab + 3", "1 + tab + 2", "报错"],
                1,
                "只有列表末尾的函数调用才展开多返回值，f() 在中间只贡献第一个值 1，所以输出是 1、制表符、3；选项里的 + tab + 表示制表符。",
            ),
        ],
        exercise(
            "商与余数",
            "实现 divmod(a, b)：返回商和余数两个值，商用 math.floor(a / b)。b 为 0 时返回 nil 和错误信息 'division by zero'。",
            "function divmod(a, b)\n  \nend\n\nlocal q, r = divmod(7, 2)\nprint(q, r)",
            "先用 if b == 0 then return nil, 'division by zero' end 挡住除零，再 return math.floor(a / b), a % b。",
            [
                "local q, r = divmod(7, 2); assert(q == 3, '7 / 2 的商应为 3')",
                "local q, r = divmod(7, 2); assert(r == 1, '7 % 2 的余数应为 1')",
                "local q, r = divmod(9, 3); assert(q == 3 and r == 0, '整除时余数应为 0')",
                "local q, e = divmod(1, 0); assert(q == nil, '除零应返回 nil')",
                "local q, e = divmod(1, 0); assert(e == 'division by zero', '除零应带错误信息')",
            ],
            "function divmod(a, b)\n  if b == 0 then return nil, 'division by zero' end\n  return math.floor(a / b), a % b\nend\n",
            100,
        ),
    ))

    items.append(lesson(
        "lua12", 411, 42, CORE, "可变参数", "... 与 select", 80,
        [
            h("接收未知数量的参数"),
            p("在参数列表最后写三个点 ...，函数就变成可变参数函数，调用时可以传任意多个实参。函数体里 ... 代表整个参数列表，可以整体转交给另一个函数，也可以用 select 按位置取。最典型的例子是包装 print：local function log(...) print('[LOG]', ...) end，所有实参原样传给内部的 print，不需要知道有几个。这种「透传」是 ... 最常见的用法，写日志、调试、代理函数时都会用到。"),
            p("要在函数体里逐个处理参数，有两种方式。第一种是 for i = 1, select('#', ...) do local v = select(i, ...) end，它不创建表，也不会因为 nil 丢信息；第二种是 local args = {...}，然后遍历数组，写法更顺手，但遇到 nil 时长度会提前截断，参数个数信息就丢了。选择哪一种取决于你是否需要保留 nil。如果参数是「可选的若干配置值」，nil 有意义，就用 select；如果只是数量不定的同类数据，用表更直观。"),
            p("可变参数和固定参数可以混用：function f(a, b, ...) 里前两个按位置绑定，剩下的都进 ...。这在写「必填项 + 可选扩展」的接口时很好用，比如 function query(sql, ...) 让调用方传任意多个绑定值。注意 ... 只能出现在参数列表的最后，函数体里也不能把它赋给变量后当普通值用，它不是一个真正的表，只是一个语法占位。需要保存时，必须显式打包成表。"),
            p("select 的负数下标也很实用：select(-1, ...) 取最后一个参数，select(-2, ...) 取倒数第二个。写「取最后一个元素」的辅助函数时，这样比先算长度再取更直接。select('#', ...) 返回的是参数总个数，包括 nil 占位，这一点和 # 完全不同，# 遇到 nil 会停止计数。理解这两个口径的差异，是写可变参数函数不踩坑的关键，也是很多标准库行为看起来「奇怪」的原因。"),
            p("把可变参数和表结合，可以写出很灵活的接口。比如一个批量插入函数 insert_all(t, ...)，内部用 select 遍历参数逐个插入，调用方就不用自己组装数组；反过来，一个展开函数 spread(t) 用 table.unpack 把数组还原成参数列表。这两个方向合起来，就是 Lua 里「数组」和「参数列表」互相转换的标准手法。需要注意 unpack 一次展开的元素个数受参数上限约束，几十万个元素的大数组不要直接展开，改成传表更安全。"),
            *code(
                r"""local function sum(...)
  local total = 0
  for i = 1, select('#', ...) do
    total = total + select(i, ...)
  end
  return total
end
print(sum(1, 2, 3))
print(sum(10))

local function log(...)
  print('[LOG]', ...)
end
log('start', 1, true)""",
                "6\n10\n[LOG]\tstart\t1\ttrue",
            ),
            table(
                ["写法", "含义", "注意"],
                [
                    ["function f(...)", "声明可变参数", "必须是最后一个形参"],
                    ["select('#', ...)", "参数个数", "包含 nil 占位"],
                    ["select(n, ...)", "从第 n 个开始的参数", "n 可为负数"],
                    ["{...}", "打包成数组", "遇到 nil 会截断"],
                    ["f(...)", "原样透传给另一个函数", "保留全部参数"],
                ],
            ),
            p("一个常见误区是以为 {...} 和参数列表完全等价。实际上 {...} 创建了一张新表，遍历它得到的是拷贝后的值，修改表不会影响原参数；而且当参数里有 nil 时，表构造会在第一个 nil 处留下空洞，# 的结果不可靠。所以库函数在需要「参数个数」时几乎都用 select('#', ...)，而不是 #{...}。这个细节在写通用工具函数时尤其重要，因为调用方可能传 nil 表示「这一项不设置」。"),
            *code(
                r"""local function count(...)
  return select('#', ...)
end
print(count(1, nil, 3))
print(#{1, nil, 3})

local function last(...)
  return select(-1, ...)
end
print(last('a', 'b', 'c'))""",
                "3\n1\nc",
            ),
            warn("不要把 ... 当成表来用：不能写 #...、不能 ... [1]、不能 pairs(...)。需要表就先写 local args = {...}，需要精确个数就用 select('#', ...)。"),
            quiz(
                "函数 f(...) 中，select('#', ...) 与 #{...} 的区别是？",
                ["完全等价", "select 计入 nil，{} 遇到 nil 截断", "select 更慢", "{} 计入 nil，select 截断"],
                1,
                "select('#', ...) 返回真实参数个数，包括 nil；{...} 构造表时遇到 nil 会形成空洞，# 的结果不可靠。",
            ),
        ],
        exercise(
            "可变参数求和",
            "实现 sum_all(...)：返回所有数字参数的和；没有参数时返回 0。必须用 select('#', ...) 遍历，保证 nil 不会被静默跳过。",
            "function sum_all(...)\n  \nend\n\nprint(sum_all(1, 2, 3))",
            "for i = 1, select('#', ...) do local v = select(i, ...) ... end，遇到 nil 时按 0 处理。",
            [
                "assert(sum_all(1, 2, 3) == 6, '1+2+3 应为 6')",
                "assert(sum_all() == 0, '没有参数应返回 0')",
                "assert(sum_all(5) == 5, '单个参数应为 5')",
                "assert(sum_all(1, 2, nil, 3) == 6, 'nil 应被跳过而不是提前截断')",
                "assert(sum_all(-1, 1) == 0, '正负相抵应为 0')",
            ],
            "function sum_all(...)\n  local total = 0\n  for i = 1, select('#', ...) do\n    local v = select(i, ...)\n    if v ~= nil then total = total + v end\n  end\n  return total\nend\n",
            110,
        ),
    ))

    items.append(lesson(
        "lua13", 412, 42, CORE, "string 库", "查找、替换与格式化", 80,
        [
            h("字符串工具全集"),
            p("string 库是 Lua 最常用的标准库，核心函数可以分成四组。长度与截取：len、sub。大小写与重复：upper、lower、rep。查找与替换：find、match、gsub、gmatch。格式化与字节：format、byte、char。日常九成的工作都能用这几组解决。所有函数都可以用冒号语法调用，s:upper() 等价于 string.upper(s)，冒号把 s 作为第一个参数传进去，写起来更紧凑。"),
            p("find 返回匹配的起止下标，找不到返回 nil；第四个参数为 true 时按纯文本查找，不做模式匹配。match 只返回匹配到的内容，如果有捕获组就依次返回各组。gsub 做全局替换，返回替换后的字符串和替换次数，第二个返回值经常被忽略，但它在做统计时很有用。gmatch 返回一个迭代器，配合 for 循环可以逐个取出所有匹配，这是解析文本最顺手的工具。"),
            p("format 的常用占位符：%s 字符串、%d 整数、%f 浮点、%x 十六进制、%c 字符、%% 百分号。宽度可以组合，比如 %03d 补前导零、%5s 右对齐。要注意 LuaJ 对精度修饰的支持不完整：%.2f 不会把 3.14159 截成 3.14，而是原样输出，所以「保留两位小数」必须自己用 math.floor(x * 100 + 0.5) / 100 算好再交给 %s 或 %f。这是一处和标准 Lua 文档不一致的运行时差异，写代码时按实测行为来，不要照抄文档。"),
            p("字符串在 Lua 里不可变，所以 gsub 不会修改原串，而是返回新串。批量拼接时不要写成 s = s .. x 的循环，每次都会创建新串，长度一大就明显变慢；正确做法是用 table 收集片段，最后 table.concat 一次拼完。这个优化在生成报告、拼装 JSON 时很关键。同理，反复用 sub 切字符串也要注意下标计算，负数下标表示从末尾倒数，越界会被裁剪而不是报错，这让代码不容易崩，但也容易掩盖逻辑错误。"),
            *code(
                r"""local s = 'Night City 2077'
print(s:len(), s:sub(1, 5))
print(s:upper())
print(s:find('City'))
print((s:gsub(' ', '-')))
print(string.format('%s|%03d', 'id', 7))""",
                "15\tNight\nNIGHT CITY 2077\n7\t10\nNight-City-2077\nid|007",
            ),
            table(
                ["函数", "作用", "返回值"],
                [
                    ["len(s)", "字节长度", "数字"],
                    ["sub(s, i, j)", "截取，闭区间", "新字符串"],
                    ["find(s, p [, init, plain])", "查找位置", "起止下标或 nil"],
                    ["match(s, p)", "提取匹配内容", "匹配串或捕获组"],
                    ["gsub(s, p, r [, n])", "全局替换", "新串, 替换次数"],
                    ["gmatch(s, p)", "逐个匹配的迭代器", "函数"],
                    ["format(fmt, ...)", "格式化", "新字符串"],
                ],
            ),
            p("这里只做能力概览，模式匹配的语法（%a、%d、%s、捕获组、%b 等）留到进阶篇专门讲。现在你需要建立的是「什么时候用哪个函数」的判断：要位置就用 find，要内容就用 match，要批量改写就用 gsub，要逐个处理就用 gmatch。选错函数不会报错，但会让你多写很多无谓的循环和临时变量。写完之后对照一下标准库文档，通常能删掉三分之一的行数。"),
            p("string.rep 的第三个参数是分隔符，写 string.rep('ab', 3, '-') 会得到 ab-ab-ab。生成分隔线、重复填充、构造测试数据时都很好用。它第二个参数是次数，不是总长度，所以想要得到长度为 20 的横线，要写 string.rep('-', 20)。这两个参数的类型都是数字，传字符串不会自动转换，会直接报错，正好帮你早发现错误。"),
            p("还有一个实用技巧是「先用 find 判断，再用 sub 切」：因为 find 返回的是下标，配合 sub 可以精确取出匹配前后的内容。比如要取出用户名 @ 前面的部分，可以 local i = s:find('@', 1, true)，然后判断 i 是否为 nil，再用 s:sub(1, i - 1)。这种写法比模式匹配更直白，也不受特殊字符影响。简单任务用简单工具，不必一上来就写正则，可读性和调试成本都要考虑。"),
            *code(
                r"""local text = 'lua,js,sql'
for part in text:gmatch('[^,]+') do
  print(part)
end

print(('  trim  '):match('^%s*(.-)%s*$'))
print(string.byte('ABC', 1, 3))
print(string.char(72, 105))""",
                "lua\njs\nsql\ntrim\n65\t66\t67\nHi",
            ),
            tip("gsub 返回两个值。只想要替换结果时用括号包起来：(s:gsub('a', 'b'))，否则它会污染多值上下文，比如直接塞进 print 会多打印一个替换次数。"),
            quiz(
                "表达式 ('a-b-c'):gsub('-', '/') 的返回值是？",
                ["'a/b/c'", "'a/b/c', 2", "2", "nil"],
                1,
                "gsub 返回两个值：替换后的字符串和替换次数。单独打印时会看到 a/b/c 和 2，用括号包住才只取第一个。",
            ),
        ],
        exercise(
            "路径改成点号",
            "实现 to_dotted(name)：把字符串里所有的 - 和 / 都替换成 .，返回替换后的字符串。",
            "function to_dotted(name)\n  \nend\n\nprint(to_dotted('a-b/c'))",
            "连续调用两次 gsub，记得用括号包住第一次的结果，避免多返回值影响第二次调用。",
            [
                "assert(to_dotted('a-b/c') == 'a.b.c', '横线和斜杠都应替换')",
                "assert(to_dotted('abc') == 'abc', '没有分隔符应原样返回')",
                "assert(to_dotted('') == '', '空串应返回空串')",
                "assert(to_dotted('a--b') == 'a..b', '连续分隔符应各自替换')",
            ],
            "function to_dotted(name)\n  local s = name:gsub('-', '.')\n  s = s:gsub('/', '.')\n  return s\nend\n",
            100,
        ),
    ))

    items.append(lesson(
        "lua14", 413, 42, CORE, "table 库", "insert、remove、sort、concat", 80,
        [
            h("数组操作的官方工具箱"),
            p("table 库提供的函数覆盖了数组的增删改查和排序。insert(t, v) 在末尾追加，insert(t, i, v) 在位置 i 插入并把后面整体后移；remove(t) 删除末尾并返回它，remove(t, i) 删除指定位置。这两个函数的返回值经常被忽略，但删除时返回被删元素很有用，比如实现「抽一张牌」时直接拿到抽走的那张。注意插入位置必须在 1 到 #t+1 之间，越界会报错。"),
            p("concat 把数组元素用分隔符连成字符串，可以指定起止下标。它要求元素是字符串或数字，遇到表或 nil 会报错，所以拼接前要先确认数据干净。sort 默认升序，传第二个参数可以自定义比较函数，比较函数返回 true 表示第一个参数应排在前面。排序是原地进行的，会修改原表；不想破坏原始顺序就先复制一份。排序元素类型必须一致，数字和字符串混排会直接抛错。"),
            p("table 库没有提供 map、filter、reduce 这类函数式工具，需要自己写。这不是缺陷，而是 Lua 的取舍：核心库保持最小，扩展交给用户或第三方。写这些工具时注意它们应该返回新表还是原地修改，两种风格各有用途。原地修改省内存但会改变调用方的数据，返回新表更安全但要多分配。团队里最好统一一种约定，否则同一份代码里两种风格混用，读起来会很累。"),
            p("concat 的起止下标参数经常被低估。做分页展示时可以用 table.concat(items, ', ', from, to) 只拼当前页，不需要先切出一个子数组；生成带序号的列表时，可以先拼出主体，再在前后补上标题和尾注。注意 concat 不会自动跳过 nil，遇到空洞会报「invalid value (nil) at index N」，所以拼接前要么确保数据连续，要么先过滤一遍。这个错误信息很明确，看到它就去检查数组里哪一项是 nil。"),
            p("排序的自定义比较函数有一个硬性要求：必须是严格弱序，也就是「a < b」为真时「b < a」必须为假，相等时两者都为假。写成 return a.x <= b.x 就会违反这个条件，某些输入下 table.sort 可能报「invalid order function for sorting」，或者排出难以解释的结果。正确写法是用 <，需要降序就写 a.x > b.x。这个坑在按对象字段排序时非常常见，遇到莫名其妙的排序报错，先检查比较函数里的等号。"),
            *code(
                r"""local t = {3, 1, 2}
table.sort(t)
print(table.concat(t, ','))
table.insert(t, 4)
print(#t, t[4])
print(table.remove(t, 1))
print(table.concat(t, ','))""",
                "1,2,3\n4\t4\n1\n2,3,4",
            ),
            table(
                ["函数", "作用", "是否原地修改"],
                [
                    ["insert(t, v)", "末尾追加", "是"],
                    ["insert(t, i, v)", "指定位置插入", "是"],
                    ["remove(t [, i])", "删除并返回元素", "是"],
                    ["sort(t [, cmp])", "排序", "是"],
                    ["concat(t, sep)", "拼接成字符串", "否"],
                    ["unpack(t, i, j)", "展开成多个值", "否"],
                ],
            ),
            p("实际项目里最常用的是 sort 加 concat 的组合：先把数据整理成数组，排序，再拼接输出。这个流程几乎出现在所有报表、排行榜、日志汇总里。写的时候注意 sort 会改原表，如果原始顺序后面还要用，就先复制。复制也有讲究，浅拷贝只复制第一层，元素还是同一批引用；如果元素是表，要逐个复制才安全。想清楚拷贝的深度，比多写十行代码更重要。"),
            *code(
                r"""local heroes = {
  {name = 'V', level = 66},
  {name = 'Judy', level = 42},
  {name = 'Jackie', level = 30}
}
table.sort(heroes, function(a, b) return a.level > b.level end)
for _, h in ipairs(heroes) do
  print(h.name, h.level)
end""",
                "V\t66\nJudy\t42\nJackie\t30",
            ),
            practice(
                "按分数排序",
                "local rows = {{name='B', score=5}, {name='A', score=9}}\ntable.sort(rows, function(x, y) return x.score > y.score end)\nprint(rows[1].name, rows[2].name)",
                "A\tB",
                "比较函数返回 x.score > y.score 就是降序；不要写 >=，会破坏严格弱序。",
            ),
            tip("table.unpack 把数组展开成多个返回值：print(table.unpack({1,2,3})) 输出 1、2、3。它在需要把数组当参数列表传给函数时非常方便。"),
            quiz(
                "table.sort 的比较函数写成 return a <= b 可能出什么问题？",
                ["没有影响", "违反严格弱序，可能报 invalid order function", "总是降序", "自动去重"],
                1,
                "比较函数必须满足严格弱序：相等时 a<b 与 b<a 都应为假。用 <= 会让相等元素互相「小于」，排序算法可能检测到非法顺序并报错。",
            ),
        ],
        exercise(
            "排行榜前三",
            "实现 top_names(players, n)：players 是 {name=..., score=...} 的数组，按 score 从高到低排序后返回前 n 个名字组成的数组；不足 n 个时返回全部。不要修改传入的数组。",
            "function top_names(players, n)\n  \nend\n\nprint(table.concat(top_names({{name='A',score=3},{name='B',score=9}}, 1), ','))",
            "先复制一份数组，再 table.sort 按 score 降序，最后循环取前 math.min(n, #copy) 个。",
            [
                "local r = top_names({{name='A',score=3},{name='B',score=9},{name='C',score=6}}, 2); assert(table.concat(r, ',') == 'B,C', '应按分数降序取前两名')",
                "local r = top_names({{name='A',score=1}}, 5); assert(#r == 1, '不足 n 个时返回全部')",
                "local p = {{name='A',score=1},{name='B',score=2}}; top_names(p, 1); assert(p[1].name == 'A', '不应修改原数组')",
                "local r = top_names({}, 3); assert(#r == 0, '空数组应返回空数组')",
            ],
            "function top_names(players, n)\n  local copy = {}\n  for i, v in ipairs(players) do copy[i] = v end\n  table.sort(copy, function(a, b) return a.score > b.score end)\n  local out = {}\n  local limit = math.min(n, #copy)\n  for i = 1, limit do out[i] = copy[i].name end\n  return out\nend\n",
            120,
        ),
    ))

    items.append(lesson(
        "lua15", 414, 42, CORE, "math 库", "取整、极值与随机数", 70,
        [
            h("数学函数与数值边界"),
            p("math 库提供常用的数学函数。取整有 floor、ceil 两个方向，floor 向负无穷取整，ceil 向正无穷取整，所以 math.floor(-3.5) 是 -4，math.ceil(-3.5) 是 -3。绝对值 abs、平方根 sqrt、幂运算可以用 ^ 也可以 pow。三角函数 sin、cos、tan 以弧度为单位，deg 和 rad 负责角度与弧度的互转。常数 math.pi 和 math.huge 也在这个库里。"),
            p("max 和 min 可以接收任意多个参数，返回最大或最小值；只传一个参数时返回它自己，传零个参数会报错。需要从数组里取极值时，用 table.unpack 把数组展开：math.max(table.unpack(t))。数组很大时 unpack 可能触及参数个数上限，几万个元素以内通常没问题，再大就应该手写循环，边遍历边比较，既安全又省内存。"),
            p("随机数用 math.random。不传参数返回 [0,1) 的浮点数，传一个整数 n 返回 1 到 n 的整数，传两个整数返回闭区间内的整数。math.randomseed 用来设置种子，让序列可复现。注意本沙箱不保证跨平台的随机序列一致，所以课程练习不会依赖具体随机结果，需要确定性时请用固定数据或自己写一个简单的线性同余生成器。"),
            p("浮点数有一个必须接受的现实：0.1 + 0.2 不一定等于 0.3。判断两个浮点数是否相等，应该看它们的差是否小于一个容差，比如 math.abs(a - b) < 1e-9。做金额计算时更稳妥的做法是全部换成整数分，算完再除以 100 展示，这样能彻底避开二进制小数的误差。这一讲练习里的四舍五入到两位小数，就是这种思路的简化版。"),
            *code(
                r"""print(math.floor(3.7), math.ceil(3.2))
print(math.floor(-3.5), math.ceil(-3.5))
print(math.abs(-9), math.sqrt(16))
print(math.max(3, 9, 2), math.min(3, 9, 2))
print(math.floor(math.pi * 100) / 100)""",
                "3\t4\n-4\t-3\n9\t4\n9\t2\n3.14",
            ),
            table(
                ["函数", "作用", "示例"],
                [
                    ["floor(x)", "向下取整", "3.7 → 3，-3.5 → -4"],
                    ["ceil(x)", "向上取整", "3.2 → 4，-3.5 → -3"],
                    ["abs(x)", "绝对值", "-9 → 9"],
                    ["sqrt(x)", "平方根", "16 → 4"],
                    ["max(...) / min(...)", "极值", "max(3,9,2) → 9"],
                    ["random([m [, n]])", "随机数", "random(1, 6) → 1..6"],
                ],
            ),
            p("整数和浮点在 Lua 5.2 里是同一个类型，所以 4 / 2 得到 2，看起来像整数，实际是浮点值 2.0 的显示形式。做下标、做循环次数时通常没问题，但涉及取模、位运算模拟、哈希计算时就要小心精度。需要明确整数时，用 math.floor 包一层，或者用 math.floor(x + 0.5) 做四舍五入。这些转换看起来琐碎，但它们是数值代码正确性的基础，写财务、统计、游戏数值时绕不开。"),
            p("取整函数的选择会直接影响业务结果。做分页时总页数要用 ceil(total / size)，因为最后一页不满也要算一页；做数组下标时要用 floor，因为下标不能超出实际长度。同样是「除法后取整」，方向选反了就会出现「少一页」或「多出一个越界下标」。拿不准的时候，代入两个极端的例子：总数正好整除，以及总数比除数多一，看哪个方向符合预期。"),
            p("randomseed 的作用是让随机序列可复现：同一个种子跑两次，得到同样的序列。测试随机相关逻辑时，先设种子再断言，就能写出稳定的用例；上线时用默认种子或时间种子，避免每次都一样。本沙箱不保证不同平台上的序列一致，所以课程示例只验证范围，不验证具体值。真实项目里如果需要跨平台一致，应该自己实现一个确定的伪随机算法。"),
            p("math.huge 代表正无穷，-math.huge 代表负无穷，0/0 会得到 nan。判断 nan 不能用 ==，因为 nan 与自己都不相等，标准做法是检查 x ~= x 是否为真。这些边界值在正常业务里很少遇到，但一旦出现往往意味着上游数据有问题，比如除零、溢出、解析失败。与其让 nan 一路传播到界面显示「nan」，不如在计算入口就检查除数、检查输入范围，把问题挡在源头。"),
            *code(
                r"""local function round2(x)
  return math.floor(x * 100 + 0.5) / 100
end
print(round2(3.14159), round2(2.005), round2(-1.234))
print(7 % 3, math.fmod(7, 3), math.fmod(-7, 3))""",
                "3.14\t2.01\t-1.23\n1\t1\t-1",
            ),
            tip("math.fmod 和 % 在负数上结果不同：% 的结果与除数同号，fmod 的结果与被除数同号。做周期性索引时通常用 %，做 C 风格取余时用 fmod。"),
            quiz(
                "math.floor(-3.5) 的值是？",
                ["-3", "-4", "3", "4"],
                1,
                "floor 是向负无穷方向取整，-3.5 更小的整数是 -4。要朝零取整用其他方式，ceil(-3.5) 才是 -3。",
            ),
        ],
        exercise(
            "距离与取整",
            "实现 distance(x1, y1, x2, y2)：返回两点欧氏距离，保留两位小数（用 math.floor(d * 100 + 0.5) / 100）。",
            "function distance(x1, y1, x2, y2)\n  \nend\n\nprint(distance(0, 0, 3, 4))",
            "先算 dx 和 dy，再用 math.sqrt(dx * dx + dy * dy)，最后四舍五入到两位。",
            [
                "assert(distance(0, 0, 3, 4) == 5, '3-4-5 直角三角形距离应为 5')",
                "assert(distance(0, 0, 0, 0) == 0, '同一点距离应为 0')",
                "assert(distance(0, 0, 1, 1) == 1.41, '对角线应四舍五入到 1.41')",
                "assert(distance(1, 1, 1, 4) == 3, '竖直距离应为 3')",
            ],
            "function distance(x1, y1, x2, y2)\n  local dx = x2 - x1\n  local dy = y2 - y1\n  local d = math.sqrt(dx * dx + dy * dy)\n  return math.floor(d * 100 + 0.5) / 100\nend\n",
            100,
        ),
    ))

    return items


def _core_16_20():
    items = []

    items.append(lesson(
        "lua16", 415, 42, CORE, "迭代器 pairs/ipairs", "泛型 for 的两种遍历", 80,
        [
            h("两种遍历，两种语义"),
            p("泛型 for 写作 for k, v in 迭代器 do ... end，每次循环从迭代器取一组值。最常用的是 ipairs 和 pairs。ipairs 从下标 1 开始，按顺序返回下标和值，遇到第一个 nil 就停止；pairs 遍历所有键值对，包括字符串键和数字键，顺序由哈希实现决定。选哪一个取决于你的数据结构是数组还是字典，而不是个人喜好。"),
            p("ipairs 的「遇到 nil 就停」是它的定义，不是 bug。如果数组中间有空洞，后面的元素不会被遍历到，所以删除元素后不要指望 ipairs 还能走完全部。pairs 则会跳过空洞继续遍历其他键，但顺序不确定。需要稳定顺序时先收集键再排序，这个套路在基础篇已经用过。判断一个表是数组还是字典，看它的键是不是从 1 开始的连续整数，而不是看它「看起来像」。"),
            p("迭代器的本质是一个函数，每次调用返回下一个值，返回 nil 表示结束。pairs 返回的是 next 函数、表本身和 nil 三个值，所以 for k, v in pairs(t) 等价于 for k, v in next, t, nil。理解这一点，你就能自己写迭代器：只要返回一个符合「调用一次给一组值、结束时给 nil」约定的函数即可。写自定义迭代器时，把状态存在闭包里，比用全局变量安全得多。"),
            p("遍历过程中修改表是危险操作。新增键可能导致遍历不到、也可能报错；删除当前键在某些实现下可行，但依赖具体版本。稳妥的做法是先收集要删除的键，遍历结束后统一处理，或者用 while 加 next 手动控制。这个建议看起来保守，但能避免那种「本地跑得好、线上偶发错误」的问题，而后者往往要花几倍时间定位。"),
            *code(
                r"""local arr = {'a', 'b', 'c'}
for i, v in ipairs(arr) do
  print(i, v)
end

local map = {name = 'V', level = 66}
for k, v in pairs(map) do
  print(k, v)
end""",
                "1\ta\n2\tb\n3\tc\nname\tV\nlevel\t66",
            ),
            table(
                ["迭代器", "遍历范围", "顺序", "遇到 nil"],
                [
                    ["ipairs(t)", "下标 1 开始的连续整数键", "固定升序", "停止"],
                    ["pairs(t)", "所有键值对", "不保证", "跳过并继续"],
                    ["next(t, k)", "底层单步遍历", "不保证", "跳过"],
                    ["自定义迭代器", "由函数决定", "由函数决定", "由函数决定"],
                ],
            ),
            p("for 循环还能直接接多个返回值：for k, v in pairs(t) 就是每次拿两个。如果迭代器只返回一个值，写 for v in it do 即可，多的变量自然是 nil。自定义迭代器时，返回 nil 就表示结束，所以迭代器不能把 nil 当作有效值返回，否则循环会提前停止。需要表达「有效值是 nil」时，通常要多返回一个状态位，或者在协议层约定用别的哨兵值，这是设计迭代器时要提前想清楚的边界。"),
            p("遍历的顺序在测试里经常成为隐患。同一份字典，pairs 这次输出 A、B、C，下次可能是 C、A、B，所以断言不能写成比较整段输出，而应该把结果排序后再比较，或者逐项检查而不依赖次序。写课程示例时也要注意这一点：凡是涉及字典遍历的输出，示例里都先排序，保证每次运行结果一致。这个习惯能省掉很多「本地过、CI 挂」的排查时间。"),
            p("除了 ipairs 和 pairs，标准库还能直接产出迭代器：string.gmatch 返回按模式逐个匹配的迭代器，io.lines 返回逐行读取的迭代器（本沙箱没有 io）。它们都是同一种协议的不同实现，学会看「这个函数返回的是值还是迭代器」，比记住函数名更有用。判断方法很简单：如果它出现在 for ... in 的 in 后面，或者需要先赋给变量再循环，那就是迭代器；如果直接给出结果，那就是普通函数。"),
            *code(
                r"""local function range(n)
  local i = 0
  return function()
    i = i + 1
    if i <= n then return i end
  end
end

for v in range(4) do
  print(v)
end""",
                "1\n2\n3\n4",
            ),
            visualize(
                "ipairs 的三次迭代",
                "t = {'a', 'b', 'c'}，i 从 1 递增到 4 时循环结束",
                [
                    frame("i=1，取到 t[1]", [("i", "1"), ("v", "a")], ["i", "v"]),
                    frame("i=2，取到 t[2]", [("i", "2"), ("v", "b")], ["i", "v"]),
                    frame("i=3，取到 t[3]", [("i", "3"), ("v", "c")], ["i", "v"]),
                    frame("i=4，t[4] 为 nil，循环结束", [("i", "4"), ("v", "nil")], ["i"]),
                ],
            ),
            warn("不要在 ipairs 循环里删除元素，后面的元素会前移导致漏遍历。需要过滤时从后往前遍历，或者先把要保留的元素收集到新表。"),
            quiz(
                "local t = {1, nil, 3}，ipairs(t) 会遍历到几个元素？",
                ["3 个", "2 个", "1 个", "不确定"],
                2,
                "ipairs 从 1 开始，遇到第一个 nil（下标 2）就停止，所以只会遍历到下标 1 的元素。",
            ),
        ],
        exercise(
            "统计非空键",
            "实现 count_entries(t)：返回表 t 中所有值不为 nil 的键的数量。用 pairs 遍历，这样字符串键和数字键都能统计到。",
            "function count_entries(t)\n  \nend\n\nprint(count_entries({a = 1, b = 2}))",
            "local n = 0，for k, v in pairs(t) do n = n + 1 end；pairs 本身不会返回 nil 值，所以直接计数即可。",
            [
                "assert(count_entries({a = 1, b = 2}) == 2, '两个字符串键应计为 2')",
                "assert(count_entries({}) == 0, '空表应为 0')",
                "assert(count_entries({1, 2, 3}) == 3, '三个数组元素应计为 3')",
                "assert(count_entries({x = 1, 2, 3}) == 3, '混合键应全部计入')",
            ],
            "function count_entries(t)\n  local n = 0\n  for _ in pairs(t) do n = n + 1 end\n  return n\nend\n",
            100,
        ),
    ))

    items.append(lesson(
        "lua17", 416, 42, CORE, "闭包", "upvalue 与状态封装", 90,
        [
            h("函数记住了它的出生地"),
            p("闭包是「函数 + 它引用的外部局部变量」的组合。当一个内部函数引用了外层的 local 变量，并且这个内部函数被返回或传出外层作用域，那个变量就不会被释放，而是跟着函数一起活下去。这个被捕获的变量叫 upvalue。闭包让函数有了记忆，也让「私有状态」成为可能，是 Lua 里实现对象、模块、计数器的核心机制。"),
            p("闭包捕获的是变量本身，不是创建时的值。所以两个函数如果引用同一个 upvalue，它们看到的是同一份数据，一个改另一个立刻能看到；反之，每次调用外层函数都会创建一组全新的 upvalue，彼此互不影响。这个区别是理解闭包的关键：make_counter() 每次调用都返回一个独立的计数器，而同一个工厂里返回的两个函数共享同一个计数。写之前先想清楚你要的是「共享」还是「独立」。"),
            p("用闭包封装状态比用全局变量安全得多。外部拿不到那个 local 变量，只能通过你暴露的函数去读写，相当于天然的私有字段。很多 Lua 模块就是这么写的：文件顶部 local state = {}，下面定义若干操作 state 的函数，最后 return 一个表把这些函数暴露出去。调用方看不到 state，也无法绕过你的校验逻辑，这与面向对象的封装效果一致，但不需要 class 语法。"),
            p("闭包还有一个常见用途是延迟执行和回调。比如把「要做什么」和「做的时候用的参数」一起打包成函数，稍后再调用。这种写法在事件处理、任务队列里非常普遍。要注意的是，如果在循环里创建闭包并捕获循环变量，Lua 的数值 for 每轮都会创建新的变量，所以每个闭包拿到的是当轮的值，这通常正是你想要的；如果捕获的是循环外声明的变量，那所有闭包看到的都是同一个值。"),
            *code(
                r"""local function make_counter()
  local n = 0
  return function()
    n = n + 1
    return n
  end
end

local a = make_counter()
local b = make_counter()
print(a(), a(), b(), a())""",
                "1\t2\t1\t3",
            ),
            table(
                ["概念", "含义", "影响"],
                [
                    ["upvalue", "被闭包捕获的外层局部变量", "函数返回后仍然存活"],
                    ["共享", "多个闭包引用同一个变量", "一处修改处处可见"],
                    ["独立", "每次调用外层函数新建变量", "互不干扰"],
                    ["私有状态", "外部无法直接访问的 local", "只能通过暴露的函数操作"],
                ],
            ),
            p("把闭包和表结合，就能写出「带状态的对象」：每个对象是一张表，方法定义在表外并通过闭包访问私有字段，或者用元表把方法共享给所有实例。前者每次创建对象都会新建一批函数，内存开销大但隔离彻底；后者只创建一份函数，实例只存数据，更省内存。进阶篇讲元表时会给出后者的完整写法，现在先理解两种方案的取舍，遇到具体问题时就知道该选哪一种。"),
            *code(
                r"""local function make_adder(base)
  return function(x)
    return base + x
  end
end
local add10 = make_adder(10)
print(add10(5), add10(-3))

local fns = {}
for i = 1, 3 do
  fns[i] = function() return i * i end
end
print(fns[1](), fns[2](), fns[3]())""",
                "15\t7\n1\t4\t9",
            ),
            warn("闭包会延长 upvalue 的生命周期。如果捕获了一个很大的表却只用其中一项，整张表都无法被回收——这是 Lua 里常见的内存泄漏原因之一。"),
            quiz(
                "两次调用 make_counter() 得到的计数器为什么互不影响？",
                ["因为函数是值", "因为每次调用都创建了新的 local n", "因为 n 是全局变量", "因为闭包不能共享"],
                1,
                "local n = 0 在每次调用 make_counter 时都会重新创建，返回的闭包各自捕获自己的那一份，所以互不干扰。",
            ),
        ],
        exercise(
            "累加器工厂",
            "实现 make_accumulator(start)：返回一个函数，每次调用传入一个数字并返回累加后的总和，初始值为 start。",
            "function make_accumulator(start)\n  \nend\n\nlocal acc = make_accumulator(10)\nprint(acc(5))",
            "在 make_accumulator 里声明 local total = start，返回的函数接收 x 并执行 total = total + x。",
            [
                "local a = make_accumulator(10); assert(a(5) == 15, '10 + 5 应为 15')",
                "local a = make_accumulator(0); a(3); assert(a(4) == 7, '连续累加应为 7')",
                "local a, b = make_accumulator(1), make_accumulator(100); a(1); assert(b(1) == 101, '两个累加器应互相独立')",
                "local a = make_accumulator(5); assert(a(-5) == 0, '负数应能抵消')",
            ],
            "function make_accumulator(start)\n  local total = start\n  return function(x)\n    total = total + x\n    return total\n  end\nend\n",
            120,
        ),
    ))

    items.append(lesson(
        "lua18", 417, 42, CORE, "递归", "自我调用与记忆化", 90,
        [
            h("把问题缩小一号"),
            p("递归是函数调用自己来解决问题。写递归只需要想清楚两件事：什么时候停（基准情形），以及如何把问题缩小成同类的小问题（递归情形）。阶乘的基准是 n <= 1 时返回 1，递归是 n * fact(n - 1)；斐波那契的基准是 n < 2 时返回 n，递归是 fib(n-1) + fib(n-2)。把这两件事写对，剩下的交给调用栈。"),
            p("递归函数必须保证每次调用都向基准靠近，否则会无限递归直到栈溢出。LuaJ 的调用栈深度有限，几千层就可能报错，所以处理大规模数据时要评估深度。另外，朴素递归会重复计算大量子问题，斐波那契的朴素版本时间复杂度是指数级的，n 到 35 就明显卡顿。解决办法是记忆化：用一个表缓存已经算过的结果，进入函数先查缓存。"),
            p("尾递归是一种特殊的递归形式：递归调用是函数返回前的最后一个动作，没有后续计算。某些语言会把它优化成循环，避免栈增长；Lua 5.2 的标准实现确实支持尾调用优化，但不要依赖它来写无限递归。更稳妥的做法是能改成迭代就改成迭代，尤其是深度可能上千的场景。递归适合表达「树形结构」和「分治」，不适合单纯计数。"),
            p("记忆化的写法是在外层创建一个缓存表，函数内部先查 cache[n]，有就直接返回，没有就计算并写回。缓存表应该放在闭包里，而不是全局，否则不同调用之间会互相污染，也无法针对不同参数集重置。斐波那契加上记忆化之后，复杂度从指数级降到线性，n 到几百都能瞬间算完。这个优化思路可以套用到任何「同样的输入会被重复计算」的递归上。"),
            *code(
                r"""local function fact(n)
  if n <= 1 then return 1 end
  return n * fact(n - 1)
end
print(fact(5), fact(10))

local function fib(n)
  if n < 2 then return n end
  return fib(n - 1) + fib(n - 2)
end
print(fib(10))""",
                "120\t3628800\n55",
            ),
            table(
                ["问题", "基准情形", "递归情形"],
                [
                    ["阶乘", "n <= 1 返回 1", "n * fact(n - 1)"],
                    ["斐波那契", "n < 2 返回 n", "fib(n-1) + fib(n-2)"],
                    ["求和", "n == 1 返回 1", "n + sum(n - 1)"],
                    ["目录遍历", "没有子项就返回", "对每个子项递归"],
                ],
            ),
            p("写递归时还要注意参数的设计。把「累计结果」作为参数往下传，可以让递归函数变成尾调用形式，也避免了在返回时再做合并；把「缓存」作为参数传，可以控制作用域，不必依赖全局表。参数多的递归函数读起来累，可以包一层对外接口，把内部递归函数藏在里面，对外只暴露最简签名。这种「外壳 + 内部实现」的结构，在树遍历、解析器里非常常见。"),
            p("递归和迭代不是对立的，很多问题两种写法都行。经验法则是：数据结构本身是递归的（树、链表、嵌套表）就用递归，因为代码结构和数据形状一致，最不容易写错；如果只是计数、累加、遍历数组，用迭代更直接，也没有栈深度的顾虑。真要用递归处理大数据，先把深度算清楚，必要时加一个深度参数做保护，超过阈值就报错，而不是让程序崩在栈溢出上。"),
            *code(
                r"""local function fib_memo(n)
  local cache = {}
  local function go(k)
    if k < 2 then return k end
    if cache[k] then return cache[k] end
    local v = go(k - 1) + go(k - 2)
    cache[k] = v
    return v
  end
  return go(n)
end
print(fib_memo(10), fib_memo(30))""",
                "55\t832040",
            ),
            warn("递归深度受调用栈限制。处理上万个节点时优先用显式栈（一个表当栈）改写，别指望尾调用优化在所有环境都生效。"),
            quiz(
                "朴素递归求斐波那契为什么慢？",
                ["函数调用开销大", "大量子问题被重复计算", "数字太大", "没有返回值"],
                1,
                "fib(n-1) 和 fib(n-2) 会展开出大量重叠的子问题，复杂度接近指数级。用缓存记住算过的值可以降到线性。",
            ),
        ],
        exercise(
            "递归求和",
            "实现 sum_to(n)：用递归返回 1 到 n 的和，n < 1 时返回 0。",
            "function sum_to(n)\n  \nend\n\nprint(sum_to(5))",
            "基准情形是 n < 1 返回 0，递归情形是 n + sum_to(n - 1)。",
            [
                "assert(sum_to(5) == 15, '1 到 5 的和应为 15')",
                "assert(sum_to(1) == 1, 'n 为 1 应返回 1')",
                "assert(sum_to(0) == 0, 'n 为 0 应返回 0')",
                "assert(sum_to(-3) == 0, '负数应返回 0')",
                "assert(sum_to(100) == 5050, '1 到 100 应为 5050')",
            ],
            "function sum_to(n)\n  if n < 1 then return 0 end\n  return n + sum_to(n - 1)\nend\n",
            110,
        ),
    ))

    items.append(lesson(
        "lua19", 418, 42, CORE, "错误处理", "pcall / error / xpcall", 90,
        [
            h("让错误可控"),
            p("Lua 没有 try/catch 语法，错误处理靠函数。error(msg) 主动抛出错误，pcall(f, ...) 以保护模式调用 f：成功时返回 true 加上 f 的所有返回值，失败时返回 false 加错误信息。错误信息可以是字符串，也可以是任意值，比如一张带 code 和 message 的表。用表作为错误对象，能携带结构化信息，比纯字符串更适合分层处理。"),
            p("pcall 只捕获运行时错误，语法错误在加载阶段就会被发现，轮不到 pcall。它也不区分错误类型，所有失败都返回 false，所以要靠错误信息或错误对象的字段来判断是哪一类问题。xpcall 比 pcall 多一个消息处理器，可以在错误传播出去之前做转换，比如统一加上时间戳或调用链。第三个参数必须是一个函数，不能直接传字符串。"),
            p("错误处理的原则是：能恢复的就恢复，不能恢复的就让它尽快失败。给用户看的错误信息要具体，比如「第 3 行：字段 name 不能为空」，而不是「出错了」；给日志看的错误要带上下文，比如输入值、函数名、阶段。不要用 pcall 把所有代码包起来然后什么都不做，那等于把 bug 藏起来，等到数据错乱时更难查。"),
            p("assert 是最常用的轻量校验：assert(cond, 'msg') 在条件为假时抛出 msg，为真时返回所有参数。它适合放在函数入口检查前置条件，比如 assert(type(n) == 'number', 'n must be a number')。注意 assert 只在条件为 nil 或 false 时触发，0 和空串都算通过，所以别用 assert(n) 来检查数字是否为 0 以外的值，要写明确的比较。"),
            *code(
                r"""local ok, err = pcall(function()
  error('something went wrong')
end)
print(ok, type(err))

local ok2, value = pcall(function()
  return 1 + 1
end)
print(ok2, value)""",
                "false\tstring\ntrue\t2",
            ),
            table(
                ["函数", "用法", "返回"],
                [
                    ["error(msg)", "抛出错误", "不返回，向上传播"],
                    ["pcall(f, ...)", "保护模式调用", "true + 返回值 / false + 错误"],
                    ["xpcall(f, handler)", "带处理器的保护调用", "同上，错误先经 handler"],
                    ["assert(cond, msg)", "条件为假时抛错", "条件为真时原样返回参数"],
                ],
            ),
            p("调试错误时，先看错误信息的第一个冒号前面是什么。如果有文件名和行号，说明是源码里的错误；如果只有一段字符串，说明是 error 里手写的消息，可能已经被中间层包装过。再往下看调用栈（LuaJ 的报错一般会附带层级），找到第一处属于你自己代码的位置，那里往往才是真正的问题所在，而不是最深的那一层。这个定位习惯能让你少走很多弯路。"),
            p("pcall 也可以用来保护「可能不存在」的库函数。比如某些环境没有某个函数，直接调用会报错，可以先判断 type(f) == 'function'，再用 pcall 包一层兜底。这种防御式写法在跨平台脚本里很常见，但不要滥用：如果错误是程序 bug，让它崩掉反而更容易定位；只有外部输入、可选依赖这类「预期内可能失败」的场景，才值得用 pcall 包住。"),
            p("错误处理还分层次：底层函数负责检测和抛出，中层负责转换和补充上下文，最外层负责展示或记录。如果一个函数既做业务又打印错误，它就没法被复用，因为你无法在测试里静默调用它。更好的做法是函数只返回错误对象，由调用方决定是打印、重试还是向上抛。这种「谁决策谁处理」的原则，能让错误路径和正常路径一样可测试。"),
            *code(
                r"""local function divide(a, b)
  if b == 0 then
    error({code = 'DIV_ZERO', message = '除数不能为 0'})
  end
  return a / b
end

local ok, err = pcall(divide, 6, 0)
print(ok, type(err), err.code, err.message)
print(pcall(divide, 6, 3))""",
                "false\ttable\tDIV_ZERO\t除数不能为 0\ntrue\t2",
            ),
            tip("错误对象用表时可以带 code 字段，调用方按 code 分支处理，比字符串匹配稳定得多。字符串里的行号会随代码改动变化，code 不会。"),
            quiz(
                "pcall(f) 在 f 成功执行时返回什么？",
                ["只有 true", "true 加上 f 的返回值", "f 的返回值", "nil"],
                1,
                "pcall 成功时返回 true，后面依次是 f 的所有返回值；失败时返回 false 加错误信息。",
            ),
        ],
        exercise(
            "安全除法",
            "实现 safe_div(a, b)：b 为 0 时返回 nil 和错误信息 'division by zero'（不要用 error 抛出，直接用多返回值），否则返回 a / b 和 nil。",
            "function safe_div(a, b)\n  \nend\n\nprint(safe_div(6, 3))",
            "if b == 0 then return nil, 'division by zero' end，否则 return a / b, nil。",
            [
                "local v, e = safe_div(6, 3); assert(v == 2 and e == nil, '6/3 应为 2')",
                "local v, e = safe_div(1, 0); assert(v == nil, '除零应返回 nil')",
                "local v, e = safe_div(1, 0); assert(e == 'division by zero', '应带错误信息')",
                "local v, e = safe_div(0, 5); assert(v == 0, '0 除以非零应为 0')",
            ],
            "function safe_div(a, b)\n  if b == 0 then return nil, 'division by zero' end\n  return a / b, nil\nend\n",
            110,
        ),
    ))

    items.append(lesson(
        "lua20", 419, 42, CORE, "模块与 require 概念", "用表组织代码", 90,
        [
            h("模块就是一个表"),
            p("Lua 没有内置的 class 和 namespace，模块的概念非常简单：一个文件返回一张表，表里放你希望暴露的函数和常量，其他人拿到这张表就能用。这种「返回表」的约定被社区广泛接受，几乎所有第三方库都这么写。文件顶层的辅助函数和状态都用 local 声明，外部完全看不到，天然实现了私有性。"),
            p("require 是加载模块的标准函数，它按 package.path 里的模式去文件系统找对应的 .lua 文件，加载后缓存结果，重复 require 返回同一张表。本课程的沙箱刻意关闭了文件查找器，所以 require 找不到任何外部文件，调用会失败。这不是让你绕过，而是让你理解：require 的价值在于「定位文件 + 执行一次 + 缓存结果」，语言层面并没有魔法。"),
            p("没有 require 时，模块模式依然可以手写：定义一个 local M = {}，把函数挂到 M 上，最后 return M。需要多个模块协作时，可以在主文件里按顺序定义，把前一个的返回值赋给一个 local 变量，再传给后一个。这模拟了 require 的核心语义，也让你看清模块之间真正的依赖关系。理解这一点，换到任何支持 require 的环境都能无缝迁移。"),
            p("模块设计有几条经验：只暴露必要的接口，内部实现细节一律 local；不要在模块加载时做重活，加载应该快速且无副作用；模块之间的依赖尽量单向，避免 A 依赖 B、B 又依赖 A 的循环引用，那种情况在 Lua 里会拿到半初始化的表。需要共享状态时，用一个显式的 init 函数，而不是靠加载顺序碰运气。"),
            *code(
                r"""local Counter = {}
Counter.__index = Counter

function Counter.new(start)
  return setmetatable({value = start or 0}, Counter)
end

function Counter:inc(step)
  self.value = self.value + (step or 1)
  return self.value
end

local c = Counter.new(10)
print(c:inc(), c:inc(5))
print(Counter.new().value)""",
                "11\t16\n0",
            ),
            table(
                ["要素", "作用", "本课做法"],
                [
                    ["local M = {}", "模块命名空间", "所有导出项挂在 M 上"],
                    ["local 辅助函数", "私有实现", "外部无法访问"],
                    ["return M", "导出模块", "调用方拿到同一张表"],
                    ["require('name')", "加载并缓存", "本沙箱不可用，用变量传递替代"],
                ],
            ),
            p("组织多文件项目时，可以把「数据」和「逻辑」分开：数据模块只返回配置表，逻辑模块接收配置表作为参数。这样测试逻辑时可以直接构造一份假配置，不需要真的加载文件；改配置也不会碰到代码，降低了误改的风险。Lua 没有编译期的模块检查，这种「显式传入依赖」的风格能让错误更早暴露，在启动阶段就发现缺字段，而不是运行到某个分支才崩。"),
            p("模块的返回值不一定是表。有些库只导出一个函数，那就直接 return 那个函数；有些库导出的是「可调用对象」，一张表加 __call 元方法。选择哪种取决于使用方式：如果调用方主要写 M.func()，用表；如果主要写 M(...)，用可调用对象。不要为了形式统一而强行包一层表，多余的间接层只会让调用代码变长，也让阅读者多跳一次。"),
            p("模块之间传递依赖有两种常见方式：一种是在文件顶部用 local 变量接收另一个模块，另一种是通过参数注入。前者写起来短，但会形成硬编码依赖，测试时不好替换；后者多写几个参数，却能在测试里传入假对象，也更容易看清调用关系。小项目用前者足够，代码量上来之后建议逐步转向后者。选择标准是：这个依赖会不会在测试或不同环境里需要替换，会就用注入。"),
            *code(
                r"""local MathUtil = {}

local function square(x)
  return x * x
end

function MathUtil.sum_squares(t)
  local s = 0
  for _, v in ipairs(t) do s = s + square(v) end
  return s
end

print(MathUtil.sum_squares({1, 2, 3}))
print(type(MathUtil.square))""",
                "14\nnil",
            ),
            tip("模块文件不要写全局变量。用 local 把所有东西收起来，只 return 一张表，这样加载十次也不会污染全局命名空间。"),
            quiz(
                "Lua 里模块的标准形态是？",
                ["一个 class 声明", "一个返回表的文件", "一个全局函数", "一个特殊的关键字"],
                1,
                "Lua 没有专门的模块语法，社区约定是文件最后 return 一张表，表里放导出的函数和数据，其余用 local 隐藏。",
            ),
        ],
        exercise(
            "计数器模块",
            "实现 new_counter(start)：返回一个表，表里有 inc(step) 和 get() 两个方法，内部值从 start 开始（默认 0）。inc 返回新值，get 返回当前值。",
            "function new_counter(start)\n  \nend\n\nlocal c = new_counter(10)\nprint(c.inc(5), c.get())",
            "在函数里 local value = start or 0，返回一张表，两个函数都捕获这个 value。",
            [
                "local c = new_counter(10); assert(c.inc(5) == 15, '10 加 5 应为 15')",
                "local c = new_counter(0); c.inc(); assert(c.get() == 1, '默认步长应为 1')",
                "local a, b = new_counter(1), new_counter(100); a.inc(); assert(b.get() == 100, '两个计数器应互相独立')",
                "local c = new_counter(); assert(c.get() == 0, '不传参数应从 0 开始')",
            ],
            "function new_counter(start)\n  local value = start or 0\n  return {\n    inc = function(step)\n      value = value + (step or 1)\n      return value\n    end,\n    get = function()\n      return value\n    end\n  }\nend\n",
            120,
        ),
    ))

    return items


def _adv_21_25():
    items = []

    items.append(lesson(
        "lua21", 420, 43, ADV, "元表入门", "setmetatable 与 getmetatable", 90,
        [
            h("给表挂上一层行为"),
            p("元表是 Lua 里最独特也最强大的机制。每张表都可以关联另一张表，称为元表，元表里的特定字段（以双下划线开头，比如 __index、__add）会在特定操作发生时被查找。setmetatable(t, mt) 给 t 挂上元表，getmetatable(t) 取回来。没有挂元表的表，所有元操作都走默认行为，一旦挂上，就等于给这张表定制了「遇到加法怎么办」「读不存在的键怎么办」。"),
            p("元表本身只是一张普通的表，没有任何特殊语法。真正起作用的是一组约定的字段名，Lua 虚拟机会在这些时刻去查：索引不存在的键查 __index，给不存在的键赋值查 __newindex，算术运算查 __add、__sub、__mul、__div、__mod、__pow、__unm，比较查 __eq、__lt、__le，拼接查 __concat，取长度查 __len，调用查 __call，转字符串查 __tostring。记住这张清单，就掌握了元表的全部入口。"),
            p("setmetatable 会直接修改传入的表并返回它，所以可以写成链式调用。getmetatable 返回元表，但如果你在元表里设置了 __metatable 字段，getmetatable 会返回那个字段的值而不是元表本身，setmetatable 也会被拒绝，这是一种保护机制，防止别人改你的元表。调试时如果发现 getmetatable 返回一个字符串，不要惊讶，那是作者故意锁上的。"),
            p("元表最适合用在「需要统一行为的同类对象」上。比如所有向量都用同一张元表定义加法，所有配置对象都用同一张元表定义默认值。不要给每张表都挂一个新的元表，那样既浪费内存，也让行为难以追踪。常见做法是把元表定义成模块级别的 local，所有实例共享，实例只存数据，行为全在元表里。这正是面向对象风格在 Lua 里的实现基础。"),
            *code(
                r"""local mt = {
  __index = function(t, k)
    return 'missing:' .. k
  end
}
local t = setmetatable({name = 'V'}, mt)
print(t.name)
print(t.level)
print(getmetatable(t) == mt)

local plain = {}
print(getmetatable(plain))""",
                "V\nmissing:level\ntrue\nnil",
            ),
            table(
                ["字段", "触发时机", "参数"],
                [
                    ["__index", "读取不存在的键", "表, 键"],
                    ["__newindex", "给不存在的键赋值", "表, 键, 值"],
                    ["__add / __sub", "加减运算", "两个操作数"],
                    ["__eq / __lt / __le", "比较运算", "两个操作数"],
                    ["__concat", ".. 拼接", "两个操作数"],
                    ["__len", "# 取长度", "表"],
                    ["__call", "把表当函数调用", "表, 其余参数"],
                    ["__tostring", "tostring 转换", "表"],
                ],
            ),
            p("元表还可以和继承一起用，形成方法查找链。把类的 __index 指向自己，实例的元表设为这个类，实例读方法时就会走「实例 → 类」这一跳；如果类本身还有元表且 __index 指向父类，就再多一跳。这条链是 Lua 面向对象的基础，但它的代价是每次读不存在的键都要多一次表查找。对性能敏感的内层循环，可以把常用的方法先取到局部变量，避免重复走链。"),
            p("一个常见误解是以为元表能拦截所有读写。实际上 __index 只在键不存在时触发，键存在就直接返回原值；__newindex 也只在键不存在时触发，键已存在就直接覆盖。要拦截「已存在键的赋值」，得把原表藏起来，用代理表配合 __newindex 转发，这是进阶技巧。理解「只在缺失时触发」这条规则，能避免很多「为什么我的钩子没执行」的困惑。"),
            *code(
                r"""local log = {}
local proxy = setmetatable({}, {
  __newindex = function(t, k, v)
    log[#log + 1] = k
    rawset(t, k, v)
  end,
  __index = function(t, k)
    return rawget(t, k)
  end
})
proxy.a = 1
proxy.b = 2
print(proxy.a, #log, log[1], log[2])""",
                "1\t2\ta\tb",
            ),
            tip("rawset 和 rawget 可以绕过元表直接读写原表，写元方法时几乎一定会用到，否则会在 __index 里再次触发 __index，造成无限递归。"),
            quiz(
                "给表设置元表后，访问一个已存在的键会触发 __index 吗？",
                ["会", "不会，只有键不存在时才触发", "取决于键的类型", "会触发两次"],
                1,
                "__index 只在键不存在时作为兜底被调用。键存在时直接返回原值，元表完全不参与。",
            ),
        ],
        exercise(
            "默认值表",
            "实现 with_default(t, default)：返回一张新表，读取不存在的键时返回 default。已有的键必须保持原值。",
            "function with_default(t, default)\n  \nend\n\nlocal d = with_default({a = 1}, 0)\nprint(d.a, d.b)",
            "创建一张空表，用 setmetatable 挂上 __index 函数，函数返回 default。注意不要把 t 直接当结果返回，否则会改到原表。",
            [
                "local d = with_default({a = 1}, 0); assert(d.a == 1, '已有的键应保持原值')",
                "local d = with_default({a = 1}, 0); assert(d.b == 0, '缺失的键应返回默认值')",
                "local src = {x = 5}; with_default(src, 9); assert(src.y == nil, '不应修改原表')",
                "local d = with_default({}, 'none'); assert(d.anything == 'none', '默认值可以是字符串')",
            ],
            "function with_default(t, default)\n  local copy = {}\n  for k, v in pairs(t) do copy[k] = v end\n  return setmetatable(copy, {__index = function() return default end})\nend\n",
            120,
        ),
    ))

    items.append(lesson(
        "lua22", 421, 43, ADV, "__index 与继承", "元表链与原型模式", 100,
        [
            h("沿元表链向上查找"),
            p("__index 除了可以是函数，还可以是另一张表。当它是表时，读取不存在的键会去那张表里继续查；如果那张表也有元表，就继续往上，形成一条查找链。这条链就是 Lua 的继承机制。最经典的写法是：模块表 M 里写 M.__index = M，然后让所有实例的元表都是 M，实例读不到的方法就会自动去 M 里找。"),
            p("实现继承时，子类的元表用 __index 指向父类：setmetatable(Child, {__index = Parent})。这样 Child 找不到的字段会去 Parent 找，包括方法。实例的元表指向 Child，实例找不到就去 Child，Child 找不到再去 Parent，三层就串起来了。注意两件事：实例的元表是 Child（为了拿到 Child 的方法），Child 自己的元表才是 {__index = Parent}（为了继承），这两个 setmetatable 不能搞混。"),
            p("方法里用 self 访问实例字段，冒号调用会自动传入 self。定义方法时写成 function M:method() 等价于 function M.method(self)，调用时写 obj:method() 等价于 obj.method(obj)。如果漏了冒号，self 就会变成第一个普通参数，通常会得到 nil 相关的报错。这个错误在继承链里尤其隐蔽，因为方法可能来自父类，报错位置看起来和你写的代码对不上。"),
            p("原型模式的好处是方法共享。一百个实例只存一百份数据，方法只在原型表里存一份，内存占用远小于「每个对象都带一份方法」的写法。代价是查找要走元表链，比直接访问字段多一层间接。对绝大多数业务来说这点开销可以忽略，但在每帧都要访问的高频路径上，可以把常用字段缓存到局部变量，或者干脆用扁平的表结构，别为了「像面向对象」而牺牲性能。"),
            *code(
                r"""local Animal = {}
Animal.__index = Animal

function Animal.new(name)
  return setmetatable({name = name}, Animal)
end

function Animal:speak()
  return self.name .. ' makes a sound'
end

local Dog = setmetatable({}, {__index = Animal})
Dog.__index = Dog

function Dog.new(name)
  local d = Animal.new(name)
  return setmetatable(d, Dog)
end

function Dog:speak()
  return self.name .. ' barks'
end

print(Dog.new('Rex'):speak())
print(Animal.new('Cat'):speak())""",
                "Rex barks\nCat makes a sound",
            ),
            table(
                ["关系", "写法", "作用"],
                [
                    ["实例 → 类", "setmetatable(obj, Class)", "obj 能查到 Class 的方法"],
                    ["类 → 父类", "setmetatable(Class, {__index = Parent})", "Class 继承 Parent 的字段"],
                    ["类自身", "Class.__index = Class", "让实例的查找落在类上"],
                    ["调用", "obj:method()", "自动把 obj 作为 self 传入"],
                ],
            ),
            p("还有一个实用技巧是用 __index 表做「默认配置」。把默认值集中放在一张表里，实例的元表 __index 指向它，实例只存用户显式设置过的字段。读的时候不需要写 value = obj.x or default，因为缺失的键会自动落回默认表；写的时候直接赋值，不会污染默认表。这比在构造函数里逐字段填默认值更省代码，也让「哪些是默认值」集中在一处，改起来不容易漏。"),
            p("构造实例时要注意元表挂在哪一层。如果 make 函数先返回父类实例，再把它 setmetatable 成子类，原来的父类元表就被替换掉了，之前挂的字段仍然保留，但方法查找会改走子类链。这个顺序不能反：先创建数据表，再挂最终元表，最后填字段。顺序反了容易出现「方法找到了但字段读不到」的怪现象，因为 __index 只负责缺失的键，已存在的字段永远优先于元表。"),
            p("继承链不是越长越好。三层以上就开始难追踪：一个方法到底定义在哪儿，要沿着 __index 一路找。调试时可以在关键方法里打印 self 和 getmetatable(self)，确认走的是哪一层。设计上优先用组合代替继承：把可复用的能力拆成独立的模块表，需要时用字段挂上去，比拉长继承链更灵活，也更容易测试。Lua 没有强制的类体系，你完全可以不用继承，只用「表 + 函数」。"),
            *code(
                r"""local Base = {}
Base.__index = Base
function Base.new(v) return setmetatable({v = v}, Base) end
function Base:get() return self.v end
function Base:describe() return 'base:' .. self:get() end

local Derived = setmetatable({}, {__index = Base})
Derived.__index = Derived
function Derived.new(v) return setmetatable({v = v}, Derived) end
function Derived:describe() return 'derived:' .. self:get() end

print(Derived.new(7):describe())
print(Derived.new(7):get())""",
                "derived:7\n7",
            ),
            warn("setmetatable(Child, {__index = Parent}) 里创建的那张元表只服务于 Child 本身，不要拿它当实例的元表；实例的元表应该是 Child。两处都用 __index 指向不同的表，混淆会导致方法找不到。"),
            quiz(
                "实例 obj 的元表是 Dog，Dog 的元表是 {__index = Animal}。obj 调用一个只在 Animal 里定义的方法，能找到吗？",
                ["找不到，报错", "能找到，沿两级 __index 链", "只有 obj 自己定义才行", "需要重新 setmetatable"],
                1,
                "查找顺序是 obj → Dog → Animal，两级 __index 链会依次兜底，所以能拿到 Animal 的方法。",
            ),
        ],
        exercise(
            "带默认值的计数器类",
            "实现 Counter 类：Counter.new(start) 创建实例，实例有 inc(n) 和 get() 方法，默认从 0 开始。要求方法定义在 Counter 表上，实例只存数据。",
            "Counter = {}\nCounter.__index = Counter\n\nfunction Counter.new(start)\n  \nend\n\nlocal c = Counter.new(5)\nprint(c:inc(2), c:get())",
            "Counter.new 返回 setmetatable({value = start or 0}, Counter)；inc 里写 self.value = self.value + (n or 1)。",
            [
                "local c = Counter.new(5); assert(c:inc(2) == 7, '5 加 2 应为 7')",
                "local c = Counter.new(); assert(c:get() == 0, '默认应从 0 开始')",
                "local c = Counter.new(0); c:inc(); assert(c:get() == 1, '默认步长应为 1')",
                "local a, b = Counter.new(1), Counter.new(100); a:inc(); assert(b:get() == 100, '实例应互相独立')",
            ],
            "Counter = {}\nCounter.__index = Counter\n\nfunction Counter.new(start)\n  return setmetatable({value = start or 0}, Counter)\nend\n\nfunction Counter:inc(n)\n  self.value = self.value + (n or 1)\n  return self.value\nend\n\nfunction Counter:get()\n  return self.value\nend\n",
            120,
        ),
    ))

    items.append(lesson(
        "lua23", 422, 43, ADV, "运算符重载", "__add / __eq / __lt / __concat", 100,
        [
            h("让自定义类型参与运算"),
            p("元表可以让表参与原本只支持数字和字符串的运算。__add 处理加法，__sub、__mul、__div、__mod、__pow 分别对应减法、乘法、除法、取模、幂，__unm 处理一元负号。写 __add 时接收两个操作数，返回一个结果；结果通常也是带同样元表的表，这样连续运算才能继续工作。两个操作数类型不同时，Lua 会先找左边值的元方法，找不到再找右边的。"),
            p("比较运算符的规则更微妙。__eq 只在两个操作数都是表且类型相同时触发，不会拿表和数字比较；__lt 和 __le 在 Lua 5.2 里允许不同类型，但实际使用中最好保持同类型，否则语义会很混乱。比较函数必须返回 boolean，不能返回数字或 nil。写 __eq 时记得它只影响 ==，~= 会自动取反，不需要单独定义。"),
            p("__concat 处理 .. 拼接。注意它可能被调用两次：a .. b .. c 会先算 a .. b，再拿结果和 c 拼接，所以 __concat 必须能接受「另一个操作数不是同类」的情况，通常在里面判断类型，不是同类就转成字符串。__len 在 Lua 5.2 里对表有效，返回任何值都会被接受，但 # 的语义要求是非负整数，返回别的值可能导致后续逻辑出错。"),
            p("运算符重载是双刃剑。用得好，向量、矩阵、复数、金额这些类型的代码会非常接近数学表达式；用得不好，读者看到一个 + 却不知道它到底做了什么，调试成本陡增。原则是「行为符合直觉」：向量相加就该逐分量相加，金额相加就该按分相加。如果某个运算符的语义需要解释半天，那就不该重载它，老老实实写一个具名函数更清楚。"),
            *code(
                r"""Vec = {}
Vec.__index = Vec

local function vec(x, y)
  return setmetatable({x = x, y = y}, Vec)
end

Vec.__add = function(a, b)
  return vec(a.x + b.x, a.y + b.y)
end

Vec.__eq = function(a, b)
  return a.x == b.x and a.y == b.y
end

Vec.__tostring = function(v)
  return '(' .. v.x .. ',' .. v.y .. ')'
end

local a, b = vec(1, 2), vec(3, 4)
print(tostring(a + b))
print(a == vec(1, 2), a == b)""",
                "(4,6)\ntrue\tfalse",
            ),
            table(
                ["元方法", "运算符", "返回"],
                [
                    ["__add", "+", "任意值"],
                    ["__sub", "-", "任意值"],
                    ["__mul / __div", "* /", "任意值"],
                    ["__unm", "一元 -", "任意值"],
                    ["__eq", "==", "boolean"],
                    ["__lt / __le", "< / <=", "boolean"],
                    ["__concat", "..", "字符串或任意值"],
                ],
            ),
            p("运算符重载还要考虑和其他元方法的配合。比如定义了 __add 之后，a + 1（表加数字）也会调用 __add，这时第二个参数是数字而不是表，函数体里访问 b.x 就会报错。稳妥的做法是在 __add 开头判断类型，不同类型就走不同的分支，或者直接报一个清晰的错误信息。不要假设两个操作数一定同类型，调用方的写法你控制不了，防御性判断能省下很多排查时间。"),
            p("比较运算还有一条容易踩的规则：__eq 只在两个操作数都是表时才触发，而且它不参与 ~= 的推导——~= 会自动取反，不需要额外定义。__lt 和 __le 的关系也类似，a <= b 在 Lua 5.2 里会先找 __le，找不到再回退到 __lt，所以只定义 __lt 也能让 <= 工作。理解这套回退规则，能少写很多重复代码，也能解释为什么某些比较结果和预期不一样。"),
            p("写向量类的关键是保持「运算结果还是向量」。如果 __add 返回一个普通表，下次再相加就没有元表了，会报「attempt to perform arithmetic on a table value」。所以每个运算的返回值都要用同样的方式构造，最好抽一个内部构造函数统一处理，避免某处漏了 setmetatable。这个模式在写矩阵、复数、分数、金额类时完全一样。"),
            *code(
                r"""local Money = {}
Money.__index = Money
local function money(cents) return setmetatable({cents = cents}, Money) end

Money.__add = function(a, b) return money(a.cents + b.cents) end
Money.__sub = function(a, b) return money(a.cents - b.cents) end
Money.__eq = function(a, b) return a.cents == b.cents end
Money.__tostring = function(m)
  local sign = m.cents < 0 and '-' or ''
  local abs = math.abs(m.cents)
  local yuan = math.floor(abs / 100)
  local fen = abs % 100
  return sign .. yuan .. '.' .. (fen < 10 and '0' or '') .. fen
end

local total = money(1999) + money(250) - money(49)
print(tostring(total))
print(total == money(2200))""",
                "22.00\ntrue",
            ),
            tip("__eq 只在两个操作数都是表时触发。拿自定义类型和数字比较不会调用它，结果直接是 false，所以不要指望靠 __eq 实现「金额等于 19.99」这种跨类型比较。"),
            quiz(
                "定义 __add 时，结果的类型应该是什么？",
                ["任意类型都行", "最好仍是带同样元表的表，方便连续运算", "必须是数字", "必须是字符串"],
                1,
                "如果结果是普通表或数字，后续的 + 就无法继续触发元方法。保持结果类型一致，才能写出 a + b + c 这样的链式表达式。",
            ),
        ],
        exercise(
            "二维向量加法",
            "实现 Vec 模块：Vec.new(x, y) 创建向量，支持 + 运算和 == 比较，并提供 tostring 输出 (x,y) 格式。",
            "Vec = {}\nVec.__index = Vec\n\nfunction Vec.new(x, y)\n  \nend\n\nlocal a = Vec.new(1, 2)\nprint(tostring(a + Vec.new(3, 4)))",
            "Vec.new 返回 setmetatable({x=x, y=y}, Vec)；定义 Vec.__add 和 Vec.__eq，注意 __add 的结果也要用 Vec.new 构造。",
            [
                "local a = Vec.new(1, 2) + Vec.new(3, 4); assert(a.x == 4 and a.y == 6, '(1,2)+(3,4) 应为 (4,6)')",
                "local a = Vec.new(1, 2); assert(a == Vec.new(1, 2), '相同分量应相等')",
                "local a = Vec.new(1, 2); assert(a ~= Vec.new(2, 1), '不同分量应不相等')",
                "local a = Vec.new(1, 2) + Vec.new(3, 4) + Vec.new(1, 1); assert(a.x == 5 and a.y == 7, '应支持连续相加')",
            ],
            "Vec = {}\nVec.__index = Vec\n\nfunction Vec.new(x, y)\n  return setmetatable({x = x, y = y}, Vec)\nend\n\nVec.__add = function(a, b)\n  return Vec.new(a.x + b.x, a.y + b.y)\nend\n\nVec.__eq = function(a, b)\n  return a.x == b.x and a.y == b.y\nend\n\nVec.__tostring = function(v)\n  return '(' .. v.x .. ',' .. v.y .. ')'\nend\n",
            130,
        ),
    ))

    items.append(lesson(
        "lua24", 423, 43, ADV, "__call 与 __tostring", "可调用对象与打印友好", 90,
        [
            h("像函数一样使用对象"),
            p("__call 让表可以像函数一样被调用。给表挂上 __call 元方法后，写 obj(args) 实际执行的是 元方法(obj, args)。第一个参数永远是表本身，后面的参数才是调用时传的。这个机制适合做「带配置的函数」：表里存配置，__call 里用配置执行逻辑，调用方看起来就是在调一个函数，不需要知道背后是对象。"),
            p("__tostring 控制 tostring(obj) 的输出。没有它时，tostring 一张表得到的是 table: 0x... 这样的地址，几乎没法调试。定义 __tostring 返回一个有意义的描述，比如类名加关键字段，日志和报错信息立刻可读。注意它必须返回字符串，返回数字或其他类型会抛错。"),
            p("这两个元方法经常一起用。比如一个「查询构造器」：内部存 SQL 片段和参数，__call 执行查询，__tostring 返回拼好的 SQL 方便调试。再比如一个「配置对象」：__call 返回配置的副本，__tostring 输出可读的键值列表。它们把「对象」和「函数」「字符串」这两种日常形态连接起来，让 API 用起来更自然。"),
            p("__tostring 和 __concat 一起用能让日志更好读。定义了 __tostring 之后，字符串拼接仍然不会自动调用它，a .. b 走的是 __concat，需要你自己在 __concat 里调用 tostring。很多人以为定义了 __tostring 就能随便拼接，结果得到一个「table: 0x...」，还以为是元表没生效。记住：tostring 只影响显式转换和 print，其他上下文各走各的元方法。"),
            p("__index 和 __call 组合起来，可以实现「惰性初始化」的对象：第一次访问某个字段时才去计算并缓存，之后直接返回。写法是在 __index 函数里判断缓存表，没有就计算、写入、返回。这在加载昂贵资源时很有用，比如第一次访问配置时才解析文件，之后都走缓存。要注意缓存表本身要放在闭包里，不能放在对象字段上，否则序列化或遍历时会把缓存也带出去，产生难以解释的数据。"),
            p("__tostring 的输出应该稳定且可读。不要在里面放地址、时间戳这类每次都变的内容，否则日志无法比对，测试也无法断言。如果确实需要唯一标识，单独提供一个 id 字段，在 __tostring 里输出它，而不是依赖默认的表格地址。一个好的 __tostring 通常形如 ClassName(field=value, ...)，字段顺序固定，值做截断，长表只显示前几项并标注省略。"),
            p("不要滥用 __call。一个表如果能被调用，读者会默认它是函数，如果它同时还有一堆字段和方法，认知负担就上来了。判断标准是：这个对象的主要用途是不是「被调用」？是，就用 __call；不是，就用普通方法。__tostring 则可以放心多用，它只影响展示，不会改变语义，是提升可调试性的低成本手段。"),
            *code(
                r"""local Greeter = {}
Greeter.__index = Greeter

function Greeter.new(greeting)
  return setmetatable({greeting = greeting}, Greeter)
end

Greeter.__call = function(self, name)
  return self.greeting .. '，' .. name
end

Greeter.__tostring = function(self)
  return 'Greeter(' .. self.greeting .. ')'
end

local hello = Greeter.new('你好')
print(hello('V'))
print(tostring(hello))""",
                "你好，V\nGreeter(你好)",
            ),
            table(
                ["元方法", "触发", "第一个参数"],
                [
                    ["__call", "obj(args)", "obj 本身"],
                    ["__tostring", "tostring(obj) 或 print(obj)", "obj 本身"],
                    ["__len", "#obj", "obj 本身"],
                    ["__index", "obj.k", "obj 和键"],
                ],
            ),
            p("要注意本沙箱的 print 直接取值的字符串表示，不会调用 __tostring，所以 print(obj) 仍然输出 table: 0x...，想看到自定义描述必须显式写 print(tostring(obj))。这不是 Lua 语法的问题，而是运行时实现的选择，换成别的宿主可能行为不同。写日志时统一走 tostring 再拼接，就不依赖具体实现，也能保证格式稳定；如果返回值里含有制表符或换行，还会打乱表格对齐，必要时先做一次替换。"),
            *code(
                r"""local Range = {}
Range.__index = Range

function Range.new(a, b)
  return setmetatable({a = a, b = b}, Range)
end

Range.__call = function(self, i)
  return self.a + (i - 1)
end

Range.__len = function(self)
  return self.b - self.a + 1
end

Range.__tostring = function(self)
  return '[' .. self.a .. '..' .. self.b .. ']'
end

local r = Range.new(5, 9)
print(r(1), r(3), #r, tostring(r))""",
                "5\t7\t5\t[5..9]",
            ),
            warn("__call 的第一个参数是表本身，不是调用时传的第一个参数。写成 function(self, x) 才对，漏掉 self 会让所有参数整体左移一位，错误很难一眼看出。"),
            quiz(
                "给表 t 定义 __call 后，t(1, 2) 实际调用的是？",
                ["__call(1, 2)", "__call(t, 1, 2)", "t.call(1, 2)", "__call(2)"],
                1,
                "__call 的第一个参数永远是表本身，后面才是调用时传入的参数，所以是 __call(t, 1, 2)。",
            ),
        ],
        exercise(
            "可调用的乘法器",
            "实现 Multiplier：Multiplier.new(factor) 返回一个对象，调用 obj(x) 返回 factor * x，tostring(obj) 返回 'x<factor>' 形式，比如 'x3'。",
            "Multiplier = {}\nMultiplier.__index = Multiplier\n\nfunction Multiplier.new(factor)\n  \nend\n\nlocal triple = Multiplier.new(3)\nprint(triple(5), tostring(triple))",
            "定义 Multiplier.__call = function(self, x) return self.factor * x end，以及 __tostring 返回 'x' .. self.factor。",
            [
                "local m = Multiplier.new(3); assert(m(5) == 15, '3 乘 5 应为 15')",
                "local m = Multiplier.new(0); assert(m(99) == 0, '因子为 0 应返回 0')",
                "local m = Multiplier.new(2); assert(tostring(m) == 'x2', 'tostring 应输出 x2')",
                "local a, b = Multiplier.new(2), Multiplier.new(10); assert(a(3) == 6 and b(3) == 30, '两个乘法器应互相独立')",
            ],
            "Multiplier = {}\nMultiplier.__index = Multiplier\n\nfunction Multiplier.new(factor)\n  return setmetatable({factor = factor}, Multiplier)\nend\n\nMultiplier.__call = function(self, x)\n  return self.factor * x\nend\n\nMultiplier.__tostring = function(self)\n  return 'x' .. self.factor\nend\n",
            120,
        ),
    ))

    items.append(lesson(
        "lua25", 424, 43, ADV, "协程", "create / resume / yield", 110,
        [
            h("可以暂停的函数"),
            p("协程是一种可以暂停和恢复的执行流。coroutine.create(f) 把函数包装成一个协程对象，coroutine.resume(co, ...) 启动或恢复它，协程内部调用 coroutine.yield(...) 把控制权交回调用方。resume 返回 true 加上 yield 的值；协程结束时会返回 true 加上 return 的值；出错时返回 false 加错误信息。这套协议让「生产者—消费者」可以写成两个顺序执行的函数。"),
            p("协程的状态有四种：suspended（挂起，还没启动或刚 yield）、running（正在执行）、normal（恢复了别的协程，自己让位）、dead（结束或出错）。coroutine.status(co) 查询状态，coroutine.running() 在协程内部返回当前协程和「是否是主线程」的布尔值。主线程里 running 返回 nil 和 true。理解状态机，才能判断一个协程还能不能被 resume。"),
            p("coroutine.wrap(f) 是 create 的简化版，它返回一个函数，调用这个函数就等于 resume，但出错时直接抛异常而不是返回 false。用它写迭代器特别顺手：一个循环里不断 yield，外面用 for 循环取值。注意 wrap 丢掉了错误信息里的 ok 标志，如果你需要区分「正常结束」和「出错」，还是用 create 加手动 resume 更清楚。"),
            p("协程不是线程，同一时刻只有一个协程在跑，切换是显式的，不需要锁，也没有竞态。它适合表达「有来有回」的流程：逐行解析文件、遍历树的每个节点、把一个复杂计算拆成多步让出控制权。不适合做真正的并行计算，那需要多线程或多进程。把协程当轻量级的状态机用，是最不容易出错的方式。"),
            *code(
                r"""local co = coroutine.create(function(a, b)
  print('start', a + b)
  local x = coroutine.yield(a * b)
  print('resumed', x)
  return 'done'
end)

print(coroutine.resume(co, 2, 3))
print(coroutine.status(co))
print(coroutine.resume(co, 'hello'))
print(coroutine.status(co))""",
                "start\t5\ntrue\t6\nsuspended\nresumed\thello\ntrue\tdone\ndead",
            ),
            table(
                ["函数", "作用", "返回"],
                [
                    ["create(f)", "创建协程", "协程对象"],
                    ["resume(co, ...)", "启动或恢复", "true + 值 / false + 错误"],
                    ["yield(...)", "暂停并交回控制权", "下次 resume 时收到参数"],
                    ["status(co)", "查询状态", "suspended / running / normal / dead"],
                    ["wrap(f)", "包装成普通函数", "调用即 resume，错误直接抛"],
                ],
            ),
            p("协程的另一个常见用途是把「深度优先遍历」写成顺序代码。遍历树时，递归写法要维护调用栈，改成协程后每访问一个节点就 yield 一次，调用方用 for 逐个消费，遍历逻辑保持从上到下的阅读顺序，也不需要一次性把整棵树展开成数组。这个技巧在遍历文件目录、解析嵌套结构时特别顺手，代价是要理解 yield 的位置决定了「什么时候交还控制权」。"),
            p("协程和 pcall 的组合要小心。协程内部抛出的错误会被 resume 捕获成 false 加错误信息，协程随即变成 dead；但如果错误发生在 yield 之后、resume 之外的地方，可能会直接中断整个调用。稳妥的写法是在协程函数体内部用 pcall 包住可能失败的逻辑，把错误转换成返回值再 yield 出去，这样外层始终能拿到结构化的结果，而不是一个无法恢复的 dead 协程。"),
            p("用协程写生成器是最常见的练手项目。函数里一个 while 循环不断 yield 出下一个值，外面用 for 逐个消费，生产逻辑和消费逻辑各自保持顺序，不需要维护一堆状态变量。它比一次性生成整个数组省内存，也比手写迭代器闭包更直观，因为代码是从上往下读的，不会被拆成「初始化 + 每次调用做什么」两段。"),
            *code(
                r"""local function range_gen(n)
  return coroutine.wrap(function()
    for i = 1, n do
      coroutine.yield(i)
    end
  end)
end

local sum = 0
for v in range_gen(5) do
  sum = sum + v
end
print(sum)

local co = coroutine.create(function()
  coroutine.yield('a')
  coroutine.yield('b')
end)
print(coroutine.resume(co))
print(coroutine.resume(co))
print(coroutine.resume(co))""",
                "15\ntrue\ta\ntrue\tb\ntrue",
            ),
            visualize(
                "协程的挂起与恢复",
                "co 依次经历 suspended → running → suspended → dead",
                [
                    frame("resume(2,3) 启动", [("status", "running"), ("yield 值", "6")], ["status"]),
                    frame("yield 交出控制权", [("status", "suspended"), ("x", "nil")], ["status"]),
                    frame("resume('hello') 恢复", [("status", "running"), ("x", "hello")], ["x"]),
                    frame("函数返回 'done'", [("status", "dead"), ("返回值", "done")], ["status"]),
                ],
            ),
            warn("协程出错后不会自动恢复。resume 返回 false 时协程已经变成 dead，再 resume 只会继续得到 false。需要重试就得重新 create，不能指望它自己回到可用状态。"),
            quiz(
                "协程内部调用 coroutine.yield(1) 后，外部的 resume 返回什么？",
                ["1", "true, 1", "false, 1", "nil"],
                1,
                "resume 成功时先返回 true 表示没有出错，后面依次是 yield 传出的值，所以是 true 和 1。",
            ),
        ],
        exercise(
            "协程生成斐波那契",
            "实现 fib_gen(n)：用协程返回一个迭代器，依次产出前 n 个斐波那契数（从 1, 1 开始）。",
            "function fib_gen(n)\n  \nend\n\nfor v in fib_gen(5) do\n  print(v)\nend",
            "用 coroutine.wrap 包一个函数，内部维护 a, b = 1, 1，循环 n 次每次 yield a，然后 a, b = b, a + b。",
            [
                "local out = {}; for v in fib_gen(5) do out[#out + 1] = v end; assert(table.concat(out, ',') == '1,1,2,3,5', '前五个斐波那契数应为 1,1,2,3,5')",
                "local out = {}; for v in fib_gen(1) do out[#out + 1] = v end; assert(#out == 1 and out[1] == 1, 'n 为 1 时应只产出 1')",
                "local out = {}; for v in fib_gen(0) do out[#out + 1] = v end; assert(#out == 0, 'n 为 0 时不应产出')",
                "local out = {}; for v in fib_gen(7) do out[#out + 1] = v end; assert(out[7] == 13, '第七个数应为 13')",
            ],
            "function fib_gen(n)\n  return coroutine.wrap(function()\n    local a, b = 1, 1\n    for _ = 1, n do\n      coroutine.yield(a)\n      a, b = b, a + b\n    end\n  end)\nend\n",
            140,
        ),
    ))

    return items


def build_core():
    items = []
    items.extend(_core_11_15())
    items.extend(_core_16_20())
    return items


CORE_ITEMS = build_core()


def _adv_26_30():
    items = []

    items.append(lesson(
        "lua26", 425, 43, ADV, "string 模式匹配", "%a %d %s 与捕获组", 110,
        [
            h("比正则更轻的模式语言"),
            p("Lua 的模式匹配不是正则，它更小、更快，也没有回溯爆炸的风险。字符类用百分号开头：%a 字母、%d 数字、%s 空白、%w 字母数字、%p 标点、%l 小写、%u 大写，大写形式表示取反，比如 %D 是非数字。量词有 *（零或多次）、+（一次或多次）、-（零或多次但尽量短）、?（零或一次）。这套语法覆盖了绝大多数文本处理需求。"),
            p("捕获组用圆括号包住，match 会按顺序返回各组内容。位置捕获用 () 表示，返回匹配开始的下标，适合做「在哪个位置」的判断。gsub 的替换串里可以用 %1、%2 引用捕获组，%0 表示整个匹配。注意 % 在替换串里有特殊含义，想输出字面百分号要写 %%。这些规则和正则很像，但细节不同，直接套正则经验容易出错。"),
            p("锚点用 ^ 表示开头、$ 表示结尾，它们只在模式的首尾才有特殊含义。%b 用于匹配成对的字符，比如 %b() 匹配一对括号，包括嵌套；%f 是边界匹配，用来判断「前面是某类字符、后面不是」。这两个是 Lua 特有的，写解析器时很好用。转义元字符用 %，比如 %. 匹配字面点号，%( 匹配左括号。"),
            p("模式匹配的性能取决于模式本身。gmatch 逐个产出匹配，适合流式处理大文本；gsub 一次替换全部，内部会反复扫描。避免写「贪婪匹配一大段再回溯」的模式，Lua 的 - 量词就是为了解决这个问题：它尽量匹配最短，配合锚点可以精确截取两个标记之间的内容，比如 ^%s*(.-)%s*$ 就是标准的 trim 写法。"),
            *code(
                r"""print(string.match('key=value', '(%w+)=(%w+)'))
print(string.match('2026-11-06', '(%d+)-(%d+)-(%d+)'))
print(string.gsub('a1b2', '%d', '#'))
print(('  trim  '):match('^%s*(.-)%s*$'))
print(string.match('(abc)', '%b()'))""",
                "key\tvalue\n2026\t11\t06\na#b#\t2\ntrim\n(abc)",
            ),
            table(
                ["模式", "含义", "示例"],
                [
                    ["%a / %d / %s", "字母 / 数字 / 空白", "'abc123':match('%a+') → abc"],
                    ["%w", "字母或数字", "'a1':match('%w+') → a1"],
                    [".", "任意字符", "'ab':match('a.') → ab"],
                    ["* + - ?", "量词", "'aaa':match('a+') → aaa"],
                    ["(...)", "捕获组", "'a=1':match('(%w+)=(%w+)')"],
                    ["%b()", "成对括号", "'(x)':match('%b()') → (x)"],
                    ["^...$", "首尾锚点", "整串匹配"],
                ],
            ),
            p("gsub 的第四个参数可以限制替换次数，写 1 表示只替换第一个匹配。这个参数在「只改开头一处」的场景里很有用，比如给一行文本加前缀。gmatch 没有次数限制，需要提前退出就在循环里 break。选择 gsub 还是 gmatch，取决于你是要「生成新字符串」还是「逐个处理匹配」，前者一次成型，后者更灵活，也更容易中途停止。"),
            p("捕获组可以嵌套，返回值按左括号出现的顺序排列。比如 ((%a+)(%d+)) 会先返回整体，再返回字母部分和数字部分。如果只需要其中某一段，在模式里少写一层括号即可，不必在结果里挑。位置捕获 () 不消耗字符，只记录位置，适合做「从这里开始匹配」的标记。gsub 的替换函数收到的是所有捕获组作为参数，返回 nil 表示保留原样，返回字符串则替换。"),
            p("一个常见误区是把 Lua 模式当正则用，写出 \\d+ 这种语法。Lua 里没有反斜杠转义，数字类就是 %d，写 \\d 会去匹配字面的反斜杠和 d。另一个误区是以为点号只匹配非换行字符，实际上它匹配任意字符包括换行，想排除换行要写 [^\\n]。遇到模式不生效，先检查是不是把正则语法搬过来了，再看特殊字符有没有转义。"),
            *code(
                r"""for k, v in string.gmatch('a=1,b=2,c=3', '(%w+)=(%w+)') do
  print(k, v)
end

print(string.gsub('hello world', '(%w+)', '<%1>'))
print(string.find('a.b', '%.', 1, false))
print(('abc123'):match('%a+(%d+)'))""",
                "a\t1\nb\t2\nc\t3\n<hello> <world>\t2\n2\t2\n123",
            ),
            practice(
                "逐个取出单词",
                "for w in ('one two three'):gmatch('%a+') do\n  print(w)\nend",
                "one\ntwo\nthree",
                "gmatch 返回迭代器，直接放在 for ... in 后面即可逐个取值。",
            ),
            tip("gsub 的替换串里，%1 到 %9 是捕获组，%0 是整个匹配。想插入字面百分号写 %%。替换函数返回 nil 表示保留原匹配，返回 false 表示不替换。"),
            quiz(
                "Lua 模式中匹配「一个或多个数字」的正确写法是？",
                ["\\\\d+", "%d+", "[0-9]+", "d+"],
                1,
                "Lua 用 %d 表示数字类，+ 表示一次或多次，所以是 %d+。\\\\d+ 是正则语法，在 Lua 里会匹配反斜杠和 d。",
            ),
        ],
        exercise(
            "提取所有数字",
            "实现 extract_numbers(s)：返回字符串 s 中所有连续数字组成的数组，顺序与原串一致。",
            "function extract_numbers(s)\n  \nend\n\nprint(table.concat(extract_numbers('a1b22c333'), ','))",
            "用 string.gmatch(s, '%d+') 遍历，把每个匹配 push 进结果数组。",
            [
                "assert(table.concat(extract_numbers('a1b22c333'), ',') == '1,22,333', '应依次提取 1、22、333')",
                "assert(#extract_numbers('abc') == 0, '没有数字应返回空数组')",
                "assert(table.concat(extract_numbers('42'), ',') == '42', '纯数字应提取自身')",
                "assert(table.concat(extract_numbers('1 2 3'), ',') == '1,2,3', '空格分隔的数字应分别提取')",
            ],
            "function extract_numbers(s)\n  local out = {}\n  for n in s:gmatch('%d+') do\n    out[#out + 1] = n\n  end\n  return out\nend\n",
            140,
        ),
    ))

    items.append(lesson(
        "lua27", 426, 43, ADV, "序列化与配置表", "把表转成文本再读回来", 110,
        [
            h("表的文本表示"),
            p("Lua 没有内置的 JSON 库，但把表转成文本非常自然：遍历键值对，拼成 key=value 这样的行，写入配置时人也能读。反过来读回来时，需要自己写一个小解析器：按行切分，用 string.match 取出键和值，再按类型转换。这个「序列化 + 解析」的往返过程，是配置文件、存档、日志这几类需求共同的核心。"),
            p("序列化的关键是区分类型。数字直接 tostring，字符串要能表达空格和特殊字符，布尔要区分 true/false，嵌套表则要另想办法（可以用前缀路径，比如 hero.name=V 表示嵌套字段）。这一讲只处理扁平表，规则简单但足够实用：每行一个 key=value，字符串原样写，数字和布尔在解析时自动识别。关键约定是「值里不能有换行」，有换行就先转义，否则一条记录会被拆成两条。"),
            p("解析要按类型还原。读到 \"66\" 这样的内容，应该转成数字 66 还是保留字符串，取决于你的约定。常见的做法是：能 tonumber 成功且看起来像数字就转数字，\"true\"/\"false\" 转布尔，其余保留字符串。这个启发式规则在配置场景里够用，但也有坑，比如版本号 \"1.10\" 会被转成 1.1，所以真正的配置系统会给每个字段声明类型，而不是靠猜。"),
            p("配置表的组织方式值得单独设计。常见做法是「默认配置 + 用户覆盖」两层：默认配置写死在代码里，用户配置只存差异，合并时逐字段覆盖。合并函数要区分「用户显式设为 false」和「用户没设置」，前者应该覆盖，后者应该保留默认值，所以判断要用 ~= nil 而不是 if v then。这个细节决定了配置系统好不好用，也是很多默认值 bug 的根源。"),
            *code(
                r"""local function serialize(t)
  local keys = {}
  for k in pairs(t) do keys[#keys + 1] = k end
  table.sort(keys)
  local lines = {}
  for _, k in ipairs(keys) do
    lines[#lines + 1] = k .. '=' .. tostring(t[k])
  end
  return table.concat(lines, '\n')
end

local cfg = {name = 'V', level = 66, online = true}
local text = serialize(cfg)
print(text)""",
                "level=66\nname=V\nonline=true",
            ),
            table(
                ["类型", "序列化写法", "解析时的判断"],
                [
                    ["number", "tostring(v)", "tonumber 成功则转数字"],
                    ["string", "原样写入", "默认保留字符串"],
                    ["boolean", "tostring(v)", "等于 'true' / 'false' 时转布尔"],
                    ["table", "不展开（本讲）", "需要路径或 JSON 格式"],
                ],
            ),
            p("解析函数的骨架是遍历每一行、跳过空行和注释行、用 match 拆出键和值。string.gmatch 配合模式 ([^=]+)=(.+) 就能一次取出两段：左边是键，右边是值。注意 .+ 是贪婪匹配，值里如果有等号会全部保留在值里，这通常正是想要的行为，因为键一般不含等号。拆完之后做类型转换，写进结果表。"),
            *code(
                r"""local function parse(text)
  local out = {}
  for line in text:gmatch('[^\n]+') do
    line = line:match('^%s*(.-)%s*$')
    if line ~= '' and line:sub(1, 1) ~= '#' then
      local k, v = line:match('^([^=]+)=(.+)$')
      if k then
        k = k:match('^%s*(.-)%s*$')
        v = v:match('^%s*(.-)%s*$')
        local n = tonumber(v)
        if n ~= nil then
          out[k] = n
        elseif v == 'true' or v == 'false' then
          out[k] = (v == 'true')
        else
          out[k] = v
        end
      end
    end
  end
  return out
end

local parsed = parse('level=66\nname=V\nonline=true\n# comment')
print(parsed.level, parsed.name, parsed.online)""",
                "66	V	true",
            ),
            p("读取配置后一定要校验。解析只保证格式能对上，不保证字段齐全、类型正确、取值合理。一个稳妥的做法是写一个 validate 函数，逐字段检查类型和范围，缺失的用默认值补上，非法的直接报错并指出字段名。配置错误在启动时暴露，比运行到一半才发现好得多；尤其是数值字段，字符串 '66' 和数字 66 在 Lua 里参与运算的结果可能一样，但比较和序列化行为不同，早点统一类型能省很多事。"),
            *code(
                r"""local defaults = {level = 1, hp = 100, name = 'unknown'}

local function merge(base, override)
  local out = {}
  for k, v in pairs(base) do out[k] = v end
  for k, v in pairs(override) do
    if v ~= nil then out[k] = v end
  end
  return out
end

local merged = merge(defaults, {level = 66, hp = false})
print(merged.level, merged.hp, merged.name)""",
                "66	false	unknown",
            ),
            warn("自己写的格式只适合小配置。字段一多、类型一变（嵌套、数组、转义），手写解析器就会失控，那时应该换成 JSON 这类成熟格式和对应库，而不是继续加 if。"),
            quiz(
                "把配置写成 key=value 的文本格式，最大的局限是？",
                ["速度太慢", "不支持嵌套和复杂类型，需要自己定转义规则", "不能被读取", "只能存数字"],
                1,
                "扁平文本格式表达不了嵌套表和数组，值里出现分隔符或换行还要额外转义，字段一多就会变得难维护。",
            ),
        ],
        exercise(
            "扁平表序列化",
            "实现 serialize_flat(t)：把只有字符串/数字/布尔值的一层表转成每行 key=value 的文本，键按字母升序排列，行之间用换行分隔。",
            "function serialize_flat(t)\n  \nend\n\nprint(serialize_flat({name = 'V'}))",
            "先收集键并 table.sort，再逐行拼 k .. '=' .. tostring(v)，最后 table.concat(lines, '\n')。",
            [
                "local s = serialize_flat({name = 'V'}); assert(s == 'name=V', '单个字段应输出 name=V')",
                "local s = serialize_flat({b = 2, a = 1}); assert(s == 'a=1\\nb=2', '键应按字母升序')",
                "local s = serialize_flat({ok = true}); assert(s == 'ok=true', '布尔应输出 true')",
                "local s = serialize_flat({}); assert(s == '', '空表应返回空串')",
            ],
            "function serialize_flat(t)\n  local keys = {}\n  for k in pairs(t) do keys[#keys + 1] = k end\n  table.sort(keys)\n  local lines = {}\n  for _, k in ipairs(keys) do\n    lines[#lines + 1] = k .. '=' .. tostring(t[k])\n  end\n  return table.concat(lines, '\\n')\nend\n",
            130,
        ),
    ))

    items.append(lesson(
        "lua28", 427, 43, ADV, "函数式编程", "map / filter / reduce", 110,
        [
            h("把函数当作参数"),
            p("函数式编程的核心是把「做什么」和「怎么做」分开：map 对每个元素应用一个函数，filter 按条件筛选，reduce 把数组折叠成一个值。Lua 没有内置这些函数，但用函数作为参数、配合 ipairs 遍历，几行就能写出来。真正的价值不在函数本身，而在这种「把循环的骨架抽出来，把变化的逻辑传进去」的思路。"),
            p("写 map 时要注意返回新表还是原地修改。函数式风格强调不修改输入，所以 map 返回新表，原表保持不变。这在链式调用里很重要：map → filter → reduce 每一步都产生新表，原始数据始终可复用。代价是内存开销，数据量大时要权衡。Lua 的表是引用类型，一旦某处原地修改，调用方拿到的数据就变了，排查起来很麻烦。"),
            p("reduce 的初始值是个容易出错的地方。sum 的初始值是 0，product 是 1，字符串拼接是空串，找最大值则应该用第一个元素而不是 0（否则全是负数时会出错）。把初始值作为参数传进来，让调用方决定，比在函数里硬编码更通用。空数组加初始值时直接返回初始值，这个边界要单独处理。"),
            p("函数式写法不是万能的。它适合「对数据做一系列变换」的场景，不适合「有复杂状态和提前退出」的流程。Lua 没有尾调用优化的保证，链式嵌套太深也会有性能开销。实际项目里往往是混合风格：数据处理用 map/filter，控制流程用循环，关键路径手写优化。选择的标准是「这段代码三个月后还看不看得懂」，而不是「够不够函数式」。"),
            *code(
                r"""local function map(t, f)
  local out = {}
  for i, v in ipairs(t) do out[i] = f(v) end
  return out
end

local function filter(t, pred)
  local out = {}
  for _, v in ipairs(t) do
    if pred(v) then out[#out + 1] = v end
  end
  return out
end

local function reduce(t, f, init)
  local acc = init
  for _, v in ipairs(t) do acc = f(acc, v) end
  return acc
end

local nums = {1, 2, 3, 4, 5}
local squares = map(nums, function(x) return x * x end)
local evens = filter(squares, function(x) return x % 2 == 0 end)
print(table.concat(evens, ','))
print(reduce(nums, function(a, b) return a + b end, 0))""",
                "4,16\n15",
            ),
            table(
                ["函数", "作用", "返回"],
                [
                    ["map(t, f)", "对每个元素应用 f", "新数组"],
                    ["filter(t, pred)", "保留 pred 为真的元素", "新数组"],
                    ["reduce(t, f, init)", "从左到右折叠", "单个值"],
                    ["any(t, pred)", "是否存在满足条件的元素", "boolean"],
                    ["all(t, pred)", "是否全部满足条件", "boolean"],
                ],
            ),
            p("写 map/filter 时要注意它们对稀疏数组的处理。ipairs 遇到 nil 就停，所以中间有空洞的数组只会处理前半段；pairs 能遍历全部键，但顺序不保证，结果数组的下标也会变得不可预测。函数式工具默认假设输入是连续数组，这个假设要写进注释，调用方才知道边界在哪里。输入可能稀疏时，先过滤成连续数组再传进去，比在工具函数里到处判断更清晰。"),
            p("高阶函数还有一个常被忽略的用途是「延迟求值」。比如把「要执行的查询」包装成函数，等真正需要结果时才调用；或者把「失败时的兜底逻辑」作为函数传入，主流程成功就不执行它。这种写法把控制流从「先算再判断」变成「按需计算」，在数据量大或副作用昂贵的场景里能省掉大量无用功。Lua 的函数是值，传函数和传数字一样自然，不需要额外的语法支持。"),
            p("链式调用可以写得更紧凑：reduce(filter(map(nums, square), is_even), add, 0)。但嵌套三层以上就该拆成中间变量，否则读的时候要从内往外倒着看。给中间结果起个有意义的名字，比省两行代码更重要。Lua 没有管道运算符，所以「先拆变量再串起来」是最实用的风格，调试时也能逐个打印中间结果。"),
            *code(
                r"""local function compose(f, g)
  return function(x)
    return f(g(x))
  end
end

local function inc(x) return x + 1 end
local function double(x) return x * 2 end

local both = compose(inc, double)
print(both(5))

local function memoize(f)
  local cache = {}
  return function(x)
    if cache[x] == nil then cache[x] = f(x) end
    return cache[x]
  end
end

local slow = memoize(function(n) return n * n end)
print(slow(6), slow(6))""",
                "11\n36\t36",
            ),
            tip("compose(f, g) 的语义是「先执行 g，再执行 f」，从右往左读。如果你觉得别扭，可以改写成 pipe(f, g) 表示从左往右，团队里统一一种就好，别两种混用。"),
            quiz(
                "reduce 求最大值的初始值应该用什么？",
                ["0", "第一个元素或负无穷", "1", "空字符串"],
                1,
                "如果初始值用 0，数组全是负数时会错误地返回 0。应该用第一个元素，或者用 -math.huge 作为下界。",
            ),
        ],
        exercise(
            "映射与过滤",
            "实现 transform(nums)：先对所有元素乘以 2，再去掉小于 10 的结果，返回新数组。必须用 map 和 filter 两个辅助函数（可以自己定义）。",
            "function transform(nums)\n  \nend\n\nprint(table.concat(transform({1, 5, 10}), ','))",
            "先定义 map 和 filter（或内联实现），再组合：filter(map(nums, double), at_least_10)。",
            [
                "assert(table.concat(transform({1, 5, 10}), ',') == '10,20', '1*2=2 被过滤，5*2=10、10*2=20 保留')",
                "assert(#transform({}) == 0, '空数组应返回空数组')",
                "assert(#transform({1, 2}) == 0, '全部小于 10 时应返回空数组')",
                "assert(table.concat(transform({6}), ',') == '12', '6*2=12 应保留')",
            ],
            "function transform(nums)\n  local doubled = {}\n  for i, v in ipairs(nums) do doubled[i] = v * 2 end\n  local out = {}\n  for _, v in ipairs(doubled) do\n    if v >= 10 then out[#out + 1] = v end\n  end\n  return out\nend\n",
            140,
        ),
    ))

    items.append(lesson(
        "lua29", 428, 43, ADV, "常用算法", "排序、查找、去重与统计", 120,
        [
            h("把基础拼成解法"),
            p("这一讲把前面学的东西组合起来解决几类常见问题。排序直接用 table.sort，但真实场景往往要按字段排、要稳定、要只取前几名，这些都需要在比较函数和数据结构上做文章。查找分线性查找和二分查找，后者要求数据已排序，时间复杂度从 O(n) 降到 O(log n)，写之前先确认数组有序，否则结果不可靠。"),
            p("去重的经典做法是用字典记录出现过的值：遍历数组，如果 seen[v] 为 nil 就保留并标记，否则跳过。这个方法时间复杂度 O(n)，比双重循环的 O(n^2) 快得多，代价是需要额外的表。注意 nil 不能作为键值参与去重，因为表里存不了「值为 nil 的键」，遇到可能含 nil 的数据要先过滤。"),
            p("二分查找的边界是最容易写错的地方。用 lo, hi 表示当前搜索区间，循环条件写 lo <= hi，中间值写 math.floor((lo + hi) / 2)，比较后移动 lo 或 hi 时要想清楚新区间是否包含 mid。建议写完拿三个元素的数组手推一遍，再测「找不到」「在头部」「在尾部」三种情况，基本就能覆盖常见错误。"),
            p("统计类问题通常用一次遍历加字典：计数、求和、求平均、找众数都能在 O(n) 内完成。需要同时维护多个统计量时，用一个表把它们装起来，遍历结束一次性返回，比多次遍历更高效。真实数据里还要考虑异常值：空数组、全相同、含 nil，这些边界在写之前就该列出来，而不是等测试报错再补。"),
            *code(
                r"""local function binary_search(t, target)
  local lo, hi = 1, #t
  while lo <= hi do
    local mid = math.floor((lo + hi) / 2)
    if t[mid] == target then
      return mid
    elseif t[mid] < target then
      lo = mid + 1
    else
      hi = mid - 1
    end
  end
  return nil
end

local sorted = {1, 3, 5, 7, 9}
print(binary_search(sorted, 7))
print(binary_search(sorted, 4))""",
                "4\nnil",
            ),
            table(
                ["问题", "方法", "复杂度"],
                [
                    ["排序", "table.sort + 比较函数", "O(n log n)"],
                    ["有序查找", "二分查找", "O(log n)"],
                    ["无序查找", "线性遍历", "O(n)"],
                    ["去重", "字典标记", "O(n)"],
                    ["计数", "字典累加", "O(n)"],
                ],
            ),
            p("前缀和是另一件值得掌握的武器：预先算一个 prefix 数组，prefix[i] 表示前 i 个元素的和，之后任意区间 [l, r] 的和就是 prefix[r] - prefix[l-1]，查询变成 O(1)。构造前缀和只要一次遍历，代价是额外一个数组。频繁做区间求和的场景，这个预处理几乎总是划算的。要注意下标从 1 开始，prefix[0] 要单独约定为 0，否则 l=1 时会越界。"),
            p("滑动窗口是另一类高频算法：维护一个左右指针，右指针扩张、左指针收缩，窗口内的数据满足某个条件。求最长无重复子串、和不超过 K 的最长子数组都用这个套路。实现时用字典记录窗口内元素的出现次数，扩张时加一、收缩时减一，减到 0 就删键。窗口类问题的难点不在代码，而在想清楚「什么时候收缩」和「收缩到什么程度」，把这两个条件写对，循环结构几乎是固定的。"),
            p("去重时如果还要求保持原顺序，就不能先排序再去重，必须用「见过就跳过」的方式一次遍历完成。如果需要去重后排序，可以先去重再 sort，两步都很清晰。要注意 table.sort 不保证稳定，相同键的元素相对顺序可能变；需要稳定排序时，把原始下标作为第二比较键，先比主键再比下标，就能得到确定的结果。"),
            *code(
                r"""local function dedupe(t)
  local seen, out = {}, {}
  for _, v in ipairs(t) do
    if seen[v] == nil then
      seen[v] = true
      out[#out + 1] = v
    end
  end
  return out
end
print(table.concat(dedupe({3, 1, 3, 2, 1}), ','))

local function mode(t)
  local counts, best, bestN = {}, nil, 0
  for _, v in ipairs(t) do
    counts[v] = (counts[v] or 0) + 1
    if counts[v] > bestN then bestN, best = counts[v], v end
  end
  return best, bestN
end
print(mode({1, 2, 2, 3, 3, 3}))""",
                "3,1,2\n3\t3",
            ),
            warn("二分查找的前提是数组已排序。对无序数组用二分，结果可能返回 nil 也可能返回错误的下标，而且不会报错，是最难查的一类 bug。"),
            quiz(
                "对无序数组使用二分查找会发生什么？",
                ["一定返回 nil", "可能返回错误结果且不报错", "自动先排序", "抛出异常"],
                1,
                "二分依赖有序性来排除区间。数组无序时，排除逻辑失效，可能找不到存在的元素，也可能返回错误位置，但不会有任何报错。",
            ),
        ],
        exercise(
            "两数之和",
            "实现 two_sum(nums, target)：返回数组中两个下标 i < j，使 nums[i] + nums[j] == target；找不到返回 nil。要求 O(n) 复杂度，用字典记录「还差多少」。",
            "function two_sum(nums, target)\n  \nend\n\nprint(two_sum({2, 7, 11, 15}, 9))",
            "遍历数组，对每个 nums[i] 先查 need = target - nums[i] 是否在字典里，在就返回两个下标；不在就把 nums[i] 和下标存进字典。",
            [
                "local i, j = two_sum({2, 7, 11, 15}, 9); assert(i == 1 and j == 2, '应返回 1 和 2')",
                "assert(two_sum({1, 2}, 100) == nil, '找不到应返回 nil')",
                "local i, j = two_sum({3, 3}, 6); assert(i == 1 and j == 2, '重复值也应正确配对')",
                "local i, j = two_sum({-1, 0, 1}, 0); assert(i == 1 and j == 3, '负数应能参与计算')",
            ],
            "function two_sum(nums, target)\n  local seen = {}\n  for i, v in ipairs(nums) do\n    local need = target - v\n    if seen[need] ~= nil then\n      return seen[need], i\n    end\n    seen[v] = i\n  end\n  return nil\nend\n",
            150,
        ),
    ))

    items.append(lesson(
        "lua30", 429, 43, ADV, "综合项目", "状态机与背包系统", 150,
        [
            h("把三十讲串成一个作品"),
            p("最后一讲做一个能跑的小项目：一个带状态机的背包系统。状态机负责「当前处于什么模式」，比如探索、战斗、背包；背包负责「有哪些物品、各多少个」。两者用表实现，状态用字符串表示，转移用一张表描述，物品用字典存储。整个项目不到一百行，但用到了表、函数、闭包、元表、字符串处理这些全部核心知识。"),
            p("状态机的设计要点是把「状态」和「转移」分开。状态是一组字符串常量，转移表用「从哪个状态」到「允许去哪些状态」的映射。切换时先检查目标状态是否合法，不合法就返回 false 和原因，而不是直接改状态。这样调用方可以决定是报错、忽略还是提示用户，状态机本身不负责展示。"),
            p("背包系统的核心是一张字典 items，键是物品名，值是数量。add 增加数量，remove 减少数量并在数量为 0 时删除键，count 查询数量，list 返回按名称排序的清单。所有操作都要处理边界：添加数量必须为正，移除不能超过现有数量，移除不存在的物品要返回失败而不是悄悄创建负数。"),
            p("项目做到最后，建议自己加一道「存档与读档」：把背包的 items 和状态机的当前状态序列化成文本，重新加载后恢复。这一步会把序列化、解析、状态校验三块知识串起来，也会暴露很多平时注意不到的问题，比如某个字段是数字还是字符串、空背包怎么表示、非法状态怎么拒绝。能把这些边界处理好，这个项目就算真正完成了。"),
            p("状态机还可以加「进入」和「离开」钩子：每次切换状态时，先执行旧状态的 on_exit，再执行新状态的 on_enter，用来做资源释放和初始化。钩子表同样用数据描述，键是状态名，值是函数。这样状态机本身只负责调度，具体行为由数据决定，加新状态只需要补两条钩子，不用改调度逻辑。这个模式在游戏、工作流、协议解析里都非常常见，值得反复练。"),
            p("把两者组合起来时，用闭包把状态藏起来，只暴露方法。这样外部无法直接改 items 或 state，必须走 add、remove、switch 这些入口，所有校验都集中在一处。这是本课程反复强调的「私有状态 + 显式接口」模式，也是真实项目里最常用的组织方式。写完可以自己加功能，比如背包容量上限、物品分类、状态切换时自动保存，这些都是很好的练习。"),
            *code(
                r"""local Bag = {}
Bag.__index = Bag

function Bag.new(capacity)
  return setmetatable({items = {}, capacity = capacity or 10}, Bag)
end

function Bag:count(name)
  return self.items[name] or 0
end

function Bag:add(name, n)
  n = n or 1
  if n <= 0 then return false, '数量必须为正' end
  if self:count(name) + n > self.capacity then
    return false, '背包已满'
  end
  self.items[name] = self:count(name) + n
  return true
end

function Bag:remove(name, n)
  n = n or 1
  if self:count(name) < n then return false, '数量不足' end
  local left = self:count(name) - n
  self.items[name] = left > 0 and left or nil
  return true
end

function Bag:list()
  local names = {}
  for k in pairs(self.items) do names[#names + 1] = k end
  table.sort(names)
  return names
end

local bag = Bag.new(5)
print(bag:add('chip', 3), bag:add('cell', 1))
print(bag:count('chip'), table.concat(bag:list(), ','))
print(bag:remove('chip', 3), bag:count('chip'))""",
                "true\ttrue\n3\tcell,chip\ntrue\t0",
            ),
            table(
                ["模块", "职责", "关键方法"],
                [
                    ["Bag", "存物品与数量", "add / remove / count / list"],
                    ["StateMachine", "管状态与转移", "switch / can / current"],
                    ["组合", "用闭包隐藏内部状态", "只暴露必要方法"],
                ],
            ),
            p("状态机的转移表这样写：transitions = { explore = {battle = true, bag = true}, battle = {explore = true}, bag = {explore = true} }。can(state, target) 查 transitions[state][target] 是否为真，switch 先 can 再赋值。要加新状态，只改这张表，不用改任何逻辑代码，这就是「数据驱动」的好处：规则变了改数据，流程不变。"),
            *code(
                r"""local Bag = {}
Bag.__index = Bag
function Bag.new(cap) return setmetatable({items = {}, cap = cap or 3}, Bag) end
function Bag:count(n) return self.items[n] or 0 end
function Bag:add(n, c)
  c = c or 1
  if self:count(n) + c > self.cap then return false end
  self.items[n] = self:count(n) + c
  return true
end
function Bag:remove(n, c)
  c = c or 1
  if self:count(n) < c then return false end
  local left = self:count(n) - c
  self.items[n] = left > 0 and left or nil
  return true
end

local bag = Bag.new(5)
print(bag:add('chip', 3), bag:add('cell', 1))
print(bag:count('chip'), bag:remove('chip', 2), bag:count('chip'))
print(bag:add('core', 9))""",
                "true\ttrue\n3\ttrue\t1\nfalse",
            ),
            tip("真实项目里，状态机和背包都应该有单元测试。先测边界（加 0 个、删不存在的、容量刚好满），再测正常流程，最后测组合（在背包状态下尝试战斗转移应该被拒绝）。"),
            quiz(
                "把状态转移规则写成一张表，最主要的收益是？",
                ["运行更快", "新增状态只改数据不改逻辑", "自动生成界面", "减少内存"],
                1,
                "转移表让规则和流程分离，加状态、改允许的转移都只动数据，switch 逻辑保持不变，也不容易漏分支。",
            ),
        ],
        exercise(
            "实现背包的批量添加",
            "实现 add_batch(bag, items)：items 是 {name=..., count=...} 的数组，按顺序尝试加入 bag（bag 有 add(name, n) 方法，返回 true 或 false）。全部成功返回 true；任意一个失败就返回 false 和失败物品的名字，已经成功的保留。",
            "function add_batch(bag, items)\n  \nend\n\nlocal bag = {items = {}, cap = 10, add = function(self, n, c) local cur = self.items[n] or 0; if cur + c > self.cap then return false end; self.items[n] = cur + c; return true end}\nprint(add_batch(bag, {{name = 'a', count = 2}}))",
            "遍历 items，调用 bag:add(it.name, it.count)，失败时 return false, it.name。注意把 self 传进去：bag:add(...)。",
            [
                "local bag = {items = {}, cap = 10}; function bag:add(n, c) local cur = self.items[n] or 0; if cur + c > self.cap then return false end; self.items[n] = cur + c; return true end; assert(add_batch(bag, {{name='a', count=2}}) == true, '单个物品应成功')",
                "local bag = {items = {}, cap = 10}; function bag:add(n, c) local cur = self.items[n] or 0; if cur + c > self.cap then return false end; self.items[n] = cur + c; return true end; assert(add_batch(bag, {{name='a', count=20}}) == false, '超出容量应失败')",
                "local bag = {items = {}, cap = 10}; function bag:add(n, c) local cur = self.items[n] or 0; if cur + c > self.cap then return false end; self.items[n] = cur + c; return true end; local ok, name = add_batch(bag, {{name='a', count=1}, {name='b', count=99}}); assert(ok == false and name == 'b', '应返回失败物品名')",
                "local bag = {items = {}, cap = 10}; function bag:add(n, c) local cur = self.items[n] or 0; if cur + c > self.cap then return false end; self.items[n] = cur + c; return true end; add_batch(bag, {{name='a', count=1}, {name='b', count=99}}); assert(bag.items.a == 1, '已成功的物品应保留')",
            ],
            "function add_batch(bag, items)\n  for _, it in ipairs(items) do\n    if not bag:add(it.name, it.count) then\n      return false, it.name\n    end\n  end\n  return true\nend\n",
            160,
        ),
    ))

    return items


def build_advanced():
    items = []
    items.extend(_adv_21_25())
    items.extend(_adv_26_30())
    return items


ADVANCED_ITEMS = build_advanced()


NL = chr(10) + chr(10)

EXTRA_TEXT = {'lua01': '最后补充一个读报错的技巧。LuaJ 的语法错误会带文件名和行号，比如 [string "<lesson>"]:3: unexpected symbol near \')\'，先看行号定位，再看 near 后面的字符，基本就能判断是少写 end、引号没闭合，还是把中文标点写进了代码。运行期错误则会给出更具体的描述，比如 attempt to call a nil value，说明你在调用一个还不存在的函数，多半是函数名拼错或定义顺序不对。养成先读报错再改代码的顺序，比盲目删改快得多。', 'lua02': "类型判断还有一个实用组合：先用 type 确认大类，再用具体规则确认取值。比如一个参数既可能是数字也可能是数字字符串，先判 type(v) == 'number' 直接用，否则尝试 tonumber(v)，失败就返回 nil 并带上说明。这样调用方既能传 66 也能传 '66'，而不会被自动转换悄悄改掉语义。写库函数时，把「接受什么类型、返回什么类型、失败时返回什么」写在函数上方的注释里，比事后靠读实现去猜要可靠得多。", 'lua05': '条件语句还可以用来表达「查表式分支」。当分支超过四五个、每个分支只是返回不同的常量时，用一张映射表代替一长串 elseif，代码会短很多，加新分支也只改数据。写法是 local map = {A = 1, B = 2}，然后 local v = map[key]，取不到再走默认值。注意表的键只能是字符串或数字，而且查表不执行任何逻辑，所以只适合「输入到输出」的静态映射；需要计算或副作用时，仍然要写成函数。', 'lua06': '循环还可以和表配合做「累积构造」。比如遍历一个数组，把满足条件的元素放进新表，这就是最朴素的筛选；把每个元素变换后放进新表，就是映射。手写这两个模式时，用 result[#result + 1] = v 追加，比先算下标再赋值更不容易越界。等熟练之后，可以把它抽成通用函数，接收数组和判断函数，代码会进一步缩短。这个演进过程本身就是从「会写循环」到「会抽象」的分界线。', 'lua07': '函数返回多个值时，调用方如果只关心第一个，可以直接赋值给一个变量，其余自动丢弃；如果想把全部返回值收集起来，用 local t = {f()} 或 select 遍历。函数作为表的字段时，用点号调用不会传 self，用冒号才会。这两个调用方式经常被混用，尤其是在把函数从表里取出来赋给局部变量之后：local f = obj.method 之后再 f() 就不会带 self，这是 Lua 里非常经典的一个坑，遇到 self 为 nil 的报错先检查这里。', 'lua08': '数组的遍历还有一个性能细节：ipairs 每次迭代都要调用一次迭代器函数，而数值 for 直接按整数递增，后者通常更快。对性能敏感的循环，可以写 for i = 1, #t do local v = t[i] ... end，语义和 ipairs 一致，但少了一层调用。可读性上 ipairs 更清楚，所以普通业务代码优先用它，只有确实测出瓶颈时才换成数值 for。优化要看数据，不要凭感觉提前改写。', 'lua09': '字典还有一个常见用法是「反向索引」：用值查键。比如把 名字 → id 的表反过来建成 id → 名字，查询就能从遍历变成一次取值。构建反向表时要注意值可能重复，后写入的会覆盖先写入的，如果必须保留全部，就把值改成数组。反向索引的代价是内存翻倍和维护两份数据的一致性，所以只在读多写少、查询频繁的场景才值得，写操作频繁时反而会增加出错机会。', 'lua10': '作用域还影响错误处理。在 pcall 里定义的局部变量，出了 pcall 就不可见，想把结果带出来必须在外层先声明，再在内部赋值。这是新手常犯的错：local ok, v = pcall(function() local x = 1 return x end) 是可行的，但如果函数体里写的是 local x 而没有 return，外层拿到的就是 nil。记住「局部变量的生命周期跟着块走」，写闭包和回调时就不会把变量和值的可见范围搞混。', 'lua11': '多返回值还可以配合 table.unpack 做「参数转发」。一个函数收到多个值后，如果想原样传给另一个函数，直接写 g(f()) 只会在末尾展开一次；更稳妥的是 local a, b, c = f() 再 g(a, b, c)，或者用 table.pack 打包后 unpack。转发时要注意 nil 会截断数组，所以参数里可能有空洞时，用 select 逐个取比打包更可靠。这些细节在写装饰器、代理函数时特别重要。', 'lua12': '可变参数还有一个容易忽略的限制：不能在函数体里对 ... 做算术或比较，它不是一个值，只是参数列表的占位。要处理参数，必须先取出来赋给局部变量，或者用 select 逐个访问。另一个限制是 ... 不能出现在嵌套函数里直接引用外层函数的参数列表，必须先用 local args = {...} 或 select 打包，再在闭包里使用。理解这两条，能避免很多「为什么这里语法错误」的困惑。最后提醒一个命名问题：可变参数函数的参数名通常写成 ...，但内部处理时需要一个有名字的数组或计数变量。把计数叫 n、把数组叫 args，比叫 t 或 x 更清楚。函数文档里写清楚「参数可以是 0 到多个」「nil 会被跳过还是保留」，调用方就不用去读实现。Lua 没有类型标注，这类约定只能靠文字和测试表达，写的时候多花一分钟，后面能省很多沟通成本。', 'lua13': 'string 库还有几个不常用但很实用的函数：string.rep 生成重复串，string.byte 和 string.char 做字节与字符的互转，string.reverse 反转字符串。byte 和 char 在处理二进制协议、编码转换时是基础工具，比如把整数拆成字节再拼回去。它们都按字节操作，对 ASCII 完全够用，对多字节字符则要自己处理边界。先把 ASCII 场景练熟，遇到 UTF-8 再引入专门的库。', 'lua14': 'table 库的另一个常见需求是「深拷贝」。浅拷贝只复制第一层，嵌套的表仍然共享；深拷贝要递归处理每一层，并且用一张 seen 表记录已经复制过的表，防止循环引用导致无限递归。写深拷贝时先判断类型，不是表就直接返回，是表就查 seen，没有再创建新表并递归填充。这段代码不长，但它是理解「引用 vs 值」的最好练习，也是很多配置合并、状态快照功能的基础。', 'lua16': '迭代器还可以带「过滤」能力。写一个 filter_iter(t, pred)，返回的迭代器每次跳过不满足条件的元素，直到找到下一个符合条件的值。这类迭代器把筛选逻辑封装起来，调用方写 for v in filter_iter(t, is_even) do 就能只处理偶数，循环体里不需要再写 if。它的实现要点是内部用 while 循环推进，找到就 return，遍历完就 return nil 结束。组合多个这样的迭代器，就能搭出很像流式处理的管道。', 'lua17': '闭包和模块结合还能实现「单例」。把创建逻辑放在闭包里，用一个 local instance 缓存，第一次调用时创建，之后直接返回缓存的实例。这个模式适合配置对象、连接池这类「全局只应该有一份」的东西。要注意单例会让测试之间互相影响，测试里必须提供重置入口，否则前一个用例改过的状态会带到后一个。能用参数传递解决的依赖，尽量不要做成单例，显式依赖永远比隐式全局状态好维护。闭包还能用来做「轻量级的对象方法缓存」。如果一个方法需要反复创建内部函数，可以把内部函数在闭包里创建一次，返回多个引用它的方法，避免每次调用都新建函数对象。代价是这些方法共享同一份 upvalue，状态会互相影响，适合无状态的工具函数，不适合需要独立状态的场景。判断标准是：这些方法之间是否需要隔离数据，需要就各自建闭包，不需要就共享。', 'lua18': '递归还有一个常见陷阱是「重复计算参数」。比如递归函数每次调用都重新计算 #t 或重新查表，深度一大就明显变慢。把不变的值算一次作为参数传下去，或者放在闭包外层缓存，能显著减少开销。另一个陷阱是递归里修改共享表，导致不同分支互相干扰，排查时非常困难。写递归前先确认：哪些数据是只读的，哪些是每个分支独立的，把这两类分清楚，代码结构自然就清晰了。', 'lua19': 'pcall 之外，Lua 还提供 xpcall 和 assert 的组合用法。xpcall 的消息处理器可以返回任意值，最终作为第二个返回值给调用方，所以它适合做「错误转换」：把底层库的原始错误统一包装成带 code 的业务错误。assert 则适合做「前置条件」，在函数入口把非法参数挡掉。两者配合的常见模式是：入口用 assert 校验参数，可能失败的外部调用用 pcall 包住，最外层用 xpcall 统一格式。', 'lua20': '模块的加载顺序也会影响行为。如果模块 A 在加载时就去读模块 B 的字段，而 B 还没加载完，拿到的可能是 nil 或半成品表。稳妥的做法是「加载时只定义，使用时才读取」，把跨模块的访问推迟到函数调用时。这样即使加载顺序变化，也不会出现初始化时的空值错误。Lua 没有编译期的依赖检查，这条约定只能靠代码规范和测试来保证，但收益很大。', 'lua21': '元表的 __metatable 字段值得单独提一句。把它设成一个字符串或 true，getmetatable 就会返回这个值而不是元表本身，setmetatable 也会被拒绝。这是一种轻量的保护，防止调用方随意替换元表、破坏对象行为。它挡不住有意的攻击（rawget 仍能读到），但能防住误用。写库的时候，给核心对象加一层 __metatable 保护，是成本很低的好习惯。元表的调试有一个实用技巧：把元表本身也当成普通表打印出来，看看它到底有哪些字段，很多时候问题就是字段名拼错了（比如把 __index 写成 _index，或把 __tostring 写成 __tostring）。Lua 不会对元表字段做校验，拼错只会静默失效。另一个技巧是临时把 __index 换成一个打印函数，观察哪些键被访问、访问顺序如何，这对理解查找链和排查「为什么拿到了 nil」非常有效。', 'lua22': '继承还可以用「mixin」的方式实现组合：把一组方法表逐个复制进目标类，而不是拉一条继承链。复制时只复制函数字段，冲突时后复制的覆盖先复制的，顺序要写清楚。mixin 的好处是行为来源一目了然，不需要沿链查找；坏处是方法被复制了多份，修改原表不会影响已复制的地方。选择继承还是 mixin，取决于你更需要「是一个」还是「具备某种能力」。', 'lua23': '运算符重载的测试要覆盖三种情况：同类运算、混合类型运算、以及运算结果为 nil 或错误的情况。很多人只测第一种，上线后遇到「表加数字」才发现没处理。稳妥的写法是在每个元方法开头做类型判断，不是预期类型就返回 nil 或抛一个清晰的错误。另外，重载了 __eq 之后，表作为字典键的行为不变，因为键比较用的是引用和哈希，不会被 __eq 影响，这一点容易误解。', 'lua24': '__call 和 __index 组合还能实现「命令对象」：把参数和操作打包成一张表，调用时执行。比如一个查询构造器，链式调用 where、order 收集条件，最后调用对象本身触发执行。这种 API 读起来接近自然语言，也方便做延迟执行和日志记录。要注意每次链式调用都返回新对象还是同一个对象，前者更安全但分配多，后者更省但要小心共享状态。', 'lua25': '协程的调试信息比普通函数少，出错时不容易看出是哪个 yield 之后出的问题。实用的办法是在协程函数里给每个阶段加日志，或者把 yield 的返回值打印出来对照。另一个技巧是用 coroutine.status 在 resume 前后各查一次，确认状态变化符合预期（suspended → running → suspended/dead）。协程的 bug 往往是「以为它在等，其实已经结束」，状态检查能立刻发现这类问题。协程的数量也要控制。每个协程对象都占内存，创建几万个只跑一次就丢弃，会让 GC 压力明显上升。能用一个普通函数加状态表解决的，就不要上协程；协程适合「流程确实需要暂停和恢复」的场景，不适合当作廉价的回调包装。判断标准是：这段逻辑有没有「中途让出、之后继续」的语义，有就用协程，没有就别引入额外复杂度。', 'lua26': '模式匹配还可以用来做简单的词法分析：用 gmatch 按 token 模式逐个取出标识符、数字、运算符，再按顺序组装成 token 列表。这比手写逐字符扫描简单得多，性能也够用。限制是 Lua 模式没有回溯和分组替换的高级能力，遇到嵌套结构（比如表达式括号）就要配合栈或递归。先用模式做「切分」，再用递归下降做「解析」，是写小型解析器的常见组合。', 'lua27': '自定义格式的兼容性也要考虑。字段增删时，旧版本的配置文件可能缺少新字段，也可能带着已经废弃的字段。读取时对缺失字段补默认值，对未知字段选择忽略而不是报错，这样升级不会让老用户的配置直接失效。反过来，写回文件时应该保留未知字段，避免「读进来再写出去」把用户手写的注释和扩展配置弄丢。这些细节决定了配置系统是「能用」还是「好用」。最后说一个安全边界：配置文件里不要放可执行代码，也不要用 load 去解析。哪怕只是「让用户写一点表达式」，也意味着任意代码执行，沙箱就形同虚设。纯数据的 key=value 或 JSON 虽然表达力弱，但边界清晰，解析失败时能给出准确的行号和原因。宁可让用户多写几个字段，也不要把执行权限交出去，这是配置系统设计里最不能妥协的一条。', 'lua28': '函数式风格和 Lua 的惯用法并不冲突。Lua 的 table 库本身就是「数据 + 函数」的组合，map/filter 只是把循环的控制权交给调用方。写库时提供一个「迭代器版」和一个「数组版」两套接口，能让调用方按场景选择：数据量大时用迭代器省内存，需要多次访问时用数组更方便。两套接口共享同一份核心逻辑，只是外层包装不同，维护成本并不高。', 'lua29': '算法题在 Lua 里写，要特别注意下标从 1 开始带来的偏移。很多在别的语言里用 0 基写的模板，直接搬过来会全部错位一格，尤其是二分查找和滑动窗口。稳妥的做法是先用小数据手算一遍下标，再写代码；写完用小数组验证首尾元素。另一个细节是 # 对带空洞的数组不可靠，算法里如果需要频繁删除元素，先用标记法记录删除，最后统一压缩，比边遍历边 remove 安全。', 'lua30': '这个项目还可以继续扩展成「多背包 + 装备槽」：背包负责数量，装备槽负责当前穿戴，两者通过物品 id 关联。扩展时先想清楚数据模型，再写操作函数，最后补测试。每加一个功能，都先问三个问题：这个操作会不会破坏已有不变量？失败时应该返回什么？并发（协程切换）时状态会不会被改到一半？把这三问答清楚，代码结构基本就不会乱，这也是三十讲最想传递的工程习惯。'}


def enrich(lessons):
    """把「延伸阅读」并入最后一段正文，保证每讲仍是 2-3 段 text。

    课程渲染按 text 块分段，块太多会把讲解切碎；内容上又不希望篇幅被
    压缩，所以这里选择「合段」而不是「加段」：同一块内用空行分自然段，
    阅读节奏不变，块数不增。
    """
    for item in lessons:
        extra = EXTRA_TEXT.get(item["id"])
        if not extra:
            continue
        blocks = item["blocks"]
        for i in range(len(blocks) - 1, -1, -1):
            if blocks[i].get("type") == "text":
                blocks[i]["text"] = blocks[i]["text"] + NL + extra
                break
    return lessons


def main():
    packs = [
        ("lua-basics", enrich(build_basics())),
        ("lua-core", enrich(CORE_ITEMS)),
        ("lua-advanced", enrich(ADVANCED_ITEMS)),
    ]
    for name, lessons in packs:
        path = PACKS / f"{name}.json"
        path.write_text(
            json.dumps(lessons, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"{name}: {len(lessons)} lessons -> {path}")


if __name__ == "__main__":
    main()
