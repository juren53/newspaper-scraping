from newspaper import Article
import sys

url = str(sys.argv[1])
article = Article(url)
article.download()
article.html
article.parse()
article.title
article.authors
article.publish_date
article.text
print(article.text,  file=open(article.title+'.txt', 'w'))

