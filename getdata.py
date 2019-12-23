#! /usr/bin/python3

import requests
from html.parser import HTMLParser
import re
import logging
import datetime
import json
import sys

log = logging.getLogger(__name__)

if __name__ == '__main__':
    logging.basicConfig()


class Node:
    tag: str
    attrs: dict

    def __init__(self, *av, **kw):
        tag = kw.pop('tag', None)
        classes2 = []
        attrs = {}
        if av:
            tag, *av = av
            tag, *classes2 = tag.split('.')

        if av:
            attrs.update(av[0])
            assert not av[1:]

        attrs.update(kw)

        classes = set(filter(None, attrs.pop('class', '').split(' ')))
        classes.update(classes2)
        if classes:
            attrs['class'] = ' '.join(classes)
        self.tag = None if tag == '*' else tag
        self.attrs = attrs

    def __repr__(self):
        args = []
        if self.tag:
            args.append(f'tag={self.tag!r}')
        if self.attrs:
            args.append(f'attrs={self.attrs}')
        return f'{type(self).__name__}({", ".join(args)})'

    @property
    def classes(self):
        return set(self.attrs.get('class', '').split())

    def __eq__(self, other: 'Node'):
        if self.tag is not None and other.tag is not None and self.tag != other.tag:
            return False

        self_classes = self.classes
        pther_classes = other.classes
        if pther_classes - self_classes:
            return False

        return True


class ExtHTMLParser(HTMLParser):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.path = []

    def handle_starttag(self, tag, attrs):
        self.path.append(Node(tag, dict(attrs)))

    # Overridable -- handle end tag
    def handle_endtag(self, tag):
        self.path.pop(-1)

    @property
    def last_node(self):
        return self.path and self.path[-1] or None


class HabrStatParser(ExtHTMLParser):
    def __init__(self, user=None, **kw):
        super().__init__(**kw)
        no_metrics = set(self.__dict__.keys())
        self.time = datetime.datetime.utcnow()
        self.user = user
        self.votes = None
        self.karma = None
        self.rating = None
        self.subscribers = None
        self.subscribes = None
        self._metrics = set(self.__dict__.keys()) - no_metrics

    def log_line(self):
        stat = {k: v for k, v in self.__dict__.items() if k in self._metrics}
        return json.dumps(stat, ensure_ascii=False, default=str)

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        attrs = dict(attrs)

        if self.votes is None and self.path[-2:] == [
                Node('div.media-obj__body.media-obj__body_user-info'),
                Node('a.user-info__stats-item.stacked-counter'),
        ]:
            title = attrs.get('title', '')
            karma = re.match(r'(?P<votes>\d+)\s+голо.*', title)
            self.votes = int(karma.groups()[0])

    @staticmethod
    def cast_float(s: str):
        try:
            return float(s.replace(',', '.'))
        except:
            log.error(f'Cast error: {s!r} to float')

    def handle_data(self, data):
        if self.path[-3:] == [
                Node('div.media-obj__body.media-obj__body_user-info'),
                Node('a.user-info__stats-item.stacked-counter'),
                Node('div.stacked-counter__value'),
        ]:
            if self.karma is None:
                self.karma = self.cast_float(data)
            elif self.path[-2] == Node('a.stacked-counter_rating'):
                self.rating = self.cast_float(data)
            elif self.path[-2] == Node('a.stacked-counter_subscribers'):
                if self.subscribers is None:
                    self.subscribers = int(data)
                else:
                    self.subscribes = int(data)


def get_habr_stat(user, site='https://habr.com', lang='ru'):
    url = f'{site}/{lang}/users/{user}/comments/'
    with requests.get(url) as r:
        data = r.text
        hp = HabrStatParser(user=user)
        hp.feed(data)
        print(hp.log_line())


if __name__ == '__main__':
    user = sys.argv[1]
    get_habr_stat(user)
