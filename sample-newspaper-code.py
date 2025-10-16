from newspaper import Article
url = 'https://www.npr.org/2018/10/19/658732039/turkey-questions-employees-of-saudi-consulate-over-journalists-disappearance'
article = Article(url)
article.download()
article.html
article.parse()
article.title
article.authors
article.publish_date
article.text

