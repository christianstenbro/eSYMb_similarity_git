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
import pandas as pd

import skimage.io, skimage.transform, skimage.color


"""


"""

# setting up classes
# I (Christian) am not sure I understand these yet – somehow they are connected to the data

# first, some constants are instantiated. Some of these are easy to understand
class C(BaseConstants):
    NAME_IN_URL = "memorability" # name of page
    PLAYERS_PER_GROUP = None # not relevant to our experiment either, I suppose
    NUM_ROUNDS = 36 # would be six
    INSTRUCTIONS_TEMPLATE = "memorability/Instructions.html" # link to instructions, although I don't see the instruction in the file
    IMG_DIM = 400 # could be the dimensions of the shown image (will not be relevant for experiment 1)
    GRID_DIM = 312 # could be the dimensions of the drawing surface - but seems not to be.
    STIM_DB = pd.read_csv("_static/esymb_transmission/stims_memorability.csv") # this file links to the stimuli images. 
    
    # perhaps the easiest thing right now is to make a demo experiment inside of the ESYMB_TRANSMISSION folder
    # to not have to worry about the folder structure stuff...

# pass probably = not relevant for this experiment
class Subsession(BaseSubsession):
    pass

# pass probably = not relevant for this experiment
class Group(BaseGroup):
    pass

# this is relevant! Check out the otree documentation for an explanation of the data types
class Player(BasePlayer):
    playerid = models.IntegerField()
    drawing = models.LongStringField()
    linecount = models.IntegerField()


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


def get_drawing_to_remember(player):
    # filter the db to the right participant and the right round
    # print(player.in_round(1))
    selection = (
        C.STIM_DB.loc[(C.STIM_DB.participant == player.in_round(1).playerid)]
        .loc[(C.STIM_DB.trial == player.round_number)]
        .reset_index()
    )
    # print(selection)
    return selection.loc[0, "drawing"]


class Remember(Page):
    timeout_seconds = 3

    @staticmethod
    def vars_for_template(player):
        return {"drawing": get_drawing_to_remember(player)}


class Decorate(Page):
    form_model = "player"
    form_fields = ["drawing", "linecount"]

    @staticmethod
    def vars_for_template(player):
        return {
            "instructions_hidden": "",
        }

# defines the sequence of pages to be played
page_sequence = [
    AskID,
    Introduction,
    Remember,
    Decorate,
]
