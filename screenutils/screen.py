# -*- coding:utf-8 -*-
#
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the GNU Public License 2 or upper.
# Please ask if you wish a more permissive license.


from screenutils.errors import ScreenNotFoundError
import os
import commands as cox

try:
    from commands import getoutput
except:
    from subprocess import getoutput
from threading import Thread
from os import system
from os.path import isfile, getsize
from time import sleep

def tailf(file_):
    """Each value is content added to the log file since last value return"""
    last_size = getsize(file_)
    while True:
        cur_size = getsize(file_)
        if ( cur_size != last_size ):
            f = open(file_, 'r')
            f.seek(last_size if cur_size > last_size else 0)
            text = f.read()
            f.close()
            last_size = cur_size
            yield text
        else:
            yield ""

def list_screens():
    """List all the existing screens and build a Screen instance for each
    """
    return [
                Screen(".".join(l.split(".")[1:]).split("\t")[0])
                for l in getoutput("screen -ls | grep -P '\t'").split('\n')
                if ".".join(l.split(".")[1:]).split("\t")[0]
            ]

def getfile(string, alternative):
	""" return alternative if the string is empty
	"""
	if len(string) == 0:
		return alternative
	else:
		return string

class Screen(object):
    """Represents a gnu-screen object::

        >>> s=Screen("screenName", initialize=True)
        >>> s.name
        'screenName'
        >>> s.exists
        True
        >>> s.state
        >>> s.send_commands("man -k keyboard")
        >>> s.kill()
        >>> s.exists
        False
    """

    def __init__(self, name, initialize=False):
        self.name = name
        self.commanddict = dict() # for collecting the logs
        self.flag = 'deactive' #do you need the status of a command ?
        self._id = None
        self._status = None
        self.logs=None
        if initialize:
            self.initialize()

    @property
    def id(self):
        """return the identifier of the screen as string"""
        if not self._id:
            self._set_screen_infos()
        return self._id

    @property
    def status(self):
        """return the status of the screen as string"""
        self._set_screen_infos()
        return self._status

    @property
    def exists(self):
        """Tell if the screen session exists or not."""
        # Parse the screen -ls call, to find if the screen exists or not.
        # The screen -ls | grep name returns something like that:
        #  "	28062.G.Terminal	(Detached)"
        lines = getoutput("screen -ls | grep " + self.name).split('\n')
        return self.name in [".".join(l.split(".")[1:]).split("\t")[0]
                             for l in lines]

    def enable_logs(self):
        self.flag = 'active'
        self._screen_commands("logfile " + self.name, "log on")
        system('touch '+self.name)
        self.logs=tailf(self.name)
        next(self.logs)

    def disable_logs(self):
        self._screen_commands("log off")
        self.logs=None
        self.flag = 'deactive'

    def initialize(self):
        """initialize a screen, if does not exists yet"""
        if not self.exists:
            self._id=None
            # Detach the screen once attached, on a new tread.
            Thread(target=self._delayed_detach).start()
            # support Unicode (-U),
            # attach to a new/existing named screen (-R).
            system('screen -UR ' + self.name)

    def interrupt(self):
        """Insert CTRL+C in the screen session"""
        self._screen_commands("eval \"stuff \\003\"")

    def kill(self):
        """Kill the screen applications then close the screen"""
        if self.flag == 'active': # remove the status files
			if os.path.isfile(self.name+'.err'):
				os.unlink(self.name+'.err')
			if os.path.isfile(self.name+".log"):
				os.unlink(self.name+'.err')
			if os.path.isfile(self.name+".log"):
				os.unlink(self.name+".log")
        self._screen_commands('quit')

    def detach(self):
        """detach the screen"""
        self._check_exists()
        system("screen -d " + self.name)
        

    def send_commands_original(self, *commands):
        """send commands to the active gnu-screen"""
        self._check_exists()
				
        for command in commands:
            self._screen_commands( 'stuff "' + command + '" ' ,
                                   'eval "stuff \\015"' )
                                   
    def send_commands(self, *commands, **status):
        """send commands to the active gnu-screen"""
        
        status_show = status.get('status', False)
        for command in commands:
			if self.flag == 'active':
				cmd = command + '> ' + str(self.name)+'.out 2> ' + str(self.name)+'.err'
			else:
				cmd = command
			self._screen_commands( 'stuff "' + cmd + '" ' ,
                                   'eval "stuff \\015"' )
        
        if self.flag == 'active':
			f = open(self.name+'.out', 'r')
			textout = f.read()
			f.close
			
			f = open(self.name+'.err', 'r')
			texterr = f.read()
			f.close
			
			if status_show == True:
				print(textout)
				if getsize(self.name + '.err') != 0:
					print 'ERROR:\n'
        # below is the log dictionary ! contains, command, stdout, stderr
        self.commanddict[len(self.commanddict)+1] = [commands[0], getfile(textout, 'ERROR'), getfile(texterr, 'Done')]

    def add_user_access(self, unix_user_name):
        """allow to share your session with an other unix user"""
        self._screen_commands('multiuser on', 'acladd ' + unix_user_name)
        
    def report(self, n=1, entire=False):
		""" return nth command status or write the entire log file
		"""
		L = range(1, len(self.commanddict)+1)
		if entire==True:
			f = open(str(self.name)+"_screen.log", "w")
			for item in L:
				f.writelines("# " + str(item) + "\n")
				f.writelines(["%s\n" % item  for item in self.commanddict.get(item)])
				f.writelines("--------------------\n\n")
			f.close()
			f = open(str(self.name)+"_screen.log", "r")
			mylog = f.read()
			print mylog
			print 'find the log file at \n' + str(os.getcwd()) + "/" + str(self.name)+"_screen.log"
		else:
			f = open(str(self.name)+".log", "w")
			for item in L[-n:]:
				f.writelines("# " + str(item) + "\n")
				f.writelines(["%s\n" % item  for item in self.commanddict.get(item)])
				f.writelines("--------------------\n\n")
			f.close()
			f = open(str(self.name)+".log", "r")
			mylog = f.read()
			print mylog
		
    def cmdcounter(self):
		"""how many commands are executed in a given screen"""
		print len(self.commanddict)

    def _screen_commands(self, *commands):
        """allow to insert generic screen specific commands
        a glossary of the existing screen command in `man screen`"""
        self._check_exists()
        for command in commands:
			#~ print 'screen -x ' + self.name + ' -X ' + command
			system('screen -x ' + self.name + ' -X ' + command)
			#~ print(cox.getstatusoutput('screen -x ' + self.name + ' -X ' + command))
			sleep(0.02)

    def _check_exists(self, message="Error code: 404"):
        """check whereas the screen exist. if not, raise an exception"""
        if not self.exists:
            raise ScreenNotFoundError(message)

    def _set_screen_infos(self):
        """set the screen information related parameters"""
        if self.exists:
            infos = getoutput("screen -ls | grep %s" % self.name).split('\t')[1:]
            self._id = infos[0].split('.')[0]
            if len(infos)==3:
                self._date = infos[1][1:-1]
                self._status = infos[2][1:-1]
            else:
                self._status = infos[1][1:-1]

    def _delayed_detach(self):
        sleep(0.5)
        self.detach()

    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self.name)
        

import paramiko
import os, shutil


class tunel(object):
	def __init__(self, server, username, password='empty', key='empty', rsa =False):
		self.server = server
		self.username = username
		self.password = password
		self.rsa = rsa
		self.key = key
		
	def execute(self,cmd):
		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		if self.password != 'empty' and self.rsa == True:
			raise Exception("!! either password or rsa - not both")
		if self.password == 'empty' and self.rsa == False and self.key == 'empty':
			raise Exception("how should I access without rsa/password")
		if self.password != 'empty':
			self.ssh.connect(self.server, username=self.username, password=self.password)
		if self.key != 'empty':
			if os.path.isfile(self.key):
				self.ssh.connect(self.server, username=self.username, key_filename=self.key)
			else:
				raise Exception('I cant see the key file at\n'+self.key)
		if self.rsa == True:
			rsafile = os.path.expanduser('~/.ssh/id_rsa')
			print 'rsa file vojod dare'
			if os.path.isfile(rsafile):
				try:
					mykey = paramiko.RSAKey.from_private_key_file(rsafile)
				except:
					raise Exception('If your rsa is encrypted - please make connection using the actual password')
				self.ssh.connect(self.server, username=self.username, pkey=mykey)
			else:
				raise Exception('Cant see id_rsa at\n' + str(rsafile))
		
		stdin, stdout, stderr = self.ssh.exec_command(cmd)
		stderr.flush()
		cmd_error = stderr.readlines()
		cmd_out = stdout.readlines()
		#~ cmd_in = stdin.readlines()
		#~ if cmd_error:
			#~ print 'Error :\n'
			#~ print cmd_error[0]
		#~ else:
			#~ print 'the code is executed\n'
			#~ print stdout.readlines()
		self.ssh.close()
		return cmd_out, cmd_error

	def upload(self, filename, remotepath, localpath):
		ssh = paramiko.SSHClient() 
		#~ ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # take care of unknown hosts
		
		if self.password == 'empty' and self.rsa == False and self.key == 'empty':
			raise Exception("how should I login ? \n provide me with password/key/rsa")
		
		elif self.password != 'empty' and self.rsa == False and self.key == 'empty':
			ssh.connect(self.server, username=self.username, password=self.password)
			
		elif self.password == 'empty' and self.rsa == False and self.key != 'empty':
			ssh.connect(self.server, username=self.username, key_filename=self.key)
			
		elif self.rsa == True:
			rsafile = os.path.expanduser('~/.ssh/id_rsa')
			if os.path.isfile(rsafile):
				try:
					mykey = paramiko.RSAKey.from_private_key_file(rsafile)
				except:
					raise Exception('If your rsa is encrypted - please make connection using the actual password')
				self.ssh.connect(self.server, username=self.username, pkey=mykey)
			else:
				raise Exception('Cant see id_rsa at\n' + str(rsafile))
				
		else:
			raise Exception('unknown error in ssh communication')

		sftp = ssh.open_sftp()
		try:
			sftp.put(localpath+filename, remotepath+filename)
		except OSError:
			print 'Upload Error; possibilities\n file/localpath/remotepath does not exist\n'
		sftp.close()
		ssh.close()
		tmp = tunel(self.server, self.username, self.password)
		[cmdout,cmderror] = tmp.execute('ls '+ remotepath+filename)
		if cmderror:
			print 'ERORR in uploading : '+ str(cmderror[0])
		if cmdout:
			print 'the file is there ! : ' + str(cmdout[0])
			
	def kill_screen_ssh(conn, name):
		'''kill a screen session by its name'''
		cmd = 'screen -S '+name+' -X quit'
		cmd_out, cmd_err = conn.execute(cmd)
		return cmd_out, cmd_err
		
	def execute_command_screen_ssh(conn, command, name=''):
		'''execute cmd in a server under a new screen session'''
		if len(name) == 0:
			name = command.split(' ')[0][0:5]
	
		screensonssh = list_screens_ssh(conn)
		if name in screensonssh:
			name = name+"_"+str(screensonssh.count(name)+1)
	
		cmd = 'screen -m -d -S '+name+' '+command
		cmd_out, cmd_err = conn.execute(cmd)
		return cmd_out, cmd_err
		
		
def list_screens_ssh(conn):
    """List all the existing screens and build a Screen instance for each
    """
    a, b = conn.execute("screen -ls | grep -P '\t'")
    return [".".join(l.split(".")[1:]).split("\t")[0] for l in a]
