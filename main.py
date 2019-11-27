import sys

from utils.asm import ASM
#op(6) nixbpe dsip(12)
a = ASM()
#Setup OP Table
if not a.OPTAB_SETUP():
	input('Op code file is LOST or NOT EXSIST...>')
	quit()
print('OPTAB:',a.OpTable(),'\n')
#Setup Reserve Word Table
if not a.DIRECTIVES_SETUP():
	input('Reserve word file is LOST or NOT EXSIST...>')
	quit()
print('DIRECTIVES:',a.Directives(),'\n')
#Read assembly code file
try:
	file_name = sys.argv[1]
except:
	file_name = '新文字文件.txt'#input('Please input the file path...>')
if not a.Load_Instructions(file_name):
	input('The file is NOT EXSIST...>')
	quit()
print('ins_list:')
for x in a.Instruction_List():
	print(x)
print()
#Handle input
if a.SYMTAB_SETUP():
	print('start:',hex(a.Program_Start()))
	print('end:',hex(a.Program_End()),'\n')
	print('SYMTAB:',a.SymbolTable())

input()
	