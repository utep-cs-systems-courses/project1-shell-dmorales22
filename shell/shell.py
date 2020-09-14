import os 
import sys
import re 

def shell_input():
	args = user_input()

	for i in range(len(args)):
		if(args[i] == '&'):
			background_u(args)
			return

		elif(args[i] == '|'):
			pipe_u(args)
			return

		elif(args[i] == '<'):
			print("redirect go here")

		elif(args[i] == '>'): 
			print("redirect go here too")

		elif(args[i] == 'exit'):
			sys.exit(1)

	exec_u(args)

def pipe_u(args):
	pid = os.getpid()               # get and remember pid
	pr, pw = os.pipe()

	for f in (pr, pw):
		os.set_inheritable(f, True)

	import fileinput

	rc = os.fork()

	if rc < 0:
		sys.exit(1)

	elif rc == 0:                   #  child - will write to pipe
		os.close(1)                 # redirect child's stdout
		os.dup(pw)
		for fd in (pr, pw):
			os.close(fd)

	else:                           # parent (forked ok)
		os.close(0)
		os.dup(pr)
		for fd in (pw, pr):
			os.close(fd)

		for line in fileinput.input():
			print("From child: <%s>" % line)
	
	shell_input()

def background_u(args):
	rc = os.fork()

	for dir in re.split(":", os.environ['PATH']):
		program = "%s/%s" % (dir, args[0])
		if rc == 0:
			try:
				os.execve(program, args, os.environ) # try to exec program
			except FileNotFoundError:             # ...expected
				continue                              # ...fail quietly
		else:
			shell_input()
			return

def exec_u(args):
	pid = os.getpid()
	rc = os.fork()

	for dir in re.split(":", os.environ['PATH']):
		program = "%s/%s" % (dir, args[0])
		if rc < 0:
			print("fork failed. Try again.")
			sys.exit(1)
		elif rc == 0:
			try:
				os.execve(program, args, os.environ) # try to exec program
			except FileNotFoundError:             # ...expected
				continue                              # ...fail quietly
		elif rc > 0:
			childPidCode = os.wait()
			shell_input()
			return

	print(args[0] + " not found")

def user_input():
	u_str = input()
	args = u_str.split(" ")
	return args

def main():
	shell_input()

main()