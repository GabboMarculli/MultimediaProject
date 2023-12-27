
import sys
import time
sys.path.append('../')  # Go up two folders to the project root

from pre_processing.Decompress_collection import Collection_Reader
from building_data_structures.IndexBuilder import IndexBuilder
from utilities.General_Utilities import get_available_memory,get_memory_in_GB


tot_doc=[
    "0     The pen is on the table",
    "1     The day is very sunny",
    "2     Goodmoring new article",
    "3     A cat is faster then a dog",
    "4     How are you",
    "5     A boy is a man with low age",
    "6     Lake Ontario is one of the biggest lake in the world",
    "7     English is worst than Italian",
    "8     Spiderman is the best superhero in Marvel universe",
    "9     Last night I saw a Netflix series",
    "10    A penny for your thoughts",
    "11    Actions speak louder than words",
    "12    All that glitters is not gold",
    "13    Beauty is in the eye of the beholder",
    "14    Birds of a feather flock together",
    "15    Cleanliness is next to godliness",
    "16    Don't count your chickens before they hatch",
    "17    Every people cloud has a silver lining people",
    "18    Fool me once shame on you fool me twice shame on me",
    "19    Honesty is the best policy.",
    "20    If the shoe fits, wear it",
    "21    It's a piece of cake",
    "22    Jump on the bandwagon",
    "23    Keep your chin up",
    "24    Let the cat out of the bag",
    "25    Make a long story short",
    "26    Necessity is the mother of invention",
    "27    Once in a blue moon",
    "28    Practice makes perfect",
    "29    Read between the lines",
    "30    The early bird catches people the worm",
    "31    The pen is mightier than the sword",
    "32    There's no smoke without fire",
    "33    To each his own",
    "34    Two heads are better than one",
    "35    You can't have your cake and eat it too",
    "36    A watched pot never boils",
    "37    Beggars can't be choosers",
    "38    Better late than never",
    "39    Calm before the storm",
    "40    Curiosity killed the cat",
    "41    Every dog has its day",
    "42    Great minds think alike",
    "43    Hope for the best prepare for the worst",
    "44    Ignorance is bliss.",
    "45    It's the last straw that breaks the camel's back",
    "46    Laugh and the world laughs with you weep and you weep alone",
    "47    Money can't buy happiness",
    "48    No news is good news",
    "49    Out of sight out of mind",
    "50    People who live in glass houses shouldn't throw stones",
    "51    Rome wasn't built in a day",
    "52    Silence is golden",
    "53    The apple doesn't fall far from the tree",
    "54    The more, the merrier",
    "55    There's no place like home",
    "56    Two wrongs don't make a right",
    "57    When in Rome do as the Romans do",
    "58    You reap what you sow",
    "59    People people people"
]





def main():
	
	print("\n\n")
	print("*************************************")
	print("*                                   *")
	print("*  Indexing: build data structures  *")
	print("*                                   *")
	print("*************************************")
	print("\n")
	
	tot_available=get_available_memory()
	
	print("\n")
	
	while True:
		try:
			mem_perc=input("Insert % of RAM to use to store partial structure information (default 20%): ")
			
			#Handling default value	
			if(mem_perc.strip()==""):
				mem_perc=20
		
			mem_perc = float(mem_perc)
			
			if (mem_perc<=0 or mem_perc>100):
				continue
			break  # The input is correct
		except ValueError:
			continue
	
	mem_used_for_partial_storage=((mem_perc*tot_available)/100)
	print ("Memory used for partial storage information: "+get_memory_in_GB(mem_used_for_partial_storage))
	
	while True:
		try:
			max_no_doc=input("MAX No. of document to extract from the collection at time default(100000):")
			
			#Handling default value	
			if(max_no_doc.strip()==""):
				max_no_doc=100000

			max_no_doc = int(max_no_doc)
			if (max_no_doc<=0):
				continue
			break  # The input is correct
		except ValueError:
			continue
			
	while True:
		try:
			no_processes=input("No. of processes to use for pre-processing documents (default 10):")
			
			#Handling default value
			if(no_processes.strip()==""):
				no_processes=10
				
			no_processes = int(no_processes)
			if (max_no_doc<=0):
				continue
			break  # The input is correct
		except ValueError:
			continue
			
	while True:
		try:
			steam_stop=input("Use steamming and stop word removal (y/n) (default 'y'):")
			
			#Handling default value
			if(steam_stop.strip()==""):
				steam_stop='y'
			
			if (steam_stop.lower()!='y' and steam_stop.lower()!='n'):
				continue
				
			if(steam_stop.lower()=='y'):
				steam_stop=True
			else:
				steam_stop=False
			
			break  # The input is correct
		except ValueError:
			continue
	
	while True:
		try:
			compression_mode=input("Use compression (y/n): (default 'y')")
			
			#Handling default value
			if(compression_mode.strip()==""):
				compression_mode='y'
			
			if (compression_mode.lower()!='y' and compression_mode.lower()!='n'):
				continue
				
			if(compression_mode.lower()=='y'):
				compression_mode=True
			else:
				compression_mode=False
			break  # The input is correct
		except ValueError:
			continue
			
	while True:
		try:
			debug_mode=input("Debug mode (y/n): (default 'y')")
			
			#Handling default value
			if(debug_mode.strip()==""):
				debug_mode='y'
			
			if (debug_mode.lower()!='y' and debug_mode.lower()!='n'):
				continue
				
			if(debug_mode.lower()=='y'):
				debug_mode=True
			else:
				debug_mode=False
			break  # The input is correct
		except ValueError:
			continue
	
	print("\n")
	print("RECAP")
	print ("Memory used for partial storage information: "+get_memory_in_GB(mem_used_for_partial_storage))
	
	
	indexBuilder=IndexBuilder(debug_mode,compression_mode,Collection_Reader("./collection.tar.gz",max_no_doc,no_processes,steam_stop,True))
	
	input("Press something to START the INDEXING")
	
	start_process=time.time()
	
	start_spmi = time.time()
	print ("SPIMI start")
	indexBuilder.single_pass_in_memory_indexing(mem_used_for_partial_storage)
	
	print ("SPIMI end")
	end_spmi = time.time()
	print ("Tot Time spent in SPMI: "+str(end_spmi-start_spmi))
	
	print ("MERGING start")
	start_merging = time.time()
	
	indexBuilder.index_merging()
	
	end_merging = time.time()
	print ("MERGING end")
	
	end_process=time.time()
	
	print ("Tot Time spent : "+str(end_process-start_process))
	
	
	
	
	
	
	
	
	
	print("End!")

if __name__ == "__main__":
    main()