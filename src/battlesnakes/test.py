import time
start_time = time.time()
time.sleep(1)
end_time = time.time()
log_time_diff = end_time - start_time
log_time_diff = f"time: {log_time_diff:.3f}s"
print(log_time_diff)