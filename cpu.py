# cpu
import sys


class CPU:
    def __init__(self):
        self.registers = [0b0] * 8
        self.pc = 0
        self.ir = None
        self.ram = [0b0] * 0xFF
        self.spl = 8 - 1
        self.registers[self.spl] = 0xF4
        self.fl = 0b00000000
        self.eq = 0b00000000
        self.lt = 0b00000000
        self.gt = 0b00000000

        self.OPCODES = {
            0b10000010: 'LDI',
            0b01000111: 'PRN',
            0b00000001: 'HLT',
            0b10100000: 'ADD',
            0b10100010: 'MUL',
            0b01000110: 'POP',
            0b01000101: 'PUSH',
            0b10000100: 'ST',
            0b01010000: 'CALL',
            0b00010001: 'RET',
            0b10100111: 'CMP',
            0b01010100: 'JMP',
            0b01010101: 'JEQ',
            0b01010110: 'JNE',
        }

    def load(self, filename):
        try:
            with open(filename, 'r') as f:
                lines = (line for line in f.readlines() if not (
                    line[0] == '#' or line[0] == '\n'))
                program = [int(line.split('#')[0].strip(), 2)
                           for line in lines]
            address = 0

            for instruction in program:
                self.ram[address] = instruction
                address += 1
        except FileNotFoundError as e:
            print(e)
            sys.exit()

    def alu(self, op, reg_a, reg_b):
        # addition
        if op == "ADD":
            self.registers[reg_a] += self.registers[reg_b]
        # multiplication
        elif op == "MUL":
            self.registers[reg_a] *= self.registers[reg_b]
        # compare
        elif op == "CMP":
            a = self.registers[reg_a]
            b = self.registers[reg_b]
            if a == b:
                self.eq, self.lt, self.gt = (1, 0, 0)
            elif a < b:
                self.eq, self.lt, self.gt = (0, 1, 0)
            elif a > b:
                self.eq, self.lt, self.gt = (0, 0, 1)
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')
        for i in range(8):
            print(" %02X" % self.registers[i], end='')
        print()

    def ram_read(self, addr):
        return self.ram[addr]

    def ram_write(self, value, addr):
        self.ram[addr] = value

    def ldi(self):
        reg = self.ram[self.pc + 1]
        val = self.ram[self.pc + 2]
        self.registers[reg] = val
        self.pc += 3

    def prn(self):
        reg = self.ram[self.pc + 1]
        val = self.registers[reg]
        print(f"hex val: {val:x}\tdec val: {val}")
        self.pc += 2

    def aluf(self, op):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        self.alu(op, reg_a, reg_b)
        self.pc += 3

    def push(self):
        reg = self.ram[self.pc + 1]
        val = self.registers[reg]
        self.registers[self.spl] -= 1
        self.ram[self.registers[self.spl]] = val
        self.pc += 2

    def pop(self):
        reg = self.ram[self.pc + 1]
        val = self.ram[self.registers[self.spl]]
        self.registers[reg] = val
        self.registers[self.spl] += 1
        self.pc += 2

    def st(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        address_a = self.registers[reg_a]
        val_b = self.registers[reg_b]
        self.ram[address_a] = val_b
        self.pc += 2

    def call(self):
        return_address = self.pc + 2
        self.registers[self.spl] -= 1
        val = self.registers[self.spl]
        self.ram[val] = return_address

        register_address = self.ram[self.pc + 1]
        subroutine_location = self.registers[register_address]
        self.pc = subroutine_location

    def ret(self):
        return_address = self.ram[self.spl]
        self.registers[self.spl] += 1
        self.pc = return_address

    def jmp(self):
        register_address = self.ram[self.pc + 1]
        subroutine_location = self.registers[register_address]
        self.pc = subroutine_location

    def jeq(self):
        if self.eq:
            register_address = self.ram[self.pc + 1]
            subroutine_location = self.registers[register_address]
            self.pc = subroutine_location
        else:
            self.pc += 2

    def jne(self):
        if not self.eq:
            register_address = self.ram[self.pc + 1]
            subroutine_location = self.registers[register_address]
            self.pc = subroutine_location
        else:
            self.pc += 2

    def comp(self):
        self.alu("CMP", self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3

    def run(self):
        running = True
        while running:
            self.ir = self.ram[self.pc]
            try:
                op = self.OPCODES[self.ir]
                if op == 'LDI':
                    self.ldi()
                elif op == 'PRN':
                    self.prn()
                elif op == 'ADD' or op == 'MUL':
                    self.aluf(op)
                elif op == 'PUSH':
                    self.push()
                elif op == 'POP':
                    self.pop()
                elif op == 'ST':
                    self.st()
                elif op == 'CALL':
                    self.call()
                elif op == 'RET':
                    self.ret()
                elif op == 'JMP':
                    self.jmp()
                elif op == 'JEQ':
                    self.jeq()
                elif op == 'JNE':
                    self.jne()
                elif op == 'CMP':
                    self.comp()
                elif op == 'HLT':
                    running = False
            except KeyError:
                print(f"unknown command {self.ir}")
                self.pc += 1
        pass