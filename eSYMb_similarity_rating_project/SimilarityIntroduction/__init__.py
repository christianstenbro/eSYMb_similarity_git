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

# defining parameters (for the practice round only)
drawings_pr_round = 1

# setting up classes
class C(BaseConstants):
    NAME_IN_URL = "SimilarityIntroduction" 
    PLAYERS_PER_GROUP = None # not relevant to our experiment either, I suppose
    NUM_ROUNDS = 1
    INSTRUCTIONS_TEMPLATE = "SimilarityRatingExperiment/Instructions.html" 
    IMG_DIM = 400 # could be the dimensions of the shown image
    GRID_DIM = 312 # could be the dimensions of the drawing surface
    DRAWINGS_PR_ROUND = drawings_pr_round

# defining pages

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    prolific_id = models.StringField(default=str("NA"))
    #playerid = models.IntegerField()
    # adding new variables for the sim.experiment
    imageRatings = models.StringField(blank=True)
    imageIndices = models.StringField(blank=True)
    stimIndices = models.StringField(blank=True)


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

class Consent_9(ConsentPage):
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

class Instruction_5(InstructionPage):
    pass

# Defining rating practice page

class Rating_practice(Page):
    form_model = "player"
    form_fields = ["imageRatings", 
                   "imageIndices",
                   "stimIndices"]

    @staticmethod # sending variables to the HTML template
    def vars_for_template(player):
        
        instructions_per_round = {
            1: 'How do you rate the similarity of these drawings? Use the scale below to respond.',
        }

        return {
            "instructions_hidden": "",
            "round_instruction": instructions_per_round[1],
            "round_number": player.round_number,
            "id_in_group": player.id_in_group, # strangely, I can't use ID in session . . .
            "drawings_pr_round": C.DRAWINGS_PR_ROUND,
        }
    
    # def is_displayed(player):
    #        return player.round_number in [1, 3, 5]

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
    Consent_1, 
    Consent_2, 
    Consent_3, 
    Consent_4, 
    Consent_5, 
    Consent_6, 
    Consent_7, 
    Consent_8,
    Consent_9,
    Instruction_1,
    Instruction_2,
    Instruction_3,
    Instruction_4,
    Instruction_5,
    Rating_practice,
    #Decorate,
]
