# Little Man Computer

This repository contains a few tools around the little man computer.

## asm.py

A simple but roboust assembler for lmc assmebly.

### Usage

```bash
$ python3 asm.py input.asm > output
```

### Example Programs

| Program                             | Description                    |
|-------------------------------------|--------------------------------|
| [mul.asm](examples/mul.asm)         | Multiplies two numbers         |
| [sum-100.asm](examples/sum-100.asm) | Sums the numbers from 1 to 100 |

### Example Programs

| Program                             | Description                    |
|-------------------------------------|--------------------------------|
| [mul.asm](examples/mul.asm)         | Multiplies two numbers         |
| [sum-100.asm](examples/sum-100.asm) | Sums the numbers from 1 to 100 |


## sim.py

An lmc simulator.

### Usage

```bash
$ python3 sim.py input
```
or
```bash
$ python3 asm.py examples/sum-100.asm | python3 sim.py -
```

> [!NOTE]
> The simulator may prompt for input over stdin. This is not possible when the simulator accepts a program over stdin. In this case, the simulator will exit with an error.
