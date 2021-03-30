# doing necessary imports


from flask import Flask, render_template, request,jsonify
# from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs  # This library is used to beautify the data as the data which we get is not given in proper way
from urllib.request import urlopen as uReq  # This library is used to request the data from the given website url , which is Flipkart
import pymongo

pal = Flask(__name__)  # initialising the flask app with the name 'app'




@pal.route('/',methods=['POST','GET']) # route with allowed methods as POST and GET , Get is used for Url and Post is used for body
def index():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ","") # obtaining the search string entered in the form
        try:
            dbConn = pymongo.MongoClient("mongodb://localhost:27017/")  # opening a connection to Mongo
            db = dbConn['crawlerDB'] # connecting to the database called crawlerDB
            reviews = db[searchString].find({}) # searching the collection with the name same as the keyword
            if reviews.count() > 0: # if there is a collection with searched keyword and it has records in it
                return render_template('results.html',reviews=reviews) # show the results to userx
            else:
                flipkart_url = "https://www.flipkart.com/search?q=" + searchString # preparing the URL to search the product on flipkart
                uClient = uReq(flipkart_url) # requesting the webpage from the internet
                flipkartPage = uClient.read() # reading the webpage
                uClient.close() # closing the connection to the web server
                flipkart_html = bs(flipkartPage, "html.parser") # parsing the webpage as HTML , used to exact information like the title of the page, paragraphs in the page, headings in the page, links, bold text etc.
                bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"}) # seacrhing for appropriate tag to redirect to the product link , This class is used when we inspect the entire whole page
                del bigboxes[0:3] # the first 3 members of the list do not contain relevant information, hence deleting them.
                box = bigboxes[0] #  taking the first iteration (for demo)
                productLink = "https://www.flipkart.com" + box.div.a['href'] # extracting the actual product link / href is a hyper link which is mentioned to evry Product
                prodRes = requests.get(productLink) # getting the product page from server
                prod_html = bs(prodRes.text, "html.parser") # parsing the product page as HTML , we can use "lxml also instead of html.parser
                commentboxes = prod_html.find_all('div', {'class': "_16PBlm"}) # finding the HTML section containing the customer comments . and this class is used when we inspect only a single prdouct of that mai product

                table = db[searchString] # creating a collection with the same name as search string. Tables and Collections are analogous.
                #filename = searchString+".csv" #  filename to save the details
                #fw = open(filename, "w") # creating a local file to save the details
                #headers = "Product, Customer Name, Rating, Heading, Comment \n" # providing the heading of the columns
                #fw.write(headers) # writing first the headers to file
                reviews = [] # initializing an empty list for reviews
                #  iterating over the comment section to get the details of customer and their comments
                for commentbox in commentboxes:
                    try:
                        name = commentbox.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text  # comment k niche comment krne wale ka nam likha hota ha usko inspect kre toh wo ek <p> tag me likhe hoti hai class , so use class ka nam likhna hai hume

                    except:
                        name = 'No Name'

                    try:
                        rating = commentbox.div.text

                    except:
                        rating = 'No Rating'

                    try:
                        commentHead = commentbox.div.p.text
                    except:
                        commentHead = 'No Comment Heading'
                    try:
                        comtag = commentbox.div.find_all('div', {'class': ''})
                        custComment = comtag[0].div.text
                    except:
                        custComment = 'No Customer Comment'
                    #fw.write(searchString+","+name.replace(",", ":")+","+rating + "," + commentHead.replace(",", ":") + "," + custComment.replace(",", ":") + "\n")
                    mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                              "Comment": custComment} # saving that detail to a dictionary
                    x = table.insert_one(mydict) #insertig the dictionary containing the rview comments to the collection
                    reviews.append(mydict) #  appending the comments to the review list
                return render_template('results.html', reviews=reviews) # showing the review to the user
        except:
            return 'something is wrong'
            #return render_template('results.html')
    else:
        return render_template('index.html')
if __name__ == "__main__":
    pal.run(port=8000,debug=True) # running the app on the local machine on port 8000
