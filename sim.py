import sys
from dataclasses import dataclass
from typing import SupportsIndex, TextIO


@dataclass
class LMCState:
    """The state of the LMC.

    Attributes:
        pc (int): The program counter.
        acc (int): The accumulator.
        memory (list[int]): The memory of the LMC.
    """

    pc: int
    """The program counter."""
    acc: int
    """The accumulator."""
    memory: list[int]
    """The memory of the LMC."""
    input: list[int]
    """The input to the LMC."""
    output: list[int]
    """The output of the LMC."""


def tick(opcode: int, lmc: LMCState, *, interactive: bool) -> LMCState | None:
    """Execute a single instruction on the LMC.

    Args:
        opcode (int): The opcode of the instruction to be executed.
        inputs (list[int]): The inputs to the LMC.
        lmc (LMCState): The current state of the LMC.
        interactive (bool): Whether the program can be interactive.

    Returns:
        LMCState | None: The new state of the LMC, or None if the instruction was HLT.
    """
    instruction = opcode // 100
    operand = opcode % 100

    if instruction == 0:
        # HLT
        return None
    elif instruction == 1:
        # ADD
        value = lmc.memory[operand]
        lmc.acc += value
    elif instruction == 2:
        value = lmc.memory[operand]
        lmc.acc -= value
    elif instruction == 3:
        lmc.memory[operand] = lmc.acc
    elif instruction == 5:
        lmc.acc = lmc.memory[operand]
    elif instruction == 6:
        # BRA - branch
        lmc.pc = operand
        return lmc
    elif instruction == 7:
        # BRZ - branch if zero
        if lmc.acc == 0:
            lmc.pc = operand
            return lmc
    elif instruction == 8:
        # BRP - branch if positive
        if lmc.acc >= 0:
            lmc.pc = operand
            return lmc
    elif instruction == 9:
        # IO
        if operand == 1:
            # INP
            if not interactive:
                print(
                    "error: cannot read input in non-interactive mode",
                    file=sys.stderr,
                )
                sys.exit(1)

            lmc.acc = lmc.input.pop(0)
        elif operand == 2:
            # OUT
            lmc.output.append(lmc.acc)
    else:
        raise ValueError(f"Invalid instruction {instruction}")

    lmc.pc += 1
    return lmc


def sim(opcodes: list[int], inputs: list[int], *, interactive: bool) -> LMCState:
    """Simulate the execution of a program on the LMC.

    Args:
        opcodes (list[int]): The opcodes of the program to be executed.
        inputs (list[int]): The inputs to the LMC.
        interactive (bool, optional): Whether the program can be interactive.

    Returns:
        LMCState: The final state of the LMC.
    """  # noqa: E501
    lmc = LMCState(pc=0, acc=0, memory=opcodes, input=inputs, output=[])

    while lmc.pc < len(lmc.memory):
        opcode = lmc.memory[lmc.pc]
        value = tick(opcode, lmc, interactive=interactive)
        if value is None:
            break

    return lmc


class InputList(list[int]):
    """A list that prompts for integers when empty."""

    def pop(self, index: SupportsIndex = -1, /) -> int:
        """Pop an item from the list.

        Args:
            index (SupportsIndex, optional): The index of the item to pop. Defaults to -1.

        Returns:
            int: The item that was popped.
        """  # noqa: E501
        if len(self) == 0:
            item = int(input("Input: "))
            return item

        return super().pop(index)


def main(file: TextIO, *, interactive: bool) -> None:
    """CLI Entry point.

    Args:
        fp (str): The filepath to the input file.
    """
    opcodes = [int(line) for line in file]

    memory = opcodes.copy()
    memory.extend([0] * (100 - len(opcodes)))

    lmc = sim(memory, InputList(), interactive=interactive)

    print("\n".join(str(x) for x in lmc.output))


if __name__ == "__main__":
    file: TextIO
    interactive = True
    if len(sys.argv) < 2:
        print("error: no input file", file=sys.stderr)
        sys.exit(1)

    if sys.argv[1] == "-":
        file = sys.stdin
        interactive = False
    else:
        file = open(sys.argv[1])

    main(file, interactive=interactive)
