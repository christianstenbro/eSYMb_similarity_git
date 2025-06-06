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

# defining parameters (should correspond to the ones in the stimSet gen script)
ratings_pr_drawing = 7
num_participants = 100
num_total_drawings = 4751
num_rounds = 3
num_breaks = 2

stim_set_size = math.ceil(num_total_drawings * ratings_pr_drawing / num_participants)

drawings_pr_round = math.ceil(stim_set_size / num_rounds)

# setting up classes
class C(BaseConstants):
    NAME_IN_URL = "SimilarityRatingExperiment" 
    PLAYERS_PER_GROUP = None # not relevant to our experiment either, I suppose
    NUM_ROUNDS = num_rounds + num_breaks
    INSTRUCTIONS_TEMPLATE = "SimilarityRatingExperiment/Instructions.html" 
    IMG_DIM = 400 # could be the dimensions of the shown image
    GRID_DIM = 312 # could be the dimensions of the drawing surface
    STIM_DB = pd.read_csv("_static/BTL/stims_memorability.csv") # this file links to the stimuli images. 
    DRAWINGS_PR_ROUND = drawings_pr_round

# pass probably = not relevant for this experiment
class Subsession(BaseSubsession):
    pass

# pass probably = not relevant for this experiment
class Group(BaseGroup):
    pass

# this is relevant! Check out the otree documentation for an explanation of the data types
class Player(BasePlayer):
    prolific_id = models.StringField(default=str("NA"))
    #playerid = models.IntegerField()
    # adding new variables for the sim.experiment
    imageRatings = models.StringField(blank=True)
    imageIndices = models.StringField(blank=True)
    stimIndices = models.StringField(blank=True)
    
# def creating_session(subsession):
#     subsession.session.vars["memorability_db"] = C.STIM_DB)


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


class Break(Page):
    pass

class Break_2(Page):
    pass

class AskID(Page):
    form_model = "player"
    form_fields = ["playerid"]

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Rating_modification(Page):
    form_model = "player"
    form_fields = [#"drawing", 
                   #"linecount", 
                   #"startPosData", 
                   #"angleData", 
                   "imageRatings", 
                   "imageIndices",
                   "stimIndices"]

    @staticmethod # sending variables to the HTML template
    def vars_for_template(player):
        
        instructions_per_round = {
            1: 'Rate the similarity:',
            # 2: 'Draw two lines:',
            # 3: 'Draw three lines:',
            # 4: 'Draw four lines:',
            # 5: 'Draw five lines:',
            # 6: 'Draw six lines:',
        }

        return {
            "instructions_hidden": "",
            "round_instruction": instructions_per_round[1],
            "round_number": player.round_number,
            "id_in_group": player.id_in_group, # strangely, I can't use ID in session . . .
            "drawings_pr_round": C.DRAWINGS_PR_ROUND,
        }
    
    # send the round number variable to the backend java script
    def js_vars(player):
        return dict(
            roundNumber=player.round_number,
        )
 
    # # send the round number variable to the template (HTML page)
    # def vars_for_template(player):
    #     return dict(
    #     round_number=player.round_number,
    #     )
        

    #def is_displayed(player):
    #    return player.round_number <= 6

class Rating_modification_2(Page):
    form_model = "player"
    form_fields = ["imageRatings", 
                   "imageIndices",
                   "stimIndices"]

    @staticmethod # sending variables to the HTML template
    def vars_for_template(player):
        
        instructions_per_round = {
            1: 'Rate the similarity:',
        }

        return {
            "instructions_hidden": "",
            "round_instruction": instructions_per_round[1],
            "round_number": player.round_number,
            "id_in_group": player.id_in_group, # strangely, I can't use ID in session . . .
            "drawings_pr_round": C.DRAWINGS_PR_ROUND,
        }
    
class Rating_modification_3(Page):
    form_model = "player"
    form_fields = ["imageRatings", 
                   "imageIndices",
                   "stimIndices"]

    @staticmethod # sending variables to the HTML template
    def vars_for_template(player):
        
        instructions_per_round = {
            1: 'Rate the similarity:',
        }

        return {
            "instructions_hidden": "",
            "round_instruction": instructions_per_round[1],
            "round_number": player.round_number,
            "id_in_group": player.id_in_group, # strangely, I can't use ID in session . . .
            "drawings_pr_round": C.DRAWINGS_PR_ROUND,
        }

### the definitive page set-up
    
class Rating_modification_round_structure(Page):
    form_model = "player"
    form_fields = ["imageRatings", 
                   "imageIndices",
                   "stimIndices"]

    @staticmethod # sending variables to the HTML template
    def vars_for_template(player):
        
        instructions_per_round = {
            1: 'Rate the similarity:',
        }

        return {
            "instructions_hidden": "",
            "round_instruction": instructions_per_round[1],
            "round_number": player.round_number,
            "id_in_group": player.id_in_group, # strangely, I can't use ID in session . . .
            "drawings_pr_round": C.DRAWINGS_PR_ROUND,
        }
    
    def is_displayed(player):
           return player.round_number in [1, 3, 5]

class BreakPage(Page):

    @staticmethod
    def is_displayed(player: Player):
        """ Show break after rounds 2 and 4 (but not on the last round) """
        return player.round_number in [2, 4]

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
    Goodbye,
]
