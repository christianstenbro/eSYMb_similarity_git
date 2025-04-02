from otree.api import *
from random import shuffle, choice
from con1_aesthetics.esymblib import *

# from scipy import stats
# from skimage.metrics import mean_squared_error, structural_similarity
# from skimage.measure import moments_central, moments_normalized, moments_hu
# from sklearn.metrics.pairwise import euclidean_distances, cosine_distances
import io
import base64
import numpy
import pathlib

import skimage.io, skimage.transform, skimage.color


# import redis
# from ast import literal_eval

# r = redis.Redis(host="localhost", port=6379, decode_responses=True)

"""
moderation client

"""


class C(BaseConstants):
    NAME_IN_URL = "moderation"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    # ROUNDS = 1
    # NUM_STIM = 4
    # INSTRUCTIONS_TEMPLATE = "con0_practice/Instructions.html"
    SURFACE_OPTIONS = [
        f"/static/objects_decoration/Object trace {i}.png" for i in range(1, 8 + 1)
    ]
    PATTERN_SEED = [
        "/static/seeds/practice_trial2.png",
        "/static/seeds/foil_1.png",
        "/static/seeds/foil_2.png",
        "/static/seeds/foil_3.png",
    ]
    IMG_DIM = 155
    GRID_DIM = 312


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


def vars_for_admin_report(subsession):
    # TODO ?
    pass


def load_img_b64(img: str) -> numpy.ndarray:
    return load_preprocess_img(io.BytesIO(base64.b64decode(img[22:])))


def load_img_filename(img: str) -> numpy.ndarray:
    path = pathlib.Path("_static") / pathlib.Path(*pathlib.PurePath(img).parts[2:])
    return load_preprocess_img(path)


def load_preprocess_img(filepath) -> numpy.ndarray:
    im = 1 - skimage.color.rgb2gray(
        skimage.color.rgba2rgb(skimage.io.imread(filepath, plugin="pil"))
    )
    return im


def pattern_choices(player):
    return list(range(1, C.NUM_STIM + 1))


def get_pattern_image(player, pattern):
    return C.PATTERN_SEED[pattern - 1]


def get_judge_image(player: Player, img: int) -> str:
    if img == 1:
        return C.PATTERN_SEED[0]
    else:
        return choice(C.PATTERN_SEED[1:])


def accept_save_latest_drawing(player: Player):
    player.drawing = get_latest_drawing(player, Drawing)[1].drawing


class Moderate(Page):

    @staticmethod
    def live_method(player, data):
        if "event" not in data:
            print(f"ERROR: Data recieved, no event found {data}")
            return

        match data["event"]:
            case "init":
                # page reload or first (late?) load
                jobs = moderation_init()
                if len(jobs) == 0:  # TODO check if this is the right test
                    message = {"event": "update_empty"}
                else:
                    message = {"event": "update", "jobs": jobs}
                return {player.id_in_group: message}

            case "ping":
                # are there any new drawings up for moderation?
                jobs = moderation_init()
                if len(jobs) == 0:  # TODO check if this is the right test
                    message = {"event": "update_empty"}
                else:
                    message = {"event": "update", "jobs": jobs}
                return {player.id_in_group: message}

            case "accept":
                # moderator clicked "accept" on a drawing
                moderation_change_status(data["id"], "accept")
                return
            case "reject":
                # moderator clicked "reject"
                moderation_change_status(data["id"], "reject")
                return

        print(f"live_method ERROR: no event case matching: {data}")
        return


page_sequence = [Moderate]
