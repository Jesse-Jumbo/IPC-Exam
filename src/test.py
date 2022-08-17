import os
import subprocess
import sys
import time


if os.path.isfile("../results/test.jpeg"):
    os.remove("../results/test.jpeg")

""" compile consumer test  """
s = os.system("make")
assert s == 0

""" open judge  """
# p_judg = subprocess.Popen(["./System/test_judge"])
p_judg = subprocess.Popen(["python3", "test_judge.py"])
p_cons = subprocess.Popen(["./Consumer"])
p_coll = subprocess.Popen(["python3.8", "ResultCollector.py"])
p_prod = subprocess.Popen(["python3.8", "Producer.py"])

s_time = time.process_time()
while p_coll.poll() == None:
    if time.process_time() - s_time > 30:
        print("[System] system build failed. (timeout)")
        sys.exit(1)

p_judg.kill()
p_cons.kill()
p_coll.kill()
p_prod.kill()

""" system check  """
if p_judg.returncode or p_cons.returncode or p_coll.returncode or p_prod.returncode:
    print("[System] System establish failed. see the output message(s) for the error(s).")
    sys.exit(1)
elif os.path.isfile("../results/test.jpeg"):
    print("[System] Congratulation! System establish successfully !!")
    sys.exit(0)
