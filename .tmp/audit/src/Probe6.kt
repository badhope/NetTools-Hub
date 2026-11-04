import com.pyneon.academy.c.CInterpreter
import com.pyneon.academy.ts.TypeScriptTranspiler

fun main() {
    // C string equality -> false pass
    val src = """int f() { return "WRONG"; }"""
    val tests = listOf("""int main() { assert(f() == "EXPECTED", "f() 应返回 EXPECTED"); return 0; }""")
    val r = CInterpreter.check(src, tests)
    println("C string-eq wrong solution: ok=${r.ok} passed=${r.ok} msg=${r.errorMessage}")

    val src2 = """int f() { return 42; }"""
    val tests2 = listOf("""int main() { assert(f() == 0, "should fail"); return 0; }""")
    println("C numeric wrong solution: ok=${CInterpreter.check(src2, tests2).ok}")

    // TS object literal with identifier value in call
    val ts = "var name = 'V';\nconsole.log({name: name, level: 66});"
    println("TS: " + TypeScriptTranspiler.transpile(ts).code.replace("\n","\n"))
    val ts2 = "function f(o) { return o.name; }\nvar name = 'V';\nconsole.log(f({name: name}));"
    println("TS2: " + TypeScriptTranspiler.transpile(ts2).code.replace("\n","\n"))
    // TS string corruption
    println("TS3: " + TypeScriptTranspiler.transpile("console.log(\"public static void main\");").code)
    println("TS4: " + TypeScriptTranspiler.transpile("var s = \"this as number is text\";").code)
}
