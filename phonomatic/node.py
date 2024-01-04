# -*- coding: utf-8 -*-
from .confusionmatrix import IPASubmap, ConfusionMatrix
import epitran

submap = IPASubmap()

class TreeNode(object):
  """ A tree node in the intent graph. There are multiple possible type of TreeNode object
      The *basic* version is a textual version that must match 1:1 with the expressed string
      of phoneme (SOP)
      The *alternative* version allow multiple choice of SOP from a limited set of possibilities
      The *parametric* version allow any value that are well defined for the language
      The *optional* version is a node that would also match being missing or 1:1
      The *leaf* version is a node that used to store an identifier for this branch
  """
  def __init__(self, parent = None):
    self.parent = parent
    self.children = []

  def appendChild(self, child):
    assert isinstance(child, TreeNode)
    self.children.append(child)

  def matchText(self, text, budget):
    """ Match the given text with the given allowed budget.
        The text is first converted to SOP (you can use matchSOP if you already have the SOP
        The tree is followed as long as the budget isn't spent for a branch.
        This method returns the node with the highest budget if one found with a remaining budget
        or None if none matched withing the budget
    """
    return self.matchSOP(submap.discode(text.split(' ')), budget)

  def matchSOP(self, SOP, budget):
    pass

class BasicNode(TreeNode):

  def __init__(self, text, parent = None):
    super().__init__(parent)
    self.text = text.split(' ')
    self.SOP = submap.discode(text)


class AlternativeNode(TreeNode):
  def __init__(self, alternatePossibilities, parent = None):
    super().__init__(parent)
    self.forms = forms
    self.SOPforms = [submap.discode(text) for text in alternatePossibilities]

class ParametricNode(TreeNode):
  def __init__(self, variant, parent = None):
      super().__init__(parent)
      self.variant = variant
      self.value = None

class OptionalNode(TreeNode):
  def __init__(self, text, parent = None):
    super().__init__(parent)
    self.text = text
    self.SOP = submap.discode(text)

class LeafNode(TreeNode):
  def __init__(self, id, parent = None):
    super().__init__(parent)
    self.id = id


