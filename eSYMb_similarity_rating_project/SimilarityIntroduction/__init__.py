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
    NAME_IN_URL = "LinePractice"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    ROUNDS = 1
    NUM_STIM = 0
    INSTRUCTIONS_TEMPLATE = "SimilarityIntroduction/Instructions.html"
    SURFACE_OPTIONS = [
        f"/static/similarity/objects_decoration/Object trace {i}.png"
        for i in range(1, 8 + 1) # figure out what surface options refers to
    ]
    # PATTERN_SEED = [
    #     "/static/esymb_transmission/seeds/practice_trial2.png",
    #     "/static/esymb_transmission/seeds/foil_1.png",
    #     "/static/esymb_transmission/seeds/foil_2.png",
    #     "/static/esymb_transmission/seeds/foil_3.png",
    # ]
    # IMG_DIM = 155
    # GRID_DIM = 312

    # C: Commenting the above out this effectively removed the stimuli


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    prolific_id = models.StringField(default=str("NA"))
    drawing = models.LongStringField()
    linecount = models.IntegerField()
    surface = models.IntegerField()
    startPosData = models.StringField(blank=True) # blank=True makes the field optional
    angleData = models.StringField(blank=True)


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


# Defining consent page structure
    
class ConsentPage(Page):
    @staticmethod
    def vars_for_template(player):
        return {"instructions_hidden": ".show"}

class Consent_1(ConsentPage):
    # stores the prolific ID in the database
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.prolific_id = player.participant.label

class Consent_2(ConsentPage):
    pass

class Consent_3(ConsentPage):
    pass

class Consent_4(ConsentPage):
    pass

class Consent_5(ConsentPage):
    pass

class Consent_6(ConsentPage):
    pass

class Consent_7(ConsentPage):
    pass

class Consent_8(ConsentPage):
    pass

# Defining instruction pages

class InstructionPage(Page):
    @staticmethod
    def vars_for_template(player):
        return {"instructions_hidden": ".show"}

class Instruction_1(InstructionPage):
    pass

class Instruction_2(InstructionPage):
    pass

class Instruction_3(InstructionPage):
    pass

class Instruction_4(InstructionPage):
    pass


# Defining other pages

class Introduction(Page):

    @staticmethod
    def vars_for_template(player):
        return {"instructions_hidden": ".show"}


class Decorate(Page):
    form_model = "player"
    form_fields = ["drawing", "linecount", "startPosData", "angleData"]

    @staticmethod
    
    def error_message(player, values):
        if "drawing" in values:
            del values["drawing"]
        m = dict()
        if "linecount" not in values or not values["linecount"] >= 1: # allows for submitting any number of lines except 0
            m["linecount"] = "Please draw at least one line to proceed"
        return m

    def vars_for_template(player):
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
            #"surface": C.SURFACE_OPTIONS[player.surface - 1],
        }
    
page_sequence = [
    # Consent_1, 
    # Consent_2, 
    # Consent_3, 
    # Consent_4, 
    # Consent_5, 
    # Consent_6, 
    # Consent_7, 
    # Consent_8,
    Instruction_1,
    Instruction_2,
    Instruction_3,
    Instruction_4,
    #Decorate,
]
