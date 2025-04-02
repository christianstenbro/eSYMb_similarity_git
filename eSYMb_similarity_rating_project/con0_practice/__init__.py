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

import skimage.io, skimage.transform, skimage.color


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
    NAME_IN_URL = "study0"
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    ROUNDS = 1
    NUM_STIM = 4
    INSTRUCTIONS_TEMPLATE = "con0_practice/Instructions.html"
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
    ERROR_THRESHOLD = 35


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    playing = models.IntegerField(blank=True)


class Player(BasePlayer):
    drawing = models.LongStringField()
    judge = models.IntegerField()
    linecount = models.IntegerField()
    surface = models.IntegerField()
    error_hd = models.FloatField()
    error_hu_e = models.FloatField()
    error_hu_c = models.FloatField()
    error_hu_i1 = models.FloatField()
    error_hu_i2 = models.FloatField()
    error_hu_i3 = models.FloatField()
    error_lewis = models.FloatField()


class Drawing(ExtraModel):
    player = models.Link(Player)
    attempt = models.IntegerField()
    drawing = models.LongStringField()
    similarity = models.FloatField()
    status = models.StringField()


def creating_session(subsession):
    labels = [
        str(i) for i in range(1, subsession.session.config["num_demo_participants"] + 1)
    ]
    for player, label in zip(subsession.get_players(), labels):
        player.participant.label = label


def vars_for_admin_report(subsession):
    ps = [p.participant for p in subsession.get_players()]
    return {
        "participant_waittimes": [
            {
                "id": p.id_in_session,
                "wait1": 0 if p.vars["con2_generation"] % 3 else 1,
                "wait2": max(0, p.vars["con3_generation"] - p.vars["con2_generation"]),
            }
            for p in ps
        ]
    }


def moderation_img_distance(player, drawing):
    im1 = load_img_filename(get_pattern_image(player, 1))
    im2 = load_img_b64(drawing)
    # skimage.io.imsave("/tmp/tmpimg/im1.png", im1, plugin="pil")
    # skimage.io.imsave("/tmp/tmpimg/im2.png", im2, plugin="pil")

    val = calc_hu_i3(calc_hu_moments(im1), calc_hu_moments(im2))
    del im1
    del im2
    return val


# def drawing_error_message(player, value):
#     return
#     im1 = load_img_filename(get_pattern_image(player, 1))
#     im2 = load_img_b64(value)

#     # print((im2 == 0).sum(), (im2 == 1).sum(), im2.shape)

#     skimage.io.imsave("/tmp/tmpimg/im1.png", im1, plugin="pil")
#     skimage.io.imsave("/tmp/tmpimg/im2.png", im2, plugin="pil")
#     # error = mean_squared_error(im1, im2)
#     # error = structural_similarity(im1, im2, data_range=255)

#     # Lewis et al. predict 26% of variability of human similarity
#     # judgement of two drawings with a model using hausdorff,
#     # mahalanobis, and euclidian distance. They also use stroke count
#     # and length as predictors, but those are constant in our case
#     # https://escholarship.org/content/qt702482s5/qt702482s5.pdf

#     hu1 = calc_hu_moments(im1)
#     hu2 = calc_hu_moments(im2)
#     hu_euclid = euclidean_distances([hu1], [hu2])[0][0]
#     hu_cosine = cosine_distances([hu1], [hu2])[0][0]

#     hu_i1 = calc_hu_i1(hu1, hu2)
#     hu_i2 = calc_hu_i2(hu1, hu2)
#     hu_i3 = calc_hu_i3(hu1, hu2)

#     hd = numpy.log(skimage.metrics.hausdorff_distance(im1, im2))
#     mh = 0
#     eu = euclidean_distances([im1.flatten()], [im2.flatten()])[0][0]
#     lewis = hd * 0.37 + mh * 0.25 + eu * (-0.26)
#     # similarity = hd * 0.37
#     # error = 1 - similarity
#     # error = hd

#     del im1
#     del im2

#     error = hu_i3

#     # if similarity < C.SIMILARITY_THRESHOLD:
#     if error > C.ERROR_THRESHOLD:
#         return f"Your image is too different from the given pattern. Error {error}. Please try again."
#     else:
#         player.error_hd = hd
#         player.error_hu_e = hu_euclid
#         player.error_hu_c = hu_cosine
#         player.error_lewis = lewis
#         player.error_hu_i1 = hu_i1
#         player.error_hu_i2 = hu_i2
#         player.error_hu_i3 = hu_i3


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

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1
        return 1 not in [p.field_maybe_none("judge") for p in player.in_all_rounds()]


class Decorate(Page):
    form_model = "player"
    form_fields = ["drawing", "linecount"]

    @staticmethod
    def error_message(player, values):
        if "drawing" in values:
            del values["drawing"]
        m = dict()
        if "linecount" not in values or not values["linecount"] == 6:
            m["linecount"] = "Please draw 6 lines"
        return m

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1
        return 1 not in [p.field_maybe_none("judge") for p in player.in_all_rounds()]

    @staticmethod
    def live_method(player, data):
        if "event" not in data:
            print(f"ERROR: Data recieved, no event found {data}")
            return

        match data["event"]:
            case "check_drawing":
                if "drawing" not in data:
                    print(f"ERROR: Drawing not found {data}")
                    return

                error = moderation_img_distance(player, data["drawing"])

                new_drawing = Drawing.create(
                    player=player,
                    attempt=get_latest_drawing(player, Drawing)[0] + 1,
                    similarity=error,
                    drawing=data["drawing"],
                )  # save drawing in question

                print(new_drawing)
                if error > C.ERROR_THRESHOLD:
                    new_drawing.status = "waiting"
                    moderation_submit(
                        player, new_drawing, get_drawing_template(player), C
                    )
                    message = {"event": "drawing_wait"}
                    return {player.id_in_group: message}
                else:
                    new_drawing.status = "accepted_no_moderation"
                    # accept drawing and move on
                    message = {"event": "drawing_accepted"}
                    return {player.id_in_group: message}
            case "init":
                latest_drawing = get_latest_drawing(player, Drawing)[1]
                match moderation_status(player, C):
                    case "wait":
                        message = {
                            "event": "init_con0",
                            "drawing": latest_drawing.drawing,
                        }
                        return {player.id_in_group: message}
                    case "accept":
                        latest_drawing.status = "accepted_moderation"
                        message = {"event": "drawing_accepted"}
                        return {player.id_in_group: message}
                    case "reject":
                        latest_drawing.status = "rejected_moderation"
                        message = {"event": "drawing_rejected"}
                        return {player.id_in_group: message}
                    case default:
                        message = {"event": "init_con0"}
                        return {player.id_in_group: message}

            case "ping":
                latest_drawing = get_latest_drawing(player, Drawing)[1]
                match moderation_status(player, C):
                    case "accept":
                        latest_drawing.status = "accepted_moderation"
                        message = {"event": "drawing_accepted"}
                        return {player.id_in_group: message}
                    case "reject":
                        latest_drawing.status = "rejected_moderation"
                        message = {"event": "drawing_rejected"}
                        return {player.id_in_group: message}
                    case "wait":
                        message = {"event": "pong"}
                        return {player.id_in_group: message}
                    case default:
                        print(f"live_method ping UNKNOWN STATUS {default}")

        print(f"live_method ERROR: no event case matching: {data}")
        return

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

    @staticmethod
    def before_next_page(player, timeout_happened):
        # print(f"before_next_page {player}")
        player.drawing = Drawing.filter(player=player)[-1].drawing


class Welcome(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


page_sequence = [
    Welcome,
    Introduction,
    Decorate,
]
