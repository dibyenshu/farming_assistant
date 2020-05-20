import pickle

def predict(tp):
   
    filename = 'finalized_model.pkl'
    clf = pickle.load(open(filename,'rb'))
    #tp=[50,50,34,100]#input

    #humidity-0 temp-1 rainfall-3 
    atemp=tp[0]
    ah=tp[1]
    rain=tp[2]

    crop={1:'mungBean',2:'tea',3:'maize',4:'millet',5:'rice',6:'wheat'}
    l=[]
    l.append(atemp)
    l.append(ah)
    l.append(rain)
    predictcrop=[l]

    #Predicting the crop
    predictions = clf.predict(predictcrop)
    n=predictions[0]
    return crop[n]