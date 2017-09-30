import ast
import random
from datetime import datetime

from disco.bot.plugin import Plugin
from disco.util.logging import LoggingClass


class Discojunk(Plugin, LoggingClass):

    CHAIN_FILE = 'chain.json'

    def load(self, ctx):
        super(Discojunk, self).load(ctx)
        self.junk = self.storage.plugin('junk').data.data
        if 'data' not in self.junk:
            self.junk['data'] = []

        with open(self.CHAIN_FILE, 'r') as fh:
            content = fh.read()
            self.chain = ast.literal_eval(content)

    def generate_sentence(self, chain, words=20):
        sentence = []
        current, next_ = random.choice(list(chain.keys()))
        for i in range(words):
            sentence.append(next_)
            current, next_ = next_, random.choice(chain[(current, next_)])
            if next_ is False:
                break

        sentence = ' '.join(sentence)
        sentence = sentence[0].capitalize() + sentence[1:]

        # Should have been cleaned before, but whatever...
        sentence = sentence.replace(' ,', ',')

        return sentence

    @Plugin.command('tellsomejunk', '[args:int]')
    def on_tellmassjunk(self, event, args=1):
        for i in range(args):
            event.msg.reply(
                self.generate_sentence(
                    self.chain,
                    words=random.randint(10, 40)
                )
            )

    @Plugin.listen('MessageCreate')
    def on_something(self, event):
        self.junk['data'].append(
            {
                'content': event.content,
                'ts': datetime.now().timestamp(),
                'author': str(event.author)
            }
        )
        self.storage.save()
