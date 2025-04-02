from otree.api import *



"""
resources:
https://www.otree.org/newformat.html
otree.readthedocs.io
https://code.djangoproject.com/wiki/Emacs

drawing similarity: judy tan, bill thompson, gary lupian
- https://scikit-image.org/docs/stable/api/skimage.metrics.html#skimage.metrics.hausdorff_distance
- https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance_matrix.html
- https://www.geeksforgeeks.org/how-to-calculate-mahalanobis-distance-in-python/


deep learning image similarity:
- opencv2?
- sentence-transformers + CLIP https://stackoverflow.com/questions/11541154/checking-images-for-similarity-with-opencv

drawing outside the canvas -> error 

"""

class C(BaseConstants):
    NAME_IN_URL = 'goodbye'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    LINK = "https://forms.gle/9Y9FC8N6mshneKJcA"


class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class Goodbye(Page):
    pass

page_sequence = [
    Goodbye
]
