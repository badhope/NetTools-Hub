#!/usr/bin/env python3
"""生成 JavaScript 三阶段课程包（30 讲）。

运行：python tools/gen_js_curriculum.py
产物：content_packs/js-basics.json / js-core.json / js-advanced.json

课程面向 PyNeon 内置的 Mozilla Rhino 1.7.15（解释模式，ES6 子集）。
生成器内置结构自检：id/order/chapter、块数量、代码块与输出块配对、
quiz 答案范围、练习字段与用例数量、正文汉字量。任一不满足直接抛错。
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "content_packs"


# ---------------------------------------------------------------------------
# 块构造器
# ---------------------------------------------------------------------------

def heading(text):
    return {"type": "heading", "text": text}


def paragraph(text):
    return {"type": "text", "text": text}


def code(src, runnable=True):
    return {"type": "code", "code": src.strip("\n"), "runnable": runnable}


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
    return {
        "type": "quiz",
        "question": question,
        "options": options,
        "answer": answer,
        "explain": explain,
    }


def practice(title, src, expected, hint):
    return {
        "type": "practice",
        "title": title,
        "code": src.strip("\n"),
        "output": expected.strip("\n"),
        "hint": hint,
    }


def steps(items):
    return {"type": "steps", "items": items}


def fill(goal, src, answer, explain):
    return {
        "type": "fill",
        "goal": goal,
        "code": src.strip("\n"),
        "answer": answer,
        "explain": explain,
    }


def order(title, lines):
    return {"type": "order", "title": title, "lines": lines}


def task(text):
    return {"type": "task", "text": text}


def visualize(title, caption, frames):
    return {
        "type": "visualize",
        "title": title,
        "caption": caption,
        "frames": frames,
    }


def pair(src, expected):
    """一个可运行代码块 + 紧随其后的真实输出块。"""
    return [code(src), output(expected)]


def exercise(title, brief, starter, hint, tests, solution, xp=100):
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


def lesson(id_, order, chapter, chapter_name, title, subtitle, xp, blocks, ex):
    return {
        "id": id_,
        "order": order,
        "chapter": chapter,
        "chapterName": chapter_name,
        "lang": "javascript",
        "title": title,
        "subtitle": subtitle,
        "xp": xp,
        "blocks": blocks,
        "exercise": ex,
    }


# ---------------------------------------------------------------------------
# 基础篇 js01 - js10
# ---------------------------------------------------------------------------

BASIC_CHAPTER = "JavaScript · 基础篇"


def js01():
    return lesson(
        "js01", 300, 21, BASIC_CHAPTER,
        "第一次握手", "console.log 与程序结构", 60,
        [
            heading("让程序开口：从第一行到最后一行"),
            paragraph(
                "JavaScript 程序没有神秘的入口函数。一个脚本文件就是一批语句，运行时从上到下依次执行：先声明变量，再计算，再输出。浏览器在页面加载时执行脚本，Node 执行整个文件，本课程的 Rhino 运行时也遵守同一规则。只要能在脑子里按行「走一遍」，你就能预测程序的行为，这是后面所有调试能力的地基。"
            ),
            paragraph(
                "console.log() 是最常用的输出与观察工具。它接受任意多个参数，把每个参数转成字符串后用空格连接，再补一个换行。因此 console.log('level', 66) 输出的是 level 66，而不是两个独立的值。字符串可以用单引号或双引号包裹，两种写法完全等价；语句末尾的分号在 JS 里可以省略，但本课程统一保留，避免自动分号插入带来的歧义。"
            ),
            *pair(
                """var agent = 'V';
var level = 66;

console.log('boot:', agent);
console.log('level:', level);
console.log('ready', true);""",
                """boot: V
level: 66
ready true""",
            ),
            table(
                ["程序要素", "写法", "作用"],
                [
                    ["变量声明", "var name = 'V';", "给值起一个可复用的名字"],
                    ["输出", "console.log(a, b);", "把值打印到控制台，便于观察"],
                    ["单行注释", "// 说明", "给人看，运行时跳过"],
                    ["多行注释", "/* 说明 */", "临时屏蔽一段代码"],
                ],
            ),
            paragraph(
                "初学阶段最常见的三个坑：第一，把 console.log 当成 return，函数里打印了值却没有返回，调用处拿到 undefined；第二，字符串引号不配对，解析器直接报语法错误；第三，使用了中文引号或中文分号，它们看起来很像，但对 JS 来说是非法的。遇到报错先看行号，再检查这一行的引号、括号和逗号是否成对。"
            ),
            tip(
                "调试时给输出加标签：console.log('level =', level) 比只打印一个 66 有用得多。输出里的标签就是你的路标。"
            ),
            quiz(
                "console.log('1' + 2) 会输出什么？",
                ["3", "12", "报错", "NaN"],
                1,
                "加号遇到字符串会执行拼接：数字 2 被转成字符串 '2'，结果是 '12'。想得到 3 应写 Number('1') + 2。",
            ),
            steps(
                [
                    "声明变量并赋初值",
                    "用运算符算出结果",
                    "用 console.log 输出，并给输出加标签",
                    "改动一处后重新运行，对照输出定位变化",
                ]
            ),
            *pair(
                """var a = 7;
var b = 3;

console.log('sum =', a + b);
console.log('mod =', a % b);
console.log('done');""",
                """sum = 10
mod = 1
done""",
            ),
            task("把 agent 改成自己的代号，再增加一行输出，预测它会出现在第几行。"),
        ],
        exercise(
            "生成入网代号",
            "实现 greet(name)：返回字符串 'HELLO, ' 拼上 name。greet('v') 应返回 'HELLO, v'。",
            """function greet(name) {
  // 在这里返回拼接后的字符串

}

console.log(greet('v'));""",
            "return 'HELLO, ' + name; 注意 HELLO 后面的逗号和空格都在字符串内部。",
            [
                "assert(greet('v') === 'HELLO, v', 'greet(\"v\") 应为 HELLO, v')",
                "assert(greet('judy') === 'HELLO, judy', 'greet(\"judy\") 应为 HELLO, judy')",
                "assert(greet('') === 'HELLO, ', '空名字也要能拼接')",
            ],
            """function greet(name) {
  return 'HELLO, ' + name;
}

console.log(greet('v'));
console.log(greet('judy'));""",
        ),
    )


def js02():
    return lesson(
        "js02", 301, 21, BASIC_CHAPTER,
        "变量的三种身份", "var / let / const 与类型系统", 70,
        [
            heading("声明、赋值与类型"),
            paragraph(
                "JS 是动态类型语言：变量本身没有类型，值才有类型。同一个变量可以先存数字再存字符串，语言不会阻止你，但这类随意改型会让代码难以推理。声明变量有三种关键字：var 是历史写法，函数级作用域；let 和 const 是 ES6 写法，块级作用域。const 约束的是「绑定不能重新指向」，不是「对象不能修改」，这一点最容易误会。"
            ),
            paragraph(
                "七个基本类型值得先记住：number、string、boolean、undefined、null、symbol、bigint（后两种本课程不展开），其余都是 object，包括数组和函数。typeof 可以探测类型，但有两个历史遗留：typeof null 返回 'object'，typeof function 返回 'function'。判断 null 要用 value === null，判断数组要用 Array.isArray(value)。"
            ),
            *pair(
                """var legacy = 'var 是函数作用域';
let modern = 'let 是块级作用域';
const fixed = 42;

console.log(typeof legacy, typeof modern, typeof fixed);
console.log(typeof null, typeof [], typeof function () {});

{
  let modern = '内层块';
  console.log(modern);
}
console.log(modern);""",
                """string string number
object object function
内层块
let 是块级作用域""",
            ),
            table(
                ["声明", "作用域", "能否重新赋值", "典型用途"],
                [
                    ["var", "函数级", "可以", "维护旧代码时偶尔遇到"],
                    ["let", "块级", "可以", "会变化的计数器、循环变量"],
                    ["const", "块级", "不可以", "配置、引用、不会换指向的值"],
                ],
            ),
            paragraph(
                "优先使用 const，需要改变绑定时才用 let，基本不用 var。原因是块级作用域把变量的可见范围压缩在花括号内，减少互相污染。另一个常见坑是 const 对象：const user = { name: 'V' } 之后 user.name = 'J' 完全合法，因为对象内部属性没有被冻结；只有 user = {} 这种重新赋值才会报错。"
            ),
            warn(
                "不要用 typeof 判断数组或 null。数组用 Array.isArray(x)，null 用 x === null。"
            ),
            quiz(
                "const user = { name: 'V' }; user.name = 'J'; 的结果是？",
                ["报错，const 不能改", "合法，name 变成 'J'", "合法，但 name 仍是 'V'", "返回 undefined"],
                1,
                "const 锁定的是变量绑定，不是对象内容。要真正禁止修改需要 Object.freeze，而且它只是浅冻结。",
            ),
            fill(
                "补全判断：确认 value 是数组",
                "if (____(value)) {\n  console.log('array');\n}",
                "Array.isArray",
                "Array.isArray 专门用于数组判断，能避开 typeof [] 返回 'object' 的坑。",
            ),
            *pair(
                """let count = 0;
count = count + 1;
console.log('count =', count);

const config = { mode: 'offline' };
config.mode = 'online';
console.log(config.mode);""",
                """count = 1
online""",
            ),
        ],
        exercise(
            "类型报告员",
            "实现 describe(v)：number/string/boolean/undefined/function 返回 typeof 的结果；null 返回 'null'；数组返回 'array'。",
            """function describe(v) {
  // 先处理 null 和数组，再返回 typeof

}

console.log(describe(42));
console.log(describe([]));""",
            "先写 if (v === null) return 'null'; 再写 if (Array.isArray(v)) return 'array'; 最后 return typeof v;",
            [
                "assert(describe(42) === 'number', '42 应为 number')",
                "assert(describe('a') === 'string', '字符串应为 string')",
                "assert(describe(null) === 'null', 'null 不能直接靠 typeof')",
                "assert(describe([]) === 'array', '数组要单独判断')",
            ],
            """function describe(v) {
  if (v === null) return 'null';
  if (Array.isArray(v)) return 'array';
  return typeof v;
}

console.log(describe(42));
console.log(describe([]));""",
        ),
    )


def js03():
    return lesson(
        "js03", 302, 21, BASIC_CHAPTER,
        "运算符与类型转换", "加号的双重人格与严格相等", 70,
        [
            heading("先看类型，再谈运算"),
            paragraph(
                "JS 的运算符会悄悄做类型转换，最典型的是加号：只要有一边是字符串，另一边就会被转成字符串再拼接；而减号、乘号、除号只会做数学运算，遇到非数字会得到 NaN。很多「玄学 bug」都来自这里。写代码时先问自己：这一行我希望做数学还是做拼接？不确定就显式转换，别把判断权交给引擎。"
            ),
            paragraph(
                "相等比较有两套：== 先做类型转换再比较，=== 要求类型和值都相同。'1' == 1 是 true，'1' === 1 是 false；null == undefined 是 true，但两者都不等于 0。现代 JS 的共识是只用 === 和 !==，把隐式转换从比较逻辑里彻底赶出去。同理，NaN 不等于任何值，包括它自己，判断要用 Number.isNaN 或 isNaN。"
            ),
            *pair(
                """console.log('1' + 1);
console.log('1' - 1);
console.log('1' === 1);
console.log(null == undefined);
console.log(Number(' 42 '), Number('abc'));
console.log(Boolean(''), Boolean('0'), Boolean(0));""",
                """11
0
false
true
42 NaN
false true false""",
            ),
            table(
                ["表达式", "结果", "原因"],
                [
                    ["'5' + 2", "'52'", "加号遇到字符串转为拼接"],
                    ["'5' - 2", "3", "减号强制转数字"],
                    ["Number('3.5')", "3.5", "字符串转数字"],
                    ["Number('')", "0", "空串被当作 0，容易踩坑"],
                    ["Boolean('0')", "true", "非空字符串都是真值"],
                ],
            ),
            paragraph(
                "假值（falsy）只有固定的一小组：false、0、-0、0n、''、null、undefined、NaN。除此之外的对象、数组、非空字符串、函数都是真值，空数组 [] 和空对象 {} 也是真值——这是从 Python 转过来的人最容易误判的地方。需要判断「数组有没有元素」就写 arr.length > 0，而不是 if (arr)。"
            ),
            warn(
                "Number('') 得到 0，parseInt('12px') 得到 12，parseFloat('3.5.1') 得到 3.5。转换函数各有脾气，输入来自用户时必须配合校验。"
            ),
            quiz(
                "下面哪个表达式的结果是 true？",
                ["[] == false", "'' === 0", "Boolean([]) === true", "NaN === NaN"],
                2,
                "空数组是真值，Boolean([]) 为 true。[] == false 会走隐式转换得到 true，但这是 == 的陷阱，不应模仿。",
            ),
            practice(
                "显式转换",
                """var raw = ' 12 ';
var n = Number(raw);

console.log(n + 1);
console.log(typeof n);""",
                """13
number""",
                "Number 会忽略首尾空白；加法两边都是数字时才做加法。",
            ),
            *pair(
                """var score = 0;
var name = '';

console.log(score || 'empty');
console.log(name || 'anonymous');
console.log(score === 0 ? 'zero' : 'nonzero');""",
                """empty
anonymous
zero""",
            ),
        ],
        exercise(
            "安全数字转换",
            "实现 toNumber(value)：数字原样返回；字符串去掉首尾空白后若为空或无法解析，返回 null，否则返回数字；true 返回 1，false 返回 0；其他类型返回 null。",
            """function toNumber(value) {
  // 处理数字、布尔、字符串三类输入

}

console.log(toNumber('42'));""",
            "先用 typeof 分流；字符串先 trim()，空串直接返回 null，再用 isNaN(Number(s)) 判断。",
            [
                "assert(toNumber(7) === 7, '数字应原样返回')",
                "assert(toNumber(' 3.5 ') === 3.5, '数字字符串应转成数字')",
                "assert(toNumber('') === null, '空字符串应返回 null')",
                "assert(toNumber('abc') === null, '非法字符串应返回 null')",
                "assert(toNumber(true) === 1 && toNumber(false) === 0, '布尔值应转成 1/0')",
            ],
            """function toNumber(value) {
  if (typeof value === 'number') return value;
  if (typeof value === 'boolean') return value ? 1 : 0;
  if (typeof value === 'string') {
    var s = value.trim();
    if (s === '') return null;
    var n = Number(s);
    if (isNaN(n)) return null;
    return n;
  }
  return null;
}

console.log(toNumber('42'));
console.log(toNumber('abc'));""",
        ),
    )


def js04():
    return lesson(
        "js04", 303, 21, BASIC_CHAPTER,
        "字符串与模板字符串", "不可变序列与反引号", 80,
        [
            heading("字符串是一把只读的刀"),
            paragraph(
                "JS 字符串是按 UTF-16 码元排列的不可变序列：所有看起来像修改的方法，都会返回一个新字符串，原值保持不变。s.toUpperCase() 不会改变 s，s.slice(0, 3) 也不会。理解不可变性后，链式调用就很自然：每一步拿上一步的返回值继续处理，原始数据始终干净。这和后面要讲的纯函数、不可变数据是同一条思想线索。"
            ),
            paragraph(
                "常用方法可以按目的分组：截取用 slice(start, end) 或 substring；查找用 indexOf、includes、startsWith、endsWith；切分与合并用 split 和 join；清理用 trim；替换用 replace。slice 支持负索引，s.slice(-3) 取最后三个字符；split('') 可以把字符串拆成字符数组，再用 join('') 拼回。"
            ),
            *pair(
                """var base = 'cyberpunk';

console.log(base.slice(0, 5));
console.log(base.slice(-4));
console.log(base.toUpperCase());
console.log(base.length);
console.log(base.includes('punk'));""",
                """cyber
punk
CYBERPUNK
9
true""",
            ),
            table(
                ["目的", "写法", "结果示例"],
                [
                    ["截取", "s.slice(0, 3)", "'cyber' -> 'cyb'"],
                    ["负索引截取", "s.slice(-4)", "'punk'"],
                    ["分割", "s.split(';')", "字符串转数组"],
                    ["连接", "arr.join(' | ')", "数组转字符串"],
                    ["去空白", "s.trim()", "去掉首尾空格"],
                ],
            ),
            paragraph(
                "模板字符串用反引号包裹，可以用 ${表达式} 直接嵌入变量或运算结果，还支持换行，不必再用加号拼接。它解决的是「长字符串 + 多个变量」的可读性问题，不会改变类型。注意反引号不是单引号，键盘位置不同；在模板里写 ${} 时，花括号内必须是合法表达式，不能写语句。"
            ),
            tip(
                "链式调用时按「从内到外」读：title.trim().toLowerCase().split(' ').join('-') 依次是清理、转小写、切词、连接。"
            ),
            quiz(
                "var s = 'abc'; s.toUpperCase(); console.log(s); 输出什么？",
                ["ABC", "abc", "undefined", "报错"],
                1,
                "字符串不可变。toUpperCase 返回新字符串，但没有赋回给 s，所以 s 仍是 'abc'。",
            ),
            *pair(
                """var name = 'V';
var city = 'night city';

var card = `AGENT: ${name}
CITY: ${city.toUpperCase()}
TAG: ${name.toLowerCase()}-01`;

console.log(card);""",
                """AGENT: V
CITY: NIGHT CITY
TAG: v-01""",
            ),
            practice(
                "拆解日志",
                """var line = 'error:disk:full';
var parts = line.split(':');

console.log(parts[0]);
console.log(parts.length);
console.log(parts.join('/'));""",
                """error
3
error/disk/full""",
                "split 按冒号切成三段，join 再用斜杠拼回去。",
            ),
            task("把 card 改成三行模板，并在第二行调用 slice 只保留城市名的前五个字符。"),
        ],
        exercise(
            "生成姓名缩写",
            "实现 initials(fullName)：按空格切分姓名，取每个单词首字母并转大写，用点号连接。initials('judy alvarez') 应返回 'J.A'；空字符串返回 ''。",
            """function initials(fullName) {
  // 切分、取首字母、转大写、用点连接

}

console.log(initials('judy alvarez'));""",
            "fullName.trim().split(' ') 得到单词数组；循环取 word.charAt(0).toUpperCase()，最后用 join('.')。",
            [
                "assert(initials('judy alvarez') === 'J.A', 'judy alvarez 应为 J.A')",
                "assert(initials('v') === 'V', '单名应返回 V')",
                "assert(initials('') === '', '空字符串应返回空字符串')",
                "assert(initials('johnny silverhand') === 'J.S', '多段姓名都要取首字母')",
            ],
            """function initials(fullName) {
  if (fullName === '') return '';
  var words = fullName.trim().split(' ');
  var out = [];
  for (var i = 0; i < words.length; i++) {
    out.push(words[i].charAt(0).toUpperCase());
  }
  return out.join('.');
}

console.log(initials('judy alvarez'));""",
        ),
    )


def js05():
    return lesson(
        "js05", 304, 21, BASIC_CHAPTER,
        "条件分支", "if / else if / switch 与守卫", 80,
        [
            heading("让程序学会选择"),
            paragraph(
                "条件分支解决的是「不同输入走不同路径」。JS 的写法与 C 家族一致：if 后面的条件必须放在小括号里，代码块用花括号包住；多路判断用 else if，最后用 else 兜底。判断从上到下短路，命中第一个真值分支后就不再检查后面的条件，所以顺序本身就是逻辑的一部分。写范围判断时，从最严格或最高的区间开始写。"
            ),
            paragraph(
                "条件表达式最终都会被转成布尔值，这里用的是真值/假值规则：false、0、''、null、undefined、NaN 为假，其余为真。因此 if (name) 判断的是「name 非空且不是那几个假值」，不是「name 已声明」。如果变量可能没被赋值，应先用 typeof name !== 'undefined' 或提前 return 的守卫（guard clause）把异常输入挡在函数入口。"
            ),
            *pair(
                """function access(level) {
  if (level >= 100) {
    return 'ROOT';
  } else if (level >= 50) {
    return 'OPERATOR';
  } else {
    return 'GUEST';
  }
}

console.log(access(120));
console.log(access(66));
console.log(access(3));""",
                """ROOT
OPERATOR
GUEST""",
            ),
            diagram(
                """if (条件 A) {
  ...            // A 为真，执行这里
} else if (条件 B) {
  ...            // A 假、B 真
} else {
  ...            // 以上都假
}"""
            ),
            paragraph(
                "switch 适合「一个值对应多条固定路径」的场景，比如命令分发。它用 === 比较，每个 case 后要写 break，否则会继续执行下一个 case（fallthrough）。多数情况下 switch 可以用对象映射替代：把命令名作为键、处理函数作为值，查表比长串 if 更清晰。选择哪种写法看可读性，不必教条。"
            ),
            warn(
                "if (x = 5) 是赋值不是比较，条件永远为真。写比较时把常量放左边（5 === x）可以让这类笔误直接报错。"
            ),
            quiz(
                "score = 75 时，依次判断 score >= 90、score >= 75、score >= 60，会进入哪个分支？",
                ["第一个", "第二个", "第三个", "都不进"],
                1,
                "75 不满足 >=90，满足 >=75，命中第二个分支后立即返回，不会再检查 >=60。",
            ),
            fill(
                "补全守卫：参数不是数字时提前返回",
                "function guard(x) {\n  if (____(x)) return 'bad input';\n  return 'ok';\n}",
                "isNaN",
                "isNaN(x) 为 true 表示 x 不能转成有效数字。真实项目里还应判断 typeof x === 'number'，避免把 '12' 当成合法数字。",
            ),
            *pair(
                """function route(cmd) {
  switch (cmd) {
    case 'start':
      return 'engine on';
    case 'stop':
      return 'engine off';
    default:
      return 'unknown';
  }
}

console.log(route('start'));
console.log(route('jump'));""",
                """engine on
unknown""",
            ),
            practice(
                "等级速查",
                """function badge(score) {
  if (score >= 90) return 'S';
  if (score >= 60) return 'A';
  return 'F';
}

console.log(badge(95), badge(60), badge(59));""",
                "S A F",
                "多个 if 从高到低排列，命中即 return，不必层层嵌套 else。",
            ),
        ],
        exercise(
            "权限分级器",
            "实现 grade(score)：90 及以上返回 'S'，75 到 89 返回 'A'，60 到 74 返回 'B'，低于 60 返回 'F'；score 不是数字或超出 0-100 返回 'INVALID'。",
            """function grade(score) {
  // 先做输入校验，再按区间返回等级

}

console.log(grade(95));""",
            "先写 if (typeof score !== 'number' || isNaN(score) || score < 0 || score > 100) return 'INVALID'; 再按 90/75/60 从高到低判断。",
            [
                "assert(grade(95) === 'S', '95 应为 S')",
                "assert(grade(90) === 'S', '边界 90 应为 S')",
                "assert(grade(75) === 'A', '边界 75 应为 A')",
                "assert(grade(60) === 'B', '边界 60 应为 B')",
                "assert(grade(101) === 'INVALID' && grade('x') === 'INVALID', '非法输入应被拦截')",
            ],
            """function grade(score) {
  if (typeof score !== 'number' || isNaN(score) || score < 0 || score > 100) {
    return 'INVALID';
  }
  if (score >= 90) return 'S';
  if (score >= 75) return 'A';
  if (score >= 60) return 'B';
  return 'F';
}

console.log(grade(95));
console.log(grade(75));""",
        ),
    )


def js06():
    return lesson(
        "js06", 305, 21, BASIC_CHAPTER,
        "循环", "for / while / for-of 与聚合", 80,
        [
            heading("重复劳动交给机器"),
            paragraph(
                "循环让一段代码按条件重复执行。最通用的是三段式 for：初始化、继续条件、步进，三段用分号隔开；while 适合「不知道要跑几次，只知道何时停」的场景；do-while 至少执行一次，再判断条件。遍历数组时，for-of 更简洁，直接拿到元素而不是下标，但它拿不到索引，需要索引时还是用经典 for。"
            ),
            paragraph(
                "写循环先确定三件事：起点、终点、每次怎么变。终点用数组的 length，不要在循环体里修改被遍历的数组长度，否则很容易越界或漏项。累加、计数、找极值是三种最基本的循环模式：先初始化一个「种子」（0、空数组、第一个元素），再把每个元素合并进去。循环结束后返回种子。"
            ),
            *pair(
                """var scores = [88, 92, 79];
var total = 0;

for (var i = 0; i < scores.length; i++) {
  total = total + scores[i];
  console.log(i, scores[i]);
}

console.log('total =', total);""",
                """0 88
1 92
2 79
total = 259""",
            ),
            table(
                ["循环", "适合场景", "注意点"],
                [
                    ["for", "已知次数或需要下标", "三段都不能少，步进别忘写"],
                    ["while", "条件驱动、次数未知", "循环体里必须让条件有机会变假"],
                    ["do-while", "至少执行一次", "条件在末尾，末尾有分号"],
                    ["for-of", "直接遍历数组/字符串", "不提供下标"],
                ],
            ),
            paragraph(
                "break 立即结束整个循环，continue 跳过本轮剩余语句进入下一轮。它们会影响控制流，滥用会让循环难以读懂。更推荐用「提前 return」把函数逻辑拆开。嵌套循环里 break 只跳出最内层，需要跳出多层时用标签（label），但标签可读性差，通常说明该把内层逻辑抽成函数了。"
            ),
            tip(
                "空数组要先守卫再访问 values[0]，否则 best 是 undefined。JS 不会因为越界报错，只会安静地给你 undefined。"
            ),
            quiz(
                "for (var i = 0; i < 3; i++) 循环体执行几次？i 最终是多少？",
                ["2 次，i=2", "3 次，i=3", "3 次，i=2", "4 次，i=4"],
                1,
                "i 取 0、1、2 各执行一次，共 3 次；执行完 i++ 后 i=3，条件不成立退出。",
            ),
            visualize(
                "循环求最大值",
                "nums = [3, 7, 2]，观察 i 与 max 的变化",
                [
                    {"label": "初始化：max 取第一个元素", "items": [{"name": "i", "value": "0"}, {"name": "max", "value": "3"}], "highlight": ["max"]},
                    {"label": "i=1，7 > 3，更新 max", "items": [{"name": "i", "value": "1"}, {"name": "max", "value": "7"}], "highlight": ["i", "max"]},
                    {"label": "i=2，2 < 7，保持不变", "items": [{"name": "i", "value": "2"}, {"name": "max", "value": "7"}], "highlight": ["i"]},
                    {"label": "循环结束，最大值 7", "items": [{"name": "i", "value": "3"}, {"name": "max", "value": "7"}], "highlight": ["i"]},
                ],
            ),
            *pair(
                """function peak(values) {
  if (values.length === 0) return null;
  var best = values[0];
  for (var i = 1; i < values.length; i++) {
    if (values[i] > best) best = values[i];
  }
  return best;
}

var found = [];
for (var v of [4, 9, 1]) {
  found.push(v * 2);
}

console.log(peak([88, 92, 79]));
console.log(peak([]));
console.log(found.join('-'));""",
                """92
null
8-18-2""",
            ),
        ],
        exercise(
            "累加器",
            "实现 sumTo(n)：返回 1 到 n 的整数和；n 小于 1 时返回 0。",
            """function sumTo(n) {
  // 用循环累加

}

console.log(sumTo(10));""",
            "var total = 0; for (var i = 1; i <= n; i++) total += i; return total;",
            [
                "assert(sumTo(10) === 55, 'sumTo(10) 应为 55')",
                "assert(sumTo(1) === 1, 'sumTo(1) 应为 1')",
                "assert(sumTo(0) === 0, 'sumTo(0) 应为 0')",
                "assert(sumTo(-5) === 0, '负数应返回 0')",
            ],
            """function sumTo(n) {
  var total = 0;
  for (var i = 1; i <= n; i++) {
    total = total + i;
  }
  return total;
}

console.log(sumTo(10));
console.log(sumTo(0));""",
        ),
    )


def js07():
    return lesson(
        "js07", 306, 21, BASIC_CHAPTER,
        "数组", "下标、长度与增删改查", 80,
        [
            heading("一组有序的值"),
            paragraph(
                "数组是按整数下标排列的有序集合，下标从 0 开始，length 表示元素个数。JS 数组是动态的：可以随时 push 追加、pop 弹出、用下标赋值扩展，甚至把 length 改小来截断。这种灵活性很方便，也意味着越界访问不会报错，只会得到 undefined。凡是依赖下标的代码，都要先确认长度。"
            ),
            paragraph(
                "修改原数组的方法有 push、pop、shift、unshift、splice、sort、reverse；返回新数组的方法有 slice、concat、map、filter。初学时要分清「改自己」和「返回副本」，否则函数调用后原数据被悄悄改动，排查起来非常痛苦。一个实用习惯：需要保留原数组时先 slice() 复制一份，再对副本排序或修改。"
            ),
            *pair(
                """var queue = ['V', 'Judy'];

queue.push('Jackie');
console.log(queue.join(','), queue.length);

var first = queue.shift();
console.log(first, queue.join(','));

var copy = queue.slice();
copy.push('Rogue');
console.log(queue.length, copy.length);""",
                """V,Judy,Jackie 3
V Judy,Jackie
2 3""",
            ),
            table(
                ["操作", "方法", "是否修改原数组"],
                [
                    ["末尾追加/删除", "push / pop", "是"],
                    ["开头追加/删除", "unshift / shift", "是"],
                    ["截取片段", "slice(start, end)", "否，返回新数组"],
                    ["任意位置增删", "splice(start, deleteCount, ...items)", "是"],
                    ["拼接", "concat(other)", "否，返回新数组"],
                ],
            ),
            paragraph(
                "sort 默认按字符串排序：[10, 2, 1].sort() 得到 [1, 10, 2]，因为每个元素先转字符串再逐字符比较。数字排序必须传比较函数 (a, b) => a - b，返回负数表示 a 在前，正数表示 b 在前。这个比较函数的方向记不住时，用两个数试一遍即可。"
            ),
            warn(
                "splice 的参数容易记反：splice(起始下标, 删除个数, 要插入的元素...)。它会直接修改原数组，并返回被删除元素组成的新数组。"
            ),
            quiz(
                "var a = [1, 2, 3]; var b = a.slice(1); b.push(9); 此时 a 和 b 分别是什么？",
                ["a=[1,2,3]，b=[2,3,9]", "a=[1,2,3,9]，b=[2,3,9]", "a=[2,3]，b=[2,3,9]", "两者都是 [1,2,3,9]"],
                0,
                "slice 返回新数组，b 是 [2,3]；push 只改 b，a 保持不变。",
            ),
            *pair(
                """var nums = [10, 2, 1];
var sorted = nums.slice().sort(function (a, b) {
  return a - b;
});

console.log(nums.join(','));
console.log(sorted.join(','));
console.log(nums.indexOf(2));
console.log(nums.includes(99));""",
                """10,2,1
1,2,10
1
false""",
            ),
            practice(
                "切片复制",
                """var src = ['a', 'b', 'c', 'd'];
var mid = src.slice(1, 3);

console.log(mid.join('-'));
console.log(src.length);""",
                """b-c
4""",
                "slice(1, 3) 取下标 1 和 2，不包含 3；原数组不变。",
            ),
        ],
        exercise(
            "数组分块",
            "实现 chunk(values, size)：把数组按 size 个一组切成二维数组；size 小于 1 或数组为空时返回空数组。",
            """function chunk(values, size) {
  // 每次用 slice 取一段，push 进结果

}

console.log(JSON.stringify(chunk([1, 2, 3, 4, 5], 2)));""",
            "for (var i = 0; i < values.length; i += size) { out.push(values.slice(i, i + size)); }",
            [
                "assert(JSON.stringify(chunk([1,2,3,4,5], 2)) === '[[1,2],[3,4],[5]]', '按 2 分组')",
                "assert(JSON.stringify(chunk([1,2,3], 5)) === '[[1,2,3]]', 'size 大于长度时只有一组')",
                "assert(JSON.stringify(chunk([], 3)) === '[]', '空数组应返回空数组')",
                "assert(JSON.stringify(chunk([1,2], 0)) === '[]', 'size 小于 1 应返回空数组')",
            ],
            """function chunk(values, size) {
  if (size < 1) return [];
  var out = [];
  for (var i = 0; i < values.length; i += size) {
    out.push(values.slice(i, i + size));
  }
  return out;
}

console.log(JSON.stringify(chunk([1, 2, 3, 4, 5], 2)));""",
        ),
    )


def js08():
    return lesson(
        "js08", 307, 21, BASIC_CHAPTER,
        "对象", "键值对、in 与 Object.keys", 80,
        [
            heading("用名字索引数据"),
            paragraph(
                "对象是键值对的集合，键是字符串（或 Symbol），值可以是任意类型。它承担了 Python 字典的角色，但访问方式更丰富：点号 obj.name 适合固定的合法标识符，中括号 obj['key'] 适合动态键、含空格或数字的键。读取不存在的键不会报错，而是返回 undefined，这一点和 Python 抛 KeyError 完全不同。"
            ),
            paragraph(
                "判断键是否存在用 'key' in obj，它同时检查原型链；只想看对象自身属性用 Object.prototype.hasOwnProperty.call(obj, 'key')。遍历自身可枚举键用 Object.keys，拿值用 Object.values，拿键值对用 Object.entries。对象里键的顺序：整数形式的键按数值升序，其余按插入顺序，不要依赖顺序写业务逻辑。"
            ),
            *pair(
                """var agent = { name: 'V', level: 66, online: true };

console.log(agent.name);
console.log(agent['level']);
console.log('name' in agent);
console.log('rank' in agent);
console.log(Object.keys(agent).join(','));""",
                """V
66
true
false
name,level,online""",
            ),
            table(
                ["需求", "写法", "说明"],
                [
                    ["读属性", "obj.key / obj['key']", "不存在的键返回 undefined"],
                    ["写属性", "obj.key = value", "键不存在就新增"],
                    ["删除属性", "delete obj.key", "删除后 in 返回 false"],
                    ["列出键", "Object.keys(obj)", "只含自身可枚举属性"],
                    ["遍历键值", "Object.entries(obj)", "返回 [key, value] 数组的数组"],
                ],
            ),
            paragraph(
                "用对象做频次统计是经典套路：遍历数据，若 counts[key] === undefined 就置 1，否则加 1。这里不能写成 if (counts[key])，因为计数为 0 时会被当成假值，虽然本场景初值不会是 0，但习惯上应显式判断 undefined。统计完成后，用 Object.keys(counts).length 可以得到不同键的数量。"
            ),
            tip(
                "中括号里的键会被转成字符串：obj[1] 和 obj['1'] 是同一个属性。用对象当键会得到 '[object Object]'，需要真正的对象键请用 Map。"
            ),
            quiz(
                "var o = {}; console.log(o.missing); 输出什么？",
                ["null", "undefined", "报错 ReferenceError", "0"],
                1,
                "读取不存在的属性返回 undefined，不报错。这也是为什么拼错属性名时程序会安静地出错。",
            ),
            *pair(
                """function freq(text) {
  var counts = {};
  for (var i = 0; i < text.length; i++) {
    var ch = text[i];
    if (counts[ch] === undefined) {
      counts[ch] = 1;
    } else {
      counts[ch] = counts[ch] + 1;
    }
  }
  return counts;
}

var result = freq('aab');
console.log(JSON.stringify(result));
console.log(Object.keys(result).length);""",
                """{"a":2,"b":1}
2""",
            ),
            practice(
                "对象读写",
                """var profile = { name: 'Judy', tags: ['netrunner'] };

profile.level = 42;
delete profile.tags;

console.log(profile.name, profile.level);
console.log('tags' in profile);""",
                """Judy 42
false""",
                "点号新增属性；delete 删除后 in 返回 false。",
            ),
        ],
        exercise(
            "字符频率统计",
            "实现 freq(text)：返回每个字符出现次数的对象。freq('aab') 应得到 { a: 2, b: 1 }。",
            """function freq(text) {
  // 遍历字符，用对象累计次数

}

console.log(JSON.stringify(freq('aab')));""",
            "counts[ch] === undefined 时置 1，否则 counts[ch] += 1；最后返回 counts。",
            [
                "var c1 = freq('aab');\nassert(c1.a === 2, 'a 应出现 2 次')",
                "assert(c1.b === 1, 'b 应出现 1 次')",
                "var c2 = freq('');\nassert(Object.keys(c2).length === 0, '空串应得到空对象')",
                "var c3 = freq('xyx');\nassert(c3.x === 2 && c3.y === 1, '多字符统计')",
            ],
            """function freq(text) {
  var counts = {};
  for (var i = 0; i < text.length; i++) {
    var ch = text[i];
    if (counts[ch] === undefined) counts[ch] = 1;
    else counts[ch] = counts[ch] + 1;
  }
  return counts;
}

console.log(JSON.stringify(freq('aab')));""",
        ),
    )


def js09():
    return lesson(
        "js09", 308, 21, BASIC_CHAPTER,
        "函数与参数", "声明、表达式、返回值与 rest", 90,
        [
            heading("把逻辑封装成可复用的盒子"),
            paragraph(
                "函数是 JS 的一等公民：它可以被声明、赋值给变量、作为参数传递、作为返回值返回。声明式函数 function add(a, b) 会被提升，可以在定义之前调用；函数表达式 var add = function (a, b) 不会提升，必须先赋值再调用。箭头函数是表达式的简写，(a, b) => a + b，适合短小的回调，但它没有自己的 this 和 arguments。"
            ),
            paragraph(
                "参数是按值传递的：基本类型传副本，对象传引用的副本，所以函数内部修改对象属性会影响外部，但重新给参数赋值不会改变外部变量。参数个数不匹配不会报错：少传得到 undefined，多传会被忽略（可用 arguments 或 rest 参数收集）。rest 参数写作 ...args，必须是最后一个参数，得到真正的数组。"
            ),
            *pair(
                """function total() {
  var sum = 0;
  for (var i = 0; i < arguments.length; i++) {
    sum = sum + arguments[i];
  }
  return sum;
}

function average() {
  var args = Array.prototype.slice.call(arguments);
  return total.apply(null, args) / args.length;
}

console.log(total(1, 2, 3, 4));
console.log(average(2, 4, 6));""",
                """10
4""",
            ),
            table(
                ["写法", "示例", "关键差异"],
                [
                    ["函数声明", "function add(a, b) {}", "会提升，可先调用后定义"],
                    ["函数表达式", "var add = function (a, b) {}", "不提升，赋值后才可用"],
                    ["箭头函数", "var add = (a, b) => a + b;", "无自己的 this/arguments"],
                    ["rest 参数", "function f(...args) {}", "收集剩余参数为数组"],
                ],
            ),
            paragraph(
                "return 立即结束函数并交回一个值；不写 return 的函数返回 undefined。不要用 console.log 代替 return——打印只是给人看，返回值才是给调用者用的。一个函数最好只做一件事：计算就返回结果，输出交给调用方；这样它才能被测试、被复用、被组合。参数超过三个时，考虑改传一个配置对象。"
            ),
            warn(
                "箭头函数不能用作构造函数，也没有 arguments。需要动态 this 的方法不要写成箭头函数，否则 this 会指向外层作用域。"
            ),
            quiz(
                "function f(a, b) { return a + b; } console.log(f(1)); 输出什么？",
                ["1", "2", "NaN", "报错"],
                2,
                "少传的 b 是 undefined，1 + undefined 得到 NaN。参数缺省不会自动补 0。",
            ),
            order(
                "把函数调用链排成正确顺序",
                [
                    "定义函数 add(a, b)",
                    "调用 add(2, 3) 得到 5",
                    "把返回值传给 console.log",
                    "控制台输出 5",
                ],
            ),
            *pair(
                """function makeBadge(name, role) {
  return '[' + role + '] ' + name;
}

var badge = makeBadge('V', 'netrunner');

console.log(badge);
console.log(badge.length);""",
                """[netrunner] V
13""",
            ),
            practice(
                "默认值的手动写法",
                """function greet(name) {
  if (name === undefined) name = 'anonymous';
  return 'hi, ' + name;
}

console.log(greet('Judy'));
console.log(greet());""",
                """hi, Judy
hi, anonymous""",
                "本运行时支持 rest 参数但不支持默认参数，用 if (name === undefined) 手动兜底。",
            ),
        ],
        exercise(
            "重复拼接",
            "实现 repeatJoin(word, times, sep)：把 word 重复 times 次，用 sep 连接；times 小于等于 0 时返回空字符串。",
            """function repeatJoin(word, times, sep) {
  // 用循环收集，再 join

}

console.log(repeatJoin('ab', 3, '-'));""",
            "var parts = []; for (var i = 0; i < times; i++) parts.push(word); return parts.join(sep);",
            [
                "assert(repeatJoin('ab', 3, '-') === 'ab-ab-ab', '重复 3 次用 - 连接')",
                "assert(repeatJoin('x', 1, ',') === 'x', '只重复 1 次')",
                "assert(repeatJoin('x', 0, ',') === '', '0 次应返回空串')",
                "assert(repeatJoin('a', 2, '') === 'aa', '分隔符可以为空')",
            ],
            """function repeatJoin(word, times, sep) {
  var parts = [];
  for (var i = 0; i < times; i++) {
    parts.push(word);
  }
  return parts.join(sep);
}

console.log(repeatJoin('ab', 3, '-'));""",
        ),
    )


def js10():
    return lesson(
        "js10", 309, 21, BASIC_CHAPTER,
        "作用域与提升", "变量住在哪一层", 90,
        [
            heading("可见性决定一切"),
            paragraph(
                "作用域是变量能被访问的范围。JS 有三层：全局作用域、函数作用域、块级作用域（let/const 引入）。函数内部可以访问外部的变量，外部不能访问函数内部的变量；内层同名变量会遮蔽（shadow）外层变量。查找变量时从当前作用域逐层向外，直到全局；找不到就抛 ReferenceError。"
            ),
            paragraph(
                "提升（hoisting）是 JS 在进入作用域前先登记声明的机制。var 声明的变量会被提升到函数顶部，但赋值留在原处，所以声明前访问得到 undefined，而不是报错。函数声明整体被提升，可以在定义之前调用。标准 JS 里 let/const 也有暂时性死区（TDZ），声明前访问会抛 ReferenceError；但本课程使用的 Rhino 运行时在脚本顶层把 let/const 处理得接近 var，声明前读到 undefined。知道标准与实现的差异，比背结论更重要。"
            ),
            *pair(
                """console.log('var before:', typeof legacy);

var legacy = 'assigned';

function hoisted() {
  return 'function is hoisted';
}

console.log(hoisted());
console.log('var after:', legacy);

try {
  console.log(undeclaredName);
} catch (e) {
  console.log('undeclared error:', e.name);
}

let modern = 'block';
console.log('let after:', modern);""",
                """var before: undefined
function is hoisted
var after: assigned
undeclared error: ReferenceError
let after: block""",
            ),
            diagram(
                """全局作用域
  └─ 函数 outer
       ├─ var x（函数级，整段可见）
       └─ 块 { let y }（只在该块内可见）
            └─ 内层函数可读取 x / y（闭包）"""
            ),
            paragraph(
                "闭包是作用域规则的自然结果：函数会记住它定义时所在的作用域，即使外层函数已经返回，内层函数仍能读取那些变量。后面核心篇会专门展开。现在先建立一个判断标准：看一个变量属于谁，不看它在哪一行被使用，而看它在哪里被声明。把变量声明得离使用处越近，作用域越小，出错概率越低。"
            ),
            warn(
                "var 在 for 循环中只有一个变量，循环结束后仍是最后一个值；let 在每次迭代会创建新的绑定，更适合配合回调。但本运行时对 let 的每次迭代绑定支持不完整，写闭包时用函数工厂而不是依赖循环变量。"
            ),
            quiz(
                "console.log(x); var x = 5; 输出什么？",
                ["5", "undefined", "报错 ReferenceError", "null"],
                1,
                "var 声明被提升，赋值没有；所以此时 x 已存在但值是 undefined。",
            ),
            fill(
                "补全代码：让函数内部的变量不污染全局",
                "function run() {\n  ____ secret = 'local';\n  return secret;\n}",
                "var",
                "函数内部用 var（或 let/const）声明，变量就属于函数作用域；不加关键字会创建或修改全局变量。",
            ),
            *pair(
                """var label = 'global';

function show() {
  var label = 'local';
  return label;
}

function readGlobal() {
  return label;
}

console.log(show());
console.log(readGlobal());
console.log(label);""",
                """local
global
global""",
            ),
            task("把 show 里的 var 改成 let，观察块级作用域；再访问一个从未声明的变量，对比 ReferenceError 与 undefined 的区别。"),
        ],
        exercise(
            "乘法器工厂",
            "实现 makeMultiplier(factor)：返回一个函数，调用它时传入数字 x，返回 x * factor。两次调用 makeMultiplier 得到的函数互不影响。",
            """function makeMultiplier(factor) {
  // 返回一个函数，它记住 factor

}

var triple = makeMultiplier(3);
console.log(triple(5));""",
            "在 makeMultiplier 内部写 return function (x) { return x * factor; }; factor 被内层函数捕获，这就是闭包。",
            [
                "assert(makeMultiplier(3)(5) === 15, '3 倍器：5 -> 15')",
                "assert(makeMultiplier(0)(99) === 0, '0 倍器任何数都是 0')",
                "assert(makeMultiplier(-2)(4) === -8, '负数因子也要正确')",
                "var a = makeMultiplier(2);\nvar b = makeMultiplier(10);\nassert(a(3) === 6 && b(3) === 30, '两个工厂互不影响')",
            ],
            """function makeMultiplier(factor) {
  return function (x) {
    return x * factor;
  };
}

var triple = makeMultiplier(3);
console.log(triple(5));
console.log(makeMultiplier(10)(2));""",
        ),
    )


BASICS = [js01(), js02(), js03(), js04(), js05(), js06(), js07(), js08(), js09(), js10()]

# ---------------------------------------------------------------------------
# 核心篇 js11 - js20
# ---------------------------------------------------------------------------

CORE_CHAPTER = "JavaScript · 核心篇"


def js11():
    return lesson(
        "js11", 310, 22, CORE_CHAPTER,
        "数组三剑客", "map / filter / reduce", 90,
        [
            heading("把循环写成声明式的表达"),
            paragraph(
                "上一章我们用 for 循环手动累加、筛选、变形。数组自带三个高阶方法，把这三种模式各封成一个词：map 负责「每个元素变成什么」，返回等长新数组；filter 负责「留下哪些元素」，返回长度可能变小的新数组；reduce 负责「折叠成一个值」，返回累加结果。它们都不修改原数组，回调收到的参数是 (当前值, 下标, 原数组)。"
            ),
            paragraph(
                "三者可以链式组合：先 filter 筛选，再 map 变形，最后 reduce 汇总。链式写法的可读性来自「每行只做一件事」，但也要注意代价：每一步都会生成一个中间数组。数据量小的时候不必在意，数据量大时可以用一次 reduce 完成多件事，或者改回 for 循环。工具没有绝对优劣，关键是你知道每一步发生了什么。"
            ),
            *pair(
                """var nums = [1, 2, 3, 4, 5];

var doubled = nums.map(function (n) {
  return n * 2;
});

var evens = nums.filter(function (n) {
  return n % 2 === 0;
});

var total = nums.reduce(function (sum, n) {
  return sum + n;
}, 0);

console.log(doubled.join(','));
console.log(evens.join(','));
console.log(total);""",
                """2,4,6,8,10
2,4
15""",
            ),
            table(
                ["方法", "回调返回值", "结果", "是否改原数组"],
                [
                    ["map", "新元素", "等长新数组", "否"],
                    ["filter", "布尔值", "通过筛选的元素", "否"],
                    ["reduce", "新的累加值", "单个值", "否"],
                    ["forEach", "无", "undefined", "否（但可产生副作用）"],
                ],
            ),
            paragraph(
                "reduce 最容易写错。它的第二个参数是初始值：给了初始值，第一次回调的 sum 就是它；不给，则拿第一个元素当初始值，从第二个元素开始遍历。空数组不带初始值调用 reduce 会抛 TypeError。因此求和、计数这类场景一律显式传 0，字符串拼接传空串，找最大值可以传第一个元素或极小值。回调的返回值会成为下一轮的累加值，忘记 return 是最常见的错误。"
            ),
            warn(
                "不要在 map 里做副作用（比如 push 到外部数组）。map 的语义是「返回新数组」，用 forEach 做副作用更诚实。"
            ),
            quiz(
                "[1, 2, 3].reduce(function (a, b) { return a + b; }) 的结果是？",
                ["6", "NaN", "3", "报错"],
                0,
                "没有初始值时，第一次回调用 1 作为 a、2 作为 b，得到 3；第二次 3 + 3 = 6。",
            ),
            *pair(
                """var people = [
  { name: 'V', level: 66 },
  { name: 'Judy', level: 42 },
  { name: 'Jackie', level: 30 }
];

var names = people
  .filter(function (p) { return p.level >= 40; })
  .map(function (p) { return p.name; });

var maxLevel = people.reduce(function (best, p) {
  return p.level > best ? p.level : best;
}, 0);

console.log(names.join(' & '));
console.log(maxLevel);""",
                """V & Judy
66""",
            ),
            practice(
                "链式过滤",
                """var words = ['neon', 'rain', 'city', 'sky'];

var long = words
  .filter(function (w) { return w.length > 3; })
  .map(function (w) { return w.toUpperCase(); });

console.log(long.join('-'));""",
                "NEON-RAIN-CITY",
                "filter 先留下长度大于 3 的词，map 再统一转大写。",
            ),
        ],
        exercise(
            "数组分析器",
            "实现 analyze(nums)：返回对象 { squares, evens, total }。squares 是每个元素的平方，evens 是偶数，total 是总和。空数组时 squares/evens 为空数组、total 为 0。",
            """function analyze(nums) {
  // 分别用 map / filter / reduce

}

console.log(JSON.stringify(analyze([1, 2, 3, 4])));""",
            "var squares = nums.map(function (n) { return n * n; }); evens 用 filter；total 用 reduce 传初始值 0。",
            [
                "assert(JSON.stringify(analyze([1,2,3,4]).squares) === '[1,4,9,16]', 'squares 应为平方')",
                "assert(JSON.stringify(analyze([1,2,3,4]).evens) === '[2,4]', 'evens 只留偶数')",
                "assert(analyze([1,2,3,4]).total === 10, 'total 应为总和')",
                "assert(JSON.stringify(analyze([])) === '{\"squares\":[],\"evens\":[],\"total\":0}', '空数组要有兜底结果')",
            ],
            """function analyze(nums) {
  var squares = nums.map(function (n) { return n * n; });
  var evens = nums.filter(function (n) { return n % 2 === 0; });
  var total = nums.reduce(function (sum, n) { return sum + n; }, 0);
  return { squares: squares, evens: evens, total: total };
}

console.log(JSON.stringify(analyze([1, 2, 3, 4])));""",
        ),
    )


def js12():
    return lesson(
        "js12", 311, 22, CORE_CHAPTER,
        "字符串工具箱", "trim / split / replace / padStart", 90,
        [
            heading("清洗、切分、重组"),
            paragraph(
                "真实数据几乎总是脏的：前后有空格、大小写混乱、分隔符不统一。字符串方法就是流水线上的工位。trim 去掉首尾空白（包括换行和制表符），toLowerCase/toUpperCase 统一大小写，split 按分隔符切成数组，join 再拼回字符串，replace 替换第一处匹配。把这些方法串起来，就能完成大部分清洗任务。"
            ),
            paragraph(
                "replace 默认只替换第一处，需要全部替换时有两个选择：传带 g 标志的正则，或者用 split(旧串).join(新串) 的技巧。replace 的第二个参数可以是函数，接收匹配到的内容并返回替换值，这是做模板填充的关键。slice、substring、substr 都能截取，但参数语义不同，统一用 slice 最省心：它支持负索引，结束位置不包含。"
            ),
            *pair(
                """var raw = '  Neon City  ';

console.log('[' + raw.trim() + ']');
console.log(raw.trim().toLowerCase());
console.log(raw.trim().split(' ').join('-'));
console.log('abc'.toUpperCase());
console.log('x'.repeat(3));""",
                """[Neon City]
neon city
Neon-City
ABC
xxx""",
            ),
            table(
                ["方法", "作用", "示例"],
                [
                    ["trim", "去掉首尾空白", "'  a  '.trim() -> 'a'"],
                    ["split", "按分隔符切数组", "'a,b'.split(',') -> ['a','b']"],
                    ["join", "数组拼字符串", "['a','b'].join('-') -> 'a-b'"],
                    ["replace", "替换第一处", "'a-b-c'.replace('-','/') -> 'a/b-c'"],
                    ["padStart", "左侧补字符", "'7'.padStart(3,'0') -> '007'"],
                    ["includes", "是否包含子串", "'abc'.includes('b') -> true"],
                ],
            ),
            paragraph(
                "数字补零是常见需求：String(7).padStart(3, '0') 得到 '007'。注意 padStart 只能作用于字符串，数字要先 String() 或 .toString()。另一个坑是 split('') 与 split() 不同：前者按字符切，后者把整串作为一个元素。处理用户输入的空格时，split(' ') 会保留连续空格产生的空串，通常要再 filter 掉空串。"
            ),
            tip(
                "需要「全部替换」又不想写正则时：s.split(old).join(new)。它按字面量匹配，不会误触发正则元字符。"
            ),
            quiz(
                "'a-b-c'.replace('-', '/') 的结果是？",
                ["'a/b/c'", "'a/b-c'", "'a-b/c'", "报错"],
                1,
                "replace 传字符串时只替换第一处匹配。全部替换要传 /-/g 或使用 split/join。",
            ),
            *pair(
                """var line = 'ERROR|disk|full';

var parts = line.split('|');
var label = parts[0].toLowerCase();
var path = parts.slice(1).join('/');

console.log(label);
console.log(path);
console.log(String(7).padStart(3, '0'));""",
                """error
disk/full
007""",
            ),
            practice(
                "清理空格",
                """var input = '  a   b  c  ';

var words = input.trim().split(' ').filter(function (w) {
  return w !== '';
});

console.log(words.length);
console.log(words.join('_'));""",
                """3
a_b_c""",
                "先 trim 去掉首尾，再按单个空格切，最后 filter 掉连续空格产生的空串。",
            ),
        ],
        exercise(
            "词频摘要",
            "实现 wordStats(text)：按空白切词（忽略多余空格），返回 { count, longest, upper }。count 是词数，longest 是最长单词（并列取第一个），upper 是全部单词转大写后用空格连接。空文本返回 { count: 0, longest: '', upper: '' }。",
            """function wordStats(text) {
  // 清洗、切词，再统计

}

console.log(JSON.stringify(wordStats('Neon city rain')));""",
            "var words = text.trim().split(' ').filter(function (w) { return w !== ''; }); 然后用循环找最长，用 map/join 生成 upper。",
            [
                "var s = wordStats('Neon city rain');\nassert(s.count === 3, '应有 3 个词')",
                "assert(s.longest === 'Neon', '最长词应为 Neon')",
                "assert(s.upper === 'NEON CITY RAIN', 'upper 应全大写')",
                "var e = wordStats('   ');\nassert(e.count === 0 && e.longest === '' && e.upper === '', '空文本要有兜底')",
            ],
            """function wordStats(text) {
  var words = text.trim().split(' ').filter(function (w) {
    return w !== '';
  });
  if (words.length === 0) {
    return { count: 0, longest: '', upper: '' };
  }
  var longest = words[0];
  for (var i = 1; i < words.length; i++) {
    if (words[i].length > longest.length) longest = words[i];
  }
  var upper = words.map(function (w) { return w.toUpperCase(); }).join(' ');
  return { count: words.length, longest: longest, upper: upper };
}

console.log(JSON.stringify(wordStats('Neon city rain')));""",
        ),
    )


def js13():
    return lesson(
        "js13", 312, 22, CORE_CHAPTER,
        "JSON 与数据交换", "序列化、解析与深拷贝", 90,
        [
            heading("把内存里的对象变成可传输的文本"),
            paragraph(
                "JSON 是一种文本格式，不是 JS 对象。JSON.stringify 把值序列化成字符串，JSON.parse 把字符串还原成值。网络传输、本地存储、配置文件都靠它。JSON 的语法比 JS 对象字面量更严格：键必须用双引号，不能有尾逗号，不能写注释，值只支持对象、数组、字符串、数字、true、false、null。"
            ),
            paragraph(
                "序列化时有几条容易踩的规则：undefined、函数、Symbol 作为对象属性时会被直接丢弃；作为数组元素时变成 null；NaN 和 Infinity 变成 null；Date 会先转成 ISO 字符串。反序列化失败会抛 SyntaxError，所以处理外部输入时一定要 try/catch，不能假设对方给的字符串一定合法。"
            ),
            *pair(
                """var agent = {
  name: 'V',
  level: 66,
  tags: ['netrunner', 'merc'],
  active: true
};

var text = JSON.stringify(agent);
console.log(text);

var back = JSON.parse(text);
console.log(back.name, back.tags.length, back.active);""",
                """{"name":"V","level":66,"tags":["netrunner","merc"],"active":true}
V 2 true""",
            ),
            table(
                ["JS 值", "JSON.stringify 结果", "说明"],
                [
                    ["{ a: 1 }", "'{\"a\":1}'", "键必须双引号"],
                    ["[1, 'x']", "'[1,\"x\"]'", "数组保持顺序"],
                    ["undefined（对象属性）", "被丢弃", "数组里则变 null"],
                    ["NaN", "null", "非有限数字无法表示"],
                    ["function", "被丢弃", "JSON 只存数据"],
                ],
            ),
            paragraph(
                "用 JSON.parse(JSON.stringify(obj)) 可以做「深拷贝」，但它有明确边界：函数和 undefined 会丢，Date 会变成字符串，循环引用直接抛错。真正的深拷贝要自己写递归，或使用结构化克隆（本运行时没有 structuredClone）。教学阶段可以用这个技巧处理纯数据，生产代码要确认数据里没有特殊类型。"
            ),
            warn(
                "JSON.parse 对格式极其严格：单引号、尾逗号、注释都会抛 SyntaxError。不要用 eval 解析 JSON，那是安全漏洞。"
            ),
            quiz(
                "JSON.stringify({ a: undefined, b: 1 }) 的结果是？",
                ["'{\"a\":null,\"b\":1}'", "'{\"b\":1}'", "报错", "'{\"a\":undefined,\"b\":1}'"],
                1,
                "对象里的 undefined 属性会被整体丢弃，所以只剩 b。数组里的 undefined 才会变成 null。",
            ),
            *pair(
                """var raw = '{"id":7,"name":"Judy"}';
var data = JSON.parse(raw);

console.log(data.name.toUpperCase());

var pretty = JSON.stringify(data, null, 2);
console.log(pretty);""",
                """JUDY
{
  "id": 7,
  "name": "Judy"
}""",
            ),
            practice(
                "安全解析",
                """function parseOrNull(text) {
  try {
    return JSON.parse(text);
  } catch (e) {
    return null;
  }
}

console.log(parseOrNull('{"ok":true}').ok);
console.log(parseOrNull('not json'));""",
                """true
null""",
                "解析外部文本必须捕获异常，失败时返回一个明确的兜底值。",
            ),
        ],
        exercise(
            "字段提取",
            "实现 pickFields(jsonText, fields)：先解析 JSON，再返回只包含 fields 中列出的键的新对象；解析失败返回 null；缺失的键不出现在结果里。",
            """function pickFields(jsonText, fields) {
  // 解析失败返回 null；否则按 fields 挑选

}

console.log(JSON.stringify(pickFields('{"a":1,"b":2,"c":3}', ['a', 'c'])));""",
            "try { var data = JSON.parse(jsonText); ... } catch (e) { return null; } 用循环和 in 判断键是否存在。",
            [
                "assert(JSON.stringify(pickFields('{\"a\":1,\"b\":2,\"c\":3}', ['a','c'])) === '{\"a\":1,\"c\":3}', '只保留指定字段')",
                "assert(JSON.stringify(pickFields('{\"a\":1}', [])) === '{}', 'fields 为空应返回空对象')",
                "assert(pickFields('bad json', ['a']) === null, '解析失败应返回 null')",
                "assert(JSON.stringify(pickFields('{\"a\":1}', ['a','zzz'])) === '{\"a\":1}', '缺失字段应跳过')",
            ],
            """function pickFields(jsonText, fields) {
  var data;
  try {
    data = JSON.parse(jsonText);
  } catch (e) {
    return null;
  }
  var out = {};
  for (var i = 0; i < fields.length; i++) {
    var key = fields[i];
    if (key in data) out[key] = data[key];
  }
  return out;
}

console.log(JSON.stringify(pickFields('{"a":1,"b":2,"c":3}', ['a', 'c'])));""",
        ),
    )


def js14():
    return lesson(
        "js14", 313, 22, CORE_CHAPTER,
        "Math 与 Date", "取整、随机与时间计算", 100,
        [
            heading("数值与时间的工具层"),
            paragraph(
                "Math 是静态工具对象，不需要 new。常用方法分三类：取整（floor 向下、ceil 向上、round 四舍五入、trunc 截断）、幂与根（pow、sqrt）、极值与绝对值（max、min、abs）。Math.random() 返回 [0, 1) 的伪随机小数，做随机整数要写成 Math.floor(Math.random() * n) + 1。注意它不可加密，不能用来生成令牌。"
            ),
            paragraph(
                "Date 同时表示时间点和日历字段。new Date() 取当前时刻，new Date(年, 月, 日) 用本地时间构造，月份从 0 开始（0 是一月，11 是十二月）。getFullYear、getMonth、getDate、getDay、getHours 分别取年、月、日、星期、小时。两个 Date 相减得到毫秒差，除以 86400000 就是天数。Date 的内部值是一个毫秒时间戳，可以用 getTime() 取出。"
            ),
            *pair(
                """console.log(Math.floor(6.9));
console.log(Math.ceil(0.1));
console.log(Math.round(2.5), Math.round(-2.5));
console.log(Math.max(3, 9, 2), Math.min(3, 9, 2));
console.log(Math.pow(2, 10));
console.log(Math.abs(-7));""",
                """6
1
3 -2
9 2
1024
7""",
            ),
            table(
                ["需求", "写法", "结果示例"],
                [
                    ["向下取整", "Math.floor(6.9)", "6"],
                    ["向上取整", "Math.ceil(0.1)", "1"],
                    ["四舍五入", "Math.round(2.5)", "3"],
                    ["平方根", "Math.sqrt(81)", "9"],
                    ["随机整数 1..6", "Math.floor(Math.random()*6)+1", "1 到 6"],
                    ["时间差（天）", "(b - a) / 86400000", "数字"],
                ],
            ),
            paragraph(
                "日期格式化必须手动补零：getMonth() 返回 0-11，显示时要 +1；getDate() 和 getHours() 可能是一位数，要用 padStart(2, '0')。不要依赖 toLocaleDateString 的输出，它受运行环境和时区影响，不同设备结果可能不同。做跨时区计算时统一用 getUTCFullYear 等 UTC 方法，避免本地时区把日期推前或推后一天。"
            ),
            tip(
                "new Date(2026, 10, 6) 表示 2026 年 11 月 6 日，不是 10 月。月份从 0 开始是 JS 最著名的历史包袱之一。"
            ),
            quiz(
                "new Date(2026, 0, 15).getMonth() 返回什么？",
                ["1", "0", "15", "2026"],
                1,
                "构造时 0 表示一月，getMonth() 也返回 0。只有展示给用户时才 +1。",
            ),
            *pair(
                """var d = new Date(2026, 10, 6, 9, 5, 7);

console.log(d.getFullYear());
console.log(d.getMonth() + 1);
console.log(d.getDate());
console.log(d.getDay());

var start = new Date(2026, 0, 1);
var end = new Date(2026, 0, 10);
console.log((end - start) / 86400000);""",
                """2026
11
6
5
9""",
            ),
            practice(
                "补零格式化",
                """var d = new Date(2026, 0, 5);

var text = d.getFullYear() + '-' +
  String(d.getMonth() + 1).padStart(2, '0') + '-' +
  String(d.getDate()).padStart(2, '0');

console.log(text);""",
                "2026-01-05",
                "月和日都可能是 1 位数，统一 String(...).padStart(2, '0')。",
            ),
        ],
        exercise(
            "日期工具",
            "实现 formatDate(date)：返回 'YYYY-MM-DD'（月、日补零）。实现 daysBetween(a, b)：返回两个日期相差的整天数，取绝对值。",
            """function formatDate(date) {
  // 年-月-日，月和日补零

}

function daysBetween(a, b) {
  // 毫秒差除以一天

}

console.log(formatDate(new Date(2026, 0, 5)));""",
            "formatDate 用 getFullYear/getMonth+1/getDate 拼 padStart；daysBetween 用 Math.abs((b - a) / 86400000)。",
            [
                "assert(formatDate(new Date(2026, 0, 5)) === '2026-01-05', '月和日要补零')",
                "assert(formatDate(new Date(2026, 10, 30)) === '2026-11-30', '两位月日保持原样')",
                "assert(daysBetween(new Date(2026, 0, 1), new Date(2026, 0, 10)) === 9, '相差 9 天')",
                "assert(daysBetween(new Date(2026, 0, 10), new Date(2026, 0, 1)) === 9, '反向也要取绝对值')",
            ],
            """function formatDate(date) {
  var m = String(date.getMonth() + 1).padStart(2, '0');
  var d = String(date.getDate()).padStart(2, '0');
  return date.getFullYear() + '-' + m + '-' + d;
}

function daysBetween(a, b) {
  return Math.abs((b - a) / 86400000);
}

console.log(formatDate(new Date(2026, 0, 5)));""",
        ),
    )


def js15():
    return lesson(
        "js15", 314, 22, CORE_CHAPTER,
        "错误处理", "try / catch / throw 与异常设计", 100,
        [
            heading("失败也是程序的一部分"),
            paragraph(
                "错误处理不是「出问题时再说」，而是函数契约的一部分。JS 用 throw 抛出一个值，通常是 Error 实例；用 try 包住可能出错的代码，catch 捕获并处理，finally 无论成功失败都会执行。Error 实例有 name 和 message 两个关键属性，堆栈信息由运行时补充。抛字符串虽然合法，但会丢失类型和堆栈，生产代码应抛 Error。"
            ),
            paragraph(
                "catch 捕获的是运行时错误和主动 throw 的错误，不包括语法错误（语法错误在解析阶段就失败）。处理错误有三种策略：就地恢复（返回兜底值）、转换后重抛（补充上下文）、向上冒泡（让调用方决定）。不要吞掉错误——空的 catch 会让故障变成幽灵。至少记录日志，或者返回一个调用方能识别的失败标记。"
            ),
            *pair(
                """function parseAge(text) {
  var n = Number(text);
  if (isNaN(n)) {
    throw new Error('age must be a number');
  }
  if (n < 0 || n > 150) {
    throw new Error('age out of range');
  }
  return n;
}

try {
  console.log(parseAge('42'));
  console.log(parseAge('abc'));
} catch (e) {
  console.log('caught:', e.message);
} finally {
  console.log('cleanup');
}""",
                """42
caught: age must be a number
cleanup""",
            ),
            table(
                ["关键字", "作用", "注意点"],
                [
                    ["throw", "主动抛出错误", "抛 Error 而不是字符串"],
                    ["try", "包住可能失败的代码", "范围尽量小"],
                    ["catch", "捕获并处理", "不要留空，至少记录"],
                    ["finally", "收尾清理", "return 也拦不住它执行"],
                ],
            ),
            paragraph(
                "自定义错误类型用构造函数加原型继承实现（class 语法在本运行时不可用）：function ValidationError(message) { this.name = 'ValidationError'; this.message = message; } 然后 ValidationError.prototype = Object.create(Error.prototype)。这样 instanceof Error 和 instanceof ValidationError 都成立，调用方可以按类型分别处理。"
            ),
            warn(
                "不要用 try/catch 包住整个程序来掩盖问题。异常应该在最接近发生点的地方被分类处理，而不是在入口处统一静默。"
            ),
            quiz(
                "try { throw new Error('x'); } finally { console.log('f'); } 会输出什么？",
                ["什么都不输出", "f，然后异常继续抛", "f，异常被吞掉", "报错，finally 不执行"],
                1,
                "finally 一定执行，但它不会吞掉异常；没有 catch 时异常继续向外传播。",
            ),
            *pair(
                """function ValidationError(message) {
  this.name = 'ValidationError';
  this.message = message;
}
ValidationError.prototype = Object.create(Error.prototype);

function checkLevel(level) {
  if (typeof level !== 'number') {
    throw new ValidationError('level must be a number');
  }
  return level;
}

try {
  checkLevel('high');
} catch (e) {
  console.log(e.name);
  console.log(e instanceof Error);
}""",
                """ValidationError
true""",
            ),
            practice(
                "兜底解析",
                """function toInt(text, fallback) {
  try {
    var n = parseInt(text, 10);
    if (isNaN(n)) throw new Error('NaN');
    return n;
  } catch (e) {
    return fallback;
  }
}

console.log(toInt('12', 0));
console.log(toInt('x', -1));""",
                """12
-1""",
                "parseInt 失败返回 NaN，主动 throw 后由 catch 统一返回兜底值。",
            ),
        ],
        exercise(
            "参数校验器",
            "实现 requirePositive(n)：n 是大于 0 的有限数字时返回 n，否则抛 Error，消息为 'must be a positive number'。再实现 safePositive(n)：调用 requirePositive，成功返回数字，失败返回 0。",
            """function requirePositive(n) {
  // 校验失败时 throw new Error(...)

}

function safePositive(n) {
  // 捕获异常并返回 0

}

console.log(safePositive(5));""",
            "requirePositive 里判断 typeof n !== 'number' || isNaN(n) || n <= 0；safePositive 用 try/catch 包住调用。",
            [
                "assert(requirePositive(5) === 5, '正数应原样返回')",
                "var ok = false;\ntry { requirePositive(0); } catch (e) { ok = e.message === 'must be a positive number'; }\nassert(ok, '0 应抛出指定消息')",
                "assert(safePositive(-3) === 0, '负数应返回 0')",
                "assert(safePositive('x') === 0, '非数字应返回 0')",
                "assert(safePositive(2.5) === 2.5, '正小数也合法')",
            ],
            """function requirePositive(n) {
  if (typeof n !== 'number' || isNaN(n) || n <= 0) {
    throw new Error('must be a positive number');
  }
  return n;
}

function safePositive(n) {
  try {
    return requirePositive(n);
  } catch (e) {
    return 0;
  }
}

console.log(safePositive(5));
console.log(safePositive(-1));""",
        ),
    )


def js16():
    return lesson(
        "js16", 315, 22, CORE_CHAPTER,
        "闭包", "函数记住它出生的地方", 100,
        [
            heading("私有状态的最小实现"),
            paragraph(
                "闭包是「函数 + 它定义时所处的词法环境」。内层函数引用了外层函数的变量，外层函数返回后，这些变量不会被回收，因为内层函数还握着引用。于是我们可以用函数创建带私有状态的对象：外部只能通过返回的方法读写状态，无法直接访问变量本身。这是模块模式、计数器、缓存、柯里化的共同基础。"
            ),
            paragraph(
                "闭包捕获的是变量本身，不是创建时的值快照。多个函数共享同一个外层变量时，一个改动另一个能看到。经典陷阱是在循环里用 var 创建回调：所有回调共享同一个 i，循环结束后都读到最终值。解决方式是用函数工厂为每次迭代创建独立作用域，或者使用 let（本运行时对 let 的迭代绑定支持不完整，优先用工厂函数）。"
            ),
            *pair(
                """function makeCounter() {
  var count = 0;
  return {
    increment: function () {
      count = count + 1;
      return count;
    },
    current: function () {
      return count;
    }
  };
}

var c1 = makeCounter();
var c2 = makeCounter();

console.log(c1.increment(), c1.increment());
console.log(c1.current());
console.log(c2.current());""",
                """1 2
2
0""",
            ),
            table(
                ["能力", "实现方式", "用途"],
                [
                    ["私有变量", "外层函数内的局部变量", "外部无法直接篡改"],
                    ["状态保持", "内层函数引用外层变量", "计数器、缓存、连接池"],
                    ["函数工厂", "外层接收参数并返回函数", "生成一族行为相似的函数"],
                    ["模块封装", "IIFE 返回公开方法", "只暴露必要接口"],
                ],
            ),
            paragraph(
                "闭包也会带来内存问题：被闭包引用的变量无法被垃圾回收。如果闭包持有大数组或大对象，又不释放，就会造成泄漏。解决办法是缩小捕获范围（只捕获需要的值）、在不再使用时把引用置空、避免在长生命周期对象上挂大量闭包。理解「谁还引用着它」，就能判断一个闭包是否该被释放。"
            ),
            tip(
                "判断闭包的最快方式：内层函数里出现了外层函数的变量名。只要它还活着，那个变量就不会消失。"
            ),
            quiz(
                "function outer() { var x = 1; return function () { return x; }; } outer()() 的结果是？",
                ["undefined", "1", "报错", "null"],
                1,
                "outer 返回的内层函数仍然引用 x，调用时读到 1。x 不会因为 outer 返回而销毁。",
            ),
            *pair(
                """function makeGreeter(greeting) {
  return function (name) {
    return greeting + ', ' + name;
  };
}

var hi = makeGreeter('hi');
var yo = makeGreeter('yo');

console.log(hi('V'));
console.log(yo('Judy'));

function makeAdders() {
  var out = [];
  for (var i = 0; i < 3; i++) {
    out.push((function (n) {
      return function () { return n; };
    })(i));
  }
  return out;
}

var adders = makeAdders();
console.log(adders[0](), adders[1](), adders[2]());""",
                """hi, V
yo, Judy
0 1 2""",
            ),
            practice(
                "私有计数",
                """function makeIdGen(prefix) {
  var n = 0;
  return function () {
    n = n + 1;
    return prefix + '-' + n;
  };
}

var next = makeIdGen('agent');
console.log(next());
console.log(next());""",
                """agent-1
agent-2""",
                "n 是外层局部变量，返回的函数每次调用都修改同一个 n。",
            ),
        ],
        exercise(
            "账户工厂",
            "实现 makeAccount(balance)：返回对象 { deposit, withdraw, balance }。deposit(n) 增加余额并返回新余额；withdraw(n) 在余额不足时返回 -1，否则扣减并返回新余额；balance() 返回当前余额。余额必须私有，外部不能直接改。",
            """function makeAccount(balance) {
  // 用闭包保存余额，返回三个方法

}

var acc = makeAccount(100);
console.log(acc.deposit(50));""",
            "var current = balance; 返回的对象方法都读写 current。withdraw 先判断 current < n。",
            [
                "var a = makeAccount(100);\nassert(a.balance() === 100, '初始余额 100')",
                "assert(a.deposit(50) === 150 && a.balance() === 150, '存款后 150')",
                "assert(a.withdraw(30) === 120, '取款后 120')",
                "assert(a.withdraw(999) === -1 && a.balance() === 120, '余额不足返回 -1 且不扣款')",
                "var b = makeAccount(0);\nassert(b.balance() === 0 && a.balance() === 120, '两个账户互不影响')",
            ],
            """function makeAccount(balance) {
  var current = balance;
  return {
    deposit: function (n) {
      current = current + n;
      return current;
    },
    withdraw: function (n) {
      if (n > current) return -1;
      current = current - n;
      return current;
    },
    balance: function () {
      return current;
    }
  };
}

var acc = makeAccount(100);
console.log(acc.deposit(50));
console.log(acc.withdraw(30));""",
        ),
    )


def js17():
    return lesson(
        "js17", 316, 22, CORE_CHAPTER,
        "高阶函数与回调", "把行为当参数传", 100,
        [
            heading("函数是值，不是语法装饰"),
            paragraph(
                "高阶函数是「接收函数作为参数」或「返回函数」的函数。JS 里函数是一等值，可以赋给变量、存进对象、作为参数传递。回调就是被传进去、稍后调用的函数。数组的 map/filter/reduce、sort 的比较器、事件处理都是高阶函数的应用。理解这一点，你就能把「变化的逻辑」抽成参数，把「稳定的流程」留在函数体里。"
            ),
            paragraph(
                "回调的常见坑是 this 和调用时机。普通函数作为回调传入时，调用方式决定了 this；箭头函数没有自己的 this，会捕获外层。回调还分同步和异步：数组方法里的回调是同步的，Promise 的 then 回调是异步的。写代码时要清楚回调会在什么时候执行，以及它执行时哪些变量已经就绪。"
            ),
            *pair(
                """function applyTwice(fn, value) {
  return fn(fn(value));
}

function compose(f, g) {
  return function (x) {
    return f(g(x));
  };
}

var inc = function (n) { return n + 1; };
var double = function (n) { return n * 2; };

console.log(applyTwice(inc, 10));
console.log(compose(inc, double)(5));""",
                """12
11""",
            ),
            table(
                ["模式", "签名", "典型用途"],
                [
                    ["回调", "run(value, callback)", "完成后通知调用方"],
                    ["函数工厂", "makeX(config) -> function", "生成定制行为"],
                    ["组合", "compose(f, g) -> function", "把多个小函数串起来"],
                    ["谓词", "fn(value) -> boolean", "filter / some / every"],
                ],
            ),
            paragraph(
                "sort 的比较器是高阶函数的经典案例：它接收 (a, b)，返回负数表示 a 在前，正数表示 b 在后，0 表示相等。按对象的某个字段排序就写 function (a, b) { return a.level - b.level; }。排序前记得复制数组，因为 sort 会原地修改。回调不要写得太长，超过五六行就该提取成具名函数，否则调用处会被噪音淹没。"
            ),
            warn(
                "把方法直接当回调传（如 arr.map(obj.format)）可能丢失 this。需要保留上下文时用 obj.format.bind(obj)，或者包一层 function (x) { return obj.format(x); }。"
            ),
            quiz(
                "compose(f, g)(3) 等价于？",
                ["f(3) + g(3)", "f(g(3))", "g(f(3))", "f(3) * g(3)"],
                1,
                "compose 的惯例是从右向左：先执行 g，再把结果交给 f。",
            ),
            *pair(
                """var people = [
  { name: 'V', level: 66 },
  { name: 'Judy', level: 42 },
  { name: 'Jackie', level: 30 }
];

var byLevel = people.slice().sort(function (a, b) {
  return a.level - b.level;
});

console.log(byLevel.map(function (p) { return p.name; }).join(' > '));

function myFilter(list, predicate) {
  var out = [];
  for (var i = 0; i < list.length; i++) {
    if (predicate(list[i], i)) out.push(list[i]);
  }
  return out;
}

console.log(myFilter([1, 2, 3, 4], function (n) { return n % 2 === 0; }).join(','));""",
                """Jackie > Judy > V
2,4""",
            ),
            practice(
                "重复执行",
                """function times(n, fn) {
  var out = [];
  for (var i = 0; i < n; i++) out.push(fn(i));
  return out;
}

console.log(times(3, function (i) { return i * i; }).join('-'));""",
                "0-1-4",
                "高阶函数把「做几次」和「每次做什么」分开。",
            ),
        ],
        exercise(
            "函数组合器",
            "实现 compose2(f, g)：返回新函数，调用时先执行 g 再执行 f。实现 mapWith(list, fn)：不调用内置 map，用循环实现同样的效果。",
            """function compose2(f, g) {
  // 返回 function (x) { ... }

}

function mapWith(list, fn) {
  // 用循环生成新数组

}

console.log(compose2(function (n) { return n + 1; }, function (n) { return n * 2; })(5));""",
            "compose2 返回 function (x) { return f(g(x)); }；mapWith 遍历 list，把 fn(list[i], i) push 进结果。",
            [
                "var f = compose2(function (n) { return n + 1; }, function (n) { return n * 2; });\nassert(f(5) === 11, '先乘 2 再加 1')",
                "assert(compose2(String, function (n) { return n + 1; })(2) === '3', '外层函数可以是内置函数')",
                "assert(JSON.stringify(mapWith([1,2,3], function (n) { return n * 10; })) === '[10,20,30]', 'mapWith 应返回新数组')",
                "assert(JSON.stringify(mapWith([], function (n) { return n; })) === '[]', '空数组返回空数组')",
            ],
            """function compose2(f, g) {
  return function (x) {
    return f(g(x));
  };
}

function mapWith(list, fn) {
  var out = [];
  for (var i = 0; i < list.length; i++) {
    out.push(fn(list[i], i));
  }
  return out;
}

console.log(compose2(function (n) { return n + 1; }, function (n) { return n * 2; })(5));
console.log(JSON.stringify(mapWith([1, 2, 3], function (n) { return n * 10; })));""",
        ),
    )


def js18():
    return lesson(
        "js18", 317, 22, CORE_CHAPTER,
        "解构赋值", "从数组和对象里拆出变量", 100,
        [
            heading("一次声明多个名字"),
            paragraph(
                "解构赋值让你按「形状」从数组或对象里取数据。数组按位置：var a = pair[0], b = pair[1] 可以写成 var [a, b] = pair。对象按键名：var name = user.name, level = user.level 可以写成 var { name, level } = user。解构只是语法糖，不会改变原数据，也不会自动深拷贝嵌套对象。"
            ),
            paragraph(
                "常见用法有三种：交换变量 [a, b] = [b, a]；函数参数直接解构 function render({ title, body })；从函数返回的多个值里按名字取。重命名用 { name: agentName }，嵌套用 { user: { name } }。本运行时支持对象和数组解构，但不支持解构中的默认值写法，需要兜底时在解构后单独判断 undefined。"
            ),
            *pair(
                """var pair = [10, 20];
var [first, second] = pair;

console.log(first, second);

var a = 1;
var b = 2;
[a, b] = [b, a];
console.log(a, b);""",
                """10 20
2 1""",
            ),
            table(
                ["写法", "含义", "结果"],
                [
                    ["var [x, y] = [1, 2]", "按位置取值", "x=1, y=2"],
                    ["var { name } = user", "按键名取值", "name = user.name"],
                    ["var { name: n } = user", "取值并重命名", "n = user.name"],
                    ["var { user: { name } } = data", "嵌套解构", "name = data.user.name"],
                    ["[a, b] = [b, a]", "交换", "两变量互换"],
                ],
            ),
            paragraph(
                "对象解构经常和函数参数配合：function greet(person) { var name = person.name; ... } 可以简化为 function greet({ name }) { ... }。这让调用方必须传对象，接口更清晰。数组解构适合「有序的多个返回值」，对象解构适合「有名字的字段」。选择哪种取决于数据本身的语义，不要为了炫技把简单代码写复杂。"
            ),
            tip(
                "解构不存在的键得到 undefined，不会报错。需要默认值时写 var name = user.name === undefined ? 'anonymous' : user.name;，本运行时不支持 { name = 'anonymous' } 这种语法。"
            ),
            quiz(
                "var { a, b } = { a: 1 }; 之后 b 的值是？",
                ["0", "null", "undefined", "报错"],
                2,
                "对象里没有 b 键，解构得到 undefined。解构不会因为缺键而抛错。",
            ),
            *pair(
                """var agent = {
  name: 'V',
  stats: { level: 66, hp: 100 },
  tags: ['netrunner', 'merc']
};

var { name, stats: { level } } = agent;
var [primary] = agent.tags;

console.log(name, level, primary);

function describe({ name, stats }) {
  return name + ':' + stats.level;
}
console.log(describe(agent));""",
                """V 66 netrunner
V:66""",
            ),
            practice(
                "函数参数解构",
                """function area({ width, height }) {
  return width * height;
}

console.log(area({ width: 3, height: 4 }));
console.log(area({ width: 5, height: 2 }));""",
                """12
10""",
                "参数位置直接写 { width, height }，调用时传对象即可。",
            ),
        ],
        exercise(
            "姓名拆分与交换",
            "实现 splitName(full)：按最后一个空格拆成 { first, last }；只有一个词时 last 为 ''；空字符串返回 { first: '', last: '' }。实现 swapPair(pair)：返回交换后的新数组，不修改原数组。",
            """function splitName(full) {
  // 用 lastIndexOf 找最后一个空格

}

function swapPair(pair) {
  // 返回 [pair[1], pair[0]]

}

console.log(JSON.stringify(splitName('Judy Alvarez')));""",
            "用 full.lastIndexOf(' ') 找位置；找不到返回 { first: full, last: '' }。swapPair 用解构交换后返回新数组。",
            [
                "assert(JSON.stringify(splitName('Judy Alvarez')) === '{\"first\":\"Judy\",\"last\":\"Alvarez\"}', '正常两段姓名')",
                "assert(JSON.stringify(splitName('V')) === '{\"first\":\"V\",\"last\":\"\"}', '单词姓名 last 为空')",
                "assert(JSON.stringify(splitName('')) === '{\"first\":\"\",\"last\":\"\"}', '空串要有兜底')",
                "var src = [1, 2];\nassert(JSON.stringify(swapPair(src)) === '[2,1]' && JSON.stringify(src) === '[1,2]', '交换结果正确且不改原数组')",
            ],
            """function splitName(full) {
  if (full === '') return { first: '', last: '' };
  var idx = full.lastIndexOf(' ');
  if (idx === -1) return { first: full, last: '' };
  var first = full.slice(0, idx);
  var last = full.slice(idx + 1);
  return { first: first, last: last };
}

function swapPair(pair) {
  var [a, b] = pair;
  return [b, a];
}

console.log(JSON.stringify(splitName('Judy Alvarez')));
console.log(JSON.stringify(swapPair([1, 2])));""",
        ),
    )


def js19():
    return lesson(
        "js19", 318, 22, CORE_CHAPTER,
        "Map 与 Set", "真正的键值容器与去重集合", 100,
        [
            heading("对象之外的两件容器"),
            paragraph(
                "普通对象的键只能是字符串或 Symbol，数字键会被转成字符串，对象键会变成 '[object Object]'。Map 解决了这个问题：键可以是任意类型，按 SameValueZero 比较（NaN 等于 NaN），并保留插入顺序。常用 API：set(k, v)、get(k)、has(k)、delete(k)、size 属性，以及 forEach 和 for-of 遍历。"
            ),
            paragraph(
                "Set 是只存唯一值的集合。new Set(array) 会自动去重，add、has、delete、size 是常用操作，遍历用 forEach 或 for-of。判断数组是否有重复元素，用 new Set(arr).size !== arr.length 一行就能完成。Set 和 Map 都是 ES6 新增，本运行时已经支持；但它们不能用 JSON.stringify 直接序列化。"
            ),
            *pair(
                """var visits = new Map();

visits.set('V', 3);
visits.set('Judy', 5);
visits.set('V', visits.get('V') + 1);

console.log(visits.get('V'));
console.log(visits.has('Jackie'));
console.log(visits.size);

var unique = new Set([3, 1, 3, 2, 1]);
console.log(unique.size);

var out = [];
unique.forEach(function (v) { out.push(v); });
console.log(out.join(','));""",
                """4
false
2
3
3,1,2""",
            ),
            table(
                ["对比项", "Object", "Map"],
                [
                    ["键类型", "字符串 / Symbol", "任意类型"],
                    ["顺序", "整数键升序，其余插入序", "严格插入顺序"],
                    ["长度", "Object.keys(obj).length", "map.size"],
                    ["原型污染", "键名可能撞上原型属性", "无此问题"],
                    ["JSON", "可直接序列化", "需要手动转数组"],
                ],
            ),
            paragraph(
                "用 Map 做频次统计比对象更安全：键是任意值时不会被转成字符串，也不会意外访问到 toString 之类的原型属性。遍历 Map 的推荐方式是 forEach(function (value, key) { ... }) 或 for (var pair of map)，其中 pair 是 [key, value] 数组。需要转成普通对象时，遍历后手动赋值，注意键最终仍会变成字符串。"
            ),
            warn(
                "Map 的 get 读取不存在的键返回 undefined，不会抛错；size 是属性不是方法，写 map.size 而不是 map.size()。"
            ),
            quiz(
                "new Set([1, 1, 2, 3, 3]).size 的结果是？",
                ["5", "3", "2", "1"],
                1,
                "Set 自动去重，剩下 1、2、3 三个元素。",
            ),
            *pair(
                """var words = ['neon', 'rain', 'neon', 'city', 'rain'];

var counts = new Map();
for (var i = 0; i < words.length; i++) {
  var w = words[i];
  if (counts.has(w)) {
    counts.set(w, counts.get(w) + 1);
  } else {
    counts.set(w, 1);
  }
}

counts.forEach(function (n, w) {
  console.log(w + '=' + n);
});""",
                """neon=2
rain=2
city=1""",
            ),
            practice(
                "数组去重",
                """var nums = [3, 1, 3, 2, 1];
var seen = new Set();
var out = [];

for (var i = 0; i < nums.length; i++) {
  if (!seen.has(nums[i])) {
    seen.add(nums[i]);
    out.push(nums[i]);
  }
}

console.log(out.join(','));""",
                "3,1,2",
                "Set 记录见过的值，数组保留首次出现的顺序。",
            ),
        ],
        exercise(
            "集合工具",
            "实现 dedupe(list)：按首次出现顺序去重并返回新数组。实现 frequency(list)：返回 Map，键是元素，值是出现次数。",
            """function dedupe(list) {
  // 用 Set 记录见过的值

}

function frequency(list) {
  // 返回 Map

}

console.log(dedupe([3, 1, 3, 2]).join(','));""",
            "dedupe 遍历 list，用 seen.has 判断；frequency 用 map.has/map.get/map.set 累加。",
            [
                "assert(JSON.stringify(dedupe([3,1,3,2,1])) === '[3,1,2]', '去重并保留首次顺序')",
                "assert(JSON.stringify(dedupe([])) === '[]', '空数组返回空数组')",
                "var m = frequency(['a','b','a']);\nassert(m.get('a') === 2 && m.get('b') === 1, '频次统计正确')",
                "assert(frequency([]).size === 0, '空数组返回空 Map')",
                "assert(dedupe([1,1,1]).length === 1, '全相同只留一个')",
            ],
            """function dedupe(list) {
  var seen = new Set();
  var out = [];
  for (var i = 0; i < list.length; i++) {
    if (!seen.has(list[i])) {
      seen.add(list[i]);
      out.push(list[i]);
    }
  }
  return out;
}

function frequency(list) {
  var counts = new Map();
  for (var i = 0; i < list.length; i++) {
    var item = list[i];
    if (counts.has(item)) counts.set(item, counts.get(item) + 1);
    else counts.set(item, 1);
  }
  return counts;
}

console.log(dedupe([3, 1, 3, 2]).join(','));
console.log(frequency(['a', 'b', 'a']).get('a'));""",
        ),
    )


def js20():
    return lesson(
        "js20", 319, 22, CORE_CHAPTER,
        "正则表达式", "test / exec / match / replace", 110,
        [
            heading("用模式描述文本"),
            paragraph(
                "正则表达式是描述字符串模式的迷你语言。字面量写法 /pattern/flags，flags 常见的有 g（全局）、i（忽略大小写）、m（多行）。最常用的四个方法：test 判断是否匹配返回布尔值；exec 返回第一个匹配及捕获组；String.match 在 g 标志下返回所有匹配；String.replace 替换匹配内容。先写最简单的模式，再逐步加约束。"
            ),
            paragraph(
                "基础元字符要熟：\\d 数字，\\w 字母数字下划线，\\s 空白，点号匹配任意字符（不含换行），^ 行首，$ 行尾。量词：星号零次或多次，加号一次或多次，问号零次或一次，{2,4} 两到四次。字符类 [abc] 表示其中之一，[^abc] 表示排除。分组用圆括号，replace 里用 $1、$2 引用捕获组。"
            ),
            *pair(
                """console.log(/^\\d{4}-\\d{2}-\\d{2}$/.test('2026-11-06'));
console.log(/^\\d{4}-\\d{2}-\\d{2}$/.test('2026-1-6'));

var m = /(\\d+)-(\\d+)/.exec('range 12-34');
console.log(m[0]);
console.log(m[1]);
console.log(m[2]);""",
                """true
false
12-34
12
34""",
            ),
            table(
                ["符号", "含义", "例子"],
                [
                    ["\\d", "数字", "\\d+ 匹配 123"],
                    ["\\w", "字母数字下划线", "\\w+ 匹配 neon_1"],
                    ["\\s", "空白", "\\s+ 匹配连续空格"],
                    ["^ $", "行首 / 行尾", "^abc$ 整行匹配"],
                    ["{n,m}", "重复次数范围", "\\d{2,4}"],
                    ["( )", "分组与捕获", "replace 中用 $1 引用"],
                ],
            ),
            paragraph(
                "正则默认只匹配第一处，需要全部匹配必须加 g 标志。test 和 exec 在带 g 的正则上会维护 lastIndex，连续调用会在字符串中向前推进，这常常导致「第一次 true 第二次 false」的困惑。需要重复判断时，要么每次新建正则，要么在调用前把 lastIndex 置 0。写复杂正则时先用简单字符串试，再逐步加规则。"
            ),
            warn(
                "不要用正则解析 HTML 或任意嵌套结构。正则适合线性、规则明确的文本；嵌套结构请用专门的解析器。"
            ),
            quiz(
                "'a1b22c'.match(/\\d+/g) 的结果是？",
                ["['1']", "['1','22']", "['1','2','2']", "null"],
                1,
                "g 标志返回所有匹配；\\d+ 会尽量连续匹配，所以是 '1' 和 '22'。",
            ),
            *pair(
                """var text = 'contact: v@night.city, backup: judy@afterlife.net';

var emails = text.match(/[\\w.]+@[\\w.]+/g);
console.log(emails.length);
console.log(emails[0]);

var masked = '13800138000'.replace(/(\\d{3})\\d{4}(\\d{4})/, '$1****$2');
console.log(masked);

console.log('a-b-c'.replace(/-/g, '/'));""",
                """2
v@night.city
138****8000
a/b/c""",
            ),
            practice(
                "校验与提取",
                """var ok = /^[a-z]+$/.test('neon');
var nums = 'x1 y22 z333'.match(/\\d+/g);

console.log(ok);
console.log(nums.join(','));""",
                """true
1,22,333""",
                "test 适合整串校验（加 ^$），match 加 g 适合提取全部片段。",
            ),
        ],
        exercise(
            "邮箱提取器",
            "实现 extractEmails(text)：返回文本中所有邮箱地址组成的数组，没有则返回空数组。实现 maskPhone(phone)：把 11 位手机号的中间四位替换成 ****，格式不匹配时原样返回。",
            """function extractEmails(text) {
  // 用 match 加 g 标志提取

}

function maskPhone(phone) {
  // 用 replace 的捕获组保留首尾

}

console.log(JSON.stringify(extractEmails('a@b.com and c@d.org')));""",
            "extractEmails 用 text.match(/[\\w.]+@[\\w.]+/g)，结果为 null 时返回 []；maskPhone 用 /^(\\d{3})\\d{4}(\\d{4})$/ 和 '$1****$2'。",
            [
                "assert(JSON.stringify(extractEmails('a@b.com and c@d.org')) === '[\"a@b.com\",\"c@d.org\"]', '提取两个邮箱')",
                "assert(JSON.stringify(extractEmails('no mail here')) === '[]', '无匹配返回空数组')",
                "assert(maskPhone('13800138000') === '138****8000', '中间四位打码')",
                "assert(maskPhone('123') === '123', '格式不符应原样返回')",
            ],
            """function extractEmails(text) {
  var found = text.match(/[\\w.]+@[\\w.]+/g);
  return found === null ? [] : found;
}

function maskPhone(phone) {
  return phone.replace(/^(\\d{3})\\d{4}(\\d{4})$/, '$1****$2');
}

console.log(JSON.stringify(extractEmails('a@b.com and c@d.org')));
console.log(maskPhone('13800138000'));""",
        ),
    )


CORE = [js11(), js12(), js13(), js14(), js15(), js16(), js17(), js18(), js19(), js20()]


# ---------------------------------------------------------------------------
# 进阶篇 js21 - js30
# ---------------------------------------------------------------------------

ADV_CHAPTER = "JavaScript · 进阶篇"


def js21():
    return lesson(
        "js21", 320, 23, ADV_CHAPTER,
        "构造函数与原型", "new 到底做了什么", 110,
        [
            heading("对象模板的第一种写法"),
            paragraph(
                "在没有 class 语法的年代（本运行时也不支持 class），JS 用构造函数创建对象模板：函数名首字母大写，内部用 this 挂属性，调用时加 new。new 做四件事：创建空对象、把它的原型指向构造函数的 prototype、以这个对象为 this 执行函数、返回这个对象（除非构造函数显式返回了一个对象）。理解这四步，this 和原型就不再神秘。"
            ),
            paragraph(
                "把方法挂在 prototype 上而不是构造函数内部，可以避免每个实例都复制一份函数。实例读取属性时先找自身，找不到就沿原型链向上查。因此 Robot.prototype.speak 是所有实例共享的，修改它会影响所有实例。判断属性是自身的还是继承的，用 hasOwnProperty；判断实例关系用 instanceof，它会沿原型链检查。"
            ),
            *pair(
                """function Robot(name, level) {
  this.name = name;
  this.level = level;
}

Robot.prototype.speak = function () {
  return 'I am ' + this.name;
};

Robot.prototype.upgrade = function () {
  this.level = this.level + 1;
  return this.level;
};

var r = new Robot('V', 66);
console.log(r.speak());
console.log(r.upgrade());
console.log(r instanceof Robot);
console.log(r.hasOwnProperty('name'), r.hasOwnProperty('speak'));""",
                """I am V
67
true
true false""",
            ),
            table(
                ["概念", "位置", "判断方式"],
                [
                    ["实例属性", "构造函数内 this.x = ...", "obj.hasOwnProperty('x')"],
                    ["共享方法", "Constructor.prototype.fn", "不是实例自身属性"],
                    ["原型对象", "Constructor.prototype", "Object.getPrototypeOf(obj)"],
                    ["实例关系", "new Constructor()", "obj instanceof Constructor"],
                ],
            ),
            paragraph(
                "两个常见错误：第一，构造函数忘记写 new，this 会指向全局对象（非严格模式），属性被挂到全局；第二，把方法写在构造函数内部，每个实例都得到一份独立函数，浪费内存且无法统一修改。约定俗成的防护是构造函数开头检查 this instanceof Robot，或者用工厂函数替代。本课程统一使用 new 并保持首字母大写。"
            ),
            warn(
                "构造函数里 return 一个对象会覆盖 new 的结果；return 基本类型则被忽略。不要依赖这个特性写业务逻辑，它只会让调用方困惑。"
            ),
            quiz(
                "new Robot('V') 之后，r.speak 这个函数来自哪里？",
                ["每个实例各有一份", "Robot.prototype", "全局对象", "Robot 函数自身"],
                1,
                "方法挂在 Robot.prototype 上，所有实例共享同一份函数，通过原型链查找到。",
            ),
            *pair(
                """function Counter(start) {
  this.value = start;
}

Counter.prototype.add = function (n) {
  this.value = this.value + n;
  return this.value;
};

var a = new Counter(0);
var b = new Counter(100);

console.log(a.add(5));
console.log(b.add(1));
console.log(a.value, b.value);

Counter.prototype.add = function (n) {
  this.value = this.value + n * 10;
  return this.value;
};
console.log(a.add(1));""",
                """5
101
5 101
15""",
            ),
            practice(
                "共享方法",
                """function Point(x, y) {
  this.x = x;
  this.y = y;
}

Point.prototype.describe = function () {
  return '(' + this.x + ',' + this.y + ')';
};

console.log(new Point(3, 4).describe());""",
                "(3,4)",
                "describe 挂在 prototype 上，实例通过原型链调用。",
            ),
        ],
        exercise(
            "坦克工厂",
            "用构造函数实现 Tank(name, hp)：实例有 name、hp 属性；prototype 上有 hit(damage) 扣血（最低 0）并返回剩余血量；isAlive() 返回 hp > 0。",
            """function Tank(name, hp) {
  // 挂实例属性

}

Tank.prototype.hit = function (damage) {
  // 扣血，最低 0

};

Tank.prototype.isAlive = function () {
  // 返回布尔值

};

var t = new Tank('V', 50);
console.log(t.hit(20));""",
            "构造函数里 this.name = name; this.hp = hp; hit 里 this.hp = Math.max(0, this.hp - damage); return this.hp;",
            [
                "var t = new Tank('V', 50);\nassert(t.name === 'V' && t.hp === 50, '实例属性正确')",
                "assert(t.hit(20) === 30, '扣血后剩 30')",
                "assert(t.hit(999) === 0 && t.isAlive() === false, '血量最低为 0')",
                "var t2 = new Tank('J', 10);\nassert(t2.hp === 10 && t.hp === 0, '实例互不影响')",
                "assert(Tank.prototype.hasOwnProperty('hit'), '方法应挂在 prototype 上')",
            ],
            """function Tank(name, hp) {
  this.name = name;
  this.hp = hp;
}

Tank.prototype.hit = function (damage) {
  this.hp = Math.max(0, this.hp - damage);
  return this.hp;
};

Tank.prototype.isAlive = function () {
  return this.hp > 0;
};

var t = new Tank('V', 50);
console.log(t.hit(20));""",
        ),
    )


def js22():
    return lesson(
        "js22", 321, 23, ADV_CHAPTER,
        "this / call / apply / bind", "调用方式决定 this", 110,
        [
            heading("this 不是声明出来的，是调用出来的"),
            paragraph(
                "this 的值由调用方式决定，而不是函数定义的位置。四种常见绑定：作为方法调用 obj.fn()，this 是 obj；普通函数调用 fn()，非严格模式下 this 是全局对象，严格模式下是 undefined；用 new 调用，this 是新创建的实例；用 call/apply/bind 显式指定，this 就是你传入的对象。箭头函数例外，它没有自己的 this，捕获定义时外层的 this。"
            ),
            paragraph(
                "call 和 apply 立即执行函数，区别只在传参方式：call(thisArg, a, b)，apply(thisArg, [a, b])。bind 不执行，返回一个绑定了 this 的新函数，还可以预设部分参数（偏函数）。把方法从对象上摘下来单独调用时，this 会丢失，这是回调场景最常见的 bug，用 bind 或箭头函数包一层即可。"
            ),
            *pair(
                """var ship = {
  name: 'Normandy',
  greet: function (pilot) {
    return this.name + ' -> ' + pilot;
  }
};

console.log(ship.greet('Joker'));

var detached = ship.greet;
console.log(detached.call({ name: 'SR2' }, 'V'));
console.log(ship.greet.apply({ name: 'SR1' }, ['Judy']));

var bound = ship.greet.bind({ name: 'Bound' }, 'Jackie');
console.log(bound());""",
                """Normandy -> Joker
SR2 -> V
SR1 -> Judy
Bound -> Jackie""",
            ),
            table(
                ["调用方式", "this 指向", "示例"],
                [
                    ["方法调用", "调用它的对象", "obj.fn()"],
                    ["普通调用", "全局 / undefined（严格）", "var f = obj.fn; f()"],
                    ["new 调用", "新实例", "new Fn()"],
                    ["call / apply", "显式传入的第一个参数", "fn.call(ctx, a)"],
                    ["bind", "固定为新函数的第一参数", "var g = fn.bind(ctx)"],
                ],
            ),
            paragraph(
                "严格模式用 'use strict' 开启，它让普通调用的 this 变成 undefined，而不是偷偷指向全局。这能尽早暴露 this 丢失的问题。另一个细节：call 传 null 或 undefined 时，非严格模式会把 this 替换成全局对象，严格模式保持原值。调试 this 问题时，先问「这个函数是怎么被调用的」，答案通常就在调用点。"
            ),
            tip(
                "偏函数：fn.bind(null, 1) 把第一个参数固定为 1，之后调用只需传剩余参数。bind 返回新函数，原函数不受影响。"
            ),
            quiz(
                "var f = obj.method; f(); 在非严格模式下，f 内部的 this 是？",
                ["obj", "undefined", "全局对象", "null"],
                2,
                "方法被摘下来单独调用，绑定丢失；非严格模式下 this 回落到全局对象。",
            ),
            *pair(
                """function sum(a, b) {
  return this.base + a + b;
}

var ctx = { base: 100 };

console.log(sum.call(ctx, 1, 2));
console.log(sum.apply(ctx, [3, 4]));

var addTen = sum.bind(ctx, 10);
console.log(addTen(5));

function Person(name) {
  this.name = name;
}
Person.prototype.say = function () {
  return 'I am ' + this.name;
};

var p = new Person('V');
var say = p.say.bind(p);
console.log(say());""",
                """103
107
115
I am V""",
            ),
            practice(
                "借用方法",
                """var stats = { values: [3, 9, 2] };

var max = Math.max.apply(null, stats.values);

console.log(max);
console.log(Math.max.apply(null, [1, 5, 4]));""",
                """9
5""",
                "apply 把数组展开成参数列表，Math.max 需要一个个数字。",
            ),
        ],
        exercise(
            "绑定工具",
            "实现 bindAll(obj, names)：names 是方法名数组，返回一个新对象，其中每个方法都绑定到 obj，单独调用也不会丢失 this。",
            """function bindAll(obj, names) {
  // 逐个 bind 后放进新对象

}

var ship = { name: 'Normandy', greet: function () { return this.name; } };
var safe = bindAll(ship, ['greet']);
var g = safe.greet;
console.log(g());""",
            "var out = {}; 遍历 names，out[name] = obj[name].bind(obj); 最后 return out。",
            [
                "var ship = { name: 'N', greet: function () { return this.name; } };\nvar safe = bindAll(ship, ['greet']);\nvar g = safe.greet;\nassert(g() === 'N', '解绑后仍能读到 this.name')",
                "var ctx = { n: 5, add: function (x) { return this.n + x; } };\nvar b = bindAll(ctx, ['add']).add;\nassert(b(3) === 8, '带参数的方法也要绑定')",
                "var o = { a: function () { return 1; }, b: function () { return 2; } };\nvar both = bindAll(o, ['a','b']);\nassert(both.a() === 1 && both.b() === 2, '多个方法一起绑定')",
                "assert(typeof bindAll({ x: function () {} }, []).x === 'undefined', '空数组返回空对象')",
            ],
            """function bindAll(obj, names) {
  var out = {};
  for (var i = 0; i < names.length; i++) {
    var key = names[i];
    out[key] = obj[key].bind(obj);
  }
  return out;
}

var ship = { name: 'Normandy', greet: function () { return this.name; } };
var safe = bindAll(ship, ['greet']);
var g = safe.greet;
console.log(g());""",
        ),
    )


def js23():
    return lesson(
        "js23", 322, 23, ADV_CHAPTER,
        "原型继承", "ES5 的 OOP 组装术", 120,
        [
            heading("把原型链接起来"),
            paragraph(
                "继承的本质是让子类的实例能访问父类原型上的方法。ES5 的标准做法分两步：子类构造函数内部调用父类构造函数（借用 this），再把子类的 prototype 设为一个以父类 prototype 为原型的空对象。第二步不能写成 Child.prototype = Parent.prototype，否则子类方法会污染父类；要写 Object.create(Parent.prototype)。"
            ),
            paragraph(
                "接好原型链后，还要修正 constructor 指向：Child.prototype.constructor = Child。否则实例的 constructor 会指向 Parent。方法覆盖时，子类可以定义同名方法，需要复用父类实现就用 Parent.prototype.method.call(this, ...)。这就是 ES5 世界里的 super。整条链路是：实例 -> 子类 prototype -> 父类 prototype -> Object.prototype -> null。"
            ),
            *pair(
                """function Unit(name, hp) {
  this.name = name;
  this.hp = hp;
}
Unit.prototype.describe = function () {
  return this.name + '(' + this.hp + ')';
};
Unit.prototype.hit = function (dmg) {
  this.hp = Math.max(0, this.hp - dmg);
  return this.hp;
};

function Ninja(name, hp, weapon) {
  Unit.call(this, name, hp);
  this.weapon = weapon;
}
Ninja.prototype = Object.create(Unit.prototype);
Ninja.prototype.constructor = Ninja;

Ninja.prototype.hit = function (dmg) {
  return Unit.prototype.hit.call(this, Math.floor(dmg / 2));
};

var n = new Ninja('K', 100, 'katana');
console.log(n.describe());
console.log(n.hit(30));
console.log(n instanceof Ninja, n instanceof Unit);""",
                """K(100)
85
true true""",
            ),
            diagram(
                """n（实例）
 └─ Ninja.prototype { hit, constructor }
     └─ Unit.prototype { describe, hit }
         └─ Object.prototype
             └─ null"""
            ),
            paragraph(
                "原型继承的坑集中在三处：忘记 Object.create 导致共享原型；忘记修正 constructor 导致 instanceof 之外的判断出错；在构造函数里忘了调用父类构造函数，导致父类属性缺失。另外，给原型加方法要在创建实例之前完成，或者接受已创建实例也能看到新方法（原型是活的，这一点其实是优势）。"
            ),
            warn(
                "不要修改内置对象的原型（如 Array.prototype），这会影响运行环境里的所有代码，属于典型的全局污染。"
            ),
            quiz(
                "Ninja.prototype = Object.create(Unit.prototype) 的作用是？",
                ["复制父类所有方法到子类", "让子类原型以父类原型为原型", "调用父类构造函数", "把子类变成父类"],
                1,
                "Object.create 创建一个新对象，并把它的原型设为参数。方法不复制，靠原型链查找。",
            ),
            *pair(
                """function Shape(kind) {
  this.kind = kind;
}
Shape.prototype.area = function () {
  return 0;
};
Shape.prototype.info = function () {
  return this.kind + ':' + this.area();
};

function Rect(w, h) {
  Shape.call(this, 'rect');
  this.w = w;
  this.h = h;
}
Rect.prototype = Object.create(Shape.prototype);
Rect.prototype.constructor = Rect;
Rect.prototype.area = function () {
  return this.w * this.h;
};

var r = new Rect(3, 4);
console.log(r.info());
console.log(r.constructor === Rect);
console.log(Shape.prototype.isPrototypeOf(r));""",
                """rect:12
true
true""",
            ),
            practice(
                "复用父类方法",
                """function Animal(name) {
  this.name = name;
}
Animal.prototype.speak = function () {
  return this.name + ' makes a sound';
};

function Dog(name) {
  Animal.call(this, name);
}
Dog.prototype = Object.create(Animal.prototype);
Dog.prototype.constructor = Dog;

console.log(new Dog('Rex').speak());""",
                "Rex makes a sound",
                "Dog 没定义 speak，沿原型链找到 Animal.prototype.speak。",
            ),
        ],
        exercise(
            "员工继承体系",
            "实现 Person(name)：有 name 属性和 describe() 返回 name。实现 Engineer(name, stack)：继承 Person，额外有 stack 属性，describe() 返回 'name [stack]'。要求 instanceof 同时成立。",
            """function Person(name) {
  // 实例属性

}
Person.prototype.describe = function () {
  // 返回 name

};

function Engineer(name, stack) {
  // 调用父类构造函数并挂 stack

}
// 接好原型链并修正 constructor

console.log(new Engineer('V', 'JS').describe());""",
            "Engineer 里 Person.call(this, name)；Engineer.prototype = Object.create(Person.prototype)；再修正 constructor；覆盖 describe。",
            [
                "var p = new Person('Judy');\nassert(p.describe() === 'Judy', 'Person.describe 返回名字')",
                "var e = new Engineer('V', 'JS');\nassert(e.describe() === 'V [JS]', 'Engineer 覆盖 describe')",
                "assert(e instanceof Engineer && e instanceof Person, '两边的 instanceof 都应成立')",
                "assert(e.constructor === Engineer, 'constructor 应修正为 Engineer')",
                "assert(Person.prototype.describe.call(e) === 'V', '父类方法仍可借用')",
            ],
            """function Person(name) {
  this.name = name;
}
Person.prototype.describe = function () {
  return this.name;
};

function Engineer(name, stack) {
  Person.call(this, name);
  this.stack = stack;
}
Engineer.prototype = Object.create(Person.prototype);
Engineer.prototype.constructor = Engineer;
Engineer.prototype.describe = function () {
  return this.name + ' [' + this.stack + ']';
};

console.log(new Engineer('V', 'JS').describe());""",
        ),
    )


def js24():
    return lesson(
        "js24", 323, 23, ADV_CHAPTER,
        "迭代器与生成器", "function* 与惰性序列", 120,
        [
            heading("可暂停的函数"),
            paragraph(
                "生成器用 function* 声明，调用它不会立即执行函数体，而是返回一个迭代器。每次调用迭代器的 next()，函数执行到下一个 yield 就暂停，并把 yield 的值包装成 { value, done } 返回。这让我们能按需生成序列，而不是一次性把整个数组造出来。无限序列在生成器里是合法的，因为值只在被请求时才计算。"
            ),
            paragraph(
                "生成器天然实现了迭代器协议：有 next 方法，返回 { value, done }。因此可以直接用 for-of 遍历，也可以配合手写迭代器。next(value) 可以把值送回生成器，作为上一个 yield 表达式的结果。return 会提前结束并设置 done。理解「暂停/恢复」模型后，生成器可以用来写状态机、分页器、树遍历。"
            ),
            *pair(
                """function* naturals() {
  var i = 0;
  while (true) {
    yield i;
    i = i + 1;
  }
}

var it = naturals();
console.log(it.next().value);
console.log(it.next().value);
console.log(it.next().value);

function* take(source, n) {
  var count = 0;
  for (var v of source) {
    if (count >= n) return;
    yield v;
    count = count + 1;
  }
}

var out = [];
for (var x of take(naturals(), 5)) {
  out.push(x);
}
console.log(out.join(','));""",
                """0
1
2
0,1,2,3,4""",
            ),
            table(
                ["成员", "作用", "示例"],
                [
                    ["function*", "声明生成器函数", "function* gen() {}"],
                    ["yield", "产出一个值并暂停", "yield i;"],
                    ["next()", "恢复执行，返回 {value, done}", "it.next()"],
                    ["return", "提前结束生成器", "return;"],
                    ["for-of", "自动消费到 done", "for (var v of gen())"],
                ],
            ),
            paragraph(
                "生成器的价值在于「惰性」和「可组合」。惰性意味着不必为用不到的数据付出内存；可组合意味着可以写 take、map、filter 这样的生成器适配器，把数据管道拆成小步骤。代价是调试稍难、每次 next 有状态开销。数据量小的时候直接返回数组更简单，不要为了用生成器而用生成器。"
            ),
            tip(
                "生成器函数调用后函数体一行都没执行，只有第一次 next() 才开始。这是判断「是不是生成器」的最快方式。"
            ),
            quiz(
                "function* g() { yield 1; yield 2; } 调用 g() 之后立即得到什么？",
                ["1", "[1, 2]", "一个迭代器对象", "undefined"],
                2,
                "生成器函数返回迭代器，函数体尚未执行；第一次 next() 才执行到第一个 yield。",
            ),
            *pair(
                """function* range(start, end) {
  for (var i = start; i < end; i++) {
    yield i;
  }
}

var values = [];
for (var n of range(2, 6)) {
  values.push(n * n);
}
console.log(values.join(' '));

function* mapGen(source, fn) {
  for (var v of source) {
    yield fn(v);
  }
}

var doubled = [];
for (var d of mapGen(range(1, 4), function (x) { return x * 2; })) {
  doubled.push(d);
}
console.log(doubled.join(','));""",
                """4 9 16 25
2,4,6""",
            ),
            practice(
                "手动取三个",
                """function* letters() {
  yield 'a';
  yield 'b';
  yield 'c';
}

var it = letters();
console.log(it.next().value);
console.log(it.next().value);
console.log(it.next().done);
console.log(it.next().done);""",
                """a
b
false
true""",
                "第三次 next 返回 c 且 done 为 false；第四次才 done 为 true。",
            ),
        ],
        exercise(
            "生成器工具",
            "实现 genRange(start, end)：生成 [start, end) 的整数。实现 takeGen(iterable, n)：返回前 n 个元素组成的数组。",
            """function* genRange(start, end) {
  // 逐个 yield

}

function takeGen(iterable, n) {
  // 用 for-of 收集前 n 个

}

console.log(takeGen(genRange(1, 10), 3).join(','));""",
            "genRange 用 for 循环 yield；takeGen 里 count 达到 n 就 break，把值 push 进数组。",
            [
                "assert(JSON.stringify(takeGen(genRange(1, 10), 3)) === '[1,2,3]', '取前 3 个')",
                "assert(JSON.stringify(takeGen(genRange(5, 6), 5)) === '[5]', '不足 n 个时全部返回')",
                "assert(JSON.stringify(takeGen(genRange(0, 0), 3)) === '[]', '空区间返回空数组')",
                "var it = genRange(2, 4);\nassert(it.next().value === 2 && it.next().value === 3 && it.next().done === true, '生成器逐个产出并结束')",
            ],
            """function* genRange(start, end) {
  for (var i = start; i < end; i++) {
    yield i;
  }
}

function takeGen(iterable, n) {
  var out = [];
  for (var v of iterable) {
    if (out.length >= n) break;
    out.push(v);
  }
  return out;
}

console.log(takeGen(genRange(1, 10), 3).join(','));""",
        ),
    )


def js25():
    return lesson(
        "js25", 324, 23, ADV_CHAPTER,
        "递归与算法", "自己调用自己的艺术", 120,
        [
            heading("把大问题拆成同构的小问题"),
            paragraph(
                "递归函数在内部调用自己，把规模为 n 的问题化成规模更小的同类问题。写递归只需要想清楚两件事：基准情形（什么时候直接返回，不再递归）和递归步骤（如何把 n 变成 n-1 或更小）。缺少基准情形会导致无限递归，最终栈溢出。递归的思维价值在于「相信子调用能正确工作」，不要试图在脑子里展开每一层。"
            ),
            paragraph(
                "递归不是免费的：每次调用都会压栈，深度过大（通常几万层）会抛 RangeError: Maximum call stack size exceeded。斐波那契的朴素递归复杂度是 O(2^n)，因为大量重复计算；用记忆化（缓存已算结果）可以降到 O(n)。尾递归在部分语言里能优化，但 JS 引擎普遍不保证，所以深递归应改成循环或显式栈。"
            ),
            *pair(
                """function factorial(n) {
  if (n <= 1) return 1;
  return n * factorial(n - 1);
}

function fib(n) {
  if (n < 2) return n;
  return fib(n - 1) + fib(n - 2);
}

console.log(factorial(5));
console.log(fib(10));

function sumTree(node) {
  if (node === null) return 0;
  return node.value + sumTree(node.left) + sumTree(node.right);
}

var tree = {
  value: 1,
  left: { value: 2, left: null, right: null },
  right: { value: 3, left: null, right: null }
};
console.log(sumTree(tree));""",
                """120
55
6""",
            ),
            table(
                ["问题", "基准情形", "递归步骤"],
                [
                    ["阶乘", "n <= 1 返回 1", "n * factorial(n-1)"],
                    ["斐波那契", "n < 2 返回 n", "fib(n-1) + fib(n-2)"],
                    ["树求和", "节点为 null 返回 0", "value + 左 + 右"],
                    ["数组求和", "空数组返回 0", "首元素 + 剩余部分"],
                ],
            ),
            paragraph(
                "记忆化递归用一个对象缓存参数到结果的映射：进入函数先查缓存，算完写回。参数必须是可稳定序列化的简单值，否则缓存键会撞。更通用的做法是把缓存放在闭包里，避免污染全局。递归和迭代可以互相转换：任何递归都能用显式栈模拟，但代码通常更长；选择的标准是清晰度和深度。"
            ),
            warn(
                "递归函数一定要先写基准情形，再写递归步骤。只写递归步骤的代码在运行时才会暴露问题，而且往往以栈溢出的形式出现。"
            ),
            quiz(
                "朴素递归 fib(30) 很慢，主要原因是？",
                ["函数调用开销大", "重复计算大量子问题", "数字太大溢出", "缺少基准情形"],
                1,
                "fib(n-1) 和 fib(n-2) 会重复计算同一批子问题，复杂度指数级。记忆化可以消除重复。",
            ),
            *pair(
                """function fibMemo(n, memo) {
  if (memo === undefined) memo = {};
  if (memo[n] !== undefined) return memo[n];
  if (n < 2) return n;
  memo[n] = fibMemo(n - 1, memo) + fibMemo(n - 2, memo);
  return memo[n];
}

console.log(fibMemo(10));
console.log(fibMemo(40));

function flatten(list) {
  var out = [];
  for (var i = 0; i < list.length; i++) {
    if (Array.isArray(list[i])) {
      var inner = flatten(list[i]);
      for (var j = 0; j < inner.length; j++) out.push(inner[j]);
    } else {
      out.push(list[i]);
    }
  }
  return out;
}
console.log(flatten([1, [2, [3, 4]], 5]).join(','));""",
                """55
102334155
1,2,3,4,5""",
            ),
            practice(
                "递归求和",
                """function sum(list) {
  if (list.length === 0) return 0;
  return list[0] + sum(list.slice(1));
}

console.log(sum([1, 2, 3, 4]));
console.log(sum([]));""",
                """10
0""",
                "基准情形是空数组；递归步骤取首元素，剩下的交给子调用。",
            ),
        ],
        exercise(
            "递归工具箱",
            "实现 power(base, exp)：用递归计算 base 的 exp 次方（exp 为非负整数，0 次方返回 1）。实现 countDown(n)：返回从 n 到 0 的数组，n 小于 0 返回空数组。",
            """function power(base, exp) {
  // 基准情形 exp === 0

}

function countDown(n) {
  // 递归拼接

}

console.log(power(2, 10));
console.log(countDown(3).join(','));""",
            "power: if (exp === 0) return 1; return base * power(base, exp - 1); countDown: if (n < 0) return []; return [n].concat(countDown(n - 1));",
            [
                "assert(power(2, 10) === 1024, '2 的 10 次方')",
                "assert(power(5, 0) === 1, '0 次方返回 1')",
                "assert(power(3, 4) === 81, '3 的 4 次方')",
                "assert(JSON.stringify(countDown(3)) === '[3,2,1,0]', '倒计时包含 0')",
                "assert(JSON.stringify(countDown(-1)) === '[]', '负数返回空数组')",
            ],
            """function power(base, exp) {
  if (exp === 0) return 1;
  return base * power(base, exp - 1);
}

function countDown(n) {
  if (n < 0) return [];
  return [n].concat(countDown(n - 1));
}

console.log(power(2, 10));
console.log(countDown(3).join(','));""",
        ),
    )


def js26():
    return lesson(
        "js26", 325, 23, ADV_CHAPTER,
        "IIFE 与模块模式", "用函数造一个封闭宇宙", 110,
        [
            heading("立即执行函数表达式"),
            paragraph(
                "IIFE（Immediately Invoked Function Expression）是定义后立刻执行的函数：(function () { ... })(); 外层括号把函数声明变成表达式，后面的括号立即调用它。它创建了一个独立作用域，内部的变量不会泄漏到全局。在模块系统出现之前，这是 JS 隔离代码的主要手段，至今仍用于初始化、避免全局污染和创建单例。"
            ),
            paragraph(
                "模块模式在 IIFE 基础上增加「公开接口」：内部保留私有变量和函数，返回一个对象，只暴露必要的方法。外部拿不到私有状态，只能通过公开方法操作。这就是闭包的实际应用。现代项目用 ES Modules（import/export），但本运行时和很多老代码库仍依赖 IIFE，理解它对读旧代码非常重要。"
            ),
            *pair(
                """var counterModule = (function () {
  var count = 0;

  function increase() {
    count = count + 1;
    return count;
  }

  function reset() {
    count = 0;
    return count;
  }

  return {
    increase: increase,
    reset: reset,
    current: function () { return count; }
  };
})();

console.log(counterModule.increase());
console.log(counterModule.increase());
console.log(counterModule.current());
console.log(typeof counterModule.count);""",
                """1
2
2
undefined""",
            ),
            table(
                ["写法", "作用域", "典型用途"],
                [
                    ["(function () {})()", "独立函数作用域", "初始化、隔离变量"],
                    ["模块模式", "IIFE + 返回对象", "私有状态 + 公开 API"],
                    ["命名空间对象", "单个全局对象挂方法", "旧式库的组织方式"],
                    ["ES Module", "文件级作用域", "现代项目的标准"],
                ],
            ),
            paragraph(
                "IIFE 的参数可以用来注入依赖： (function (window, undefined) { ... })(window) 这种写法在旧库里很常见，好处是内部引用更短，也能防止 undefined 被外部改写。本课程不需要这么极端，但可以借鉴「显式传入依赖」的思路：把外部依赖作为参数传进去，模块的可测试性会更好。"
            ),
            tip(
                "如果 IIFE 前一行没有分号，JS 可能把上一行的表达式和它连起来解析。习惯上在 IIFE 前加分号，或者统一给每行语句写分号。"
            ),
            quiz(
                "IIFE 的主要作用是？",
                ["让函数执行得更快", "创建独立作用域，避免污染全局", "把函数变成对象", "实现异步"],
                1,
                "IIFE 立即执行并形成封闭作用域，内部变量外部不可见。",
            ),
            *pair(
                """var config = (function () {
  var secret = 'offline-mode';

  function get(key) {
    if (key === 'mode') return secret;
    return null;
  }

  function set(key, value) {
    if (key === 'mode') secret = value;
  }

  return { get: get, set: set };
})();

console.log(config.get('mode'));
config.set('mode', 'online');
console.log(config.get('mode'));
console.log(typeof config.secret);""",
                """offline-mode
online
undefined""",
            ),
            practice(
                "一次性初始化",
                """var boot = (function () {
  var started = true;
  return {
    started: function () { return started; },
    stop: function () { started = false; }
  };
})();

console.log(boot.started());
boot.stop();
console.log(boot.started());""",
                """true
false""",
                "started 被闭包保存，只能通过返回的方法读写。",
            ),
        ],
        exercise(
            "模块化计数器",
            "实现 createStore(initial)：用闭包保存一个值，返回 { get, set, add }。get() 读值；set(v) 覆盖并返回值；add(n) 累加并返回新值。initial 缺省时按 0 处理。",
            """function createStore(initial) {
  // 用 IIFE 或普通闭包都可以

}

var store = createStore(10);
console.log(store.add(5));""",
            "var value = initial === undefined ? 0 : initial; 返回三个方法，全部读写 value。",
            [
                "var s = createStore(10);\nassert(s.get() === 10, '初始值 10')",
                "assert(s.add(5) === 15 && s.get() === 15, 'add 累加并返回新值')",
                "assert(s.set(0) === 0 && s.get() === 0, 'set 覆盖')",
                "var d = createStore();\nassert(d.get() === 0, '缺省初始值为 0')",
                "assert(typeof s.value === 'undefined', '内部值不应暴露')",
            ],
            """function createStore(initial) {
  var value = initial === undefined ? 0 : initial;
  return {
    get: function () { return value; },
    set: function (v) { value = v; return value; },
    add: function (n) { value = value + n; return value; }
  };
}

var store = createStore(10);
console.log(store.add(5));""",
        ),
    )


def js27():
    return lesson(
        "js27", 326, 23, ADV_CHAPTER,
        "不可变数据与纯函数", "让变化可控", 120,
        [
            heading("同样的输入，永远同样的输出"),
            paragraph(
                "纯函数满足两个条件：相同的输入永远返回相同的输出；不修改外部状态、不产生可观察的副作用。Math.max、数组的 slice、字符串方法都是纯的；push、sort、Math.random、console.log 不是。纯函数容易测试、容易推理、可以安全缓存，是函数式编程的基石。把业务计算写成纯函数，把读写外部世界的操作推到边界，代码会稳定得多。"
            ),
            paragraph(
                "不可变数据指「不修改原对象，而是返回带改动的新对象」。JS 没有内置的持久化数据结构，但可以用浅复制加覆盖实现：var next = Object.assign({}, state, { level: 67 })；数组用 slice 复制后修改，或者用 concat、map、filter 生成新数组。嵌套结构要逐层复制，否则内层仍是共享引用。"
            ),
            *pair(
                """var state = { level: 66, hp: 100 };

var up = Object.assign({}, state, { level: 67 });
var hurt = Object.assign({}, state, { hp: 80 });

console.log(state.level, up.level);
console.log(state.hp, hurt.hp);
console.log(state === up);""",
                """66 67
100 80
false""",
            ),
            table(
                ["操作", "可变写法", "不可变写法"],
                [
                    ["改对象字段", "obj.x = 1", "Object.assign({}, obj, {x:1})"],
                    ["追加数组", "arr.push(x)", "arr.concat([x])"],
                    ["删除字段", "delete obj.x", "复制后不写入该键"],
                    ["排序", "arr.sort()", "arr.slice().sort()"],
                    ["更新嵌套", "obj.a.b = 1", "逐层复制"],
                ],
            ),
            paragraph(
                "不可变的代价是内存和写法啰嗦。Object.assign 只做浅复制，嵌套对象仍然共享；真正的深更新要写辅助函数，沿路径逐层复制。判断是否值得：状态被多方共享、需要撤销/重做、需要比较前后差异时，不可变收益很大；局部临时计算则没必要教条。关键是「谁拥有这份数据、谁有权修改」要有明确约定。"
            ),
            warn(
                "Object.freeze 是浅冻结，嵌套对象仍可修改。它也不能阻止数组元素被重新赋值，除非逐层冻结。不要把它当成深度不可变方案。"
            ),
            quiz(
                "var b = Object.assign({}, a); b.x = 9; 之后 a.x 会变吗？",
                ["会，因为共享引用", "不会，b 是新对象", "取决于 x 的类型", "报错"],
                1,
                "Object.assign 把 a 的可枚举属性复制到新对象，b.x 修改的是新对象的属性，a 不受影响。",
            ),
            *pair(
                """var cart = [
  { name: 'chip', price: 10 },
  { name: 'cell', price: 25 }
];

function addItem(items, item) {
  return items.concat([item]);
}

function total(items) {
  return items.reduce(function (sum, it) { return sum + it.price; }, 0);
}

var bigger = addItem(cart, { name: 'deck', price: 100 });

console.log(cart.length, bigger.length);
console.log(total(cart), total(bigger));

function applyDamage(state, dmg) {
  return Object.assign({}, state, {
    hp: Math.max(0, state.hp - dmg)
  });
}

var s1 = { hp: 100 };
var s2 = applyDamage(s1, 30);
console.log(s1.hp, s2.hp);""",
                """2 3
35 135
100 70""",
            ),
            practice(
                "不修改原数组",
                """var base = [3, 1, 2];

var sorted = base.slice().sort(function (a, b) { return a - b; });
var added = base.concat([4]);

console.log(base.join(','), sorted.join(','), added.join(','));""",
                """3,1,2 1,2,3 3,1,2,4""",
                "slice 复制后排序；concat 生成新数组，base 始终不变。",
            ),
        ],
        exercise(
            "不可变更新",
            "实现 updateScore(state, delta)：返回新对象，score 增加 delta，其余字段不变，原对象不能被修改。实现 addTag(state, tag)：返回新对象，tags 是追加 tag 后的新数组，原 state 与 tags 都不能被修改。",
            """function updateScore(state, delta) {
  // 用 Object.assign 生成新对象

}

function addTag(state, tag) {
  // tags 也要生成新数组

}

var s = { score: 10, tags: ['a'] };
console.log(updateScore(s, 5).score);""",
            "updateScore: Object.assign({}, state, { score: state.score + delta }); addTag 再额外传 { tags: state.tags.concat([tag]) }。",
            [
                "var s = { score: 10, tags: ['a'] };\nassert(updateScore(s, 5).score === 15 && s.score === 10, '新对象变化，原对象不变')",
                "var s2 = { score: 1, extra: 'keep' };\nassert(updateScore(s2, 2).extra === 'keep', '其余字段应保留')",
                "var t = addTag({ tags: ['a'] }, 'b');\nassert(JSON.stringify(t.tags) === '[\"a\",\"b\"]', 'tags 应追加')",
                "assert(t !== null && JSON.stringify(t.tags) === '[\"a\",\"b\"]' && t.tags.length === 2, '返回新 tags')",
            ],
            """function updateScore(state, delta) {
  return Object.assign({}, state, { score: state.score + delta });
}

function addTag(state, tag) {
  return Object.assign({}, state, { tags: state.tags.concat([tag]) });
}

var s = { score: 10, tags: ['a'] };
console.log(updateScore(s, 5).score);
console.log(JSON.stringify(addTag(s, 'b').tags));""",
        ),
    )


def js28():
    return lesson(
        "js28", 327, 23, ADV_CHAPTER,
        "Promise 概念与链式", "同步调度下的 then / catch / all", 130,
        [
            heading("一个代表未来结果的对象"),
            paragraph(
                "Promise 是一个占位对象，代表「现在还没有、将来会有的结果」。它有三种状态：pending（进行中）、fulfilled（成功）、rejected（失败），状态只能从 pending 变一次，之后不可逆。用 new Promise(function (resolve, reject) { ... }) 创建，成功调 resolve(value)，失败调 reject(error)。then 注册成功回调，catch 注册失败回调。"
            ),
            paragraph(
                "then 返回一个新的 Promise，因此可以链式调用：每个 then 的回调返回值会成为下一个 then 的输入；如果回调抛出异常，链条转入 rejected，由后面的 catch 接住。这就是 Promise 解决「回调地狱」的方式——把嵌套改成扁平的链。注意 then 的回调总是异步执行（微任务队列），所以它不会阻塞当前同步代码。"
            ),
            *pair(
                """var p = new Promise(function (resolve, reject) {
  resolve(7);
});

p.then(function (v) {
  console.log('got', v);
  return v + 1;
}).then(function (v) {
  console.log('next', v);
})['catch'](function (e) {
  console.log('error', e.message);
});

console.log('sync first');""",
                """sync first
got 7
next 8""",
            ),
            table(
                ["成员", "作用", "返回"],
                [
                    ["new Promise(executor)", "创建 Promise，executor 立即执行", "Promise 实例"],
                    ["then(onFulfilled)", "注册成功回调", "新 Promise"],
                    ["catch(onRejected)", "注册失败回调", "新 Promise"],
                    ["Promise.resolve(v)", "创建已成功的 Promise", "Promise"],
                    ["Promise.reject(e)", "创建已失败的 Promise", "Promise"],
                    ["Promise.all(list)", "等全部成功", "结果数组的 Promise"],
                ],
            ),
            paragraph(
                "本运行时（Rhino）的 Promise 是同步调度的：then 回调会在当前代码跑完后、同一轮里执行，不依赖事件循环。因此上面的输出里 sync first 先出现，随后才是 got 和 next。这与其他环境的微任务时序略有差异，但链式语义、错误传播、返回值传递完全一致。课程里的示例不依赖精确的微任务时序，只依赖「同步代码先跑、回调后跑」。"
            ),
            warn(
                "Promise 一旦创建就会立即执行 executor，无法取消。不要在里面做不可回滚的副作用；需要惰性执行时包成函数，调用时再 new Promise。"
            ),
            quiz(
                "then 回调里 return 5 之后，下一个 then 收到什么？",
                ["undefined", "5", "原来的 Promise", "报错"],
                1,
                "then 的返回值会成为下一个 then 的输入；如果返回 Promise，还会等它 resolve。",
            ),
            *pair(
                """Promise.resolve(2)
  .then(function (v) { return v * 3; })
  .then(function (v) { return v + 4; })
  .then(function (v) { console.log('result', v); });""",
                "result 10",
            ),
            practice(
                "错误恢复链",
                """Promise.reject(new Error('denied'))
  .then(function () { console.log('never'); })
  ['catch'](function (e) { return 'recovered:' + e.message; })
  .then(function (v) { console.log(v); });""",
                "recovered:denied",
                "catch 的回调返回普通值时，链条重新变成成功状态。",
            ),
            practice(
                "并行汇合",
                """Promise.all([Promise.resolve('a'), Promise.resolve('b')])
  .then(function (list) { console.log('all', list.join('')); });""",
                "all ab",
                "Promise.all 等全部成功，结果顺序与输入顺序一致。",
            ),
            practice(
                "错误恢复",
                """Promise.reject(new Error('boom'))
  .then(function () { return 'skipped'; })
  ['catch'](function (e) {
    return 'recovered:' + e.message;
  })
  .then(function (v) { console.log(v); });""",
                "recovered:boom",
                "catch 的回调返回普通值时，链条重新变成成功状态，后续 then 会执行。",
            ),
        ],
        exercise(
            "Promise 工具集",
            "实现 delayedValue(v)：返回一个立即 resolve 为 v 的 Promise。实现 chainDouble(p)：返回新 Promise，p 成功后把结果乘 2，失败则原样传递错误。",
            """function delayedValue(v) {
  // 返回已成功的 Promise

}

function chainDouble(p) {
  // 用 then 转换，错误自动透传

}

chainDouble(delayedValue(5)).then(function (v) { console.log(v); });""",
            "delayedValue 用 Promise.resolve(v)；chainDouble 用 p.then(function (v) { return v * 2; })。",
            [
                "var seen = null;\ndelayedValue(7).then(function (v) { seen = v; });\nassert(seen === null, 'then 回调不应同步执行')",
                "assert(seen === 7, '上一次判题结束后回调应已执行')",
                "var out = null;\nchainDouble(Promise.resolve(5)).then(function (v) { out = v; });\nassert(out === null, '链式回调不应同步执行')",
                "assert(out === 10, '上一次判题结束后结果应已翻倍')",
                "assert(typeof chainDouble(Promise.resolve(1)).then === 'function', '应返回 Promise')",
            ],
            """function delayedValue(v) {
  return Promise.resolve(v);
}

function chainDouble(p) {
  return p.then(function (v) {
    return v * 2;
  });
}

chainDouble(delayedValue(5)).then(function (v) { console.log(v); });""",
        ),
    )


def js29():
    return lesson(
        "js29", 328, 23, ADV_CHAPTER,
        "性能与复杂度", "让代码跑得聪明", 120,
        [
            heading("先量，再优化"),
            paragraph(
                "性能优化最常见的错误是凭直觉改代码。正确顺序是：先确认瓶颈在哪（测量），再判断算法复杂度是否合理，最后才做常数级优化。复杂度描述输入规模 n 增长时工作量如何增长：O(1) 常数、O(log n) 对数、O(n) 线性、O(n log n)、O(n^2) 平方。n 翻倍时，O(n) 的工作量翻倍，O(n^2) 翻四倍。"
            ),
            paragraph(
                "JS 里最常见的性能陷阱是嵌套循环里的线性查找。判断数组是否包含某元素，includes/indexOf 是 O(n)，放进循环就变成 O(n^2)。换成 Set 或 Map 的 has 是平均 O(1)，整体降到 O(n)。另一个陷阱是在循环里反复计算不变的 length 或拼接大字符串；前者影响很小，后者在旧引擎里是 O(n^2)，现代引擎有优化但仍建议用数组收集后 join。"
            ),
            *pair(
                """function hasDuplicateSlow(list) {
  for (var i = 0; i < list.length; i++) {
    for (var j = i + 1; j < list.length; j++) {
      if (list[i] === list[j]) return true;
    }
  }
  return false;
}

function hasDuplicateFast(list) {
  var seen = new Set();
  for (var i = 0; i < list.length; i++) {
    if (seen.has(list[i])) return true;
    seen.add(list[i]);
  }
  return false;
}

var data = [3, 9, 1, 7, 9];
console.log(hasDuplicateSlow(data));
console.log(hasDuplicateFast(data));""",
                """true
true""",
            ),
            table(
                ["复杂度", "n=10", "n=1000", "典型场景"],
                [
                    ["O(1)", "1", "1", "对象/Map 取值"],
                    ["O(log n)", "约 3", "约 10", "二分查找"],
                    ["O(n)", "10", "1000", "一次遍历"],
                    ["O(n log n)", "约 33", "约 10000", "高效排序"],
                    ["O(n^2)", "100", "1000000", "双重循环"],
                ],
            ),
            paragraph(
                "测量用 Date 取毫秒时间戳，跑足够多的次数取平均，避免单次抖动。不要用 console.time，本运行时不一定提供。测量时注意「热身」：第一次执行包含解析和缓存预热，通常比后续慢。比较两个实现要在相同数据、相同环境下跑，否则数字没有意义。优化后必须重跑测试，确认行为没变。"
            ),
            tip(
                "先让代码正确，再让它清晰，最后才让它快。三者冲突时，可读性通常比微优化更值钱，除非测量证明这里是热点。"
            ),
            quiz(
                "在长度 1000 的数组里用嵌套循环查重，比较次数大约是多少？",
                ["1000", "10000", "500000", "1000000"],
                2,
                "内层从 i+1 开始，总比较次数是 n(n-1)/2，约 50 万次，属于 O(n^2)。",
            ),
            *pair(
                """function sumLoop(n) {
  var total = 0;
  for (var i = 1; i <= n; i++) total = total + i;
  return total;
}

function sumFormula(n) {
  return n * (n + 1) / 2;
}

console.log(sumLoop(100));
console.log(sumFormula(100));
console.log(sumLoop(100) === sumFormula(100));

var start = new Date().getTime();
var acc = 0;
for (var k = 0; k < 2000; k++) acc = acc + sumLoop(200);
var cost = new Date().getTime() - start;
console.log('loop cost ms >= 0:', cost >= 0);""",
                """5050
5050
true
loop cost ms >= 0: true""",
            ),
            practice(
                "用空间换时间",
                """var prices = { chip: 10, cell: 25, deck: 100 };
var wanted = ['chip', 'deck', 'missing'];

var out = [];
for (var i = 0; i < wanted.length; i++) {
  if (wanted[i] in prices) out.push(prices[wanted[i]]);
}

console.log(out.join(','));""",
                "10,100",
                "对象查找是 O(1)，比每次遍历价格列表快得多。",
            ),
        ],
        exercise(
            "两数之和",
            "实现 twoSum(nums, target)：返回两个下标组成的数组，使对应元素之和为 target；不存在返回 null。要求用 Map 做一次遍历，时间复杂度 O(n)。",
            """function twoSum(nums, target) {
  // 边遍历边记录「还差多少」

}

console.log(JSON.stringify(twoSum([2, 7, 11, 15], 9)));""",
            "遍历时先算 diff = target - nums[i]，若 Map 里有 diff 就返回 [map.get(diff), i]，否则 map.set(nums[i], i)。",
            [
                "assert(JSON.stringify(twoSum([2,7,11,15], 9)) === '[0,1]', '经典样例')",
                "assert(JSON.stringify(twoSum([3,2,4], 6)) === '[1,2]', '答案在后半段')",
                "assert(twoSum([1,2], 100) === null, '无解返回 null')",
                "assert(JSON.stringify(twoSum([3,3], 6)) === '[0,1]', '重复元素也要处理')",
            ],
            """function twoSum(nums, target) {
  var seen = new Map();
  for (var i = 0; i < nums.length; i++) {
    var diff = target - nums[i];
    if (seen.has(diff)) return [seen.get(diff), i];
    seen.set(nums[i], i);
  }
  return null;
}

console.log(JSON.stringify(twoSum([2, 7, 11, 15], 9)));""",
        ),
    )


def js30():
    return lesson(
        "js30", 329, 23, ADV_CHAPTER,
        "综合项目：文本冒险", "状态机 + 命令解析 + 状态更新", 150,
        [
            heading("把三十讲拧成一个作品"),
            paragraph(
                "最后这一讲做一个纯文本冒险游戏。核心是一个有限状态机：state 记录当前位置、背包、已访问房间；命令解析器把 'go north'、'take key' 这样的输入拆成动词和宾语；reducer 是纯函数，接收旧状态和命令，返回新状态；渲染器把状态转成文字。所有逻辑都在内存里，不依赖 DOM、文件或网络。"
            ),
            paragraph(
                "设计上有三个关键决定：第一，状态不可变，每次命令都返回新对象，方便回放和调试；第二，房间表用对象索引，房间之间用出口名字连接；第三，未知命令和非法移动返回带提示的新状态，而不是抛错，游戏循环永远能继续。这套「数据 + 纯函数 + 小解析器」的结构，可以直接迁移到工作流引擎、表单校验器等场景。"
            ),
            *pair(
                """var rooms = {
  hall: { desc: '大厅', exits: { north: 'lab' }, items: [] },
  lab: { desc: '实验室', exits: { south: 'hall' }, items: ['key'] }
};

var start = { at: 'hall', bag: [], log: [] };

function step(state, command) {
  var parts = command.split(' ');
  var verb = parts[0];
  var arg = parts[1];
  var room = rooms[state.at];
  var next = Object.assign({}, state, { log: state.log.concat([command]) });

  if (verb === 'look') {
    return Object.assign(next, { message: room.desc + ' / ' + room.items.join(',') });
  }
  if (verb === 'go') {
    var dest = room.exits[arg];
    if (!dest) return Object.assign(next, { message: 'no exit: ' + arg });
    return Object.assign(next, { at: dest, message: 'moved to ' + dest });
  }
  if (verb === 'take') {
    var idx = room.items.indexOf(arg);
    if (idx === -1) return Object.assign(next, { message: 'not here: ' + arg });
    var items = room.items.slice();
    items.splice(idx, 1);
    rooms[state.at] = Object.assign({}, room, { items: items });
    return Object.assign(next, { bag: state.bag.concat([arg]), message: 'took ' + arg });
  }
  return Object.assign(next, { message: 'unknown: ' + verb });
}

var s1 = step(start, 'look');
console.log(s1.message);
var s2 = step(s1, 'go north');
console.log(s2.message, s2.at);
var s3 = step(s2, 'take key');
console.log(s3.message, s3.bag.join(','));
var s4 = step(s3, 'go west');
console.log(s4.message, s4.at);""",
                """大厅 /
moved to lab lab
took key key
no exit: west lab""",
            ),
            table(
                ["模块", "职责", "输入到输出"],
                [
                    ["状态 state", "保存位置、背包、日志", "不可变对象"],
                    ["解析器 parse", "拆分动词与宾语", "'go north' -> ['go','north']"],
                    ["reducer step", "根据命令产生新状态", "(state, cmd) -> state"],
                    ["渲染 render", "把状态转成可读文本", "state -> string"],
                ],
            ),
            paragraph(
                "把这段代码继续扩展的方向：给房间加锁和钥匙、给物品加使用效果、加战斗回合、把命令表做成对象映射而不是 if 链。每次扩展都遵守同一个原则：只加数据和纯函数，不改游戏循环。这样即使功能变多，复杂度也是线性增长，而不是互相纠缠。测试时直接断言 step 的返回值，不需要模拟输入输出。"
            ),
            warn(
                "示例里为了演示简洁直接改了 rooms 这个模块级数据。真实项目应把房间表也放进 state 或作为只读配置传入，避免隐式共享状态破坏「纯函数」承诺。"
            ),
            quiz(
                "reducer 风格的核心特征是？",
                ["直接修改传入的 state", "返回新 state，不修改旧 state", "必须用 class 实现", "必须异步"],
                1,
                "reducer 是纯函数：(state, action) => newState，旧 state 保持不变，便于追踪和回放。",
            ),
            *pair(
                """function makeGame() {
  var rooms = {
    hall: { desc: 'hall', exits: { north: 'lab' }, items: [] },
    lab: { desc: 'lab', exits: { south: 'hall' }, items: ['key'] }
  };
  var state = { at: 'hall', bag: [], moves: 0 };

  function step(cmd) {
    var parts = cmd.split(' ');
    var room = rooms[state.at];
    var next = Object.assign({}, state, { moves: state.moves + 1 });
    if (parts[0] === 'go') {
      if (!room.exits[parts[1]]) return { ok: false, state: next };
      state = Object.assign(next, { at: room.exits[parts[1]] });
      return { ok: true, state: state };
    }
    return { ok: false, state: next };
  }

  return { step: step, state: function () { return state; } };
}

var game = makeGame();
console.log(game.step('go north').ok);
console.log(game.step('go west').ok);
console.log(game.state().at);""",
                """true
false
lab""",
            ),
            task("给示例加一个 'inventory' 命令，打印背包内容；再加一个 'drop' 命令，把物品放回当前房间。"),
        ],
        exercise(
            "状态机冒险",
            "实现 makeAdventure()：返回 { run(cmd), state() }。初始在 hall，出口 north 通往 lab，lab 里有 key。run 支持 look（返回当前房间描述）、go <dir>（合法则移动）、take key（在 lab 时拿到钥匙）、其他命令返回 'unknown'。每次 run 返回一条消息字符串，state() 返回 { at, bag }。",
            """function makeAdventure() {
  // 房间表、状态、命令处理

}

var game = makeAdventure();
console.log(game.run('look'));
console.log(game.run('go north'));""",
            "用闭包保存 state；run 里用 cmd.split(' ') 取动词和参数；go 查 exits，take 检查当前房间和 key。",
            [
                "var g = makeAdventure();\nassert(g.run('look') === 'hall', '初始房间是 hall')",
                "assert(g.run('go north') === 'moved to lab' && g.state().at === 'lab', '向北进入 lab')",
                "assert(g.run('take key') === 'took key' && g.state().bag.join(',') === 'key', '可以拿钥匙')",
                "assert(g.run('go west') === 'unknown' && g.state().at === 'lab', '非法出口不移动')",
                "assert(g.run('dance') === 'unknown', '未知命令返回 unknown')",
            ],
            """function makeAdventure() {
  var rooms = {
    hall: { exits: { north: 'lab' } },
    lab: { exits: { south: 'hall' }, items: ['key'] }
  };
  var state = { at: 'hall', bag: [] };

  function run(cmd) {
    var parts = cmd.split(' ');
    var verb = parts[0];
    var arg = parts[1];
    if (verb === 'look') return state.at;
    if (verb === 'go') {
      var dest = rooms[state.at].exits[arg];
      if (!dest) return 'unknown';
      state.at = dest;
      return 'moved to ' + dest;
    }
    if (verb === 'take') {
      var items = rooms[state.at].items || [];
      if (items.indexOf(arg) === -1) return 'unknown';
      state.bag = state.bag.concat([arg]);
      rooms[state.at].items = items.filter(function (x) { return x !== arg; });
      return 'took ' + arg;
    }
    return 'unknown';
  }

  return { run: run, state: function () { return state; } };
}

var game = makeAdventure();
console.log(game.run('look'));
console.log(game.run('go north'));""",
        ),
    )


ADVANCED = [
    js21(), js22(), js23(), js24(), js25(),
    js26(), js27(), js28(), js29(), js30(),
]


# ---------------------------------------------------------------------------
# 正文扩写：把每讲的讲解补到 900 汉字以上（追加到三段 text 之后）
# ---------------------------------------------------------------------------

ENRICH = {
    "js01": (
        "初学者常把「写出来」当成「跑过了」。真正可靠的流程是：先预测输出，再运行对照，不一致就逐行缩小范围。预测错了不是坏事，那正是你发现自己理解偏差的时刻。控制台里的报错通常包含行号和错误类型，先读第一行，再读行号，最后才看堆栈。",
        "语句和表达式要分清：表达式产生一个值，语句执行一个动作。var x = 1 + 2; 整体是语句，右边的 1 + 2 是表达式。函数调用既是表达式也可以单独成句。分号不是装饰，它标记语句结束；省略分号时引擎按规则自动插入，遇到以括号或方括号开头的下一行就可能误判。",
        "console.log 打印对象时，本运行时会先做字符串转换，直接打印往往只看到 [object Object]，看不清内部结构。想观察对象就用 JSON.stringify(obj)，想观察多个值就用逗号分隔并加标签。输出是给你自己看的证据，写得越清楚，后面排查越省时间。",
    ),
    "js02": (
        "undefined 和 null 都表示「没有」，但来源不同：undefined 是引擎给的默认值，变量声明未赋值、函数没有返回值、访问不存在的属性都会得到它；null 是程序员主动写的空值，表示「这里刻意留空」。比较时用 === 区分，序列化时两者都会被 JSON 变成 null，这是数据交换时要注意的失真。",
        "数字只有一个 number 类型，底层是 64 位浮点。0.1 + 0.2 得到 0.30000000000000004，不是 JS 的 bug，而是二进制无法精确表示这些小数。涉及金额时用整数分做单位，或者把结果 toFixed 后再转数字。安全整数范围是 ±2^53，超过后精度会悄悄丢失。",
        "命名是类型之外的另一层可读性：变量用名词，函数用动词，常量全大写加下划线。不要用 data、temp、value 这类含糊名字，它们会在几天后让你重新读一遍代码。声明时尽量一行一个，别写 var a = 1, b = 2 这种紧凑写法，调试时不好定位。",
    ),
    "js03": (
        "加号是唯一同时承担加法与拼接的运算符，所以它的行为取决于两边的类型。减号、乘号、除号、取余没有拼接语义，一律先转数字。想确认结果类型，用 typeof 打印出来；想显式转换，用 Number、String、Boolean 三个函数，别依赖隐式规则。",
        "逻辑运算符返回的不一定是布尔值：a || b 在 a 为真时返回 a 本身，否则返回 b；a && b 在 a 为假时返回 a，否则返回 b。这个特性常被用来写默认值，比如 name || 'anonymous'，但它会把 0 和空串也当成缺失。需要精确判断 undefined 时，老老实实写三元表达式。",
        "运算符优先级决定表达式的分组：乘除高于加减，比较高于逻辑，赋值最低。记不住就用括号，括号不会让代码变慢，只会让人一眼看懂。混合使用 && 和 || 时尤其要加括号，否则读代码的人需要停下来查优先级表。",
    ),
    "js04": (
        "字符串的长度按 UTF-16 码元计算，一个汉字通常算一个码元，但 emoji 等增补字符算两个。所以 s.length 不总是「人眼看到的字符数」。做中文文本处理时这通常没问题，做用户输入限制时要意识到这个差异，必要时用 Array.from(s).length 按码点计数。",
        "slice 与 substring 的区别：slice 接受负索引，substring 会把负数当 0，还会自动交换两个参数的位置。日常统一用 slice，行为最可预测。replace 只替换第一处，全部替换要加 g 标志或用 split/join。字符串比较用 ===，不要用 ==，也不要用 localeCompare 处理简单相等。",
        "模板字符串里的表达式可以是任意合法表达式，包括函数调用和三元运算，但不能写 if 语句或 var 声明。需要复杂逻辑时先在外部算好变量，再嵌进去。模板字符串保留换行和缩进，生成多行文本很方便，但也会把缩进带进结果，必要时用 trim 清理。",
    ),
    "js05": (
        "守卫语句（guard clause）是写分支的推荐姿势：先处理异常输入并 return，主逻辑就不再被层层 else 包裹。这样函数的正常路径保持在最外层，读代码时不用在脑子里维护「现在在哪个 else 里」。嵌套超过三层，基本就该拆函数了。",
        "switch 用 === 比较，case 的值必须是常量表达式。忘记 break 会继续执行下一个 case，这叫 fallthrough，有时被故意用来合并多个条件，但更多时候是 bug。default 不是必须的，但建议写上，至少能处理意外输入。对象映射是 switch 的常见替代：把值当键、函数当值，查表即调用。",
        "边界值要专门测：等于阈值、刚好小于、刚好大于、空值、非数字。成绩分级这类逻辑，错误往往出在 90 到底算 A 还是 S。写完条件后拿三组数在纸上走一遍，比运行十次随机数据更有效。",
    ),
    "js06": (
        "循环不变式是理解循环的工具：每一轮开始时，某个条件始终成立。求最大值时不变式是「best 是已遍历元素中的最大值」；求和时是「total 是已遍历元素之和」。写循环前先说出不变式，初始化、循环体、返回值就都有了依据。",
        "for-in 遍历的是键名，不是值。对数组使用 for-in 会得到字符串下标，还可能遍历到原型上的可枚举属性，因此数组遍历不要用 for-in，用经典 for 或 for-of。对象遍历可以用 for-in，但更推荐 Object.keys 配合普通 for，顺序和边界都更可控。",
        "死循环的常见原因：条件永远为真、循环变量没有更新、浮点数步进永远到不了终点。调试时在循环体里打印计数器和关键变量，跑几轮就能看出问题。生产代码里给循环加最大次数保护，是便宜又有效的防线。",
    ),
    "js07": (
        "数组是对象的一种，typeof [] 返回 'object'，判断数组要用 Array.isArray。数组的 length 可读可写：把 length 设小会截断，设大会产生空洞（空位），空洞参与遍历时表现为 undefined。除非刻意为之，不要手动改 length，用 push/pop/splice 更清晰。",
        "二维数组是「数组的数组」，访问用 grid[row][col]。创建时不要用 new Array(3).fill([])，因为 fill 填进去的是同一个数组引用，改一行会影响所有行；应写循环，每次 push 一个新数组。这个坑在矩阵、棋盘、动态规划里非常常见。",
        "数组方法分两类：修改自身的（push/pop/shift/unshift/splice/sort/reverse）和返回新数组的（slice/concat/map/filter）。函数参数传数组时，默认是引用传递，函数内部 push 会影响调用方。需要保护原数据就开头 slice() 复制一份，成本很低。",
    ),
    "js08": (
        "对象是引用类型：var b = a 不会复制对象，只是让 b 指向同一块内存。改 b.x 等于改 a.x。需要独立副本时用 Object.assign({}, a) 做浅复制，或 JSON.parse(JSON.stringify(a)) 做深复制。浅复制的「浅」指只复制第一层，嵌套对象仍然共享。",
        "访问属性时，点号后面必须跟合法标识符；键名含空格、以数字开头、或是变量时，必须用中括号。中括号里的表达式会先求值再转字符串，所以 obj[key] 是动态访问的标准写法。读取不存在的属性返回 undefined，但读取 undefined 的属性会抛 TypeError，链式访问前要确认中间值存在。",
        "Object.keys 只返回自身可枚举属性，不含原型上的方法；for-in 会连原型上的可枚举属性一起遍历。需要完整复制时用 Object.assign，它也只复制自身可枚举属性。理解「自身」和「继承」的边界，才能解释为什么有些属性打印不出来。",
    ),
    "js09": (
        "函数的 length 属性表示声明时的形参个数，不包含 rest 参数；arguments.length 表示实际传入的实参个数。两者可以不同。ES6 之后推荐用 rest 参数代替 arguments，因为 rest 得到真正的数组，可以直接用 map/filter，而 arguments 是类数组对象。",
        "函数声明会被整体提升，函数表达式不会。把函数赋给变量时，变量声明提升但赋值不提升，所以在赋值前调用会得到 TypeError: not a function。团队协作时统一用函数声明写顶层工具函数，用函数表达式写回调和局部逻辑，可以减少这类时序问题。",
        "返回值决定函数的可用性。只打印不返回的函数难以组合，也难以测试；返回值的函数可以被断言、被缓存、被传给下一个函数。写函数时先问「调用方需要什么」，把结果 return 出去，把展示留给最外层。",
    ),
    "js10": (
        "全局变量是事故的温床：任何函数都能改它，任何脚本都能覆盖它。浏览器里 var 声明的顶层变量会挂到 window 上，Node 里模块作用域稍好一些，但污染依然危险。把代码包进函数或 IIFE，是控制影响范围最直接的办法。",
        "遮蔽（shadowing）指内层声明了同名变量，外层变量在内层不可见。适度遮蔽能让变量名贴近上下文，过度遮蔽会让人误以为在改外层变量。遇到「为什么改了没生效」，先检查是不是声明了一个新的同名变量。",
        "严格模式 'use strict' 会禁止未声明赋值、禁止删除变量、让普通调用的 this 变成 undefined。它把一批静默失败变成显式报错，是现代代码的默认姿势。本运行时的脚本默认非严格，你可以在函数或文件开头手动加上这行字符串。",
    ),
    "js11": (
        "回调的参数不止一个：map 和 filter 回调用 (value, index, array)，reduce 用 (accumulator, value, index, array)。需要下标时直接用第二个参数，不必在外层再声明计数器。回调里不要修改原数组，否则后续元素的行为会变得难以预测。",
        "链式调用有顺序成本：filter 先执行会减少后续 map 的元素数量，通常更划算；反过来先 map 再 filter 会多做无用功。把开销大的操作尽量往后放，是简单有效的优化。每一步都返回新数组，原数据始终不变。",
        "reduce 能表达 map 和 filter 能表达的一切，但可读性不一定更好。求最大值、分组、扁平化这类「折叠」场景用 reduce 很自然；只是变形或筛选就用 map/filter。工具的选择标准是让读代码的人一眼看懂意图，而不是炫技。",
    ),
    "js12": (
        "处理用户输入的标准顺序：先 trim 去掉首尾空白，再统一大小写，再按分隔符切分，最后过滤空片段。顺序错了会留下空串或大小写不一致的键。写清洗函数时把这些步骤固定成流水线，调用方就不必每次重复。",
        "replace 的第二个参数可以是函数，参数依次是匹配内容、捕获组、位置、原字符串。用函数可以做条件替换、大小写转换、模板填充。返回 undefined 时保留原匹配，返回其他值则替换。这个能力比字符串替换强得多，值得单独练几次。",
        "字符串拼接在循环里用 += 在旧引擎是 O(n^2)，现代引擎有优化但依然不如数组收集后 join。生成长文本、日志、HTML 片段时，push 到数组再 join('') 是稳妥写法。可读性上，模板字符串适合短文本，数组 join 适合大量片段。",
    ),
    "js13": (
        "JSON 只支持有限的值类型，所以序列化是有损的：Date 变字符串，undefined 和函数消失，NaN 变 null，循环引用直接报错。发送数据前先确认接收方能接受这些转换，必要时手动把 Date 转成时间戳、把 undefined 换成 null。",
        "JSON.stringify 的第二个参数是 replacer，可以是函数或字段数组；第三个参数控制缩进。调试时用 2 个空格缩进，输出立刻可读。JSON.parse 的第二个参数是 reviver，可以在还原时把日期字符串转回 Date，适合处理固定格式的配置。",
        "解析外部 JSON 时，除了语法错误，还要校验结构：字段是否存在、类型是否正确、数组长度是否合理。语法合法不代表数据可用。把校验写成独立的纯函数，解析与校验分开，错误信息就能精确指出是哪一层出了问题。",
    ),
    "js14": (
        "浮点数比较不要用 ===，0.1 + 0.2 === 0.3 是 false。判断两个小数是否相等，看差值是否小于一个极小值（如 1e-9）。金额计算用整数分，或者引入定点数库；在本课程的环境里，用 Math.round 保留两位再比较就够用了。",
        "Math.round 对负数的行为容易记错：Math.round(-2.5) 是 -2，不是 -3，因为它向 +∞ 方向取整。需要真正的四舍五入到指定小数位，用 Number(x.toFixed(2))，但要注意 toFixed 也有浮点误差。取整族方法先用几个正负样例试一遍再下结论。",
        "Date 的 getDay 返回 0 到 6，0 是星期日；getMonth 返回 0 到 11。做日历、排班、周期计算时，这两个偏移必须记牢。跨月跨年用时间戳相减最稳，不要手动加 30 天，月份长度和闰年会让结果出错。",
    ),
    "js15": (
        "错误对象的核心字段是 name 和 message。内置错误类型包括 Error、TypeError、RangeError、SyntaxError、ReferenceError，按语义选择能让调用方更容易判断。自定义错误继承 Error 后，记得设置 name，否则打印出来仍是 Error。",
        "catch 的参数在旧代码里常写成 e 或 err，名字不重要，重要的是不要忽略它。处理时至少做三件事之一：记录上下文、转换成用户能懂的提示、重新抛出。空 catch 等于告诉后来的人「这里出过问题，但我不关心」，这是维护噩梦。",
        "错误信息要包含「做了什么、期望什么、实际得到什么」。'invalid input' 是无用信息，'age must be a number, got string' 才能定位。错误信息是给未来的自己看的文档，值得多花十秒写清楚。",
    ),
    "js16": (
        "闭包让「函数携带状态」成为可能，但状态是隐藏的，调试时看不到。需要观察内部值时，提供一个 debug 或 snapshot 方法，把关键变量暴露成只读副本。不要为了调试直接把私有变量挂到返回对象上，那会破坏封装。",
        "模块模式是闭包最实用的形态：内部维护状态和辅助函数，只返回公开 API。它的缺点是每个模块一份闭包，无法被 Tree-shaking 分析；现代项目用 ES Modules 更好。但读旧代码、写单文件脚本时，模块模式依然是最轻的隔离手段。",
        "柯里化（currying）把多参数函数拆成一系列单参数函数：add(1)(2)(3)。它依赖闭包保存已传入的参数，适合做配置固定的工具函数。不要为了柯里化而柯里化，参数少、调用点固定时，普通函数更直观。",
    ),
    "js17": (
        "高阶函数的价值是「把变化点参数化」。同一个流程，排序规则、过滤条件、转换方式都可以作为函数传入，流程本身只写一次。这就是策略模式在函数层面的表达。识别出代码里「只有一小段不同」的地方，就是抽取高阶函数的时机。",
        "回调的同步/异步属性必须清楚：数组方法的回调在当前调用栈同步执行，Promise 的 then 回调在微任务里执行。把异步回调当成同步用，会得到 undefined；把同步回调包成 Promise，又会让简单逻辑复杂化。先确认回调何时执行，再决定怎么写。",
        "sort 的比较器必须满足：a 在前返回负数，b 在前返回正数，相等返回 0。返回布尔值（a > b）在部分引擎能跑，但语义错误，结果不稳定。排序对象时先取字段再比较，字段可能是字符串时要考虑 localeCompare 或统一大小写。",
    ),
    "js18": (
        "解构是「按形状取值」的语法，不改变原数据。对象解构的键必须与属性名一致，除非用冒号重命名；数组解构按位置，跳过的位置用逗号占位，如 var [, second] = pair。嵌套解构让深层字段一步取出，但层次太深会降低可读性。",
        "函数参数解构让接口自解释：function create({ name, level }) 一眼能看出需要哪些字段。调用方传对象时顺序无关，扩展字段也方便。缺点是参数不能省略，调用时必须传一个对象；需要可选参数时，在函数内部判断 undefined 并给默认值。",
        "本运行时不支持解构默认值和 rest 解构，写代码时要避开 var { a = 1 } = obj 和 var [a, ...rest] = arr。需要默认值就解构后判断 undefined，需要剩余元素就用 slice。知道运行时的边界，比记住一堆语法糖更重要。",
    ),
    "js19": (
        "Map 和 Set 的比较规则是 SameValueZero：NaN 等于 NaN，+0 等于 -0，对象按引用比较。这意味着两个内容相同的对象是不同的键。需要按内容做键时，先序列化成字符串，或者自己维护一个 id。",
        "Map 的遍历顺序是插入顺序，Set 也是。需要稳定输出时这是优点；需要排序时先转数组再 sort。Map 不能直接 JSON.stringify，转普通对象时键会变成字符串，转数组用 Array.from 或手动 push。",
        "选择容器：需要字符串键、要序列化、字段固定，用普通对象；需要任意类型键、频繁增删、关心顺序，用 Map；需要去重或集合运算，用 Set。三者不是替代关系，而是各有适用场景。",
    ),
    "js20": (
        "量词默认是贪婪的，会尽量多匹配；在量词后加问号变成懒惰，尽量少匹配。写提取标签、引号内容时，贪婪模式常常一口吞掉太多字符。调试正则时先把模式拆成小段，逐段用 test 验证，再组合起来。",
        "字符类里的大部分元字符失去特殊含义，但 ]、\\、^、- 仍需转义。点号不匹配换行，跨行匹配要用 [\\s\\S] 或 s 标志（本运行时支持有限）。锚点 ^ 和 $ 默认匹配整串首尾，加 m 标志后才匹配每行首尾。",
        "正则不是越复杂越好。一个几十字符的模式如果没有注释，三个月后没人敢改。把复杂正则拆成常量、加注释、配一组测试用例，是让它可维护的唯一办法。对于结构化数据，解析器永远比正则可靠。",
    ),
    "js21": (
        "new 的四步可以手动模拟：var obj = Object.create(Robot.prototype); Robot.call(obj, 'V'); 得到的 obj 与 new Robot('V') 结构一致。理解这一点，就能解释为什么构造函数里的 this 指向实例，以及为什么方法要挂 prototype。",
        "原型链的终点是 Object.prototype，再往上就是 null。访问属性时引擎沿链查找，找到就返回，找不到返回 undefined。原型链越长，查找越慢，但通常可以忽略；真正的问题是链太深导致理解成本上升。继承层次控制在两三层以内。",
        "工厂函数是构造函数的替代：function makeRobot(name) { return { name: name, speak: function () {...} }; }。它不需要 new，也不会出现忘记 new 的问题，但每个实例各有一份方法。构造函数加 prototype 更适合需要共享方法、需要 instanceof 判断的场景。",
    ),
    "js22": (
        "this 的绑定优先级：new 调用最高，其次 call/apply/bind，再次方法调用，最后普通调用。箭头函数不参与这套规则，它直接捕获外层 this。判断 this 时按优先级从高到低套，基本不会错。",
        "把方法作为回调传递时，this 丢失是最常见的 bug。三种修复方式：bind 绑定、箭头函数包一层、调用处用 obj.method() 形式。bind 返回新函数，适合需要反复调用的场景；箭头函数每次创建新函数，适合一次性回调。",
        "call 和 apply 的区别只在参数形式，性能差异可以忽略。apply 的经典用法是把数组展开给 Math.max/min，或者借用数组方法处理类数组对象。bind 除了绑定 this，还能预设参数，形成偏函数，这是函数式编程的常用技巧。",
    ),
    "js23": (
        "继承设置的三行模板要背下来：Child.prototype = Object.create(Parent.prototype); Child.prototype.constructor = Child; 构造函数里 Parent.call(this, ...)。少任何一行都会留下隐患：不接原型就没有继承，不修 constructor 就判断错类型，不调父构造函数就缺属性。",
        "方法覆盖时想复用父类实现，用 Parent.prototype.method.call(this, args)。直接写 this.method() 会递归调用自己。覆盖的方法签名应与父类一致，返回值语义也要一致，否则调用方按父类契约使用时会出现意外。",
        "组合优于继承：如果两个类只是共享一部分行为，用 mixin 或把共享逻辑抽成独立函数，比硬套继承层级更灵活。继承表达「是一种」，组合表达「有一个」，大多数业务场景其实是后者。",
    ),
    "js24": (
        "生成器的执行是惰性的：调用生成器函数只创建迭代器，函数体一行都不执行；第一次 next 才运行到第一个 yield。这个特性让「无限序列」变得可行，因为值只在被请求时计算。需要多少取多少，不会撑爆内存。",
        "next(value) 可以把值送回生成器，作为上一个 yield 表达式的结果，形成双向通信；这也是 async/await 的底层机制之一（本运行时不支持 async）。return 会提前结束生成器，done 变为 true，后续 next 都返回 undefined。",
        "生成器适合：分页拉取、树结构遍历、无限序列、状态机。不适合：简单数组处理、需要随机访问、需要多次遍历同一序列（生成器只能消费一次）。选型时先问「数据要不要重复读」，答案是否就用数组。",
    ),
    "js25": (
        "递归的思考方式是数学归纳法：证明基准情形成立，假设 n-1 成立，证明 n 也成立。写代码时只写这两步，不要试图在脑中展开整个调用树。调试递归时打印深度和参数，能快速看出是哪一层没有收敛。",
        "递归深度受调用栈限制，浏览器和 Node 通常在几千到几万层。树遍历、深拷贝这类天然递归的问题，如果数据可能很深，要改成显式栈的迭代写法。显式栈用数组 push/pop 模拟调用栈，代码长但不会栈溢出。",
        "记忆化是递归优化的第一把刀：用对象缓存参数到结果的映射。缓存键要能唯一标识参数，多个参数时拼接字符串或嵌套 Map。缓存放在闭包里避免全局污染。斐波那契、爬楼梯、路径计数都是记忆化的经典题。",
    ),
    "js26": (
        "IIFE 的本质是「函数表达式 + 立即调用」。外层括号不能省，否则解析器把 function 当成声明，声明后面直接跟括号会报语法错误。箭头函数也可以 IIFE：(() => { ... })()，但箭头函数没有 arguments，需要时用普通函数。",
        "模块模式的三要素：私有状态、公开方法、单一实例。返回对象里的方法共享同一份闭包状态，因此天然是单例。需要多个实例时，把 IIFE 改成工厂函数，每次调用创建独立闭包。两者结构相同，只是执行时机不同。",
        "IIFE 前加分号是防御性写法：如果上一个文件最后一行没有分号，下一行以 ( 开头会被解析成函数调用。现代构建工具会处理拼接，但手写脚本、书签脚本、嵌入式代码仍要注意。统一写分号最省心。",
    ),
    "js27": (
        "不可变更新的关键是「沿路径复制」：改嵌套字段时，从根到目标路径上的每个对象都要新建，其他分支保持共享。这样既避免了深拷贝的性能开销，又保证了新旧状态互不影响。手写辅助函数时，先复制再覆盖，顺序不能反。",
        "纯函数不等于「不调用其他函数」，而是不依赖外部可变状态、不产生副作用。读取全局配置算不算纯？如果配置在运行期不变，可以视为常量；如果会变，就不是纯函数。判断标准是「同样输入是否永远同样输出」。",
        "不可变数据让时间旅行调试成为可能：保存每次的状态快照，就能回放任意一步。它也让 React 这类 UI 框架的更新判断变简单：引用变了就重渲染。代价是内存和写法，适合状态复杂、共享频繁的场景。",
    ),
    "js28": (
        "Promise 的三种状态只能转换一次：pending 到 fulfilled 或 rejected，之后不可再变。resolve 一个 Promise 会等待它完成，这叫「状态吸收」。理解这一点，才能解释为什么 then 里返回 Promise 可以继续链式等待。",
        "错误传播是 Promise 的核心优势：链上任何一环抛错或返回 rejected，都会跳过后续的 then，直到遇到 catch。catch 本身返回新 Promise，回调返回值会让链恢复成功状态。把 catch 放在链尾，或者在每个可能失败的环节局部处理，按业务需要选择。",
        "本运行时没有事件循环意义上的宏任务，Promise 回调在脚本执行完后同步清空。所以「先注册后执行」的顺序仍然成立，但不要依赖精确的微任务时序写业务逻辑。判题时测试会在下一个脚本里看到回调结果，这已经足够验证链式语义。",
    ),
    "js29": (
        "复杂度分析看的是增长趋势，不是绝对耗时。O(n) 的算法在小数据上可能比 O(n^2) 慢，因为常数因子不同；但 n 增大后，趋势决定胜负。优化前先确认 n 的量级，几百条数据用嵌套循环完全没问题，几万条才需要换结构。",
        "空间换时间是常用手段：Set/Map 把查找从 O(n) 降到 O(1)，缓存把重复计算变成一次计算，索引把排序后的查询变快。代价是内存占用，内存紧张时要权衡。测量内存可以用运行时提供的接口，或者粗略看数据规模。",
        "字符串拼接、数组 push、对象属性增删在大数据量下都有成本。批量操作时尽量一次成型：数组先收集再 join，对象先构造再赋值。微优化只有在你确认它是热点后才值得做，否则只是给代码增加噪音。",
    ),
    "js30": (
        "状态机的关键是「状态 + 事件 -> 新状态」的映射表。把每个命令的处理写成独立函数，主循环只负责解析和分发，新增功能时改表不改循环。这样代码的复杂度随功能线性增长，而不是指数爆炸。",
        "解析器要宽容：多余空格、大小写、未知命令都不应该让程序崩溃。先 trim、转小写、按空格切分，再查命令表；查不到就返回提示。游戏循环永远继续，玩家才有继续探索的欲望。真实系统里，宽容解析同样重要。",
        "测试状态机不需要模拟输入输出：直接构造初始状态，调用 step，断言返回的新状态。纯函数让测试变得简单，也让回放和撤销成为可能。把这条原则用到业务代码里，你会发现大部分逻辑都可以脱离界面独立验证。",
    ),
}


def consolidate_paragraphs(packs):
    """把补充段落按原顺序合并为 3 段正文，段内保留空行分隔。"""
    for lessons in packs:
        for lesson in lessons:
            blocks = lesson["blocks"]
            texts = [b for b in blocks if b["type"] == "text"]
            if len(texts) <= 3:
                continue
            third = (len(texts) + 2) // 3
            groups = [texts[0:third], texts[third:third * 2], texts[third * 2:]]
            merged = []
            for group in groups:
                if not group:
                    continue
                merged.append({
                    "type": "text",
                    "text": "\n\n".join(b["text"] for b in group),
                })
            first_index = blocks.index(texts[0])
            lesson["blocks"] = [b for b in blocks if b["type"] != "text"]
            for offset, block in enumerate(merged):
                lesson["blocks"].insert(first_index + offset, block)


def dedupe_sentences(packs):
    """删除同一讲正文里完全重复的句子，保留首次出现。"""
    import re as _re

    splitter = _re.compile(r"[^。！？]*[。！？]|[^。！？]+$")
    for lessons in packs:
        for lesson in lessons:
            seen = set()
            for block in lesson["blocks"]:
                if block["type"] != "text":
                    continue
                paragraphs = []
                for para in block["text"].split("\n\n"):
                    kept = []
                    for sent in splitter.findall(para):
                        key = sent.strip()
                        if len(key) > 18 and key in seen:
                            continue
                        seen.add(key)
                        kept.append(sent)
                    paragraphs.append("".join(kept))
                block["text"] = "\n\n".join(p for p in paragraphs if p.strip())


def apply_enrichment(packs):
    for lessons in packs:
        for lesson in lessons:
            extra = ENRICH.get(lesson["id"])
            if not extra:
                continue
            text_blocks = [b for b in lesson["blocks"] if b["type"] == "text"]
            for block, addition in zip(text_blocks, extra):
                block["text"] = block["text"] + addition

# ---------------------------------------------------------------------------
# 第二段扩写：每讲再补一段原理/实践说明，使正文达到 900 汉字以上
# ---------------------------------------------------------------------------

EXTRA = {
    "js01": "运行环境决定了你能用什么。本课程跑在一个精简的 JS 引擎里，只有语言核心：没有浏览器、没有网络、没有文件系统。这看起来是限制，其实是好事——你可以把全部注意力放在语言本身。等语法和思维打牢，再迁移到浏览器或 Node，只是多学几组 API 而已。调试的第一步永远是让程序说话：在关键位置打印变量的值和类型，确认它和你的预期一致，再继续往下走。当输出和预期不符时，把范围缩小到最小的一段代码，逐行删除直到现象消失，最后删掉的那行通常就是原因。这个「二分定位」的方法比盯着屏幕猜要快得多。",
    "js02": "类型转换分为显式和隐式。显式转换是你主动调用 Number、String、Boolean，意图清楚；隐式转换是运算符或比较自动做的，容易埋雷。写代码时尽量把转换写在明面上，让读代码的人不需要背规则。还有一个常被忽略的点：变量提升与暂时性死区。var 声明的变量在声明前访问得到 undefined，因为它被提升到作用域顶部；标准 JS 里 let 和 const 在声明前访问会报错（暂时性死区），但本课程的 Rhino 运行时在脚本顶层会把它们处理得接近 var，读到 undefined。无论实现如何，先声明后使用都能避开这类差异。把声明写在作用域开头，代码的阅读顺序和执行顺序就一致了。",
    "js03": "运算符的短路特性值得单独记：a && b 在 a 为假时直接返回 a，不再计算 b；a || b 在 a 为真时直接返回 a。这意味着右边的表达式可能根本不会执行。把函数调用放在右边时要注意，副作用可能被跳过。利用这个特性可以写默认值和守卫，但不要在一行里塞太多逻辑。类型转换还有一个高频场景：表单输入。用户在输入框里敲的所有内容都是字符串，'0' 是真值，Number('0') 才是数字 0。判断「有没有填写」和判断「数值是多少」是两件事，混在一起就会出 bug。",
    "js04": "字符串方法大多返回新值，原字符串不变。这个规则适用于 toUpperCase、slice、replace、trim、padStart 等所有「看起来像修改」的方法。理解这一点，链式调用就不会写错顺序。另一个实用技巧是用 split 和 join 做批量替换：把旧分隔符切开，再用新分隔符拼起来。它按字面量匹配，不会像正则那样被特殊字符干扰。处理中文时注意 length 与视觉字符数的差异，做字数限制、截断显示时最好按码点处理。最后，字符串比较区分大小写，'A' 和 'a' 不相等；需要忽略大小写时先统一转换，再比较。",
    "js05": "条件表达式里的真值判断是很多 bug 的来源。空字符串、0、NaN 都是假值，但 '0' 和 [] 是真值。判断「有没有值」和判断「数值是否为零」必须分开写。分支顺序也很关键：范围判断从大到小或从小到大都可以，但必须覆盖所有情况，并且边界不重叠。写完后用边界值、中间值、非法值各测一次，基本就能发现漏洞。switch 适合枚举型的分发，if 适合区间和复合条件，三元表达式适合二选一的简单赋值。不要用三元表达式嵌套多层，那不是简洁，是加密。",
    "js06": "循环的边界最容易被忽略：从 0 开始还是从 1 开始，条件是小于还是小于等于，步进是加一还是加二。写完后用最小规模（0 个、1 个元素）验证，往往能立刻发现问题。遍历数组时缓存 length 在旧引擎能略微提速，但现代引擎优化后差别很小，可读性优先。需要提前退出时用 break 或 return，不要用修改循环变量的方式硬拗。嵌套循环的复杂度是乘积关系，数据量大时要考虑用 Map 或 Set 把内层查找降为常数时间，这就是后面性能课要讲的「空间换时间」。",
    "js07": "数组的很多方法都有「原地修改」和「返回新数组」两派，混用是 bug 温床。一个简单原则：函数参数里的数组默认当作只读，需要修改就先复制。复制用 slice() 或 concat([])，浅复制足够应付大多数场景。多维数组要逐层复制，否则内层仍共享。判断元素是否存在，indexOf 返回下标、includes 返回布尔值，两者对 NaN 的处理不同：includes 能找到 NaN，indexOf 不能。删除元素时，delete 只留空洞不改变长度，splice 才真正移除。",
    "js08": "对象是 JS 的核心数据结构，几乎所有复杂数据都用它表达。写对象时键名尽量用有意义的英文单词，避免拼音和缩写。嵌套层次控制在三层以内，太深的结构应该拆成多个对象或改用扁平结构加 id 引用。遍历对象时，Object.keys 返回自身可枚举键，for-in 还会遍历原型链上的可枚举属性，两者在继承场景下结果不同。需要完整复制时注意浅复制只复制第一层，嵌套对象仍然共享。判断两个对象是否相等，=== 比较的是引用，内容相等要自己逐字段比较或序列化后比较。",
    "js09": "函数是代码复用和抽象的基本单位。写函数前先想清楚输入、输出和副作用：输入是参数，输出是返回值，副作用是打印、修改外部变量、读写文件等。理想的函数只有输入和输出，副作用集中在外层。参数设计上，超过三个就考虑改传对象，调用处可读性更好，也方便以后扩展。返回值要稳定：同一个函数不要有时返回数字、有时返回 null、有时返回 undefined，调用方会疯掉。函数名用动词开头，见名知意，比写注释更有效。",
    "js10": "作用域链是在函数定义时确定的，不是调用时。这解释了为什么闭包能记住外层变量，也解释了为什么在哪个函数里调用不影响变量的查找顺序。变量查找从当前作用域开始，逐层向外，直到全局；找不到就抛 ReferenceError，而不是返回 undefined。区分「变量未声明」和「变量已声明但值为 undefined」很重要：前者报错，后者可以安全比较。把变量声明在离使用最近的地方，作用域最小，命名冲突最少，调试也最容易。",
    "js11": "map、filter、reduce 的共同点是「不修改原数组」，但它们都不是魔法：内部依然是一次遍历，只是把循环的细节藏了起来。理解回调收到的参数，就能写出更灵活的处理。比如 map 的第二个参数是下标，filter 的第二个参数也是下标，reduce 的第三个参数是当前下标。需要提前终止遍历时，map 和 filter 做不到，只能用 some、every 或普通循环。选择方法时先问「我要的是变形、筛选还是一个汇总值」，答案会直接指向对应的方法。",
    "js12": "字符串处理的难点不在方法本身，而在边界情况：空串、只有空格、连续分隔符、超长文本、非 ASCII 字符。写清洗函数时，先列出所有可能出现的脏数据形态，再逐一处理。trim 只能去掉首尾空白，中间的连续空格要 split 后过滤。大小写转换对中文没有影响，但对用户名、邮箱、标签这类英文内容很重要，统一转小写能避免「V 和 v 是两个用户」的问题。替换时注意特殊字符，普通字符串替换不会触发正则，但正则替换要转义。",
    "js13": "JSON 是数据交换的通用语言，但它不是 JS 的子集。JSON 的键必须双引号，字符串必须双引号，不允许注释和尾逗号，数字不能是 NaN 或 Infinity。写配置文件时要遵守这些规则，否则解析会失败。序列化时，对象里的 undefined、函数、Symbol 会被丢弃，数组里的会变成 null，日期会变成 ISO 字符串。需要保留类型信息时，约定一个 type 字段，或者用自定义的序列化函数。解析后先校验再使用，永远不要相信外部输入的结构。",
    "js14": "Math 的方法都是静态的，直接 Math.xxx 调用，不需要实例。取整的四个方法各有用途：floor 向下、ceil 向上、round 四舍五入、trunc 向零截断。负数时 round 和 trunc 的结果不同，做财务计算要特别小心。Date 的构造有多种形式：无参数取当前时间，传时间戳，传年月日时分秒，传 ISO 字符串。不同形式受时区影响，跨时区系统统一用 UTC 方法。格式化输出自己拼字符串最可控，不要依赖本地化方法的默认格式。",
    "js15": "错误处理的目标不是「让程序不报错」，而是「让失败可预期、可恢复、可诊断」。可预期的失败用返回值表达（比如查找不到返回 null），真正的异常才用 throw。异常会打断正常控制流，滥用会让代码难以跟踪。catch 里要区分「能处理的」和「不能处理的」：能处理就恢复或返回兜底值，不能处理就补充上下文后重新抛出。finally 用于释放资源、恢复状态，不管成功失败都要执行。写错误信息时包含关键参数，比一句「出错了」有用一百倍。",
    "js16": "闭包是 JS 最强大的特性之一，也是最容易造成内存泄漏的地方。每次调用外层函数都会创建新的闭包环境，返回的函数持有这些变量的引用。如果闭包被长期保存（比如挂在全局对象、事件监听器上），它引用的所有变量都无法回收。解决办法是只捕获必要的数据，及时解除引用，避免在闭包里持有大对象。闭包也是实现私有属性、模块化、函数工厂的基础，理解它，很多看似神奇的库代码就变得平淡无奇了。",
    "js17": "高阶函数让代码从「怎么做」转向「做什么」。map 表达「每个元素变成什么」，filter 表达「保留哪些」，reduce 表达「如何汇总」，sort 的比较器表达「谁在前」。这些方法把循环的模板代码隐藏起来，你只需要提供变化的部分。回调写得越短越专注，可读性越好；超过几行就提取成具名函数，让调用处保持一行。高阶函数不是炫技，它的价值在于把重复的控制流抽走，留下纯粹的业务表达。",
    "js18": "解构赋值在函数参数、返回值、配置对象里都非常常见。它让「从对象里取几个字段」这件事变得简洁，但也会掩盖字段缺失的问题：解构不存在的键得到 undefined，不会报错。需要严格校验时，解构后逐个检查 undefined，或者写一个校验函数。数组解构适合有序数据，比如坐标、RGB、函数的多返回值；对象解构适合有名字的字段，比如配置、用户信息。嵌套解构可读性差，深层字段建议分两步取。",
    "js19": "Map 和 Set 是 ES6 带来的新容器，解决了对象作为字典时的几个老问题：键只能是字符串、原型属性干扰、长度计算麻烦。Map 的键可以是任意类型，按引用或值比较，插入顺序稳定。Set 只存唯一值，适合去重和成员判断。它们都不是数组的替代品：需要下标访问、需要 map/filter 链式处理时，数组更合适。选择容器的标准是「我要用它做什么操作」，而不是「哪个更新」。",
    "js20": "正则表达式的学习曲线陡，但常用模式其实不多：数字、字母、空白、邮箱、日期、手机号。先把这些模式背下来，再学组合和量词，就能覆盖大部分场景。写正则时从简单到复杂，每加一个约束就用几个正例和反例验证。test 用于判断、match 用于提取、replace 用于替换、exec 用于捕获组，四个方法各司其职。正则的性能在极端输入下可能退化，处理用户输入时限制长度，避免灾难性回溯。",
    "js21": "构造函数、原型、实例三者构成一条链：实例的 __proto__ 指向构造函数的 prototype，prototype 的 constructor 指回构造函数。这条链让实例能共享方法，也让 instanceof 能判断类型。不要把方法写在构造函数内部，那样每个实例都会创建一份函数，浪费内存且无法统一修改。原型上的属性是共享的，修改会影响所有实例，所以可变状态应放在实例上，方法放在原型上，这是 ES5 OOP 的基本分工。",
    "js22": "this 的规则可以用一句话概括：看调用点，不看定义点。obj.fn() 的 this 是 obj，fn() 的 this 是全局或 undefined，new Fn() 的 this 是新实例，fn.call(x) 的 this 是 x。箭头函数是唯一例外，它没有自己的 this，定义时外层是谁就是谁。调试 this 问题时，先找到调用那一行，再看是不是把方法摘下来单独调用了。bind 可以永久固定 this，是回调场景的常用解药。",
    "js23": "ES5 的继承写法虽然啰嗦，但每一行都有明确目的：借用父类构造函数复制实例属性，用 Object.create 接上原型链，修正 constructor 保持类型判断正确。理解这三步，再去看 ES6 的 class 语法，会发现它只是同一套机制的语法糖。继承的层次不宜过深，两三层足够；更多时候应该用组合，把可复用的行为抽成独立函数或混入对象。继承表达「是一种」，组合表达「有一个」，业务代码里后者更常见。",
    "js24": "生成器把「产出值」和「控制节奏」分开：函数体负责计算，调用方通过 next 决定何时继续。这种暂停能力让无限序列、懒加载、分页、树遍历变得自然。生成器只能消费一次，遍历完就结束；需要重复遍历时重新调用生成器函数。for-of 会自动处理 done，比手动 next 简洁。生成器的调试不如普通函数直观，关键位置加日志，或者用数组收集结果再检查。",
    "js25": "递归和迭代是同一件事的两种表达。递归更贴近数学定义，代码短、可读性好；迭代更贴近机器执行，内存可控、不会栈溢出。选择标准是问题本身的形状：树、分治、回溯天然适合递归；线性扫描、累计计算适合迭代。写递归时先写终止条件，再写递推关系，最后检查是否重复计算。记忆化能把指数级递归降到多项式级，是性价比最高的优化手段之一。",
    "js26": "IIFE 和模块模式是 JS 模块化的史前史。在 import/export 出现之前，所有库都靠函数作用域隔离变量，靠返回对象暴露 API。这种模式至今仍有价值：写单文件脚本、书签工具、嵌入第三方页面的代码时，IIFE 能保证不污染全局。模块模式的私有变量通过闭包实现，外部只能调用公开方法，无法直接读写内部状态。理解它，再学 ES Modules 会更容易看清「模块」到底解决了什么问题。",
    "js27": "纯函数和不可变数据是一对搭档：纯函数不修改输入，不可变数据保证旧状态不被意外改动，两者合起来让程序的行为可以预测。实际项目里不需要 100% 纯函数，边界层（读写存储、发请求、打印日志）天然有副作用，把它们隔离出来，核心计算保持纯即可。判断一个函数是否纯，看它有没有读写外部变量、有没有调用随机数或时间、有没有修改参数。纯函数最容易测试，因为它不依赖环境。",
    "js28": "Promise 解决了回调地狱的两个问题：错误处理分散、流程难以组合。链式调用让成功路径保持扁平，catch 统一兜底；Promise.all 让并行任务汇合，Promise.race 取最快的结果。then 的返回值会被自动包装成 Promise，所以可以返回普通值、Promise 或抛出异常。不要在一个 then 里嵌套另一个 then，那是退回回调地狱；把链拉平，每一步只做一件事。错误要尽早捕获，或者在最外层统一处理。",
    "js29": "性能优化有三条原则：先测量、再优化、别过度。没有测量数据的优化是猜测，可能让代码更复杂却没有收益。复杂度是宏观指标，常数因子是微观指标，两者都要看。常见的手法是空间换时间（缓存、索引、Set）、减少重复计算（提取循环不变量）、选择合适的数据结构（Map 代替线性查找）。优化后一定要重跑正确性测试，性能提升不能以行为改变为代价。",
    "js30": "综合项目是把零散知识连成体系的最好方式。状态机、命令解析、纯函数更新、渲染输出，这四块可以复用到很多场景：工作流引擎、表单校验、游戏逻辑、对话系统。写项目时先定义数据结构和状态转换，再写解析和渲染，最后补测试。不要一上来就写界面，界面是最容易变的部分，核心逻辑稳定后再接界面，返工成本最低。项目完成后回顾一遍：哪些设计当时觉得麻烦、后来省了事？这些就是经验。",
}


def apply_extra(packs):
    for lessons in packs:
        for lesson in lessons:
            extra = EXTRA.get(lesson["id"])
            if not extra:
                continue
            blocks = lesson["blocks"]
            insert_at = len(blocks)
            for i, block in enumerate(blocks):
                if block["type"] == "quiz":
                    insert_at = i
                    break
            blocks.insert(insert_at, {"type": "text", "text": extra})

# ---------------------------------------------------------------------------
# 第三段扩写：补齐到 900 汉字以上（每讲一段针对性收束）
# ---------------------------------------------------------------------------

EXTRA2 = {
    "js01": "把第一行代码跑通之后，建议立刻做三个小实验：改字符串内容、改数字、故意删掉一个引号，观察输出和报错分别长什么样。认识报错的样子，比背语法更重要。JS 的报错通常会指出文件名、行号和错误类型，比如 SyntaxError 表示解析阶段就失败，ReferenceError 表示引用了不存在的变量。读懂这两类错误，你就能独立解决入门阶段八成的问题。每次实验只改一处，才能确定是哪个改动导致了结果变化。",
    "js02": "声明变量的位置也影响可读性。把同一类变量放在一起，按「配置、状态、临时值」分组，读代码的人能更快建立心智模型。常量用全大写命名只是社区习惯，真正的常量语义靠 const 保证。var、let、const 三者不要混用：新代码统一 let/const，遇到旧代码里的 var 再单独理解。类型判断函数要记牢：typeof 适合基本类型，Array.isArray 适合数组，instanceof 适合自定义构造函数创建的对象，Object.prototype.toString 可以拿到更精确的标签。",
    "js03": "比较运算还有一个容易忽略的点：对象和数组用 === 比较的是引用，两个内容相同的数组也不相等。需要比较内容时，数组用 join 或 JSON.stringify，对象用逐字段比较或序列化。NaN 是唯一不等于自己的值，判断要用 Number.isNaN。布尔转换在条件里自动发生，但显式写 Boolean(x) 能让意图更清楚。所有这些规则的共同目标是：让类型在代码里是可见的，而不是藏在引擎的自动转换里。",
    "js04": "模板字符串的另一个用途是生成带格式的文本，比如日志、报告、SQL 片段。它保留换行，写多行内容时不必用转义字符。嵌入表达式时保持简单，复杂的计算先抽成变量，模板只负责组装。字符串拼接的性能在短文本上无关紧要，长文本用数组 join。最后记住：字符串一旦创建就不能修改，所有方法都返回新串，变量要重新赋值才能看到变化，这是初学者最常见的「为什么没生效」。",
    "js05": "条件分支的可测试性取决于边界是否清晰。写完后列出所有分支，为每个分支准备至少一个输入，再准备空值、负数、超大值等异常输入。如果某个分支很难构造输入，说明条件设计可能有问题。else 不是必须的，提前 return 能让主路径更平。switch 的 fallthrough 要显式注释，否则读代码的人会以为是漏写 break。三元表达式只用于简单赋值，不要嵌套超过两层。",
    "js06": "循环写完后做一次「手动走查」：把 n 设成 0、1、2，在纸上写出每轮变量的值，检查是否与预期一致。这个习惯能抓住大部分边界错误。for-of 适合只关心元素的场景，经典 for 适合需要下标或要修改数组的场景。while 适合次数未知的等待，但一定要保证条件会变假。break 和 continue 会让控制流跳跃，用时加注释说明意图。嵌套循环超过两层，考虑抽函数或换数据结构。",
    "js07": "数组的 sort 默认按字符串排序，这是一个高频陷阱。数字排序必须传比较函数，字符串排序要注意大小写和本地化。sort 会修改原数组，需要保留原顺序就先 slice 复制。splice 的返回值是被删除的元素，不是修改后的数组，这个细节经常被记反。数组的 length 可以读写，但手动改 length 会产生空洞，遍历时得到 undefined。需要清空数组时，arr.length = 0 是常用写法，比 arr = [] 更能保留引用。",
    "js08": "对象字面量的键可以是标识符、字符串或数字，写成 { name: 'V', 'level': 66, 1: 'x' } 都合法。访问时点号只适合合法标识符，其他情况用中括号。对象的方法本质上是属性值为函数的属性，调用时 this 指向对象本身。遍历对象推荐 Object.keys 加普通 for，顺序可控；for-in 会遍历原型链，需要 hasOwnProperty 过滤。删除属性用 delete，但它不会释放内存，只是断开引用。",
    "js09": "参数默认值在本运行时不支持，用 if (x === undefined) x = 默认值 代替。rest 参数必须是最后一个，收集到的是真正的数组。arguments 是类数组对象，需要 Array.prototype.slice.call 转数组。函数可以作为返回值，这是闭包和工厂函数的基础。写递归函数时，基准情形要放在最前面，递归步骤要保证规模缩小。函数不要过长，超过一屏就该拆分，每个函数只做一件事。",
    "js10": "提升规则可以用一句话总结：声明被提前，赋值留在原地。var 的声明提升到函数顶部，函数声明整体提升，let/const 提升但不初始化（暂时性死区）。本运行时的 let/const 实际表现接近 var，声明前访问得到 undefined 而不是报错，写课程示例时不要依赖这个差异。作用域越小越好：块级作用域、函数作用域、模块作用域，逐层收窄。全局变量只保留真正需要共享的配置，其余一律放进函数或模块。",
    "js11": "数组方法链的调试技巧：在每一步后面加一个临时变量并打印长度，确认中间结果符合预期，再把链合并回去。reduce 的初始值类型决定了累加器的类型，求和传 0，拼接传空串，分组传空对象。回调里不要修改累加器以外的状态，否则 reduce 就不再是纯计算。map 和 filter 的回调返回值分别决定「新元素」和「是否保留」，写错返回值类型不会报错，但结果会出乎意料。",
    "js12": "处理文本时先明确「分隔符是什么、空白算不算、大小写敏不敏感」。这三个问题决定了清洗流水线的顺序。split 的分隔符可以是字符串或正则，字符串按字面量匹配，正则可以处理多种分隔符。join 的分隔符可以是空串，用来把字符数组拼回字符串。replace 的回调参数顺序是匹配、捕获组、位置、原串，写回调时按需取用。文本很长时避免在循环里反复拼接，用数组收集。",
    "js13": "JSON 的常见错误有三类：语法错误（单引号、尾逗号、注释）、类型丢失（undefined、函数、Date）、结构不符（缺字段、类型不对）。前两类在解析阶段暴露，第三类需要自己校验。序列化前先想要不要保留 undefined，必要时转成 null；反序列化后先检查关键字段是否存在、类型是否正确。配置文件、缓存、日志都适合用 JSON，但二进制数据要用 Base64 或专门的格式。",
    "js14": "数值处理要区分「显示值」和「计算值」。显示时可以用 toFixed 保留小数位，计算时用原始数字，最后一步再格式化。toFixed 返回字符串，参与运算前要转回数字。Math.random 不可预测但也不安全，不能用于密码、令牌、抽奖等安全场景。Date 的时区问题在跨地区应用里很常见，存储统一用 UTC 时间戳，展示时再转本地时间。日期加减用毫秒数，避免手动处理月份天数。",
    "js15": "异常设计要区分「预期内的失败」和「真正的 bug」。用户输入不合法是预期内的，用返回值或校验函数处理；代码逻辑写错是 bug，让它抛异常尽早暴露。自定义错误继承 Error，设置 name 和 message，必要时加 code 字段供程序判断。catch 里不要只写 console.log，要决定恢复策略或重新抛出。finally 适合清理资源，但不要在里面 return，它会覆盖 try 里的返回值。",
    "js16": "闭包和内存的关系可以用「引用计数」理解：只要还有函数引用着变量，变量就不会被回收。长生命周期的闭包（事件监听、定时器、全局缓存）最容易积累内存。解决办法是及时移除监听、清空缓存、把不再需要的大对象置为 null。闭包也是实现「私有字段」的唯一手段（在 class 语法不可用时），通过返回对象的方法访问内部变量，外部无法直接修改。",
    "js17": "高阶函数的组合能力来自「函数也是值」。把函数存在对象里就是策略表，把函数作为参数就是回调，把函数作为返回值就是工厂。compose 和 pipe 是两种组合方向：compose 从右到左，pipe 从左到右，选一种团队统一即可。回调里抛出的异常会传给调用方，除非调用方捕获；异步回调里的异常要走 Promise 的 catch。写高阶函数时，参数名用 fn、predicate、mapper 这类语义化名字，读起来更清楚。",
    "js18": "解构赋值可以用于函数返回多个值：return { ok: true, data: data }，调用方 var { ok, data } = result。这比返回数组更容易扩展字段。数组解构适合位置固定的数据，比如 [x, y] = point。解构时变量名冲突可以用重命名，嵌套太深就分步取。本运行时不支持默认值和 rest 解构，写代码前先确认语法边界，避免在真机上才发现解析失败。",
    "js19": "Map 的常用方法要记全：set 返回 Map 本身，可以链式调用；get 不存在返回 undefined；has 判断键；delete 返回布尔值表示是否删除成功；clear 清空；size 是属性。Set 的 add 也返回自身，has/delete/clear 类似。遍历 Map 用 forEach(value, key) 或 for-of 拿 [key, value]；遍历 Set 用 forEach(value) 或 for-of 拿值。两者都支持 for-of，但不支持下标访问。",
    "js20": "正则的调试方法：把模式拆成最小单元，用 test 逐个验证，再组合。字符类、量词、分组、锚点分开测试，出错时容易定位。提取用 match 加 g，捕获组用 exec 或 match 不加 g。replace 的 $1 到 $9 引用捕获组，$& 表示整个匹配。正则字面量在循环里复用会保留 lastIndex，需要每次重置或新建。复杂正则加注释，把每段的意图写清楚。",
    "js21": "原型链上的方法查找是动态的：即使实例已经创建，之后往 prototype 上加方法，实例也能访问到。这让「给所有实例统一打补丁」成为可能，但也意味着运行期修改原型会影响所有代码。判断属性来源用 hasOwnProperty，遍历自身属性用 Object.keys。构造函数的名字首字母大写只是约定，真正让它成为构造函数的是 new 调用。忘记 new 时，非严格模式下 this 指向全局，属性会挂错地方。",
    "js22": "call、apply、bind 的本质都是「指定 this 调用函数」。call 和 apply 立即执行，bind 返回新函数。apply 的第二个参数是数组，适合参数数量不定的场景；call 适合参数固定的场景。bind 还可以预设参数，形成偏函数：var add5 = add.bind(null, 5)。箭头函数没有 arguments，也没有自己的 this，不能用作构造函数。需要动态 this 的方法不要写成箭头函数。",
    "js23": "继承链上的方法查找顺序是：实例自身 -> 子类 prototype -> 父类 prototype -> Object.prototype。任何一环找到同名方法就停止，所以子类方法会覆盖父类方法。想调用父类实现，用 Parent.prototype.method.call(this)。instanceof 检查的是原型链上是否存在某个 prototype，而不是构造函数本身。Object.create(null) 创建的对象没有原型链，适合做纯字典，但不能调用 hasOwnProperty 等方法。",
    "js24": "生成器的 next 可以传值，也可以传异常：it.throw(err) 会在暂停点抛出异常，it.return(v) 会提前结束。生成器委托用 yield* 把一个生成器的产出转交给另一个。生成器函数的返回值会放在最后一个 { value, done: true } 里。无限生成器必须配合 take 或 break 使用，否则 for-of 会永远跑下去。生成器不能跨脚本保存状态，但迭代器对象可以。",
    "js25": "递归的终止条件要覆盖所有分支，包括空数组、null、负数。写递归前先写出递推公式，再翻译成代码。递归深度过大时改为迭代，用显式栈保存待处理节点。记忆化的缓存键要能唯一标识参数，多参数时用分隔符拼接或嵌套 Map。动态规划本质上是「自底向上的记忆化」，先把小规模的结果算好存表，再逐步推到目标规模。",
    "js26": "IIFE 的返回值可以是任何类型，常见的是对象（模块模式）或函数（工厂）。IIFE 内部的变量对外完全不可见，这是它最大的价值。命名 IIFE 便于调试，但名字只在内部有效。箭头函数 IIFE 写法更短，但没有 arguments 和 this。模块模式返回的对象方法共享同一份闭包状态，所以是单例；需要多实例时用工厂函数。",
    "js27": "不可变更新在嵌套结构里要逐层复制：改 obj.a.b.c，需要新 obj、新 a、新 b，其他分支共享引用。手写容易出错，可以写一个 setIn 辅助函数，沿路径递归复制。数组的不可变操作有 concat、slice、map、filter，对象的不可变操作有 Object.assign、展开运算符（本运行时不支持展开，用 Object.assign 代替）。Object.freeze 只冻结第一层，深层仍需逐层处理。",
    "js28": "Promise 的 then 可以只传成功回调，错误会继续向后传播；catch 等价于 then(null, onRejected)。Promise.all 在所有成功时返回结果数组，任何一个失败就整体失败；Promise.race 返回最先完成的结果，无论成功失败。Promise.resolve 可以包装普通值，Promise.reject 创建失败状态。本运行时的 Promise 回调在脚本结束后统一执行，写示例时不要在同一个脚本里依赖回调结果。",
    "js29": "复杂度分析要区分最好、最坏、平均情况。查重的最好情况是第一个元素就重复，最坏要遍历完；算法分析通常看最坏情况。空间复杂度也算成本，递归的调用栈、缓存的哈希表都要计入。优化时先找热点：用计时器测量各个函数的耗时，优先优化占比最大的部分。微优化（比如把 i++ 改成 ++i）在现代引擎里几乎没有收益，不要浪费时间。",
    "js30": "项目收尾时做三件事：补测试、写说明、清理临时文件。测试覆盖核心路径和边界情况，说明写清楚怎么运行、依赖什么、有哪些限制。临时文件和调试代码不要留在交付物里。回顾整个项目，把「当时为什么这样设计」记录下来，这是比代码更值钱的经验。下一步可以尝试把状态机扩展成多房间、多物品、带存档的完整游戏，或者把同样的结构用到自己的业务项目里。",
}


def apply_extra2(packs):
    for lessons in packs:
        for lesson in lessons:
            extra = EXTRA2.get(lesson["id"])
            if not extra:
                continue
            blocks = lesson["blocks"]
            insert_at = len(blocks)
            for i, block in enumerate(blocks):
                if block["type"] == "quiz":
                    insert_at = i
                    break
            blocks.insert(insert_at, {"type": "text", "text": extra})

EXTRA3 = {
    "js02": "还有一个实践建议：每次声明变量时顺手想一下它的生命周期。循环里的临时变量、只在某个分支用的中间值、整个模块共享的配置，生命周期完全不同，作用域也应该不同。能用块级作用域限制住的，就不要放大到函数级；能在函数内部消化的，就不要挂到全局。变量可见范围越小，能被意外修改的路径越少，调试时需要排查的嫌疑范围也越小。",
    "js03": "练习时可以把同一个表达式拆成多行，逐步打印中间值和类型：先算左边、再算右边、最后看运算结果。隐式转换的规则不需要全部背下来，但常见的几种要形成条件反射：字符串加数字是拼接，减号会转数字，空串转数字是 0，null 转数字是 0，undefined 转数字是 NaN。遇到不确定的表达式，写一行 console.log(typeof x, x) 比猜更快。",
    "js04": "处理用户输入时还要考虑空值和超长文本。空字符串调用 split、slice、trim 都不会报错，但业务上往往需要单独处理。超长文本做截断时，先判断长度再 slice，避免生成巨大的中间数组。模板字符串里不要直接拼接用户输入去构造代码或查询语句，那是注入漏洞的常见来源。文本处理看起来简单，边界和安全性才是真正的难点。",
    "js05": "写条件时还有一个可读性技巧：把肯定条件放前面，否定条件放后面。if (isValid) 比 if (!isInvalid) 更容易读。多个条件用括号分组，明确优先级。复杂的布尔表达式可以抽成具名变量，比如 var canAccess = level >= 50 && !banned; 然后 if (canAccess)。表达式越短，越不容易写错，也越容易在评审时被发现。",
    "js06": "如果循环体超过十行，通常说明它做了不止一件事，应该拆成函数。拆分的标准是「这段代码能否用一个动词描述」，能就可以独立。循环里尽量不要修改循环变量，那会让终止条件难以推理。需要跳过某些元素用 continue，需要提前结束用 break，两者都比嵌套 if 清晰。遍历对象数组时，先把需要的字段解构出来，循环体里就不用反复写 item.xxx。",
    "js07": "数组是引用类型，赋值和传参都不会复制。把数组交给函数前，先想清楚函数会不会修改它；如果不确定，就传一份副本。复制一维数组用 slice()，复制二维数组要逐行 slice。数组比较用内容比较，不要用 ===。需要把数组当键时，先 JSON.stringify 成字符串，但要注意键的顺序和特殊类型。",
    "js08": "对象的可枚举性影响遍历结果：通过字面量和方法定义的属性默认可枚举，Object.defineProperty 可以控制。JSON.stringify 只序列化可枚举的自身属性。原型上的属性不会被 Object.keys 返回，但 for-in 会遍历到。理解这些差异，才能解释「为什么打印出来有、遍历却拿不到」这类问题。对象嵌套过深时，考虑用扁平结构加 id 引用，读写都更简单。",
    "js09": "函数参数的设计要稳定：一旦发布，增删参数都可能破坏调用方。新增可选参数放在末尾，用 undefined 判断是否传入。返回值类型要一致，不要因为分支不同返回不同结构。函数内部不要依赖外部的可变全局变量，否则同样的输入可能得到不同输出。把依赖显式传入，测试时就能轻松替换。",
    "js10": "调试作用域问题时，先确认变量是在哪一层声明的，再看使用点位于哪一层。如果同名变量出现在多个层级，打印时加不同的标签区分。全局变量可以用 window 或 globalThis 检查，但本运行时没有这些对象，靠代码审查更实际。把代码包进函数或 IIFE，是避免全局污染最直接的手段，也是后面模块模式的基础。",
    "js11": "链式调用返回的都是新数组，所以可以在中间插入调试用的 map 打印。比如 .map(function (x) { console.log('step', x); return x; }) 不会改变结果，只增加观察点。reduce 的初始值不要省略，除非你确定数组非空且类型正确。回调函数尽量写成纯函数，不依赖外部变量，这样每一步的结果都可以独立验证。",
    "js12": "格式化输出时，padStart 和 padEnd 很有用：编号补零、对齐表格、生成固定宽度的文本。repeat 适合画分隔线。trim 只去首尾，中间的空格要自己处理。处理多行文本时，split('\n') 得到行数组，逐行 trim 后再过滤空行，是日志分析的常见套路。字符串方法都不会修改原串，记得把返回值接住。",
    "js13": "JSON 的缩进参数只影响可读性，不影响解析结果。生产环境传输时通常不缩进，节省带宽；调试和配置文件用两个空格缩进。深拷贝用 JSON 方案时，注意它会丢失函数、undefined、Date 类型和原型链，只适合纯数据。需要保留类型时，自己写序列化和反序列化函数，把类型信息显式存进字段。",
    "js14": "日期计算还有一个常见需求：判断闰年、某月有多少天。用 new Date(year, month, 0).getDate() 可以拿到上个月最后一天，也就是目标月份的天数，这是个小技巧。时间戳相减得到毫秒，除以 1000 得秒，除以 60000 得分钟，除以 3600000 得小时，除以 86400000 得天。跨时区比较统一用 getTime 或 UTC 方法。",
    "js15": "错误处理写完后要测试失败路径，而不只是成功路径。故意传错参数、制造空值、触发边界，确认 catch 里的逻辑真的执行、返回值符合预期。没有测试过的错误分支，等于没有写。日志里记录错误时，带上函数名、参数摘要和时间，方便复现。用户看到的提示要友好，开发者看到的日志要详细，两者分开。",
    "js16": "闭包在循环里的经典问题是共享变量。用 var 声明的循环变量只有一个，所有回调看到的是最终值；用函数工厂把当前值传进去，每个回调就能拿到独立副本。这个模式在事件处理、异步回调里非常常见。理解「捕获变量还是捕获值」的差别，是写出正确闭包代码的关键。",
    "js17": "回调函数的参数顺序是约定：错误优先（error-first）是 Node 的风格，数组方法则是值优先。写自己的高阶函数时，把回调放在最后一个参数，方便调用方传匿名函数。回调的返回值要明确：map 需要返回值，forEach 不需要。高阶函数不要修改传入的数组或对象，保持纯函数风格。",
    "js18": "解构和展开运算符经常一起出现，但本运行时不支持展开。需要合并对象用 Object.assign，需要合并数组用 concat。解构赋值可以一次声明多个变量，但不要在一行里塞太多，超过四五个就该拆分。函数参数解构时，调用方必须传对象，不能传 null 或 undefined，否则会抛 TypeError。",
    "js19": "Map 和 Set 的迭代器可以用 for-of 消费，也可以用 forEach。for-of 拿到的 Map 元素是 [key, value] 数组，Set 元素是值本身。它们都不能用 JSON.stringify 直接序列化，需要先转成数组或普通对象。判断是否为空用 size === 0，不要用 length。删除不存在的键不会报错，delete 返回 false。",
    "js20": "正则的字符类里，连字符表示范围，比如 a-z、0-9；要匹配连字符本身，放在开头或结尾，或者转义。点号匹配除换行外的任意字符，要匹配真正的点号就转义。括号分组会捕获内容，不想捕获用 (?:...)。锚点 ^ 和 $ 在 m 标志下匹配每行。写模式时先保证正确，再考虑性能。",
    "js21": "构造函数返回对象时，new 的结果会被这个对象替换；返回基本类型则被忽略。这个特性很少需要，但读旧代码时可能遇到。原型上的 constructor 属性默认指向构造函数本身，手动替换 prototype 后要修正它，否则类型判断会出错。instanceof 对基本类型返回 false，对 null 和 undefined 也返回 false。",
    "js22": "this 丢失的另一种场景是对象方法被赋值给另一个对象的同名属性。解决方式除了 bind，还可以在定义时用箭头函数捕获外层 this。但箭头函数不能用作构造函数，也不能用 call/apply 改变 this。选择哪种方式取决于是否需要动态 this：需要就用普通函数加 bind，不需要就用箭头函数。",
    "js23": "继承体系设计时，父类只放通用行为和字段，子类放差异部分。父类构造函数不要做太多事，尤其是不要调用子类才能提供的方法，否则初始化顺序会出问题。方法覆盖时保持签名一致，返回值语义一致。能用组合解决的问题不要用继承，继承层次越深，修改父类的影响面越大。",
    "js24": "生成器的调试可以用一个辅助函数把前 n 个值收集成数组，打印出来检查。生成器内部抛出的异常会传给 next 的调用方，可以用 try/catch 捕获。生成器函数不能是箭头函数，必须用 function*。yield 只能在生成器函数内部使用，嵌套函数里不行。",
    "js25": "递归算法的复杂度分析要看递归树：每层有多少个子问题、每个子问题规模多大、树有多深。斐波那契的递归树是指数级的，记忆化后每个状态只算一次，降到线性。树的遍历每个节点访问一次，是线性的。写递归时先把递推关系写清楚，再考虑优化，不要一上来就纠结性能。",
    "js26": "模块模式返回的对象可以逐步扩展：先定义核心方法，再按需添加辅助方法，最后统一返回。内部函数之间可以互相调用，不需要通过返回对象。私有变量命名加下划线只是约定，真正的私有靠闭包实现。IIFE 的参数注入可以让依赖更明确，测试时也更容易替换。",
    "js27": "纯函数的测试非常直接：给定输入，断言输出，不需要准备环境。不可变更新的测试要断言两件事：新状态正确、旧状态未被修改。写不可变代码时，先复制再修改，顺序不能反；直接修改原对象再复制，旧状态已经被污染。深层次更新可以写通用的 setIn 工具，避免每层手写复制。",
    "js28": "Promise 链的最后一定要有 catch，否则失败会变成未处理的拒绝。catch 里可以返回兜底值让链恢复，也可以重新抛出。then 里返回 Promise 会等待它完成，返回普通值会立即传递。不要在 then 里写复杂的同步逻辑，那会阻塞后续链；把计算抽成函数，保持每一步短小。",
    "js29": "性能测试要用真实数据规模，不要用十个元素测完就下结论。测多次取平均，排除首次运行的预热影响。比较两个实现时，除了耗时还要看内存和代码复杂度。优化后的代码必须通过同样的测试，行为不能变。如果优化让代码难以理解，而收益只有几个百分点，通常不值得。",
    "js30": "把项目拆成模块时，先定义数据结构，再定义操作这些数据的纯函数，最后写解析和渲染。数据结构稳定后，功能扩展只是增加函数和命令，不会牵动全局。测试直接针对纯函数，不需要模拟用户输入。交付前跑一遍完整流程，确认每个命令都能正确改变状态，错误命令不会破坏状态。",
}


def apply_extra3(packs):
    for lessons in packs:
        for lesson in lessons:
            extra = EXTRA3.get(lesson["id"])
            if not extra:
                continue
            blocks = lesson["blocks"]
            insert_at = len(blocks)
            for i, block in enumerate(blocks):
                if block["type"] == "quiz":
                    insert_at = i
                    break
            blocks.insert(insert_at, {"type": "text", "text": extra})

EXTRA4 = {
    "js07": "练习数组时建议把「读、改、查、删、排序」五类操作各写一遍，并观察原数组是否变化。把每个方法的返回值打印出来，确认自己理解的是返回值还是原数组。数组是后续所有数据处理的基础，map、filter、reduce 都建立在它之上。花时间把这几个方法练熟，后面的课程会轻松很多。遇到不确定的行为，直接写两行代码验证，不要凭印象。",
    "js08": "对象和数组的组合几乎能表达所有结构化数据：用户列表是对象数组，配置是嵌套对象，索引是键值映射。写业务代码时先设计数据结构，再写操作函数。数据结构清晰，逻辑就短；数据结构混乱，再多技巧也救不回来。对象字段的命名保持一致，比如统一用 camelCase，避免同一个概念在不同地方叫不同名字。",
    "js13": "处理 JSON 时还要注意编码问题：中文在 UTF-8 下正常，但如果传输环节编码不一致，可能出现乱码。序列化后的字符串是纯文本，可以安全地放进文件、网络请求、日志。不要把 JSON 字符串当代码执行，eval 会带来严重的安全风险。解析失败时给出具体的错误位置，比一句「格式错误」更有帮助。",
    "js14": "数值格式化还有一个常用技巧：用 toFixed 控制小数位，用 parseInt/parseFloat 解析用户输入。百分比计算先乘 100 再保留一位小数，避免浮点误差累积。日期比较直接用时间戳，不要比较格式化后的字符串，字符串比较是按字典序，跨世纪时会出错。时间区间计算注意包含边界还是排除边界，业务语义要写清楚。",
    "js15": "异常处理还有一个实践：把「可能失败的操作」集中到少数几个函数里，其他函数保持纯粹。这样错误边界清晰，测试也容易。比如解析、校验、IO 各自封装，调用方按顺序组合。不要让异常穿过太多层，否则堆栈很长、定位困难。每层捕获后补充上下文再抛出，是常用做法。",
    "js18": "解构赋值让代码更短，但短不等于清晰。字段很多时，逐个解构反而不如直接用一个对象变量，读代码的人能看出数据来源。函数参数解构适合字段少、语义明确的场景。解构后的变量名如果和外部变量冲突，用重命名解决，不要勉强复用。数组解构注意跳过元素的逗号数量，写错会取到错误位置。",
    "js19": "Map 和 Set 的性能优势在大数据量下才明显，小数据用对象和数组更简单。选择容器时还要考虑团队熟悉度：大家都熟悉的写法比冷门技巧更可维护。Map 的键可以是对象，但对象键按引用比较，两个内容相同的对象不相等，这点和普通对象不同。Set 的遍历顺序是插入顺序，需要排序时先转数组。",
    "js20": "正则表达式的可读性可以通过命名捕获组改善，但本运行时不支持 (?<name>...) 语法，只能用编号捕获组。写复杂模式时把每部分拆成变量，用字符串拼接构造 RegExp，虽然不如字面量直观，但更容易加注释。测试正则时准备一组正例和反例，覆盖边界情况：空串、超长串、特殊字符。",
    "js21": "原型方法里的 this 指向调用它的实例，所以实例之间共享方法但状态独立。如果方法内部需要访问构造函数的私有变量，只能用闭包，不能用 prototype。构造函数适合需要 instanceof 判断、需要共享方法的场景；工厂函数适合不需要类型判断、每个实例行为略有差异的场景。两者没有绝对优劣，看需求。",
    "js22": "调试 this 时可以在函数第一行打印 this，观察它到底是什么。非严格模式下普通调用的 this 是全局对象，严格模式下是 undefined。方法调用时 this 是调用它的对象，但把方法赋给变量后再调用就丢了。箭头函数的 this 在定义时确定，之后不会改变，适合用在回调里保持外层上下文。",
    "js23": "继承体系的测试要覆盖：父类方法可访问、子类方法可访问、覆盖方法生效、instanceof 两级都成立、constructor 指向正确。任何一项失败都说明原型链接错了。修改原型后，已创建的实例也会看到新方法，这是原型动态性的体现。不要在继承链上放可变共享状态，那会导致实例之间互相影响。",
    "js24": "生成器的常见用途是分页：每次 yield 一页数据，调用方处理完再请求下一页。也可以用来做树的深度优先遍历，把递归改成可暂停的迭代。生成器函数的返回值会出现在 done 为 true 的那次 next 里，别忘了取。生成器不能重复使用，需要重新遍历时再调用一次生成器函数。",
    "js26": "IIFE 和模块模式在单文件脚本里非常实用：把变量包起来，只暴露一个全局名字。返回的对象就是模块的公开 API，内部实现可以随时替换。模块之间通过参数注入依赖，避免隐式依赖全局变量。现代项目虽然用 ES Modules，但理解模块模式有助于读懂打包后的代码和旧库。",
    "js28": "Promise 的错误处理要区分「可恢复」和「不可恢复」：网络超时可以重试，参数错误重试也没用。catch 里根据错误类型决定策略，不要一律返回同一个兜底值。Promise.all 的失败会丢失其他成功结果，需要全部结果时用 allSettled（本运行时不一定支持），或者给每个 Promise 单独 catch。链式调用保持扁平，不要嵌套。",
}


def apply_extra4(packs):
    for lessons in packs:
        for lesson in lessons:
            extra = EXTRA4.get(lesson["id"])
            if not extra:
                continue
            blocks = lesson["blocks"]
            insert_at = len(blocks)
            for i, block in enumerate(blocks):
                if block["type"] == "quiz":
                    insert_at = i
                    break
            blocks.insert(insert_at, {"type": "text", "text": extra})

EXTRA5 = {
    "js14": "最后提醒一个实践细节：不要把「当前时间」写死在代码里，测试和回放都会因此失效。需要当前时间时通过参数传入，函数只负责计算。这样日期逻辑可以脱离系统时钟独立测试，也能在需要时模拟不同时间点。日期工具的输入输出用时间戳或标准字符串，避免各平台解析格式不一致。",
    "js19": "最后补充一个使用场景：用 Map 做缓存。键是请求参数序列化后的字符串，值是计算结果，取之前先 has 判断，没有就计算并 set。这种缓存策略简单有效，但要注意内存增长，必要时限制条目数或定期清理。Set 可以用来记录「已经处理过的 id」，避免重复处理。两种容器都是日常业务里高频出现的基础设施，值得熟练。",
    "js22": "最后给出一个判断口诀：看到 this，先找调用表达式；看到箭头函数，直接找外层；看到 bind，认准绑定的对象。三者按顺序检查，基本不会判断错。写代码时尽量让 this 的使用局部化，方法内部不要跨多层回调引用 this，需要时先存成 var self = this，这是 ES5 时代最稳的写法。",
}


def apply_extra5(packs):
    for lessons in packs:
        for lesson in lessons:
            extra = EXTRA5.get(lesson["id"])
            if not extra:
                continue
            blocks = lesson["blocks"]
            insert_at = len(blocks)
            for i, block in enumerate(blocks):
                if block["type"] == "quiz":
                    insert_at = i
                    break
            blocks.insert(insert_at, {"type": "text", "text": extra})


# ---------------------------------------------------------------------------
# 结构自检与落盘
# ---------------------------------------------------------------------------

CHAPTERS = [
    ("js-basics", 21, "JavaScript · 基础篇", BASICS),
    ("js-core", 22, "JavaScript · 核心篇", CORE),
    ("js-advanced", 23, "JavaScript · 进阶篇", ADVANCED),
]

REQUIRED_BLOCKS = {"heading", "text", "code", "output", "quiz"}


def _chinese_chars(text):
    return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")


def validate_pack(pack_id, chapter, chapter_name, lessons):
    problems = []
    if len(lessons) != 10:
        problems.append(f"{pack_id}: 应为 10 讲，实际 {len(lessons)}")
    expected_order = 300 + (chapter - 21) * 10
    for i, lesson in enumerate(lessons):
        lid = lesson["id"]
        if lesson["order"] != expected_order + i:
            problems.append(f"{lid}: order 应为 {expected_order + i}")
        if lesson["chapter"] != chapter:
            problems.append(f"{lid}: chapter 应为 {chapter}")
        if lesson["chapterName"] != chapter_name:
            problems.append(f"{lid}: chapterName 不一致")
        if lesson["lang"] != "javascript":
            problems.append(f"{lid}: lang 应为 javascript")

        types = [b["type"] for b in lesson["blocks"]]
        if types.count("heading") != 1:
            problems.append(f"{lid}: 应有且仅有 1 个 heading")
        for required in REQUIRED_BLOCKS:
            if required not in types:
                problems.append(f"{lid}: 缺少 {required} 块")
        if types.count("text") < 2:
            problems.append(f"{lid}: 至少 2 段 text")
        if types.count("code") < 2:
            problems.append(f"{lid}: 至少 2 个代码块")
        if types.count("code") != types.count("output"):
            problems.append(f"{lid}: code 与 output 数量不匹配")
        if not any(t in types for t in ("table", "diagram")):
            problems.append(f"{lid}: 缺少 table 或 diagram")
        if not any(t in types for t in ("tip", "warn")):
            problems.append(f"{lid}: 缺少 tip 或 warn")
        if "quiz" not in types:
            problems.append(f"{lid}: 缺少 quiz")
        for block in lesson["blocks"]:
            if block["type"] == "quiz":
                if not (0 <= block["answer"] < len(block["options"])):
                    problems.append(f"{lid}: quiz answer 越界")
                if len(block["options"]) != 4:
                    problems.append(f"{lid}: quiz 应有 4 个选项")
            if block["type"] == "code" and not block.get("runnable"):
                problems.append(f"{lid}: 代码块必须显式 runnable")

        body = "".join(b.get("text", "") for b in lesson["blocks"] if b["type"] == "text")
        han = _chinese_chars(body)
        if han < 900:
            problems.append(f"{lid}: 正文汉字 {han} 少于 900")
        if han > 2200:
            problems.append(f"{lid}: 正文汉字 {han} 偏多")

        ex = lesson["exercise"]
        for key in ("title", "brief", "starterCode", "hint", "tests", "stdin", "xp", "solution"):
            if key not in ex:
                problems.append(f"{lid}: exercise 缺少 {key}")
        if not (3 <= len(ex["tests"]) <= 5):
            problems.append(f"{lid}: tests 应为 3-5 条，实际 {len(ex['tests'])}")
        if not ex.get("starterCode", "").strip():
            problems.append(f"{lid}: starterCode 为空")
        if not ex.get("solution", "").strip():
            problems.append(f"{lid}: solution 为空")
    return problems


def main():
    apply_enrichment([BASICS, CORE, ADVANCED])
    apply_extra([BASICS, CORE, ADVANCED])
    apply_extra2([BASICS, CORE, ADVANCED])
    apply_extra3([BASICS, CORE, ADVANCED])
    apply_extra4([BASICS, CORE, ADVANCED])
    apply_extra5([BASICS, CORE, ADVANCED])
    consolidate_paragraphs([BASICS, CORE, ADVANCED])
    dedupe_sentences([BASICS, CORE, ADVANCED])
    problems = []
    seen_ids = set()
    seen_orders = set()
    for pack_id, chapter, chapter_name, lessons in CHAPTERS:
        problems.extend(validate_pack(pack_id, chapter, chapter_name, lessons))
        for lesson in lessons:
            if lesson["id"] in seen_ids:
                problems.append(f"重复 id: {lesson['id']}")
            seen_ids.add(lesson["id"])
            if lesson["order"] in seen_orders:
                problems.append(f"重复 order: {lesson['order']}")
            seen_orders.add(lesson["order"])

    if problems:
        for p in problems:
            print("STRUCT:", p)
        sys.exit(1)

    OUT.mkdir(parents=True, exist_ok=True)
    for pack_id, _, _, lessons in CHAPTERS:
        path = OUT / f"{pack_id}.json"
        path.write_text(
            json.dumps(lessons, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"{pack_id}: {len(lessons)} 讲 -> {path.name}")


if __name__ == "__main__":
    main()
