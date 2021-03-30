from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs  # this library is used to Beautify your data as we dont get data in a proper way 
from urllib.request import urlopen as uReq # This library is used to request the data from the Given Url Which is Flipkart

app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()  # wheneever we Try to Deploy something on a Server , so the Server will be Avaliable in SOme other Location(USA) , and we will be Trying to hit that URL From other Location (Hindi) , so it allows us to communicate with outside Servers
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI   , Get is used for URL and POst is used for Body
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","") # replace means dekho search page pr maine likha iphone      mobile ,tph ye dono k bich me jo gap hai na usko replace kete hai
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"}) # this class is used when we Inspct entire page
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.a['href'] # href is a hyper link means assume as a id , where each products has the id so it is accessed by this href
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"}) # This Class is used when we Inspect one specific product 

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    name = 'No Name'

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text


                except:
                    rating = 'No Rating'

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ",e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
	app.run(debug=True)




# payle terminal me heroku login krna phir link pr Click kr k site pr jana then usk bad waha  create a new app / new pr click krna koi bhi ek pr , then app mame me Kuch bhi dalna jo tumhe nam dena hai project ka
# ab anaconda prpmpt me janeka aur waha jo file ko deployment krna hai uss file ki location dal dena  " cd aur path "
# then dir dal kr dekhna jo cmd me aaya hai file wo file agar apne jo path dala hai usmer hai means we are going good
# then we have to Create a New Environment " conda create -n REVIEW_SCRAPPER_USING_HEROKU python=3.6.9"
# then cmd pr aayenga to activate the environment aur activation command aayenga usko run krna
# then website p[r login kr k deploy me jitne bhi command hai wo run krte baitna apne hisab se

# at the last jse humne push krdiya masters k ander toh hume sb se niche ek link milenge usko copy kr lema aur browser msai paste kr dene khatam apka ready hai scrapper reviews check krne k liye



