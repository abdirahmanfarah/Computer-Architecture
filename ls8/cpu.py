"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.SP = 7
        self.reg[7] = 0xF4
        self.branch_table = {
            0b00000001: self.HLT,
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b10100010: self.MULT,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b01010000: self.CALL,
            0b00010001: self.RET,
            0b10100000: self.ADD,

        }

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def load(self, file_name):
        """Load a program into memory."""

        address = 0
        with open(sys.argv[1]) as f:
            for line in f:
                string_val = line.split("#")[0].strip()
                if string_val == '':
                    continue
                v = int(string_val, 2)
                # print[v]
                self.ram[address] = v
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MULT":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def HLT(self):
        sys.exit()

    def LDI(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)

        self.reg[operand_a] = operand_b
        self.pc += 3

    def PRN(self):
        operand_a = self.ram_read(self.pc + 1)
        print(self.reg[operand_a])
        self.pc += 2

    def MULT(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)

        self.alu("MULT", operand_a, operand_b)
        self.pc += 3

    def ADD(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)

        self.alu("ADD", operand_a, operand_b)
        self.pc += 3

    def PUSH(self):
        operand_a = self.ram_read(self.pc + 1)
        # Decrement the SP
        self.reg[self.SP] -= 1
        # Get value out of register
        data = self.reg[operand_a]
        # store value in memory at SP
        top_of_stack_addr = self.reg[self.SP]
        self.ram_write(top_of_stack_addr, data)
        self.pc += 2

    def POP(self):
        operand_a = self.ram_read(self.pc + 1)

        top_of_stack_addr = self.reg[self.SP]

        value = self.ram_read(top_of_stack_addr)

        self.reg[operand_a] = value

        self.reg[self.SP] += 1

        self.pc += 2

    def CALL(self):

        # Push it on the Stack
        self.reg[self.SP] -= 1

        get_addr = self.pc + 2

        top_of_stack_addr = self.reg[self.SP]

        self.ram[top_of_stack_addr] = get_addr

        operand_a = self.ram_read(self.pc + 1)
        self.pc = self.reg[operand_a]

    def RET(self):
        top_of_stack_addr = self.reg[self.SP]
        self.pc = self.ram[top_of_stack_addr]
        self.reg[self.SP] += 1

    def run(self):

        running = True

        while running:
            IR = self.ram_read(self.pc)
            self.branch_table[IR]()
