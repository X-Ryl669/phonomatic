from phonomatic.confusionmatrix import IPASubmap, ConfusionMatrix

def test_IPASubmap():
    """Test IPA submap"""
    sm = IPASubmap()
    a = sm.discode("insanity is doing the same thing over and over again")
    b = sm.discode("insanity is doing the same thing over and over again")
    assert a == b, "Discoding same text failed"
    a = sm.discode("insanity is doing the same thing over and over again".split(" "))
    b = sm.discode("insanity is doing the same thing over and over again".split(" "))
    assert a == b, "Discoding same list failed"

def test_confusionmatrix():
    """Test confusion matrix"""
    cm = ConfusionMatrix()
    a = cm.confuseScore("insanity is doing the same thing over and over again", "insanity is doing the same thing over and over again")
    assert a == 1.0, "ConfuseScore of same text failed"
    a = cm.confuseScore("insanity is doing the same thing over and over again".split(" "), "insanity is doing the same thing over and over again".split(" "))
    assert a == 1.0, "ConfuseScore of same list failed"
    a = cm.confuseScore("insanity is doing the same thing over and over again", "insanity is doing the same thing uver and over again")
    assert a == 0.0, "ConfuseScore of different text failed"
    a = cm.confuseScore("insanity is doing the same thing over and over again", "insanity is doing the same thing uver and over again", 2.0)
    assert a == 1.0, "ConfuseScore of replacemed char failed"
    a = cm.confuseScore("insanity is doing the same thing over and over again", "insanity is doing the same thing ver and over again", 2.0)
    assert a == 1.0, "ConfuseScore of deleted char failed"
    a = cm.confuseScore("insanity is doing the same thing over and over again", "insanity is doing the same thing oover and over again", 2.0)
    assert a == 1.0, "ConfuseScore of inserted char failed"
