import com.pyneon.academy.ts.TypeScriptTranspiler
import java.io.File

fun main(args: Array<String>) {
    val text = File(args[0]).readText()
    val parts = text.split("<<<SNIP>>>")
    val meta = File(args[1]).readLines()
    parts.forEachIndexed { i, raw ->
        val src = raw.trim('\r','\n')
        if (src.isEmpty()) return@forEachIndexed
        val out = TypeScriptTranspiler.transpile(src).code
        if (out != src) {
            println("### ${meta.getOrElse(i){"?"}}")
            println("IN : " + src.replace("\n","\n"))
            println("OUT: " + out.replace("\n","\n"))
        }
    }
}
