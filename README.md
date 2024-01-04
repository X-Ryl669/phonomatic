# Phon-o-matic

This repository is implementing a phonetic sentence matching algorithm based on what I've read so far (and probably misunderstood).

The goal is the following:
1. Imagine you have a (bad) recording of a sentence
2. You convert this recording to text with an ASR (automatic speech recognition) tool and this gives you a (bad) textual transcription.
3. You have a list of sentences to match against (these sentences can be programmatically generated or parametrics like `set volume to {number} percent`)
4. Find the most likely sentence that was initially intended and ideally extract the parametric variable if any


This repository implements an algorithm that tries to solve the above in as many languages as possible. It's expected however that the language the speaker uses is known and matched against a set of sentences of the same language.

### Why use this instead of a string matching algorithm?

While you can match a perfect ASR output to a perfect sentence and get a perfect match, in the real world, it's very unlikely that the ASR output will be perfect.
So a simple string matching (or a regular expression) can not work directly, since it would collapse at the first mismatch.

Then, one can use a fuzzy string matching algorithm, like Levenshtein matching (and alike). There are good for spelling correction (where very few characters can be mistyped, added or removed) but not really good for utterance matching.
This is because a single confusion in one phoneme in the sentence will lead to a very different textual representation. For example, in English, `flower` and `flour` or  `their`, `there` and `they're` are pronounced the same but have a
very different spelling (homophones). Similarly, heterophone are undistinguishable in their written form, but not on their utterance (like `I've read this book` `I read this book`).

Hence, for a better matching algorithm, not using text (graphemes) should lead to much better results.

## Implementation

Here's the implementation details for what it's worth (might not be accurate, since the code is not released yet):

### ASR output processing

Sadly, most STT (speech to text) algorithms output text and not phonemes (even if they do that internally). So a processing step is required to convert the STT result back to a string of phonemes stored in IPA form.

This is done with [Epitran](https://github.com/dmort27/epitran) MIT-licensed library. Epitran will fail to convert text to phoneme for words it didn't know so it might need some help here (like setting up a backoff language)

The output of this step is a **string of phonemes** (SOP)

### Intents processing

In general, intents are exponentially complex sentences that the user want to select from. It's exponential because it contains many branches (like optional words, parametric variables, abbreviations, ...).
So it's not efficient to build a array of all possible sentences and convert them to SOP, since this can be huge (memory) and slow (processing).

Instead one can see the potential sentences as a match tree with partial branching.

For example, let's say you have such sentences to match against:

- Open the <object: curtain|object: cover|object: door> <name> [optional: please]
- Open all <object: curtains|object: covers|object: doors> [optional: please]
- Set [optional: the] volume to <value> [optional: percent] [optional: please]
- Set <name>[optional: 's] color to <color> [optional: please]

These 4 basic rules, expended, would generate 2*4*O(name) + 2*4 + 2⁴*100 sentences.

Thus, instead, the idea is to create a graph to match against, by first splitting on divergent path, a bit like this:
```

                 / curtain - <name> - *please -> ID0
           (the)-  cover   - <name> - *please -> ID1
          /      \ door    - <name> - *please -> ID2
         /
        /       / curtains - *please -> ID3
  (Open) - (all)- covers   - *please -> ID4
 /              \ doors    - *please -> ID5
 \
  (Set) - (*the) - (volume to) - <value> - *please -> ID6
       \
        - <name> - *'s - color to - <color> - *please -> ID7
```

This graph is a bit special: it has 4 kinds of node: parent node (which are always textual), parametric node, optional nodes and object node. The leaf of the graph is the identifier of the selected variant of the sentence.

It looks like a ternary tree but instead of splitting on any character in a word to sort in lexical order, the complete word is always used for a node. This is absolutely required for phonetic matching.

Thus, walking this graph is a O(log N) operation.

The second processing step after graph creation is to convert parent node and optional nodes to SOP similarly to the ASR output.

### Parametric processing

When a sentence contains parametric variables, it is required to create a map for each possible variable value to its SOP form.
Thus a set of variable map is created. In the intent graph above, when a parametric node is created, a link it made to the expected variable map or graph.
If the number of item is large, a (ternary) graph is preferred to allow O(log N) searching.

However, for value processing (where the set would be unlimited), some additional processing is required that implies runtime completion (see below for details).

From now, everything above was preprocessed, anything below is done at runtime.

### Confusion matrix and fuzzy matching

Confusion happens frequently on phoneme selection and matching. Some phonemes are very similar to other phonemes, so the substitution cost isn't the same for any two phoneme.
Instead, we use a confusion matrix (extracted from Munson et al. (2002) JASA) to penalize the confusion from one phoneme to another phoneme.
Very distinct phoneme have a higher penalty than "similar" phoneme (normalized, from 0: same to 1: very different).


### Fuzzy matching

When it's time to find out the selected sentence (that is: match the ASR to the selected intend) the algorithm is quite simple:
1. Set a penalty budget to P
2. Start from the root node and walk down the graph based on the IPA similarity. If the penalty budget is 0, stop processing that branch
3. Since words might not be exactly the same, we can perform a strcmp-like match and then check the confusion matrix on the first mismatched character. Subtract the confusion penalty from the budget and continue processing if it's greater than 0.
4. If reaching an optional node, try matching the optional node's SOP with a temporary penalty budget. After processing the last phoneme of the optional node, compare the temporary budget with some threshold to accept/deny the optional node
5. If the optional node's penalty is below the threshold, subtract this penalty from the budget and continue processing
6. Upon reaching parametric or value node, similarly to optional node, a temporary budget is created and the graph/set is processed. The smallest penalty is retained, all others are discarded.
7. The selected branch's penalty is subtracted from the budget
8. When reaching a terminal ID node, the match is completed, so save the current (penalty, ID) tuple to a temporary result array (or simply return the found ID)
9. As an optimization step, it's possible to remember the first node found that decreased the penalty budget so we can resume searching from that node next sibling.
10. Once all branch were visited (and probably ended early), sort the temporary result array and return the ID with the highest penalty budget.

Please notice that parametric matching is a complex problem because of the large search area. One might decide not to perform fuzzy matching in the parametric search case to simplify processing (a perfect IPA match is then requested).
However, another possible solution could be to sort IPA phoneme from their similarity so a lexical search could be performed without computing the confusion penalty.

For example, since `oU` is very similary to `u`, if ordered lexically, then when walking down the ternary search tree, instead of selecting the left or right child branch based on "greater than" or "lower than",
we can decide to select "2 places greater than" or "3 places lower than", provided the lower node is further away from the allowed tolerance. This has to be tested to see how effective it is.



