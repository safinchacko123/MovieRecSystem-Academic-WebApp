from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import HttpResponseRedirect
from django.shortcuts import render 
from .forms import InputForm
from .cosineEngine import CosineEngine
import json
import pandas as pd
import json
import redis
from numpy import asarray
from numpy import savetxt
# load numpy array from csv file
from numpy import loadtxt
import pdb
dataFrameFileName = "dataFrame.csv"
similarityFileName = "similarity.csv"


def main_page(request):  
  movie_name=""
  if request.method == "POST":
    form = InputForm(request.POST)
    if form.is_valid():      
      engine_response = [];
      movie_name = form.cleaned_data["movie_name"]
      #remove extra space
      movie_name = " ".join(movie_name.split())
      movie_name = movie_name.lower()
      preLoadedDataFrame = []
      preLoadedSimilarity = []
      isSimilarityPreLoaded = False
      isDataFramePreLoaded = False

      #Note:fresh generation of df and similarity takes 37 sec to show result
      #Note:fresh generating of df file (if similarity file exists) takes : 18 sec to generate df and show result
      if checkDataFrameFileFound():
        preLoadedDataFrame = pd.read_csv(dataFrameFileName)
        isDataFramePreLoaded = True
        if findMovie(preLoadedDataFrame,movie_name) == False:
          return render(request, "searchPage.html", {
                "movie_name": movie_name,"form":form,"similar_movies":[],"disimilar_movies":[],"status":0
            })  
 
      #Note:fresh generating of similarity file (if df file exists) takes : 27 sec to generate similarity and show result
      #Note: Takes oly 7 sec to show result with pre ploaded data using read df and similaity from csv
      if checkSimilarityFileFound():
        isSimilarityPreLoaded = True
        preLoadedSimilarity = (pd.read_csv(similarityFileName)).to_numpy()
      engine_response = CosineEngine.main(movie_name,10,isSimilarityPreLoaded,preLoadedSimilarity,isDataFramePreLoaded,preLoadedDataFrame)

      #poster API
      for index in range(len(engine_response[0]['similar_movies'])):        
            image = CosineEngine.getMovieImages(engine_response[0]['similar_movies'][index]["id"])
            engine_response[0]['similar_movies'][index]["image"] = image
      return render(request, "searchPage.html", {
                "movie_name": movie_name,"form":form,"similar_movies":engine_response[0]['similar_movies'],"status":engine_response[0]['status']
            })
    else:
      movie_name = "error"
      return render(request, "searchPage.html", {
                "movie_name": movie_name,"form":form
            })
  else:   
    form= InputForm()
    return render(request, "searchPage.html", {"form":form, "movie_name": movie_name})     

def checkDataFrameFileFound():
  import os.path            
  dataframe_file_exists = os.path.exists(dataFrameFileName)
  if dataframe_file_exists:
    return True
  else:
    return False

def checkSimilarityFileFound():
  import os.path            
  similarity_file_exists = os.path.exists(similarityFileName)
  if similarity_file_exists:
    return True
  else:
    return False
  
def findMovie(data,movie_name):
    found = False      
    #pdb.set_trace()
    if (data['title'].eq(movie_name)).any():
      found = True
    return found

 

'''
      #trying using session to store similarity data
      if request.session.get('similarity'):
        isSimilarityPreLoaded = True
        preLoadedSimilarity = (pd.read_json(request.session['similarity'])).to_numpy()
      else:
        if checkSimilarityFileFound():          
          request.session['similarity']=(pd.read_csv(similarityFileName)).to_json()
          preLoadedSimilarity = (pd.read_json(request.session['similarity'])).to_numpy()
          isSimilarityPreLoaded = True          
'''