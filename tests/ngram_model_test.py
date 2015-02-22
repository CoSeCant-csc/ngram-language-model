import sys
sys.path.append('..')
import unittest
import partition_tree
import sampler
import ngram_model
import tokenizer

class TokenizerTest(unittest.TestCase):
    def test_tokenizer(self):
        test_strings = ['The man who is tall is happy.','Is the man who is tall happy?']
        tokenized_strings = [['The','man','who','is','tall','is','happy','.'],
                             ['Is', 'the', 'man','who','is','tall','happy','?']]
        T = tokenizer.Tokenizer()
        assert T.process(test_strings) == tokenized_strings

class NgramTest(unittest.TestCase):
    def test_frequency_tree(self):
        train_sequences = [['the','dog','runs'],['the','dog','jumps']]
        unigram_tree = ngram_model.NGramFrequencyTree(N=1)
        for sequence in train_sequences:
            for unigram in sequence:
                unigram_tree.add_ngram_observation([unigram])
        assert set(unigram_tree.get_all_continuations(())) == {'the', 'dog','runs', 'jumps'}
        self._assert_ngram_frequency(unigram_tree, ['the'], 6, 2)


    def _assert_ngram_frequency(self, tree, sequence, expected_total, expected_sequence_count):
        sequence_total, sequence_count = tree.get_ngram_frequency(sequence)
        assert sequence_total == expected_total and sequence_count == expected_sequence_count

class PartitionTreeTrest(unittest.TestCase):
    def test_partition_tree(self):
        tree = partition_tree.PartitionTree([(0.0,0.5),(0.5,1.0)],['A', 'B'])
        values = [0.0, 0.3, 0.5, 0.7, 1.0]
        labels = [tree.get_label(v) for v in values]
        correct_labels = ['A', 'A', 'A', 'B', 'B']
        assert labels == correct_labels

class MultinomialSampleTest(unittest.TestCase):
    def test_biased_coin_flip(self):
        true_heads, true_tails = 0.3, 0.7
        P = [true_heads, true_tails]
        event_names = ['Heads', 'Tails']
        s = sampler.Multinomial_Sampler(P, event_names)
        from collections import Counter
        total_samples = 400000
        sample_counter = Counter([s.sample() for i in range(total_samples)])
        allowed_error = 0.001
        head_frequency = 1.0*sample_counter['Heads']/total_samples
        tail_frequency = 1.0*sample_counter['Tails']/total_samples
        print(head_frequency, tail_frequency)
        assert true_heads - allowed_error <= head_frequency <= true_heads + allowed_error
        assert true_tails - allowed_error <= tail_frequency <= true_tails + allowed_error

class NGramSamplerTest(unittest.TestCase):
    def bigram_sample_from_corpus_model(self, test_sequences):
        N = 2
        sequence_tree = ngram_model.NGramFrequencyTree(N)
        token = tokenizer.Tokenizer()
        ngram_maker = ngram_model.NGramMaker(N)
        tokenized_sequences = token.process(test_sequences)
        prepared_sequences = [ngram_maker.make_ngrams(s) for s in tokenized_sequences]
        [sequence_tree.add_ngram_observation(ngram) for sequence in prepared_sequences for ngram in sequence]
        sampler = ngram_model.NGramSampler(sequence_tree, N)
        return sampler.sample_sequence(ngram_maker.starting_tokens)


    def test_single_length_sample(self):
        test_sequences = ['a.', 'a.']
        assert self.bigram_sample_from_corpus_model(test_sequences)  == ['*_-1', 'a', '.', 'STOP']

    def test_very_unlikely_sample(self):
        test_sequences = ['a.']*10000 + ['b.']
        assert self.bigram_sample_from_corpus_model(test_sequences)  == ['*_-1', 'a', '.', 'STOP']

    def test_long_sequence(self):
        test_sequences = ['a b c d e f g.']
        assert self.bigram_sample_from_corpus_model(test_sequences) == ['*_-1', 'a', 'b', 'c', 'd', 'e', 'f', 'g', '.', 'STOP']

if __name__ == '__main__':
    unittest.main()
