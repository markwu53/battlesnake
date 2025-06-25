import time

now = time.localtime()

if not 6 <= now.tm_hour < 20:
    print("not")
else:
    print("yes")