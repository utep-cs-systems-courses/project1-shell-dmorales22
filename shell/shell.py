import os 
import sys
import re 

def shell_input():
	u_str = input()
	args = u_str.split(" ")

	for i in range(len(args)):
		if(args[i] == '&'):
			print("background tasks here")

		elif(args[i] == '|'):
			print("pipes go here")

		elif(args[i] == '<'):
			print("redirect go here")

		elif(args[i] == '>'): 
			print("redirect go here too")

		elif(args[i] == 'exit'):
			sys.exit(0)

	exec_u(args)

def exec_u(args):
	for dir in re.split(":", os.environ['PATH']):
		program = "%s/%s" % (dir, args[0])
		try:
			os.execve(program, args, os.environ) # try to exec program
		except FileNotFoundError:             # ...expected
			continue                              # ...fail quietly

	
def main():
	shell_input()

main()