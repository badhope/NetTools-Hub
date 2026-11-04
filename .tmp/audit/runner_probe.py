import sys, os, time, threading, json
sys.path.insert(0, r"D:\workspaspace2\06\mashang\app\src\main\python")
import runner

# 1) runaway print: how much does the capture buffer hold before truncation?
t0 = time.time()
r = runner._run_protected("while True:\n    print('x'*1000)\n", {"__name__":"__main__"}, [], 0.5)
print("timeout-run sec=%.2f stdout_len=%d err=%s" % (time.time()-t0, len(r["stdout"]), r["error"]["type"] if r["error"] else None))

# 2) zombie C-call thread clobbers sys.stdout for the next run
print("--- zombie test ---")
code1 = "import time\ntime.sleep(2.0)\nprint('LATE')\n"
res1 = runner._run_protected(code1, {"__name__":"__main__"}, [], 0.3)
print("run1 err=%s alive=%s" % (res1["error"]["type"] if res1["error"] else None, res1["worker_still_alive"]))
# immediately run a second snippet; zombie wakes during it
res2 = runner._run_protected("import time\ntime.sleep(1.0)\nprint('SECOND')\n", {"__name__":"__main__"}, [], 3.0)
print("run2 stdout=%r err=%s" % (res2["stdout"], res2["error"]))
time.sleep(1.5)
