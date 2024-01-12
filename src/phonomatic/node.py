# -*- coding: utf-8 -*-
from .confusionmatrix import IPASubmap, ConfusionMatrix
from .matchresults import Optional, ID, Parameter
import epitran
import re

submap = IPASubmap()
confusionMatrix = ConfusionMatrix()

class EpitranInst:
  """ The instance wrapper of Epitran that can change language at runtime """
  def __init__(self, language = None):
    if language == None:
      self.epiInst = None
    else:
      self.epiInst = epitran.Epitran(language)

  def transliterate(self, text):
    if self.epiInst == None:
      return text
    return self.epiInst.transliterate(text)

  def setLanguage(self, language):
    self.epiInst = epitran.Epitran(language)

class TreeNode(object):
  epiInst = EpitranInst()
  # Increase the verbosity to the logger. 0: nothing, 1: include processing steps
  verbosity = 0
  # From an old issue in Epitran Github, it's said it should transliterate only words not sentences. Yet, it seems to work better if running on sentences.
  # Set to True to enable word only processing
  wordProcessing = False

  """ A tree node in the intent graph. There are multiple possible type of TreeNode object
      The *basic* version is a textual version that must match 1:1 with the expressed string
      of phoneme (SOP)
      The *alternative* version allow multiple choice of SOP from a limited set of possibilities
      The *parametric* version allow any value that are well defined for the language
      The *optional* version is a node that would also match being missing or 1:1
      The *end* version is a node that used reject any SOP if anything remains
  """
  def __init__(self, parent = None, verbosity = 0):
    self.parent = parent
    self.children = []

  def appendChild(self, child):
    assert isinstance(child, TreeNode)
    self.children.append(child)
    if child.parent == None:
      child.parent = self

  @staticmethod
  def setLanguage(language):
    """ Static method to set the language of the Epitran instance.
        Refer to https://github.com/dmort27/epitran for a list of supported languages """
    TreeNode.epiInst.setLanguage(language)

  @staticmethod
  def setVerbosity(verbosity):
    TreeNode.verbosity = verbosity

  @staticmethod
  def setWordProcessing(wordProcessing):
    """ Set to True to enable word only processing
        From issue https://github.com/dmort27/epitran/issues/61 Epitran transliteration is supposed 
        to be run on single word only and not plain sentences
        
        By limited testing, seems to behave better without, so defaults to False """
    TreeNode.wordProcessing = wordProcessing

  @staticmethod
  def splitToSOP(text):
    """ Split the text into list of string of phoneme (SOP) """
    # Remove punctuations since Epitran doesn't deal with it correctly
    text = re.sub(r"[,.:;']", "", text)
    
    if TreeNode.wordProcessing:    
      words = list(filter(lambda x: len(x)>0, text.split(' ')))
      sop = [TreeNode.epiInst.transliterate(x) for x in words]
    else:
      sop = list(filter(lambda x: len(x)>0, TreeNode.epiInst.transliterate(text).split(' ')))

    if (TreeNode.verbosity > 1):
      print("Text: [{}] transliterated to [{}]".format(text, sop))

    return sop

  @staticmethod
  def splitToList(text):
    """ Split the text into list of non empty words """
    return list(filter(lambda x: len(x)>0, text.split(' ')))

  @staticmethod
  def splice(SOP, indexes, wordBoundaries = False):
      lenInput = [len(x) for x in SOP]
      # Then splice the string from all required elements (including leaking words)
      for i in range(0, len(SOP)):
        if indexes >= lenInput[i]:
          SOP.pop(0)
          indexes = indexes - lenInput[i]
        elif indexes > 0:
          # If we always cut at word boundaries, let's drop the end of this current word anyway
          if (wordBoundaries):
            SOP.pop(0)
          else:
            SOP[0][:] = SOP[0][indexes:]
          break
        else:
          break

  def matchText(self, text, budget):
    """ Match the given text with the given allowed budget.
        The text is first converted to SOP (you can use matchSOP if you already have the SOP
        The tree is followed as long as the budget isn't spent for a branch.
        This method returns the node with the highest budget if one found with a remaining budget
        or None if none matched withing the budget
    """
    ids = []
    wl = TreeNode.splitToList(text)
    vt = submap.discode(TreeNode.splitToSOP(text))
    print("Matching [{}] => {} with".format(wl, vt))
    t = budget
    for child in self.children:
      r = child.matchSOP(vt, t, wl)
      if r[0] > 0.0:
        if r[1] != None:
          ids.append(r[1])
        t = r[0]
      else: 
        ids = None
        break
    print("Result {}".format(ids))
    return ids

  @staticmethod
  def results_to_str(ids, withOptionals = False):
    return [str(x) for x in ids if withOptionals or not isinstance(x, Optional)]

  def matchSOP(self, SOP, budget, wl = None):
    pass

  def dump(self):
    print("TreeNode with {} children".format(len(self.children)))
    for child in self.children:
      child.dump()





class BasicNode(TreeNode):
  """ A basic node is a node that is 1:1 with the string of phonemes (SOP) """

  def __init__(self, text, id = None, parent = None):
    super().__init__(parent)
    if id != None:
      self.id = id
    if isinstance(text, tuple):
      self.id = ID(text[0])
      text = text[1]
    self.text = TreeNode.splitToSOP(text)
    self.SOP = submap.discode(self.text)

  def matchSOP(self, SOP, budget, wl):
    if budget <= 0:
      return (0.0, None)
    
    r = confusionMatrix.confuseScorePre(self.SOP, SOP, budget)
    if (TreeNode.verbosity > 1):
      print("Basic match {} SOP{} T{}".format(r, SOP, self.SOP))
    if r[0] > 0.0:
      # Remove the number of element of self.SOP from SOP to avoid rematching them if we selected them
      TreeNode.splice(SOP, r[1], wordBoundaries = True) # Remove any leaking words 

    return (r[0], self.id)

  def dump(self):
    print("BasicNode with id {} and text {} => {}".format(self.id, self.text, self.SOP))





class AlternativeNode(TreeNode):
  """ An alternative node is a node that has multiple possible SOPs """
  def __init__(self, alternatePossibilities, parent = None):
    """ alternatePossibilities is a list of tuple containing the ID and the text of the alternative in the form:
        (ID, text)
    """
    super().__init__(parent)
    self.forms = []
    for form in alternatePossibilities:
      self.forms.append((form[0], submap.discode(TreeNode.splitToSOP(form[1]))))

  def matchSOP(self, SOP, budget, wl):
    if budget <= 0:
      return (0.0, None)

    scores = {}
    consumed = {}
    for form in self.forms:
      t = budget
      t = confusionMatrix.confuseScorePre(form[1], SOP, t)
      if (TreeNode.verbosity > 1):
        print("Alt match {} SOP{} T{}".format(t, SOP, form[1]))
      if t[0] <= 0:
        scores[form[0]] = 0
        consumed[form[0]] = 0
      else:
        scores[form[0]] = t[0]
        consumed[form[0]] = t[1]

    # Find the maximum score here
    m = max(scores, key=scores.get)
    if scores[m] > 0:
      # Splice the string from what's recognized so far
      TreeNode.splice(SOP, consumed[m])

    return (scores[m], ID(m) if scores[m] > 0 else None)

  def dump(self):
    print("AlternativeNode with forms {} = {}".format([x[0] for x in self.forms], [x[1] for x in self.forms]))





class ParametricNode(TreeNode):
  """ An parametric node is a node that stores the spoken text that was pronounced 
      It's a bit more complex than usual node because there's no limit to the parameter so the next nodes in the tree must resynchronize to the remaining SOP 
      
      Parametric nodes can only match complete words
  """
  def __init__(self, parameterName, parent = None, maximumParameterWordCount = 8):
    """ optionalText is a text or a list of text """
    super().__init__(parent)
    self.name = parameterName
    self.maxParamCount = maximumParameterWordCount
    
  def extractText(self, SOP, wl, length):
    # Split the matching word list from the SOP and given len
    start = len(wl) - len(SOP)
    stop = start + (length if length > 0 else len(SOP))
    remainingWords = wl[start:stop]
    return " ".join(remainingWords)

  
  def matchSOP(self, SOP, budget, wl):
    if budget <= 0:
      return (0.0, None)
    # Matching parameters is a more complex
    # In order to do so, we are using a simple trick
    # We check what the next node is and we try to match it with the remaining string until it either work or we run out of tokens to match against
    # This can be a O(N²) operation here, since we don't know when it's supposed to re-synchronize
    # So we limit the search to a limited number of words (by default it's 8 words), in worst case, we'll try to match the next node 7 times, 
    # but it's usually less since parameters are at end of sentence.
    # We search in SOP space not text. 
    
    nextNodeIndex = self.parent.children.index(self) + 1

    while True:
      # Check if we are at the end
      try:
        nextNode = self.parent.children[nextNodeIndex]
      except:
        nextNode = EndNode()


      if isinstance(nextNode, EndNode):
        # Now other node after us, let's capture everything that remains
        return (budget, Parameter(self.name, self.extractText(SOP, wl, 0)))

      if isinstance(nextNode, ParametricNode):
        raise Exception("Parametric nodes can not be successive in the tree")

      # We are not, let's check the minimum length to search for
      paramCount = min(self.maxParamCount, len(SOP) - 1) # At least one word for matching this node
      # Then let it match the next node until we get a score
      if (TreeNode.verbosity > 1):
        print("Param match {} SOP{}".format(budget, SOP))

      scores = []
      for i in range(paramCount):
        t = budget
        sop = SOP[1+i:]
        r = nextNode.matchSOP(sop, t, wl)
        if r[0] > 0 and r[1] == None:
          # Next node is likely an Optional node that hasn't found anything, so special treatment here 
          scores.append(0.0)
        else:
          scores.append(r[0])
      
      # Find the maximum score
      m = scores.index(max(scores))
      if scores[m] > 0:
        # Ok, found a potential match here, let's save it
        cumLen = sum(len(x) for x in SOP[:m+1])
        text = self.extractText(SOP, wl, m + 1) # Must be done before the SOP is modified
        TreeNode.splice(SOP, cumLen)
        return (budget, Parameter(self.name, text))
      
      # Capture everything here if next node is an optional node and got a 0 score
      if isinstance(nextNode, OptionalNode):
        nextNodeIndex = nextNodeIndex + 1
        continue
      
      # Not a optional node so let's return 
      return (0.0, None)

  def dump(self):
    print("ParametricNode with name {}".format(self.name))




class OptionalNode(TreeNode):
  """ An optional node is a node that has multiple possible SOPs but none is useful for intent processing """
  def __init__(self, optionalText, parent = None):
    """ optionalText is a text or a list of text """
    super().__init__(parent)
    self.texts = []
    
    if isinstance(optionalText, str):
      optionalText = [optionalText]

    self.optionalText = optionalText

    for text in optionalText:
      self.texts.append(submap.discode(TreeNode.splitToSOP(text)))

  def matchSOP(self, SOP, budget, wl):
    if budget <= 0:
      return (0.0, None)

    if len(SOP) == 0:
      return (budget, None)

    scores = []
    consumed = []
    # Find the optional node with the highest score
    for text in self.texts:
      t = budget
      t = confusionMatrix.confuseScorePre(text, SOP, t)
      if (TreeNode.verbosity > 1):
        print("Opt match {} SOP{} T{}".format(t, SOP, text))
      if t[0] <= 0:
        scores.append(0)
        consumed.append(0)
      else:
        scores.append(t[0])
        consumed.append(len(text))

    # Find the maximum score here
    m = scores.index(max(scores))
    if scores[m] > 0:
      # Splice the string from what's recognized so far
      consumedLen = sum([len(self.texts[m][x]) for x in range(0, consumed[m])])
      TreeNode.splice(SOP, consumedLen)
      return (scores[m], Optional(self.optionalText[m]))
    
    # No optional found, let's mark it
    return (budget, None)

  def dump(self):
    print("OptionalNode with text {}".format(self.texts))



class EndNode(TreeNode):
  """ An end node is a node that terminate an utterance, it doesn't accept any lingering utterance when it's reached.
      If there's still text to match against, it'll return no match """
  def __init__(self, parent = None):
    super().__init__(parent)

  def matchSOP(self, SOP, budget, wl):
    if budget <= 0 or len(SOP) > 0:
      return (0.0, None)
    return (budget, None)

  def dump(self):
    print("EndNode")

