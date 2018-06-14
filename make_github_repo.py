#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  make_repo.py
#  
#  Copyright 2018 Ian Ichung'wa Karanj <karanjaichungwa@gmail.com>
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
import sys
from getpass import getpass
try:
	import github
	from github import Github
except ImportError:
	print("Please install pygithub!")
	sys.exit()

def main():
	username = input("Enter github username : ")
	password = getpass("Enter github password: ")
	repo_name = input("Name of repository: ")

	try:
		g = Github(username, password)
		user = g.get_user()
		repo = user.create_repo(repo_name)
	except github.BadCredentialsException:
		print("Invalid credentials. Try again\n")
		return

	print("Created github repository at : ")
	print(repo.clone_url)

if __name__ == '__main__':
    import sys
    sys.exit(main())
