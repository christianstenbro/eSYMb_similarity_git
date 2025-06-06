from otree.api import *
from random import shuffle, choice
from con1_aesthetics.esymblib import *
import io
import base64
import numpy as np
import pathlib
import pandas as pd
import skimage.io, skimage.transform, skimage.color
import json
import math

"""


"""

# Parameters that can be modified.
# These parameters should correspond to the ones in the stimSet gen R-script
ratings_pr_drawing = 5
num_participants = 100
num_total_drawings = 1584+1452+4750 # drawings from study 1, 2 and 3
num_rounds = 3
num_attention_checks_in_total = 6

# Parameters that are set automatically based on the above
num_breaks = num_rounds - 1
stim_set_size = math.ceil(num_total_drawings * ratings_pr_drawing / num_participants) + num_attention_checks_in_total
drawings_pr_round = math.ceil(stim_set_size / num_rounds)

# Setting up classes --> these can be imported into front-end
class C(BaseConstants):
    NAME_IN_URL = "SimilarityRatingExperiment" 
    PLAYERS_PER_GROUP = None # not relevant to our experiment either, I suppose
    NUM_ROUNDS = num_rounds + num_breaks
    INSTRUCTIONS_TEMPLATE = "SimilarityRatingExperiment/Instructions.html" 
    IMG_DIM = 400 # could be the dimensions of the shown image
    GRID_DIM = 312 # could be the dimensions of the drawing surface
    DRAWINGS_PR_ROUND = drawings_pr_round
    NUM_ATTENTION_CHECKS_IN_TOTAL = num_attention_checks_in_total

# pass probably = not relevant for this experiment
class Subsession(BaseSubsession):
    pass

# pass probably = not relevant for this experiment
class Group(BaseGroup):
    pass

# this is relevant! Check out the otree documentation for an explanation of the data types
class Player(BasePlayer):
    prolific_id = models.StringField(default=str("NA"))
    imageRatings = models.StringField(blank=True)
    imageIndices = models.StringField(blank=True)
    stimIndices = models.StringField(blank=True)
    ratingTimes = models.StringField(blank=True)
    isAttentionCheck = models.StringField(blank=True)
    withinExpectedRatingRange = models.StringField(blank=True)
    originalFileName = models.StringField(blank=True)
    technicalIssues = models.StringField(label="Did you encounter any technical issue when doing the experiment? Please let us know so we can address it!", 
                                         blank=True)
    dataValidity = models.StringField(label="Is there any reason why we should not use your data?", 
                                      blank=True)
    
# PAGES
class Introduction(Page):

    @staticmethod
    def vars_for_template(player):
        return {"instructions_hidden": ".show"}

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        player.prolific_id = player.participant.label

def playerid_error_message(player, value):
    print("validating", value)
    print(pd.unique(C.STIM_DB.participant))
    if value not in C.STIM_DB.participant.values:
        print("ERROR")
        return "Please enter a valid ID"


class AskID(Page):
    form_model = "player"
    form_fields = ["playerid"]

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

class Rating_modification_round_structure(Page):
    form_model = "player"
    form_fields = ["imageRatings", 
                   "imageIndices",
                   "stimIndices",
                   "ratingTimes", 
                   "isAttentionCheck",
                   "withinExpectedRatingRange",
                   "originalFileName"]

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
            "num_attention_checks_in_total": C.NUM_ATTENTION_CHECKS_IN_TOTAL,
        }
    
    def is_displayed(player):
           return player.round_number in [1, 3, 5]


class BreakPage(Page):

    @staticmethod
    def is_displayed(player: Player):
        """ Show break after rounds 2 and 4 (but not on the last round) """
        return player.round_number in [2, 4]

class FinalQuestions(Page):
    form_model = "player"
    form_fields = ["technicalIssues", 
                   "dataValidity"]
    
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

class Goodbye(Page):
    form_model = "player"

    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

# defines the sequence of pages to be played
page_sequence = [
    # AskID,
    Introduction,
    Rating_modification_round_structure,
    BreakPage,
    FinalQuestions,
    Goodbye,
]
