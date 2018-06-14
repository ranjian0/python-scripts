import sys
import time

def progress_bar(current, total, bar_width=50, units=''):
	done = int(bar_width * (current/total))
	sys.stdout.write("\r[%s%s] %s/%s %s" % ('=' * done, ' ' * (bar_width-done), current, total, units))
	sys.stdout.flush()
	if current == total:
		sys.stdout.write('\n')

if __name__ == '__main__':
	# -- test
	for i in range(100):
		time.sleep(0.1)
		progress_bar(i+1, 100, units='')
