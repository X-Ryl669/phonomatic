# -*- coding: utf-8 -*-

# Results of matching
class Result(object):
  def __init__(self, id):
    self.id = id
  
  def __str__(self):
    return self.id

class Optional(Result):
  """ An optional node was detected, this stores the optional text that matched. """
  def __init__(self, text):
    super().__init__(text)

class ID(Result):
  """ An identified was detected, this stores the identifier that matched. """
  def __init__(self, id):
    super().__init__(id)

class Parameter(Result):
  """ A parameter was detected, this stores the actual text found for the parameter. """
  def __init__(self, id, value):
    super().__init__(id)
    self.value = value

  def __str__(self):
    return super().__str__() + " = " + self.value