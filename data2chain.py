#!/usr/bin/env python

import json

from markovish_chain import MarkovishChain


DATA_FILE = 'storage.json'
CHAIN_FILE = 'chain.json'

BOT_AUTHORS = ['discoscope#5358', 'Sweety-bot#5624', 'Miam R.U. Bot#4894']
BOT_CMDS = ['whois', 'db']


def get_data(data_file):
    with open(data_file, 'r+') as fh:
        messages = json.load(fh)['_pDiscojunk:junk']['data']

    return messages


def remove_content_between(message, start_symbol, end_symbol):
    new_message = ''
    nested_level = 0
    for c in message:
        if c == start_symbol:
            nested_level += 1
        elif c == end_symbol:
            # If we meet an end_symbol without having encountered a start,
            # just reset the new_message. It must be a typo.
            # ex: "telling this) and that" => we want only " and that"
            if nested_level == 0:
                new_message = ''
            else:
                nested_level -= 1
        else:
            if nested_level == 0:
                new_message += c
    return new_message


def clean_messages(messages):
    # Bot messages
    messages = [
        m for m in filter(lambda x: x['author'] not in BOT_AUTHORS, messages)]

    # Extract messages with multiple lines
    for m in messages[:]:
        lines = m['content'].splitlines()

        if len(lines) > 1:
            messages.remove(m)

            for l in lines:
                messages.append(
                    {
                        'content': l,
                        'author': m['author'],
                        'ts': m['ts']
                    }
                )

    # Clean, prepare
    for m in messages:
        m['content'].strip()
        for start, end in [('(', ')'), ('[', ']'), ('«', '»')]:
            m['content'] = remove_content_between(m['content'], start, end)
            m['content'].strip()
        # Approximation... it must be a better way to handle this char '"'
        m['content'] = m['content'].replace('"', '')
        m['content'] = m['content'].lower()
        m['words'] = m['content'].split(' ')
        # Remove useless strings like '', '\t', '\n'
        m['words'] = [w for w in filter(lambda x: x.strip(), m['words'])]

    # One word or less
    messages = [
        m for m in filter(lambda x: len(set(x['words'])) > 1, messages)]

    # Bot commands
    messages = [
        m for m in filter(lambda x: x['words'][0] not in BOT_CMDS, messages)]

    # Add start and stop symbol
    for m in messages:
        m['words'].append(False)

    return messages


if __name__ == '__main__':
    messages = get_data(DATA_FILE)
    messages = clean_messages(messages)

    sentences = [m['words'] for m in messages]
    chain = MarkovishChain(sentences=sentences, chain_file=CHAIN_FILE)
    chain.sanitize().save(pretty=False)
