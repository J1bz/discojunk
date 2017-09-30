discojunk
=========

Discojunk is a discord bot able to generate grammatically okish sentences
based on what previous users said.

The bot can first learn what users say by recording everything. And then,
when there is enough available data, it can speak of its own.

Sentences are generated with a naive algorithm based on markov chains,
implying grammar is often correct, but it just does not make any sense. Which
is actually funny.

Installation
------------

  sudo aptitude install python-virtualenv git

  virtualenv -p python3 venv_discojunk
  source venv_discojunk/bin/activate

  git clone https://github.com/b1naryth1ef/disco
  cd disco
  python setup.py install  # may take some time to compile gevent
  cd ..

  git clone https://github.com/J1bz/discojunk
  cd discojunk
  cp config.json_DIST config.json

Update `config.json` with your own bot token, then :

  python -m disco.cli

How to make it work ?
---------------------

Just let the bot alone and speak... for a while... *at least* one day or one
week. The more you speak, the more the bot will have to speak about.

Just don't use the `tellsomejunk` command for now since it's just gonna crash
(maybe I should fix this one day).

When you think you have enough data :

  cd discojunk
  python data2chain.py

After reloading the bot, you can ask it to `tellsomejunk`.
