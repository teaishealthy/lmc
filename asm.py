# SPDX-License-Identifier: MIT
"""A simple LMC assembler"""

import sys
from typing import TypeAlias

Labels: TypeAlias = dict[str, int | None]

TAB = "    "
instructions: dict[str, int] = {
    "ADD": 100,
    "SUB": 200,
    "STA": 300,
    "LDA": 500,
    "BRA": 600,
    "BRZ": 700,
    "BRP": 800,
    "INP": 901,
    "OUT": 902,
    "HLT": 0,
}


def process_line(code: str) -> int:
    """Returns the opcode for the instruction.

    Args:
        line (list[str]): The instruction.

    Returns:
        int: The opcode for the instruction. -1 if the instruction does not exist.
    """
    return instructions.get(code, -1)


def is_branch(code: str) -> bool:
    """Whether the instruction is a branch instruction.

    Args:
        code (str): The instruction.

    Returns:
        bool: Whether the instruction is a branch instruction.
    """
    return code in ["BRA", "BRZ", "BRP"]


def needs_address(code: str) -> bool:
    """Whether the instruction needs an address.

    Args:
        code (str): The instruction.

    Returns:
        bool: Whether the instruction needs an address.
    """
    if code not in instructions:
        return False

    if code == "INP":
        return False
    elif code == "OUT":
        return False
    elif code == "HLT":
        return False
    else:
        return True


class Lazy:
    """A lazy opcode that needs to be resolved later."""

    def __init__(self, code: int, item: str, labels: Labels):
        """Creates a lazy opcode.

        Args:
            code (int): The base opcode.
            item (str): The referenced address.
            labels (Labels): A lookup table for labels.
        """
        self.code = code
        self.item = item
        self.lookup = labels

    def __int__(self) -> int:
        value = self.lookup.get(self.item)
        if value is None:
            print(f"error: label '{self.item}' not found")
            exit(1)

        return self.code + value

    def __str__(self) -> str:
        return str(int(self))


def process_instruction(
    instruction: str,
    line_number: int,
    len_machine_code: int,
    labels: Labels,
) -> int | Lazy | None:
    """Processes an instruction.

    Args:
        instruction (str): The instruction.
        line_number (int): The line number of the instruction. Used for error messages.
        len_machine_code (int): The length of the machine code so far.
        labels (Labels): A lookup table for labels.

    Returns:
        int | Lazy | None: The opcode for the instruction.
            Lazy if the instruction needs to be resolved later.
            None if there was an error.
    """
    instruction_split = instruction.strip().split(" ")

    if instruction_split[0] == "DAT":
        if len(instruction_split) < 2:
            spaces = len(instruction) - len(instruction.lstrip())
            hint = " " * (spaces + len(instruction_split[0])) + " " + "^"
            syntax_error(
                line_number,
                instruction,
                hint,
                "missing value",
            )
            return None

        try:
            value = int(instruction_split[1])
        except ValueError:
            spaces = len(instruction) - len(instruction.lstrip())
            hint = (
                " " * (spaces + len(instruction_split[0]))
                + " "
                + "^" * len(instruction_split[1])
            )
            syntax_error(
                line_number,
                instruction,
                hint,
                "invalid value",
            )
            return None
        return value

    if needs_address(instruction_split[0]):
        if len(instruction_split) != 2:
            spaces = len(instruction) - len(instruction.lstrip())
            hint = " " * (spaces + len(instruction_split[0])) + " " + "^"
            syntax_error(
                line_number,
                instruction,
                hint,
                "missing address",
            )
            return None

        try:
            address: int | str = int(instruction_split[1])
        except ValueError:
            location = instruction_split[1]
            if location not in labels:
                labels[location] = None

            return Lazy(process_line(instruction_split[0]), location, labels)

        if address < 0 or address > 99:
            spaces = len(instruction) - len(instruction.lstrip())
            hint = (
                " " * (spaces + len(instruction_split[0]))
                + " "
                + "^" * len(instruction_split[1])
            )
            syntax_error(line_number, instruction, hint, "address out of range (0-99)")

        if isinstance(address, str):
            return Lazy(process_line(instruction_split[0]), address, labels)
        else:
            return process_line(instruction_split[0]) + address

    else:
        op_code = process_line(instruction_split[0])
        if op_code == -1:
            # this is a label
            labels[instruction_split[0]] = len_machine_code
            new_instruction = " ".join(instruction_split[1:])

            if not new_instruction.strip():
                syntax_error(
                    line_number,
                    instruction,
                    " " + " " * len(instruction_split[0]) + "^",
                    "missing instruction",
                )
                exit(1)
            result = process_instruction(
                new_instruction,
                line_number,
                len_machine_code,
                labels,
            )
            return result
        return op_code


def compile_lmc(instructions: list[str], labels: Labels) -> list[int | Lazy] | None:
    """Compiles the LMC assembly into machine code.

    Args:
        instructions (list[str]): The LMC assembly.
        labels (Labels): A lookup table for labels. Should be empty.

    Returns:
        list[int | Lazy] | None: The machine code, contains Lazy objects that need to be resolved.
            None if there was an error.
    """  # noqa: E501
    machine_code: list[int | Lazy] = []

    for line, instruction in enumerate(instructions):
        if not instruction.strip():
            continue

        result = process_instruction(
            instruction,
            line,
            len(machine_code),
            labels,
        )

        if result is None:
            return None

        else:
            machine_code.append(result)

    return machine_code


def syntax_error(line: int, instruction: str, hint: str, error: str) -> None:
    """A shorthand for printing a syntax error and exiting.

    Args:
        line (int): The line the syntax error occurred on.
        instruction (str): The instruction that caused the syntax error.
        hint (str): A hint showing where on the line the syntax error occurred.
        error (str): The error message.
    """
    print(f"line {line}:")
    print(TAB + instruction)
    print(TAB + hint)
    print("syntax error: " + error)
    exit(1)


def main(fp: str):
    """The main function.

    Args:
        fp (str): The path to the file.
    """
    with open(fp, "r", encoding="utf8") as file:
        data = file.read()

    instructions = data.split("\n")
    labels: Labels = {}

    op_codes = compile_lmc(instructions, labels)
    if op_codes is None:
        exit(1)

    print("\n".join([str(op_code) for op_code in op_codes]))


if __name__ == "__main__":
    if sys.argv[1:]:
        main(sys.argv[1])
    else:
        print("error: no input file")
