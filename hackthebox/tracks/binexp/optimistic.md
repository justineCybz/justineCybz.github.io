# Optimistic
## Behaviour
```
└─$ ./optimistic           
Welcome to the positive community!
We help you embrace optimism.
Would you like to enroll yourself? (y/n): y
Great! Here's a small welcome gift: 0x7ffdafc3d5c0
Please provide your details.
```
After inputting 'y' to enrol, the user is provided with a memory address.

## Static Analysis


```c
  printf("Length of name: ");
  __isoc99_scanf(&DAT_00102104,&local_84); // [1]
  if (0x40 < (int)local_84) { //[2]
    puts("Woah there! You shouldn\'t be too optimistic.");
                    /* WARNING: Subroutine does not return */
    exit(0);
  }
  printf("Name: ");
  sVar2 = read(0,local_68,(ulong)local_84); //[3]
  local_84 = 0;
  while( true ) {
    if ((int)sVar2 + -9 <= (int)local_84) {
      puts("Thank you! We\'ll be in touch soon.");
      return;
    }
```
### Vulnerability
- `[1]` an unsigned integer is taken as input
- `[2]` the value is type cast to a signed integer and checked whether its value is less than 64
- `[3]` it is type casted to unsigned long, thus it is vulnerable to an integer overflow wraparound, where a negative signed integer wraps around to a large number when unsigned.
This allows us to increase the amount of bytes read in by `read()` beyond the 64bytes that were checked in the statement at `[2]`.


