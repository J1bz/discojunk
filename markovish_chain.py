import ast
import pprint
import random
import string


class MarkovishChain(object):
    def __init__(
            self,
            sentences=None,
            load_from_file=False,
            chain_file='chain.json'
    ):
        if all([sentences, load_from_file]):
            raise ValueError(
                'Cannot initialize chain from 2 different sources')

        self.chain_file = chain_file

        if sentences:
            self.sentences2chain(sentences)
        elif load_from_file:
            self.load()

        self._flavourless_chars = string.ascii_letters + string.digits

    def sentences2chain(self, sentences):
        self.chain = {}
        for words in sentences:
            for i in range(len(words) - 2):
                key = (words[i], words[i + 1])
                if key in self.chain:
                    self.chain[key].append(words[i + 2])
                else:
                    self.chain[key] = [words[i + 2]]

        return self

    def load(self):
        with open(self.chain_file, 'r') as fh:
            content = fh.read()
        self.chain = ast.literal_eval(content)
        return self

    def save(self, pretty=False):
        with open(self.chain_file, 'w+') as fh:
            if pretty:
                fh.write(pprint.pformat(self.chain))
            else:
                fh.write(str(self.chain))
            fh.write('\n')

        return self

    def generate_sentence(self, root_nodes, words=20):
        sentence = []

        current, next_ = random.choice(root_nodes)
        for i in range(words):
            sentence.append(next_)
            current, next_ = next_, random.choice(self.chain[(current, next_)])
            if next_ is False:
                break

        sentence = ' '.join(sentence)
        sentence = sentence.capitalize()

        # Should have been cleaned before, but whatever...
        sentence = sentence.replace(' ,', ',')

        return sentence

    def sanitize(self, flavourless_chars=None):
        # This algorithm is bugged for the moment :/
        raise NotImplementedError

        if flavourless_chars is not None:
            self._flavourless_chars = flavourless_chars

        remaining_nodes = list(self.chain.keys())

        iter_n = 0
        continue_ = True
        while continue_:
            iter_n += 1
            root_nodes = self.get_root_nodes(remaining_nodes)
            if not root_nodes:
                continue_ = False
            else:
                for root_node in root_nodes:
                    remaining_nodes.remove(root_node)
                    self._pop_flavourless_root_relations(root_node)

        return self

    def get_root_nodes(self, remaining_nodes=None):
        if remaining_nodes is None:
            remaining_nodes = self.chain.keys()

        for current_node in remaining_nodes:
            w1, w2 = current_node

            potential_previous_nodes = filter(
                lambda w1_w2: w1_w2[1] == w1,
                remaining_nodes
            )

            for n in potential_previous_nodes:
                if w2 in self.chain[n]:
                    break
            else:
                yield current_node

    def _pop_flavourless_root_relations(self, root_node):
        sentences = self._get_all_truncated_sentences(root_node, max_nodes=10)

        for s in sentences:
            if self._is_sentence_flavourless(s, 9):
                _, next_word = s[1]
                self.chain[root_node] = filter(
                    lambda w: w != next_word, self.chain[root_node]
                )

        if not self.chain[root_node]:
            self.chain.pop(root_node)

    def _get_all_truncated_sentences(self, node, max_nodes):
        sentences = []
        sentences_to_continue = [(node,)]

        for i in range(max_nodes):
            for s in sentences_to_continue[:]:
                try:
                    new_sentences = self._continue_sentence(s)
                # Raised when the last node of this sentence cannot be
                # continued (currently (WORD, False,))
                except KeyError:
                    sentences.append(s)
                else:
                    sentences_to_continue.extend(new_sentences)
                finally:
                    sentences_to_continue.remove(s)
        else:
            sentences.extend(sentences_to_continue)

        return sentences

    def _continue_sentence(self, sentence):
        new_sentences = []

        last_node = sentence[-1]
        previous_word, current_word = last_node

        next_words = set(self.chain[last_node])
        for next_word in next_words:
            next_node = (current_word, next_word)
            new_sentences.append(sentence + (next_node,))

        return new_sentences

    def _is_sentence_flavourless(self, sentence, min_words):
        return (
            all([self._is_word_flavourless(w1) for w1, _ in sentence]) or
            len(sentence) < min_words
        )

    def _is_word_flavourless(self, word):
        return all([(char in self._flavourless_chars) for char in word])
