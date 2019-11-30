import sys

from utils.asm import ASM
#op(6) nixbpe dsip(12)
a = ASM()
#Setup OP Table
try:
	a.OPTAB_SETUP()
except Exception as e:
	print(e)
	input()
	quit()
print('OPTAB:')
print(a.OpTable(),'\n')
#Setup Directives Table
try:
	a.DIRECTIVES_SETUP()
except Exception as e:
	print(e)
	input()
	quit()
print('DIRECTIVES:\n',a.Directives(),'\n')
#Read assembly code file
try:
	file_name = sys.argv[1]
except:
	file_name = '標準版.txt'#input('Please input the file path...>')
try:
	a.Load_Instructions(file_name)
except Exception as e:
	print(e)
	input()
	quit()
print('ins_list:')
for x in a.Instruction_List():
	print(x)
print()
#Establish Symbol Table
try:
	a.SYMTAB_SETUP_AND_ADDRESS_ASSIGN()
except Exception as e:
	print(e)
	input()
	quit()
print('start:',hex(a.Program_Start()))
print('end:',hex(a.Program_End()),'\n')
print('SYMTAB:\n',a.SymbolTable())
#generate object code
for r in a.Compile():
	print(r)

input()
	