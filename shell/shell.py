#Author: David Morales 
#Course: CS 4375 Theory of Operating Systems
#Instructor: Dr. Eric Freudenthal
#T.A: David Pruitt 
#Assignment: Lab 2
#Last Modification: 09/15/2020
#Purpose: Basic shell

import os 
import sys
import re 

def shell_input(u_str): #This method checks out string 
	if '' == u_str or u_str.isspace():
		return

	if 'exit' in u_str:  #If exit is detected, then program quits 
		sys.exit(0)

	if 'cd' in u_str: #Changes directory using input
		try:
			os.chdir(u_str.split()[1])
		except Exception:
			print("cd: no such file or directory: {}".format(args[1]))
		return

	if '|' in u_str: #Detects pipes from the string
		n_args = []
		args = u_str.split('|')
		
		for i in range(len(args)):
			n_args.append(args[i].split())

		pipe_u(n_args)
		return

	if '>' in u_str: #Redirects
		n_args = []
		args = u_str.split('>')

		for i in range(len(args)):
			n_args.append(args[i].split())

		redirect_u_input(n_args)
		return

	#if '<' in u_str: #WIP
	#	n_args = []
	#	args = u_str.split('<')
	#	for i in range(len(args)):
	#		n_args.append(args[i].split())

	#	redirect_u_input(n_args)
	#	return

	if '&' in u_str: #For background processes
		n_args = []
		args = u_str.split('&')
		
		if args[-1] == "": #Runs background process
			args.remove("")
			for i in range(len(args)):
				n_args.append(args[i].split())

			print(n_args)
			for i in range(len(n_args)):
				background_exec_u(n_args[i])

		else: #Runs processes normally
			for i in range(len(args)):
				n_args.append(args[i].split())

			for i in range(len(n_args)):
				exec_u(n_args[i])

		return

	args = u_str.split()
	exec_u(args)

def redirect_u_output(args): #Redirects. 
	path = args[1]
	path_str = path[0]
	program = args[0]
	program_str = program[0]

	pid = os.getpid()               # get and remember pid
	rc = os.fork()

	if rc < 0:
		os.write(2, ("fork failed, returning %d\n" % rc).encode())
		sys.exit(1)

	elif rc == 0:                   # child
		os.close(1)                 # redirect child's stdout
		os.open(path_str, os.O_RDONLY);
		os.set_inheritable(1, True)

		args.pop()

		for dir in re.split(":", os.environ['PATH']): # try each directory in path
			program = "%s/%s" % (dir, program)
			try:
				os.execve(program, args[0], os.environ) # try to exec program
			except FileNotFoundError:             # ...expected
				pass                              # ...fail quietly 

		return

	else:                           # parent (forked ok)
		childPidCode = os.wait()

	sys.exit(-1)

def redirect_u_input(args): #Redirects
	path = args[1]
	path_str = path[0]
	program = args[0]
	program_str = program[0]

	print(path_str)
	pid = os.getpid()               # get and remember pid
	rc = os.fork()

	if rc < 0:
		os.write(2, ("fork failed, returning %d\n" % rc).encode())
		sys.exit(1)

	elif rc == 0:                   # child
		os.close(1)                 # redirect child's stdout
		fdOut = os.open(path_str, os.O_CREAT | os.O_WRONLY)
		os.set_inheritable(1, True)

		args.pop()

		for dir in re.split(":", os.environ['PATH']): # try each directory in path
			program = "%s/%s" % (dir, program_str)
			try:
				os.execve(program, args[0], os.environ) # try to exec program
			except FileNotFoundError:             # ...expected
				pass                              # ...fail quietly 

		return

	else:                           # parent (forked ok)
		childPidCode = os.wait()

	sys.exit(-1)

def pipe_u(args): #Method for pipe instructions
	arg1, arg2 = args[0], args[1]  #Separating commands (only two)
	s_in = os.dup(0) 
	s_out = os.dup(1) 
	fd_in = os.dup(s_in) 

	pipe_r, pipe_w = os.pipe() #Starts pipe
	os.dup2(pipe_w, 1) 

	exec_u(arg1) #Running first command that does wait. 
	os.dup2(pipe_r, 0) 
	os.dup2(s_out, 1) 

	background_exec_u(arg2) #Running second command that doesn't wait.
	os.dup2(s_in, 0) 

	os.close(s_in) #Closes out input and output
	os.close(s_out)
	os.close(pipe_r)
	os.close(pipe_w)
	return

def exec_u(args): #This method execs commands using forks. 
	pid = os.getpid()
	rc = os.fork()

	if(os.path.isfile(args[0])): #For absolute paths only. 
		if rc < 0:
			print("fork failed. Try again.")
			sys.exit(1)
		elif rc == 0:
			try:
				program = args[0]
				os.execve(program, args, os.environ) # try to exec program
			except FileNotFoundError:             # ...expected
				print("")                              # ...fail quietly
		elif rc > 0:
			childPidCode = os.wait()
			return

	for dir in re.split(":", os.environ['PATH']): #when path is not specified 
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
			return

	print(args[0] + " command not found.")
	sys.exit(-1)

def background_exec_u(args): #This method executes commands in background. 
	pid = os.getpid()
	rc = os.fork()
	program = args[0]

	if rc < 0:
		print("fork failed. Try again.")
		sys.exit(1)
	elif rc == 0:
		try:
			os.execve(program, args, os.environ) # try to exec program
			return
		except FileNotFoundError:             # ...expected
			print("")
	elif rc > 0:
		return

	for dir in re.split(":", os.environ['PATH']):
		program = "%s/%s" % (dir, args[0])
		if rc < 0:
			print("fork failed. Try again.")
			sys.exit(-1)
		elif rc == 0:
			try:
				os.execve(program, args, os.environ) # try to exec program
			except FileNotFoundError:             # ...expected
				continue                              # ...fail quietly
		elif rc > 0: #Does not wait for other command to finish. 
			return

	print(args[0] + " command not found.")
	sys.exit(-1)

def main():
	while(1): #Everything is ran in loop
		u_str = input()
		args = u_str.splitlines()

		for i in range(len(args)): #For inputs that are multiple lines. 
			shell_input(str(args[i]))


main()