import com.pyneon.academy.ts.TypeScriptTranspiler

fun t(label: String, src: String) {
    val r = TypeScriptTranspiler.transpile(src)
    println("### $label\nIN : " + src.replace("\n","\n") + "\nOUT: " + r.code.replace("\n","\n"))
}
fun main() {
    t("ts02 test 1", "assert(intro({name:'V', level:66}) === 'V(66)', 'intro 应返回 V(66)')")
    t("ts02 test 2", "assert(intro({name:'Judy', level:30}) === 'Judy(30)', '应支持不同英雄')")
    t("console.log obj arg", "console.log({a: 1, b: 2});")
    t("fn call obj arg", "f({a: 1});")
    t("nested obj", "f({a: {b: 1}});")
    t("obj arg multiline", "assert(intro({\n  name: 'V',\n  level: 66\n}) === 'V(66)', 'x')")
    t("array of objects", "var xs: Hero[] = [{name:'V', level:1}];")
    t("object spread", "var x = {...y, a: 1};")
    t("return obj literal", "function f() { return {a: 1}; }")
    t("obj in if condition", "if (f({a:1})) {}")
    t("method call obj arg", "obj.method({a: 1});")
}
