import json
import pathlib


def lesson(id_, order, chapter, chapter_name, title, subtitle, xp, blocks, exercise):
    return {
        "id": id_,
        "order": order,
        "chapter": chapter,
        "chapterName": chapter_name,
        "lang": "typescript",
        "title": title,
        "subtitle": subtitle,
        "xp": xp,
        "blocks": blocks,
        "exercise": exercise,
    }


C = "语言包 · TypeScript 启程"

ts = [
    lesson("ts01", 600, 33, C, "第一次握手", "类型标注 + console.log", 60, [
        {"type": "heading", "text": "TypeScript 是什么"},
        {"type": "text", "text": "TypeScript 是 JavaScript 加上「类型标注」。浏览器和运行时其实看不懂类型——类型只在你写代码时帮你抓错，跑起来之前会被擦掉。所以同一段代码，加了类型和去掉类型，运行结果完全一样。"},
        {"type": "diagram", "text": "你写的 TS              运行时看到的 JS\n──────────────        ─────────────────\nvar n: number = 5  →  var n = 5\nfunction f(a: string) → function f(a)"},
        {"type": "text", "text": "先看对比：下面这段代码带类型标注，运行输出和不带类型完全一致。"},
        {"type": "code", "code": "var name: string = 'V';\nvar level: number = 66;\nconsole.log(name, level);\nconsole.log('HELLO, ' + name);", "runnable": True},
        {"type": "output", "text": "V 66\nHELLO, V"},
        {"type": "tip", "text": "`var name: string` 里的 `: string` 是给编辑器和编译器看的。运行时拿到的只有 `var name`。"},
        {"type": "quiz", "question": "运行 `var n: number = 5` 时，真正执行的代码是？", "options": ["var n: number = 5", "var n = 5", "n = 5", "报错，缺少类型"], "answer": 1, "explain": "类型标注在编译阶段被擦除，运行时只看到 `var n = 5`。这就是本课程的转译器做的事。"},
        {"type": "task", "text": "把 `level` 改成你自己的等级数字，运行看看输出。"},
    ], {
        "title": "带类型的入网代号",
        "brief": "声明一个带类型标注的常量，拼出问候语。",
        "starterCode": "var codename: string = 'V';\n// 用 codename 拼出 'HELLO, V'\nvar greeting: string = '';\nconsole.log(greeting);",
        "hint": "字符串拼接用 +，例如 'HELLO, ' + codename。",
        "tests": ["assert(greeting === 'HELLO, V', 'greeting 应为 HELLO, V')", "assert(typeof codename === 'string', 'codename 应为字符串')"],
        "stdin": [],
        "xp": 80,
        "solution": "var codename: string = 'V';\nvar greeting: string = 'HELLO, ' + codename;\n",
    }),

    lesson("ts02", 601, 33, C, "类型即文档", "interface 与类型别名", 70, [
        {"type": "heading", "text": "用 interface 描述形状"},
        {"type": "text", "text": "JS 里对象长什么样全靠猜。interface 就是给对象画一张「形状说明」：有哪些字段、各是什么类型。它同样只存在于编写阶段——转译时整段被删掉。"},
        {"type": "code", "code": "interface Hero {\n  name: string;\n  level: number;\n}\n\nvar v: Hero = { name: 'V', level: 66 };\nconsole.log(v.name, v.level);", "runnable": True},
        {"type": "output", "text": "V 66"},
        {"type": "diagram", "text": "interface Hero  ──擦除──►  （消失）\nvar v: Hero = {...} ──────►  var v = {...}"},
        {"type": "table", "headers": ["写法", "运行时还在吗", "作用"], "rows": [["interface Hero { }", "否", "描述对象形状"], ["type Id = string", "否", "给类型起别名"], ["var v: Hero = {}", "只留 var v = {}", "标注变量类型"]]},
        {"type": "warn", "text": "注意：interface 写错字段名，运行时不会报错（它已被删掉），但编辑器会立刻标红。类型是「写代码时的安全带」，不是运行时检查。"},
        {"type": "quiz", "question": "`interface` 在运行时还存在吗？", "options": ["存在，是一个对象", "不存在，编译时被删除", "存在，但被冻结", "取决于浏览器"], "answer": 1, "explain": "interface 只用于类型检查，编译（转译）阶段整段删除，不产生任何运行时代码。"},
    ], {
        "title": "英雄档案",
        "brief": "用 interface 描述英雄，返回它的简介字符串。",
        "starterCode": "interface Hero {\n  name: string;\n  level: number;\n}\n\nfunction intro(h: Hero): string {\n  // 返回 'V(66)'\n  return '';\n}",
        "hint": "用 h.name + '(' + h.level + ')' 拼接。",
        "tests": ["assert(intro({name:'V', level:66}) === 'V(66)', 'intro 应返回 V(66)')", "assert(intro({name:'Judy', level:30}) === 'Judy(30)', '应支持不同英雄')"],
        "stdin": [],
        "xp": 80,
        "solution": "interface Hero {\n  name: string;\n  level: number;\n}\n\nfunction intro(h: Hero): string {\n  return h.name + '(' + h.level + ')';\n}\n",
    }),

    lesson("ts03", 602, 33, C, "函数的类型签名", "参数与返回值标注", 70, [
        {"type": "heading", "text": "参数和返回值都能标"},
        {"type": "text", "text": "函数最容易出错的地方是「传错类型」。给参数和返回值加标注，编辑器就能在你调用时就发现 `add('a', 1)` 这种错误——不用等运行时。"},
        {"type": "code", "code": "function add(a: number, b: number): number {\n  return a + b;\n}\n\nvar arrow = (x: number, y: number): number => x * y;\n\nconsole.log(add(2, 3));\nconsole.log(arrow(4, 5));", "runnable": True},
        {"type": "output", "text": "5\n20"},
        {"type": "practice", "title": "带返回类型的箭头函数", "code": "var double = (n: number): number => n * 2;\nconsole.log(double(21));", "output": "42", "hint": "箭头函数也可以标返回类型，写在参数括号后面。"},
        {"type": "tip", "text": "返回类型标成 `: number` 后，如果你写 `return 'abc'`，编辑器立刻报错。这是 TS 最大的价值：把错误提前到写代码那一刻。"},
        {"type": "quiz", "question": "`function f(a: number): string` 里，`: string` 标注的是什么？", "options": ["参数 a 的类型", "函数返回值的类型", "变量 f 的类型", "都不是"], "answer": 1, "explain": "参数括号后面的 `: string` 标注的是返回值类型。"},
    ], {
        "title": "伤害计算器",
        "brief": "实现 damage(base, mult)：返回 base 乘 mult 的结果。",
        "starterCode": "function damage(base: number, mult: number): number {\n  // 返回 base * mult\n  return 0;\n}",
        "hint": "直接 return base * mult。",
        "tests": ["assert(damage(10, 3) === 30, 'damage(10,3) 应为 30')", "assert(damage(0, 5) === 0, '0 乘任何数都是 0')", "assert(damage(7, 1) === 7, '乘 1 不变')"],
        "stdin": [],
        "xp": 90,
        "solution": "function damage(base: number, mult: number): number {\n  return base * mult;\n}\n",
    }),

    lesson("ts04", 603, 33, C, "联合类型与类型收窄", "string | number 与 typeof", 80, [
        {"type": "heading", "text": "一个参数，两种可能"},
        {"type": "text", "text": "有时一个值既可能是字符串也可能是数字。用 `|` 表示「或」，这叫联合类型。用到它之前，先用 `typeof` 判断当前到底是哪一种——这个动作叫「类型收窄」。"},
        {"type": "code", "code": "function describe(v: string | number): string {\n  if (typeof v === 'number') {\n    return 'number:' + v;\n  }\n  return 'string:' + v;\n}\n\nconsole.log(describe(42));\nconsole.log(describe('hi'));", "runnable": True},
        {"type": "output", "text": "number:42\nstring:hi"},
        {"type": "diagram", "text": "v: string | number\n      │\n      ├─ typeof v === 'number' → 这里 v 被收窄成 number\n      └─ 否则                  → 这里 v 被收窄成 string"},
        {"type": "warn", "text": "联合类型不擦除会怎样？`string | number` 里的 `|` 在 JS 里是「按位或」。所以转译器必须整段擦除类型，保留 `function describe(v)`。"},
        {"type": "quiz", "question": "`typeof 42` 返回什么？", "options": ["'int'", "'number'", "'Number'", "42"], "answer": 1, "explain": "JS 只有一种数字类型，typeof 返回小写的 'number'。"},
    ], {
        "title": "类型报告员",
        "brief": "实现 label(v)：数字返回 'num:x'，字符串返回 'str:x'。",
        "starterCode": "function label(v: string | number): string {\n  // 用 typeof 判断\n  return '';\n}",
        "hint": "typeof v === 'number' 时返回 'num:' + v，否则 'str:' + v。",
        "tests": ["assert(label(5) === 'num:5', 'label(5) 应为 num:5')", "assert(label('a') === 'str:a', 'label(\"a\") 应为 str:a')", "assert(label(0) === 'num:0', '0 也是数字')"],
        "stdin": [],
        "xp": 100,
        "solution": "function label(v: string | number): string {\n  if (typeof v === 'number') {\n    return 'num:' + v;\n  }\n  return 'str:' + v;\n}\n",
    }),

    lesson("ts05", 604, 33, C, "数组与泛型", "T[] 与泛型函数", 80, [
        {"type": "heading", "text": "数组也有类型"},
        {"type": "text", "text": "`number[]` 表示「全是数字的数组」。而 `<T>` 是泛型：一个函数可以处理任意类型，但调用时类型就定下来了。转译时泛型参数表整段被删掉。"},
        {"type": "code", "code": "function first<T>(arr: T[]): T {\n  return arr[0];\n}\n\nvar nums: number[] = [10, 20, 30];\nvar names: string[] = ['V', 'Judy'];\n\nconsole.log(first(nums));\nconsole.log(first(names));", "runnable": True},
        {"type": "output", "text": "10\nV"},
        {"type": "diagram", "text": "function first<T>(arr: T[])  ──擦除──►  function first(arr)\n\n调用 first([1,2])   → T 推断为 number\n调用 first(['a'])   → T 推断为 string"},
        {"type": "tip", "text": "泛型的价值：一个实现，两种类型都安全。如果写成 `any`，就失去了类型检查；用 `<T>` 则调用时自动推断。"},
        {"type": "quiz", "question": "`function first<T>(arr: T[])` 转译后是？", "options": ["function first<T>(arr)", "function first(arr)", "function first(arr: T[])", "报错"], "answer": 1, "explain": "泛型参数表 `<T>` 和类型标注 `: T[]` 都会被擦除，只剩 `function first(arr)`。"},
    ], {
        "title": "取首元素",
        "brief": "实现 head(arr)：返回数组第一个元素，空数组返回 null。",
        "starterCode": "function head<T>(arr: T[]): T {\n  // 空数组返回 null\n  return null;\n}",
        "hint": "先判断 arr.length === 0，是则 return null，否则 return arr[0]。",
        "tests": ["assert(head([1,2,3]) === 1, 'head([1,2,3]) 应为 1')", "assert(head(['a']) === 'a', '字符串数组应返回 a')", "assert(head([]) === null, '空数组应返回 null')"],
        "stdin": [],
        "xp": 100,
        "solution": "function head<T>(arr: T[]): T {\n  if (arr.length === 0) {\n    return null;\n  }\n  return arr[0];\n}\n",
    }),

    lesson("ts06", 605, 33, C, "枚举与常量", "enum 转成冻结对象", 90, [
        {"type": "heading", "text": "给数字起名字"},
        {"type": "text", "text": "`enum` 让你用有意义的名字代替魔法数字。它是少数**会留下运行时产物**的 TS 特性——转译后变成一个冻结的对象。"},
        {"type": "code", "code": "enum Level {\n  Low,\n  Mid = 10,\n  High\n}\n\nconsole.log(Level.Low);\nconsole.log(Level.Mid);\nconsole.log(Level.High);", "runnable": True},
        {"type": "output", "text": "0\n10\n11"},
        {"type": "diagram", "text": "enum Level { Low, Mid = 10, High }\n        │ 转译\n        ▼\nvar Level = Object.freeze({ Low: 0, Mid: 10, High: 11 })"},
        {"type": "table", "headers": ["成员", "值", "说明"], "rows": [["Low", "0", "从 0 开始自动编号"], ["Mid", "10", "手动指定"], ["High", "11", "接着上一个 +1"]]},
        {"type": "warn", "text": "enum 是 TS 里唯一「擦除后还留下东西」的常见特性。interface、type、类型标注全都会消失，但 enum 会变成真实对象。"},
        {"type": "quiz", "question": "`enum E { A, B = 5, C }` 中 C 的值是？", "options": ["2", "5", "6", "undefined"], "answer": 2, "explain": "C 接着 B 的 5 自动 +1，所以是 6。"},
    ], {
        "title": "段位判定",
        "brief": "用 enum 定义三个段位，实现 rankName(level) 返回段位名。",
        "starterCode": "enum Rank {\n  Rookie,\n  Hacker,\n  Legend\n}\n\nfunction rankName(level: Rank): string {\n  // Rookie→'rookie'，Hacker→'hacker'，Legend→'legend'\n  return '';\n}",
        "hint": "用 if 依次比较 level === Rank.Rookie 等，或直接 switch。",
        "tests": ["assert(rankName(Rank.Rookie) === 'rookie', 'Rookie 应为 rookie')", "assert(rankName(Rank.Hacker) === 'hacker', 'Hacker 应为 hacker')", "assert(rankName(Rank.Legend) === 'legend', 'Legend 应为 legend')", "assert(Rank.Hacker === 1, 'Hacker 的值应为 1')"],
        "stdin": [],
        "xp": 110,
        "solution": "enum Rank {\n  Rookie,\n  Hacker,\n  Legend\n}\n\nfunction rankName(level: Rank): string {\n  if (level === Rank.Rookie) { return 'rookie'; }\n  if (level === Rank.Hacker) { return 'hacker'; }\n  return 'legend';\n}\n",
    }),
]

pathlib.Path("content_packs/ts-basics.json").write_text(
    json.dumps(ts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
)
print("ts", len(ts), "lessons,", sum(len(x["exercise"]["tests"]) for x in ts), "cases")
