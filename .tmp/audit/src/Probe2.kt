import com.pyneon.academy.c.CInterpreter

fun show(label: String, src: String) {
    val r = CInterpreter.run(src)
    println("### $label -> ok=${r.ok} type=${r.errorType} stdout=[${r.stdout.replace("\n","\n")}] msg=${r.errorMessage}")
}
fun main() {
    show("dynamic scoping", "int f() { return n; } int main() { int n = 5; printf(\"%d\", f()); return 0; }")
    show("block scope", "int main(){ int n=1; { int m=2; printf(\"%d%d\", n, m); } return 0; }")
    show("shadow", "int main(){ int n=1; { int n=2; printf(\"%d\", n); } printf(\"%d\", n); return 0; }")
    show("array oom", "int main(){ int a[10000000]; a[9999999]=1; return 0; }")
    show("array size zero", "int main(){ int a[0]; return 0; }")
    show("div assign", "int main(){ int x=10; x /= 2; printf(\"%d\", x); return 0; }")
    show("mod assign", "int main(){ int x=10; x %= 3; printf(\"%d\", x); return 0; }")
    show("string brace", "int main(){ printf(\"{\"); return 0; }")
    show("string comment", "int main(){ printf(\"/* hi */\"); return 0; }")
    show("reject struct in string", "int main(){ printf(\"struct\"); return 0; }")
    show("if decl", "int main(){ if (1) int x = 3; return 0; }")
    show("return in main", "int main(){ return 42; }")
    show("void func", "void hi(){ printf(\"hi\"); } int main(){ hi(); return 0; }")
    show("func without return", "int f(){ } int main(){ printf(\"%d\", f()); return 0; }")
    show("char comparison", "int main(){ char c='A'; printf(\"%d\", c=='A'); return 0; }")
    show("string var", "int main(){ char s[] = \"hi\"; printf(\"%s\", s); return 0; }")
    show("char array", "int main(){ char s[3]; s[0]='h'; s[1]='i'; s[2]=0; printf(\"%s\", s); return 0; }")
    val s = CInterpreter.Session()
    println("session brace string: " + s.push("printf(\"{\");"))
    println("session brace string second: " + s.push("printf(\"x\");"))
}
