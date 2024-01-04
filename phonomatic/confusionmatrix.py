# -*- coding: utf-8 -*-

# English case below

# From Phoneme Perception Errors Munson et al. (2002) JASA
# Table II. Vowel confusion matrix, poorer listeners
#     Q   A   E  eI   ‘   I   i  oU   U   U   u
# Q 303  28  66  20  30  16  12   4   2   4   1
# A 143 207  11   6  61   2   1  22   6  22   5
# E  19   5 186  14   4 186  11   4  25  30   2
# eI 21   6  16 305  12  17  98   3   2   2   4
# ‘   8  11  29   8 240  13   2  36  47  27  65
# I   6   0  66  12   3 356  30   1   4   7   1
# i  10   0  11  49   6  18 387   4   1   0   0
# oU  2  17   7   4  33   2   2 231  31   8 149
# U   7  10  28   4  22  39   4  31 257  47  37
# U  11  19  64   3  19  38   6  15 164 134  13
# u  10  12   7   7  54   5   1  94  38  12 246
#
#
#


# Table IV. Consonant confusion matrix, poorer listeners
#     p   t   k   b   d   g   f   T   s   S   v   D   z   Z   m   n   r   l  j
# p 188  98 106  12   6  15  17  13   5   1   3   3   2   2   0   2   2   4  1
# t  55 234 135   2   2   5   8  22   3   4   1   3   2   2   0   0   0   2  0
# k  72 115 242   1   1   4   7  11   9   4   0   5   1   0   1   2   0   3  2
# b  32   3   6 190  55  60  31  21   3   0  33  10   3   0  16   9   3   5  0
# d  13  12   9  42 151 200   9  11   0   0   7   7   0   0   4   5   1   3  6
# g  14  16  15  15  80 268   7   9   3   1  11   5   6   2   2  11   3   3  9
# f  39  14  13  11   1   4 177  86  55  17  20  13   5   8   3   2   3   2  7
# T  44  16  12   9   8   4 171 127  50   5   5  19   4   0   0   2   0   3  1
# s  24   8   6   7   7   4 102  79 128  46  10  21  11  18   1   3   4   1  0
# S   2   5   0   0   1   0   5   1  49 353   1   2  11  46   1   0   1   2  0
# v  15   9   8  55  16  39  16  42  19   2 101  22  25   6  26  26  22  21 10
# D  10   7   6  66  24  28  22  51   7   2 101  23  21   8  17  37  18  19 13
# z   9   2   5  22  11  14  17  39  31  32  57   9  79  43   5  22  22  11 50
# Z   1   4   2   1   0   3   4   3   7 103   5   2  54 258   2   2   7   4 18
# m   7   0   7  23   2   5  19   4   4   1  14   2   6   2 217 119  20  25  3
# n   7   6   6   8  21  12   4   4   5   1  16   2  12   2  67 250   8  11 38
# r   4   0   2  14   2   7   5   6   5   0  56   5  10   5  22  24 206  29 78
# l   5   1   0  17   1   4   5   1   3   1  12   2   5   0  78  87  95 128 35
# j   2   5   5   1   4  10   4   3   6  12  11   2  24  13   6  28   8   5 33
#

class IPASubmap(object):
  """ In order to use IPA for phoneme fuzzy matching, we first remove all diacritics and map all remaining phonemes to an index in a chart as seen below.
      This allows to simplify the confusion matrix fuzzy matching algorithm (but at a loss of precision).

      use discode to convert a unicode encoded IPA string to an array of index in the alphabet
      """

  def __init__(self):
    # Extracted from https://en.wikipedia.org/wiki/Phonetic_symbols_in_Unicode, sorted, ignoring diacritics and modifiers,
    # That's exactly 324 characters, so an index into this string will require 9 bits
    self.alphabet = "abcdefhjklmnopqrstvwxzæçðøħŋœȡȴȵȶɐɑɒɓɔɕɖɗɘəɚɛɜɝɞɟɠɡɢɣɤɥɦɧɨɩɪɫɬɭɮɯɰɱɲɳɴɵɶɷɸɹɺɻɼɽɾɿʀʁʂʃʄʅʆʇʈʉʊʋʌʍʎʏʐʑʒʓʔʕʖʗʘʙʚʛʜʝʞʟʠʡʢʣʤʥʦʧʨʩʪʫʬʭʮʯβθχᴀᴁᴂᴃᴄᴅᴆᴇᴈᴉᴊᴋᴌᴍᴎᴏᴐᴑᴒᴓᴔᴕᴖᴗᴘᴙᴚᴛᴜᴝᴞᴟᴠᴡᴢᴣᴤᴥᴦᴧᴨᴩᴪᴫᴬᴭᴮᴯᴰᴱᴲᴳᴴᴵᴶᴷᴸᴹᴺᴻᴼᴽᴾᴿᵀᵁᵂᵃᵄᵅᵆᵇᵈᵉᵊᵋᵌᵍᵎᵏᵐᵑᵒᵓᵔᵕᵖᵗᵘᵙᵚᵛᵜᵝᵞᵟᵠᵡᵢᵣᵤᵥᵦᵧᵨᵩᵪᵫᵬᵭᵮᵯᵰᵱᵲᵳᵴᵵᵶᵷᵸᵹᵺᵻᵼᵽᵾᵿᶀᶁᶂᶃᶄᶅᶆᶇᶈᶉᶊᶋᶌᶍᶎᶏᶐᶑᶒᶓᶔᶕᶖᶗᶘᶙᶚᶛᶜᶝᶞᶟᶠᶡᶢᶣᶤᶥᶦᶧᶨᶩᶪᶫᶬᶭᶮᶯᶰᶱᶲᶳᶴᶵᶶᶷᶸᶹᶺᶻᶼᶽᶾᶿ"

  @staticmethod
  def binarySearchOnString(arr, x):
    l = 0
    r = len(arr) - 1
    while (l <= r):
      m = (l + r) // 2
      if (arr[m] == x):
        return m
      elif (arr[m] < x):
        l = m + 1
      else:
        r = m - 1
    return -1  #   If element is not found  then it will return -1

  def discode(self, text):
    r = [ self.binarySearchOnString(self.alphabet, c) for c in text ]
    return [ c for c in r if c >= 0 ]


class ConfusionMatrix(object):
  """ Get the confusion matrix for the given language (currently, only English is supported)"""
  def __init__(self, language = "en"):
    if language == "en":
      self.matrix = []
      self.submap = IPASubmap()

  def confuseScore(self, A, B, budget = None):
    """ Get the similarity score of string of phoneme A vs string of phoneme B. Similar phonemes will have a score close to 1, while dissimilar phonemes will have a score close to 0
        If budget is None, this returns a score of similarity of 1 for similar SOP.
        Else, this returns the updated budget, where each change decreasing the budget by the confusion matrix score. It stops matching if budget is 0.
    """
    a = self.submap.discode(A)
    b = self.submap.discode(B)

    if budget == None:
      # Don't try a Levenshtein search if no budget for it
      # For now, string of different length are different in all cases
      if len(a) != len(b):
        return 0.0
      score = 1.0
      for c in zip(a, b):
        score = score * self.confuseScorePhoneme(c[0], c[1])
      return score
    else:
      threshold = 0.99
      score = budget
      j = 0; i = 0
      while i < len(a):
        # Substitution on end of the string ?
        if j >= len(b):
          return max(0.0, score - (len(a) - i) * 1.0)
        s = self.confuseScorePhoneme(a[i], b[j])
        if s <= threshold:
          # It fails, let's see if we still have the budget for it
          if score <= 1.0:
            return 0.0
          # Check if substitution with the next char is better
          if j + 1 < len(b) and (t := self.confuseScorePhoneme(a[i], b[j+1])) > threshold:
            # Missing a phoneme in B, so skip it
            j = j+1
          elif i + 1 < len(a) and (t := self.confuseScorePhoneme(a[i+1], b[j])) > threshold:
            # Missing phoneme in A, so skip it
            i = i+1
          # Else, let's assume it's a replacement

          score = score - 1.0

        j = j + 1
        i = i + 1

      return score

  def confuseScorePhoneme(self, A, B):
    # TODO: Supports confusion matrix here
    return 1.0 if A == B else 0.0

