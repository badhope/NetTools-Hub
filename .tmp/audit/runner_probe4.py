import sys, time
sys.path.insert(0, r"D:\workspaspace2\06\mashang\app\src\main\python")
import runner
LOG = open(r"D:\workspaspace2\06\mashang\.tmp\audit\probe4.log", "w", encoding="utf-8")
def log(*a):
    LOG.write(" ".join(str(x) for x in a) + "\n"); LOG.flush()

r1 = runner._run_protected("import time\ntime.sleep(3.0)\nprint('ZOMBIE')\n", {"__name__":"__main__"}, [], 0.2)
log("r1 err=", r1["error"]["type"] if r1["error"] else None, "alive=", r1["worker_still_alive"])
r2 = runner._run_protected("import time\ntime.sleep(2.0)\nprint('SECOND-OUTPUT')\n", {"__name__":"__main__"}, [], 6.0)
log("r2 ok, stdout=", repr(r2["stdout"]), "err=", r2["error"], "alive=", r2["worker_still_alive"])
log("r2 captured its print? ", "SECOND-OUTPUT" in r2["stdout"])
time.sleep(1.0)
LOG.close()
