__author__ = 'DM-user'
#coding: utf8
#import pymorphy2_dicts
# pymorphy2_dicts.get_path()

import pymorphy2
import re
import os

morph = pymorphy2.MorphAnalyzer()

def splitbylist (a, splist):
    for i in splist:
        a = re.sub(i, '$$$'+i, a)
    out = a.split('$$$')
    return out

def splittowords (text):
    words = re.findall('\w*', text)
    out = []
    for i in words:
        if i != '':
            out.append(i)
    return out


def returnlemma(word):
    return re.findall('normal_form=\'(\w*)\'',str(morph.parse(word)[0]))[0]

def findPOS(wordsar, POS):
    for i in wordsar:
        if morph.parse(i)[0].tag.POS == POS:
            return i
    return ''

def findpredinclause(clause):
    clwords=  splittowords(clause)
    out = ''
    for i in ['VERB','INFN']:
        out = findPOS(clwords, i)
        if out != '':
            break
    return out

def splitbylist (a, splist):
    for i in splist:
        a = re.sub(i, '$$$'+i, a)
    out = a.split('$$$')
    return out

def splittoclauses(sentence):
    out = splitbylist (sentence, [',',' и ',' - ','\(','\)',':','\.',' или '])
    return out

def findpredintext (text):
    clauses = splittoclauses (text)
    predlist = []
    for i in clauses:
        apd = findpredinclause (i)
        if apd != '':
             predlist.append(apd)
    return predlist

def agreement(verb, noun):
    nounparse = morph.parse(noun)
    verbparse = morph.parse(verb)
    tense = None
    vper = None
    vgen = None
    vnum = None
    for i in verbparse:
        if i.tag.tense != None:
            tense = i.tag.tense
            vper = i.tag.person
            vgen = i.tag.gender
            vnum = i.tag.number
            break
    if tense == 'past':
        for i in nounparse:
            if i.tag.number == vnum and i.tag.gender == vgen and i.tag.tense == None and i.tag.case == 'nomn':
                return 1
    else:
        for i in nounparse:
            if i.tag.number == vnum and i.tag.tense == None and i.tag.case == 'nomn':
                if i.tag.person == vper and vper != '3per':
                    return 1
                elif vper == '3per' and (i.tag.person == None or i.tag.person == vper):
                    return 1
    return 0

def findcasesinclause(clause):
    cases = []
    words = splittowords(clause)
    pred = findpredinclause(clause)
    if pred != '\\.' and pred != '':
        predlemma = morph.parse(pred)[0].normal_form
        for root, dirs, files in os.walk('фреймбанк/verbmodels'):
            if predlemma + '.txt' not in files:
                a = addmodel (morph.parse(pred)[0])
        filein = open ('фреймбанк/verbmodels/' + predlemma +'.txt','r',encoding = 'utf-8')
        modelcases = filein.read().split()
        filein.close()
        for i in range (len(words)):
            curparse = morph.parse(words[i])
            nom = 0
            for j in curparse:
                if j.tag.POS == 'PREP' or j.tag.POS == 'CONJ':
                    break
                if j.tag.case == 'nomn' and agreement(pred, words[i]) == 1 and 'nomn' not in cases:
                    if morph.parse(words[i-1])[0].tag.POS != 'PREP':
                        if morph.parse(words[i-1])[0].tag.POS != 'ADJF' or morph.parse(words[i-2])[0].tag.POS != 'PREP' or i <= 2:
                            cases.append('nomn')
                    break
                if nom == 0:
                    if j.tag.case != None and j.tag.case not in cases and j.tag.case in modelcases and j.tag.case != 'nomn':
                        if morph.parse(words[i-1])[0].tag.POS != 'PREP':
                            if morph.parse(words[i-1])[0].tag.POS != 'ADJF' or morph.parse(words[i-2])[0].tag.POS != 'PREP' or i <= 2:
                                cases.append(j.tag.case)
                        break
    return cases


def checkargumentabsense(clause):
    pred = findpredinclause(clause)
    absentcases = []
    if pred != '\\.' and pred != '':
        predlemma = morph.parse(pred)[0].normal_form
        for root, dirs, files in os.walk('фреймбанк/verbmodels'):
            if predlemma + '.txt' not in files:
                a = addmodel (morph.parse(pred)[0])
        filein = open ('фреймбанк/verbmodels/' + predlemma +'.txt','r',encoding = 'utf-8')
        modelcases = filein.read().split()
        filein.close()
        cases = findcasesinclause(clause)
        for i in modelcases:
            if i not in cases:
                if morph.parse(pred)[0].tag.POS != 'INFN' or i != 'nomn':
                    absentcases.append(i)
    return absentcases

def findbycase (case, clause):
    for j in range(0,6):
        cand = ''
        cPOS = ''
        for i in clause.split():
            if j < len(morph.parse(i)):
                if morph.parse(i)[j].tag.case == case:
                    if cand == '':
                        cand = i
                        cPOS = morph.parse(i)[j].tag.POS
                    elif (morph.parse(i)[j].tag.POS == 'NPRO' or morph.parse(i)[j].tag.POS == 'NOUN') and cPOS != 'NPRO' and cPOS != 'NOUN':
                        cand = i
                        cPOS = morph.parse(i)[j].tag.POS
        if cand != '':
            return cand
    return None

def findnearestclausewin (clauses, num, forgottennums, winrange):
    leftnearestnum = 1000
    rightnearestnum = 1000
    if len (clauses) <= 3:
        if num == 1:
            return 0
        else:
            return 1
    for i in range (0, min(winrange, num+1)):
        if num - i >= 0:
            if num - i not in forgottennums:
                if findpredinclause(clauses[num-i]) != '\\.' and findpredinclause(clauses[num-i]) != '':
                    leftnearestnum = num - i
                    break
    for i in range (0, min(len(clauses) - num, winrange)):
        if num + i not in forgottennums:
            if findpredinclause(clauses[num+i]) != '\\.' and findpredinclause(clauses[num+i]) != '':
                rightnearestnum = num + i
                break
    if abs(rightnearestnum - num) <= abs(leftnearestnum-num):
        return rightnearestnum
    else:
        return leftnearestnum


def findnearestclause (clauses, num, forgottennums):
    leftnearestnum = 1000
    rightnearestnum = 1000
    if len (clauses) <= 3:
        if num == 1:
            return 0
        else:
            return 1
    for i in range (0, num+1):
        if num - i >= 0:
            if num - i not in forgottennums:
                if findpredinclause(clauses[num-i]) != '\\.' and findpredinclause(clauses[num-i]) != '':
                    leftnearestnum = num - i
                    break
    for i in range (0, len(clauses) - num):
        if num + i not in forgottennums:
            if findpredinclause(clauses[num+i]) != '\\.' and findpredinclause(clauses[num+i]) != '':
                rightnearestnum = num + i
                break
    if abs(rightnearestnum - num) <= abs(leftnearestnum-num):
        return rightnearestnum
    else:
        return leftnearestnum

def findabsentcaseinotherclause(clauses,clnum,abscase):
    forgottennums = []
    foundinclause = 'not found'
    while foundinclause == 'not found' and len(forgottennums) != len(clauses)-1:
        if abscase != 'nomn':
            nearestclausenum = findnearestclausewin(clauses,clnum,forgottennums, 2)
        else:
            nearestclausenum = findnearestleftclause (clauses, clnum, forgottennums)
        if nearestclausenum == 1000:
            break
        if abscase in findcasesinclause(clauses[nearestclausenum]):
            if abscase != 'nomn' or agreement(findpredinclause(clauses[clnum]), findbycase(abscase,clauses[nearestclausenum])) != 0:
                foundinclause = nearestclausenum
            else:
                forgottennums.append(nearestclausenum)
        else:
            forgottennums.append(nearestclausenum)
    return foundinclause

def findnearestleftclause (clauses, num, forgottennums):
    leftnearestnum = num-1
    if len (clauses) <= 3:
        if num == 1:
            return 0
        else:
            return 1
    lft = 0
    for i in range (0, num+1):
        if num - i >= 0:
            if num - i not in forgottennums:
                if findpredinclause(clauses[num-i]) != '\\.' and findpredinclause(clauses[num-i]) != '':
                    leftnearestnum = num - i
                    lft = 1
                    break
    if lft == 0:
        rnrstnum = findnearestrightclause(clauses,num,forgottennums)
        if rnrstnum != None:
            return rnrstnum
    return leftnearestnum

def findnearestrightclause(clauses, num, forgottennums):
    rightnearestnum = num+1
    if len (clauses) <= 3:
        if num == 1:
            return 0
        else:
            return 1
    rgt = 0
    for i in range (0, len(clauses)-num):
        if num + i < len(clauses):
            if num + i not in forgottennums:
                if findpredinclause(clauses[num+i]) != '\\.' and findpredinclause(clauses[num+i]) != '':
                    rightnearestnum = num + i
                    rgt = 1
                    break
    if rgt == 0:
        return None
    return rightnearestnum

def checkotherclauses (clauses, givennum):
    clnum = givennum-1
    if len(clauses) <= 2:
        return ['В этом тексте только одна клауза.']
    absent = checkargumentabsense(clauses[clnum])
    if len (absent) == 0:
        return None
    out = []
    for i in absent:
        foundinclause = findabsentcaseinotherclause(clauses,clnum,i)
        if foundinclause != 'not found':
            out.append ('в клаузе' + ' "' + clauses[clnum].strip(',\ .""\?!;-:') + '" ' + ' словоформа в падеже ' + i + ' отсутствует, но соответствующим актантом предиката этой клаузы является словоформа' +' "' + str(findbycase(i,clauses[foundinclause])) + '" ' + 'в клаузе' + ' "' + clauses[foundinclause].strip(', \.""\?!:-;') + ' "')
    return out

def addmodel (verbparsed):
    nf = verbparsed.normal_form
    a = input ('К сожалению, в нашей базе данных нет глагола "' + nf + '".\n Пожалуйста, введите "nomn accs ", если глагол переходный и "nomn ", если он непереходный.\n')
    file  = open('фреймбанк/verbmodels/' + nf + '.txt','w',encoding = 'utf-8')
    file.write(str(a))
    file.close()
    return a

def test():
    filein = open ('test.txt','r',encoding = 'utf-8')
    filetext =filein.read()
    filein.close()
    filetext = filetext.replace(u'\xa0', u' ')
    fcls = filetext.split('\n')
    print (fcls)
    for j in fcls:
        print (j)
        t = splittoclauses(j)
        print (t)
        for k in range(len(splittoclauses(j))):
            curcheck = checkotherclauses(splittoclauses(j), k)
            if curcheck != None:
                for i in checkotherclauses(splittoclauses(j), k):
                        print (i)
        s = input('нажмите enter для продолжения')
    return 0

def testline(line):
    line = line.replace(u'\xa0', u' ')
    s = (splittoclauses(line))
    print (s)
    print (len(s))
    for i in checkotherclauses(s, int(input('clause number'))):
        print (i)
    s = input ('press enter')
    return 0

a = test()
