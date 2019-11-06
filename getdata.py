
import requests
from html.parser import HTMLParser


class Habr_statParser(HTMLParser):
    def __int__(self):
        self.karma_votes_count = None

    def handle_starttag(self, tag, attrs):
        cls = attrs.get('class')
        if 'user-info__stats-item' in cls:
            self.karma_votes_count = int(attrs['title'].split()[0])
            print(self.karma_votes_count)


def get_habr_stat(url):
    with requests.get(url) as r:
        data = r.content
        hp = HTMLParser()
        hp.feed(data)

        print(len(data))


if __name__ == '__main__':
    url = 'https://habr.com/ru/users/trapwalker/comments/'
    get_habr_stat(url)
