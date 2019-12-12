import sys

from utils.asm import ASM

DEBUG_USE_MASSAGE = True

a = ASM()
a.Turn_On_Debug()
#Setup OP Table
a.OPTAB_SETUP()
#Setup Directives Table
a.DIRECTIVES_SETUP()
#Read assembly code file
try:
	file_name = sys.argv[1]
except:
	file_name = 'test.txt'#input('Please input the file path...>')
a.Load_Instructions(file_name)
#some handeler
a.Blocks_Handeler()
a.Literal_Handeler()
#Establish Symbol Table
a.SYMTAB_SETUP_AND_ADDRESS_ASSIGN()
a.Symbol_Defining_Handeler()
#generate and print object program
objprogram = a.Compile('0x1D')
print()
for x in objprogram['object_program']:
	print(x)