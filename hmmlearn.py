# -*- coding: UTF-8 -*-
import sys
import json
import codecs
import itertools
from collections import defaultdict
import math
def obtain_tags_wordcnt_transcnt(text_file):
	
	tagCount=defaultdict(int)
	tagWordCount=defaultdict(lambda:{})
	transitionsCount=defaultdict(lambda:{})
	start="q0"
	global length
	length=0
	entireTags=[]
	tagsandtransitions=[]
	for line in text_file:
		length+=1
		line=line.rstrip()
		wordList=line.split(" ")
		tagSeq=[]
		tagSeq.append(start)
		for word in wordList:
			tag=word[-2:]
			##Updating tag word count freq
			token=word[:-3]
			wordcount={}
			if tag not in tagWordCount:
				wordcount={}
				wordcount[token]=1
				tagWordCount[tag]=wordcount
			else:
				wordcount=tagWordCount.get(tag)
				if token not in wordcount:
					wordcount[token]=1
					tagWordCount[tag]=wordcount
				else:
					tokencnt=wordcount.get(token)
					tokencnt+=1
					wordcount[token]=tokencnt
					tagWordCount[tag]=wordcount
			###Updating tag count ends

			tagSeq.append(tag)
			if tag not in tagCount:
				tagCount[tag]=1
			else:
				count=tagCount.get(tag)
				count+=1
				tagCount[tag]=count
		entireTags.append(tagSeq)
	for row in range(0,len(entireTags)):
		## 14 = len(entireTags[row])
		for col in range(0,len(entireTags[row])):
			if col < len(entireTags[row])-1:
				t=entireTags[row][col]
				if t not in transitionsCount:
					transitionDict={}
					nextTag=entireTags[row][col+1]
					transitionDict[nextTag]=1
					transitionsCount[t]=transitionDict
				else:
					transitionDict = transitionsCount.get(t)
    				nextTag=entireTags[row][col+1]
    				if nextTag not in transitionDict:
    					transitionDict[nextTag]=1
    					transitionsCount[t]=transitionDict
    				else:
    					count = transitionDict[nextTag]
    					count= count+1
    					transitionDict[nextTag]=count
    					transitionsCount[t]=transitionDict
	#print transitionsCount
	tagsandtransitions.append(tagCount)
	tagsandtransitions.append(transitionsCount)
	tagsandtransitions.append(tagWordCount)
	#print tagWordCount
	return tagsandtransitions



def create_transition_table(tags,transitions):
	#print tags
	transitionProb={}
	transitions
	for subseq in itertools.product(tags.keys(),repeat=2):
		tag=subseq[0]
		if tag in transitions:
			tag_dict=transitions.get(tag)
			if subseq[1] in tag_dict:
				num = tag_dict.get(subseq[1]) + 1
				value=math.log(float(num)/(int(tags.get(subseq[0]))+len(tags.keys())+1))
				transitionProb[subseq]=value
			else:
				value=math.log(float(1)/(int(tags.get(subseq[0]))+len(tags.keys())+1))
				transitionProb[subseq]=value

	for t in tags.keys():
		q0=u"q0"
		subseq = (q0,t)
		tag=subseq[0]
		if tag in transitions:
			tag_dict=transitions.get(tag)
			if subseq[1] in tag_dict:
				num = tag_dict.get(subseq[1]) + 1
				value=math.log(float(num)/(length+len(tags.keys())+1))
				transitionProb[subseq]=value
			else:
				value=math.log(float(1)/(length+len(tags.keys())+1))
				transitionProb[subseq]=value
	return transitionProb

def create_tag_word_count(tags,tagWordCount):
	for tag in tagWordCount:
		completeCount=tags.get(tag)
		word_cnt=tagWordCount.get(tag)
		for word in word_cnt:
			wcount=word_cnt.get(word)
			word_cnt[word]=math.log(float(wcount)/completeCount)
		tagWordCount[tag]=word_cnt
	return tagWordCount
   
s=sys.argv
text_file=codecs.open(s[1], 'r', encoding='utf-8')
out_file=codecs.open("hmmmodel.txt", 'w', encoding='utf-8')
copy=text_file
tags_transitions=obtain_tags_wordcnt_transcnt(text_file)
tags=tags_transitions[0]
transitions=tags_transitions[1]
tagWordCount=tags_transitions[2]
transition_table=create_transition_table(tags,transitions)
tag_word_count_table=create_tag_word_count(tags,tagWordCount)

## create transition dictionary
transitionDict={}
for key in transition_table:
	if key[0] not in transitionDict:
		inner_transitions={}
		inner_transitions[key[1]]=float(transition_table.get(key))
		transitionDict[key[0]]=inner_transitions
	else:
		inner_transitions=transitionDict.get(key[0])
		inner_transitions[key[1]]=float(transition_table.get(key))
		transitionDict[key[0]]=inner_transitions

model_output={"Transitions":transitionDict,"Tag_Word_Count":tag_word_count_table}
#print model_output
json.dump(model_output,out_file,ensure_ascii=False)


