
from flask import Flask, render_template, request
import os
import re
import random
import string
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB, BernoulliNB, GaussianNB
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
from collections import OrderedDict
import json


def readDataset(dataSetPath, splitPercent):
    files_data = []
    class_labels=[]
    for root, dirs, files in os.walk(dataSetPath):
        for file in files:
            class_labels.append(re.search('(.+?)_.*\.txt', file).group(1))
            files_data.append(open(root + "/" + file, 'r').read())
    n_training=int((len(class_labels)*splitPercent)/100)

    together = list(zip(files_data, class_labels))
    random.shuffle(together)
    files_data[:], class_labels[:] = zip(*together)
    
    training_dataset = files_data[:n_training]
    test_dataset = files_data[n_training:]
    training_labels = class_labels[:n_training]
    test_labels = class_labels[n_training:]
    return training_dataset, test_dataset, training_labels, test_labels

def preprocess(corpus, lower, punc, number):
    preprocessed_corpus=[]
    for i in range(len(corpus)):
        f=corpus[i]
        if lower:
            f=f.lower()
        if punc:
            punc_replace = string.maketrans(string.punctuation, ' '*len(string.punctuation))
            f=f.translate(punc_replace)
            #punc_replace=str.maketrans(string.punctuation, ' '*len(string.punctuation))
            #f=f.translate(punc_replace)
        if number:
            f=f.translate(string.maketrans('', ''), string.digits)
            #remove_digits=str.maketrans('', '', string.digits)
            #f=f.translate(remove_digits)
        f=re.sub('\s+',' ',f)
        preprocessed_corpus.append(f)
    return preprocessed_corpus


def getDocumentTermMatrix(myCorpusTraining, myCorpusTest, style):
    if style == 'count':
        vectorizer1 = CountVectorizer()
        #docterm_matrix_training=(vectorizer1.fit_transform(myCorpusTraining)).toarray()
        docterm_matrix_training=(vectorizer1.fit_transform(myCorpusTraining)).todense()        
        docterm_matrix_test=(vectorizer1.transform(myCorpusTest)).todense()
    elif style == 'tf_idf':
        vectorizer2 = TfidfVectorizer()
        docterm_matrix_training=(vectorizer2.fit_transform(myCorpusTraining)).todense()
        docterm_matrix_test=(vectorizer2.transform(myCorpusTest)).todense()

    return docterm_matrix_training, docterm_matrix_test

def trainModel(documentTermMatrix, trainLabels, classifierName, bonus_options):
    if classifierName == 'SVM':
        if not bonus_options[0] and not bonus_options[1]:
            clf=svm.SVC()
        elif bonus_options[0] and not bonus_options[1]:
            clf=svm.SVC(C=float(bonus_options[0]))
        elif not bonus_options[0] and bonus_options[1]:
            clf=svm.SVC(kernel=bonus_options[1])
        elif bonus_options[0] and bonus_options[1]:
            clf=svm.SVC(C=float(bonus_options[0]), kernel=bonus_options[1])
        clf=clf.fit(documentTermMatrix, trainLabels)
    
    elif classifierName == 'Naive bayes':
        if not bonus_options[3]:
            if bonus_options[2]:
                clf=MultinomialNB(alpha=float(bonus_options[2])).fit(documentTermMatrix, trainLabels)
            elif not bonus_options[2]:
                clf=MultinomialNB().fit(documentTermMatrix, trainLabels)
        
        elif bonus_options[3]:
            if bonus_options[3] == 'GaussianNB':
                clf=GaussianNB().fit(documentTermMatrix, trainLabels)
            elif bonus_options[3] == 'MultinomialNB':
                if bonus_options[2]:
                    clf=MultinomialNB(alpha=float(bonus_options[2])).fit(documentTermMatrix, trainLabels)
                elif not bonus_options[2]:
                    clf=MultinomialNB().fit(documentTermMatrix, trainLabels)
            elif bonus_options[3] == 'BernoulliNB':
                if bonus_options[2]:
                    clf=BernoulliNB(alpha=float(bonus_options[2])).fit(documentTermMatrix, trainLabels)
                elif not bonus_options[2]:
                    clf=BernoulliNB().fit(documentTermMatrix, trainLabels)
    
    elif classifierName == 'Multi-layer Perceptron':
        if not bonus_options[4] and not bonus_options[5]:
            clf=MLPClassifier()
        elif bonus_options[4] and not bonus_options[5]:
            clf=MLPClassifier(hidden_layer_sizes=(int(bonus_options[4]), int(bonus_options[4]), int(bonus_options[4])))
        elif not bonus_options[4] and bonus_options[5]:
            clf=MLPClassifier(activation=bonus_options[5])
        elif bonus_options[4] and bonus_options[5]:
            clf=MLPClassifier(hidden_layer_sizes=(int(bonus_options[4]), int(bonus_options[4]), int(bonus_options[4])), activation=bonus_options[5])
        clf=clf.fit(documentTermMatrix, trainLabels)
    
    elif classifierName == 'Random Forest':
        if not bonus_options[6] and not bonus_options[7]:
            clf=RandomForestClassifier()
        elif bonus_options[6] and not bonus_options[7]:
            clf=RandomForestClassifier(n_estimators=int(bonus_options[6]))
        elif not bonus_options[6] and bonus_options[7]:
            clf=RandomForestClassifier(criterion=str(bonus_options[7]))
        elif bonus_options[6] and bonus_options[7]:
            clf=RandomForestClassifier(n_estimators=int(bonus_options[6]), criterion=str(bonus_options[7]))
        clf=clf.fit(documentTermMatrix, trainLabels)
    
    elif classifierName == 'Decision Tree':
        if not bonus_options[8] and not bonus_options[9]:
            clf=tree.DecisionTreeClassifier()
        elif bonus_options[8] and not bonus_options[9]:
            clf=tree.DecisionTreeClassifier(splitter=str(bonus_options[8]))
        elif not bonus_options[8] and bonus_options[9]:
            clf=tree.DecisionTreeClassifier(criterion=str(bonus_options[9]))
        elif bonus_options[8] and bonus_options[9]:
            clf=tree.DecisionTreeClassifier(criterion=str(bonus_options[9]), splitter=str(bonus_options[8]))
        clf=clf.fit(documentTermMatrix, trainLabels)

    return clf

def getLabels(documentTermMatrix, classifierName, trainedModel):
    predicted_labels=trainedModel.predict(documentTermMatrix)
    return predicted_labels

def evaluate(true_label, predict_label):
    accuracy=accuracy_score(true_label, predict_label)
    return accuracy

def all_func(splitPercent, lower, punc, number, style, classifierName, bonus_options):
    dataSetPath="/media/lakshay/A052AD7452AD5038/MS Dal/Fall 2017-18/Visual Analytics/A2/classification"
    training_dataset, test_dataset, training_labels, test_labels = readDataset(dataSetPath, splitPercent)
    training_dataset = preprocess(training_dataset, lower, punc, number)
    test_dataset = preprocess(test_dataset, lower, punc, number)
    docterm_matrix_training, docterm_matrix_test = getDocumentTermMatrix(training_dataset, test_dataset, style)
    clf=trainModel(docterm_matrix_training, training_labels, classifierName, bonus_options)
    predicted_labels=getLabels(docterm_matrix_test, classifierName, clf)
    accuracy=evaluate(test_labels, predicted_labels)
    return accuracy

app = Flask(__name__)

global splitPercent, lower, punc, number, style
splitPercent=0
lower=0
punc=0
number=0
style=0
global json_data
json_data=[]
global legenddata
legenddata=0
global options_data
options_data=[]
global options_values
options_values=[]

def pass_data(splitper, lwr, pun, num, styl, bonus_options):
    lower=False
    punc=False
    number=False
    splitPercent = splitper
    if lwr is not None:
        lower=lwr
    if pun is not None:
        punc=pun
    if num is not None:
        number=num
    if styl is not None:
        style=styl
    
    if splitPercent != None and lower != None and  punc != None and  number != None and style != None:
        splitPercent=int(splitPercent)
        classifiers_list=['SVM', 'Naive bayes', 'Multi-layer Perceptron', 'Random Forest', 'Decision Tree']
        accuracy=[]
        for j in range(len(classifiers_list)):
            accuracy.append(all_func(splitPercent, lower, punc, number, style, classifiers_list[j], bonus_options))
        dictionary=OrderedDict(zip(classifiers_list, accuracy))    
        lower= json.dumps(dictionary)
        lower=str(lower)
    
    return lower

def pass_data_options(splitper, lwr, pun, num, styl):
    lower=False
    punc=False
    number=False
    splitPercent = splitper
    if lwr is not None:
        lower=lwr
    if pun is not None:
        punc=pun
    if num is not None:
        number=num
    if styl is not None:
        style=styl
    
    if splitPercent != None and lower != None and  punc != None and  number != None and style != None:
        splitPercent=int(splitPercent)
    
    options_list=['SplitPerc', 'Lower', 'Punc', 'Num', 'Style']
    if splitper!=None and splitper!= False and styl!=None and styl!= False:
        if lwr is None:
            lwr="False"
        if pun is None:
            pun="False"
        if num is None:
            num="False"
        options_values=[splitper, lwr, pun, num, styl]
        lower=OrderedDict(zip(options_list, options_values))
        lower= json.dumps(lower)
        lower=str(lower)
    
    return lower

@app.route('/',methods = ['POST', 'GET'])
def get_form_data():
    
    splitper=request.form.get('splitPercent')
    lwr=request.form.get('lower')
    pun=request.form.get('punc')
    num=request.form.get('number')
    styl=request.form.get('style')
    bonus_options=[0,0,0,0,0,0,0,0,0,0]
    bonus_options[0]=request.form.get('penalty')
    bonus_options[1]=request.form.get('kernel')
    bonus_options[2]=request.form.get('smoothing')
    bonus_options[3]=request.form.get('nbtype')
    bonus_options[4]=request.form.get('neurons')
    bonus_options[5]=request.form.get('activation')
    bonus_options[6]=request.form.get('trees')
    bonus_options[7]=request.form.get('criterion')
    bonus_options[8]=request.form.get('splitter')
    bonus_options[9]=request.form.get('dtcriterion')
    
    lower=pass_data(splitper, lwr, pun, num, styl, bonus_options)
    if lower!=None and lower!= False:
        json_data.append(lower)
    
    lower=pass_data_options(splitper, lwr, pun, num, styl)
    if lower!=None and lower!= False:
        options_data.append(lower)

    return render_template('a2.html', value=json_data, value1=options_data, value2=bonus_options)

if __name__ == "__main__":
    app.run(debug=True)

# http://127.0.0.1:5000/

