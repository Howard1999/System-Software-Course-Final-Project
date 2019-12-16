import sys

from utils.asm import ASM

DEBUG_USE_MASSAGE = True

try:
	a = ASM()
	a.Turn_On_Debug()
	#Setup OP Table
	a.OPTAB_SETUP()
	input('Press Enter To Continue...>')
	#Setup Directives Table
	a.DIRECTIVES_SETUP()
	input('Press Enter To Continue...>')
	#Read assembly code file
	try:
		file_name = sys.argv[1]
	except:
		file_name = 'sample input.txt'#input('Please input the file path...>')
	a.Load_Instructions(file_name)
	input('Press Enter To Continue...>')
	#some handler
	a.Blocks_Handler()
	input('Press Enter To Continue...>')
	a.Literal_Handler()
	input('Press Enter To Continue...>')
	#Establish Symbol Table
	a.SYMTAB_SETUP_AND_ADDRESS_ASSIGN()
	input('Press Enter To Continue...>')
	a.Symbol_Defining_Handler()
	input('Press Enter To Continue...>')
	#generate and print object program
	objprogram = a.Compile('0x1D')
	print()
	for x in objprogram['object_program']:
		print(x)
	input('Press Enter To Continue...>')
except Exception as e:
	print(e)