#!/usr/bin/env python3
"""生成 TypeScript 30 讲课程包（基础 / 核心 / 进阶各 10 讲）。

运行：python tools/gen_ts_curriculum.py
输出：content_packs/ts-basics.json、ts-core.json、ts-advanced.json

所有运行代码都限制在 TypeScriptTranspiler 支持的子集内：
变量/参数/返回值标注、interface、type 别名、泛型参数列表、as、非空断言、enum。
不使用 class、装饰器、命名空间、条件类型的运行语义、展开运算符、默认参数、
async/await、可选链、空值合并。
"""

import json
import pathlib
import re
import textwrap

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "content_packs"

C1 = "TypeScript · 基础篇"
C2 = "TypeScript · 核心篇"
C3 = "TypeScript · 进阶篇"

CJK = re.compile(r"[\u4e00-\u9fff]")


def _t(src):
    return textwrap.dedent(src).strip("\n")


def h(text):
    return {"type": "heading", "text": text}


def p(text):
    return {"type": "text", "text": text}


def code(src):
    return {"type": "code", "code": _t(src), "runnable": True}


def code_static(src):
    return {"type": "code", "code": _t(src), "runnable": False}


def out(text):
    return {"type": "output", "text": _t(text)}


def table(headers, rows):
    return {"type": "table", "headers": headers, "rows": rows}


def diagram(text):
    return {"type": "diagram", "text": _t(text)}


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


def practice(title, src, output, hint):
    return {
        "type": "practice",
        "title": title,
        "code": _t(src),
        "output": _t(output),
        "hint": hint,
    }


def steps(items):
    return {"type": "steps", "items": items}


def task(text):
    return {"type": "task", "text": text}


def fill(goal, src, answer, explain):
    return {
        "type": "fill",
        "goal": goal,
        "code": _t(src),
        "answer": answer,
        "explain": explain,
    }


def order(title, lines):
    return {"type": "order", "title": title, "lines": lines}


def exercise(title, brief, starter, hint, tests, solution, xp=90):
    return {
        "title": title,
        "brief": brief,
        "starterCode": _t(starter),
        "hint": hint,
        "tests": [_t(t) for t in tests],
        "stdin": [],
        "xp": xp,
        "solution": _t(solution),
    }


def lesson(lid, order_no, chapter, chapter_name, title, subtitle, xp, blocks, ex):
    return {
        "id": lid,
        "order": order_no,
        "chapter": chapter,
        "chapterName": chapter_name,
        "lang": "typescript",
        "title": title,
        "subtitle": subtitle,
        "xp": xp,
        "blocks": blocks,
        "exercise": ex,
    }


def prose_cjk(lesson_obj):
    """统计讲解文本里的汉字数（不含代码）。"""
    total = 0

    def add(value):
        nonlocal total
        if isinstance(value, str):
            total += len(CJK.findall(value))

    for b in lesson_obj["blocks"]:
        t = b["type"]
        if t in ("heading", "text", "tip", "warn", "task", "diagram"):
            add(b.get("text", ""))
        elif t == "table":
            for cell in b["headers"]:
                add(cell)
            for row in b["rows"]:
                for cell in row:
                    add(cell)
        elif t == "quiz":
            add(b["question"])
            for opt in b["options"]:
                add(opt)
            add(b.get("explain", ""))
        elif t == "practice":
            add(b["title"])
            add(b["hint"])
        elif t == "fill":
            add(b["goal"])
            add(b["explain"])
        elif t == "steps":
            for item in b["items"]:
                add(item)
        elif t == "order":
            add(b["title"])
            for line in b["lines"]:
                add(line)
    add(lesson_obj["title"])
    add(lesson_obj["subtitle"])
    add(lesson_obj["exercise"]["title"])
    add(lesson_obj["exercise"]["brief"])
    add(lesson_obj["exercise"]["hint"])
    return total


TS_BASICS = [
    lesson("ts01", 600, 61, C1, "TypeScript 是什么", "类型擦除与运行时的真相", 60, [
        h("先看清 TypeScript 的真面目"),
        p("TypeScript 由微软在 2012 年发布，设计者是 C# 之父 Anders Hejlsberg。它的定位不是另起炉灶，而是给 JavaScript 加一层静态类型系统：任何合法的 JavaScript 代码都是合法的 TypeScript，额外的类型语法只在编写和编译阶段生效。浏览器、Node.js、以及本应用使用的 Rhino 引擎，最终执行的都是擦掉类型之后的普通 JavaScript。理解了这一点，你就不会把类型当成运行时的魔法。"),
        p("类型擦除的流程可以拆成几步：先整段删除 interface 和 type 声明，再去掉函数名后的泛型参数表，然后擦掉变量、参数、返回值的类型标注，接着去掉 as 断言和非空断言，最后把 enum 换成一个冻结对象。前四步的结果是代码变短，语义不变；enum 是唯一会留下运行时产物的语法，所以第八讲会单独讨论它。整个过程不改动任何表达式逻辑，也不做类型转换。"),
        p("既然类型会被删掉，它到底解决了什么问题？第一是把错误提前：编辑器在你写 `damage(10)` 时就提示缺少参数，不必等到运行时才发现。第二是文档作用：一个陌生的函数签名 `function rank(users: User[], top: number): string[]` 比任何注释都直接。第三是重构安全：字段改名时，类型系统会列出所有受影响的调用点。这三件事都发生在代码运行之前，因此擦除不会损失任何收益。"),
        p("本应用的 TypeScript 是一个教学子集：支持类型标注、interface、type 别名、泛型参数、as、非空断言和 enum，不支持 class、装饰器、命名空间、抽象类，也不支持默认参数、展开运算符、async/await、可选链和空值合并。课程里所有能运行的代码都写成 ES5 风格，对象用构造函数加 prototype 模拟，这样你看到的输出就是真实引擎的输出，不是模拟器编出来的。"),
        p("课程分三包共 30 讲。基础篇解决「类型怎么写」：变量、数组、函数、interface、type、联合类型、枚举、收窄和三个极端类型。核心篇解决「类型怎么组合」：泛型、可选与只读、索引签名、函数类型、对象组合、断言、非空断言、建模和 JS 迁移。进阶篇解决「类型怎么设计」：泛型约束、条件类型、映射类型、工具类型、可辨识联合、类型守卫、声明文件、编译流程和综合项目实战。三包按顺序学，每讲的练习都建立在前面讲过的语法之上。"),
        p("学习方式建议固定成四步：先读讲解，理解这段语法在编写阶段解决什么问题；再运行示例，把输出和预期对一遍；然后做练习，让起始代码从「跑不通」变成「全部通过」；最后合上教程，用一句话向自己解释这讲的核心概念。能讲清楚，才算真的学会。遇到报错不要急着重写，先读错误信息里的行号和符号名，多数问题来自括号不匹配、拼写错误或者把类型写进了运行表达式。"),
        p("把 TypeScript 当成「带注释的 JavaScript」会更准确：注释写给读代码的人，类型写给读代码的工具。区别在于注释不会被检查，而类型会被 tsc 检查；相同点是两者都不进入运行时。你可以先用纯 JavaScript 写完整逻辑，再回头补类型，顺序反过来也成立。真正要避免的是把类型当成业务逻辑的一部分——比如用类型去校验用户输入、用类型去做数据转换，那些事情只能由运行时代码完成。把边界划清楚，你写的每一行类型标注都会是净收益。"),
        code("""
            var name: string = 'V';
            var level: number = 66;

            console.log('HELLO, ' + name);
            console.log('LEVEL ' + level);
        """),
        out("HELLO, V\nLEVEL 66"),
        table(["你写的 TS", "转译后交给 Rhino 的 JS", "运行结果"], [
            ["var n: number = 5", "var n = 5", "完全一致"],
            ["function f(a: string)", "function f(a)", "完全一致"],
            ["interface Hero { }", "整段消失", "没有任何影响"],
        ]),
        tip("在本应用里写错类型不会报错，因为这里只做语法擦除、不做类型检查。类型检查需要 tsc 或专业 IDE；本课的重点是理解类型在什么时候存在、什么时候消失。"),
        quiz("运行 `var n: number = 'abc'` 时，最可能发生什么？", [
            "引擎抛出类型错误",
            "变量 n 变成字符串 abc，程序继续运行",
            "编译阶段直接崩溃",
            "n 被自动转成数字",
        ], 1, "类型标注会被擦除，运行时只看到 `var n = 'abc'`。类型错误只有 tsc 或编辑器会指出，Rhino 不检查类型。"),
        task("把代码里的 name 和 level 换成你自己的代号与等级，运行看看输出。再试着把 level 的值改成字符串，观察程序是否仍然能跑。"),
    ], exercise(
        "带类型的问候函数",
        "实现 welcome(name, level)：返回 'HELLO, ' 拼上 name、一个空格、井号和 level。例如 welcome('V', 66) 返回 'HELLO, V #66'。",
        """
        function welcome(name: string, level: number): string {
          // 返回 'HELLO, ' + name + ' #' + level
          return '';
        }
        """,
        "注意空格和井号的位置：'HELLO, ' 后面是 name，再拼 ' #'，最后拼 level。",
        [
            "assert(welcome('V', 66) === 'HELLO, V #66', 'welcome(V,66) 应为 HELLO, V #66')",
            "assert(welcome('Judy', 30) === 'HELLO, Judy #30', '应支持不同名字与等级')",
            "assert(welcome('', 0) === 'HELLO,  #0', '空名字也要按规则拼接')",
            "assert(typeof welcome('A', 1) === 'string', '返回值应为字符串')",
        ],
        """
        function welcome(name: string, level: number): string {
          return 'HELLO, ' + name + ' #' + level;
        }
        """,
        80,
    )),

    lesson("ts02", 601, 61, C1, "变量与基础类型", "string / number / boolean 与类型推断", 70, [
        h("给变量贴上类型标签"),
        p("TypeScript 的基础类型不多：string 表示文本，number 表示数字，boolean 表示真假，此外还有 null、undefined、any、unknown、never。标注写在变量名后面、等号前面，例如 `var level: number = 66`。本课程统一使用 var，因为最终执行的是 ES5 代码；let 和 const 属于 ES6 语法，虽然 Rhino 的 ES6 模式也能跑，但为了和运行时边界保持一致，课程不依赖它们。"),
        p("大多数时候不需要手写每一个标注，TypeScript 会做类型推断：`var level = 66` 自动推断为 number，`var name = 'V'` 自动推断为 string。推断让代码保持简洁，标注则用在函数边界和公共数据结构上，因为那里是别人最容易传错值的地方。一个实用的分工是：函数参数、返回值、导出的对象必须标注；函数内部的临时变量交给推断，既不啰嗦，也不容易写错。"),
        p("类型标注是一份承诺，不是运行时转换。写 `var n: number = 'abc'` 不会把字符串变成数字，也不会阻止程序运行；它只是告诉读代码的人「这里应该放数字」。真正的转换要靠 Number()、String()、parseInt()、parseFloat() 这些函数。把标注和转换分开，是学好 TypeScript 的第一道分水岭：标注影响阅读与检查，转换才影响运行结果。"),
        p("变量还有作用域。var 声明的变量属于最近的函数作用域，而不是块作用域：在 if 或 for 的大括号里用 var 声明，循环结束后它依然存在，这一点和很多语言不同。函数内部的 var 不会污染外部，函数外部也读不到内部的局部变量。写循环时如果要在闭包里保存每一轮的值，var 会共享同一个变量，这是老代码里常见的坑，本课程不涉及闭包循环，但值得先记住结论。"),
        p("命名变量时也有类型层面的讲究。同一个概念在不同文件里用同一个词，能让类型推断和搜索都更可靠；把布尔变量命名为 isXxx、hasXxx、canXxx，读起来就是一句判断。避免用 data、info、temp 这类含义过宽的词，它们通常意味着你还没想清楚这个值代表什么。类型标注能发现拼写错误，却发现了不了命名混乱，后者只能靠团队约定和代码评审来解决。"),
        p("选择标注还是推断，可以按「契约与实现」来分。函数参数、返回值、模块导出、公共数据结构属于契约，写清楚能让调用方不必读实现；循环计数器、临时字符串、一次性的中间结果属于实现，交给推断更清爽。养成这个习惯后，代码会形成明显的层次：外圈签名密集，内圈逻辑干净。读代码的人从签名进入，从实现细节退出，认知负担最低。初学者常犯的错是反过来——内部变量标得很细，函数签名却一片空白。"),
        p("另外提醒一点：不要把类型标注写成注释的替代品。注释解释「为什么这样做」，类型说明「这里是什么」。两者各司其职，缺一不可。只写类型不写注释，读者知道结构却不知道意图；只写注释不写类型，工具帮不上忙，拼写错误也发现不了。好的代码通常两者都有，但都克制——只在必要处出现，不为凑数而写。"),
        code("""
            var name: string = 'V';
            var level: number = 66;
            var online: boolean = true;

            console.log(name, level, online);
            console.log(typeof name, typeof level, typeof online);
        """),
        out("V 66 true\nstring number boolean"),
        table(["类型", "能表示什么", "典型写法"], [
            ["string", "文本，单引号或双引号包裹", "var s: string = 'hi'"],
            ["number", "整数与小数，只有这一种数字类型", "var n: number = 3.14"],
            ["boolean", "true 或 false", "var ok: boolean = true"],
            ["null / undefined", "空值与未赋值，常与联合类型搭配", "var x: string | null = null"],
        ]),
        p("运行时只有一个数字类型 number，没有 int、float、double 之分。所有数字都是 64 位浮点数，所以 0.1 加 0.2 得到的是 0.30000000000000004，整数除法也要自己取整。TypeScript 不会改变这些底层语义，它只是在类型层面告诉你「这是数字」。同理，typeof null 返回字符串 object，这是 JavaScript 从第一版遗留至今的 bug，类型标注无法修正它，只能提醒你额外判空。"),
        warn("本应用的转译器只认语法形状。`var n: number = 'abc'` 会被擦成 `var n = 'abc'`，照常运行；但如果你把标注写成复杂的内联对象类型，例如 `var p: { x: number } = ...`，擦除可能失败并留下语法错误。课程里一律用 interface 或 type 别名描述对象，既清晰又安全。"),
        quiz("`var level = 66` 不写标注时，TypeScript 会怎么处理？", [
            "类型是 any，之后可以赋任何值",
            "推断为 number，再赋字符串会被 tsc 拒绝",
            "推断为 string",
            "必须手写标注才能通过编译",
        ], 1, "TypeScript 会根据初始值推断类型，66 推断为 number。推断只发生在编写阶段，运行时仍然是普通的 var 赋值。"),
        task("分别声明一个 string、一个 number、一个 boolean，用 typeof 打印它们的运行时类型，观察结果是否和标注一致。"),
    ], exercise(
        "角色档案卡",
        "实现 profile(name, level, active)：返回 name、level、active 三段用竖线拼起来的字符串，例如 profile('V', 66, true) 返回 'V|66|true'。",
        """
        function profile(name: string, level: number, active: boolean): string {
          // 用 '|' 拼接三个参数
          return '';
        }
        """,
        "字符串拼接用 +，注意三段之间都要有竖线，末尾不要多写。",
        [
            "assert(profile('V', 66, true) === 'V|66|true', 'profile(V,66,true) 不符合预期')",
            "assert(profile('Judy', 30, false) === 'Judy|30|false', '应支持 false 与不同等级')",
            "assert(profile('', 0, false) === '|0|false', '空名字也要保留分隔符')",
            "assert(typeof profile('A', 1, true) === 'string', '返回值应为字符串')",
        ],
        """
        function profile(name: string, level: number, active: boolean): string {
          return name + '|' + level + '|' + active;
        }
        """,
        80,
    )),

    lesson("ts03", 602, 61, C1, "数组与元组", "批量数据与固定位置", 70, [
        h("一组同类型的数据"),
        p("数组类型有两种等价写法：`number[]` 和 `Array<number>`，都表示「装满了数字的数组」。字符串数组是 `string[]`，对象数组写成 `Hero[]`，其中 Hero 是 interface 名。数组的方法本身来自 JavaScript：push、pop、slice、join、sort、map、filter 都会照常工作。TypeScript 只负责约束元素类型，让你在写 `nums.push('abc')` 时被 tsc 拦下来，而不是等到运行时才发现数组里混进了字符串。"),
        p("元组是另一种数组：长度固定、每个位置的类型固定。`var p: [string, number] = ['hp', 100]` 表示第一个元素必须是字符串、第二个必须是数字。元组适合表达「一对有明确含义的值」，例如坐标、键值对、函数返回多个结果。元素超过三个时，元组会迅速变得难以阅读，这时候应该改用 interface，让每个字段都有名字，代码才能自解释。"),
        p("转译之后，`number[]` 和 `[string, number]` 都会消失，数组还是那个数组，元组也只是普通数组。这意味着两件事：第一，运行时不会检查你放进去的元素类型；第二，越界访问不会报错，而是返回 undefined。写循环时仍然要先判断长度，访问元组下标时也要自己保证位置正确。类型的价值在于让 tsc 在编写阶段提醒你，而不是替你做运行时保护。"),
        p("数组还支持嵌套：`number[][]` 是二维数字数组，`Array<Array<string>>` 写法不同但含义一样。遍历二维数组要用两层循环，外层拿行、内层拿列。空数组声明要显式标注，例如 `var list: number[] = []`；如果只写 `var list = []`，TypeScript 可能把它推断成 never[]，后续 push 会被拒绝。先标注再使用，是数组声明的稳妥习惯。"),
        p("数组方法里有几个必须注意的细节。sort 默认按字符串比较，[10, 2, 1] 会排成 1、10、2，要按数值排序必须传比较函数 `function (a: number, b: number): number { return a - b; }`。map 和 filter 的回调参数类型可以不写，交给推断；一旦要写，回调本身也要标注参数和返回值，否则擦除后可能留下残渣。slice 返回新数组，不改变原数组；push、pop、sort 会改原数组，需要保留原数据时先 slice() 复制一份。"),
        p("遍历数组时有两套写法：传统的下标 for 循环和 forEach 回调。下标循环兼容性最好、可以中途 break、也能同时拿到索引；forEach 更接近「对每个元素做一件事」的语义，但无法提前退出。本课程以传统 for 循环为主，因为它在 ES5 里行为最稳定，也最容易在判题里复现。无论用哪种，都要记住数组长度是在循环开始时读取的，循环体内不要随意 push 或 pop，否则容易死循环或漏掉元素。"),
        p("数组和元组的区别可以这样记：数组回答「有多少个同类元素」，元组回答「每个位置分别是什么」。前者长度可变，后者长度固定。业务里绝大多数集合都是数组，元组只在「固定几个有明确含义的值」时使用，例如返回坐标、返回两个统计值、表示键值对。如果一个元组超过三个元素，几乎总是应该改成 interface 加具名字段，因为人记不住第四个位置代表什么，而字段名永远记得住。"),
        p("最后强调长度检查的两个位置：进入循环前检查一次，访问元素前再检查一次。前者用于提前返回空数组的结果，后者用于确认下标没有越界。两次检查看起来重复，但它们防的是不同的错误：一次防「没有数据」，一次防「算错了下标」。养成这个习惯，数组相关的运行时错误会少一大半，调试时间也会明显缩短。"),
        code("""
            var scores: number[] = [10, 20, 30];
            var total: number = 0;

            for (var i = 0; i < scores.length; i++) {
              total += scores[i];
            }

            console.log('count=' + scores.length);
            console.log('sum=' + total);
        """),
        out("count=3\nsum=60"),
        diagram("""
            number[]              Array<number>
            ─────────             ─────────────
            下标 0 → 10           同一种类型的另一种写法
            下标 1 → 20           运行时都是普通数组
            下标 2 → 30           类型标注会被擦除

            元组 [string, number]
            ─────────────────────
            位置 0 必须是 string
            位置 1 必须是 number
            长度固定，越界读到 undefined
        """),
        tip("空数组要显式标注：`var list: number[] = []`。这样后续 push 的元素类型才被约束住；不标注的空数组在严格模式下几乎无法使用。"),
        quiz("`var pair: [string, number] = ['hp', 100]` 中，pair[1] 的静态类型是什么？", [
            "string",
            "number",
            "string | number",
            "any",
        ], 1, "元组按位置确定类型，第二个位置标注为 number，所以 pair[1] 是 number。运行时它仍然是普通数组元素。"),
        practice("数组求和", """
            var nums: number[] = [4, 5, 6];
            var sum: number = 0;

            for (var i = 0; i < nums.length; i++) {
              sum += nums[i];
            }

            console.log(sum);
        """, "15", "循环从下标 0 开始，累加到 sum 里。"),
    ], exercise(
        "数组统计与元组标签",
        "实现 stats(nums) 返回 'count=数量,sum=总和,max=最大值'，空数组返回 'count=0,sum=0,max=0'；再实现 pairLabel(p) 把元组 ['hp', 100] 拼成 'hp=100'。",
        """
        function stats(nums: number[]): string {
          // 空数组返回 count=0,sum=0,max=0
          return '';
        }

        type Pair = [string, number];

        function pairLabel(p: Pair): string {
          // 返回 p[0] + '=' + p[1]
          return '';
        }
        """,
        "先处理空数组；非空时用第一个元素初始化 max，再从下标 1 开始比较。pairLabel 直接拼两个位置。",
        [
            "assert(stats([10, 20, 30]) === 'count=3,sum=60,max=30', '普通数组统计错误')",
            "assert(stats([5]) === 'count=1,sum=5,max=5', '单元素数组统计错误')",
            "assert(stats([]) === 'count=0,sum=0,max=0', '空数组要有默认结果')",
            "assert(pairLabel(['hp', 100]) === 'hp=100', '元组标签拼接错误')",
        ],
        """
        function stats(nums: number[]): string {
          if (nums.length === 0) {
            return 'count=0,sum=0,max=0';
          }
          var sum: number = 0;
          var max: number = nums[0];
          for (var i = 0; i < nums.length; i++) {
            sum += nums[i];
            if (nums[i] > max) {
              max = nums[i];
            }
          }
          return 'count=' + nums.length + ',sum=' + sum + ',max=' + max;
        }

        type Pair = [string, number];

        function pairLabel(p: Pair): string {
          return p[0] + '=' + p[1];
        }
        """,
        90,
    )),

    lesson("ts04", 603, 61, C1, "函数签名", "参数与返回值是契约", 70, [
        h("函数是类型最重要的战场"),
        p("函数签名由参数类型和返回值类型组成。参数标注写在参数名后面，返回值标注写在参数括号后面、函数体前面。`function damage(base: number, mult: number): number` 表达了一份契约：调用者必须提供两个数字，函数承诺返回一个数字。签名一旦确定，函数体怎么改都不影响调用方，这就是接口稳定的价值，也是团队协作里最值得投入的文档。"),
        p("箭头函数也能标注，写法是 `(n: number): number => n * 2`。回调函数通常不内联写类型，而是先用 type 别名定义：`type Op = (n: number) => number;` 然后写 `function apply(n: number, op: Op): number`。这样做不只是风格问题——本应用的转译器对内联函数类型支持不好，`op: (n: number) => number` 这样的标注会在擦除时留下残渣，导致语法错误。拆成别名既符合工程习惯，也绕开了运行时限制。"),
        p("可选参数用问号标记：`function greet(name: string, title?: string)`。调用时可以只传一个参数，函数体里读取 title 得到的是 undefined，所以必须先判断再使用。本应用不支持默认参数语法 `function f(a: number = 1)`，它会在 Rhino 里直接报语法错误；需要默认值时，在函数体开头写 `if (a === undefined) { a = 1; }`，效果一样，兼容性更好。"),
        p("返回值标注有一个常见误区：它不会把返回值转换成目标类型。`function f(): string { return 123; }` 在本应用里会原样返回数字，因为标注被擦掉了；只有 tsc 会报错。另一个误区是给没有返回值的函数标 `: void`——本应用的转译器对 void 标注处理不稳定。课程统一省略无返回值函数的返回标注，用注释说明意图。记住：签名是给写代码的人看的约束，不是运行时的转换器。"),
        p("写函数签名时，参数的顺序和命名同样重要。把最重要的参数放前面，把可选的、带默认语义的参数放后面；参数名用动词或名词短语，避免 a、b、c 这类无法自解释的短名。纯函数——同样的输入永远得到同样的输出、不修改外部状态——最容易标注也最容易测试，因为它的签名就是完整的行为说明。有副作用的函数则要在名字或注释里说清楚它改了什么，类型系统无法表达副作用，只能靠约定。"),
        p("函数的返回类型还有两个特殊标记：void 表示不返回有意义的值，never 表示永远不会正常返回。本应用的转译器对 void 处理不稳定，课程统一省略无返回值函数的标注；never 只用于总是抛异常的函数，第十讲会再见到它。另一个实用习惯是让函数尽量短，一个函数只做一件事，签名自然就简单，测试也好写。函数超过三十行时，先想想能不能拆成两个职责更清晰的函数。"),
        p("函数签名写好后，就把它当成不可随意改动的合同。改参数名不影响调用方，改参数顺序和类型则一定会；新增可选参数是兼容的，把可选改成必填则不兼容。理解这一点，你就能判断一次改动会不会影响其他模块。本课程虽然只有一个文件，但同样的判断在真实项目里每天都在发生。养成「先想签名再写实现」的顺序，返工会少很多，因为最难改的永远是被别人依赖的那部分。"),
        p("还有一个小技巧：把复杂函数拆成「签名简单、职责单一」的小函数后，类型标注会自然变短。一个接收五个参数、返回嵌套对象的函数，签名很难看清；拆成两个各接收两三个参数的函数，签名一眼就能读完。类型复杂度往往不是类型系统的问题，而是函数设计的问题。签名难写时，先回头看看函数是不是承担了太多职责，通常能一举两得。"),
        code("""
            type Op = (n: number) => number;

            function add(a: number, b: number): number {
              return a + b;
            }

            function twice(n: number, op: Op): number {
              return op(op(n));
            }

            console.log(add(2, 3));
            console.log(twice(5, function (n: number): number {
              return n + 1;
            }));
        """),
        out("5\n7"),
        table(["签名部分", "示例", "作用"], [
            ["参数类型", "a: number", "限制调用者传什么"],
            ["返回类型", ": number", "限制函数体返回什么"],
            ["可选参数", "b?: number", "允许省略，读取时可能是 undefined"],
            ["函数类型别名", "type Op = (n: number) => number", "描述回调的形状"],
        ]),
        warn("本应用不支持默认参数、剩余参数和函数重载的真实运行语义。`function f(a: number = 1)` 会直接语法错误；`function f(...args: number[])` 里的展开运算符也不被支持。需要可变参数时，改为传入数组并在函数体里遍历。"),
        quiz("`function f(a: number): string` 中，`: string` 约束的是什么？", [
            "参数 a 的类型",
            "函数返回值的类型",
            "函数名 f 的类型",
            "调用时的 this 类型",
        ], 1, "参数括号后面的标注属于返回值，参数自己的类型写在参数名后面。"),
        task("给 practice 里的函数加一个参数，再修改返回值类型标注，观察运行时输出是否变化。"),
    ], exercise(
        "带签名的加成计算",
        "实现 bonus(base, rate)：返回 base 乘以 (1 + rate) 后四舍五入的整数。bonus(100, 0.5) 返回 150。",
        """
        function bonus(base: number, rate: number): number {
          // 先算 base * (1 + rate)，再用 Math.round 取整
          return 0;
        }
        """,
        "表达式是 Math.round(base * (1 + rate))，注意括号不要漏。",
        [
            "assert(bonus(100, 0.5) === 150, '100 加成 50% 应为 150')",
            "assert(bonus(50, 0) === 50, '加成为 0 应保持原值')",
            "assert(bonus(99, 0.1) === 109, '108.9 四舍五入应为 109')",
            "assert(bonus(10, -0.5) === 5, '负加成也要算对')",
        ],
        """
        function bonus(base: number, rate: number): number {
          return Math.round(base * (1 + rate));
        }
        """,
        90,
    )),

    lesson("ts05", 604, 61, C1, "interface", "给对象画一张形状说明书", 80, [
        h("对象长什么样，一次说清楚"),
        p("JavaScript 的对象是开放的：运行时想加什么字段就加什么字段。这很灵活，也很容易出错。interface 用声明的方式描述对象形状：有哪些字段、每个字段是什么类型、哪些字段可以省略、哪些字段只读。例如 `interface Hero { name: string; level: number; }` 表示一个 Hero 必须同时拥有 name 和 level，且类型分别是 string 和 number。任何拿到 Hero 的函数，都可以放心访问这两个字段。"),
        p("interface 可以继承：`interface Boss extends Hero { phase: number; }` 表示 Boss 拥有 Hero 的全部字段，再加一个 phase。继承让小的形状可以组合成大的形状，避免重复抄写。interface 还支持可选属性 `age?: number` 和只读属性 `readonly id: number`，前者表示字段可能不存在，后者表示初始化后不应再赋值。这两种修饰都只影响编写阶段的检查，运行时既不删除字段，也不冻结对象。"),
        p("interface 是 TypeScript 里最纯粹的零成本抽象：转译时整段删除，不生成任何代码，也不影响对象结构。它的收益全部在编写阶段——编辑器能提示字段名、检查拼写、在字段改名时找到所有使用点。一个常见的误解是「interface 会创建类」，不会。它既不创建构造函数，也不做运行时校验；`var v: Hero = { name: 'V' }` 少了 level 也能跑，只是 tsc 会报错。"),
        p("工程上建议把 interface 放在文件顶部，与使用它的函数分开，命名用大驼峰，字段用 camelCase。描述公共 API、组件 props、领域模型时优先用 interface；只出现一次的临时对象不必单独建 interface，交给类型推断更轻。interface 之间还可以同名声明合并，但本应用的转译器会把每个 interface 整段删除，合并语义只在真正的 tsc 里有效，课程不依赖这个特性。"),
        p("interface 和 class 经常被混淆。class 会创建构造函数、生成实例、带有运行时行为；interface 只描述形状，不产生任何运行时代码。本应用甚至不支持 class 语法，所有对象都用对象字面量或构造函数加 prototype 创建。这并不妨碍你用好 interface：函数的参数、返回值、数组元素、配置对象，都可以用 interface 描述，代码依然清晰，只是运行时看不到这层描述而已。"),
        p("interface 里的方法可以写成属性形式，也可以写成方法简写形式。本应用支持属性形式 `run: (v: number) => number`（配合 type 别名），对方法简写支持不稳定，所以课程统一用属性形式描述回调字段。字段之间用分号分隔，最后一个字段后面的分号可以省略，但建议保留，将来增删字段时不容易漏。缩进统一两个空格，嵌套对象要逐层缩进，长 interface 才能一眼看清层级。"),
        p("interface 的字段应该描述「稳定的结构」，而不是「某一次调用的临时形状」。判断标准是：这个对象会不会在多个函数之间传递？会不会被序列化成 JSON 存起来？如果会，就值得为它建一个 interface 并命名。临时拼装、用完即弃的对象则不必。另一个实践是把 interface 的字段按重要性排序：标识字段在前、业务字段居中、元数据在后。顺序本身没有语法意义，但它能帮助读者快速抓住这个结构的主干。"),
        p("实践中最容易忽略的是 interface 的演化成本。给一个已被广泛使用的 interface 加必填字段，会让所有构造该对象的地方报错；加可选字段则不会。所以在公共接口上新增字段时，优先考虑可选，或者在类型文件里同时保留新旧两个版本，用别名标记废弃。类型不是写完就不动的，它和代码一样需要版本管理的意识。"),
        code("""
            interface Hero {
              name: string;
              level: number;
            }

            interface Boss extends Hero {
              phase: number;
            }

            var v: Hero = { name: 'V', level: 66 };
            var boss: Boss = { name: 'Judy', level: 99, phase: 2 };

            console.log(v.name, v.level);
            console.log(boss.name, boss.phase);
        """),
        out("V 66\nJudy 2"),
        diagram("""
            你写的代码                        运行时
            ─────────────────────           ─────────────────
            interface Hero { ... }    ──►   整段删除，不生成变量
            var v: Hero = { ... }     ──►   var v = { ... }
            v.level                   ──►   v.level

            类型只在编写阶段存在，运行时只有对象本身。
        """),
        tip("interface 适合描述公共 API、组件 props、领域模型。命名用大驼峰，字段用 camelCase；不要把 interface 写成一次性局部变量的形状说明书，那种场景交给推断。"),
        warn("interface 在转译时按花括号配平整段删除，所以不要把它写在字符串以外的奇怪位置。把 interface 放在文件顶部、与使用它的函数分开，既符合习惯，也避免擦除时牵连其他代码。"),
        quiz("运行时执行 `var v: Hero = { name: 'V', level: 66 }`，实际得到的是？", [
            "一个 Hero 类的实例",
            "一个带类型标签的普通对象",
            "一个普通对象 { name: 'V', level: 66 }",
            "报错，因为缺少构造函数",
        ], 2, "interface 和类型标注都会被删除，运行时只剩对象字面量本身。"),
        task("给 Hero 增加一个可选字段 title，再创建两个对象：一个有 title，一个没有，分别打印。"),
    ], exercise(
        "英雄名片",
        "用 interface Hero 描述 name、level、title 三个字段，实现 intro(h) 返回 '名字 the 头衔 (等级)'，例如 'V the Hacker (66)'。",
        """
        interface Hero {
          name: string;
          level: number;
          title: string;
        }

        function intro(h: Hero): string {
          // 返回 h.name + ' the ' + h.title + ' (' + h.level + ')'
          return '';
        }
        """,
        "按顺序拼接四段：名字、' the '、头衔、' (' + 等级 + ')'。注意空格。",
        [
            "assert(intro({name:'V', level:66, title:'Hacker'}) === 'V the Hacker (66)', '名片格式错误')",
            "assert(intro({name:'Judy', level:30, title:'Runner'}) === 'Judy the Runner (30)', '应支持不同英雄')",
            "assert(intro({name:'', level:0, title:'Ghost'}) === ' the Ghost (0)', '空名字与 0 级也要能拼')",
            "assert(typeof intro({name:'A', level:1, title:'B'}) === 'string', '返回值应为字符串')",
        ],
        """
        interface Hero {
          name: string;
          level: number;
          title: string;
        }

        function intro(h: Hero): string {
          return h.name + ' the ' + h.title + ' (' + h.level + ')';
        }
        """,
        90,
    )),

    lesson("ts06", 605, 61, C1, "type 别名", "给任何类型起个短名字", 70, [
        h("类型也可以有名字"),
        p("interface 只能描述对象，type 别名能命名任何类型：`type Id = string` 给基础类型起名，`type Point = { x: number; y: number }` 给对象形状起名，`type Status = 'on' | 'off'` 给联合类型起名，`type Op = (n: number) => number` 给函数类型起名。它本质上是文本替换：所有出现 Id 的地方，编译器都当作 string 处理。运行时代码里不会留下任何痕迹。"),
        p("type 和 interface 有明确的分工。interface 可以被 extends 继承、可以同名合并、错误信息更友好；type 能表达联合、交叉、元组、函数、条件类型等更自由的组合。一个常见的经验法则是：描述对象结构优先用 interface，需要组合或命名非对象类型时用 type。两者并不对立，同一个项目混用很正常，关键是团队内保持一致。"),
        p("type 别名还可以嵌套引用，从而把复杂类型拆成可读的层次。例如先定义 `type OrderId = string`，再定义 `type OrderStatus = 'pending' | 'paid' | 'shipped'`，最后写 `interface Order { id: OrderId; status: OrderStatus; total: number; }`。这样业务语义被名字固定下来，函数签名一眼就能读懂，也能避免同一个概念在不同文件里写成不同形状。"),
        p("本应用的转译器按行删除 `type X = ...;` 声明：只要一行以 type 开头并包含等号，就会整行删掉；如果类型体跨多行并且含有花括号，会按花括号配平继续删除。因此 type 别名要和别的语句分开写，不要写在一行中间，也不要在别名里放函数调用这类运行时代码。它本来就只应该出现在类型层，这一点和 TypeScript 的设计完全一致。"),
        p("类型别名不创建运行时对象，也不做任何校验。它的全部价值在于给一段类型表达式起名字，让签名变短、让概念固定。工程上建议先建领域词汇表：把 Id、Status、Money、Timestamp 这些概念定义成别名，再在 interface 里引用它们。这样将来把 Id 从 string 改成 number，只需要改一行别名，所有引用处自动跟着变。命名带来的这种「单点修改」能力，是类型系统最实用的收益之一。"),
        p("类型别名可以互相引用，但不能循环引用。`type A = B; type B = A;` 会让编译器陷入无限展开，tsc 会直接报错。正常业务里也很少需要循环引用，如果出现了，通常说明建模有问题：要么应该拆成两个独立概念，要么应该用 interface 的递归结构（例如树节点引用自身）。递归类型是合法且有用的，例如 `interface TreeNode { value: number; children: TreeNode[] }`，它描述的是数据结构的嵌套，而不是类型之间的循环定义。"),
        p("type 别名和常量一样，命名要表达「它代表什么」而不是「它由什么构成」。`type Id = string` 好过 `type StringType = string`，`type Status = 'on' | 'off'` 好过 `type TwoStrings = 'on' | 'off'`。名字是给未来的自己看的，等三个月后回来，你只会记得业务概念，不会记得当时的类型表达式。另外，别名一经发布就应尽量稳定：改名字会让所有引用点报错，虽然编译器能帮你改，但在多人协作里仍然是一次不必要的打扰。"),
        p("最后一个建议：把类型别名按「从具体到抽象」的顺序排列。先放基础别名（Id、Cents、Timestamp），再放枚举式联合（Status、Role），最后放实体（Order、User）。读的人从上往下，概念由简单到复杂，理解成本最低。反过来排列也能工作，但读者会在第一个实体定义里遇到一堆没见过的别名，不得不来回跳转，体验差很多。"),
        p("补一个使用场景：当你需要给「函数返回多个值」建模时，type 别名配合元组很短；但本应用不支持内联元组返回类型，所以课程里用 type 先命名再使用。命名之后，签名变成 `function split(text: string): Pair`，读者不必在签名里解析 `[string, string]` 这种没有语义的位置信息。给位置起名字，是元组和别名配合的最大价值。"),
        code("""
            type Id = string;
            type Point = { x: number; y: number };
            type Status = 'on' | 'off';

            var id: Id = 'agent-7';
            var p: Point = { x: 3, y: 4 };
            var status: Status = 'on';

            console.log(id);
            console.log(p.x + p.y);
            console.log(status);
        """),
        out("agent-7\n7\non"),
        table(["能力", "interface", "type 别名"], [
            ["描述对象形状", "可以", "可以"],
            ["命名联合类型", "不可以", "可以"],
            ["命名基础类型", "不可以", "可以"],
            ["继承 / 扩展", "extends 继承", "用 & 交叉组合"],
            ["同名合并", "支持", "不支持"],
        ]),
        tip("给返回值命名时，type 别名能显著提升签名可读性。`function parse(text: string): Result` 比 `function parse(text: string): { ok: boolean; data: string[] }` 容易读得多，后者只适合一次性的内部形状。"),
        warn("type 别名不支持同名合并，写两次会报「重复标识符」。需要扩展时用交叉 `type AB = A & B`，或者改用 interface 的 extends。本应用不支持 `&` 的真实运行语义，交叉类型只能出现在类型标注里，运行时代码仍需手工合并字段。"),
        quiz("下面哪一项只能用 type 别名、不能用 interface 表达？", [
            "带 name 与 level 的对象",
            "字符串或数字的联合类型",
            "带可选字段的对象",
            "带方法的对象",
        ], 1, "interface 只能描述对象形状；联合类型、基础类型、元组、函数类型都必须用 type 别名命名。"),
        practice("给状态起名", """
            type Status = 'idle' | 'run' | 'done';

            var s: Status = 'run';
            console.log(s === 'run');
        """, "true", "类型别名被擦除，运行时只剩字符串比较。"),
    ], exercise(
        "用别名描述订单",
        "先定义 OrderId、OrderStatus、Order 三个类型别名，再实现 describe(order) 返回 '订单号 状态 金额'，例如 describe({id:'A1', status:'paid', total:30}) 返回 'A1 paid 30'。",
        """
        type OrderId = string;
        type OrderStatus = 'pending' | 'paid' | 'shipped';
        type Order = { id: OrderId; status: OrderStatus; total: number };

        function describe(order: Order): string {
          // 返回 id + ' ' + status + ' ' + total
          return '';
        }
        """,
        "三个字段用空格连接；status 是字符串字面量联合，运行时就是普通字符串。",
        [
            "assert(describe({id:'A1', status:'paid', total:30}) === 'A1 paid 30', '订单描述格式错误')",
            "assert(describe({id:'B2', status:'pending', total:0}) === 'B2 pending 0', '0 金额也要输出')",
            "assert(describe({id:'C3', status:'shipped', total:99}) === 'C3 shipped 99', '应支持第三种状态')",
            "assert(typeof describe({id:'D4', status:'paid', total:1}) === 'string', '返回值应为字符串')",
        ],
        """
        type OrderId = string;
        type OrderStatus = 'pending' | 'paid' | 'shipped';
        type Order = { id: OrderId; status: OrderStatus; total: number };

        function describe(order: Order): string {
          return order.id + ' ' + order.status + ' ' + order.total;
        }
        """,
        90,
    )),

    lesson("ts07", 606, 61, C1, "联合类型与字面量类型", "一个位置，几种可能", 80, [
        h("用竖线表达「或」"),
        p("联合类型用竖线把多个类型连起来：`string | number` 表示这个值要么是字符串、要么是数字。它最常见的用途是描述「输入形态不固定」的参数，例如一个既能接收用户 ID 数字、也能接收用户名的函数。使用联合类型的值之前，必须先判断当前是哪一种，否则只能调用两种类型都支持的方法，而这样的方法往往很少。"),
        p("字面量类型更严格：它不是「字符串」，而是「某几个具体字符串之一」。`type Status = 'pending' | 'paid' | 'shipped'` 表示 status 只能取这三个值，写 'canceled' 会被 tsc 拒绝。字面量类型常和联合类型搭配，用来模拟枚举，优点是零运行时开销——转译后什么都不剩，运行时只有普通字符串。数字字面量也支持，例如 `type Dice = 1 | 2 | 3 | 4 | 5 | 6`。"),
        p("联合类型有一个重要规则：访问属性时必须对所有成员都合法。`var v: string | number; v.length` 会报错，因为 number 没有 length。这时要么先用 typeof 收窄，要么用类型断言明确告诉编译器「我知道现在是什么」。收窄是更安全的做法，断言则把责任交给开发者。第九讲会专门讲 typeof 收窄，这里先建立「先判断、后使用」的直觉。"),
        p("字面量联合还有一个实用技巧：配合 switch 使用。`type Shape = 'circle' | 'square'`，函数里 `switch (shape) { case 'circle': ...; case 'square': ...; }`，tsc 能检查你是否漏掉了某个分支。这种「穷尽检查」在业务状态机里非常有价值，因为新增一个状态时，所有没处理它的地方都会亮红，不会等到线上才发现某条分支返回 undefined。"),
        p("使用联合类型时，函数末尾要准备一个兜底分支。即使你认为所有情况都覆盖了，运行时仍可能收到意料之外的值，尤其是数据来自外部接口时。兜底分支可以返回默认值、抛异常或者记录日志，但不要让它悄悄返回 undefined。字面量联合的穷尽检查只在 tsc 下有效，本应用不做类型检查，所以兜底分支是运行时真正的最后一道防线，不能省。"),
        p("联合类型和可选属性容易混淆。`{ status?: 'on' | 'off' }` 表示字段可以不存在；`{ status: 'on' | 'off' }` 表示字段必须存在，但值只能是两个之一。前者读取时要判 undefined，后者不用。设计 API 时先想清楚「字段缺失」和「字段有值但为空」是不是一回事：缺失通常表示调用者没提供，空值表示调用者明确提供了空。把这两种情况混成一个可选字段，是后期 bug 的常见来源。"),
        p("联合类型的成员数量要控制。两三个成员时，代码读起来像自然语言；超过五个，判断逻辑会迅速膨胀，这时应该改用可辨识联合或拆分成多个函数。另一个实践是给联合类型起名：`string | number` 直接写在签名里还能接受，`'pending' | 'paid' | 'shipped' | 'refunded' | 'closed'` 就必须起名，否则同一个联合会在十个地方重复出现，改一处漏九处。命名是控制复杂度的第一手段。"),
        p("写联合类型的判断时，把「最可能出现的成员」放在最前面。运行时 if 从上往下判断，热点分支靠前能减少比较次数；更重要的是，读者第一眼看到的是最常见的情况，理解主干更快。异常分支放最后，并用注释或命名标出它是兜底。这个顺序对性能的影响微乎其微，但对可读性的影响很明显。"),
        code("""
            type Status = 'pending' | 'paid' | 'shipped';

            function badge(status: Status): string {
              if (status === 'paid') {
                return '[PAID]';
              }
              if (status === 'shipped') {
                return '[SHIPPED]';
              }
              return '[PENDING]';
            }

            console.log(badge('paid'));
            console.log(badge('pending'));
        """),
        out("[PAID]\n[PENDING]"),
        diagram("""
            type Status = 'pending' | 'paid' | 'shipped'
                                │
                                ├─ 只允许这三个字符串
                                ├─ 写别的值 → tsc 报错
                                └─ 运行时 → 就是普通字符串

            string | number
                                │
                                ├─ typeof v === 'string' → 按字符串用
                                └─ typeof v === 'number' → 按数字用
        """),
        tip("字面量联合适合状态、方向、等级这类封闭集合。集合会长期扩张、又需要运行时遍历时，改用 enum 更方便，因为 enum 会生成真实对象。"),
        warn("联合类型的竖线在 JavaScript 里是按位或运算符。如果转译器漏擦，`string | number` 会被当成表达式求值，得到 NaN 或 0。所以类型标注必须写在冒号后面、由转译器整体识别，不能把类型拼进运行表达式。"),
        quiz("`type Code = 'A' | 'B'`，那么 `var c: Code = 'C'` 在 tsc 下会怎样？", [
            "正常运行，c 的值是 C",
            "编译报错，C 不在联合成员里",
            "c 自动变成 undefined",
            "c 被转成数字",
        ], 1, "字面量联合限定了取值范围，'C' 不在 'A' | 'B' 里，tsc 会在编译阶段报错。运行时因为类型被擦除，仍然会赋值成功。"),
        practice("状态判断", """
            type Status = 'on' | 'off';

            function isOn(s: Status): boolean {
              return s === 'on';
            }

            console.log(isOn('on'), isOn('off'));
        """, "true false", "字面量比较就是普通字符串比较。"),
    ], exercise(
        "支付状态机",
        "实现 statusText(status)：'pending' 返回 'wait'，'paid' 返回 'ok'，'shipped' 返回 'sent'，其他值返回 'unknown'。再实现 isFinal(status)：只有 'shipped' 返回 true。",
        """
        type Status = 'pending' | 'paid' | 'shipped';

        function statusText(status: Status): string {
          // pending → wait，paid → ok，shipped → sent
          return '';
        }

        function isFinal(status: Status): boolean {
          // 只有 shipped 是最终态
          return false;
        }
        """,
        "statusText 用 if 依次判断三个值；isFinal 直接返回 status === 'shipped'。",
        [
            "assert(statusText('pending') === 'wait', 'pending 应为 wait')",
            "assert(statusText('paid') === 'ok', 'paid 应为 ok')",
            "assert(statusText('shipped') === 'sent', 'shipped 应为 sent')",
            "assert(isFinal('shipped') === true && isFinal('paid') === false, 'isFinal 只在 shipped 时为 true')",
        ],
        """
        type Status = 'pending' | 'paid' | 'shipped';

        function statusText(status: Status): string {
          if (status === 'pending') {
            return 'wait';
          }
          if (status === 'paid') {
            return 'ok';
          }
          return 'sent';
        }

        function isFinal(status: Status): boolean {
          return status === 'shipped';
        }
        """,
        90,
    )),

    lesson("ts08", 607, 61, C1, "枚举", "唯一会留下运行时产物的类型", 90, [
        h("给一组常量起名字"),
        p("枚举用 enum 声明一组有名字的常量。默认从 0 开始自动编号：`enum Level { Low, Mid, High }` 中三个成员依次是 0、1、2。也可以手动指定起点，后面的成员接着加一：`enum Level { Low = 1, Mid, High }` 得到 1、2、3。手动指定某个成员后，它后面的成员会以它为基准继续递增，这个细节在算值时经常被忽略。"),
        p("enum 是 TypeScript 里最特殊的存在：interface、type、类型标注在转译后全部消失，enum 却会变成一个真实对象。本应用的转译器把它转换成 `var Level = Object.freeze({ Low: 0, Mid: 1, High: 2 })`，用 Object.freeze 冻结，防止运行时被篡改。这也是为什么 enum 可以直接在 console.log 里打印、可以被 for 循环遍历键名，而 interface 完全做不到。"),
        p("枚举的典型用途是替代魔法数字。代码里到处写 0、1、2，过一周就没人记得哪个是哪个；写成 Level.Low、Level.Mid，含义立刻清楚。枚举还提供了一个约束：函数参数标注为 `level: Level` 后，调用者只能传枚举成员或对应数字，传一个无关字符串会被 tsc 拒绝。运行时虽然不做检查，但代码可读性和编写阶段的保护都已经到位。"),
        p("本应用的 enum 只支持数值成员和无初始化成员，不支持字符串成员。`enum Dir { Up = 'u' }` 在标准 TypeScript 里合法，但这里的转译器会把它拼进对象字面量，遇到引号时行为不可靠，所以课程统一用数值枚举。需要字符串常量时，改用字面量联合 `type Dir = 'up' | 'down'`，同样安全，而且零运行时开销。选哪种取决于你是否需要在运行时遍历或打印这组值。"),
        p("枚举值一旦写进数据库或日志，就变成了长期契约。发布之后修改某个成员的数字，会让历史数据无法对应；删除成员更危险，旧数据会变成未知值。稳妥的做法是显式写全每个成员的值，并在注释里记录每个值的业务含义；确实需要下线时，保留成员但标记为废弃，而不是直接删掉。枚举适合稳定的、封闭的、需要运行时存在的常量集合，不适合频繁变动的配置。"),
        p("枚举和字面量联合的取舍可以总结成一张简单的判断表：需要在运行时遍历成员、需要打印成员名、需要把数值存进数据库，选枚举；只在类型层约束取值范围、追求零运行时开销，选字面量联合。两者都能提供编写阶段的检查，区别只在运行时是否留下对象。同一个项目里混用也没问题，关键是同一组常量不要两种写法各来一份，否则迟早出现对不上的情况。"),
        p("枚举适合「需要运行时存在」的封闭集合。判断方法很简单：这个值会不会被打印、被存储、被网络传输？会，就用枚举或字符串常量；只在函数之间传递、只在类型层约束，就用字面量联合。两者都能提供编写阶段的检查，区别只在运行时是否留下对象。混用没有问题，但要避免同一个概念同时存在枚举和联合两份定义——那一定会出现某天只改了一边的情况。"),
        code("""
            enum Level {
              Low,
              Mid = 10,
              High
            }

            console.log(Level.Low);
            console.log(Level.Mid);
            console.log(Level.High);
            console.log(Level.High === 11);
        """),
        out("0\n10\n11\ntrue"),
        table(["成员", "值", "来源"], [
            ["Low", "0", "没有初始化，从 0 开始"],
            ["Mid", "10", "手动指定"],
            ["High", "11", "接着上一个成员加一"],
        ]),
        p("枚举在编译后仍然存在，这意味着它可以跨模块传递、可以存进数据库、可以在日志里打印。这既是优点也是负担：一旦发布，枚举的数值就变成了对外契约，改动会让历史数据对不上。所以生产项目里常把数值显式写全，例如 `Low = 0, Mid = 10, High = 11`，不依赖自动递增，将来插入新成员也不会意外改变已有值。"),
        warn("enum 是唯一「擦除后还留下东西」的常见 TypeScript 特性。不要以为所有类型语法都免费——每增加一个 enum，运行时就多一个对象。集合很小、只在类型层使用时，字面量联合更轻。"),
        quiz("`enum E { A, B = 5, C }` 中 C 的值是多少？", [
            "2",
            "5",
            "6",
            "undefined",
        ], 2, "C 没有显式初始化，会接着上一个成员 B 的值 5 加一，得到 6。"),
        task("把 Level 的 Mid 改成 100，重新运行，观察 High 的值如何跟着变化。"),
    ], exercise(
        "段位与经验值",
        "用 enum Rank 定义 Rookie=0、Hacker=1、Legend=2，实现 rankName(rank) 返回对应小写名字，实现 nextRank(rank) 返回下一段位（Legend 仍是 Legend）。",
        """
        enum Rank {
          Rookie,
          Hacker,
          Legend
        }

        function rankName(rank: Rank): string {
          // Rookie → rookie，Hacker → hacker，Legend → legend
          return '';
        }

        function nextRank(rank: Rank): Rank {
          // Legend 保持不变，其余 +1
          return Rank.Rookie;
        }
        """,
        "rankName 用 if 依次比较枚举成员；nextRank 先判断 rank === Rank.Legend，再返回 rank + 1。",
        [
            "assert(rankName(Rank.Rookie) === 'rookie', 'Rookie 应为 rookie')",
            "assert(rankName(Rank.Hacker) === 'hacker', 'Hacker 应为 hacker')",
            "assert(nextRank(Rank.Rookie) === Rank.Hacker, 'Rookie 的下一段是 Hacker')",
            "assert(nextRank(Rank.Legend) === Rank.Legend, 'Legend 已封顶')",
        ],
        """
        enum Rank {
          Rookie,
          Hacker,
          Legend
        }

        function rankName(rank: Rank): string {
          if (rank === Rank.Rookie) {
            return 'rookie';
          }
          if (rank === Rank.Hacker) {
            return 'hacker';
          }
          return 'legend';
        }

        function nextRank(rank: Rank): Rank {
          if (rank === Rank.Legend) {
            return Rank.Legend;
          }
          return rank + 1;
        }
        """,
        100,
    )),

    lesson("ts09", 608, 61, C1, "类型收窄 typeof", "先判断，再使用", 80, [
        h("让类型跟着条件变窄"),
        p("联合类型让一个值有多种可能，但真正使用时你只能确定其中一种。类型收窄就是通过运行时判断，让编译器在某个分支内把类型缩小。最常用的是 typeof：`typeof v === 'string'` 为真时，分支内的 v 被收窄为 string；`typeof v === 'number'` 时被收窄为 number。这不是运行时的新机制，typeof 本来就是 JavaScript 运算符，TypeScript 只是在类型层面读懂了它。"),
        p("typeof 的返回值只有几种：'string'、'number'、'boolean'、'undefined'、'object'、'function'、'symbol'、'bigint'。注意两个陷阱：`typeof null` 返回 'object'，所以判 null 要单独写 `v === null`；`typeof []` 也返回 'object'，区分数组要用 `Array.isArray(v)`。这两个陷阱来自 JavaScript 的历史设计，TypeScript 不会替你修正，只会在类型层面配合你写的判断。"),
        p("除了 typeof，还有几种常见收窄方式。判等字面量：`if (status === 'paid')` 把联合类型收窄到 'paid'。判 null/undefined：`if (v !== null)` 排除 null。in 运算符：`if ('name' in obj)` 判断某个属性是否存在。instanceof：判断对象是不是某个构造函数的实例。本应用支持前三种；instanceof 虽然 Rhino 能跑，但课程里的对象都用普通对象字面量构造，很少需要它。"),
        p("收窄的价值在于把「可能出错」变成「不可能出错」。没有收窄时，访问 `v.length` 需要先断言 v 是字符串；有收窄后，分支内编译器已经知道它是字符串，属性访问、方法调用全部合法。更重要的是，收窄是运行时真实发生的判断，所以它同时保护了程序不崩溃——这和 as 断言有本质区别，断言只是让编译器闭嘴，运行时该崩还是崩。"),
        p("收窄最常见的写法是提前返回，而不是层层嵌套。先把异常情况挡在函数开头：`if (v === null) { return 0; }`，后面的代码就自动处于「v 不是 null」的分支里，不需要再缩进。这种「守卫子句」让主逻辑保持在最外层，可读性远好于金字塔式的 if 嵌套。循环里同理，先判断数组长度，再进入循环，循环体内就可以放心访问元素。"),
        p("typeof 收窄还有一个容易忽略的细节：判断顺序会影响结果。如果先判断 `typeof v === 'object'`，null 也会进入这个分支，所以必须紧接着判 `v !== null`。数组也会进入 object 分支，需要再用 Array.isArray 区分。把最常见的类型放在最前面、把兜底放在最后，能让分支结构最清晰。判断条件尽量互斥，避免一个值同时满足多个分支，导致后面的分支永远执行不到。"),
        p("把收窄写成小函数，可以让主逻辑更干净。例如 `function isText(v: unknown): boolean { return typeof v === 'string'; }`，调用处写 `if (isText(v))`。不过普通布尔返回值不会让 TypeScript 收窄类型，真正能让编译器跟着收窄的是类型守卫函数 `function isText(v: unknown): v is string`，这个语法在第二十六讲详细展开。本讲先用内联 typeof，把判断逻辑写在使用现场最直观。"),
        p("收窄写得好，函数会呈现「先排除、再处理」的结构：开头几个 if 把 null、undefined、错误类型挡掉，剩下的代码在确定的类型里展开。这种结构比层层嵌套的 if-else 好读得多，也更容易测试——每个提前返回的分支都是一个独立的边界用例。写练习时可以先列出所有非法输入，再写对应守卫，最后写主逻辑。顺序清楚，代码自然清楚。"),
        p("还有一个易错点：收窄之后的变量仍然是同一个变量，运行时它的值不会因为类型变窄而改变。`if (typeof v === 'string')` 只是让编译器知道分支内 v 是字符串，v 本身还是原来那个值。所以收窄不能替代转换：如果分支内需要数字，仍然要写 Number(v)。类型收窄管「能不能安全访问」，数据转换管「值变成什么」，两者不能混用。"),
        code("""
            function describe(value: string | number): string {
              if (typeof value === 'number') {
                return 'number:' + value;
              }
              return 'string:' + value;
            }

            console.log(describe(42));
            console.log(describe('hi'));
        """),
        out("number:42\nstring:hi"),
        diagram("""
            value: string | number
                    │
                    ├─ typeof value === 'number'
                    │     └─ 这个分支里 value 是 number
                    │
                    └─ 否则
                          └─ 这个分支里 value 是 string

            收窄是运行时判断 + 编译期推断，两层同时生效。
        """),
        tip("写收窄判断时优先用具体条件，不要用 `if (value)`。空字符串、0、false 都会让 `if (value)` 为假，容易把合法值误判成缺失值。要判空就明确写 `value === undefined` 或 `value === null`。"),
        warn("收窄只在当前作用域和当前分支内有效。把变量传进回调函数后，TypeScript 无法保证回调执行时类型没变，所以回调内部往往需要重新判断。这不是编译器笨，而是 JavaScript 的变量确实可能被异步修改。"),
        quiz("`typeof null` 返回什么？", [
            "'null'",
            "'object'",
            "'undefined'",
            "'boolean'",
        ], 1, "这是 JavaScript 从第一版遗留的 bug，typeof null 返回 'object'。所以判 null 必须用 v === null，不能靠 typeof。"),
        practice("混合类型求和", """
            function toNumber(v: string | number): number {
              if (typeof v === 'number') {
                return v;
              }
              return Number(v);
            }

            console.log(toNumber(7), toNumber('8'));
        """, "7 8", "数字直接返回，字符串用 Number 转换。"),
    ], exercise(
        "混合输入格式化",
        "实现 formatValue(v)：数字返回 'num:值'，字符串返回 'str:长度'，布尔返回 'bool:值'。参数类型写成 string | number | boolean。",
        """
        function formatValue(v: string | number | boolean): string {
          // 用 typeof 分别判断三种类型
          return '';
        }
        """,
        "依次判断 typeof v === 'number'、'string'、'boolean'；字符串分支要输出 v.length。",
        [
            "assert(formatValue(42) === 'num:42', '数字分支错误')",
            "assert(formatValue('abc') === 'str:3', '字符串分支应输出长度')",
            "assert(formatValue(true) === 'bool:true', '布尔分支错误')",
            "assert(formatValue('') === 'str:0', '空字符串长度是 0')",
        ],
        """
        function formatValue(v: string | number | boolean): string {
          if (typeof v === 'number') {
            return 'num:' + v;
          }
          if (typeof v === 'string') {
            return 'str:' + v.length;
          }
          return 'bool:' + v;
        }
        """,
        90,
    )),

    lesson("ts10", 609, 61, C1, "any / unknown / never", "三种极端类型", 90, [
        h("类型系统的三个极端"),
        p("any 表示「放弃检查」：标注为 any 的值可以赋给任何类型、可以调用任何方法、可以访问任何属性，编译器全程不吭声。它适合与没有类型定义的老代码打交道，但滥用 any 等于把 TypeScript 退化成 JavaScript，而且错误会沿着赋值链一路传播——一个 any 赋给十个变量，这十个变量都失去了保护。所以工程上把 any 视为逃生舱，只在边界处短暂使用。"),
        p("unknown 是 any 的安全版本：它可以接收任何值，但使用前必须先收窄。`var v: unknown = getInput();` 之后不能直接 `v.length`，必须先 `if (typeof v === 'string')`。这正是处理外部输入的正确姿势——JSON.parse 的结果、用户输入、网络响应，在验证之前都应该当成 unknown。unknown 把「不确定」显式写在类型里，强迫你在使用前做检查。"),
        p("never 表示「不可能有值」。它最常见的用途是标注永远不会正常返回的函数，例如总是抛异常的函数：`function fail(msg: string): never { throw new Error(msg); }`。另一个用途是穷尽检查：当联合类型的所有分支都处理完，剩下的值在类型上就是 never。never 是 TypeScript 类型系统里最底层的类型，它可以赋给任何类型，但没有任何值能赋给它。"),
        p("三者的选择顺序可以记成一句话：能确定就用具体类型，不能确定但要用就先 unknown 再收窄，实在没办法才 any，永远不返回就 never。本应用的转译器会把这些标注全部擦除，所以运行时 any 和 unknown 完全没有区别，区别只存在于编写阶段。真正让程序安全的，是你写的那些 typeof 判断，而不是标注本身。"),
        p("最后强调一点：这三种类型不是语法糖，而是三种工程态度。any 是放弃，unknown 是谨慎，never 是不可能。初学者容易把 any 当默认类型，写着写着 TypeScript 就退化成了 JavaScript；有经验的开发者会把 any 压缩到最少的边界代码里，其余部分全部用具体类型或 unknown。你不需要一次做对，但每写一个 any，都应该能说出为什么这里无法确定类型。"),
        p("三种极端类型对应三种工程判断：any 表示「我不打算管」，unknown 表示「我还没确认」，never 表示「这里不可能继续」。实际项目里，any 应该只出现在与无类型代码交界的最外层，并且尽快转成 unknown 或具体类型；unknown 应该出现在所有外部输入的入口；never 应该出现在穷尽检查和异常函数的返回位置。把这三个位置记牢，你就不太会滥用它们。"),
        p("还有一条实践建议：把 any 的出现位置记下来，定期复查。可以用编辑器的搜索功能统计 any 的数量，也可以在每个 any 旁写一行注释说明原因。数量上升说明类型覆盖在退化，原因长期不变说明那个边界确实无法类型化，可以考虑封装成一个小模块，把 any 关在里面，对外只暴露具体类型。这样 any 的影响范围就被限制住了。"),
        p("还有一个和判题相关的提醒：测试里写 `assert(typeof value === 'string')` 时，断言的是运行时类型，不是静态标注。标注写得再准，运行时值也可能是别的类型；反过来，运行时检查通过，也不代表标注正确。两者要分别检查，不能互相替代。养成「标注管编译期、断言管运行期」的区分，调试时就不会混淆问题来源，能更快定位是类型设计错了还是数据真的错了。"),
        code("""
            function safeLength(value: unknown): number {
              if (typeof value === 'string') {
                return value.length;
              }
              if (Array.isArray(value)) {
                return value.length;
              }
              return -1;
            }

            console.log(safeLength('abc'));
            console.log(safeLength([1, 2, 3, 4]));
            console.log(safeLength(42));
        """),
        out("3\n4\n-1"),
        table(["类型", "能赋给它什么", "能直接用吗", "典型场景"], [
            ["any", "任何值", "能，完全不检查", "老代码兼容、临时逃生"],
            ["unknown", "任何值", "不能，必须先收窄", "外部输入、JSON 解析"],
            ["never", "没有任何值", "它是「不会返回」", "抛异常函数、穷尽检查"],
        ]),
        p("一个常见的误区是把 unknown 当成 any 的别名，然后在使用时直接 as 断言。`(v as string).length` 确实能通过编译，但运行时如果 v 是数字，照样得到 undefined 甚至崩溃。断言绕过了收窄，也就绕过了 unknown 的全部价值。正确的用法是老老实实写 typeof、Array.isArray、=== null 这些判断，让运行时和编译期同时获得保证。"),
        tip("函数返回值标注为 never 时，函数体必须有 throw 或死循环，否则 tsc 会报错。本应用不做类型检查，但保持这个习惯能让代码在真正的 TypeScript 项目里直接复用。"),
        warn("any 会传染：一个 any 参与运算，结果往往还是 any。团队规范里通常禁止显式 any，用 unknown 替代，只有在对接无类型第三方库时才短暂放开，并在边界处立刻收窄成具体类型。"),
        quiz("`var v: unknown = 'abc'; console.log(v.length)` 在 tsc 下会怎样？", [
            "正常编译，输出 3",
            "编译报错，unknown 不能直接访问属性",
            "运行时崩溃",
            "v 被推断为 any",
        ], 1, "unknown 必须先收窄才能使用，直接访问 length 会被 tsc 拒绝。运行时因为类型被擦除，实际上会输出 3，但这正是需要避免的写法。"),
        practice("unknown 守卫", """
            function firstChar(v: unknown): string {
              if (typeof v === 'string' && v.length > 0) {
                return v.charAt(0);
              }
              return '?';
            }

            console.log(firstChar('abc'), firstChar(5), firstChar(''));
        """, "a ? ?", "先确认是字符串，再确认非空，最后取首字符。"),
    ], exercise(
        "安全解析数字",
        "实现 toSafeNumber(v)：如果 v 是数字直接返回；如果是字符串且能转成有限数字，返回转换结果；其他情况返回 -1。用 unknown 作为参数类型。",
        """
        function toSafeNumber(v: unknown): number {
          // 数字直接返回；字符串先转换再判断 isNaN；其余返回 -1
          return -1;
        }
        """,
        "先用 typeof v === 'number'；再用 typeof v === 'string' 加 Number(v) 和 isNaN 判断；注意空字符串转数字是 0，要单独排除。",
        [
            "assert(toSafeNumber(42) === 42, '数字应原样返回')",
            "assert(toSafeNumber('3.5') === 3.5, '数字字符串应被转换')",
            "assert(toSafeNumber('abc') === -1, '非数字字符串应返回 -1')",
            "assert(toSafeNumber('') === -1, '空字符串应返回 -1')",
            "assert(toSafeNumber(true) === -1, '布尔值应返回 -1')",
        ],
        """
        function toSafeNumber(v: unknown): number {
          if (typeof v === 'number') {
            return v;
          }
          if (typeof v === 'string' && v !== '') {
            var n: number = Number(v);
            if (!isNaN(n)) {
              return n;
            }
          }
          return -1;
        }
        """,
        110,
    )),
]

TS_CORE = [
    lesson("ts11", 610, 62, C2, "泛型入门", "把类型也变成参数", 90, [
        h("一个函数，多种类型"),
        p("泛型是把类型当作参数：写函数时不锁定具体类型，调用时才确定。最直观的例子是「返回数组第一个元素」——数字数组返回数字，字符串数组返回字符串。如果没有泛型，要么写两个几乎一样的函数，要么退化成 any 并失去全部检查。`function first<T>(arr: T[]): T` 里的 T 就是类型参数，它在调用时被推断成 number 或 string，而函数体只有一份。"),
        p("调用时通常不需要手写类型参数，TypeScript 会从实参推断：传 `[1, 2, 3]`，T 就是 number；传 `['a']`，T 就是 string。这种推断让调用处保持干净。只有在推断不出来、或者你希望强制约束时，才需要显式写 `first<number>(...)`。本应用的转译器不支持这种「调用时带尖括号」的写法，所以课程里的泛型全靠推断，调用处一律不写类型参数。"),
        p("泛型的价值在于把「类型关系」写进签名。`function wrap<T>(v: T): T[]` 表达的不只是「参数是某个类型、返回值是数组」，而是「返回的数组元素类型和参数类型一致」。这个一致性是 any 给不了的：用 any 时，`wrap(5)` 返回 any[]，你把它当字符串数组用也不会报错；用 T，`var xs: string[] = wrap(5)` 会被 tsc 当场拦下。类型参数让输入和输出之间的关联变得可检查。"),
        p("泛型参数名有约定：T 表示 Type，K 表示 Key，V 表示 Value，U、R 用于第二、第三个参数。名字可以随便取，但遵循约定能让别人一眼看懂。泛型不是越多越好，一个函数有四个以上类型参数时，通常说明它承担了太多职责，应该拆分。先写好一个类型参数，再考虑增加，是更稳妥的顺序；能用一个就别用两个。"),
        p("最后要记住泛型的边界：它只在编写和编译阶段存在。转译器会把 `<T>` 和 `: T[]` 一起删掉，运行时看到的是普通函数，没有任何类型检查，也没有额外开销。这意味着泛型无法阻止运行时传错值，它的全部价值是让 tsc 和编辑器提前发现错误。理解这一点，你就不会期待泛型在运行时保护你。"),
        p("泛型还有一层容易被忽略的价值：它让重构变得安全。假设你后来决定把 first 的返回值从 T 改成 T | undefined（因为空数组没有首元素），只要改一处签名，所有调用点都会收到提示，编译器会告诉你哪些地方需要补判空。如果没有泛型、全用 any，这个改动只能靠人工搜索，遗漏在所难免。类型越精确，重构时的自动化程度就越高。"),
        p("泛型的常见误用是「为了显得高级而加」。如果一个函数只处理数字，就写 number，不要写 T；如果一个容器只装订单，就写 Order，不要写 T。泛型的正当理由只有一个：调用方需要保持类型之间的对应关系。函数内部并不关心具体类型，调用方却需要「传什么就得到什么」，这才是泛型的场景。判断时问自己一句：去掉 T 改成 any，调用方会损失什么？如果答不上来，就不需要泛型。"),
        p("还有一点值得注意：泛型函数的类型参数不会在运行时保留，所以无法在函数体里判断「T 是什么类型」。需要按类型分支时，要么传入类型判断函数，要么用运行时 typeof 判断具体值。这不是缺陷，而是类型擦除的必然结果。理解了这一点，你就不会写出「根据 T 做不同处理」这种在运行时无效的代码，也不会误以为泛型能替代运行时检查。"),
        code("""
            function first<T>(arr: T[]): T {
              return arr[0];
            }

            function wrap<T>(value: T): T[] {
              return [value];
            }

            console.log(first([10, 20, 30]));
            console.log(first(['V', 'Judy']));
            console.log(wrap('x').length);
        """),
        out("10\nV\n1"),
        diagram("""
            function first<T>(arr: T[]): T
                              │
                              ├─ 调用 first([10, 20, 30])
                              │     T 推断为 number，返回 number
                              │
                              └─ 调用 first(['V', 'Judy'])
                                    T 推断为 string，返回 string

            转译后：function first(arr) —— 泛型参数表整体擦除
        """),
        tip("泛型只在编写阶段存在。转译器会把 `<T>` 和 `: T[]` 一起删掉，运行时看到的是普通函数。所以泛型不会带来任何运行时代价，也不会做运行时类型检查。"),
        warn("不要给泛型加约束 `T extends X`，本应用的转译器不支持，会把 extends 原样留下导致语法错误。约束的概念在进阶篇讲解，运行代码一律用简单泛型。"),
        quiz("`function first<T>(arr: T[]): T` 被调用 `first(['a', 'b'])` 时，T 是什么？", [
            "string",
            "any",
            "T",
            "unknown",
        ], 0, "TypeScript 从实参 ['a','b'] 推断出元素类型是 string，因此 T 为 string，返回值也是 string。"),
        practice("泛型包装", """
            function wrap<T>(value: T): T[] {
              return [value];
            }

            var nums: number[] = wrap(7);
            console.log(nums[0], nums.length);
        """, "7 1", "wrap 返回只含一个元素的数组。"),
    ], exercise(
        "泛型首元素与末元素",
        "实现 firstOf(arr) 返回第一个元素，lastOf(arr) 返回最后一个元素，两者都用泛型标注；空数组时分别返回 null。",
        """
        function firstOf<T>(arr: T[]): T {
          // 空数组返回 null
          return null;
        }

        function lastOf<T>(arr: T[]): T {
          // 空数组返回 null
          return null;
        }
        """,
        "先判断 arr.length === 0 返回 null；firstOf 取 arr[0]，lastOf 取 arr[arr.length - 1]。",
        [
            "assert(firstOf([1, 2, 3]) === 1, 'firstOf 应返回首元素')",
            "assert(lastOf([1, 2, 3]) === 3, 'lastOf 应返回末元素')",
            "assert(firstOf(['a']) === 'a', '字符串数组也要支持')",
            "assert(firstOf([]) === null && lastOf([]) === null, '空数组应返回 null')",
        ],
        """
        function firstOf<T>(arr: T[]): T {
          if (arr.length === 0) {
            return null;
          }
          return arr[0];
        }

        function lastOf<T>(arr: T[]): T {
          if (arr.length === 0) {
            return null;
          }
          return arr[arr.length - 1];
        }
        """,
        100,
    )),

    lesson("ts12", 611, 62, C2, "泛型函数与泛型接口", "让容器也带上类型", 90, [
        h("把类型参数带进接口"),
        p("泛型不仅能用在函数上，也能用在 interface 和 type 上。`interface Box<T> { value: T; }` 描述一个「装着某种东西的盒子」，T 在使用时才确定：`Box<number>` 是装数字的盒子，`Box<string>` 是装字符串的盒子。这种带参数的接口叫泛型接口，它是集合类型、响应包装、缓存容器的基础，也是标准库中 Array<T>、Promise<T> 的写法来源。"),
        p("泛型接口和泛型函数搭配时，类型参数会在两者之间传递。`function unbox<T>(box: Box<T>): T` 表示「不管盒子里装什么，取出后还是那个类型」。调用时传入 boxOfNumber，编译器先由实参确定 Box<number>，再把 T 定为 number，返回类型自然也是 number。整条链路上没有 any，类型信息完整保留，这就是泛型最典型的用法：让容器和操作容器的函数共享同一个类型参数。"),
        p("类型别名也可以带参数：`type Pair<A, B> = { first: A; second: B }`。它适合表达「两个值组合」，比写两个独立接口更紧凑。泛型接口更适合会被扩展、需要被类实现的场景；泛型类型别名适合纯组合、联合、元组。两者都能被泛型函数引用，选择时看团队习惯和是否需要 extends。本应用只支持类型别名和接口的声明，运行时都不可见。"),
        p("使用泛型接口时要避免一个陷阱：不要把所有字段都写成 T。`interface ApiResponse<T> { ok: boolean; data: T; error: string | null }` 是合理的，因为只有 data 随场景变化；如果连 ok 都写成 T，调用方就无法知道它一定是布尔值了。泛型的粒度应该贴合「真正会变化的那个位置」，其余字段保持具体类型，接口才既灵活又明确。"),
        p("还有一个常见错误：在函数体里凭空使用 T 构造值。`function make<T>(): T { return {}; }` 在标准 TypeScript 里也不合法，因为编译器不知道 T 是否可能是 string。泛型函数只能操作「收到的 T」，不能凭空创造 T。需要构造时，把构造器或工厂函数作为参数传进来，让调用方提供创建逻辑，这样类型才对得上。"),
        p("把泛型接口当参数时，类型参数会沿着调用链自动传播，这个过程叫类型推断的「上下文」。`function mapBox<T>(box: Box<T>, f: Op<T>): Box<T>` 里，只要传入 Box<number>，T 立刻确定为 number，回调的参数也就确定为 number，不需要在调用处重复写。推断失败时（例如没有任何实参能提供线索），才会退化成 unknown 或报错，这时候显式标注就成了必要手段。"),
        p("泛型接口的命名通常带上容器语义：Box、Result、Page、Response、Cache。名字里带 T 的接口，读者预期它是「装着某种东西的容器」；如果接口只是普通业务对象，就不要加类型参数。另一个实践是让类型参数尽量少：一个容器一个参数最清晰，两个参数通常表示「键和值」或「成功值和错误值」，三个以上就需要解释。参数越多，调用处的心智负担越重。"),
        p("最后说一个命名细节：泛型接口的类型参数名尽量用单个大写字母，除非有明确语义。Box<T> 比 Box<Item> 更通用，因为 Item 暗示了具体业务；Result<T, E> 里的 E 表示 Error，是有语义的约定。混用单字母和单词会让读者猜测作者的意图：这个 T 是任意类型，还是特指某种类型？统一用单字母，语义靠文档和上下文补充，是最省心的做法。"),
        p("再补一个泛型接口的常见组合：包装「可能失败」的结果。`interface Result<T> { ok: boolean; value: T | null; error: string | null }`，成功时 value 有值、error 为空，失败时反过来。这种结构比抛异常更容易在类型层面表达，也比返回 any 更安全。调用方拿到 Result，先看 ok 再取 value，路径清晰。本课程在进阶篇可辨识联合那一讲会用更精确的方式表达同一种模式。"),
        code("""
            interface Box<T> {
              value: T;
            }

            function unbox<T>(box: Box<T>): T {
              return box.value;
            }

            type Pair<A, B> = { first: A; second: B };

            var numBox: Box<number> = { value: 42 };
            var strBox: Box<string> = { value: 'V' };
            var pair: Pair<string, number> = { first: 'hp', second: 100 };

            console.log(unbox(numBox));
            console.log(unbox(strBox));
            console.log(pair.first, pair.second);
        """),
        out("42\nV\nhp 100"),
        table(["写法", "含义", "典型用途"], [
            ["interface Box<T>", "带一个类型参数的接口", "容器、包装、缓存"],
            ["type Pair<A, B>", "带两个类型参数的别名", "键值对、坐标、二元组"],
            ["Box<number>", "把 T 替换为 number 后的类型", "具体使用处的标注"],
            ["function unbox<T>(b: Box<T>): T", "接收泛型接口并返回其内容", "保持类型在链路中传递"],
        ]),
        tip("泛型接口的字段不要全部写成 T。只把真正会变化的字段泛型化，其余字段用具体类型，接口的可读性和约束力都会更好。"),
        warn("本应用的转译器会删除 `interface Box<T>` 整段，也会把 `Box<number>` 这样的标注擦掉。运行时 Box 只是一个普通对象，泛型不产生任何检查，也不会限制 value 的类型。"),
        quiz("`interface Box<T> { value: T }` 中，`Box<string>` 的 value 字段是什么类型？", [
            "T",
            "string",
            "any",
            "unknown",
        ], 1, "Box<string> 把类型参数 T 替换成 string，因此 value 是 string。"),
        practice("泛型容器", """
            interface Box<T> {
              value: T;
            }

            var b: Box<number[]> = { value: [1, 2, 3] };
            console.log(b.value.length);
        """, "3", "把数组当作 T，容器里装的是数字数组。"),
    ], exercise(
        "泛型缓存与二元组",
        "实现 setItem/getItem 两个泛型函数：setItem 接收一个值并包装成 { value: T } 返回；getItem 接收包装对象并返回里面的值。再实现 makePair(a, b) 返回 { first, second }。",
        """
        interface Box<T> {
          value: T;
        }

        function setItem<T>(value: T): Box<T> {
          // 把 value 装进盒子
          return { value: null };
        }

        function getItem<T>(box: Box<T>): T {
          // 取出盒子里的值
          return null;
        }

        function makePair<A, B>(a: A, b: B): Pair<A, B> {
          // 返回包含 first 与 second 的对象
          return { first: null, second: null };
        }
        """,
        "makePair 的返回类型要用 type 别名声明，本应用不支持内联对象返回类型；返回值写成 { first: (a), second: (b) }。",
        [
            "assert(getItem(setItem(5)) === 5, '数字应能存取一致')",
            "assert(getItem(setItem('x')) === 'x', '字符串应能存取一致')",
            "assert(setItem([1,2]).value.length === 2, '数组也能装进盒子')",
            "assert(makePair('a', 1).first === 'a', '二元组第一项错误')",
            "assert(makePair('a', 1).second === 1, '二元组第二项错误')",
        ],
        """
        interface Box<T> {
          value: T;
        }

        type Pair<A, B> = { first: A; second: B };

        function setItem<T>(value: T): Box<T> {
          return { value: (value) };
        }

        function getItem<T>(box: Box<T>): T {
          return box.value;
        }

        function makePair<A, B>(a: A, b: B): Pair<A, B> {
          return { first: (a), second: (b) };
        }
        """,
        100,
    )),

    lesson("ts13", 612, 62, C2, "可选属性与 readonly", "允许缺失，也允许禁止修改", 80, [
        h("两种修饰，两种契约"),
        p("可选属性用问号标记：`interface User { name: string; age?: number }`。它表示 age 可以不存在，读取时类型是 number | undefined，使用前必须判断。可选属性和「值可以是 null」是两件事：可选表示字段本身可能没有，null 表示字段存在但值是空。设计接口时先想清楚你要表达哪一种，混用会让调用方无所适从，也会让判空逻辑越来越长。"),
        p("readonly 表示「初始化后不应再赋值」。`readonly id: number` 让 tsc 在你写 `user.id = 2` 时报错，但运行时对象并没有被冻结，仍然可以被改写。它是一份编译期约定，不是运行时保护。需要真正的运行时不可变时，要用 Object.freeze；本应用的 enum 就是这么做的。readonly 适合描述 ID、创建时间、外部系统分配的单号这类不该被本地修改的字段。"),
        p("可选属性和 readonly 可以组合：`readonly createdAt?: string` 表示字段可能不存在，存在时不应修改。组合的顺序是 readonly 在前、问号在后，写在字段名后面。数组也有只读形式 `readonly number[]`，但本应用的转译器对 readonly 前缀的处理是直接删除关键字，写在数组类型前面可能留下残渣，所以课程只在 interface 字段上用 readonly。"),
        p("判断可选属性是否存在，推荐写 `obj.age === undefined`，不要写 `if (obj.age)`——年龄为 0 时会被误判成不存在。如果接口里允许 null，还要同时判 `=== null`。这类判断在本应用里是运行时真实执行的，所以它同时保护了程序不崩溃；而 readonly 只是编写阶段的提醒，运行时完全不设防。两种修饰的强度不同，不要混为一谈。"),
        p("工程上还有一个建议：把可选字段集中在对象末尾，并且在函数入口统一归一化。例如先算出 `var age: number = u.age === undefined ? 0 : u.age;`，后面所有逻辑都用这个局部变量，不再反复判 undefined。这样既避免了遗漏，也让主逻辑保持扁平。归一化之后，可选属性只在边界出现一次，内部代码面对的都是确定值。"),
        p("对象展开是更新不可变对象的常用手法，但本应用不支持展开运算符 `...`，所以更新字段时要显式构造新对象：把旧字段逐个复制、再覆盖要改的那个。这种写法啰嗦，却完全兼容 ES5，而且读起来一目了然——哪些字段被保留、哪些被替换，全在代码里。等你在支持 ES6 的环境里工作时，可以换回展开写法，语义是一样的。"),
        p("可选属性在继承和组合时会累积。父接口有可选字段，子接口继承后仍然可选，不会因为子接口「更具体」就变成必填。如果子接口确实要求该字段必填，必须在子接口里重新声明一次：`interface Strict extends Base { age: number }`。tsc 允许子接口把可选收窄为必填，这表示子类型承诺了更强的约束，赋值方向仍然安全。"),
        p("可选属性是接口里最容易失控的部分。每增加一个可选字段，所有读取它的地方都要多一次判空；可选字段越多，函数体里的防御代码越多。控制方法是在边界处归一化：解析外部数据时把可选字段一次性补成必填，之后内部传递的对象不再有可选字段。这样「可选」只出现在最外层，核心逻辑保持干净。这也是为什么很多项目区分 Input 类型和 Model 类型。"),
        p("再补一个判断可选字段的实用方法：问自己「这个字段缺失时，业务上是否仍然成立」。用户没填年龄，用户档案仍然成立，所以 age 可选；订单没有金额，订单就不成立，所以 total 必填。用业务规则决定可选性，而不是用「暂时没有数据」决定，能避免把必填字段误标成可选，导致后续到处判空、到处兜底。"),
        code("""
            interface Profile {
              readonly id: number;
              name: string;
              age?: number;
            }

            function describe(p: Profile): string {
              var age: string = p.age === undefined ? '?' : String(p.age);
              return p.id + ':' + p.name + '(' + age + ')';
            }

            console.log(describe({ id: 1, name: 'V' }));
            console.log(describe({ id: 2, name: 'Judy', age: 30 }));
        """),
        out("1:V(?)\n2:Judy(30)"),
        diagram("""
            interface Profile {
              readonly id: number;   ← 不可改写（仅编译期）
              name: string;          ← 必填
              age?: number;          ← 可选，读取时是 number | undefined
            }

            运行时：三个修饰全部消失，只剩普通对象字段。
        """),
        tip("给可选属性写默认值时，用 `var age: number = p.age === undefined ? 0 : p.age;` 这种显式判断，比 `p.age || 0` 安全——后者会把 0 也当成缺失。"),
        warn("readonly 不阻止运行时修改。`p.id = 99` 在 tsc 下报错，在本应用里照常执行。要真正的不可变，请在构造函数或工厂函数里一次性建好对象，不对外暴露写入口。"),
        quiz("`interface U { age?: number }` 中，读取 `u.age` 的静态类型是什么？", [
            "number",
            "number | undefined",
            "any",
            "null",
        ], 1, "可选属性可能不存在，读取结果是 number | undefined，使用前必须判空。"),
        practice("可选字段默认值", """
            interface Cfg {
              retries?: number;
            }

            function retriesOf(c: Cfg): number {
              return c.retries === undefined ? 3 : c.retries;
            }

            console.log(retriesOf({}), retriesOf({ retries: 0 }));
        """, "3 0", "0 是合法值，不能用 || 兜底。"),
    ], exercise(
        "用户档案格式化",
        "实现 formatUser(u)：返回 'id:name:age'，age 缺失时输出 '?'。再实现 rename(u, name) 返回一个新对象，id 保持不变、name 用新值、age 原样保留。",
        """
        interface User {
          readonly id: number;
          name: string;
          age?: number;
        }

        function formatUser(u: User): string {
          // 缺失 age 时输出 ?
          return '';
        }

        function rename(u: User, name: string): User {
          // 返回新对象，id 与 age 保留
          return u;
        }
        """,
        "formatUser 先算 age 字符串；rename 构造新对象时把 id、age 都复制过去，age 可能是 undefined，直接赋给可选字段即可。",
        [
            "assert(formatUser({id:1, name:'V'}) === '1:V:?', '缺失 age 应输出问号')",
            "assert(formatUser({id:2, name:'J', age:30}) === '2:J:30', '有 age 时应输出数字')",
            "assert(formatUser({id:3, name:'K', age:0}) === '3:K:0', '0 岁不能被当成缺失')",
            "assert(rename({id:1, name:'V', age:9}, 'W').name === 'W', '改名应生效')",
            "assert(rename({id:1, name:'V', age:9}, 'W').id === 1, 'id 应保持原值')",
        ],
        """
        interface User {
          readonly id: number;
          name: string;
          age?: number;
        }

        function formatUser(u: User): string {
          var age: string = u.age === undefined ? '?' : String(u.age);
          return u.id + ':' + u.name + ':' + age;
        }

        function rename(u: User, name: string): User {
          return { id: (u.id), name: (name), age: (u.age) };
        }
        """,
        100,
    )),

    lesson("ts14", 613, 62, C2, "索引签名", "描述「键不固定」的对象", 90, [
        h("当对象是一张表"),
        p("有些对象的键在写代码时并不知道，比如统计字符频率的计数器、按 ID 索引的缓存、从配置里读出来的键值表。这类对象用 interface 逐个列字段不现实，要用索引签名：`interface Counter { [key: string]: number }` 表示「任意字符串键，对应的值都是数字」。它把对象描述成一张字典，键的类型和值的类型分别约束，既保留了结构，又不限定具体有哪些键。"),
        p("索引签名有两种键：string 和 number。`[key: string]: number` 覆盖所有字符串键；`[key: number]: string` 描述数字下标的数组式对象。JavaScript 里数字键最终也会被转成字符串，所以同时写两种签名时，number 键的值类型必须是 string 值类型的子类型，否则 tsc 会报错。课程里统一用 string 键，避免这层复杂度，也符合大多数字典场景。"),
        p("索引签名和具体字段可以共存：`interface Config { name: string; [key: string]: string }` 表示 name 必须存在，其余任意字符串键的值也必须是字符串。注意所有具名字段的类型都必须兼容索引签名的值类型，否则 tsc 会拒绝。这条规则保证了「用任意键访问」时返回的类型是可信的，不会出现某些键是数字、某些键是字符串的混乱局面。"),
        p("读取索引签名时有一个必须处理的细节：TypeScript 默认认为任意键都存在，但运行时不一定。`var c: Counter = {}; c['a']` 在类型上是 number，运行时是 undefined。开启 noUncheckedIndexedAccess 可以把这个差异暴露出来，但本应用不做类型检查，所以代码里要自己判断 `=== undefined`。统计频率、累加计数这类逻辑，第一步永远是判断键是否存在。"),
        p("索引签名也适合做简单的内存缓存：用 ID 当键、对象当值，读取前先判空，没有就计算并存进去。这种模式在数据量不大时非常有效，缺点是键会一直增长，需要定期清理。类型层面它能正常工作，但索引签名不限制键的数量，也不提供过期语义，真正的缓存还是要靠带有淘汰策略的库。类型系统负责结构正确，不负责运行时策略。"),
        p("索引签名还常与 Object.keys 配合做遍历。`Object.keys(dict)` 返回字符串数组，循环里用 `dict[keys[i]]` 取值，这是 ES5 里遍历字典的标准写法。注意 for...in 会遍历原型链上的可枚举属性，风险更大，课程统一用 Object.keys 加下标循环。遍历顺序在旧引擎里不保证，如果顺序重要，应该另外维护一个键数组，而不是依赖对象自身的顺序。"),
        p("索引签名描述的是「开放集合」，interface 描述的是「封闭结构」。判断用哪个：如果键的数量和名字在写代码时已知，用 interface；如果键由运行时数据决定，用索引签名。两者可以共存，但要注意具名字段的类型必须兼容索引签名的值类型。实践中，索引签名最常用于计数器、缓存、配置表和分组结果，这四类场景的共同点是「键是数据，不是设计」。"),
        p("最后提醒性能上的一个细节：频繁用字符串键读写对象时，V8 等引擎会把它当成字典模式，访问速度比固定形状的对象慢。数据量小的时候完全无感，数据量大时可以考虑用 Map，但 Map 不在本课程范围内。类型层面无法表达这种性能差异，只能靠经验判断。索引签名适合中小规模的数据，超大字典应该换数据结构。"),
        code("""
            interface Counter {
              [key: string]: number;
            }

            function countChars(text: string): Counter {
              var out: Counter = {};
              for (var i = 0; i < text.length; i++) {
                var ch: string = text[i];
                if (out[ch] === undefined) {
                  out[ch] = 1;
                } else {
                  out[ch] = out[ch] + 1;
                }
              }
              return out;
            }

            var c: Counter = countChars('aab');
            console.log(c['a'], c['b']);
            console.log(c['z'] === undefined);
        """),
        out("2 1\ntrue"),
        table(["写法", "含义", "读取未存在的键"], [
            ["[key: string]: number", "任意字符串键，值为数字", "类型上是 number，运行时是 undefined"],
            ["[key: number]: string", "数字下标，值为字符串", "同上，需自行判空"],
            ["name: string 与索引签名共存", "具名字段 + 任意键", "具名字段必须有值"],
        ]),
        tip("统计类逻辑用 `if (out[ch] === undefined) { out[ch] = 1; } else { out[ch] = out[ch] + 1; }`，不要写 `out[ch]++`——undefined 加一会得到 NaN，而且本应用的 Rhino 对自增的边界处理不如显式赋值直观。"),
        warn("索引签名不会在运行时创建任何限制。给 Counter 赋一个字符串值，tsc 会报错，本应用照常运行。所有运行时校验都要自己写，不能指望类型标注。"),
        quiz("`interface D { [key: string]: number }`，执行 `var d: D = {}; console.log(d['x'])` 输出什么？", [
            "0",
            "null",
            "undefined",
            "报错",
        ], 2, "索引签名只是类型层约定，空对象里没有这个键，运行时读到 undefined。类型标注不会凭空造出 0。"),
        practice("词频统计", """
            interface Counter {
              [key: string]: number;
            }

            function countWords(words: string[]): Counter {
              var out: Counter = {};
              for (var i = 0; i < words.length; i++) {
                var w: string = words[i];
                out[w] = out[w] === undefined ? 1 : out[w] + 1;
              }
              return out;
            }

            var c: Counter = countWords(['a', 'b', 'a']);
            console.log(c['a'], c['b']);
        """, "2 1", "用三元表达式处理首次出现。"),
    ], exercise(
        "字符频率与去重",
        "实现 freq(text) 返回字符频率对象，实现 unique(text) 返回按首次出现顺序排列的不重复字符数组。",
        """
        interface Counter {
          [key: string]: number;
        }

        function freq(text: string): Counter {
          // 统计每个字符出现次数
          return {};
        }

        function unique(text: string): string[] {
          // 按首次出现顺序返回不重复字符
          return [];
        }
        """,
        "freq 用 out[ch] === undefined 判断首次；unique 先查 out[ch] 是否存在，不存在就 push 并置 1。",
        [
            "assert(freq('aab')['a'] === 2, 'a 应出现 2 次')",
            "assert(freq('aab')['b'] === 1, 'b 应出现 1 次')",
            "assert(freq('')['a'] === undefined, '空串不应产生键')",
            "assert(unique('abac').join('') === 'abc', '去重应保留首次出现顺序')",
            "assert(unique('').length === 0, '空串去重结果为空数组')",
        ],
        """
        interface Counter {
          [key: string]: number;
        }

        function freq(text: string): Counter {
          var out: Counter = {};
          for (var i = 0; i < text.length; i++) {
            var ch: string = text[i];
            if (out[ch] === undefined) {
              out[ch] = 1;
            } else {
              out[ch] = out[ch] + 1;
            }
          }
          return out;
        }

        function unique(text: string): string[] {
          var out: Counter = {};
          var list: string[] = [];
          for (var i = 0; i < text.length; i++) {
            var ch: string = text[i];
            if (out[ch] === undefined) {
              out[ch] = 1;
              list.push(ch);
            }
          }
          return list;
        }
        """,
        110,
    )),

    lesson("ts15", 614, 62, C2, "函数类型与回调", "把行为也写进类型", 90, [
        h("函数也是一种类型"),
        p("在 TypeScript 里，函数是值，也有类型。函数类型写成 `(参数: 类型) => 返回类型`，例如 `(n: number) => number` 表示「接收一个数字、返回一个数字」。它可以直接标注变量，也可以作为参数类型或接口字段类型。把函数类型命名成别名 `type Op = (n: number) => number`，既方便复用，也能避开本应用对「内联函数类型标注」的处理缺陷。"),
        p("回调是函数类型最常见的用途。数组的 map、filter、forEach，事件的监听器，异步任务的完成通知，都是把函数当参数传。给回调标注类型后，实现回调的人立刻知道参数是什么、要返回什么；调用回调的人也能确认自己传的实参正确。回调的类型写错时，错误会在传入处就报出来，而不是等到回调被调用时才崩溃，这就是把行为写进类型的价值。"),
        p("写回调时要注意 this 和闭包。普通函数的 this 由调用方式决定，回调被单独拿出来执行时可能丢失上下文；箭头函数没有自己的 this，会沿用外层的 this。本应用的 Rhino 支持箭头函数，所以需要访问外层 this 时优先用箭头函数。另一个常见问题是回调里修改外部变量——语法上完全允许，但会让函数的副作用变得隐蔽，尽量让回调只负责计算并返回值。"),
        p("高阶函数是函数类型的自然延伸：接收函数、返回函数。`function makeAdder(base: number): Op` 返回一个把参数加上 base 的函数，这种写法把配置和执行分离，调用方可以先把 base 固定下来，反复使用。返回函数时，被返回的函数通过闭包记住 base，这个能力与类型无关，但类型签名要同时描述输入和输出，否则使用处会退回 any，前面做的类型工作就白费了。"),
        p("回调签名设计有三个实用原则：参数尽量少、顺序从「数据」到「配置」、返回值含义单一。一个回调如果既返回状态又返回错误又返回数据，调用方每次都要判断半天；拆成两个回调或者返回一个明确的结果对象，可读性会好很多。类型系统能保证形状正确，但无法保证语义清晰，后者要靠命名和拆分来达成。"),
        p("函数类型的参数名只是文档，不影响兼容性。`(n: number) => number` 和 `(value: number) => number` 是同一个类型；参数个数和类型才决定兼容。理解这一点，你在实现回调时就能自由命名，不必和类型声明保持一致。另一个实践是给回调类型起名时带上语义：Op、Predicate、Reducer、Comparator、Handler，这些词在函数式编程里有确定含义，读者一看就知道回调该做什么。"),
        p("最后是一个调试技巧：回调不执行时，先确认它真的被传进去了，再确认调用点确实调用了它。常见原因是条件分支提前返回、循环一次都没进、或者参数位置传错。类型系统能发现「传错形状」，但发现不了「传错位置」——两个都是函数类型时尤其危险。给回调参数起明确的名字，并在调用处用变量名而不是内联匿名函数，能显著降低这类错误。"),
        p("再补充一点：给回调传参时，参数的顺序应该固定为「数据在前、索引在后」，这与数组原生方法的约定一致。`function each(list: T[], fn: (item: T, index: number) => void)` 读起来自然，调用方也不会搞混。如果回调需要更多上下文，用对象包起来传，而不是继续往后加参数——参数超过三个，调用处就需要靠记忆而不是靠阅读来理解。"),
        code("""
            type Op = (n: number) => number;
            type Predicate = (n: number) => boolean;

            function applyAll(nums: number[], op: Op): number[] {
              var out: number[] = [];
              for (var i = 0; i < nums.length; i++) {
                out.push(op(nums[i]));
              }
              return out;
            }

            function countIf(nums: number[], test: Predicate): number {
              var c: number = 0;
              for (var i = 0; i < nums.length; i++) {
                if (test(nums[i])) {
                  c += 1;
                }
              }
              return c;
            }

            console.log(applyAll([1, 2, 3], function (n: number): number { return n * 2; }).join(','));
            console.log(countIf([1, 2, 3, 4], function (n: number): boolean { return n % 2 === 0; }));
        """),
        out("2,4,6\n2"),
        diagram("""
            type Op = (n: number) => number
                       │        │
                       │        └─ 返回类型
                       └─ 参数类型

            applyAll(nums: number[], op: Op): number[]
                                    │
                                    └─ 行为作为参数传入

            输出是数据，回调是行为，类型把两者都描述清楚。
        """),
        tip("回调类型优先抽成 type 别名。内联写 `op: (n: number) => number` 在本应用里会擦除失败，留下无法解析的碎片。别名写法既安全又易读。"),
        warn("本应用不支持默认参数和剩余参数，回调相关的高阶用法要避开 `...args`。需要传多个值时，用对象或数组包起来，再在回调里按字段访问。"),
        quiz("`type Op = (n: number) => number` 表示什么？", [
            "一个名为 Op 的变量，值是数字",
            "一个接收数字、返回数字的函数类型",
            "一个返回函数的数字",
            "一个数字数组",
        ], 1, "箭头左边是参数列表，右边是返回类型，整体描述函数形状。"),
        practice("回调计数器", """
            type Predicate = (n: number) => boolean;

            function countIf(nums: number[], test: Predicate): number {
              var c: number = 0;
              for (var i = 0; i < nums.length; i++) {
                if (test(nums[i])) { c += 1; }
              }
              return c;
            }

            console.log(countIf([1, 2, 3], function (n: number): boolean { return n > 1; }));
        """, "2", "大于 1 的有 2 和 3。"),
    ], exercise(
        "高阶函数三件套",
        "实现 mapNums(nums, op) 返回每个元素经过 op 处理后的新数组；实现 filterNums(nums, test) 返回满足条件的元素；实现 reduceNums(nums, init, step) 从 init 开始依次用 step 合并每个元素。",
        """
        type Op = (n: number) => number;
        type Predicate = (n: number) => boolean;
        type Reducer = (acc: number, n: number) => number;

        function mapNums(nums: number[], op: Op): number[] {
          return [];
        }

        function filterNums(nums: number[], test: Predicate): number[] {
          return [];
        }

        function reduceNums(nums: number[], init: number, step: Reducer): number {
          return init;
        }
        """,
        "三个函数都用 for 循环；map 把 op 的结果 push 进新数组，filter 只在 test 为真时 push，reduce 把 step(acc, n) 的结果赋回 acc。",
        [
            "assert(mapNums([1,2], function (n: number): number { return n + 1; }).join(',') === '2,3', 'map 结果错误')",
            "assert(filterNums([1,2,3], function (n: number): boolean { return n > 1; }).join(',') === '2,3', 'filter 结果错误')",
            "assert(reduceNums([1,2,3], 0, function (a: number, n: number): number { return a + n; }) === 6, 'reduce 求和错误')",
            "assert(reduceNums([], 10, function (a: number, n: number): number { return a + n; }) === 10, '空数组应返回初始值')",
        ],
        """
        type Op = (n: number) => number;
        type Predicate = (n: number) => boolean;
        type Reducer = (acc: number, n: number) => number;

        function mapNums(nums: number[], op: Op): number[] {
          var out: number[] = [];
          for (var i = 0; i < nums.length; i++) {
            out.push(op(nums[i]));
          }
          return out;
        }

        function filterNums(nums: number[], test: Predicate): number[] {
          var out: number[] = [];
          for (var i = 0; i < nums.length; i++) {
            if (test(nums[i])) {
              out.push(nums[i]);
            }
          }
          return out;
        }

        function reduceNums(nums: number[], init: number, step: Reducer): number {
          var acc: number = init;
          for (var i = 0; i < nums.length; i++) {
            acc = step(acc, nums[i]);
          }
          return acc;
        }
        """,
        110,
    )),
]


TS_CORE += [
    lesson("ts16", 615, 62, C2, "对象类型组合", "交叉与继承，把小块拼成大块", 90, [
        h("小形状拼成大形状"),
        p("真实项目里的对象往往由多个关注点组成：一个订单有标识信息、有时间戳、有金额、有状态。把所有字段塞进一个 interface 会越来越臃肿，也不利于复用。组合的思路是先定义小形状，再把它们拼起来。TypeScript 提供两种拼法：interface 的 extends 继承，以及 type 的交叉类型 `A & B`。两种写法结果相似，语义略有差别。"),
        p("interface 的 extends 可以一次继承多个父接口：`interface Order extends Base, Timestamped { total: number }`。子接口拥有父接口的全部字段，还可以覆盖同名但兼容的类型。继承关系是「是一个」的语义：Order 是一个 Base，也是一个 Timestamped。这种语义在阅读时很自然，也让类型错误信息更友好，所以描述领域对象时优先用 extends。"),
        p("交叉类型用 & 把多个类型合并成一个，`type Order = Base & Timestamped & { total: number }`。它适合组合类型别名、联合类型、函数类型这些 extends 无法处理的场景。交叉的语义是「同时满足」，合并后的对象必须拥有所有成员。两个类型有同名但类型不同的字段时，交叉会得到 never，这是使用时要留意的陷阱。"),
        p("本应用的转译器不支持交叉类型的真实运行语义，`A & B` 只应出现在类型标注或 type 别名里，运行时对象的字段仍要手工构造。写组合逻辑时，最稳妥的方式是让函数显式接收多个小对象，返回拼好的大对象：`function merge(a: A, b: B): AB { return { x: (a.x), y: (b.y) }; }`。这样运行时行为完全可控，类型标注则负责表达组合关系。"),
        p("组合的另一个好处是测试。小形状可以单独构造、单独断言，大对象只是把小形状拼起来，测试时只需要验证拼接逻辑，不必为每个字段准备数据。当一个 interface 超过十几个字段时，先停下来看看能不能拆成三四个小接口，再组合起来。拆分的标准不是字段数量，而是「这些字段是否总是一起变化」——一起变化的放一起，独立变化的拆开。"),
        p("组合类型时还要注意「多余属性检查」。直接传对象字面量给函数时，tsc 会检查有没有接口里未声明的字段；把对象先赋给变量再传，检查就宽松一些。这个差异经常让人困惑：同样一个多出字段的对象，直接传参报错、经变量中转却不报。理解它的方式是记住「字面量会触发更严格的检查」，需要绕过时用变量中转或调整接口定义。"),
        p("组合类型时要抵抗「大接口」的诱惑。一个接口超过十几个字段，通常意味着它承担了多个职责：展示、存储、传输混在一起。拆分的信号是「这些字段是否总是一起出现」——总是一起出现的放一个接口，偶尔才出现的拆出去。拆分之后，函数可以只声明自己真正需要的那部分，依赖面变小，测试也更容易构造数据。接口越小，复用越容易。"),
        p("组合类型还要注意循环引用。A 包含 B、B 又包含 A，TypeScript 允许接口循环引用，但构造对象时会变成无限嵌套，运行时很快就会栈溢出。真实业务里，循环结构应该用「引用 ID」而不是「嵌套对象」表达：订单里存 userId，需要用户信息时再查。类型层面能表达循环，不代表数据结构应该循环，这个判断需要工程经验。"),
        code("""
            interface Base {
              id: string;
            }

            interface Timestamped {
              createdAt: string;
            }

            interface Order extends Base, Timestamped {
              total: number;
            }

            type Audited = Base & Timestamped;

            function stamp(id: string, createdAt: string): Audited {
              return { id: (id), createdAt: (createdAt) };
            }

            var o: Order = { id: 'A1', createdAt: '2026-01-01', total: 30 };
            var a: Audited = stamp('B2', '2026-02-02');

            console.log(o.id, o.createdAt, o.total);
            console.log(a.id, a.createdAt);
        """),
        out("A1 2026-01-01 30\nB2 2026-02-02"),
        table(["组合方式", "写法", "适用场景"], [
            ["接口继承", "interface C extends A, B", "领域对象，语义是「是一个」"],
            ["交叉类型", "type C = A & B", "类型别名、联合、函数类型的组合"],
            ["手工合并", "function merge(a, b): C", "需要运行时构造完整对象"],
        ]),
        tip("继承层级不要超过三层。三层以上时，父接口往往承担了过多职责，改一处会牵连很多子类型。宁可多写几个平级的接口，用组合而不是深层继承。"),
        warn("同名但类型不同的字段交叉后会变成 never，赋值时任何值都不满足。遇到这种情况说明两个父类型的语义冲突，应该改名或重新设计，而不是硬拼。"),
        quiz("`type C = A & B` 表示什么？", [
            "C 只能是 A 或 B 之一",
            "C 同时拥有 A 和 B 的全部成员",
            "C 是 A 和 B 的数组",
            "C 继承 A 并覆盖 B",
        ], 1, "交叉类型要求同时满足所有成员，合并后的对象必须拥有 A 与 B 的全部字段。"),
        practice("组合基础字段", """
            interface Base {
              id: string;
            }

            interface Named {
              name: string;
            }

            interface Entity extends Base, Named {
              level: number;
            }

            var e: Entity = { id: 'a', name: 'V', level: 3 };
            console.log(e.id + '/' + e.name + '/' + e.level);
        """, "a/V/3", "Entity 同时拥有三个字段。"),
    ], exercise(
        "订单字段组合",
        "定义 Base（id）、Timestamped（createdAt）、Amount（total）三个接口，用 extends 组合出 Order，实现 makeOrder(id, createdAt, total) 返回 Order，实现 describe(o) 返回 'id@createdAt=total'。",
        """
        interface Base {
          id: string;
        }

        interface Timestamped {
          createdAt: string;
        }

        interface Amount {
          total: number;
        }

        interface Order extends Base, Timestamped, Amount {
        }

        function makeOrder(id: string, createdAt: string, total: number): Order {
          return { id: (id), createdAt: (createdAt), total: (total) };
        }

        function describe(o: Order): string {
          // 返回 id + '@' + createdAt + '=' + total
          return '';
        }
        """,
        "describe 直接按格式拼接三个字段；makeOrder 已经给出，不需要改。",
        [
            "assert(makeOrder('A1','2026',30).id === 'A1', 'makeOrder 的 id 错误')",
            "assert(makeOrder('A1','2026',30).total === 30, 'makeOrder 的 total 错误')",
            "assert(describe({id:'A1', createdAt:'2026', total:30}) === 'A1@2026=30', 'describe 格式错误')",
            "assert(describe({id:'B2', createdAt:'x', total:0}) === 'B2@x=0', '0 金额也要输出')",
        ],
        """
        interface Base {
          id: string;
        }

        interface Timestamped {
          createdAt: string;
        }

        interface Amount {
          total: number;
        }

        interface Order extends Base, Timestamped, Amount {
        }

        function makeOrder(id: string, createdAt: string, total: number): Order {
          return { id: (id), createdAt: (createdAt), total: (total) };
        }

        function describe(o: Order): string {
          return o.id + '@' + o.createdAt + '=' + o.total;
        }
        """,
        100,
    )),

    lesson("ts17", 616, 62, C2, "类型断言与 as", "告诉编译器你比它更了解", 80, [
        h("断言不是转换"),
        p("类型断言用 as 写：`var s = value as string`。它的含义是「我确定这个值在这里是 string，请按 string 处理」，编译器不再检查。注意用词：断言不是转换，运行时一个字节都不会变，数字还是数字，对象还是对象。写 `var n = '5' as number`，运行时 n 是字符串 '5'，对它做加法会得到 '51' 而不是 6。"),
        p("断言最常见的合法场景是收窄外部数据。`JSON.parse` 返回 any，但你知道响应结构符合某个 interface，于是写 `var order: Order = JSON.parse(raw) as Order;`。这一步把无类型的值接进了类型系统，后续代码就能享受补全和检查。代价是责任转移：如果实际数据不符合 Order，编译器不会发现，运行时会以 undefined 的形式在很远的地方爆炸。"),
        p("另一种场景是处理联合类型中编译器无法推断的分支。例如你刚刚用自定义函数判断了类型，但那个函数返回的是普通 boolean，编译器不知道它意味着什么，此时用 as 强制收窄。更好的做法是把判断函数写成类型守卫 `v is string`，让编译器自动收窄，第二十六讲会详细讲。断言应该作为最后手段，而不是遇到类型错误就加 as。"),
        p("断言的语法在本应用里是 `expr as Type`，`as` 前面必须有空格，Type 只能是标识符或带泛型参数的标识符。尖括号写法 `<Type>expr` 在 TypeScript 里也合法，但会被误认为比较运算符，本应用的转译器故意不支持。断言可以链式写 `a as any as string`，但不建议——连续两次断言通常说明类型设计有问题，应该回头改结构而不是强行绕过。"),
        p("滥用断言会让类型系统失效。一个实用判断标准是：如果 as 的目标类型和源类型毫无关系，那多半是错的；如果目标类型是源类型的子集（例如从 any、unknown 或联合类型收窄到具体成员），那可能合理。团队代码评审时可以把所有 as 列出来逐条看，数量突然增多往往意味着某处的类型建模出了问题。"),
        p("断言还有一种合法用途是处理库的类型缺口。某些老库的声明文件把参数写成 any 或过于宽泛的联合类型，你明知运行时是具体类型，却无法让编译器相信，这时用一个局部断言比全局改声明更省事。处理完立刻在注释里记下原因，将来库更新了就可以删掉。断言本身不可怕，可怕的是没有记录的断言，后人不知道它为什么存在、能不能删。"),
        p("把断言当成「需要写理由的代码」。每次写 as，都在心里补一句「因为……所以这里一定是这个类型」。如果理由说不出来，就应该改成运行时校验或调整类型设计。评审时看到 as，第一反应应该是问理由，而不是问语法。团队里可以约定：断言必须紧邻一行注释说明依据，或者封装进有名字的函数里。让断言可见、可审查，是控制它滥用的有效办法。"),
        p("断言的另一个替代方案是「解析函数」：接收 unknown，返回具体类型或 null。例如 parseOrder(raw) 返回 Order | null，调用方必须判空才能使用。这样错误被显式建模，而不是被断言掩盖。解析函数的成本是要写校验逻辑，但它把「可能失败」这件事写进了类型签名，调用方无法忽略。对外部数据，这几乎总是比 as 更好的选择。"),
        code("""
            interface Order {
              id: string;
              total: number;
            }

            function parseOrder(raw: string): Order {
              var data: Order = JSON.parse(raw) as Order;
              return data;
            }

            var o: Order = parseOrder('{"id":"A1","total":30}');
            console.log(o.id, o.total);

            var n: number = 5;
            var m = n as number;
            console.log(typeof m);
        """),
        out("A1 30\nnumber"),
        diagram("""
            value as Type
                 │
                 ├─ 编写阶段：告诉 tsc「按 Type 处理」，不再检查
                 ├─ 运行阶段：什么都没发生，值原样保留
                 └─ 责任：由写代码的人承担

            断言 ≠ 转换。转换要用 Number()、String()、JSON.parse()。
        """),
        tip("从 any 或 unknown 断言成具体类型时，最好紧接着做一次运行时校验：检查关键字段是否存在、类型是否对。断言只解决编译期，运行时的正确性仍要自己保证。"),
        warn("本应用不做类型检查，as 的唯一作用是被擦除。也就是说 `var s = 5 as string` 在本应用里完全可行，运行时 s 就是数字。不要用它来「假装」类型正确。"),
        quiz("`var s = ('5' as number) + 1` 的运行时结果是什么？", [
            "6",
            "'51'",
            "NaN",
            "报错",
        ], 1, "as 只影响编写阶段，运行时 '5' 仍是字符串，加 1 触发字符串拼接得到 '51'。"),
        practice("断言后验证", """
            interface Point {
              x: number;
              y: number;
            }

            var data: any = { x: 1, y: 2 };
            var p: Point = data as Point;
            console.log(p.x + p.y);
        """, "3", "断言只是让编译器接受，字段本身是真实存在的。"),
    ], exercise(
        "解析并格式化订单",
        "实现 parseOrder(raw)：把 JSON 字符串断言成 Order 后返回。实现 safeTotal(raw)：解析后如果 total 不是数字，返回 0。",
        """
        interface Order {
          id: string;
          total: number;
        }

        function parseOrder(raw: string): Order {
          // JSON.parse 后 as Order
          return { id: '', total: 0 };
        }

        function safeTotal(raw: string): number {
          // 解析后检查 typeof total === 'number'
          return 0;
        }
        """,
        "parseOrder 直接 `return JSON.parse(raw) as Order;`；safeTotal 先取 order，再用 `typeof order.total === 'number'` 判断，不是数字就返回 0。",
        [
            "assert(parseOrder('{\"id\":\"A1\",\"total\":30}').id === 'A1', 'parseOrder 的 id 错误')",
            "assert(parseOrder('{\"id\":\"A1\",\"total\":30}').total === 30, 'parseOrder 的 total 错误')",
            "assert(safeTotal('{\"id\":\"A1\",\"total\":30}') === 30, '正常订单应返回 total')",
            "assert(safeTotal('{\"id\":\"A1\"}') === 0, '缺少 total 应返回 0')",
            "assert(safeTotal('{\"id\":\"A1\",\"total\":\"x\"}') === 0, 'total 非数字应返回 0')",
        ],
        """
        interface Order {
          id: string;
          total: number;
        }

        function parseOrder(raw: string): Order {
          return JSON.parse(raw) as Order;
        }

        function safeTotal(raw: string): number {
          var order: Order = parseOrder(raw);
          if (typeof order.total === 'number') {
            return order.total;
          }
          return 0;
        }
        """,
        100,
    )),

    lesson("ts18", 617, 62, C2, "非空断言", "用一个感叹号去掉 null", 80, [
        h("我确定它不是空"),
        p("非空断言写在表达式后面：`value!`。它的含义是「我确定这个值不是 null 也不是 undefined，请按去掉空值的类型处理」。`var name: string | null = ...; name!.length` 在 tsc 下能通过，因为感叹号把 string | null 收窄成了 string。和 as 一样，它只影响编写阶段，运行时什么都不做，如果真的为 null，照样抛出 TypeError。"),
        p("非空断言最适合用在「刚刚检查过但编译器不知道」的场景。典型例子是查表函数的返回值：`findById(users, id)` 返回 User | null，你在上一行已经判断过它不为空，但编译器在跨函数调用后不一定能保持收窄。这时用 ! 是合理的，前提是你的判断真的成立。更稳妥的做法是保留判断结果到局部变量，让编译器自己收窄。"),
        p("非空断言也常用于数组查找后立即访问：`items[i]!.name`，前提是你已经确认 i 在范围内。它不适合用来掩盖「可能真的没有」的情况，例如用户输入的查询结果、网络请求的响应、可选配置项。这些场景应该老实判空并给出默认值或错误提示，而不是用一个感叹号把风险推给运行时。"),
        p("本应用的转译器会删除非空断言：`value!` 变成 `value`，`obj!.prop` 变成 `obj.prop`。这个擦除是安全的，因为运行时本来就没有空值检查。但要注意不要把它和逻辑非混淆：`!value` 是取反，`value!` 是断言，位置不同、含义完全不同。写成 `if (!value!)` 这种组合既难读又容易出错，课程里一律避免。"),
        p("一个团队级的建议：把非空断言控制在很少的数量，并在代码评审时特别关注。每出现一个 !，都应该能说出「为什么这里一定不为空」——是因为刚刚判过、是因为数据结构保证、还是因为构造函数一定会赋值。说不出来就说明应该改成显式判空。类型断言的强度越大，越需要纪律来约束。"),
        p("非空断言在数组下标场景要格外小心。`arr[i]!` 只在你确认 i 合法时成立，而循环边界写错恰恰是最常见的 bug 来源。更稳的写法是先取出来放到局部变量，判断不为 null 再使用：`var item = arr[i]; if (item !== undefined) { ... }`。多写一行判断，换来的是运行时不会崩，这笔账任何时候都划算。"),
        p("把非空断言和本书的判题结合起来看会更清楚：判题里经常写 `getAt(rows, 0)!.name`，前提是那一行确实知道下标合法。如果测试传入越界下标，感叹号救不了你，运行时直接抛错，判题失败。所以在写练习时，先想清楚每个断言的成立条件，再决定用 ! 还是用显式判空，这比记住语法更重要。"),
        p("非空断言最危险的地方是它会「传染」：一个地方用了 !，后续代码就默认这个值永远不为空，一旦前提被破坏，错误会在很远的地方爆发。防止传染的办法是把断言限制在最小范围：取到值后立刻放进局部变量，断言只作用于这一个变量，不作用于链式调用。更稳的做法是把「查不到」变成显式的返回值，让调用方必须处理，而不是靠断言跳过。"),
        p("如果发现自己频繁使用非空断言，通常说明数据结构设计有问题：要么该字段其实总是存在，应该改成必填；要么它确实可能缺失，应该老实判空。两种修正都比断言更彻底。断言只是让编译器闭嘴，不解决「为什么这里可能是空」这个根本问题。把每次使用 ! 当成一次设计复盘的机会，类型建模能力会提升得很快。"),
        code("""
            interface User {
              id: number;
              name: string;
            }

            function findById(users: User[], id: number): User | null {
              for (var i = 0; i < users.length; i++) {
                if (users[i].id === id) {
                  return users[i];
                }
              }
              return null;
            }

            var users: User[] = [{ id: 1, name: 'V' }, { id: 2, name: 'Judy' }];
            var hit: User | null = findById(users, 2);

            console.log(hit!.name);
            console.log(findById(users, 9) === null);
        """),
        out("Judy\ntrue"),
        table(["写法", "含义", "运行时行为"], [
            ["value!", "断言 value 不为空", "原样保留 value"],
            ["value as T", "断言 value 是类型 T", "原样保留 value"],
            ["value === null", "真实的判空", "按判断结果分支"],
            ["value || fallback", "假值兜底", "0 与空串也会被替换"],
        ]),
        tip("能用 `if (hit !== null)` 收窄时就不要用 `hit!`。显式判断既让编译器满意，也让运行时安全，还让读代码的人知道这里确实可能为空。"),
        warn("非空断言和可选链不是一回事。本应用不支持可选链 `obj?.prop`，也不支持空值合并 `a ?? b`。判空请写 `obj === null || obj === undefined`，兜底请写三元表达式。"),
        quiz("`var s: string | null = null; console.log(s!.length)` 在 tsc 下会怎样？", [
            "编译报错",
            "编译通过，运行时抛 TypeError",
            "编译通过，输出 0",
            "输出 null",
        ], 1, "非空断言让编译器闭嘴，但运行时 s 确实是 null，访问 length 会抛 TypeError。"),
        practice("查找并读取", """
            interface Row {
              name: string;
            }

            function pick(rows: Row[], i: number): Row {
              return rows[i]!;
            }

            console.log(pick([{ name: 'a' }], 0).name);
        """, "a", "下标在范围内，断言成立。"),
    ], exercise(
        "列表查找与安全读取",
        "实现 getAt(rows, i) 返回第 i 个元素，越界时返回 null；实现 nameAt(rows, i) 用非空断言取 name，调用前已保证 i 合法。",
        """
        interface Row {
          name: string;
        }

        function getAt(rows: Row[], i: number): Row | null {
          // 越界返回 null
          return null;
        }

        function nameAt(rows: Row[], i: number): string {
          // 用 getAt 取到后加 ! 再访问 name
          return '';
        }
        """,
        "getAt 判断 i < 0 或 i >= rows.length 时返回 null；nameAt 写 `return getAt(rows, i)!.name;`。",
        [
            "assert(getAt([{name:'a'}], 0)!.name === 'a', 'getAt 应返回元素')",
            "assert(getAt([{name:'a'}], 5) === null, '越界应返回 null')",
            "assert(nameAt([{name:'a'},{name:'b'}], 1) === 'b', 'nameAt 应返回对应名字')",
            "assert(getAt([], 0) === null, '空数组应返回 null')",
        ],
        """
        interface Row {
          name: string;
        }

        function getAt(rows: Row[], i: number): Row | null {
          if (i < 0 || i >= rows.length) {
            return null;
          }
          return rows[i];
        }

        function nameAt(rows: Row[], i: number): string {
          return getAt(rows, i)!.name;
        }
        """,
        100,
    )),

    lesson("ts19", 618, 62, C2, "类型别名建模", "先给业务概念起名字", 90, [
        h("类型是业务的语言"),
        p("类型别名最被低估的用途是建模：把业务概念翻译成代码里的名字。`type UserId = string`、`type Cents = number`、`type OrderStatus = 'pending' | 'paid' | 'shipped'`，这些名字让函数签名直接表达业务含义。`function refund(orderId: OrderId, amount: Cents): RefundResult` 比 `function refund(a: string, b: number): any` 清楚一百倍，而且编译器和编辑器都能沿着名字找到定义。"),
        p("建模的第一步是区分「同一种底层类型、不同业务含义」的值。用户 ID 和订单 ID 都是字符串，但混用会导致严重 bug：把订单 ID 传给按用户 ID 查询的函数，类型系统如果能区分就会立刻报错。TypeScript 的结构化类型系统默认不区分，但可以通过交叉一个标记字段模拟标称类型，本课程不展开，只要求养成「给每个业务 ID 起独立别名」的习惯。"),
        p("第二步是给状态和结果建模。业务状态往往是封闭集合，用字面量联合描述最合适；操作结果往往分为成功和失败，用可辨识联合描述最清晰，第二十五讲会展开。把这些类型集中放在一个文件里，作为模块的类型词汇表，所有函数都从这里引用，能避免同一个概念在不同文件里被写成不同形状——这是大型项目里最常见、也最难查的一类 bug。"),
        p("第三步是让函数签名使用这些名字，而不是重复底层类型。`function pay(order: Order, amount: Cents): PaymentResult` 这样的签名，读起来像业务文档，改起来也方便：将来金额从分改成元，只需要改 Cents 的定义和转换函数，所有签名自动跟着变。类型别名不产生运行时开销，却能显著降低沟通成本，是投入产出比最高的工程实践之一。"),
        p("建模时要避免过度抽象。给每个字段都起一个别名，会让代码充满跳转，反而难读。判断标准是：这个概念是否在多个函数、多个文件里出现？是否有独立的业务含义？是否可能单独变化？三个都满足才值得起名。只在一个函数里用一次的临时结构，交给类型推断或者直接写内联类型即可，不必兴师动众。"),
        p("建模还有一个细节：把「输入类型」和「输出类型」分开。同一个业务概念，创建时需要的字段和查询后返回的字段往往不同：新建订单只需要商品和数量，查询订单会返回 ID、创建时间、状态。用两个 interface 描述（例如 OrderInput 和 Order），比用一个带大量可选字段的接口更清晰，也能避免「创建时忘了传 ID」这类低级错误。"),
        p("类型词汇表应该像业务词典一样维护：每个概念一条，说明含义、取值范围、由谁产生。代码里的别名只是这份词典的实现形式。当团队对某个概念有分歧时，先改词典再改代码，比直接在代码里各写各的要高效。一个健康的项目，新人读完类型文件就能理解八成业务；一个不健康的项目，类型文件里全是 any 和重复定义。类型文件的整洁程度，往往反映了团队对业务的理解决程度。"),
        p("类型词汇表还要防止「同义词泛滥」。用户编号叫 userId、uid、user_id、UserID，四个名字可能同时出现在一个项目里，类型系统无法判断它们是不是一回事。解决办法是集中定义、禁止就地新建，并在评审时统一叫法。命名一致性带来的收益很难量化，但它直接决定了新人上手的速度和跨模块协作的顺畅程度。"),
        code("""
            type UserId = string;
            type Cents = number;
            type OrderStatus = 'pending' | 'paid' | 'shipped';

            interface Order {
              id: UserId;
              status: OrderStatus;
              total: Cents;
            }

            function formatCents(v: Cents): string {
              return (v / 100).toFixed(2);
            }

            function summarize(o: Order): string {
              return o.id + '/' + o.status + '/' + formatCents(o.total);
            }

            console.log(summarize({ id: 'U1', status: 'paid', total: 1999 }));
        """),
        out("U1/paid/19.99"),
        diagram("""
            业务概念                类型别名                使用处
            ─────────              ─────────              ─────────
            用户编号        →       type UserId = string   →   id: UserId
            金额（分）      →       type Cents = number    →   total: Cents
            订单状态        →       type OrderStatus = ... →   status: OrderStatus

            名字固定概念，概念固定行为。
        """),
        tip("类型词汇表建议单独放一个文件，按「标识 → 枚举 → 实体 → 结果」的顺序排列。新同事读一遍就能理解业务的主要概念，比读十个函数实现更快。"),
        warn("别名不会做运行时校验。`var id: UserId = ''` 在运行时就是一个空字符串，类型系统不会阻止。业务规则（例如 ID 不能为空）必须写在函数里，类型只能表达「这是一个用户编号」。"),
        quiz("给金额定义 `type Cents = number` 的主要收益是什么？", [
            "运行时会自动把元转成分",
            "签名可读性提高，且概念只需在一个地方修改",
            "能防止金额被篡改",
            "可以减少内存占用",
        ], 1, "类型别名只影响编写阶段，收益是可读性和单点修改；它不做转换，也不提供运行时保护。"),
        practice("用别名表达金额", """
            type Cents = number;

            function yuan(c: Cents): string {
              return (c / 100).toFixed(2);
            }

            console.log(yuan(250));
        """, "2.50", "分转元，保留两位小数。"),
    ], exercise(
        "订单类型词汇表",
        "定义 UserId、Cents、OrderStatus 三个别名和 Order 接口，实现 formatCents(c) 返回两位小数的元字符串，实现 describe(o) 返回 'id:status:元金额'。",
        """
        type UserId = string;
        type Cents = number;
        type OrderStatus = 'pending' | 'paid' | 'shipped';

        interface Order {
          id: UserId;
          status: OrderStatus;
          total: Cents;
        }

        function formatCents(c: Cents): string {
          return '';
        }

        function describe(o: Order): string {
          return '';
        }
        """,
        "formatCents 用 (c / 100).toFixed(2)；describe 用 o.id + ':' + o.status + ':' + formatCents(o.total)。",
        [
            "assert(formatCents(1999) === '19.99', '1999 分应为 19.99')",
            "assert(formatCents(0) === '0.00', '0 分应为 0.00')",
            "assert(describe({id:'U1', status:'paid', total:1999}) === 'U1:paid:19.99', 'describe 格式错误')",
            "assert(describe({id:'U2', status:'shipped', total:5}) === 'U2:shipped:0.05', '5 分应为 0.05')",
        ],
        """
        type UserId = string;
        type Cents = number;
        type OrderStatus = 'pending' | 'paid' | 'shipped';

        interface Order {
          id: UserId;
          status: OrderStatus;
          total: Cents;
        }

        function formatCents(c: Cents): string {
          return (c / 100).toFixed(2);
        }

        function describe(o: Order): string {
          return o.id + ':' + o.status + ':' + formatCents(o.total);
        }
        """,
        100,
    )),

    lesson("ts20", 619, 62, C2, "从 JS 迁移到 TS", "渐进式加类型，而不是重写", 90, [
        h("迁移是一步步来的"),
        p("把老 JavaScript 项目迁到 TypeScript，最忌讳的是推倒重写。正确做法是渐进式：先把文件后缀改成 .ts，让编译器以宽松模式跑通，再逐个函数补类型。TypeScript 的设计初衷就是「JavaScript 的超集」，任何合法的 JS 都是合法的 TS，所以第一步几乎不需要改代码，只需要配置一个允许隐式 any 的 tsconfig。"),
        p("第二步是给边界补类型。所谓边界，是模块的导出函数、外部输入、公共数据结构。内部的临时变量可以先留给推断，边界的参数和返回值必须标注，因为它们是别人依赖的契约。本应用虽然不跑 tsc，但同样的原则适用于阅读和改写：先写 interface 描述数据结构，再给处理这些结构的函数加签名，最后处理内部逻辑。"),
        p("第三步是消除隐式 any。每加一个类型标注，就把对应的 any 缩小一圈。开启 strict 和 noImplicitAny 后，编译器会列出所有没标注的地方，逐个处理即可。遇到确实无法确定类型的第三方库，先写一个最小的 .d.ts 声明文件，把用到的函数和类型补上，不必追求完整。声明文件是桥梁，不是负担。"),
        p("第四步是把运行时校验补上。类型在运行时不存在，从网络、存储、用户输入来的数据都必须验证。常见做法是写一个解析函数：接收 unknown，用 typeof、Array.isArray、字段存在性检查逐层验证，通过后返回具体类型，失败则抛错或返回默认值。这个函数是类型系统与真实世界之间的唯一接口，写好了，后面所有代码都可以信任类型标注。"),
        p("迁移过程中还有两个实践建议。第一，保持一次改动可回滚：一个 PR 只迁一个模块，不要把所有文件塞进同一次提交。第二，把 any 的数量当指标：每迁完一个模块，统计一下剩余的 any，看着它下降会很有成就感，也能及时发现哪些地方在反复绕过类型。迁移的终点不是「零 any」，而是「每个 any 都有正当理由」。"),
        p("迁移完成后，建议补一份简短的迁移记录：哪些模块已迁、哪些还是 any、哪些外部数据没有校验。这份记录不必很长，但它能让团队知道当前类型覆盖的真实水平，避免误以为「用了 TypeScript 就万事大吉」。类型覆盖率和测试覆盖率一样，是过程指标，不是终点；真正重要的是线上错误是否减少、重构是否更快。"),
        p("迁移的最后一步是把「临时方案」清理掉。迁移期间常见的临时手段包括：大量 as any、注释掉的类型、为绕过报错而放宽的配置。每完成一个模块，就应该回头清一遍这些痕迹，否则它们会沉淀成新的技术债。判断标准是：这段代码如果明天交给新人维护，他能不能看懂类型意图？看不懂就说明迁移只完成了一半。类型覆盖率是数字，可维护性才是目标。"),
        p("迁移完成后，建议补一份简短的迁移记录：哪些模块已迁、哪些还是 any、哪些外部数据没有校验。这份记录不必很长，但它能让团队知道当前类型覆盖的真实水平，避免误以为「用了 TypeScript 就万事大吉」。类型覆盖率和测试覆盖率一样，是过程指标，不是终点；真正重要的是线上错误是否减少、重构是否更快。"),
        code("""
            interface RawUser {
              id: number;
              name: string;
            }

            function parseUser(input: any): RawUser {
              var id: number = typeof input.id === 'number' ? input.id : 0;
              var name: string = typeof input.name === 'string' ? input.name : 'unknown';
              return { id: (id), name: (name) };
            }

            function greet(user: RawUser): string {
              return 'HI ' + user.name + '#' + user.id;
            }

            console.log(greet(parseUser({ id: 7, name: 'V' })));
            console.log(greet(parseUser({ name: 'J' })));
        """),
        out("HI V#7\nHI J#0"),
        table(["迁移阶段", "动作", "验收标准"], [
            ["改名", "js → ts，宽松配置", "能编译，行为不变"],
            ["补边界", "导出函数、数据结构加标注", "公共 API 有完整签名"],
            ["消 any", "开启 strict，逐个处理", "any 数量持续下降"],
            ["加校验", "外部输入写解析函数", "未知数据不会进入类型系统"],
        ]),
        tip("迁移时先给「数据」建模，再给「行为」标注。interface 写对了，函数签名水到渠成；反过来先写函数签名，常常会发现数据结构没想清楚，反复返工。"),
        warn("不要把迁移和重构混在一起。迁移阶段只加类型、不改逻辑，这样出问题时能确定是类型标注引起的还是行为改动引起的。等迁移完成、测试稳定后，再单独做重构。"),
        quiz("把 JS 迁到 TS 时，第一步应该做什么？", [
            "重写所有函数，加上完整类型",
            "把文件改成 .ts，用宽松配置跑通",
            "先开启最严格的编译选项",
            "删除所有 any",
        ], 1, "渐进迁移的第一步是让代码在 TS 下跑通，再逐步收紧类型；一上来就开最严格模式会产生大量错误，打击信心也难以定位。"),
        practice("宽松解析", """
            interface User {
              id: number;
              name: string;
            }

            function normalize(input: any): User {
              return {
                id: typeof input.id === 'number' ? input.id : 0,
                name: typeof input.name === 'string' ? input.name : 'unknown'
              };
            }

            console.log(normalize({ id: 1 }).name);
        """, "unknown", "缺失字段用默认值兜底。"),
    ], exercise(
        "把 JS 函数迁成 TS",
        "把下面这段 JS 思路迁成带类型的实现：normalize(input) 把任意输入整理成 User，缺失或类型不对的字段用默认值；describe(user) 返回 'name(id)'；countValid(list) 统计 id 大于 0 的用户数量。",
        """
        interface User {
          id: number;
          name: string;
        }

        function normalize(input: any): User {
          var id: number = typeof input.id === 'number' ? input.id : 0;
          var name: string = typeof input.name === 'string' ? input.name : 'unknown';
          return { id: (id), name: (name) };
        }

        function describe(user: User): string {
          // 返回 name + '(' + id + ')'
          return '';
        }

        function countValid(list: User[]): number {
          // 统计 id > 0 的用户
          return 0;
        }
        """,
        "describe 按格式拼接；countValid 用 for 循环，遇到 id > 0 就累加。",
        [
            "assert(normalize({ id: 1, name: 'V' }).name === 'V', 'normalize 应保留合法字段')",
            "assert(normalize({ id: 'x' }).id === 0, '非法 id 应回退为 0')",
            "assert(describe({ id: 3, name: 'V' }) === 'V(3)', 'describe 格式错误')",
            "assert(countValid([{id:1,name:'a'},{id:0,name:'b'},{id:2,name:'c'}]) === 2, 'countValid 统计错误')",
            "assert(countValid([]) === 0, '空数组应为 0')",
        ],
        """
        interface User {
          id: number;
          name: string;
        }

        function normalize(input: any): User {
          var id: number = typeof input.id === 'number' ? input.id : 0;
          var name: string = typeof input.name === 'string' ? input.name : 'unknown';
          return { id: (id), name: (name) };
        }

        function describe(user: User): string {
          return user.name + '(' + user.id + ')';
        }

        function countValid(list: User[]): number {
          var c: number = 0;
          for (var i = 0; i < list.length; i++) {
            if (list[i].id > 0) {
              c += 1;
            }
          }
          return c;
        }
        """,
        110,
    )),
]


TS_ADVANCED = [
    lesson("ts21", 620, 63, C3, "泛型约束", "限制 T 至少长成什么样", 100, [
        h("给类型参数划一条底线"),
        p("泛型给了完全的自由，但有时函数需要用到 T 的某些成员。`function longest<T>(a: T, b: T): T { return a.length > b.length ? a : b; }` 在标准 TypeScript 里会报错，因为 T 可能是数字，没有 length。解决办法是加约束：`<T extends { length: number }>` 表示 T 必须拥有 number 类型的 length 字段。这叫泛型约束，它把「任意类型」缩小为「至少具备某些能力的类型」。"),
        p("约束的语法是 `T extends 某个类型`。这里的 extends 不是类继承，而是「可赋值给」的意思：任何能赋值给约束类型的类型都可以作为 T。`string` 有 length，数组有 length，带 length 字段的对象也有，所以它们都满足约束；数字不满足，传进去会被 tsc 拒绝。约束越窄，函数体内能做的事越多，但能接收的类型也越少，这是一个需要权衡的取舍。"),
        p("多个类型参数可以互相约束：`function pick<T, K extends keyof T>(obj: T, key: K): T[K]` 表示 K 必须是 T 的某个键，返回值类型是那个键对应的值类型。这个签名是标准库 Pick 和很多工具函数的基础。`keyof T` 是「T 的所有键名组成的联合类型」，`T[K]` 是「用键 K 索引 T 得到的类型」，两者配合能在编译期精确追踪字段。"),
        p("本应用的转译器明确不支持泛型约束：`extends` 会原样保留，导致语法错误，条件类型和映射类型也没有真实运行语义。所以这一讲只讲概念，运行代码里一律用简单泛型，用普通参数和运行时判断替代约束。理解约束的意义仍然重要——你迟早会在真正的 TypeScript 项目里用到它，而现在知道它解决什么问题，将来只需要补语法细节。"),
        p("没有约束时，常见的替代方案有三种：第一，把需要的字段作为独立参数传入，例如 `function longest<T>(a: T, b: T, lengthOf: (v: T) => number): T`，用回调提取长度；第二，用运行时判断守卫，先检查值是否有 length；第三，直接为具体类型写重载或分支。第一种最通用，也最符合「把行为参数化」的思路，本讲的练习就用它。"),
        p("在标准 TypeScript 里，约束还支持默认类型参数：`<T = string>` 表示调用时推断不出来就用 string。这个能力在工具类型里很常见，但本应用不支持默认类型参数，课程里不写。理解默认值的意义即可：它让泛型在「没有实参可推断」时仍有确定的类型，避免退化成 unknown。"),
        p("泛型约束的反面是「过度约束」：把 T 限制得太死，函数就失去了通用性，调用方不得不做类型转换。判断约束是否合理，看它是否只包含「函数体真正用到的成员」。如果函数体只用了 length，就只约束 length；不要顺手把整个数组接口都约束上。约束越精确，可接受的类型越多，函数越通用。这和「依赖最小接口」的设计原则是同一件事。"),
        p("再补充一个判断标准：如果去掉约束后函数体仍然能编译，说明这个约束可能不是必需的。约束应该来自函数体的真实需求，而不是来自「看起来更严谨」。反过来，如果函数体大量使用 as 才能通过编译，说明约束不足或者类型设计有问题。约束和断言是一对反义词：约束越准确，需要的断言越少。"),
        p("再补充一个和本应用相关的现实：因为转译器不支持约束，课程里所有「按能力约束」的需求都改成了「传入能力函数」。这种改写不只为了绕开限制，它本身也是一种更好的设计：把「取长度」这件事显式化，函数就不再假设输入一定有 length，而是依赖调用方提供的能力。依赖越显式，函数越容易测试，也越容易复用到形状不同但语义相同的数据上。"),
        code("""
            type LengthOf = (value: string) => number;

            function longest(a: string, b: string): string {
              if (a.length >= b.length) {
                return a;
              }
              return b;
            }

            function longestBy(a: string, b: string, size: LengthOf): string {
              if (size(a) >= size(b)) {
                return a;
              }
              return b;
            }

            console.log(longest('neon', 'cyberpunk'));
            console.log(longestBy('neon', 'cyberpunk', function (s: string): number { return s.length; }));
        """),
        out("cyberpunk\ncyberpunk"),
        table(["写法", "含义", "本应用可用吗"], [
            ["<T extends { length: number }>", "约束 T 必须有 length", "不可用，转译器不支持"],
            ["<T, K extends keyof T>", "K 必须是 T 的键", "不可用，仅概念"],
            ["传入提取函数", "把取长度这件事参数化", "可用，课程采用"],
            ["运行时判空/判类型", "用 typeof 等收窄", "可用，最稳妥"],
        ]),
        tip("约束的收益是「函数体内可以直接用成员」，代价是「能传进来的类型变少」。设计时先问：这个成员是否所有合理输入都具备？如果答案是「不一定」，就别用约束，改成传入提取函数。"),
        warn("本应用不支持 `T extends ...`。写进代码会直接语法错误，判题必然失败。泛型约束这一讲的所有示例代码都不带约束，只讲思想。"),
        quiz("`<T extends { length: number }>` 表示什么？", [
            "T 必须是 number",
            "T 必须拥有 number 类型的 length 成员",
            "T 是 length 的子类",
            "T 只能是数组",
        ], 1, "extends 在这里是「可赋值给」的约束，要求 T 具备 number 类型的 length 成员；字符串、数组、带 length 的对象都满足。"),
        practice("用回调替代约束", """
            type Size = (s: string) => number;

            function sameSize(a: string, b: string, size: Size): boolean {
              return size(a) === size(b);
            }

            console.log(sameSize('ab', 'cd', function (s: string): number { return s.length; }));
        """, "true", "两个字符串长度都是 2。"),
    ], exercise(
        "按长度取较长的字符串",
        "实现 pickLonger(a, b) 返回较长的字符串，长度相同时返回 a；实现 pickBy(a, b, size) 用回调计算「长度」，返回较大的那个。",
        """
        type Size = (value: string) => number;

        function pickLonger(a: string, b: string): string {
          // 长度相同时返回 a
          return '';
        }

        function pickBy(a: string, b: string, size: Size): string {
          // 用 size 计算后再比较
          return '';
        }
        """,
        "pickLonger 用 a.length >= b.length 判断；pickBy 用 size(a) >= size(b) 判断。",
        [
            "assert(pickLonger('neon', 'cyberpunk') === 'cyberpunk', '应返回较长的字符串')",
            "assert(pickLonger('ab', 'cd') === 'ab', '长度相同时应返回 a')",
            "assert(pickBy('aa', 'b', function (s: string): number { return s.length * 10; }) === 'aa', 'pickBy 应使用回调结果')",
            "assert(pickBy('x', 'yy', function (s: string): number { return s.length; }) === 'yy', 'pickBy 普通场景错误')",
        ],
        """
        type Size = (value: string) => number;

        function pickLonger(a: string, b: string): string {
          if (a.length >= b.length) {
            return a;
          }
          return b;
        }

        function pickBy(a: string, b: string, size: Size): string {
          if (size(a) >= size(b)) {
            return a;
          }
          return b;
        }
        """,
        110,
    )),

    lesson("ts22", 621, 63, C3, "条件类型概念", "类型层面的 if-else", 100, [
        h("当类型需要判断"),
        p("条件类型的写法是 `T extends U ? X : Y`：如果 T 能赋值给 U，结果类型是 X，否则是 Y。它看起来像三元表达式，但作用在类型层面，只在编译期计算。例如 `type IsString<T> = T extends string ? true : false`，`IsString<string>` 得到 true，`IsString<number>` 得到 false。这让类型系统具备了分支能力，可以根据输入类型自动推导输出类型。"),
        p("条件类型最典型的应用是描述函数的返回类型随参数变化。例如一个函数接收字符串返回字符串数组，接收数字返回数字数组，标准库里的很多工具类型就是这么写出来的。条件类型还常与 infer 搭配：`T extends Array<infer U> ? U : never` 能从数组类型里提取元素类型，infer 相当于在类型层面做模式匹配并捕获变量。"),
        p("条件类型有两种特殊行为。第一是分布式：当 T 是联合类型时，条件会对每个成员分别判断，再把结果合并，所以 `IsString<string | number>` 会得到 boolean（true | false 合并的结果）。第二是延迟求值：如果 T 还是未确定的类型参数，条件类型会保持未求值状态，直到调用时才计算。这两条规则让条件类型强大，也让错误信息变得难读。"),
        p("本应用的转译器不支持条件类型的真实运行语义：`A extends B ? X : Y` 这样的类型表达式如果写在标注里，擦除会失败或留下残渣。所以这一讲只讲概念，所有运行代码都不含条件类型。判断逻辑一律用运行时的三元表达式、if 语句或 typeof 收窄来实现——运行时判断和类型层面的条件类型解决的是不同问题，前者影响程序行为，后者只影响类型推导。"),
        p("学习条件类型时不要急着背工具类型的实现，先理解它的三个用途：根据输入类型选择输出类型、从复杂类型中提取一部分、把联合类型拆开逐个处理。看到 `T extends ... ? ... : ...` 时，先在心里读成「如果 T 是……那么……否则……」，再去理解 infer 捕获了什么。等你能读懂标准库的 ReturnType、Parameters、Exclude 的实现，条件类型就算入门了。"),
        p("条件类型和联合类型配合时有一个反直觉的点：分布式条件类型会把联合拆开。`type Boxed<T> = T extends any ? T[] : never`，传入 string | number，得到 string[] | number[]，而不是 (string | number)[]。这个差异在写工具类型时非常重要，想要不拆分可以给 T 套一层元组：`[T] extends [any]`。课程不展开，但你应该知道它存在。"),
        p("条件类型的学习曲线很陡，但用途很集中：几乎都出现在库的类型定义里，业务代码直接写的时候不多。作为应用开发者，你更需要的是「读懂」而不是「写出」：看到 `T extends U ? X : Y`，能说出它在判断什么；看到 infer，能指出它捕获了哪部分。能读懂标准库的 ReturnType、Parameters，就足够应付绝大多数排查场景。真正要写的时候，再回头补语法细节。"),
        p("条件类型还有一个常见用途是「提取函数返回类型」：`type R = ReturnType<typeof fn>`。它让调用方不必重复书写返回类型，函数改签名时下游自动跟随。这类工具类型在库开发里非常常见，业务代码里偶尔用到。理解它们的存在，能帮你在阅读第三方类型定义时不至于卡住，也能在需要时快速找到合适的工具。"),
        p("再补充一个调试经验：条件类型出错时，错误信息往往非常长，因为编译器会把整个类型展开。有效的排查方法是从最内层开始，把复杂的类型拆成几个中间别名，逐个确认求值结果。别试图一次读懂整条错误信息，先定位是哪个别名算错了。这个方法和调试运行时代码一样：缩小范围，逐段验证，而不是盯着整体猜。"),
        code("""
            function describeValue(v: string | number): string {
              if (typeof v === 'string') {
                return 'text:' + v.length;
              }
              return 'num:' + v;
            }

            console.log(describeValue('abc'));
            console.log(describeValue(42));
        """),
        out("text:3\nnum:42"),
        diagram("""
            类型层面（仅概念，本应用不执行）
            ─────────────────────────────────
            type IsString<T> = T extends string ? true : false
            IsString<string>  →  true
            IsString<number>  →  false

            运行层面（本应用执行的部分）
            ─────────────────────────────────
            typeof v === 'string' ? A : B

            两者形状相似，作用域完全不同。
        """),
        tip("把条件类型理解成「类型层面的模式匹配」，比理解成「类型层面的 if」更准确。extends 左边是要匹配的值，右边是模式，infer 声明要捕获的部分。"),
        warn("条件类型只在类型标注里出现，不会生成运行时代码。本应用会尝试擦除它但结果不可靠，因此课程代码一律不写条件类型，只保留运行时判断。"),
        quiz("`type R<T> = T extends string ? 'text' : 'other'`，那么 `R<number>` 是什么？", [
            "'text'",
            "'other'",
            "number",
            "报错",
        ], 1, "number 不能赋值给 string，条件为假，取冒号后面的分支 'other'。"),
        practice("运行时模拟条件分支", """
            function kindOf(v: string | number): string {
              return typeof v === 'string' ? 'text' : 'other';
            }

            console.log(kindOf('a'), kindOf(1));
        """, "text other", "用运行时三元表达式完成同样的分支。"),
    ], exercise(
        "按类型分派处理",
        "实现 route(v)：字符串返回 'S:' 加长度，数字返回 'N:' 加数值，布尔返回 'B:' 加值。这是条件类型在运行时的等价实现。",
        """
        function route(v: string | number | boolean): string {
          // 用 typeof 分三种情况
          return '';
        }
        """,
        "依次判断 typeof v === 'string'、'number'、'boolean'，每个分支返回对应前缀。",
        [
            "assert(route('abc') === 'S:3', '字符串应返回长度')",
            "assert(route(42) === 'N:42', '数字应原样输出')",
            "assert(route(false) === 'B:false', '布尔值应输出 false')",
            "assert(route('') === 'S:0', '空字符串长度是 0')",
        ],
        """
        function route(v: string | number | boolean): string {
          if (typeof v === 'string') {
            return 'S:' + v.length;
          }
          if (typeof v === 'number') {
            return 'N:' + v;
          }
          return 'B:' + v;
        }
        """,
        110,
    )),

    lesson("ts23", 622, 63, C3, "映射类型概念", "批量改造已有类型的字段", 100, [
        h("把一个类型映射成另一个"),
        p("映射类型的写法是 `{ [K in keyof T]: 新类型 }`：遍历 T 的每个键 K，为每个键生成一个新字段。最常见的例子是 `type Flags<T> = { [K in keyof T]: boolean }`，它把任意对象类型的每个字段都变成布尔值。标准库的 Partial、Required、Readonly、Pick、Omit 全部建立在映射类型之上，是 TypeScript 类型系统里复用度最高的一层。"),
        p("映射时可以在键上加重映射修饰符：`+?` 和 `-?` 控制可选性，`+readonly` 和 `-readonly` 控制只读性。Partial 等价于给每个键加 `?`，Required 等价于去掉 `?`，Readonly 等价于加 readonly。这些修饰符让「同一结构的不同变体」可以自动生成，不必手工维护几份重复的 interface，改一处就能同步到所有变体。"),
        p("映射类型还可以配合 `as` 做键名重映射，例如把每个键名加上 get 前缀。这是比较高级的用法，标准库里有，但日常业务代码用得不多。更常见的是「值类型转换」：把所有字段变成可选、变成只读、变成另一种类型。理解映射类型的关键是记住它遍历的是「键」，而条件类型遍历的是「联合成员」，两者经常组合使用。"),
        p("本应用不执行映射类型的真实语义：`{ [K in keyof T]: ... }` 写在标注里会被擦除器误判，可能留下语法错误。所以这一讲同样只讲概念，运行代码统一用具体 interface 和普通对象。需要「部分更新」「全部必填」这类结构时，用 Partial、Required 这类工具类型做标注（它们能被擦掉），但运行时对象仍然手工构造。"),
        p("映射类型的实际价值在于减少重复。假设你有 Order、OrderPatch、OrderReadonly 三个几乎一样的接口，字段一改就要改三处。用映射类型可以只定义 Order，另外两个由它推导出来，改一处全部同步。这也是「类型即代码」的体现：类型可以像函数一样被计算和组合，而不是只能一行行手写。"),
        p("映射类型还能和条件类型组合，实现「只保留函数类型的字段」这类筛选。写法是先用键遍历，再用条件判断值类型，不满足的映射成 never，最后用键筛选去掉 never。这套组合是标准库 Omit、Exclude 的实现基础，可读性较差，实际项目中通常直接用现成工具类型，不必自己写。"),
        p("映射类型的实际使用频率比想象中低，因为标准库已经把常用变换封装成了工具类型。你真正需要自己写映射类型的场景通常是：批量改值类型（全部变成 boolean、全部变成可选）、批量改键名（加前缀）、按键筛选字段。这三种之外，优先找现成工具。理解原理的价值在于：当工具类型的行为不符合预期时，你能看懂它的定义，知道该换哪个，而不是盲目试错。"),
        p("映射类型有一个容易忽略的限制：它只能作用于对象类型，不能作用于联合类型或基础类型。想对联合类型做批量变换，要用条件类型；想对基础类型做变换，基本没有通用手段。理解这个边界，你就不会写出「对 string 做映射」这种无效代码，也能在选型时快速判断该用映射、条件还是工具类型。"),
        p("再补充一个工程判断：如果一个映射类型需要写超过三行，而且只在某一个文件里用一次，直接手写 interface 往往更快。映射类型的优势是「随源类型自动同步」，只有当源类型会变、派生类型需要跟随变化时才值得。一次性使用的派生，手写虽然啰嗦，但可读性更好，也不会在下一个人读代码时制造额外的跳转。工具要用在刀刃上。"),
        code("""
            interface Order {
              id: string;
              total: number;
              note: string;
            }

            interface OrderSummary {
              id: string;
              total: number;
            }

            function summarize(o: Order): OrderSummary {
              return { id: (o.id), total: (o.total) };
            }

            var full: Order = { id: 'A1', total: 30, note: 'rush' };
            var slim: OrderSummary = summarize(full);

            console.log(slim.id, slim.total);
            console.log(full.note);
        """),
        out("A1 30\nrush"),
        table(["工具类型", "等价的映射写法", "效果"], [
            ["Partial<T>", "{ [K in keyof T]?: T[K] }", "所有字段变可选"],
            ["Required<T>", "{ [K in keyof T]-?: T[K] }", "所有字段变必填"],
            ["Readonly<T>", "{ readonly [K in keyof T]: T[K] }", "所有字段变只读"],
            ["Pick<T, K>", "只保留 K 中的键", "挑选字段"],
            ["Omit<T, K>", "排除 K 中的键", "去掉字段"],
        ]),
        tip("映射类型的收益是「定义一次、派生多个变体」。当你有三个以上高度相似的结构时，先想想能不能用映射类型或工具类型派生，而不是复制粘贴 interface。"),
        warn("映射类型只存在于类型层。本应用会尝试擦除 `{ [K in keyof T]: ... }`，但结果不可靠。课程代码里只用 Partial、Required、Pick、Omit 这类具名工具类型做标注，不写内联映射语法。"),
        quiz("`Partial<T>` 的作用是什么？", [
            "把 T 的所有字段变成必填",
            "把 T 的所有字段变成可选",
            "把 T 变成数组",
            "删除 T 的所有字段",
        ], 1, "Partial 通过映射类型给每个键加上可选修饰符，得到所有字段都可选的新类型。"),
        practice("用具体接口模拟映射", """
            interface Order {
              id: string;
              total: number;
            }

            interface OrderFlags {
              id: boolean;
              total: boolean;
            }

            var flags: OrderFlags = { id: true, total: false };
            console.log(flags.id, flags.total);
        """, "true false", "手写结构相同、值类型全为布尔的接口，就是映射类型的手工版本。"),
    ], exercise(
        "用工具类型做部分更新",
        "实现 makeDraft(o) 返回一个 Partial<Order>，只包含 id；实现 makeFull(p) 接收 Partial<Order> 并返回 Order，缺失字段用空串和 0 补齐；实现 pickPreview(o) 返回 Pick<Order, 'id' | 'total'>。",
        """
        interface Order {
          id: string;
          total: number;
          note: string;
        }

        function makeDraft(o: Order): Partial<Order> {
          return { id: (o.id) };
        }

        function makeFull(p: Partial<Order>): Order {
          // 缺失字段用 '' 和 0 补齐
          return { id: '', total: 0, note: '' };
        }

        type OrderPreview = Pick<Order, 'id' | 'total'>;

        function pickPreview(o: Order): OrderPreview {
          // 只返回 id 与 total
          return { id: '', total: 0 };
        }
        """,
        "makeFull 用 p.id === undefined ? '' : p.id 这种三元判断；pickPreview 直接构造只含两个字段的对象。",
        [
            "assert(makeDraft({id:'A', total:1, note:'x'}).id === 'A', 'makeDraft 应保留 id')",
            "assert(makeDraft({id:'A', total:1, note:'x'}).total === undefined, 'makeDraft 不应包含 total')",
            "assert(makeFull({id:'B'}).total === 0, 'makeFull 应补齐 total')",
            "assert(makeFull({id:'B'}).note === '', 'makeFull 应补齐 note')",
            "assert(pickPreview({id:'C', total:5, note:'x'}).total === 5, 'pickPreview 应保留 total')",
        ],
        """
        interface Order {
          id: string;
          total: number;
          note: string;
        }

        function makeDraft(o: Order): Partial<Order> {
          return { id: (o.id) };
        }

        function makeFull(p: Partial<Order>): Order {
          var id: string = p.id === undefined ? '' : p.id;
          var total: number = p.total === undefined ? 0 : p.total;
          var note: string = p.note === undefined ? '' : p.note;
          return { id: (id), total: (total), note: (note) };
        }

        type OrderPreview = Pick<Order, 'id' | 'total'>;

        function pickPreview(o: Order): OrderPreview {
          return { id: (o.id), total: (o.total) };
        }
        """,
        110,
    )),

    lesson("ts24", 623, 63, C3, "工具类型 Partial / Required / Pick / Omit", "四个最常用的类型工具", 110, [
        h("标准库送你的四个工具"),
        p("Partial<T> 把所有字段变成可选，适合「部分更新」的参数：`function patch(o: Order, changes: Partial<Order>)`。Required<T> 相反，把所有字段变成必填，适合「完整数据」的校验结果。Pick<T, K> 保留指定键，适合做列表页的精简结构；Omit<T, K> 去掉指定键，适合隐藏敏感字段或去掉大字段。这四个工具覆盖了日常开发的大部分结构变换。"),
        p("它们的共同点是只影响类型，不产生运行时代码。`var p: Partial<Order> = { id: 'A1' }` 在 tsc 下合法，运行时就是一个只有 id 的对象，没有任何「可选」标记。所以使用工具类型时，运行时逻辑必须自己处理缺失字段：读取前判 undefined，构造完整对象时补齐默认值。类型负责表达意图，运行时负责实现行为，两者不能互相替代。"),
        p("Pick 和 Omit 的第二个参数是键名的联合：`Pick<Order, 'id' | 'total'>`。键名写错会被 tsc 拒绝，这是它们比手写 interface 更安全的地方——手写时改字段名容易漏改，Pick/Omit 会自动跟着源类型走。本应用的转译器能正确擦除这些标注，因为它们的形状是「标识符 + 尖括号 + 字面量」，课程里可以放心使用。"),
        p("什么时候不该用工具类型？当两个结构的字段差异很大、语义也完全不同时，用 Pick 强行派生会让读者频繁跳转，不如直接写下新 interface。工具类型的价值在于表达「这两个结构本质相同，只是视角不同」；如果它们本质不同，就应该分开定义。另一个注意点是嵌套：Partial 只影响第一层，嵌套对象仍然是必填的，深层可选需要单独定义或使用递归工具类型。"),
        p("这四个工具经常组合使用。例如「创建请求」用 Omit<Order, 'id' | 'createdAt'>，「更新请求」用 Partial<Omit<Order, 'id'>>，「列表项」用 Pick<Order, 'id' | 'total'>。把这几个派生类型集中定义在类型文件里，业务代码只引用名字，读起来就像在读需求文档。工具类型不是炫技，而是把「同一实体的不同视图」表达清楚的手段。"),
        p("工具类型还有一个常见误区：以为它们会生成新对象。`var p: Partial<Order> = { ... }` 里的 Partial 只是标注，对象本身仍然是普通对象，字段数量不会自动减少。要真正删掉字段，必须手工构造新对象或用解构（本应用不支持解构赋值，所以一律手工构造）。类型和值始终是两条线。"),
        p("四个工具类型里，Partial 和 Pick 用得最多，Omit 次之，Required 最少。原因是现实中的数据大多是「不完整」的：创建时没有 ID，更新时只改几个字段，列表页只需要几个字段。Required 通常出现在「校验通过之后」——外部输入校验完，你才敢断言所有字段都在。把这四个类型和你的数据流阶段对应起来：输入用 Partial、展示用 Pick、创建用 Omit、校验后用 Required。"),
        p("四个工具类型都只影响第一层，这一点要反复提醒自己。嵌套对象的部分字段可选，需要为嵌套类型单独定义 Partial，再组合。深层可选、深层只读这类需求，标准库没有现成工具，需要自己写递归类型，或者干脆手工定义。业务代码里，宁可多写一个明确的 interface，也不要用复杂的递归类型——后者调试成本很高。"),
        p("再补充一个命名实践：给派生类型起名时带上「视角」而不是「操作」。`OrderPreview` 比 `OrderPick` 好，`OrderPatch` 比 `OrderPartial` 好，因为前者描述用途，后者描述实现。读者关心的是这个类型在业务里代表什么，而不是它用了哪个工具类型生成的。将来生成方式变了（比如从 Pick 改成手写），名字不需要改，调用方也无感。"),
        code("""
            interface Order {
              id: string;
              total: number;
              note: string;
            }

            type OrderPatch = Partial<Order>;
            type OrderFull = Required<Order>;
            type OrderPreview = Pick<Order, 'id' | 'total'>;
            type OrderDraft = Omit<Order, 'id'>;

            var patch: OrderPatch = { total: 9 };
            var full: OrderFull = { id: 'A1', total: 1, note: 'x' };
            var preview: OrderPreview = { id: 'A2', total: 2 };
            var draft: OrderDraft = { total: 3, note: 'new' };

            console.log(patch.total);
            console.log(full.id);
            console.log(preview.total);
            console.log(draft.note);
        """),
        out("9\nA1\n2\nnew"),
        table(["工具类型", "作用", "典型场景"], [
            ["Partial<T>", "所有字段可选", "部分更新、补丁"],
            ["Required<T>", "所有字段必填", "完整校验后的数据"],
            ["Pick<T, K>", "只保留指定字段", "列表项、预览"],
            ["Omit<T, K>", "去掉指定字段", "创建请求、隐藏敏感字段"],
        ]),
        tip("派生类型命名建议带上用途：OrderPatch、OrderPreview、OrderDraft。名字比 `Partial<Order>` 更容易在读代码时快速理解，也方便将来调整派生规则时只改一处。"),
        warn("Partial 只作用于第一层字段。`Partial<Order>` 里的嵌套对象仍然保持原样，深层字段依然必填。需要深层可选时，必须单独定义嵌套类型或使用递归工具类型，本课程不展开。"),
        quiz("要从 Order 中去掉 id 字段得到创建请求类型，应该用哪个工具？", [
            "Pick<Order, 'id'>",
            "Omit<Order, 'id'>",
            "Partial<Order>",
            "Required<Order>",
        ], 1, "Omit 排除指定键，保留其余字段，正好用于「创建时还没有 id」的场景。"),
        practice("四个派生类型", """
            interface User {
              id: number;
              name: string;
              email: string;
            }

            type UserPreview = Pick<User, 'id' | 'name'>;
            type UserPatch = Partial<User>;

            var p: UserPreview = { id: 1, name: 'V' };
            var patch: UserPatch = { name: 'W' };
            console.log(p.id, p.name, patch.name);
        """, "1 V W", "派生类型只影响标注，对象本身仍是普通对象。"),
    ], exercise(
        "订单的四种视图",
        "基于 Order 定义四个派生类型：OrderPatch = Partial<Order>，OrderPreview = Pick<Order, 'id' | 'total'>，OrderDraft = Omit<Order, 'id'>，OrderFull = Required<Order>。实现 previewOf(o) 返回 OrderPreview，实现 totalOfPatch(p) 返回 p.total 或 0。",
        """
        interface Order {
          id: string;
          total: number;
          note: string;
        }

        type OrderPatch = Partial<Order>;

        type OrderPreview = Pick<Order, 'id' | 'total'>;

        function previewOf(o: Order): OrderPreview {
          return { id: '', total: 0 };
        }

        function totalOfPatch(p: OrderPatch): number {
          // total 缺失时返回 0
          return 0;
        }
        """,
        "previewOf 直接取 id 和 total 构造新对象；totalOfPatch 用 `p.total === undefined ? 0 : p.total`。",
        [
            "assert(previewOf({id:'A', total:5, note:'x'}).id === 'A', 'previewOf 应保留 id')",
            "assert(previewOf({id:'A', total:5, note:'x'}).total === 5, 'previewOf 应保留 total')",
            "assert(totalOfPatch({}) === 0, '空补丁应返回 0')",
            "assert(totalOfPatch({total: 7}) === 7, '有 total 时应返回其值')",
            "assert(totalOfPatch({total: 0}) === 0, '0 应保持为 0')",
        ],
        """
        interface Order {
          id: string;
          total: number;
          note: string;
        }

        type OrderPatch = Partial<Order>;

        type OrderPreview = Pick<Order, 'id' | 'total'>;

        function previewOf(o: Order): OrderPreview {
          return { id: (o.id), total: (o.total) };
        }

        function totalOfPatch(p: OrderPatch): number {
          if (p.total === undefined) {
            return 0;
          }
          return p.total;
        }
        """,
        120,
    )),

    lesson("ts25", 624, 63, C3, "可辨识联合", "用 kind 字段区分分支", 110, [
        h("让每个分支都带上身份证"),
        p("可辨识联合是把多个对象类型用联合连起来，并让每个成员都有一个字面量类型的「标签字段」。例如 `interface Circle { kind: 'circle'; radius: number }` 和 `interface Square { kind: 'square'; side: number }`，联合起来就是 `type Shape = Circle | Square`。标签字段通常是 kind、type 或 status，值必须是字面量类型，不能是宽泛的 string。"),
        p("可辨识联合的核心能力是自动收窄。写 `if (shape.kind === 'circle')`，编译器立刻知道分支内 shape 是 Circle，可以直接访问 radius；else 分支则自动变成 Square。这比手写类型断言安全得多，也比运行时判断更精确。switch 语句同样有效，每个 case 里都能拿到对应成员的字段，写错字段名会被 tsc 当场发现。"),
        p("可辨识联合适合描述「互斥的几种情况」：支付方式的信用卡、银行转账、余额支付；消息的文本、图片、系统通知；状态的加载中、成功、失败。关键在于每个成员的业务字段完全不同，用标签区分后，代码里就不会出现「访问了不属于当前分支的字段」这类错误。相比把所有字段堆在一个接口里、全部标成可选，可辨识联合让非法状态在类型层面就无法构造。"),
        p("设计时有三个要点。第一，标签字段必须是字面量类型，写成 string 就失去辨识能力；第二，标签值必须唯一，两个成员用同一个 kind 会让收窄失效；第三，每个成员只放自己需要的字段，不要为了「统一」把所有字段都加上并在不适用的分支里留空。第三点尤其重要，它决定了类型能否真正表达业务约束，而不是变成另一种形式的大杂烩。"),
        p("本应用支持可辨识联合的运行时写法：标签字段就是普通字符串字段，判断分支就是普通 if 或 switch，对象字面量正常构造。唯一要避开的是联合类型在复杂位置的标注，例如嵌套过深的交叉和条件类型。课程里的例子都用两个到三个成员，标签直接比较字符串，既清晰又能被转译器正确处理。"),
        p("可辨识联合在状态管理里特别有用。加载状态可以定义成 `Loading | Success | Failure` 三个成员，每个成员带自己的数据：Loading 没有数据，Success 带 data，Failure 带 error。这样代码里就不会出现「既在加载又有错误」这种非法组合，也不需要用一堆布尔字段互相约束。用类型表达状态，比用注释约束状态可靠得多。"),
        p("可辨识联合的关键在于「标签值唯一且稳定」。如果两个成员的标签值可能相同，收窄就会失效；如果标签值会被外部修改，收窄的前提就被破坏。所以标签字段应该在建对象时一次确定，之后不再改。业务状态变化时，应该创建新对象而不是原地改标签，这样每一份数据在任一时刻都属于确定的成员，判断逻辑才不会出现「既像 A 又像 B」的中间态。"),
        p("可辨识联合还有一个配套技巧：把「共同字段」抽到一个基础接口里，让每个成员继承它。例如所有支付方式都有 amount 和 createdAt，就定义 PaymentBase，再让 Cash、Card、Wallet 各自 extends。这样公共字段只写一次，判断逻辑里也能安全访问公共字段，不必先收窄。联合的成员越多，这个技巧越有价值。"),
        p("再补充一个常见错误：把标签字段命名成 type。`type` 是 TypeScript 关键字，虽然作为属性名合法，但在某些工具和文档生成器里会引起歧义，读代码时也容易和类型声明混淆。用 kind、tag、status 更安全。命名上的小细节，长期看能减少很多解释成本；团队的命名约定越统一，新成员理解联合结构的门槛越低。"),
        code("""
            interface Circle {
              kind: 'circle';
              radius: number;
            }

            interface Square {
              kind: 'square';
              side: number;
            }

            type Shape = Circle | Square;

            function area(shape: Shape): number {
              if (shape.kind === 'circle') {
                return 3.14 * shape.radius * shape.radius;
              }
              return shape.side * shape.side;
            }

            console.log(area({ kind: 'circle', radius: 2 }));
            console.log(area({ kind: 'square', side: 3 }));
        """),
        out("12.56\n9"),
        diagram("""
            Shape = Circle | Square
                      │         │
                      │         └─ kind: 'square'，字段 side
                      └─ kind: 'circle'，字段 radius

            if (shape.kind === 'circle')
                └─ 分支内自动收窄为 Circle，可访问 radius

            else 分支自动变成 Square，可访问 side。
        """),
        tip("标签字段建议统一叫 kind，值用小写单词。项目里保持一致比追求命名花样重要得多，统一的标签让所有联合类型的判断代码看起来一致，也方便搜索。"),
        warn("本应用不做类型检查，所以「构造一个 kind 与字段不匹配的对象」在运行时仍然能跑。可辨识联合的保护全部发生在编写阶段，运行时正确性靠你自己遵守约定。"),
        quiz("可辨识联合中，标签字段为什么必须是字面量类型？", [
            "为了节省内存",
            "只有字面量类型才能让编译器在判断时收窄到具体成员",
            "因为 JavaScript 不支持字符串",
            "为了让运行时能检查",
        ], 1, "标签值如果是宽泛的 string，编译器无法确定每个值的唯一成员；字面量类型让 kind === 'circle' 精确指向 Circle。"),
        practice("消息分支", """
            interface TextMsg {
              kind: 'text';
              body: string;
            }

            interface ImageMsg {
              kind: 'image';
              url: string;
            }

            type Msg = TextMsg | ImageMsg;

            function preview(m: Msg): string {
              if (m.kind === 'text') {
                return m.body.slice(0, 3);
              }
              return m.url;
            }

            console.log(preview({ kind: 'text', body: 'hello' }), preview({ kind: 'image', url: 'a.png' }));
        """, "hel a.png", "两个分支各自访问自己的字段。"),
    ], exercise(
        "三种支付方式",
        "定义 Cash（kind: 'cash'，amount）、Card（kind: 'card'，amount、last4）、Wallet（kind: 'wallet'，amount、account）三个接口并联合成 Payment。实现 payLabel(p) 返回 'cash:金额'、'card:尾号'、'wallet:账号'；实现 totalOf(list) 累加所有金额。",
        """
        interface Cash {
          kind: 'cash';
          amount: number;
        }

        interface Card {
          kind: 'card';
          amount: number;
          last4: string;
        }

        interface Wallet {
          kind: 'wallet';
          amount: number;
          account: string;
        }

        type Payment = Cash | Card | Wallet;

        function payLabel(p: Payment): string {
          if (p.kind === 'cash') {
            return 'cash:' + p.amount;
          }
          if (p.kind === 'card') {
            return 'card:' + p.last4;
          }
          return 'wallet:' + p.account;
        }

        function totalOf(list: Payment[]): number {
          // 累加 amount
          return 0;
        }
        """,
        "totalOf 用 for 循环遍历，直接累加 list[i].amount——三个成员都有 amount，联合类型下也能访问。",
        [
            "assert(payLabel({kind:'cash', amount:10}) === 'cash:10', '现金标签错误')",
            "assert(payLabel({kind:'card', amount:10, last4:'1234'}) === 'card:1234', '银行卡标签错误')",
            "assert(payLabel({kind:'wallet', amount:10, account:'u1'}) === 'wallet:u1', '钱包标签错误')",
            "assert(totalOf([{kind:'cash', amount:10}, {kind:'card', amount:5, last4:'1'}]) === 15, '金额累加错误')",
            "assert(totalOf([]) === 0, '空列表应为 0')",
        ],
        """
        interface Cash {
          kind: 'cash';
          amount: number;
        }

        interface Card {
          kind: 'card';
          amount: number;
          last4: string;
        }

        interface Wallet {
          kind: 'wallet';
          amount: number;
          account: string;
        }

        type Payment = Cash | Card | Wallet;

        function payLabel(p: Payment): string {
          if (p.kind === 'cash') {
            return 'cash:' + p.amount;
          }
          if (p.kind === 'card') {
            return 'card:' + p.last4;
          }
          return 'wallet:' + p.account;
        }

        function totalOf(list: Payment[]): number {
          var total: number = 0;
          for (var i = 0; i < list.length; i++) {
            total += list[i].amount;
          }
          return total;
        }
        """,
        120,
    )),

    lesson("ts26", 625, 63, C3, "类型守卫函数", "让编译器读懂你的判断", 110, [
        h("把判断封装成可复用的守卫"),
        p("类型守卫函数的返回类型写成 `value is 类型`，例如 `function isString(v: unknown): v is string { return typeof v === 'string'; }`。它的返回值仍然是布尔值，但对编译器多了一层含义：当这个函数返回 true 时，调用处的 v 会被收窄成 string。这把运行时判断和类型收窄绑定在一起，既复用了代码，又让后续访问安全。"),
        p("守卫函数的价值在复杂判断时最明显。检查一个对象是否符合 interface 需要好几行：不是 null、是 object、关键字段类型正确。把这些逻辑写进 `function isOrder(v: unknown): v is Order`，调用处只需要一行 if，后续代码就能直接访问 order.id。判断逻辑集中在一处，修改规则时只改一个函数，所有调用点自动受益。"),
        p("写守卫函数时有两个纪律。第一，函数体必须真的检查了所有关键字段，不能只写 return true 然后靠断言，否则收窄是假的，运行时照样崩。第二，尽量避免副作用，守卫只做判断，不修改传入的值。本应用不做类型检查，所以第二点尤其重要——类型层面不会验证你的实现，只能靠代码评审和测试保证守卫名副其实。"),
        p("守卫函数的返回类型 `v is string` 在本应用的转译器里会被擦除，运行时只留下普通函数。这没有问题，因为守卫的运行时行为就是返回布尔值；类型收窄只在编写阶段生效。但要注意函数名要能表达「判断什么」，isString、isOrder、hasId 这类命名让调用处读起来像自然语言，也让守卫和普通布尔函数的区别一目了然。"),
        p("守卫可以组合：先写基础守卫 isObject、isString、isNumber，再在 isOrder 里调用它们。组合时保持「每个守卫只判断一件事」的原则，复杂对象由多个小守卫拼成。这样每个守卫都容易测试，出错时也容易定位是哪一层判断漏了。测试守卫时既要测通过的情况，也要测字段缺失、类型不对、null 等失败情况，否则很容易写出永远返回 true 的假守卫。"),
        p("守卫函数还可以处理数组：`function isOrderList(v: unknown): v is Order[]` 先判断 Array.isArray，再循环调用 isOrder。这样嵌套结构也能逐层校验。代价是复杂度上升，性能也有开销，所以只对外部输入做一次完整校验，内部传递的数据信任类型即可，不必每一层都重复检查。"),
        p("守卫函数是「运行时校验」和「编译期收窄」的交汇点，也是类型系统里少数需要你同时保证两边正确的地方。写完后一定要测试失败分支：字段缺失、类型错误、null、空对象、数组混入。只测通过分支的守卫，等于没有守卫。另一个实践是让守卫保持纯函数：不修改输入、不抛异常、不依赖外部状态。纯守卫可以被任意组合，也可以放心地在循环里反复调用。"),
        p("守卫函数和断言的分工可以这样理解：守卫负责「确认」，断言负责「声明」。守卫在运行时真的检查了，断言只是口头保证。对外部数据用守卫，对内部已确认的数据用断言（甚至不用）。混用会让代码失去可信度：读者无法判断一个值到底是真检查过，还是只是被断言过。把两者分开，代码的可靠性才可评估。"),
        p("再补充一个测试建议：给守卫函数写「表格测试」。准备一组输入和期望结果，逐行验证：合法对象、缺字段、字段类型错、null、undefined、数组、字符串、数字。表格测试能快速覆盖所有分支，也方便后续加新规则时回归。守卫是数据入口的把关人，它的正确性直接决定后续代码能否信任类型，值得多花时间测试。"),
        code("""
            interface Order {
              id: string;
              total: number;
            }

            function isOrder(v: unknown): boolean {
              if (v === null || typeof v !== 'object') {
                return false;
              }
              var o: any = v;
              return typeof o.id === 'string' && typeof o.total === 'number';
            }

            var good: unknown = { id: 'A1', total: 30 };
            var bad: unknown = { id: 'A1' };

            console.log(isOrder(good), isOrder(bad));
            console.log(isOrder(null), isOrder('x'));
        """),
        out("true false\nfalse false"),
        table(["守卫", "判断内容", "典型实现"], [
            ["isString(v)", "是否为字符串", "typeof v === 'string'"],
            ["isNumber(v)", "是否为数字", "typeof v === 'number' && !isNaN(v)"],
            ["isOrder(v)", "是否符合 Order", "非空 + 逐字段检查"],
            ["hasId(v)", "是否带 id 字段", "'id' in v 或 v.id !== undefined"],
        ]),
        tip("守卫函数只负责判断，不负责转换。需要「判断并返回规范化结果」时，写两个函数：isOrder 判断、parseOrder 转换。职责分开后，两者都能单独测试，调用处也能按需选择。"),
        warn("本应用的转译器不支持 `v is Order` 这种返回类型标注，写了会擦除失败。课程里守卫函数统一返回 boolean，靠运行时判断保证正确性；概念上它仍然是类型守卫，只是类型层的收窄在真正的 tsc 下才生效。"),
        quiz("类型守卫函数 `function isString(v: unknown): v is string` 的返回值在运行时是什么？", [
            "string",
            "boolean",
            "unknown",
            "没有返回值",
        ], 1, "`v is string` 只是类型层标注，函数体返回的仍是普通布尔值。"),
        practice("基础守卫组合", """
            function isObject(v: unknown): boolean {
              return v !== null && typeof v === 'object';
            }

            function hasId(v: unknown): boolean {
              if (!isObject(v)) { return false; }
              var o: any = v;
              return typeof o.id === 'string';
            }

            console.log(hasId({ id: 'a' }), hasId({}), hasId(null));
        """, "true false false", "先判断是对象，再判断字段。"),
    ], exercise(
        "订单守卫与安全解析",
        "实现 isOrder(v) 判断对象是否有 string 类型的 id 和 number 类型的 total；实现 firstValid(list) 返回第一个通过守卫的元素，没有则返回 null。",
        """
        interface Order {
          id: string;
          total: number;
        }

        function isOrder(v: unknown): boolean {
          // 非空、是对象、id 为 string、total 为 number
          return false;
        }

        function firstValid(list: any[]): Order | null {
          // 返回第一个通过 isOrder 的元素
          return null;
        }
        """,
        "isOrder 先判 v === null 与 typeof v !== 'object'，再用 any 中转访问字段；firstValid 循环调用 isOrder，命中就 return list[i]，否则返回 null。",
        [
            "assert(isOrder({id:'A', total:1}) === true, '合法订单应通过')",
            "assert(isOrder({id:'A'}) === false, '缺少 total 应失败')",
            "assert(isOrder({id:1, total:1}) === false, 'id 非字符串应失败')",
            "assert(isOrder(null) === false, 'null 应失败')",
            "assert(firstValid([{id:'A'}, {id:'B', total:2}])!.total === 2, '应返回第一个合法元素')",
        ],
        """
        interface Order {
          id: string;
          total: number;
        }

        function isOrder(v: unknown): boolean {
          if (v === null || typeof v !== 'object') {
            return false;
          }
          var o: any = v;
          return typeof o.id === 'string' && typeof o.total === 'number';
        }

        function firstValid(list: any[]): Order | null {
          for (var i = 0; i < list.length; i++) {
            if (isOrder(list[i])) {
              return list[i];
            }
          }
          return null;
        }
        """,
        120,
    )),

    lesson("ts27", 626, 63, C3, "声明文件 .d.ts", "为没有类型的代码补一份说明", 100, [
        h("给外部世界写一份说明书"),
        p("声明文件以 .d.ts 结尾，里面只有类型声明，没有实现。它的作用是告诉 TypeScript「这个模块长什么样」：导出了哪些函数、参数和返回值是什么、有哪些 interface。库作者会随包发布 .d.ts，编辑器安装后立刻有补全和检查；没有声明文件的库，要么由社区维护 @types 包，要么自己写一份最小的。"),
        p("声明文件里用 declare 关键字描述外部存在的东西：`declare function now(): string;` 表示运行时存在一个 now 函数；`declare var VERSION: string;` 表示存在一个全局变量；`declare module 'legacy-lib' { ... }` 描述整个模块。declare 的意思是「我保证运行时存在，编译器不用管实现」，所以声明文件里不能写函数体，只能写签名。"),
        p("写声明文件的关键是「只声明你用到的那部分」。一个庞大的库可能有上百个 API，你的项目只用了三个，那就只写这三个的签名。这样工作量小、维护成本低，将来用到更多再补。签名要尽量准确：参数类型写宽了会失去检查，写窄了会误报；返回值类型不确定时先用 unknown，用的时候再收窄，比写 any 安全。"),
        p("本应用会删除以 declare 开头的整行，所以 `declare function now(): string;` 不会留下任何运行时代码。这意味着声明文件在本应用里只能作为「讲解用的静态片段」，不能真正提供类型检查，也不能调用未定义的函数。课程里的示例会标注为不可运行，帮助你区分「描述类型」和「运行代码」这两件事。"),
        p("声明文件还有一个实用场景：给 JS 文件补类型而不改 JS。项目里有一段老代码，你不想动它，可以写一个同名 .d.ts 描述它的导出，然后在 ts 文件里正常 import。这种「类型与实现分离」的能力，是渐进迁移的关键工具。等老代码将来重写时，声明文件可以直接删掉，不会留下运行时包袱。"),
        p("最后提醒一个常见坑：把 .d.ts 和 .ts 放在同名同目录下，TypeScript 会优先使用声明文件，导致你新建的实现文件被忽略。规范做法是声明文件和实现文件放在不同目录，用 outDir 或 types 字段区分。本应用不涉及目录解析，但迁移到真实项目时，这个坑非常常见。"),
        p("声明文件的质量直接影响使用体验。一份好的声明文件应该做到：类型精确到能防止常见误用，注释说明每个函数的副作用和边界，导出结构和你实际 import 的方式一致。最容易被忽略的是「可选参数」和「重载」：库函数常常有多种调用形式，声明文件要如实描述，否则使用者会遇到莫名其妙的类型错误。写不准的地方宁可标 unknown，也不要标 any，前者会提醒使用者校验。"),
        p("声明文件还要注意版本匹配。库升级后，声明文件可能没有同步更新，导致类型和实现不一致。症状是「运行时正常但类型报错」或「类型通过但运行时缺方法」。排查方法是核对包的版本和 @types 包的版本，必要时锁定版本或换用库自带的声明。类型定义也是依赖，需要和代码一起升级、一起测试。"),
        code_static("""
            // 声明文件示例（静态片段，不可运行）
            // 文件：legacy.d.ts

            declare function now(): string;

            declare var VERSION: string;

            interface LegacyOrder {
              id: string;
              total: number;
            }

            declare function loadOrder(id: string): LegacyOrder | null;
        """),
        out("（声明文件只描述类型，不产生运行代码，因此没有输出）"),
        p("声明文件本身不运行，但它描述的接口可以在真正的实现代码里使用。下面这段是可以运行的：interface 被擦除，函数按普通对象访问字段，输出和声明完全一致。对比上一段静态片段，你能直观看到「描述类型」和「运行代码」的边界。"),
        code("""
            interface LegacyOrder {
              id: string;
              total: number;
            }

            function describeOrder(o: LegacyOrder): string {
              return o.id + '=' + o.total;
            }

            console.log(describeOrder({ id: 'A1', total: 30 }));
        """),
        out("A1=30"),
        diagram("""
            legacy.js（真实实现，运行时存在）
                    │
                    ├─ loadOrder(id) { ... }
                    └─ now() { ... }

            legacy.d.ts（类型说明，编译时存在）
                    │
                    ├─ declare function now(): string;
                    └─ declare function loadOrder(id: string): LegacyOrder | null;

            两份文件配对使用，运行时只加载前者。
        """),
        tip("自己写声明文件时，先写 declare module，再在模块里列函数和 interface。不要试图一次写全，用到什么补什么，声明文件是渐进增长的。"),
        warn("本应用的转译器会整行删除 declare 语句，但不会真正读取 .d.ts 提供类型。所以声明文件在本应用里是纯讲解内容，运行代码不能依赖声明文件里的函数。"),
        quiz("声明文件里为什么不能写函数体？", [
            "因为语法不允许，.d.ts 只描述类型",
            "因为函数体会被压缩",
            "因为运行时不需要函数",
            "因为 declare 关键字会执行函数",
        ], 0, "声明文件只承载类型信息，不能包含实现；写函数体是语法错误，实现应该放在对应的 .js 或 .ts 文件里。"),
        practice("识别声明语句", """
            declare function ping(): string;

            console.log('declaration only');
        """, "declaration only", "declare 行被删除，只剩日志。"),
    ], exercise(
        "为一个老模块写类型说明",
        "不用写声明文件本身，而是模拟它的效果：定义 LegacyUser 接口，实现 readUser(raw)：接收 JSON 字符串，解析后断言成 LegacyUser；实现 userName(raw)：调用 readUser 并返回 name，解析失败时返回 'unknown'。",
        """
        interface LegacyUser {
          id: number;
          name: string;
        }

        function readUser(raw: string): LegacyUser {
          // JSON.parse 后 as LegacyUser
          return { id: 0, name: '' };
        }

        function userName(raw: string): string {
          // 解析失败返回 unknown
          return '';
        }
        """,
        "readUser 直接返回 `JSON.parse(raw) as LegacyUser`；userName 用 try/catch 包住 readUser，catch 里返回 'unknown'。",
        [
            "assert(readUser('{\"id\":1,\"name\":\"V\"}').name === 'V', 'readUser 应解析出 name')",
            "assert(readUser('{\"id\":2,\"name\":\"J\"}').id === 2, 'readUser 应解析出 id')",
            "assert(userName('{\"id\":1,\"name\":\"V\"}') === 'V', 'userName 应返回 name')",
            "assert(userName('not json') === 'unknown', '解析失败应返回 unknown')",
        ],
        """
        interface LegacyUser {
          id: number;
          name: string;
        }

        function readUser(raw: string): LegacyUser {
          return JSON.parse(raw) as LegacyUser;
        }

        function userName(raw: string): string {
          try {
            return readUser(raw).name;
          } catch (e) {
            return 'unknown';
          }
        }
        """,
        110,
    )),

    lesson("ts28", 627, 63, C3, "tsconfig 与编译流程", "从源码到可执行 JS", 100, [
        h("编译流程的四个阶段"),
        p("TypeScript 的编译分四步：解析源码生成语法树、做类型检查、转换（含类型擦除与语法降级）、输出 JavaScript。tsc 读取 tsconfig.json 决定输入哪些文件、输出到哪个目录、目标 JavaScript 版本是什么、开启哪些检查。理解这条流水线，你就能解释「为什么类型错误不一定阻止输出」——tsc 默认即使报类型错误也会生成 JS，除非显式开启 noEmitOnError。"),
        p("tsconfig 里最重要的几项：target 决定输出的 JS 版本，ES5 会降级箭头函数和 let；module 决定模块格式，commonjs 或 es2015；strict 打开一整套严格检查，包括 noImplicitAny、strictNullChecks；outDir 指定输出目录；include 和 exclude 控制参与编译的文件。新手最容易犯的错是把 target 设得太高，结果老环境跑不起来。"),
        p("本应用的运行时相当于 target 为 ES5 的一个极简编译器：只做类型擦除和 enum 转换，不做语法降级，也不做类型检查。所以课程代码必须自己写成 ES5 风格：用 var、用 function、不用 class、不用展开运算符、不用 async/await、不用可选链和空值合并。这不是 TypeScript 的限制，而是这个教学运行时的限制；理解差异，你才能把代码迁移到真正的 tsc 项目里。"),
        p("编译流程里还有一个常被忽略的环节：模块解析。import 的路径怎么找、node_modules 里的包如何定位、types 字段指向哪个声明文件，都由模块解析策略决定。写业务代码时感知不强，但排查「找不到模块」或「类型不匹配」时，理解解析顺序能节省大量时间。monorepo 里的路径别名也在这里配置。"),
        p("最后是构建工具的分工。tsc 负责类型检查和类型擦除，打包工具（Vite、webpack、esbuild）负责模块打包和体积优化。现代项目常用 esbuild 或 swc 做快速转译，再单独跑一次 tsc --noEmit 做类型检查，兼顾速度和正确性。知道这条流水线，你就不会困惑「为什么打包成功了但类型还是错的」——因为打包工具通常只擦类型，不检查类型。"),
        p("声明文件里还可以用 `export =` 和 `export default` 描述不同的模块导出形式，用 `declare global` 扩展全局类型。这些语法本应用都不支持，课程只讲最常见的 declare function、declare var 和 declare module。真正写库时，建议先用 tsc 的 --declaration 自动生成，再手工补注释，比从零手写快得多。"),
        p("编译目标还会影响代码体积和运行速度。target 越低，降级代码越多，体积越大；target 越高，越依赖运行环境支持新语法。选择标准不是「越新越好」，而是「你的用户环境支持到哪一版」。TypeScript 官方建议至少 ES2015，但如果要兼容老浏览器或嵌入式引擎，ES5 仍是安全选择——本应用就是 ES5 的一个例子。"),
        p("编译配置没有「最佳实践」，只有「匹配你的运行环境」。target 取决于用户浏览器或引擎的版本，module 取决于打包工具，strict 取决于团队对类型质量的投入意愿。新手常做的是复制别人的配置，结果要么版本太新跑不起来，要么检查太松形同虚设。正确做法是先确定运行环境，再倒推 target；先确定打包工具，再决定 module；strict 则建议新项目一开始就全开，老项目逐步收紧。"),
        p("最后补充一个常见配置陷阱：include 和 exclude 的匹配规则基于 glob，写错一个星号就可能把 node_modules 或测试文件卷进编译。排查方法是运行 tsc --showConfig，看最终生效的配置和文件列表，比盯着 json 猜要快得多。配置问题几乎都能用「打印最终配置」解决，这个习惯值得养成。"),
        code("""
            interface BuildStep {
              name: string;
              ok: boolean;
            }

            function runPipeline(steps: BuildStep[]): string {
              var out: string[] = [];
              for (var i = 0; i < steps.length; i++) {
                if (steps[i].ok) {
                  out.push(steps[i].name);
                }
              }
              return out.join('>');
            }

            console.log(runPipeline([
              { name: 'parse', ok: true },
              { name: 'check', ok: true },
              { name: 'emit', ok: true }
            ]));
        """),
        out("parse>check>emit"),
        table(["配置项", "作用", "本应用对应"], [
            ["target", "输出 JS 版本", "相当于 ES5"],
            ["strict", "打开严格类型检查", "不做类型检查"],
            ["outDir", "输出目录", "无输出文件，内存中执行"],
            ["module", "模块格式", "不支持 import/export"],
        ]),
        tip("排查编译问题时按流水线顺序走：先确认文件被 include、再确认语法能解析、再看类型错误、最后看输出目标版本。跳过前面直接怀疑类型，往往白费时间。"),
        warn("本应用不支持 import 和 export 语句，课程里所有代码都是单文件、全局作用域。真正的 TypeScript 项目里模块是常态，迁移时要把每段代码包进模块并显式导出。"),
        quiz("tsc 默认在类型检查报错时会怎样？", [
            "立即停止，不生成任何文件",
            "仍然生成 JS，只是报出错误",
            "自动修复类型错误",
            "删除源文件",
        ], 1, "默认情况下 tsc 会继续输出 JS，类型错误只是报告；需要阻止输出要开启 noEmitOnError。这也是为什么有些项目「编译有警告但照样发布」。"),
        practice("模拟流水线", """
            interface Step {
              name: string;
              ok: boolean;
            }

            function failed(steps: Step[]): string {
              var out: string[] = [];
              for (var i = 0; i < steps.length; i++) {
                if (!steps[i].ok) { out.push(steps[i].name); }
              }
              return out.join(',');
            }

            console.log(failed([{name:'parse', ok:true}, {name:'check', ok:false}]));
        """, "check", "只收集失败的阶段。"),
    ], exercise(
        "编译流水线报告",
        "实现 pipelineReport(steps)：接收阶段数组（每项有 name 和 ok），返回 'ok=成功数,failed=失败数,first=第一个失败阶段名'，全部成功时 first 为 'none'。",
        """
        interface Step {
          name: string;
          ok: boolean;
        }

        function pipelineReport(steps: Step[]): string {
          // 统计成功与失败，记录第一个失败阶段
          return '';
        }
        """,
        "用两个计数器加一个 first 变量；循环里根据 ok 累加，first 只在第一次失败时赋值。",
        [
            "assert(pipelineReport([{name:'parse',ok:true},{name:'check',ok:true}]) === 'ok=2,failed=0,first=none', '全部成功时 first 应为 none')",
            "assert(pipelineReport([{name:'parse',ok:true},{name:'check',ok:false}]) === 'ok=1,failed=1,first=check', '应记录第一个失败阶段')",
            "assert(pipelineReport([{name:'a',ok:false},{name:'b',ok:false}]) === 'ok=0,failed=2,first=a', '多个失败时 first 取第一个')",
            "assert(pipelineReport([]) === 'ok=0,failed=0,first=none', '空数组应返回全零')",
        ],
        """
        interface Step {
          name: string;
          ok: boolean;
        }

        function pipelineReport(steps: Step[]): string {
          var okCount: number = 0;
          var failCount: number = 0;
          var first: string = 'none';
          for (var i = 0; i < steps.length; i++) {
            if (steps[i].ok) {
              okCount += 1;
            } else {
              failCount += 1;
              if (first === 'none') {
                first = steps[i].name;
              }
            }
          }
          return 'ok=' + okCount + ',failed=' + failCount + ',first=' + first;
        }
        """,
        120,
    )),

    lesson("ts29", 628, 63, C3, "类型安全的数据管道", "从原始输入到可信数据", 110, [
        h("让每一段都有明确类型"),
        p("数据管道指一串处理步骤：读取原始输入、解析、校验、转换、汇总、输出。没有类型时，每一步的输入输出都靠约定，出错很难定位。加类型后，每一步都有明确的参数和返回值，管道就像流水线，上一道的输出必须符合下一道的输入，不符合时 tsc 会在连接处报错。本讲用一个小型订单统计管道串起前面学过的所有知识。"),
        p("第一步是「边界收窄」。原始数据来自外部，类型必须是 unknown 或 any，先用守卫函数判断结构，通过后才进入类型系统。第二步是「规范化」：把可选字段补上默认值、把字符串数字转成数字、把缺失的 ID 生成出来。规范化的输出是一个字段完整的 interface，后续步骤不再需要判空，代码会短很多。"),
        p("第三步是「业务转换」。订单列表转换成按用户分组的统计、按金额排序的排行榜、按状态分类的计数，每一步都用具体的 interface 描述输入输出。第四步是「汇总输出」：把结果拼成字符串或对象返回。整个过程中，类型扮演的是连接件的角色，它不执行任何逻辑，但保证每一步的输出都能被下一步正确接收。"),
        p("写管道时有两个实践要点。第一，每一步都写成纯函数，输入决定输出、不修改参数，这样每一步都能单独测试，出问题时可以逐段验证。第二，中间结果的类型要显式命名，不要一路用内联对象。命名让管道图变得清晰，也让每一步的职责边界明确。本应用的练习会把管道拆成三到四个函数，分别验证。"),
        p("最后要接受一个现实：类型不能保证业务正确。它只能保证「形状对」，无法保证「金额算得对」「排序规则符合预期」「边界条件处理正确」。所以管道必须配测试，尤其是空数组、缺失字段、零值这些边界。类型让错误更早暴露，测试让错误更少发生，两者缺一不可。"),
        p("管道里的错误处理容易被忽略。解析可能失败、字段可能缺失、除以零可能得到 Infinity，这些都不是类型能拦住的。稳妥的做法是在边界处 try/catch，把异常转换成明确的失败结果，再让上层决定是跳过、重试还是报错。类型安全解决「形状对」，错误处理解决「流程稳」，两件事都要做。"),
        p("数据管道的每一步都应该是「可单独运行」的。这意味着函数不依赖外部变量、不读写全局状态、不产生随机结果。做到这一点，你就能给每一步写独立的测试，出问题时也能把中间结果打印出来逐段比对。管道调试最怕的是「一大坨逻辑」：输入进去，输出不对，却不知道是哪一步错了。拆成小函数后，错误位置会自己浮现。这也是类型之外，管道设计最重要的工程价值。"),
        p("管道的输出格式也应该被类型化。返回值是一串拼接字符串时，调用方无法可靠解析；返回结构化对象时，展示层可以自由决定怎么渲染。把「数据」和「展示」分开，是管道设计的最后一步。本讲的 report 函数返回字符串是为了演示方便，真实项目里更常见的是返回 Summary 对象，再由 UI 层格式化。"),
        code("""
            interface RawOrder {
              id: string;
              total: number;
              user: string;
            }

            interface Totals {
              total: number;
              count: number;
            }

            function parseOrders(raw: string): RawOrder[] {
              var list: RawOrder[] = JSON.parse(raw) as RawOrder[];
              return list;
            }

            function totalOf(orders: RawOrder[]): Totals {
              var sum: number = 0;
              for (var i = 0; i < orders.length; i++) {
                sum += orders[i].total;
              }
              return { total: (sum), count: (orders.length) };
            }

            function report(raw: string): string {
              var t: Totals = totalOf(parseOrders(raw));
              return 'count=' + t.count + ',total=' + t.total;
            }

            console.log(report('[{"id":"A","total":10,"user":"u1"},{"id":"B","total":5,"user":"u1"}]'));
        """),
        out("count=2,total=15"),
        diagram("""
            raw: string
               │ parseOrders
               ▼
            RawOrder[]
               │ totalOf
               ▼
            Totals { total, count }
               │ report
               ▼
            string

            每一段的输出类型 = 下一段的输入类型。
        """),
        tip("管道里的函数命名用「动词 + 名词」：parseOrders、totalOf、groupByUser、topByTotal。名字直接说明了输入和输出，串起来读就是数据流。"),
        warn("JSON.parse 的结果必须断言或用守卫校验。直接把它当 RawOrder[] 用，字段缺失时会得到 undefined，并在很远的地方引发错误。生产代码应先校验再断言。"),
        quiz("数据管道中「边界收窄」的目的是什么？", [
            "提升运行速度",
            "把未知类型的外部数据变成可信的具体类型",
            "减少代码行数",
            "自动修复数据错误",
        ], 1, "边界收窄在数据进入类型系统前做校验，确保后续步骤面对的是结构可信的数据。"),
        practice("两步管道", """
            interface Row {
              n: number;
            }

            function sumRows(rows: Row[]): number {
              var s: number = 0;
              for (var i = 0; i < rows.length; i++) { s += rows[i].n; }
              return s;
            }

            function pipeline(raw: string): number {
              var rows: Row[] = JSON.parse(raw) as Row[];
              return sumRows(rows);
            }

            console.log(pipeline('[{"n":1},{"n":2}]'));
        """, "3", "解析后交给求和函数。"),
    ], exercise(
        "从原始 JSON 到排行榜",
        "实现三件事：parseOrders(raw) 把 JSON 断言成 Order[]；totalOf(orders) 返回金额总和；topUser(orders) 返回金额最高的用户名，空数组返回 'none'。",
        """
        interface Order {
          id: string;
          total: number;
          user: string;
        }

        function parseOrders(raw: string): Order[] {
          // JSON.parse 后 as Order[]
          return [];
        }

        function totalOf(orders: Order[]): number {
          // 累加 total
          return 0;
        }

        function topUser(orders: Order[]): string {
          // 金额最高的用户名，空数组返回 none
          return 'none';
        }
        """,
        "topUser 先判空，再用第一个元素初始化 best，从下标 1 开始比较 total。",
        [
            "assert(parseOrders('[{\"id\":\"A\",\"total\":1,\"user\":\"u1\"}]').length === 1, 'parseOrders 应返回数组')",
            "assert(totalOf([{id:'A',total:1,user:'u1'},{id:'B',total:2,user:'u2'}]) === 3, 'totalOf 求和错误')",
            "assert(totalOf([]) === 0, '空数组求和应为 0')",
            "assert(topUser([{id:'A',total:1,user:'u1'},{id:'B',total:9,user:'u2'}]) === 'u2', 'topUser 应返回最高金额用户')",
            "assert(topUser([]) === 'none', '空数组应返回 none')",
        ],
        """
        interface Order {
          id: string;
          total: number;
          user: string;
        }

        function parseOrders(raw: string): Order[] {
          return JSON.parse(raw) as Order[];
        }

        function totalOf(orders: Order[]): number {
          var sum: number = 0;
          for (var i = 0; i < orders.length; i++) {
            sum += orders[i].total;
          }
          return sum;
        }

        function topUser(orders: Order[]): string {
          if (orders.length === 0) {
            return 'none';
          }
          var best: Order = orders[0];
          for (var i = 1; i < orders.length; i++) {
            if (orders[i].total > best.total) {
              best = orders[i];
            }
          }
          return best.user;
        }
        """,
        120,
    )),

    lesson("ts30", 629, 63, C3, "综合项目：类型化订单与排行榜", "把 29 讲连成一条线", 130, [
        h("一个完整的小系统"),
        p("这一讲不再引入新语法，而是把前面的知识组装成一个可运行的小系统：订单从原始 JSON 进入，经过校验、规范化、汇总，最终生成排行榜和统计报告。它覆盖了 interface、type 别名、泛型、工具类型、可辨识联合、类型守卫、数据管道和 ES5 对象建模。做完这一讲，你应该能独立设计一个中等规模的数据处理模块。"),
        p("数据结构分三层。第一层是 RawOrder，字段全部按外部输入声明，可能缺失；第二层是 Order，字段完整、类型确定，由 normalize 从 RawOrder 转换而来；第三层是输出结构 RankRow 和 Summary，只包含展示需要的字段。三层之间用函数连接，每一层都有明确的职责，任何一层出问题都能单独定位。"),
        p("核心逻辑有三块。normalize 负责把原始数据变成可信数据：缺失字段用默认值补齐，数字字符串转成数字，非法记录返回 null 由调用方过滤。rank 负责排序：先复制数组再排序，避免修改原数据，排序规则是金额降序、金额相同按 ID 升序，保证结果稳定。summarize 负责汇总：总单数、总金额、平均金额、最高单。"),
        p("实现时注意几个 TypeScript 细节。第一，排序比较函数要显式标注参数类型，否则擦除后可能留下残渣。第二，数组复制用 slice()，不要用展开运算符。第三，金额计算用整数分，避免浮点误差。第四，所有对外函数都写完整签名，内部临时变量交给推断。第五，用接口而不是内联对象类型描述返回值。这些细节决定了代码能否在本应用里稳定运行。"),
        p("最后是验证思路。除了判题用例，自己可以构造几组数据：正常订单、缺字段订单、金额为 0 的订单、空数组。逐一确认输出符合预期。类型能保证你不会访问不存在的字段，但不能保证业务规则正确，所以边界测试必须自己补。完成这一讲后，建议把整个项目重写一遍，不看答案，只凭记忆——能独立写出来，才算真正掌握。"),
        p("综合项目的验收标准不是「能跑」，而是「能改」。试着给自己提三个需求：新增一种支付方式、按用户分组统计、把金额单位从分改成元。如果每个需求都只需要改一两个函数、加一两个字段，说明结构是健康的；如果每加一个需求都要动遍所有文件，说明抽象层次没找对。类型设计的好坏，最终就体现在「改动成本」上。写完之后做一次这样的演练，比再做十道练习题更有价值。"),
        p("最后给自己留一个扩展练习：给排行榜加分页，每页十条，实现 pageOf(rows, page, size)；再加一个按用户聚合的 groupByUser(orders)，返回每个用户的订单数和总额。这两个需求会逼你把「排序、切片、分组」拆成独立函数，也会让你体会到类型在重构时的价值：改一个签名，所有调用点立刻告诉你哪里需要跟着改。"),
        p("再补充一个结构建议：把「数据」和「视图」分成两个文件。数据文件定义 Order、RawOrder、RankRow 和 normalize、rank、totalOf 这些纯函数；视图文件只负责把结构拼成字符串。这样数据逻辑可以脱离界面单独测试，视图改动也不会影响计算。单文件项目里用注释分区也能达到类似效果，但真正的项目应该用文件边界强制分离。"),
        code("""
            interface RawOrder {
              id: string;
              total: number;
              user: string;
            }

            interface Order {
              id: string;
              total: number;
              user: string;
            }

            interface RankRow {
              user: string;
              total: number;
            }

            function normalize(raw: RawOrder[]): Order[] {
              var out: Order[] = [];
              for (var i = 0; i < raw.length; i++) {
                var r: RawOrder = raw[i];
                if (typeof r.id === 'string' && typeof r.total === 'number') {
                  out.push({ id: (r.id), total: (r.total), user: (r.user) });
                }
              }
              return out;
            }

            function rank(orders: Order[]): RankRow[] {
              var sorted: Order[] = orders.slice();
              sorted.sort(function (a: Order, b: Order): number {
                if (b.total !== a.total) { return b.total - a.total; }
                return a.id < b.id ? -1 : 1;
              });
              var rows: RankRow[] = [];
              for (var i = 0; i < sorted.length; i++) {
                rows.push({ user: (sorted[i].user), total: (sorted[i].total) });
              }
              return rows;
            }

            function summarize(orders: Order[]): string {
              var sum: number = 0;
              var top: number = 0;
              for (var i = 0; i < orders.length; i++) {
                sum += orders[i].total;
                if (orders[i].total > top) { top = orders[i].total; }
              }
              var avg: number = orders.length === 0 ? 0 : Math.round(sum / orders.length);
              return 'n=' + orders.length + ',sum=' + sum + ',avg=' + avg + ',top=' + top;
            }

            var raw: RawOrder[] = [
              { id: 'B', total: 20, user: 'u1' },
              { id: 'A', total: 50, user: 'u2' },
              { id: 'C', total: 20, user: 'u3' }
            ];

            var orders: Order[] = normalize(raw);
            var rows: RankRow[] = rank(orders);

            console.log(rows[0].user, rows[1].user);
            console.log(summarize(orders));
        """),
        out("u2 u1\nn=3,sum=90,avg=30,top=50"),
        table(["模块", "输入", "输出", "职责"], [
            ["normalize", "RawOrder[]", "Order[]", "过滤非法、补齐字段"],
            ["rank", "Order[]", "RankRow[]", "稳定排序、生成榜单"],
            ["summarize", "Order[]", "string", "统计总数/总额/均值/最高"],
        ]),
        tip("综合项目的价值在于暴露知识盲区。写不出来时不要急着看答案，先定位卡在哪一层：是数据结构没想清楚，还是某个语法不会写。前者回到 interface 那几讲，后者查对应章节，比通读一遍有效得多。"),
        warn("排序比较函数必须返回数字，且要处理相等情况，否则不同引擎的排序结果可能不一致。本应用跑在 Rhino 上，排序实现与浏览器可能不同，判题用例都避免依赖不稳定的顺序。"),
        quiz("排行榜排序时为什么要先用 slice() 复制数组？", [
            "为了提升排序速度",
            "避免 sort 修改传入的原数组",
            "因为 slice 会自动排序",
            "为了去重",
        ], 1, "sort 会原地修改数组，复制一份再排序能保持输入不变，这是纯函数的基本要求。"),
        practice("综合项目的小切片", """
            interface Order {
              id: string;
              total: number;
            }

            function sumOf(orders: Order[]): number {
              var s: number = 0;
              for (var i = 0; i < orders.length; i++) { s += orders[i].total; }
              return s;
            }

            console.log(sumOf([{ id: 'A', total: 10 }, { id: 'B', total: 20 }]));
        """, "30", "把每一单的 total 累加。"),
    ], exercise(
        "完整的订单排行榜",
        "实现四个函数：normalize(raw) 过滤掉 id 不是字符串或 total 不是数字的记录；totalOf(orders) 返回总金额；rankOf(orders) 返回按金额降序、金额相同按 id 升序排列的 Order 副本；topUser(orders) 返回排名第一的 user，空数组返回 'none'。",
        """
        interface Order {
          id: string;
          total: number;
          user: string;
        }

        interface RawOrder {
          id: string;
          total: number;
          user: string;
        }

        function normalize(raw: RawOrder[]): Order[] {
          // 过滤非法记录
          return [];
        }

        function totalOf(orders: Order[]): number {
          return 0;
        }

        function rankOf(orders: Order[]): Order[] {
          // 复制后排序：total 降序，相同则 id 升序
          return orders;
        }

        function topUser(orders: Order[]): string {
          // 排名第一的 user，空数组返回 none
          return 'none';
        }
        """,
        "rankOf 用 orders.slice() 复制，比较函数先比 total（b.total - a.total），相等时比 id（a.id < b.id ? -1 : 1）。topUser 判空后取 rankOf(orders)[0].user。",
        [
            "assert(normalize([{id:'A',total:1,user:'u1'},{id:1,total:2,user:'u2'},{id:'C',total:'x',user:'u3'}]).length === 1, 'normalize 应过滤非法记录')",
            "assert(totalOf([{id:'A',total:1,user:'u1'},{id:'B',total:2,user:'u2'}]) === 3, 'totalOf 求和错误')",
            "assert(rankOf([{id:'B',total:5,user:'u1'},{id:'A',total:5,user:'u2'}])[0].id === 'A', '金额相同应按 id 升序')",
            "assert(rankOf([{id:'A',total:1,user:'u1'},{id:'B',total:9,user:'u2'}])[0].id === 'B', '应按金额降序')",
            "assert(topUser([{id:'A',total:1,user:'u1'},{id:'B',total:9,user:'u2'}]) === 'u2', 'topUser 应返回第一名用户')",
        ],
        """
        interface Order {
          id: string;
          total: number;
          user: string;
        }

        interface RawOrder {
          id: string;
          total: number;
          user: string;
        }

        function normalize(raw: RawOrder[]): Order[] {
          var out: Order[] = [];
          for (var i = 0; i < raw.length; i++) {
            var r: RawOrder = raw[i];
            if (typeof r.id === 'string' && typeof r.total === 'number') {
              out.push({ id: (r.id), total: (r.total), user: (r.user) });
            }
          }
          return out;
        }

        function totalOf(orders: Order[]): number {
          var sum: number = 0;
          for (var i = 0; i < orders.length; i++) {
            sum += orders[i].total;
          }
          return sum;
        }

        function rankOf(orders: Order[]): Order[] {
          var sorted: Order[] = orders.slice();
          sorted.sort(function (a: Order, b: Order): number {
            if (b.total !== a.total) {
              return b.total - a.total;
            }
            return a.id < b.id ? -1 : 1;
          });
          return sorted;
        }

        function topUser(orders: Order[]): string {
          if (orders.length === 0) {
            return 'none';
          }
          return rankOf(orders)[0].user;
        }
        """,
        140,
    )),
]


def merge_text_blocks(lesson_obj, groups=3):
    """把多段讲解合并成 3 个 text 块，块数落在课程建议的 10-14 区间。

    合并时按字数尽量均分，段之间保留空行，阅读节奏不受影响。
    """
    blocks = lesson_obj["blocks"]
    positions = [i for i, b in enumerate(blocks) if b["type"] == "text"]
    if len(positions) <= groups:
        return
    texts = [blocks[i]["text"] for i in positions]
    # 按段数均分为三组，组内用空行连接，避免某组过长
    merged = []
    n = len(texts)
    base = n // groups
    extra = n % groups
    start = 0
    for g in range(groups):
        take = base + (1 if g < extra else 0)
        if take == 0:
            continue
        merged.append((chr(10) + chr(10)).join(texts[start:start + take]))
        start += take
    if start < n:
        merged[-1] = merged[-1] + chr(10) + chr(10) + (chr(10) + chr(10)).join(texts[start:])
    first = positions[0]
    new_blocks = []
    for i, b in enumerate(blocks):
        if b["type"] == "text":
            if i == first:
                for m in merged:
                    new_blocks.append({"type": "text", "text": m})
            continue
        new_blocks.append(b)
    lesson_obj["blocks"] = new_blocks


def dump(pack, name):
    path = OUT_DIR / name
    path.write_text(
        json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return path


def main():
    for pack, name in (
        (TS_BASICS, "ts-basics.json"),
        (TS_CORE, "ts-core.json"),
        (TS_ADVANCED, "ts-advanced.json"),
    ):
        for item in pack:
            merge_text_blocks(item)
        path = dump(pack, name)
        print(f"{name}: {len(pack)} lessons, {sum(len(x['exercise']['tests']) for x in pack)} cases -> {path}")


if __name__ == "__main__":
    main()
