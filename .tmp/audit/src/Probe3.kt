import com.pyneon.academy.c.CInterpreter

fun main() {
    // multi-line function definition in the C REPL
    val s = CInterpreter.Session()
    println("1) " + s.push("int add(int a, int b) {"))
    println("2) " + s.push("  return a + b;"))
    println("3) " + s.push("}"))
    println("4) " + s.push("printf(\"%d\", add(2,3));"))
    println("vars=" + s.variables())

    val s2 = CInterpreter.Session()
    println("A) " + s2.push("int x = 1;"))
    println("B) " + s2.push("if (x > 0) {"))
    println("C) " + s2.push("printf(\"pos\");"))
    println("D) " + s2.push("}"))

    val s3 = CInterpreter.Session()
    println("E) " + s3.push("printf(\"%d\", 1);"))
    println("F) " + s3.push("printf(\"%d\", 2);"))

    // string equality semantics
    val r = CInterpreter.run("""int main(){ printf("%d %d", "abc"=="def", "5"=="05"); return 0; }""")
    println("strEq ok=${r.ok} out=${r.stdout} msg=${r.errorMessage}")

    // output flooding
    val t0 = System.currentTimeMillis()
    val r2 = CInterpreter.run("""int main(){ int i; for(i=0;i<200000;i++) printf("0123456789012345678901234567890123456789012345678901234567890123456789"); return 0; }""")
    println("flood ok=${r2.ok} len=${r2.stdout.length} ms=${System.currentTimeMillis()-t0} msg=${r2.errorMessage}")
}
