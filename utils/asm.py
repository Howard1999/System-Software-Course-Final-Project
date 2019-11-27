class Instruction():
	def __init__(self, line):
		line = line.replace(', ',',')
		line = line.replace(' ,',',')
		line = line.split()
		if len(line) == 2:
			line.insert(0,'')
		elif len(line) == 1:
			line.insert(0,'')
			line.insert(2,'')
		self.ins = line
	def __str__(self):
		return 'Label: \''+self.Label()+'\'  Oprate: \''+self.Oprate()+'\'  Param :\''+self.Param()+'\''
	def Label(self):
		return self.ins[0]
	def Oprate(self):
		return self.ins[1]
	def Param(self):
		return self.ins[2]
	
class ASM():
	def __init__(self):
		self.attribute ={
			'start': None,
			'end': None
		}
		self.DIRECTIVES ={}
		self.OPTAB = {}
		self.SYMTAB = {
			'A':0,
			'X':1,
			'L':2,
			'B':3,
			'S':4,
			'T':5,
			'F':6,
			'PC':8,
			'SW':9,
		}
		self.ins_list =[]
	def OpTable(self):
		return self.OPTAB
	def SymbolTable(self):
		return self.SYMTAB
	def Directives(self):
		return self.DIRECTIVES
	def Program_Start(self):
		return self.attribute['start']
	def Program_End(self):
		return self.attribute['end']
	def Instruction_List(self):
		return self.ins_list
	def RESET(self):
		self.__init__()
	def OPTAB_SETUP(self, file_name = 'utils/opcode'):
		try:
			f = open(file_name, 'r')
		except:
			return False
		self.OPTAB = {code.split()[0]:[int(code.split()[1],16),int(code.split()[2])] for code in f.readlines()}
		f.close()
		return True
	def SYMTAB_SETUP(self):
		self.attribute['start'] = int(self.ins_list[0].Param())
		PC = self.attribute['start']
		for ins in self.ins_list:
		#put into Symbol table
			sym = ins.Label()
			if sym != '':
				if sym in self.SYMTAB:
					return False
				self.SYMTAB[sym] = PC
		#calculate Address of next instruction
			if ins.Oprate() == 'BYTE':
				t = ins.Param()[0]
				if t == 'X':
					PC += (len(ins.Param()[1:].replace("'",''))+1)//2
				elif t == 'C':
					PC += len(ins.Param()[1:].replace("'",''))
			elif ins.Oprate() == 'WORD':
				PC += 3
			elif ins.Oprate() == 'RESB':
				PC += int(ins.Param())
			elif ins.Oprate() == 'RESW':
				PC += int(ins.Param())*3
			else:
				s = ins.Oprate().replace('+','')
				if s in self.OPTAB:
					s_size = self.OPTAB[s][1]
					if (s_size) ==3 and ('+' in ins.Oprate()):
						s_size = 4
					PC += s_size
		self.attribute['end'] = PC
		return True
	def DIRECTIVES_SETUP(self, file_name = 'utils/directives'):
		try:
			f = open(file_name, 'r')
		except:
			return False
		self.DIRECTIVES = {word.replace('\n','') for word in f.readlines()}
		f.close()
		return True
	def Load_Instructions(self, file_name):
		try:
			f = open(file_name,'r')
		except:
			return False
		for x in f.readlines():
			if x.split()!=[]:
				self.ins_list.append(Instruction(x))
		f.close()
		return True
