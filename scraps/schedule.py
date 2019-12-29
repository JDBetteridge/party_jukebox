import sched
import time
import threading

s = sched.scheduler(time.time, time.sleep)
timer = threading.Timer

def print_time(a='default'):
    print("From print_time", time.time(), a)

def print_some_times():
    print(time.time())
    s.enter(10, 1, print_time)
    s.enter(5, 2, print_time, argument=('positional',))
    s.enter(5, 1, print_time, kwargs={'a': 'keyword'})
    s.run()
    print(time.time())

def thread_print_some_times():
    print(time.time())
    timer(10, print_time).start()
    timer(5, print_time, args=('positional',)).start()
    timer(5, print_time, kwargs={'a': 'keyword'}).start()
    print(time.time())

# ~ print_some_times()

thread_print_some_times()
print('blocking?')
# ~ while True:
    # ~ pass
