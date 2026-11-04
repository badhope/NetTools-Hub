import com.pyneon.academy.c.CInterpreter

fun main() {
    val t0 = System.currentTimeMillis()
    val r = CInterpreter.run("""int main(){ int i; for(i=0;i<1000000;i++) printf("0123456789012345678901234567890123456789012345678901234567890123456789"); return 0; }""")
    println("1M prints: ok=${r.ok} len=${r.stdout.length} ms=${System.currentTimeMillis()-t0} err=${r.errorType}/${r.errorMessage}")
    val r2 = CInterpreter.check("int f(){ return 1; }", listOf("""int main(){ assert("abc" == "def", "should fail if strings distinct"); return 0; }"""))
    println("string assert wrong solution: ok=${r2.ok} msg=${r2.errorMessage}")
    val r3 = CInterpreter.check("int f(){ return 2; }", listOf("""int main(){ assert(f() == 2, "ok"); return 0; }"""))
    println("correct: ok=${r3.ok}")
    val r4 = CInterpreter.check("int f(){ return 1; }", listOf("""int main(){ char *s = "V"; assert(s == "V", "x"); return 0; }"""))
    println("string compare bypass: ok=${r4.ok} msg=${r4.errorMessage}")
    val r5 = CInterpreter.run("""int main(){ int a[20000000]; a[19999999]=1; return 0; }""")
    println("20M array: ok=${r5.ok} type=${r5.errorType} msg=${r5.errorMessage}")
}
