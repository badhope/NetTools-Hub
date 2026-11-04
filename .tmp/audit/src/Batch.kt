import com.pyneon.academy.c.CInterpreter
import java.io.File

fun main(args: Array<String>) {
    val text = File(args[0]).readText()
    val snippets = text.split("<<<SNIP>>>").map { it.trim('\r','\n',' ') }.filter { it.isNotEmpty() }
    val meta = File(args[1]).readLines()
    snippets.forEachIndexed { i, s ->
        val r = CInterpreter.run(s)
        println("@@@ $i [${meta.getOrElse(i){"?"}}] ok=${r.ok} type=${r.errorType} msg=${r.errorMessage}")
        println("OUT: " + r.stdout.replace("\n", "\n"))
    }
}
