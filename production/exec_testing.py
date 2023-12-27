
import sys
import os
import time
import subprocess
#sys.path.append('../')  # Go up two folders to the project root


#from tests.Compression_Tests import Compression


def list_files(folder_path):
	file_dir_name = []
	file_names= []
	for root, dirs, files in os.walk(folder_path):
			for file in files:
				if file.endswith(".py"):
					file_dir_name.append(os.path.join(root))
					#os.path.join(root, file)
					file_names.append(file)
	return file_dir_name,file_names




def main():
	
	print("\n\n")
	print("*************************************")
	print("*                                   *")
	print("*  Testing: all python scripts      *")
	print("*                                   *")
	print("*************************************")
	print("\n")
	
	folder_path="tests"
	directories,files = list_files(folder_path)

	if not files:
		print(f"No files found in the folder '{folder_path}'.")
	else:
		print(f"List of files in the folder '{folder_path}':")
		for file in files:
			print(file)
	
	original_working_directory = os.getcwd()
	
	passed=0
	total=len(directories)
	for folder,file in zip(directories,files):
		print("\n\n")
		print("START TESTING OF: "+str(folder+file))
		try:
			os.chdir(folder)
			#sys.path.append('tests/structures')
			subprocess.run(['pytest', file], check=True)
			passed+=1
		except subprocess.CalledProcessError as e:
			print(f"Error running the script: {e}")
		os.chdir(original_working_directory)
	
	print("\n\n")
	
	print ("PASSED: "+str(passed)+"/"+str(total))

	print("\n\n")
	print("*************************************")
	print("*                                   *")
	print("*          END Testing              *")
	print("*                                   *")
	print("*************************************")
	print("\n")

if __name__ == "__main__":
    main()