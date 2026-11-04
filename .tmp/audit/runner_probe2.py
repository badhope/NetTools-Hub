import sys, time
sys.path.insert(0, r"D:\workspaspace2\06\mashang\app\src\main\python")
import runner
LOG = open(r"D:\workspaspace2\06\mashang\.tmp\audit\probe2.log", "w", encoding="utf-8")
def log(*a):
    LOG.write(" ".join(str(x) for x in a) + "\n"); LOG.flush()

code1 = "import time\ntime.sleep(2.0)\nprint('LATE')\n"
res1 = runner._run_protected(code1, {"__name__":"__main__"}, [], 0.3)
log("run1 err=", res1["error"]["type"] if res1["error"] else None, "alive=", res1["worker_still_alive"])

res2 = runner._run_protected("print('SECOND')\n", {"__name__":"__main__"}, [], 3.0)
log("run2 stdout=", repr(res2["stdout"]), "err=", res2["error"])
log("sys.stdout is original?", type(sys.stdout).__name__, getattr(sys.stdout, "name", "<StringIO>"))
log("is sys.stdout same as run1 buffer? ", )

time.sleep(2.2)
res3 = runner._run_protected("print('THIRD')\n", {"__name__":"__main__"}, [], 3.0)
log("run3 stdout=", repr(res3["stdout"]), "err=", res3["error"])
log("after all, sys.stdout type=", type(sys.stdout).__name__)
LOG.close()
