# asmmix
A tool to mix around the output of `clang -S`, breaking byte patterns in the resulting binary.

It does so by inserting `nop`s and random bytes with `jmp`s over them into user code, as well as by breaking it up into blocks based on compiler-generated labels and rearranging some of them while keeping control flow intact.

### Usage:

```shell
# Process test1.cpp
> python asmmix.py from_file test1.cpp
test1.cpp

# Process test1.s
> python asmmix.py from_file test1.cpp --ext-out=".s"
test1.s

# Process test1.s or test1.asm (whichever exists, tried in given order)
> python asmmix.py from_file test1.cpp --ext-out="['.s', '.asm']"
test1.s

# Process only files that end with ".cpp"
> python asmmix.py from_files test1.cpp test2.cpp test3.c --ext-in=".cpp"
test1.cpp test2.cpp

# Process only files that end with ".cpp" or ".c"
> python asmmix.py from_files test1.cpp test2.cxx test3.c --ext-in="['.cpp', '.c']"
test1.cpp test3.c

# Process files listed as ending with ".cpp" that actually end in ".s" or ".asm"
> python asmmix.py from_files test1.cpp test2.cpp test3.c --ext-in=".cpp" --ext-out="['.s', '.asm']"
test1.s test2.s

# Process files within the given string (arguments are same as in from_files)
> python asmmix.py from_string "clang -O2 -S test1.cpp test3.cxx -o test.exe" --ext-in=".cpp" --ext-out=".s"
clang -O2 -S test1.s test3.cxx -o test.exe
```

Preferences are taken from [prefs.py](./prefs.py)
