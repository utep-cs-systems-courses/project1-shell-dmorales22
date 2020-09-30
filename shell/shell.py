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
        pid = os.getpid()
        rc = os.fork()
        if rc == 0:
            n_args = []
            args = u_str.split('|')
            
            for i in range(len(args)):
                n_args.append(args[i].split())

            pipe(n_args)
        else: 
            childPidCode = os.wait()
            main()
            return

    if '>' in u_str: #Redirects
        n_args = []
        args = u_str.split('>')

        for i in range(len(args)):
            n_args.append(args[i].split())

        redirect_output(n_args)
        return

    if '<' in u_str: #WIP
        n_args = []
        args = u_str.split('<')
        for i in range(len(args)):
            n_args.append(args[i].split())

        redirect_input(n_args)
        return

    if '&' in u_str: #For background processes
        n_args = []
        args = u_str.split('&')

        if args[-1] == "": #Runs background process
            args.remove("")
            for i in range(len(args)):
                n_args.append(args[i].split())

            for i in range(len(n_args)):
                background_exec(n_args[i])

        else: #Runs processes normally
            for i in range(len(args)):
                n_args.append(args[i].split())

            for i in range(len(n_args)):
                exec(n_args[i])

        return

    args = u_str.split()
    exec(args)

def redirect_input(args): #Redirects. 
    #Incomplete
    print("")
    return

def redirect_output(args): #Redirects
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

	return 

def pipe(args): #Method for pipe instructions
    arg1, arg2 = args[0], args[1]  #Separating commands (only two)
    pipe_read, pipe_write = os.pipe() #Creates pipe

    for f in (pipe_read, pipe_write):
        os.set_inheritable(f, True)

    rc = os.fork() #Creates fork

    if rc < 0: 
        os.write(2,("Fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0: #Runs first command
        os.close(1) 
        file_descriptor = os.dup(pipe_write) #Gets file descriptor from pipe_write
        os.set_inheritable(1, True) #Sets the inheritable flag for file descriptor to use in child process

        for file_descriptor in (pipe_read, pipe_write): 
            os.close(file_descriptor)
        
        pipe_exec(arg1)

    elif rc > 0:
        os.close(0)
        file_descriptor = os.dup(pipe_read)
        os.set_inheritable(0, True)

        for file_descriptor in (pipe_write, pipe_read):
            os.close(file_descriptor)
        
        pipe_exec(arg2)

    else:
        main()
        return

def pipe_exec(args):

    for dir in re.split(':', os.environ['PATH']):  # try each directory in the path
        program = "%s/%s" % (dir, args[0])
        try:
            os.execve(program, args, os.environ)  # try to exec program
        except FileNotFoundError:  # ...expected
            pass  # ...fail quietly
    os.write(2, ("Could not exec %s\n" % parent[0]).encode())
    sys.exit(1)  # terminate with error


def exec(args): #This method execs commands using forks. 
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
	sys.exit(0)

def background_exec(args): #This method executes commands in background. 
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

def os_input():
	prompt = "$ "
	if "PS1" in os.environ:
		prompt = os.environ["PS1"]

	os.write(1, prompt.encode())
	u_str = os.read(0,1000).decode()
	return u_str

def main():
    while(1): #Everything is ran in loop
        u_str = os_input()
        #u_str = input()
        args = u_str.splitlines()

        for i in range(len(args)): #For inputs that are multiple lines. 
            shell_input(str(args[i]))


main()