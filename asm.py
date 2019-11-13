import sys

#op(6) nixbpe dsip(12)
if __name__=='__main__':
	#read OP table file
	op = open('opcode', 'r')
	if not op:
		print("opcode file is lost...>")
	else:
		return
	#read file
	try:
		file_name = sys.argv[1]
	except:
		file_name = input('Please input the file path...>')

	file = open(file_name, 'r')
	if not file:
		print("input file desn't exsist")
	else:
		return
	#handle input
	ins = file.readlines()
	OPTAB = {code.split()[0]:int(code.split()[1],16) for code in op.readlines()}
	print(ins)
	print(OPTAB)