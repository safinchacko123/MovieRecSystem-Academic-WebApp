import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import ast
import nltk
from nltk.stem.porter import PorterStemmer
import json
import pdb
import json
import redis
from numpy import asarray
from numpy import savetxt
# load numpy array from csv file
from numpy import loadtxt
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

tmdb_img_base_url ="https://image.tmdb.org/t/p/w500/"
tmdb_api_base_url = "https://api.themoviedb.org/3/movie/"
tmdb_api_key = "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyYmQxYzcyNjU1Njk1NWJiMzc3ZDZmMzZkODVlNzE5YyIsInN1YiI6IjY1MjcyNzZmY2VkYWM0MDEzZmFiZGM0OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.Y2vzDZSmDKOvNYCwwG5nDSbGWjaZgSg-jIxp1mIRwNY"
dataFrameFileName = "dataFrame.csv"
similarityFileName = "similarity.csv"

class CosineEngine:
    data_frame = pd.DataFrame()
    similarity =[]
    preLoadedDataFrame = []
    inputMovieName = ''
    isSimilarityPreLoaded = False
    isDataFramePreLoaded = False
    
    def main(movie_name,count,isSimilarityPreLoaded,preLoadedSimilarity,isDataFramePreLoaded,preLoadedDataFrame):
        CosineEngine.inputMovieName = movie_name        
        CosineEngine.isSimilarityPreLoaded = isSimilarityPreLoaded
        CosineEngine.similarity = preLoadedSimilarity
        CosineEngine.isDataFramePreLoaded = isDataFramePreLoaded
        CosineEngine.data_frame = preLoadedDataFrame

        #pdb.set_trace()
        return CosineEngine.run(count)           
        
    def generateDataFrame():        
        movies = pd.read_csv('static/dataset/tmdb_5000_movies.csv')
        credits = pd.read_csv('static/dataset/tmdb_5000_credits.csv')
        #movies.head()
        #credits.head()
        movies = movies.merge(credits,on='title')
        #movies.head(1)
        movies['original_language'].value_counts()
        movies = movies[['genres','id','keywords','title','overview','cast','crew']]
        #movies.isnull().sum()
        movies.dropna(inplace=True)
        #movies.isnull().sum()
        #movies.duplicated().sum()
        #movies.iloc[0].genres     

        #set all film name to lower case to match with user entry
        movies['title'] = movies['title'].apply(lambda x:x.lower()) 
        #pdb.set_trace() 

        #Convert String to List
        def convert(obj):
            L = []
            for i in ast.literal_eval(obj):
                L.append(i['name'])
            return L    

        movies['genres'] = movies['genres'].apply(convert)
        #movies.iloc[0].keywords
        movies['keywords'] = movies['keywords'].apply(convert)
        #movies['cast'][0]

        #from cast, we are using only first four actor/actress
        def convert3(obj):
            L = []
            ct = 0
            for i in ast.literal_eval(obj):
                if ct!=4:
                    L.append(i['name'])
                    ct = ct+1
                else:
                    break
            return L
        
        movies['cast'] = movies['cast'].apply(convert3)
        #pdb.set_trace()
        #movies['crew'][0]
        

        #From the crew, we are using director only
        def fetch_director(obj):
            L = []
            for i in ast.literal_eval(obj):
                if i['job']=='Director':
                    L.append(i['name'])
                    break
            return L
        
        movies['crew'] = movies['crew'].apply(fetch_director)
        #movies.head()
        # Converting overview (string) into List Remove spaces
        movies['overview'] = movies['overview'].apply(lambda x:x.split())
        # Removing spaces between words
        movies['genres'] = movies['genres'].apply(lambda x: [i.replace(" ","") for i in x])
        movies['keywords'] = movies['keywords'].apply(lambda x: [i.replace(" ","") for i in x])
        movies['cast'] = movies['cast'].apply(lambda x: [i.replace(" ","") for i in x])
        movies['crew'] = movies['crew'].apply(lambda x: [i.replace(" ","") for i in x])
        #movies.head()
        movies['tags'] = (movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']).apply(lambda x:" ".join(x))
            
        #Select the relevant columns
        CosineEngine.data_frame = movies[['id','title','tags']]        
        #data_frame['tags'][0]
        #data_frame.head()
       
        
        # Use stem to remove ing,er of words and producing morphological variants of a root/base word
        ps = PorterStemmer()        
        def stem(text):
            y = []    
            # Converting string into list    
            for i in text.split():
                y.append(ps.stem(i))        
            # Again converting list into string
            return " ".join(y)        
        
        #suppres SettingWithCopyWarning in Pandas
        CosineEngine.data_frame = CosineEngine.data_frame.iloc[:]
        CosineEngine.data_frame['tags'] = CosineEngine.data_frame["tags"].apply(lambda x:" ".join(x.split()))
        # Convert all in lower case
        CosineEngine.data_frame['tags'] = CosineEngine.data_frame['tags'].apply(lambda x:x.lower())
        #data_frame['tags'][0]
        CosineEngine.data_frame['tags'] = CosineEngine.data_frame["tags"].apply(lambda x: stem(x))
        #data_frame['tags'][0]           
        CosineEngine.saveDataFrameToFile(dataFrameFileName)   
        return CosineEngine.data_frame   


    def generateSimilarity():        
        cv = CountVectorizer(max_features=5000, stop_words='english')
        #pdb.set_trace();
        vectors = cv.fit_transform((CosineEngine.data_frame['tags'])).toarray()
        vectors.shape
        #vectors[0]
        #cv.get_feature_names_out()
        #stem('Captain Barbossa, long believed to be dead, has come back to life and is headed to the edge of the Earth with Will Turner and Elizabeth Swann. But nothing is quite as it seems.')           
        #cosine_similarity(vectors).shape
        CosineEngine.similarity = cosine_similarity(vectors) 
        CosineEngine.saveSimilarityToFile(similarityFileName)
        #similarity.shape        
        return CosineEngine.similarity

        
         
         #save data to file
    def saveDataFrameToFile(filename):
        CosineEngine.data_frame.to_csv(filename, sep=',', index=False, encoding='utf-8')
        return 1
    
        #save cosine similarity to file
        #similarity is a numpy array as default
    def saveSimilarityToFile(filename):
        #convert numpy arrray to data frame
        similarity_df = pd.DataFrame(CosineEngine.similarity)
        (similarity_df).to_csv(filename, sep=',', index=False, encoding='utf-8')
        return 1
           
       
    #recommend fntn
    def recommend(count):
        movie_index = CosineEngine.data_frame[CosineEngine.data_frame['title'] == CosineEngine.inputMovieName].index[0]            
        distances = CosineEngine.similarity[movie_index]
        similar_movies = sorted(list(enumerate(distances)),reverse=True,key=lambda x:x[1])[1:count+1]
        #pdb.set_trace()
        #return movies_list
        return_list = [{'status':1,'similar_movies':[],'disimilar_movies':[]}]       
        movies = [];
        for i in similar_movies:
            movies.append({'title':CosineEngine.data_frame.iloc[i[0]].title,'id':CosineEngine.data_frame.iloc[i[0]].id})
        return_list[0]['similar_movies'] = movies
        return return_list
        
        
        #main
    
    def run(count):
        if CosineEngine.isDataFramePreLoaded == False:
            CosineEngine.data_frame = CosineEngine.generateDataFrame()
            if CosineEngine.findMovie() == False:
                return [{'status':0,'similar_movies':[],'disimilar_movies':[]}]
        if CosineEngine.isSimilarityPreLoaded == False:
            CosineEngine.similarity = CosineEngine.generateSimilarity()
        return CosineEngine.recommend(count)            
            
        
    #api to get images
    def getMovieImages(id):
        import requests
        url = tmdb_api_base_url+str(id)+"/images"
        headers = {
        "accept": "application/json",
        "Authorization": tmdb_api_key
        }
        response = requests.get(url, headers=headers)
        json_response = json.loads(response.text)
        if not json_response['posters']:
            return "http://127.0.0.1:8000/static/assets/img/logo.jpg"
        else:
            return tmdb_img_base_url+json_response['posters'][0]['file_path']
       
    #function to check the user search string found in Db
    def findMovie():
        found = False      
        #pdb.set_trace()  
        if (CosineEngine.data_frame['title'].eq(CosineEngine.inputMovieName)).any():
            found = True
        return found