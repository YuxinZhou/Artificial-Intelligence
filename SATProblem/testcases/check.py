import os
i = 26
while i <= 100:
	print("--Test Case #{0}--".format(i))
	os.system('cp ./input{0}.txt input.txt'.format(i))
	os.system('python ./hw2cs561s2017.py')
	print("")
	# os.system('diff ./output.txt output{0}.txt'.format(i))
	i = i+1

os.system('rm input.txt output.txt')