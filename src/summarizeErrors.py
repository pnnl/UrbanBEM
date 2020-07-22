import os

os.chdir('../ep_input/stderr')

errorDict = {}

for filename in os.listdir():
	with open(filename, 'r') as file:
		content = file.read()
		if content not in errorDict:
			errorDict[content] = [filename]
		else:
			errorDict[content].append(filename)

errorDict.pop('')

outFile = open('../errorSummary.txt', 'w')

for error in errorDict:
	outFile.write(f'{errorDict[error]}\n\n{error}\n')

outFile.close()

