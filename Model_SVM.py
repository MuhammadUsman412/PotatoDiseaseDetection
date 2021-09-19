import sys
import os
import itertools
import random
import Image  # PIL
import sqlite3 as lite
from libsvm.svm import svm_problem, svm_parameter
from libsvm.svmutil import *  # libSVM
# import pandas
# from sklearn import model_selection
# from sklearn.linear_model import LogisticRegression
import pickle
# import joblib

# Image data constants
DIMENSION = 32
ROOT_DIR = "images1/"
test_DIR = "imagetotest1/"
EB = "Early_blight"
HEL = "healthy"
LB = "Late_blight"
TC = "To_Check"
CLASSES = [EB, HEL, LB]
CLASSES1 = [TC]
# libsvm constants
LINEAR = 0
RBF = 2

# Other
USE_LINEAR = False
IS_TUNING = False

def main():
    try:
        # train, tune, test = getData(IS_TUNING)
        (train, tune) = modify_getDataTrain(IS_TUNING)
        test = modify_getDataTest(IS_TUNING)
        models = getModels(train)
        # filename = 'finalized_model.sav'
        # pickle.dump(models, open(filename, 'wb'))

        resultstot = None
        if IS_TUNING:
            print ("!!! TUNING MODE !!!")
            resultfinal = classify(models, tune)
        else:
            resultfinal = classify(models, test)
            # print(resultstot)
            # return resultstot

        # print
        # totalCount = 0
        # totalCorrect = 0
        # for clazz in CLASSES1:
        #     count, correct = results[clazz]
        #     totalCount += count
        #     totalCorrect += correct
        #     print ("%s %d %d %f" % (clazz, correct, count, (float(correct) / count)))
        # print ("%s %d %d %f" % ("Overall", totalCorrect, totalCount, (float(totalCorrect) / totalCount)))
        # return resultstot
        return resultfinal

    except Exception as e:
        print (e)
        return 5

def classify(models, dataSet):
    results = []
    resultstot = []
    resultfinal = {}
    ebc = 0
    lbc = 0
    hlc = 0
    # for trueClazz in CLASSES1:
    #     count = 0
    #     correct = 0
    #
    #     for item in dataSet[trueClazz]:
    #         # for trueClazz1 in CLASSES1:
    #             #you can done any type of filter on every image there
    #             predClazz, prob = predict(models, item)
    #             print ("%s,%s,%f,%s" % (trueClazz, predClazz, prob,item))
    #             count += 1
    #             if trueClazz == predClazz: correct += 1
    #     results[trueClazz] = (count, correct)
    count = 0
    correct = 0
    for trueClazz1 in CLASSES1:
        for item in dataSet[trueClazz1]:
            predClazz, prob = predict(models, item)
            print ("%d, %s, %s, %f" % (count, trueClazz1, predClazz, prob))
            if trueClazz1 == predClazz: correct += 1
        # results[trueClazz1] = (count, correct)
            results = [count,trueClazz1,predClazz, prob]
            resultstot = resultstot + results
            # print ("OK")
            count += 1
            if predClazz == 'healthy': hlc += 1
            if predClazz == 'Late_blight': lbc += 1
            if predClazz == 'Early_blight': ebc += 1
    # print  (resultstot)
    print (hlc)
    print(ebc)
    print (lbc)
    print(count)
    hlcf = (hlc/count)*100
    ebcf = (ebc/count)*100
    lbcf = (lbc/count)*100
    print(hlcf)
    print(ebcf)
    print(lbcf)
    prescription = 0
    detail = 0
    if hlcf > 80:
        name = 'Macnozeb'
        prescription = '75%wp in dose of 1.5 kg/ha (1 time a week)'
        detail = 'Potatoes are mostly healthy but some of them is starting to early blight. The fungus Alternaria solani is attacking on fields better way to stat spray as soon as possible '
    elif ebcf > 50:
        name = 'Curzate'
        prescription = '60%DF in dose of 2kg/ha (2 times a week)'
        detail = 'This disease of potato caused by the fungus Alternaria solani. It is found wherever potatoes are grown. The disease primarily affects leaves and stems, but under favorable weather conditions, and if left uncontrolled, can result in considerable defoliation and enhance the chance for tuber infection.'
    elif lbcf >= 50:
        name = 'Matco'
        prescription = '2kg/ha (4 times a week)'
        detail = 'Late blight is caused by the funguslike oomycete pathogen Phytophthora infestans. This potentially devastating disease can infect potato foliage and tubers at any stage of crop development.'
    else:
        name = 'Macnozeb'
        prescription = '80%wp in dose of 1.5 kg/ha (1 time a week)'
        detail = 'Potato fields is affecting from funguslik oomycete pathogen Phytophthora infestans.'

    print(prescription)
    print(detail)
    hlcf = str(hlcf)
    ebcf = str(ebcf)
    lbcf = str(lbcf)
    resultfinal = {"name": name, "prescription": prescription, "detail": detail, "hlcf": hlcf, "ebcf": ebcf, "lbcf": lbcf}
    print(resultfinal)
    # return resultstot
    return resultfinal

def predict(models, item):
    maxProb = 0.0
    bestClass = ""
    for clazz, model in models.items():
        prob = predictSingle(model, item)
        if prob > maxProb:
            maxProb = prob
            bestClass = clazz
    return (bestClass, maxProb)

def predictSingle(model, item):
    output = svm_predict([0], [item], model, "-q -b 1")
    prob = output[2][0][0]
    return prob


def getModels(trainingData):
    models = {}
    param = getParam(USE_LINEAR)
    for c in CLASSES:
        labels, data = getTrainingData(trainingData, c)
        prob = svm_problem(labels, data)
        m = svm_train(prob, param)
        models[c] = m
    return models

def getTrainingData(trainingData, clazz):
    labeledData = getLabeledDataVector(trainingData, clazz, 1)
    negClasses = [c for c in CLASSES if not c == clazz]
    for c in negClasses:
        ld = getLabeledDataVector(trainingData, c, -1)
        labeledData += ld
    random.shuffle(labeledData)
    unzipped = [list(t) for t in zip(*labeledData)]
    labels, data = unzipped if unzipped else ([], [])
    return (labels, data)

def getParam(linear = True):
    param = svm_parameter("-q")
    param.probability = 1
    if(linear):
        param.kernel_type = LINEAR
        param.C = .01
    else:
        param.kernel_type = RBF
        param.C = .01
        param.gamma = .00000001
    return param

def getLabeledDataVector(dataset, clazz, label):
    data = dataset[clazz]
    labels = [label] * len(data)
    output = zip(labels, data)
    return list(output)

def getData(generateTuningData):
    trainingData = {}
    tuneData = {}
    testData = {}

    for clazz in CLASSES:
        (train, tune, test) = buildTrainTestVectors(buildImageList(ROOT_DIR + clazz + "/"), generateTuningData)
        trainingData[clazz] = train
        tuneData[clazz] = tune
        testData[clazz] = test
    for clazz1 in CLASSES1:
        (train, tune, test) = buildTrainTestVectors(buildImageList(ROOT_DIR + clazz1 + "/"), generateTuningData)
        trainingData[clazz1] = train
        tuneData[clazz1] = tune
        testData[clazz1] = test

    return (trainingData, tuneData, testData)
def modify_getDataTrain(generateTuningData):
    trainingData = {}
    tuneData = {}
    testData = {}

    for clazz in CLASSES:
        (train, tune) = buildTrainTestVectors(buildImageList(ROOT_DIR + clazz + "/"), generateTuningData)
        trainingData[clazz] = train
        tuneData[clazz] = tune
        # testData[clazz] = test
    # for clazz1 in CLASSES1:
    #     (train, tune, test) = buildTrainTestVectors(buildImageList(ROOT_DIR + clazz1 + "/"), generateTuningData)
    #     trainingData[clazz1] = train
    #     tuneData[clazz1] = tune
    #     # testData[clazz1] = test

    return (trainingData, tuneData)
def modify_getDataTest(generateTuningData):
    trainingData = {}
    tuneData = {}
    testData = {}

    for clazz in CLASSES1:
        test = buildTrainTestVectors_test(buildImageList(test_DIR + clazz + "/"), generateTuningData)
        # trainingData[clazz] = train
        # tuneData[clazz] = tune
        testData[clazz] = test
    # for clazz1 in CLASSES1:
    #     test = buildTrainTestVectors(buildImageList(ROOT_DIR + clazz1 + "/"), generateTuningData)
    #     # trainingData[clazz1] = train
    #     # tuneData[clazz1] = tune
    #     testData[clazz1] = test

    return (testData)


def buildImageList(dirName):
    imgs = [Image.open(dirName + fileName).resize((DIMENSION, DIMENSION)) for fileName in os.listdir(dirName)]

    imgs = [list(itertools.chain.from_iterable(img.getdata())) for img in imgs]
    return imgs

def buildTrainTestVectors(imgs, generateTuningData):
    # 70% for training, 30% for test.
    testSplit = int(1 * len(imgs))
    baseTraining = imgs[:testSplit]
    test = imgs[testSplit:]

    training = None
    tuning = None
    if generateTuningData:
        # 50% of training for true training, 50% for tuning.
        tuneSplit = int(.5 * len(baseTraining))
        training = baseTraining[:tuneSplit]
        tuning = baseTraining[tuneSplit:]
    else:
        training = baseTraining
    # return (training, tuning, test)
    return (training, tuning)
def buildTrainTestVectors_test(imgs, generateTuningData):
    # 70% for training, 30% for test.
    testSplit = int(1 * len(imgs))
    baseTraining = imgs[:testSplit]
    # test = imgs[testSplit:]

    training = None
    tuning = None
    if generateTuningData:
        # 50% of training for true training, 50% for tuning.
        tuneSplit = int(.5 * len(baseTraining))
        training = baseTraining[:tuneSplit]
        tuning = baseTraining[tuneSplit:]
    else:
        training = baseTraining
    # return (training, tuning, test)
    return (training)

if __name__ == "__main__":
    sys.exit(main())
