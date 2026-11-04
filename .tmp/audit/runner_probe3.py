import sys, time, io
sys.path.insert(0, r"D:\workspaspace2\06\mashang\app\src\main\python")
import runner
LOG = open(r"D:\workspaspace2\06\mashang\.tmp\audit\probe3.log", "w", encoding="utf-8")
def log(*a):
    LOG.write(" ".join(str(x) for x in a) + "\n"); LOG.flush()

runner.EXEC_LOCK.acquire()
# run1: blocking sleep -> watchdog cannot interrupt -> join times out
r1 = runner._run_protected("import time\ntime.sleep(1.2)\nprint('ZOMBIE')\n", {"__name__":"__main__"}, [], 0.2)
log("r1 error=", r1["error"]["type"] if r1["error"] else None, "alive=", r1["worker_still_alive"])
# run2 starts immediately, sleeps past the zombie's wake time, then prints
r2 = runner._run_protected("import time\ntime.sleep(1.6)\nprint('SECOND-OUTPUT')\n", {"__name__":"__main__"}, [], 5.0)
log("r2 stdout=", repr(r2["stdout"]), "r2 stderr=", repr(r2["stderr"]), "r2 err=", r2["error"])
log("r2 captured SECOND-OUTPUT? ", "SECOND-OUTPUT" in r2["stdout"])
time.sleep(0.5)
LOG.close()
