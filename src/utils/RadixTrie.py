# The RadixTrie is based on
#   https://github.com/TheAlgorithms/Python/blob/master/data_structures/trie/radix_tree.py
# With the following updates:
#   - Fixed a bug: https://github.com/TheAlgorithms/Python/issues/11316
#     A PR with an attempted fix was pending at the time of writing but it's faulty.
#     (It doesn't deal with cases, where a prefix is repeated within a word.)
#   - New feature of looping back to root when searching i.e., finding sentences.
#   - Separated trie and node classes and other minor changed.

from functools import cache
from typing import Optional


class TrieNode:

    def __init__(self,
                 prefix: str = '') -> None:
        self.prefix = prefix
        self.is_leaf = False
        self.children: dict[str, TrieNode] = {}

    def __repr__(self):
        return repr(f'{self.prefix}')


class Trie:

    def __init__(self) -> None:
        self.root = TrieNode("")

    def add(self,
            word: str) -> None:
        node = self.root
        for char in word:
            if char not in node.children.keys():
                node.children[char] = TrieNode(char)
            node = node.children[char]
        node.is_leaf = True

    def add_many(self,
                 words: list[str]) -> None:
        for word in words:
            self.add(word)

    def is_word(self,
                word: str) -> int:
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_leaf

    def is_sentence(self,
                    sentence: str) -> bool:
        node = self.root
        for i, char in enumerate(sentence):
            if char not in node.children:
                return False
            node = node.children[char]
            if node.is_leaf:
                if self.is_sentence(sentence[i+1:]):
                    return True
        return node.is_leaf

    # REVISIT: untested function
    def starts_with(self,
                    prefix: str) -> bool:
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True

    def _count_nodes(self,
                     node: TrieNode) -> int:
        count = 1
        for child in node.children.values():
            if child is not {}:
                count += self._count_nodes(child)
        return count

    def size(self) -> int:
        return self._count_nodes(self.root)


class RadixNode:

    def __init__(self,
                 root=None,
                 prefix='',
                 is_leaf=False) -> None:
        self.prefix = prefix
        self.is_leaf = is_leaf
        self.root = self if root is None else root
        self.children: dict[str, Optional[RadixNode]] = {}

    def match_prefix(self,
                     word: str) -> tuple[str, str, str]:
        i = 0
        for a, b in zip(self.prefix, word):
            if a != b:
                break
            i += 1
        # matching, remaining_prefix, remaining_word
        return self.prefix[:i], self.prefix[i:], word[i:]

    def add(self,
            word: str,
            is_repeating_prefix: bool = False) -> None:
        # Case 1: If the word is the prefix of the node
        # Solution: We set the current node as leaf
        if self.prefix == word and not self.is_leaf and not is_repeating_prefix:
            self.is_leaf = True

        # Case 2: The node has no edges that have a prefix to the word
        # Solution: We create an edge from the current node to a new one
        # containing the word
        elif word[0] not in self.children:
            self.children[word[0]] = RadixNode(root=self.root, prefix=word, is_leaf=True)

        else:
            child = self.children[word[0]]
            assert child is not None
            matching, remaining_prefix, remaining_word = child.match_prefix(word)

            # Case 3: The node prefix is equal to the matching
            # Solution: We insert remaining word on the next node
            if remaining_prefix == "":
                if remaining_word == "":
                    child.add(matching)
                # Edge case of repeating prefix, must add a new node with the same prefix
                else:
                    is_repeating_prefix = remaining_word[0] == matching[0]
                    child.add(remaining_word, is_repeating_prefix=is_repeating_prefix)

            # Case 4: The word is greater equal to the matching
            # Solution: Create a node in between both nodes, change
            # prefixes and add the new node for the remaining word
            else:
                child = self.children[matching[0]]
                assert child is not None
                child.prefix = remaining_prefix

                aux_node = child
                child = RadixNode(root=self.root, prefix=matching, is_leaf=False)
                self.children[matching[0]] = child
                child.children[remaining_prefix[0]] = aux_node

                if remaining_word == "":
                    child.is_leaf = True
                else:
                    child.add(remaining_word)

    @cache
    def find(self,
             word: str,
             loop: bool = False) -> int:
        children = [self.children.get(word[0], None)]
        if children[0] is None:
            if not self.is_leaf:
                return 0
            else:
                return self.root.find(word, loop)
        else:
            result = 0
            if self.is_leaf and loop:
                children.append(self.root.children.get(word[0], None))
            for child in children:
                assert child is not None
                _, remaining_prefix, remaining_word = child.match_prefix(word)
                if remaining_prefix == "":
                    if remaining_word == "":
                        result += 1 if child.is_leaf else 0
                    else:
                        result += child.find(remaining_word, loop)
            return result

    def print_trie(self,
                   depth: int = 0) -> None:
        if self.prefix != "":
            print("-" * depth, self.prefix, "  (leaf)" if self.is_leaf else "")
        for child in self.children.values():
            assert child is not None
            child.print_trie(depth + 1)


class RadixTrie():

    def __init__(self) -> None:
        self.root = RadixNode()

    def add(self,
            word: str) -> None:
        self.root.add(word)

    def add_many(self,
                 words: list[str]) -> None:
        for word in words:
            self.add(word)

    def is_word(self,
                word: str) -> bool:
        return self.root.find(word) > 0

    def is_sentence(self,
                    string: str) -> bool:
        return self.root.find(string, loop=True) > 0

    def possible_sentences(self,
                           string: str) -> int:
        return self.root.find(string, loop=True)

    def _count_nodes(self,
                     node: RadixNode) -> int:
        return sum([self._count_nodes(c) for c in node.children.values() if c is not None and c != {}]) + 1

    def size(self) -> int:
        return self._count_nodes(self.root)

    def print_trie(self) -> None:
        self.root.print_trie()


# TODO: turns these into unit tests

# # Test 1: each words must be found
# is_word = [rt.is_word(w) for w in words]
# assert all(is_word)

# # Test 2: generate n-word sentences and find them
# n = 2
# for w in permutations(words, n):
#     test_sentence = ''.join(w)
#     is_sentence = rt.is_sentence(test_sentence), f'{test_sentence}'
#     assert is_sentence, f'{test_sentence}'
