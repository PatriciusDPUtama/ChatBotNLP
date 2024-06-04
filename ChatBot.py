# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import nltk
import spacy
import sys
import mysql.connector
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def takeQuestionWord(question):
    question_arr=['what','where','why','who','when','how']
    comp = ['many','much']
    question_word =""
    tokens = nltk.word_tokenize(question.lower())
    for word in tokens:
        if word in question_arr:
            question_word = word.capitalize()
        else:
            sys.exit("Your format is wrong. Please start with 5W + 1H.")
        if question_word == "How":
            if word.lower() in comp:
                question_word += " " + str(word.lower())
                break
            
        elif question_word != "How" and question_word != "":
            break
    return question_word

def keywordExtract(question):
    arr_pos = ['NOUN','PROPN','VERB','ADV']
    keyword = []
    doc = nlp(question)
    for word in doc:
        if word.is_stop is False and word.pos_ in arr_pos:
            keyword.append(word.lemma_)
    
    return keyword
    

def select(questionWord,keyword):
    cursor = mydb.cursor()
    array_answer = []
    array_keyword = []
    words = ""
    
    for w in keyword:
        words += w + "; "
    
    if words == "":
        words = "; "
        
    sql = "SELECT answer,keyword FROM question WHERE question_word = %s AND keyword LIKE %s"
    cursor.execute(sql,(questionWord,'%'+words+'%'))
    rows = cursor.fetchall()

    if(len(rows)==1):
        return rows[0][0]
    elif(len(rows)==0):
        if(len(keyword)==1):
            return "No Answer"
        elif(len(keyword)==2):
            unigrams = ""
            x = 1
            for w in keyword:
                unigrams += "keyword LIKE '%" + w + ";%'"
                if(x < len(keyword)):
                    unigrams += " OR "
                    x+=1
            
            sql2 = "SELECT answer,keyword FROM question WHERE question_word = '" + questionWord  + "' AND " + unigrams
            cursor.execute(sql2)
            rowsuni = cursor.fetchall()
            
            if(len(rowsuni)==1):
                return rowsuni[0][0]
            elif(len(rowsuni)==0):
                return "No Answer"
            else:
                for row in rowsuni:
                    array_answer.append(row[0])
                    array_keyword.append(row[1])
                return similarity(array_answer,array_keyword,words)
            
        elif(len(keyword)==3):
            unigrams = ""
            bigrams = ""
            keybefore = ""
            x = 1
            y = 1
            for w in keyword:
                unigrams += "keyword LIKE '%" + w + ";%'"
                if(x < len(keyword)):
                    unigrams += " OR "
                    x+=1
                    
            for w in keyword:
                
                if(w==keyword[0]):
                    keybefore = w
                    continue
                
                else:
                    bigrams += "keyword LIKE '%" + keybefore + "; " + w + ";%'"
                    keybefore = w
                    if( y < len(keyword)-1):
                        bigrams += " OR "
                        y+=1
                       
            sql3 = "SELECT answer,keyword FROM question WHERE question_word = '" + questionWord  + "' AND " + unigrams + " OR " + bigrams
            cursor.execute(sql3)
            rowsunibi = cursor.fetchall()
            
            if(len(rowsunibi)==1):
                return rowsunibi[0][0]
            elif(len(rowsunibi)==0):
                return "No Answer"
            else:
                for row in rowsunibi:
                    array_answer.append(row[0])
                    array_keyword.append(row[1])
                return similarity(array_answer,array_keyword,words)
        
        else:
            unigrams = ""
            bigrams = ""
            trigrams = ""
            
            keybefore = ""
            keybefore2 = ""
            
            x = 1
            y = 1
            z = 1
            
            for w in keyword:
                unigrams += "keyword LIKE '%" + w + ";%'"
                if(x < len(keyword)):
                    unigrams += " OR "
                    x+=1
                 
            for w in keyword:
                if(w==keyword[0]):
                    keybefore = w
                    continue
                
                else:
                    bigrams += "keyword LIKE '%" + keybefore + "; " + w + ";%'"
                    keybefore = w
                    if( y < len(keyword)-1):
                        bigrams += " OR "
                        y+=1
                        
            for w in keyword :
                if(w==keyword[0]):
                    keybefore = w
                    continue
                elif(w==keyword[1]):
                    keybefore2 = keybefore
                    keybefore = w
                    continue
                
                else:
                    trigrams += "keyword LIKE '%" + keybefore2 + "; " + keybefore + "; " + w + ";%'"
                    keybefore2 = keybefore
                    keybefore = w
                    
                    if( z < len(keyword)-2):
                        trigrams += " OR "
                        z+=1
            
            sql4 = "SELECT answer,keyword FROM question WHERE question_word = '" + questionWord  + "' AND " + unigrams + " OR " + bigrams + " OR " + trigrams
            cursor.execute(sql4)
            rowsunibitri = cursor.fetchall()
            
            if(len(rowsunibitri)==1):
                return rowsunibitri[0][0]
            elif(len(rowsunibitri)==0):
                return "No Answer"
            else:
                for row in rowsunibitri:
                    array_answer.append(row[0])
                    array_keyword.append(row[1])
                return similarity(array_answer,array_keyword,words)
    else:
        for row in rows:
            array_answer.append(row[0])
            array_keyword.append(row[1])
        return similarity(array_answer,array_keyword,words)

def similarity(array_answer,array_keyword,words):
    idx = i = sim = 0
    for key in array_keyword:
        tfidf = TfidfVectorizer()
        vector = tfidf.fit_transform([words,key])
        cos = cosine_similarity(vector)
        res = cos[0][1]
        if sim < res:
            sim = res
            idx = 1
        i+=1
    
    if(sim > 0.5):
        return array_answer[idx]
    else :
        idx = i = sim = 0
        for ans in array_answer:
            tfidf = TfidfVectorizer()
            vector = tfidf.fit_transform([words,ans])
            cos = cosine_similarity(vector)
            res = cos[0][1]
            if sim < res:
                sim = res
                idx = 1
                i+=1
        if(sim>0.5):
            return array_answer[idx]
        else:
            return "No Answer"
        

nltk.download('punkt')
nlp = spacy.load('en_core_web_sm')
mydb = mysql.connector.connect(host="localhost",user="root",password="",database="chatbot")

questions = input("Input your questions: ")
questionWord = takeQuestionWord(questions)
keyword = keywordExtract(questions)

print(questionWord)
print(keyword,'\n')
print(select(questionWord,keyword))

mydb.close()