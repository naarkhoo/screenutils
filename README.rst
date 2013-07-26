screenutils
===========

screenutils is a set of classes that should help handling gnu-screen windows.

Feel free to report any modification you made, the whole code source is
available under the terms of the GPLv2.

Exemple usage
-------------

Exemple in a python console::

   >>> from screenutils import list_screens, Screen
   >>> list_screens()
   []
   >>> s= Screen("session1",True)
   >>> # screen blink once
   >>> # funky prompt should reduce logs lisibility so you should use sh or bash
   >>> s.send_commands('bash')
   >>> s.enable_logs()
   >>> s.send_commands("df") ## basically this function didn't work and I added a similar function
   >>> print next(s.logs)
   df
   Filesystem           1K-blocks      Used Available Use% Mounted on
   /dev/sda6             20161172   8084052  11052980  43% /
   none                   1505916       304   1505612   1% /dev
   none                   1512676       936   1511740   1% /dev/shm
   none                   1512676       380   1512296   1% /var/run
   none                   1512676         0   1512676   0% /var/lock
   none                   1512676         0   1512676   0% /lib/init/rw
   none                  20161172   8084052  11052980  43% /var/lib/ureadahead/debugfs
   /dev/sda7            403567768 196284216 186783420  52% /home
   popi@popi-laptop:~/Dev/github/screenutils$
   >>> s.disable_logs()
   >>> s = None
   >>> s = Screen("session1")
   >>> s.exists
   True
   >>> s2 = Screen("session2")
   >>> s2.exists
   False
   >>> s2.initialize()
   >>> list_screens()
   [<Screen 'session2'>, <Screen 'session1'>]
   >>>

   >>> conn = tunel('yourserver', username='yourusername',password='passx')
   >>> print conn.execute_command_screen_ssh(command='python /myremotedir/myfolder/script.py', name='python')
   >>> print conn.execute_command_screen_ssh(command='perl /myremotedir/myfolder/script.pl', name='perl')
   >>> print conn.execute_command_screen_ssh(command='ls -d > /myremotedir/tmp.log', name='log')
   >>> print conn.execute_command_screen_ssh(command='bash')
   >>> print conn.list_screens_ssh
       ['python', 'perl', 'log', 'bash']
   >>> print list_screens_ssh(conn)
   >>> print conn.kill_screen_ssh('python')
   >>> print conn.list_screens_ssh
       ['perl', 'log' ,'bash']
   >>> conn.download('tmp.log','pathto/myremotedir/', 'pathto/localdir/')
   >>> conn.upload('newfile.log','pathto/myremotedir/', 'pathto/localdir/')
   >>> conn.execute('ls /myremotedir/')

Installation
-------------

You could install screenutils from github, by doing the following::

    $ git clone http://github.com/Christophe31/screenutils.git
    $ cd screenutils
    $ python setup.py install

Or by just using the packages publicated at pypi, for instance with pip::

    $ pip install screenutils

Features
---------

 * screens listing
 * screen session creation
 * screen session closing
 * screen code insertion
 * screen monitoring/logging
 * screen session sharing with unix users
    - to allow this feature, you will **need** to change some unixs rigths:
        + ``sudo chmod +s /usr/bin/screen``
	+ ``sudo chmod 755 /var/run/screen``

 * running command on a ssh tunel
 * making screen session on ssh tunel
 * terminating a screen session on ssh tunel
 * screen listing on a ssh tunel
 * download/upload on a ssh tunel

Known issues
-------------

This may not work properly with bpython.
running short commands such as "ls" can not be run on a screen session via ssh; since the terminal ends much faster than listing the result, however it works for heavier commands; for just generating a session, "bash" command is recommended

Roadmap
--------

 * multi windows screen support
