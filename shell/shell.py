import os 
import sys
import re 

def shell_input(u_str):
	if '' == u_str or u_str.isspace():
		return

	if 'exit' in u_str:
		sys.exit(0)

	if 'cd' in u_str:
		try:
			os.chdir(u_str.split()[1])
		except Exception:
			print("cd: no such file or directory: {}".format(args[1]))
		return

	if '|' in u_str:
		n_args = []
		args = u_str.split('|')
		
		for i in range(len(args)):
			n_args.append(args[i].split())

		print(n_args)
		#pipe_u(n_args)
		return

	if '>' in u_str:
		args = u_str.split('>')
		for i in range(len(args)):
			args[i] = args[i].strip()

		redirect_u_input(args)
		return

	#if '<' in u_str:
		#args = u_str.split('<')
		#for i in range(len(args)):
			#args[i] = args[i].strip()

		#redirect_u_output(args)
		#return

	if '&' in u_str:
		n_args = []
		args = u_str.split('&')
		
		if args[-1] == "":
			args.remove("")
			for i in range(len(args)):
				n_args.append(args[i].split())

			for i in range(len(n_args)):
				background_exec_u(n_args[i])

		else:
			for i in range(len(args)):
				n_args.append(args[i].split())

			for i in range(len(n_args)):
				exec_u(n_args[i])

		return

	args = u_str.split()
	exec_u(args)

def redirect_u_output(args):
	fdIn = os.open(args[1], os.O_RDONLY)

	print(f"fdIn={fdIn}, fdOut={fdOut}");

	# note that
	#  fd #0 is "standard input" (by default, attached to kbd)
	#  fd #1 is "standard ouput" (by default, attached to display)
	#  fd #2 is "standard error" (by default, attached to display for error output)

	lineNum = 1
	while 1:
		input = os.read(fdIn, 10000)  # read up to 10k bytes
		if len(input) == 0: break     # done if nothing read
		lines = re.split(b"\n", input)
		for line in lines:
			strToPrint = f"{lineNum:5d}: {line.decode()}\n"
			os.write(1    , strToPrint.encode()) # write to fd1 (standard output)
			lineNum += 1
			

def redirect_u_input(args):
	pid = os.getpid()               # get and remember pid
	rc = os.fork()

	if rc < 0:
		os.write(2, ("fork failed, returning %d\n" % rc).encode())
		sys.exit(1)

	elif rc == 0:                   # child
		os.close(1)                 # redirect child's stdout
		os.open(args[1], os.O_CREAT | os.O_WRONLY);
		os.set_inheritable(1, True)

		args.pop()

		for dir in re.split(":", os.environ['PATH']): # try each directory in path
			program = "%s/%s" % (dir, args[0])
			try:
				os.execve(program, args, os.environ) # try to exec program
			except FileNotFoundError:             # ...expected
				pass                              # ...fail quietly 

		return

	else:                           # parent (forked ok)
		childPidCode = os.wait()

	sys.exit(-1)

def pipe_u(keyboard):
	cmd1, cmd2 = keyboard[0], keyboard[1] # seperates the two commands
	s_in = os.dup(0) #Save stdin for later, s_in is stacked in file descriptor
	s_out = os.dup(1) #Save stdout for later, s_out is also stacked
	fd_in = os.dup(s_in) #Variable for file descriptor input, created another to the stack

	pipe_r, pipe_w = os.pipe() # Get pipe file descriptors
	os.dup2(pipe_w, 1) # Put in pipe write for stdout
	running = exec_u(cmd1) # execute first command
	os.dup2(pipe_r, 0) # Put in pipe read for stdin
	os.dup2(s_out, 1) # Return stdout for stdout

	running = exec_u(cmd2) # execute second command
	os.dup2(s_in, 0) 
	os.close(s_in)
	os.close(s_out)
	os.close(pipe_r)
	os.close(pipe_w)
	return

def exec_u(args):
	pid = os.getpid()
	rc = os.fork()

	if(os.path.isfile(args[0])):
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
			return

	print(args[0] + " command not found.")
	sys.exit(-1)

def background_exec_u(args):
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
		elif rc > 0:
			return

	print(args[0] + " command not found.")
	sys.exit(-1)

def main():
	while(1):
		u_str = input()
		args = u_str.splitlines()

		for i in range(len(args)):
			shell_input(str(args[i]))

		#main()

main()