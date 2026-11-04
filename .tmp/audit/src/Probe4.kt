import com.pyneon.academy.c.CInterpreter
import java.util.Locale

fun show(label: String, src: String) {
    val r = CInterpreter.run(src)
    println("### $label -> ok=${r.ok} type=${r.errorType} stdout=[${r.stdout.replace("\n","\n")}] msg=${r.errorMessage}")
}
fun main() {
    Locale.setDefault(Locale.GERMANY)
    show("locale de %.2f", "int main(){ printf(\"%.2f\", 3.5); return 0; }")
    show("locale de %g", "int main(){ printf(\"%g\", 1.5); return 0; }")
    show("locale de default double display", "int main(){ printf(\"%s\", 1.5); return 0; }")
    Locale.setDefault(Locale.US)
    show("width %5d", "int main(){ printf(\"[%5d]\", 42); return 0; }")
    show("zero pad %02d", "int main(){ printf(\"[%02d]\", 7); return 0; }")
    show("sci 1e3", "int main(){ printf(\"%g\", 1e3); return 0; }")
    show("sci 1.5e2", "int main(){ printf(\"%g\", 1.5e2); return 0; }")
    show("hex literal", "int main(){ printf(\"%d\", 0x10); return 0; }")
    show("float default display", "int main(){ double d = 1.23456789; printf(\"%s\", d); return 0; }")
    show("tiny double", "int main(){ double d = 0.0000001; printf(\"%s\", d); return 0; }")
    show("negative hex", "int main(){ printf(\"%x\", -1); return 0; }")
    show("prec on string", "int main(){ printf(\"%.2s\", \"abcdef\"); return 0; }")
}
