# -*- coding: UTF-8 -*-
import sys
import codecs
from collections import defaultdict
import json
import re

def hasNumbers(inputString):
	return any(char.isdigit() for char in inputString)


def getTransitionsProb(transitionTable,transit_to,transit_from):
	transitionDict=transitionTable.get(transit_from)
	return float(transitionDict.get(transit_to))

def get_buffer_tups(current):
	temp={}
	bufferTups=[]
	for tup in current:
		if tup[2] not in temp:
			templist=[]
			templist.append(tup)
			temp[tup[2]]=templist
		else:
			templist=temp.get(tup[2])
			templist.append(tup)
			temp[tup[2]]=templist
	for key in temp:
		list_tups=temp.get(key)
		maxIncomingTup=max(list_tups,key=lambda x:x[3])
		bufferTups.append(maxIncomingTup)
	return bufferTups

def getTaggedList(viterbiProbs,word,first_original_word):
	status='FindMax'
	finalseq=[]
	last_seq=viterbiProbs.get(word)
	#print last_seq
	maxTup=max(last_seq,key=lambda x:x[3])
	#print maxTup
	backTrack=maxTup[0]
	backTag=maxTup[1]
	original_word=maxTup[4]
	#print original_word
	#finalseq.append(maxTup[2])
	slash="/"
	output=first_original_word+slash+maxTup[2]
	finalseq.append(output)


	while(True):
		available_seqs=viterbiProbs.get(backTrack)
		#print available_seqs
		if backTag=='q0':
			break
		for tupFound in available_seqs:
			if tupFound[2]==backTag:
				output=original_word+slash+tupFound[2]
				backTrack=tupFound[0]
				backTag=tupFound[1]
				original_word=tupFound[4]
				finalseq.append(output)
				break
	return finalseq




def run_viterbi(test,transitionTable,tagWordTable):
	testWords=test.split(' ')
	#print "Inside Viterbi"
	#print len(testWords)
	count=0
	viterbiProbs={}
	buffer_tuples=[]
	prev_word=None
	original_word=None
	while (count < len(testWords)):
		if count == 0: 
			word=testWords[count].decode('utf-8')
			prev_word=word
			word_exists_training=False
			current=[] #############current
			for key in tagWordTable:
				keyDict=tagWordTable.get(key)
				if  word in keyDict:
					word_exists_training=True
					emissionProb=keyDict.get(word)
					transitionProb=getTransitionsProb(transitionTable,key,"q0")
					tup=('Start','q0',key,float(emissionProb+transitionProb),'Start')
					buffer_tuples.append(tup)
					current.append(tup) #########current
			viterbiProbs[word]=buffer_tuples

			## If first test word is not in training set
			if (word_exists_training==False):
				transitions=transitionTable.get(key)
				for transit_to in transitions:
					if transit_to != 'q0':
						nextTag=transit_to
						transitionProb=getTransitionsProb(transitionTable,transit_to,"q0")
						tup=('Start','q0',nextTag,float(transitionProb),'Start')    ## tup=("Previous Word Name", "Current State","Next State","Current -> Next State Transition Probabiity")
						current.append(tup)
						buffer_tuples.append(tup)
				viterbiProbs[word]=buffer_tuples
			original_word=word



        # Words other than first word
		else:
			word=testWords[count].decode('utf-8')
			already_existed=False
			if word in viterbiProbs:
				newword=word+str(len(viterbiProbs.keys()))
				already_existed=True
			word_exists_training=False
			current=[]
			for key in tagWordTable:
				keyDict=tagWordTable.get(key)
				if  word in keyDict:
					word_exists_training=True
					emissionProb=keyDict.get(word)
					## making current list from buffer
					for buffer_tup in buffer_tuples:
						prev=buffer_tup[2]
						transitionProb=getTransitionsProb(transitionTable,key,prev)
						current_tup=(prev_word,buffer_tup[2],key,float(buffer_tup[3]+emissionProb+transitionProb),original_word)
						current.append(current_tup)

			if (word_exists_training==False):
				transitions=transitionTable.get(key)
				for buffer_tup in buffer_tuples:
					for transit_to in transitions:
						nextTag=transit_to
						transitionProb=getTransitionsProb(transitionTable,transit_to,buffer_tup[2])
						tup=(prev_word,buffer_tup[2],nextTag,float(buffer_tup[3]+transitionProb),original_word)    ## tup=("Previous Word Name", "Current State","Next State","Current -> Next State Transition Probabiity")
						current.append(tup)

			buffer_tuples=get_buffer_tups(current)
			prev_word=word
			if already_existed== True:
				prev_word=newword
			viterbiProbs[prev_word]=buffer_tuples
			original_word=word	

		count+=1



	finalseq=getTaggedList(viterbiProbs,prev_word,original_word)
	return finalseq





s=sys.argv
#model_file=codecs.open(s[1],'r',encoding='utf-8')
model_file=open("hmmmodel.txt","r")
model_dict=json.loads(model_file.read())
out_file=codecs.open("hmmoutput.txt","w","utf-8")
#print "printing"
tag_word_count=model_dict.get("Tag_Word_Count") ## Obtaining Tag Word Count table
transition_table=model_dict.get("Transitions")  ## Obtaining Transition Table

test_file=open(s[1],"r")
while True:
	first_line=test_file.readline()
	#print first_line
	if (""==first_line):
		break
	first_line=first_line.rstrip()
	dev_data_split=first_line.split(' ')
	result = run_viterbi(first_line,transition_table,tag_word_count)
	#print "Printing result"
	#print result
	length=len(result)
	current=length-1
	while(current>=0):
		out_file.write(result[current])
		if current != 0:
			out_file.write(" ")
		current=current-1
	out_file.write('\n')











































