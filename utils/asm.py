import re

def MyHex(i, j=6):
	t = hex(i).replace('0x','')
	if len(t) < j:
		t = ''.join(['0' for x in range(j-len(t))])+t
	elif len(t) > j:
		raise Exception('overflow')
	return t.upper()

class Instruction():
	def __init__(self, line):
		s = line[0]
		line = line.replace(', ',',')
		line = line.replace(' ,',',')
		line = line.split()
		if len(line) == 2:
			if s=='\t' or s==' ':
				line.insert(0,'')
			else:
				line.insert(2,'')
		elif len(line) == 1:
			line.insert(0,'')
			line.insert(2,'')
		line.insert(3,None)
		self.ins = line
	def __str__(self):
		l = self.Label()
		o = self.Oprate()
		p = self.Param()
		if len(l) < 7:
			l = l + ''.join([' ' for x in range(7-len(l))])
		if len(o) < 7:
			o = o + ''.join([' ' for x in range(7-len(o))])
		if len(p) < 7:
			p = p + ''.join([' ' for x in range(7-len(p))])
		return 'Label: \''+l+'\'  Oprate:\''+o+'\'  Param:\''+p+'\''
	def Label(self):
		return self.ins[0]
	def Oprate(self):
		return self.ins[1]
	def Param(self):
		return self.ins[2]
	def Address(self):
		return self.ins[3]
	def Set_Address(self, addr):
		self.ins.insert(3, addr)
class	OPtable():
	def __init__(self, list=[]):
		try:
			self.OPTAB = {code.split()[0]:[int(code.split()[1],16),int(code.split()[2])] for code in list}
		except:
			self.OPTAB = {}
			raise Exception('input format error')
	def __str__(self):
		return '\n'.join([x+' '+hex(self.OPTAB[x][0])+' '+str(self.OPTAB[x][1]) for x in self.OPTAB])
	def Is_in_OPtable(self, op):
		return op in self.OPTAB
	def Format_Search(self, op):
		return self.OPTAB[op][1]
	def HexCode_Search(self, op):
		return hex(self.OPTAB[op][0])
	def CodeValue_Search(self, op):
		return self.OPTAB[op][0]
class ASM():
	def __init__(self):
		self.attribute ={
			'name': None,
			'start': None,
			'end': None
		}
		self.DIRECTIVES ={}
		self.OPTAB = OPtable()
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
		self.ins_list = []
		self.objcode = []
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
	def Program_Name(self):
		return self.attribute['name']
	def RESET(self):
		self.__init__()
	def Set_Start_Address(self):
		for x in self.ins_list:
			if x.Oprate() == 'START':
				self.attribute['start'] = int(x.Param())
		if self.attribute['start'] == None:
			raise Exception('without start directives')
	def Set_Program_Name(self):
		for x in self.ins_list:
			if x.Oprate() == 'START':
				self.attribute['name'] = x.Label()
		if self.attribute['name'] == None:
			raise Exception('without start directives')
	def OPTAB_SETUP(self, file_name = 'utils/opcode'):
		try:
			f = open(file_name, 'r')
			self.OPTAB = OPtable(f.readlines())
			f.close()
		except Exception as e:
			raise e
	def SYMTAB_SETUP_AND_ADDRESS_ASSIGN(self):
		self.Set_Start_Address()
		self.Set_Program_Name()
		PC = self.attribute['start']
		for ins in self.ins_list:
		#setting address
			ins.Set_Address(PC)
		#put into Symbol table
			sym = ins.Label()
			if sym != '':
				if sym in self.SYMTAB:
					raise Exception('Duplicate definition')
				self.SYMTAB[sym] = PC
		#calculate Address of next instruction
			if ins.Oprate() == 'BYTE':
				t = ins.Param()[0]
				if t == 'X':
					PC += (len(ins.Param()[1:].replace("'",''))+1)//2
				elif t == 'C':
					PC += len(ins.Param()[1:].replace("'",''))
				else:
					t = hex(int(ins.Param))
					t.replace('0x','')
					PC += (len(t)+1)//2
			elif ins.Oprate() == 'WORD':
				PC += 3
			elif ins.Oprate() == 'RESB':
				PC += int(ins.Param())
			elif ins.Oprate() == 'RESW':
				PC += int(ins.Param())*3
			elif ins.Oprate() == 'END':
				self.attribute['end'] = PC
			else:
				s = ins.Oprate().replace('+','')
				if self.OPTAB.Is_in_OPtable(s):
					s_size = self.OPTAB.Format_Search(s)
					if (s_size) ==3 and ('+' in ins.Oprate()):
						s_size = 4
					PC += s_size
		if self.attribute['end'] == None:
			self.attribute['end'] = PC
	def DIRECTIVES_SETUP(self, file_name = 'utils/directives'):
		try:
			f = open(file_name, 'r')
			self.DIRECTIVES = {word.replace('\n','') for word in f.readlines()}
			f.close()
		except Exception as e:
			raise e
	def Load_Instructions(self, file_name):
		try:
			f = open(file_name,'r')
			for x in f.readlines():
				if x.split()!=[]:
					self.ins_list.append(Instruction(x))
			f.close()
		except Exception as e:
			raise e
	def Compile(self):
		#h record
		h = 'H'+'˰'+self.Program_Name()+'˰'+MyHex(self.Program_Start())+'˰'+MyHex(self.Program_End())
		#t record
		t_list = []
		t = ''#'T'+'˰'+'''start addr'''+'˰'+'''length'''+'˰'+'''entity'''
		start = None
		length = 0##upper bound 0xFF
		upper_bound = '0xFF'
		entity = ''
		for ins in self.ins_list:
			if t == '':
				t = 'T'+'˰'
			op = ins.Oprate().replace('+','')
			par = ins.Param()
			addr = ins.Address()
			BASE = 0
			if self.OPTAB.Is_in_OPtable(op):#oprate
				if start == None:
					start = addr
				fmt = self.OPTAB.Format_Search(op)
				if fmt == 1:
					length += fmt
					entity = entity + MyHex(self.OPTAB.CodeValue_Search(op),2) + '˰'
				elif fmt == 2:
					if length+fmt > int(upper_bound,16):#check if beyond bound or not
						#cut t record
						t = t + MyHex(start) + '˰' + MyHex(length,2) + '˰' + entity
						t_list.append(t)
						#start a new t record
						t = 'T'+'˰'
						start = addr
						length = 0
						entity = ''
					par = par.split(',')
					par.append('A')
					r1 = par[0]
					r2 = par[1]
					length += fmt
					entity = entity + MyHex(self.OPTAB.CodeValue_Search(op),2) + MyHex(self.SYMTAB[r1],1) + MyHex(self.SYMTAB[r2],1) + '˰'
				elif fmt == 3:
					n = '@' in par
					i = '#' in par
					x = ',X' in par
					e = '+' in ins.Oprate()
					b = None
					p = None
					if e:
						fmt = 4
					if length+fmt > int(upper_bound,16):#check if beyond bound or not
						#cut t record
						t = t + MyHex(start) + '˰' + MyHex(length,2) + '˰' + entity
						t_list.append(t)
						#start a new t record
						t = 'T'+'˰'
						start = addr
						length = 0
						entity = ''
					length += fmt
					#handle parameter
					par = par.replace('@','')
					par = par.replace('#','')
					par = par.replace(',X','')
					disp = None
					disp4 = None
					if par == '':#without parameter
						b = False
						p = False
						disp = 0
						disp4 = 0
					elif par in self.SYMTAB or not i:#Label and address
						if par in self.SYMTAB:
							laddr = self.SYMTAB[par]
						else:
							try:
								laddr = int(par)
							except:
								raise Exception('Parameter parsing error')
						r = laddr-(addr+fmt)
						br = laddr-BASE
						if i:#immediate
							b = False
							p = False
							if fmt == 3:
								disp = laddr
							elif fmt == 4:
								disp4 = laddr
						elif fmt == 3 and not i:#disp
							if -2048<=r and r<=2047:#with (PC)+disp
								b = False
								p = True
								disp = r
							elif 0<=br and br<=4065:#with (BASE)+disp
								b = True
								p = False
								disp = br
							else:
								raise Exception('Symbol can\'t reach')
						elif fmt == 4:#address
							b = False
							p = False
							disp4 = laddr
					else:#immediate data
						if i:
							b = False
							p = False
							disp = int(par)
							disp4 = int(par)
					cdv = self.OPTAB.CodeValue_Search(op)
					if not n and not i:#simple
						n = True
						i = True
					if n:
						cdv += 2
					if i:
						cdv += 1
					if x:
						cdv = (cdv<<1)+1
					else:
						cdv = cdv<<1
					if b:
						cdv = (cdv<<1)+1
					else:
						cdv = cdv<<1
					if p:
						cdv = (cdv<<1)+1
					else:
						cdv = cdv<<1
					if e:
						cdv = (cdv<<1)+1
					else:
						cdv = cdv<<1
					if fmt == 3:
						cdv = (cdv << 12) + disp
						cdv = MyHex(cdv, 6)
					elif fmt == 4:
						cdv = (cdv << 20) + disp4
						cdv = MyHex(cdv, 8)
					
					entity = entity + cdv + '˰'
			elif op in self.DIRECTIVES:#directives
				if op == 'START':
					pass
				elif op == 'END':
					pass
				elif op == 'BYTE':
					if par[0] == 'C':
						ct=par.replace("'",'')[1:]
						s=''
						for c in ct:
							s+=MyHex(ord(c),2)
						if length+len(ct) > int(upper_bound,16):#check if beyond bound or not
							#cut t record
							t = t + MyHex(start) + '˰' + MyHex(length,2) + '˰' + entity
							t_list.append(t)
							#start a new t record
							t = 'T'+'˰'
							start = addr
							length = 0
							entity = ''
						length += len(ct)
						entity = entity + s +'˰'
					elif par[0] == 'X':
						xt=par.replace("'",'')[1:]
						loft=(len(xt)+1)//2
						v=int(xt,16)
						if length+loft > int(upper_bound,16):#check if beyond bound or not
							#cut t record
							t = t + MyHex(start) + '˰' + MyHex(length,2) + '˰' + entity
							t_list.append(t)
							#start a new t record
							t = 'T'+'˰'
							start = addr
							length = 0
							entity = ''
						length += loft
						entity = entity + MyHex(v,loft*2) + '˰'
					else:
						it=hex(int(par)).replace('0x','')
						it=(len(it)+1)//2
						if length+t > int(upper_bound,16):#check if beyond bound or not
							#cut t record
							t = t + MyHex(start) + '˰' + MyHex(length,2) + '˰' + entity
							t_list.append(t)
							#start a new t record
							t = 'T'+'˰'
							start = addr
							length = 0
							entity = ''
						length += it
						entity = entity + MyHex(int(par),it) + '˰'
				elif op == 'WORD':
					if length+3 > int(upper_bound,16):#check if beyond bound or not
							#cut t record
							t = t + MyHex(start) + '˰' + MyHex(length,2) + '˰' + entity
							t_list.append(t)
							#start a new t record
							t = 'T'+'˰'
							start = addr
							length = 0
							entity = ''
					length+=3
					entity = entity + MyHex(int(par)) + '˰'
				elif op == 'RESB' or op == 'RESW':
					if start != None:#in t record
						#cut record
						t = t + MyHex(start) + '˰' + MyHex(length,2) + '˰' + entity
						t_list.append(t)
						t = 'T'+'˰'
						start = None
						length = 0
						entity = ''
				elif op == 'BASE':
					BASE = self.SYMTAB[par]
			else:#worng input
				raise Exception('instruction parsing error')
		t = t + MyHex(start) + '˰' + MyHex(length,2) + '˰' + entity
		t_list.append(t)
		#e record
		e = 'E'+'˰'+MyHex(self.Program_Start())
		
		t_list.insert(0,h)
		t_list.append(e)
		return t_list