import random
from datetime import datetime

from disco.bot.plugin import Plugin
from disco.util.logging import LoggingClass

from markovish_chain import MarkovishChain


class Discojunk(Plugin, LoggingClass):

    CHAIN_FILE = 'chain.json'

    def load(self, ctx):
        super(Discojunk, self).load(ctx)
        self.junk = self.storage.plugin('junk').data.data
        if 'data' not in self.junk:
            self.junk['data'] = []

        self.mc = MarkovishChain(
            load_from_file=True,
            chain_file=self.CHAIN_FILE
        )
        self.mc_root_nodes = list(self.mc.get_root_nodes())

    @Plugin.command('tellsomejunk', '[args:int]')
    def on_tellmassjunk(self, event, args=1):
        if args > 20:
            event.msg.reply("Even me can't tell that much junk at a time ;/")
            return

        generated_contents = []
        for i in range(args):
            generated_contents.append(
                self.mc.generate_sentence(
                    self.mc_root_nodes,
                    words=random.randint(10, 40)
                )
            )
        event.msg.reply('\n'.join(generated_contents))

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
