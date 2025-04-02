from otree.api import *
from random import shuffle, choice
from con1_aesthetics.esymblib import *

# from scipy import stats
# from skimage.metrics import mean_squared_error, structural_similarity
# from skimage.measure import moments_central, moments_normalized, moments_hu
# from sklearn.metrics.pairwise import euclidean_distances, cosine_distances
import io
import base64
import numpy as np
import pathlib


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
    NAME_IN_URL = "practice"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    ROUNDS = 1
    NUM_STIM = 4
    INSTRUCTIONS_TEMPLATE = "memorability_practice/Instructions.html"
    SURFACE_OPTIONS = [
        f"/static/esymb_transmission/objects_decoration/Object trace {i}.png"
        for i in range(1, 8 + 1)
    ]
    PATTERN_SEED = [
        "/static/esymb_transmission/seeds/practice_trial2.png",
        "/static/esymb_transmission/seeds/foil_1.png",
        "/static/esymb_transmission/seeds/foil_2.png",
        "/static/esymb_transmission/seeds/foil_3.png",
    ]
    IMG_DIM = 155
    GRID_DIM = 312


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    drawing = models.LongStringField()
    linecount = models.IntegerField()
    surface = models.IntegerField()


def pattern_choices(player):
    return list(range(1, C.NUM_STIM + 1))


def get_pattern_image(player, pattern):
    return C.PATTERN_SEED[pattern - 1]


def get_drawing_template(player: Player):
    # get the src string of the drawing the player is supposed to look after
    if player_round(player, C) == 1:
        return get_pattern_image(player, 1)  # practice round is always number 1
    else:
        print("get_drawing_template: NOT IMPLEMENTED")


# PAGES
class Introduction(Page):
    @staticmethod
    def vars_for_template(player):
        return {"instructions_hidden": ".show"}


class Decorate(Page):
    form_model = "player"
    form_fields = ["drawing", "linecount"]

    @staticmethod
    def vars_for_template(player):
        if not player.field_maybe_none("surface"):
            used_surfaces = [
                s
                for s in [
                    p.field_maybe_none("surface") for p in player.in_previous_rounds()
                ]
                if s
            ]
            available_surfaces = [
                s
                for s in range(1, len(C.SURFACE_OPTIONS) + 1)
                if s not in used_surfaces
            ]
            player.surface = choice(available_surfaces)

        # surfacelist = surface_choices(player)
        # shuffle(surfacelist)
        patternlist = pattern_choices(player)
        shuffle(patternlist)
        return {
            "instructions_hidden": "",
            "patterns": [
                {
                    "value": v,
                    "image": get_pattern_image(player, v),
                    "checked": "checked" if v == 1 else "unchecked",
                }
                for v in patternlist
            ],
            "surface": C.SURFACE_OPTIONS[player.surface - 1],
        }


page_sequence = [
    Introduction,
    Decorate,
]
