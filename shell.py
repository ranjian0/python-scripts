

def shell():

	print("Welcome to Shell")

	while True:
		print(">>", end='')
		entry = input()

		if entry == 'quit':
			break 

		if entry:
			print(entry)


shell()