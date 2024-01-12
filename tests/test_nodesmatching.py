from phonomatic.node import TreeNode, BasicNode, AlternativeNode, ParametricNode, OptionalNode, EndNode

defaultLanguage = 'fra-Latn-p'

TreeNode.setLanguage(defaultLanguage)

import pdb


def test_NodeMatching():
    """Test Node matching"""
    root = TreeNode()

    root.appendChild(AlternativeNode([("open", "Ouvrez"), ("close", "Fermez")]))
    root.appendChild(BasicNode(("the", "les")))
    root.appendChild(AlternativeNode([("curtain", "rideaux"), ("cover", "volets")]))

    root.dump()

    a = root.matchText("Ouvrez les rideaux", 1.0)
    assert TreeNode.results_to_str(a) == ["open", "the", "curtain"]

    a = root.matchText("Ouvré lé riz d'eau", 2.0) # Notice how small the budget for error is here
    assert TreeNode.results_to_str(a) == ["open", "the", "curtain"]

    a = root.matchText("Fermez les volets", 1.0)
    assert TreeNode.results_to_str(a) == ["close", "the", "cover"]

    a = root.matchText("Fermée le veau les", 5.0) # Notice how small the budget for error is here
    assert TreeNode.results_to_str(a) == ["close", "the", "cover"]

def test_ComplexIntentMatching():
    """Test optional matching"""
    # Test alternative and basic combination ending by optional node
    root = TreeNode()


    root.appendChild(AlternativeNode([("open", "Ouvrez"), ("close", "Fermez")]))
    root.appendChild(BasicNode(("the", "les")))
    root.appendChild(AlternativeNode([("curtain", "rideaux"), ("cover", "volets")]))
    root.appendChild(OptionalNode(["s'il te plait", "s'il vous plait"]))

    root.dump()

    a = root.matchText("Ouvrez les rideaux", 1.0)
    assert TreeNode.results_to_str(a) == ["open", "the", "curtain"]

    a = root.matchText("Ouvrez les rideaux, s'il te plait", 1.0)
    assert TreeNode.results_to_str(a) == ["open", "the", "curtain"]

    a = root.matchText("Ouvrez les rideaux, s'il vous plé", 2.0)
    assert TreeNode.results_to_str(a) == ["open", "the", "curtain"]
    assert TreeNode.results_to_str(a, withOptionals = True) == ["open", "the", "curtain", "s'il vous plait"]

    # Test optional, alternative and basic combination
    root = TreeNode()

    root.appendChild(OptionalNode(["S'il te plait", "S'il vous plait"]))
    root.appendChild(AlternativeNode([("open", "Ouvrez"), ("close", "Fermez")]))
    root.appendChild(BasicNode(("the", "les")))
    root.appendChild(AlternativeNode([("curtain", "rideaux"), ("cover", "volets")]))
    root.appendChild(EndNode())

    root.dump()

    a = root.matchText("S'il vous plait, ouvrez les rideaux", 1.0)
    assert TreeNode.results_to_str(a) == ["open", "the", "curtain"]

    a = root.matchText("Ouvrez les rideaux, s'il te plait", 1.0)
    assert a == None

    a = root.matchText("Ouvrez les rideaux", 1.0)
    assert TreeNode.results_to_str(a) == ["open", "the", "curtain"]


def test_ComplexIntentMatchingWithParameter():
    """Test parametric matching"""
    # Test parametric with single optional at end
    root = TreeNode()

    root.appendChild(AlternativeNode([("increase", "Montez"), ("decrease", "Baissez")]))
    root.appendChild(BasicNode(("volume", "le volume de")))
    root.appendChild(ParametricNode("percent"))
    root.appendChild(OptionalNode(["pourcent"]))

    root.dump()

    a = root.matchText("Montez le volume de cinquante pourcent", 2.0)
    assert TreeNode.results_to_str(a) == ["increase", "volume", "percent = cinquante"]

    a = root.matchText("Montez le volume de quatre vingt dix huit pourcent", 2.0)
    assert TreeNode.results_to_str(a) == ["increase", "volume", "percent = quatre vingt dix huit"]

    # Test parametric at end
    root = TreeNode()

    root.appendChild(AlternativeNode([("increase", "Montez"), ("decrease", "Baissez")]))
    root.appendChild(BasicNode(("volume", "le volume de")))
    root.appendChild(ParametricNode("value"))

    root.dump()

    a = root.matchText("Montez le volume de cinquante", 2.0)
    assert TreeNode.results_to_str(a) == ["increase", "volume", "value = cinquante"]

    a = root.matchText("Montez le volume de quatre vingt dix huit", 2.0)
    assert TreeNode.results_to_str(a) == ["increase", "volume", "value = quatre vingt dix huit"]

    # Test parametric with multiple optionals and cork
    root = TreeNode()

    root.appendChild(AlternativeNode([("increase", "Montez"), ("decrease", "Baissez")]))
    root.appendChild(BasicNode(("volume", "le volume de")))
    root.appendChild(ParametricNode("value"))
    root.appendChild(OptionalNode(["pourcent"]))
    root.appendChild(OptionalNode(["decibels"]))
    root.appendChild(BasicNode(("thanks", "merci")))


    root.dump()

    a = root.matchText("Montez le volume de cinquante pourcent decibels merci", 3.0)
    assert TreeNode.results_to_str(a) == ["increase", "volume", "value = cinquante", "thanks"]

    a = root.matchText("Montez le volume de cinquante decibels merci", 3.0)
    assert TreeNode.results_to_str(a) == ["increase", "volume", "value = cinquante", "thanks"]

    a = root.matchText("Montez le volume de cinquante merci", 2.0)
    assert TreeNode.results_to_str(a) == ["increase", "volume", "value = cinquante", "thanks"]

    a = root.matchText("Montez le volume de cinquante voiture", 2.0)
    assert a == None
