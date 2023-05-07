from django.shortcuts import render
import joblib
from textblob import TextBlob
import re
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import numpy as np
import sys
import os
from collections import Counter
from nltk.tokenize import word_tokenize, sent_tokenize
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
import pandas as pd
import json

# Load the model from the static folder
path_to_model = os.path.join(settings.BASE_DIR, './')
loaded_model = joblib.load(open(path_to_model+'review_detector_model.pkl', 'rb'))       


def POS_tagging(Review_text):
  array_Noun = []
  array_Adj = []
  array_Verb = []
  array_Adv = []

  for j in Review_text:
      text = j ;
      filter=re.sub('[^\w\s]', '', text)
      conver_lower=filter.lower()
      Tinput = conver_lower.split(" ")
      
      for i in range(0, len(Tinput)):
          Tinput[i] = "".join(Tinput[i])
      UniqW = Counter(Tinput)
      s = " ".join(UniqW.keys())
      
      tokenized = sent_tokenize(s)
      
      for i in tokenized:
          wordsList = nltk.word_tokenize(i)
          #wordsList = [w for w in wordsList if not w in stop_words]
          
                  
          tagged = nltk.pos_tag(wordsList)
          counts = Counter(tag for word,tag in tagged)

          N = sum([counts[i] for i in counts.keys() if 'NN' in i])
          Adj = sum([counts[i] for i in counts.keys() if 'JJ' in i])
          Verb = sum([counts[i] for i in counts.keys() if 'VB' in i])
          Adv = sum([counts[i] for i in counts.keys() if 'RB' in i])

          array_Noun.append(N)
          array_Adj.append(Adj)
          array_Verb.append(Verb)
          array_Adv.append(Adv)
  return [array_Noun, array_Adj, array_Verb, array_Adv]


def preprocessing(review_text,rating,review_helpful) :
  word_count = len(review_text.split())

  tb = TextBlob(review_text)
  sentiment = (tb.sentiment.polarity)
  subjectivity = (tb.sentiment.subjectivity)

  pos_values = POS_tagging([review_text])
  noun = pos_values[0]
  adjective = pos_values[1]
  verb = pos_values[2]
  adverb = pos_values[3]

  ans = [rating, review_helpful, sentiment, subjectivity, word_count, noun[0], adjective[0], verb[0], adverb[0]]
  return ans


# Create your views here.
@api_view(['GET'])
def index(request):
    return_data = {
        "error_code" : "0",
        "info" : "success",
    }
    return Response(return_data)

@api_view(["POST"])
def detect_review(request):

    try:
        data = json.loads(request.body)
        rev_text_list = request.data['data']['rev_text']
        review_useful_list = request.data['data']['review_useful']
        rating_list = request.data['data']['rating']

        output_arr = []

        for rev_text,rating, review_useful in zip(rev_text_list, review_useful_list, rating_list):
            x = preprocessing(rev_text, rating, review_useful)
            testing = pd.DataFrame(columns=['Rating',	'Review_helpful',	'Sentiment',	'Subjectivity',	'Word_Count',	'Noun_Count',	'Adj_Count',	'Verb_Count',	'Adv_Count'])
            testing.loc[len(testing.index)] = x

            # Make prediction
            review_status = loaded_model.predict(testing)
            output_arr.append(review_status[0])
            # Model confidence score
            # model_confidence_score=  np.max(loaded_model.predict(testing))




        
        

        model_prediction = {
            'info': 'success',
            "Access-Control-Allow-Origin": "https://www.flipkart.com/",
            'review_status': output_arr,
            # 'model_confidence_proba': float("{:.2f}".format(model_confidence_score*100))
        }

    except ValueError as ve:
        model_prediction = {
            'error_code' : '-1',
            "info": str(ve)
        }
    return Response(model_prediction)
    # print("_______________________________________________________________")
    # print(request.GET.get("review_helpful"))
    # print("_______________________________________________________________")