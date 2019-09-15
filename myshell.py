import os, stat, getpass, socket, pathlib, sys, datetime, readline, shlex
from subprocess import Popen

#this class contains all code used to control variables are initialised and displayed
class constructor():
	#path of the shell
	home = os.getcwd()

	#setting the environmental variable for the shell
	os.environ["shell"] = home

	#absolute file path of readme file so it can be accesed from all directories
	manual = os.path.abspath("readme")

	# ansi color codes
	red = "\033[31m"
	green = "\033[32;1m" #bright green
	blue = "\033[34;1m" 
	blue_white = "\033[34;47m" #blue w/ white background
	reset = "\033[0m"

	#contructing the cmd prompt
	def read_line(user, host, pwd):
		if os.getcwd() == constructor.home:
			return input(constructor.green + user + "@" + host + ":~" + "$ " + constructor.reset).strip()
		else:
			return input(constructor.green + user + "@" + host + ":~" + pwd + "$ " + constructor.reset).strip()

	def tokenize(line):
		return line.split()

	#controls majority of strings that are printed, 
	#all functions genrally return data as opposed to directly printing in the funtion 
	#incase the data is requested as an output to a file
	def printer(obj):
		if obj != None:
			print(obj)

	#funtion to suppurt tab feature in command line
	#only works for first word
	def make_completer(vocabulary):
		def custom_complete(text, state):
			results = [x for x in vocabulary if x.startswith(text)] + [None]
			return results[state] + " "
		return custom_complete

#this class defines all functions required to run commands
class myshell():
	#change diretory funtion
	def cd(arg):
		try:
			if len(arg) == 0:
				print(os.getcwd())
			else:
				os.chdir(arg)
		except Exception as e:
			return(constructor.red + "cd: no such file of directory: " + arg + constructor.reset)

	#funtiom to clear sreen, uses ansi to clear screen 
	def clr():
		print("\033c")

	#converts file mode into a readable string
	def make_mode(pathname):
		mode = stat.filemode(os.stat(pathname).st_mode)
		return mode

	#converts file date last modified from seconds to mon day time
	def make_date(pathname):
		months = {1 : "Jan",
			2 : "Feb",
			3 : "Mar",
			4 : "Apr",
			5 : "May",
			6 : "Jun",
			7 : "Jul",
			8 : "Aug",
			9 : "Sep",
			10 : "Oct",
			11 : "Nov",
			12 : "Dec",}

		seconds = os.stat(pathname).st_mtime
		date = str(datetime.datetime.fromtimestamp(seconds))
		mon = months[int(date[5:7])]
		day = str(int(date[8:10]))
		time = date[11:16]
		return "{} {:>2} {}".format(mon, day, time)

	#find length the largest file size, used to format size string
	def format_size(path):
		sizes = []
		for entry in os.listdir(path):
			pathname = os.path.join(path, entry)
			sizes.append(str(os.stat(pathname).st_size))

		spaces = 0
		for size in sizes:
			if len(size) > spaces:
				spaces = len(size)

		return spaces

	#list directories funtion, displayed in long listing format
	def dir(arg):
		if len(arg) == 0:
			files = []
			for entry in os.listdir("."):
				mode = myshell.make_mode(entry)
				link = str(os.stat(entry).st_nlink)
				user = getpass.getuser()
				group = getpass.getuser()
				size = str(os.stat(entry).st_size)
				date = myshell.make_date(entry)
				spaces = myshell.format_size(".")

				#print blue if directory
				if stat.S_ISDIR(os.stat(entry).st_mode) != 0:
					files.append("{} {} {} {} {:>{}} {:>2} {}{}{}".format(mode, link, user, group, size, spaces, date, constructor.blue, entry, constructor.reset))
				else:
					files.append("{} {} {} {} {:>{}} {} {}".format(mode, link, user, group, size, spaces, date, entry))
					
			return("\n".join(files))
		else:
			try:
				path = arg
				files = []
				for entry in os.listdir(path):
					pathname = os.path.join(path, entry)
					mode = myshell.make_mode(pathname)
					link = str(os.stat(pathname).st_nlink)
					user = getpass.getuser()
					group = getpass.getuser()
					size = str(os.stat(pathname).st_size)
					date = myshell.make_date(pathname)
					spaces = myshell.format_size(path)

					#print in blue if directory
					if stat.S_ISDIR(os.stat(pathname).st_mode) != 0:
						files.append("{} {} {} {} {:>{}} {:>2} {}{}{}".format(mode, link, user, group, size, spaces, date, constructor.blue, entry, constructor.reset))
					else:
						files.append("{} {} {} {} {:>{}} {} {}".format(mode, link, user, group, size, spaces, date, entry))

				return("\n".join(files))

			except Exception as e:
				return(constructor.red + "{} is not a directory".format(path) + constructor.reset)

	#funtion to display envrionment strings
	def environ(arg):
		if len(arg) == 0:
			for env in os.environ:
				print(env + "=" + os.environ["{}".format(env)])
		else:
			try:
				path = arg
				return(path + "=" + os.environ["{}".format(path)])
			except KeyError:
				return(constructor.red + "{} has not been defined as an Environment variable.".format(path) +  constructor.reset)

	def echo(arg):
		if len(arg) == 0:
			return("")
		else:
			return(arg)

	def pause():
		input(constructor.blue_white + "Press enter to continue..." + constructor.reset)

	#more filter, prints text 20 lines at a time
	#implemets pause funtion
	def more(arg):
		with open (arg) as f:
			lines = f.readlines()
			i = 0
			while i < len(lines):
				if len(lines) - i > 20:
					for line in range(i, i + 20):
						print(lines[i], end="")
						i += 1

					myshell.pause()
				else:
					for line in range(i, len(lines)):
						print(lines[i], end="")
						i += 1

	#help fucntion that displays readme file
	#can also display files with help on specific commands
	#implements more funtion
	def help(arg):
		if len(arg) == 0:
			myshell.more(constructor.manual)
			print()
		else:
			try:
				myshell.more(arg + ".txt")
				return("\n")
			except FileNotFoundError:
				return(constructor.red + "{} is not an internal command.".format(arg) + constructor.reset)


	def quit():
		print("Quitting...")
		sys.exit(0)

	#funtion to control output redirection to a file
	def redir_output(cmd, filename, sign):
		#write
		if sign == ">":
			with open(filename, "w+") as f:
				if len(cmd) > 1:
					if cmd[0] == "help":
						with open (cmd[1] + ".txt") as f2:
							f.write(f2.read())
					else:
						f.write(getattr(myshell, cmd[0])(" ".join(cmd[1:])))
				else:
					if cmd[0] == "help":
						with open (constructor.manual) as f2:
							f.write(f2.read())
					else:
						f.write(getattr(myshell, cmd[0])(""))
		else:
		#append
			with open(filename, "a+") as f:
				if len(cmd) > 1:
					if cmd[0] == "help":
						with open (cmd[1:] + ".txt") as f2:
							f.write(f2.read())
					else:
						f.write(getattr(myshell, cmd[0])(" ".join(cmd[1:])))
				else:
					if cmd[0] == "help":
						with open (constructor.manual) as f2:
							f.write(f2.read())
					else:
						f.write(getattr(myshell, cmd[0])(""))
		 		
	#funtion to control shell forking and child processes
	def launch(args):
		pid = os.fork()
		if pid > 0:
			wpid = os.waitpid(pid, 0)
		else:
			try:
				os.execvp(args[0], args)
			except Exception as e:
				print(constructor.red + "myshell: command not found: " + args[0] + constructor.reset)
				os.abort()
				

	#function take command line input from a file
	def myshell(args):
		try:
			for line in open(args, "r"):
				myshell.execute(line.split())
		except Exception as e:
			print(constructor.red + "myshell: cannot access " + args + ": No such file or directory" + constructor.reset)

	def execute(args):
		try:
			if len(args) == 0:
				pass
			elif "cd" == args[0] or "pwd" == args[0]:
				constructor.printer(myshell.cd("".join(args[1:])))

			elif "pwd" == args[0]:
				 constructor.printer(os.getcwd())

			elif "dir" == args[0]:
				constructor.printer(myshell.dir("".join(args[1:])))

			elif "clr" == args[0]:
				myshell.clr()

			elif "environ" == args[0]:
				constructor.printer(myshell.environ("".join(args[1:])))
		
			elif "echo" == args[0]:
				constructor.printer(myshell.echo(" ".join(args[1:])))
	
			elif "pause" == args[0]:
				myshell.pause()
		
			elif "help" == args[0]:
				constructor.printer(myshell.help("".join(args[1:])))

			elif "myshell" == args[0]:
				myshell.myshell("".join(args[1:]))
		
			elif "quit" == args[0]:
				myshell.quit()
			else:
				myshell.launch(args)
		except EOFError as e:
			print("")


def main():
	readline.parse_and_bind("tab: complete")
	while True:
		USER = getpass.getuser()
		HOST = socket.gethostname()
		PWD = os.getcwd()
		readline.set_completer(constructor.make_completer(os.listdir(".")))

		#contruct prompt and tokenize commands
		line = constructor.read_line(USER, HOST, PWD)
		args = constructor.tokenize(line)

		if len(args) > 1: 
			#detect output redirection
			if args[-2] == ">":
				myshell.redir_output(args[0:-2], args[-1], args[-2])
			elif args[-2] == ">>":
				myshell.redir_output(args[0:-2], args[-1], args[-2]) 
			#manage background processes
			elif args[-1] == "&": 
				Popen(args[:-1])	
			else:
				myshell.execute(args)
		else:
			myshell.execute(args)

if __name__ == '__main__':
	main()

