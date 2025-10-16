from newspaper import Article
import sys

url = str(sys.argv[1])
#url = 'https://www.alternet.org/news-amp-politics/major-texas-newspaper-dumps-ted-cruz-and-gives-glowing-endorsement-beto-orourke'



article = Article(url)
article.download()
article.html
article.parse()
article.title
article.authors
article.publish_date
article.text
print(article.title+"\n\n"+", ".join(str(x) for x in article.authors)+"\n\n"+str(article.publish_date)+"\n\n"+article.text+"\n\n"+url, file=open(article.title+'.txt', 'w'))

