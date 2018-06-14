import random
import pkgutil

LICENSE = """
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  {filename}
#  
#  Copyright 2018 Ian Ichung'wa Karanja <karanjaichungwa@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
"""

DIV = """
'''
============================================================
---   {title}
============================================================
'''
"""

MAIN_STUB = """
if __name__ == '__main__':
	main()
"""

FUNCTION_STUB = """
def {func_name}():
	{code}
"""

CLASS_STUB = """
class {cname}:
	{methods}
"""

class CodeGen:
	
	def __init__(self, num_lines, file):
		self.num_lines = num_lines
		self.file = file
		
		# -- modules
		self.pymodules = [m.name for m in pkgutil.iter_modules() 
							if not m.name.startswith('_')]
		
	def generate(self):
		self.file.write(LICENSE.format(filename=self.file.name))
		
		# -- create imports
		self.generate_imports(random.randint(2, 10))
		
		self.file.write(DIV.format(title="DRIVER FUNCTION"))
		# -- create main
		self.generate_main(random.randint(5, 50))
		
		# -- create program logic
		# -# functions
		self.file.write(DIV.format(title="UTILS"))
		for _ in range(random.randint(5, 15)):
			self.generate_function(random.randint(5, 50))
			
		# -# classes
		self.file.write(DIV.format(title="CLASSES"))
		for _ in range(random.randint(1, 10)):
			self.generate_class(random.randint(25, 150))
		
		# -- create main stub
		self.generate_main_stub()
	
	def generate_imports(self, num_lines):
		""" Create import lines {only from python standard lib}"""
		libs = sorted(random.sample(self.pymodules, num_lines), key=lambda l : len(l))
		for lib in libs:
			self.file.write(f"import {lib} \n")
			
	def generate_main(self, num_lines):
		self.file.write(FUNCTION_STUB.format(
			func_name="main", code="print('hello world')"))
		
	def generate_main_stub(self):
		self.file.write(MAIN_STUB)
		
	def generate_class(self, num_lines):
		pass
		
	def generate_function(self, num_lines):
		pass
		
	def generate_ifblock(num_lines):
		pass
		
	def generate_forblock(num_lines):
		pass
		
	def generate_whileblock(num_lines):
		pass
		
	def generate_variable_context():
		pass

with open("_test/complex_lib.py", 'w') as _file:
	c = CodeGen(10, _file)
	c.generate()

