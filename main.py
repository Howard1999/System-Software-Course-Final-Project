import sys

from utils.asm import ASM

DEBUG_USE_MASSAGE = False

a = ASM()
try:
	#Setup OP Table
	a.OPTAB_SETUP()
	#Setup Directives Table
	a.DIRECTIVES_SETUP()
	#Read assembly code file
	try:
		file_name = sys.argv[1]
	except:
		file_name = 'sample input.txt'#input('Please input the file path...>')
	a.Load_Instructions(file_name)
	#some handeler
	a.Blocks_Handeler()
	a.Literal_Handeler()
	#Establish Symbol Table
	a.SYMTAB_SETUP_AND_ADDRESS_ASSIGN()
	a.Symbol_Defining_Handeler()
	#generate and print object program
	objprogram = a.Compile('0x1D')
	for x in objprogram['object_program']:
		print(x)
except Exception as e:
	print(e)
	input()

#print debug massage
if DEBUG_USE_MASSAGE:
	print('OPTAB:')
	print(a.OpTable(),'\n')
	
	print('DIRECTIVES:\n',a.Directives(),'\n')
	
	print('ins_list:')
	for x in a.Instruction_List():
		print(x)
	print()
	
	print('start:',hex(a.Program_Start()))
	print('end:',hex(a.Program_End()))
	print('program name:',a.Program_Name(),'\n')
	print('SYMTAB:\n',a.SymbolTable(),'\n')
	print('Literal_Address:\n',a.Literals())
	
	print('ins_list after handeler:')
	for x in a.Instruction_List_After_Handeler():
		print(x)
	print()

input()