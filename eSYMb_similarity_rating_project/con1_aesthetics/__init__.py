from otree.api import models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer, Page  # type: ignore [import]
from random import shuffle, choice
from otree.export import sanitize_for_csv
from .esymblib import *
import pandas as pd
import numpy as np
import csv

from otree.database import DBSession

"""
resources:
https://www.otree.org/newformat.html
otree.readthedocs.io
https://code.djangoproject.com/wiki/Emacs


- size? looks a bit different on my two screens, what about cobelab screens?
"""


class C(BaseConstants):
    NAME_IN_URL = "study1"
    PLAYERS_PER_GROUP = None
    # TOTAL_PARTICIPANTS = 12 # (session.config['transmissions']+1)*2
    NUM_STIM = 4
    NUM_REPETITIONS = 2
    NUM_ROUNDS = NUM_STIM * NUM_REPETITIONS
    ROUNDS = NUM_ROUNDS
    # NUM_TRANSMISSIONS_PER_CHAIN = session.config['transmissions']
    INSTRUCTIONS_TEMPLATE = "con1_aesthetics/Instructions.html"
    SURFACE_OPTIONS = [
        f"/static/esymb_transmission/objects_decoration/Object trace {i}.png"
        for i in range(1, 8 + 1)
    ]
    PATTERN_SEED = [
        "/static/esymb_transmission/seeds/seed_1.png",
        "/static/esymb_transmission/seeds/seed_2.png",
        "/static/esymb_transmission/seeds/seed_3.png",
        "/static/esymb_transmission/seeds/seed_4.png",
    ]
    IMG_DIM = 155
    IMG_DIM_SMALL = 100
    GRID_DIM = 312
    DRAWINGS_DB_LOCATION = "/opt/otree/data/esymbtransmission_decoration_{session}.csv"
    ERROR_THRESHOLD = 35


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    playing = models.IntegerField(blank=True)


class Player(BasePlayer):
    drawing = models.LongStringField()
    surface = models.IntegerField()
    pattern = models.IntegerField(widget=widgets.RadioSelect)
    chain = models.IntegerField()
    generation = models.IntegerField()  # generation 1-8
    linecount = models.IntegerField()


class Drawing(ExtraModel):
    player = models.Link(Player)
    attempt = models.IntegerField()
    pattern = models.IntegerField()
    drawing = models.LongStringField()
    similarity = models.FloatField()
    status = models.StringField()


# def linecount_error_message(player, value):
#     if value != 6:
#         return "Please draw 6 lines"

# def pattern_error_message(player, value):
#     print(value)
#     if value not in pattern_choices(player):
#         return "Please pick a pattern, then draw it below"
# # FUNCTIONS


def custom_export_save(subsession):
    rows = custom_export_iter()
    str_rows = ([sanitize_for_csv(ele) for ele in row] for row in rows)
    with open(
        f"/opt/otree/data/esymbtransmission_export_con1_{subsession.session.code}.csv",
        "w",
    ) as f:
        writer = csv.writer(f)
        writer.writerows(str_rows)
    print("Wrote con1 export data to disk")


def custom_export_iter():
    session = DBSession()

    print("Exporting con1 data")
    yield [
        "session",
        "participant",
        "time_started_utc",
        "chain",
        "subchain",
        "generation",
        "round",
        "pattern",
        "surface",
        "attempt",
        "status",
        "drawing",
    ]
    # print(type(players[0]))
    # return
    # data = session.query(Drawing).join(Player)
    # print(data.all())
    # return
    # data = session.query(Player, Drawing).filter(Drawing.player == Player.)

    for drawing in session.query(Drawing).outerjoin(Player):
        # for p in players:
        # print(p.attempt)
        # print(p.player.generation)
        player = drawing.player
        participant = player.participant
        # for attempt in Drawing.filter(player=p):
        yield [
            player.session.code,
            participant.code,
            participant.time_started_utc,
            player.chain,
            calc_subchain(player, C),
            player.generation,
            player.round_number,
            player.field_maybe_none("pattern"),
            player.surface,
            drawing.attempt,
            drawing.status,
            drawing.drawing,
        ]
        print(player.id_in_subsession, end=",")
    print()


def calc_subchain(player: BasePlayer, C: BaseConstants):  # type: ignore [no-redef]
    # a player object in some round
    if player.field_maybe_none("pattern"):  # we picked a pattern this round
        if player.generation == 1:
            return player.pattern
        elif player.session.config["continue_session"] and (
            player.generation == (player.session.vars["old_generation"] + 1)
        ):
            return player.pattern
        else:
            # print(player)
            prev_sender = get_player_by_chain_generation(
                player, player.chain, player.generation - 1
            )
            return calc_subchain(prev_sender.in_round(C.NUM_STIM + player.pattern), C)
    else:
        return "NA"


def creating_session(subsession):
    if not "order1" in subsession.session.vars:
        # num_players = (C.TOTAL_PARTICIPANTS // C.NUM_TRANSMISSIONS_PER_CHAIN) * C.NUM_TRANSMISSIONS_PER_CHAIN
        num_players = (subsession.session.config["transmissions"] + 1) * 2
        subsession.session.vars["order1"] = list(range(1, num_players + 1))

        n_transmissions = 3  # subsession.session.config['transmissions']
        num_players_per_chain = num_players // (n_transmissions)

        subsession.session.vars["new_drawings_db"] = pd.DataFrame(
            columns=[
                "session",
                "prev_session",
                "chain",
                "generation",
                "drawing1",
                "drawing2",
                "drawing3",
                "drawing4",
            ],
            index=range(1, num_players + 1),
        )

        if subsession.session.config["continue_session"]:
            subsession.session.vars["old_drawings_db"] = pd.read_csv(
                C.DRAWINGS_DB_LOCATION.format(
                    session=subsession.session.config["continue_session"]
                )
            )
            subsession.session.vars["old_generation"] = int(
                subsession.session.vars["old_drawings_db"].generation.max() - 1
            )

        # shuffle(subsession.session.vars['order']) # TODO: do we unrandomize this condition to make participating easier?
        for i, p in enumerate(subsession.session.vars["order1"]):
            player = get_player_by_subsession_id(subsession, p)

            #### depth-first assignment
            # player.chain = (i // (num_players_per_chain)) + 1
            # player.generation = (i % (num_players_per_chain)) + 1

            #### width-first assignment
            if subsession.session.config["continue_session"]:
                player.generation = (
                    (i // (num_players_per_chain))
                    + 1
                    + subsession.session.vars["old_generation"]
                )
            else:
                player.generation = (i // (num_players_per_chain)) + 1
            player.chain = (i % (num_players_per_chain)) + 1

            # save it for other apps
            player.participant.vars["con1_generation"] = player.generation
    else:
        # fetch generation and chain from round 1
        for player in subsession.get_players():
            player.generation = player.in_round(1).field_maybe_none("generation")
            player.chain = player.in_round(1).field_maybe_none("chain")


def get_my_partner(player: Player) -> Player:
    assert player.generation > 1
    return get_player_by_chain_generation(player, player.chain, player.generation - 1)


def pattern_choices(player):
    return gen_pattern_choices(player, C)


def get_surface_image(player, i):
    return C.SURFACE_OPTIONS[
        player.in_round(
            C.NUM_STIM * ((player.round_number - 1) // C.NUM_STIM) + i + 1
        ).surface
        - 1
    ]


def get_surface_image_direct(player, i):
    return C.SURFACE_OPTIONS[player.in_round(i + 1).surface - 1]


def get_pattern_image(player, pattern):
    assert pattern in [1, 2, 3, 4]
    if player.generation == 1:
        return C.PATTERN_SEED[pattern - 1]
    elif player.session.config["continue_session"] and (
        player.generation == (player.session.vars["old_generation"] + 1)
    ):
        return (
            player.session.vars["old_drawings_db"]
            .loc[
                (player.session.vars["old_drawings_db"]["chain"] == player.chain)
                & (
                    player.session.vars["old_drawings_db"]["generation"]
                    == player.generation - 1
                ),
                "drawing" + str(pattern),
            ]
            .reset_index(drop=True)[0]
        )
    else:
        return get_my_partner(player).in_round(C.NUM_STIM + pattern).drawing


def actively_playing(player):
    return player.field_maybe_none("chain") is not None


def moderation_img_distance(player, drawing, pattern):
    if player.generation == 1:
        im1 = load_img_filename(get_pattern_image(player, pattern))
    else:
        im1 = load_img_b64(get_pattern_image(player, pattern))
    im2 = load_img_b64(drawing)
    # skimage.io.imsave("/tmp/tmpimg/im1.png", im1, plugin="pil")
    # skimage.io.imsave("/tmp/tmpimg/im2.png", im2, plugin="pil")

    val = calc_hu_i3(calc_hu_moments(im1), calc_hu_moments(im2))
    del im1
    del im2
    return val


# PAGES
class Introduction(Page):
    form_model = "group"
    form_fields = ["playing"]

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and actively_playing(player)

    @staticmethod
    def error_message(player, value):
        if player.generation == 1:
            return
        elif (
            player.session.config["continue_session"]
            and player.generation == player.session.vars["old_generation"] + 1
        ):
            return
        else:
            # check if the drawings from the previous player in the chain are ready to show
            prev_player = get_my_partner(player)
            prev_player_rounds = prev_player.in_rounds(
                C.NUM_STIM + 1, C.NUM_STIM * C.NUM_REPETITIONS
            )
            if not all([p.field_maybe_none("drawing") for p in prev_player_rounds]):
                return f"Player {prev_player.id_in_subsession} hasn't finished yet."

    @staticmethod
    def vars_for_template(player):
        return {
            "instructions_hidden": ".show",
        }


class Decorate(Page):
    form_model = "player"
    form_fields = ["pattern", "drawing", "linecount"]

    @staticmethod
    def is_displayed(player):
        return actively_playing(player)

    @staticmethod
    def error_message(player, values):
        if "drawing" in values:
            del values["drawing"]
        m = dict()
        if "pattern" not in values:
            m["pattern"] = "Please select a pattern and draw it below"
        if "linecount" not in values or not values["linecount"] == 6:
            m["linecount"] = "Please draw 6 lines"
        return m

    # error_messages = {'linecount': "Please draw 6 lines",
    #                   'pattern': "Please select a pattern and draw it below",
    #                   'drawing': '???'}

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

                if "pattern" not in data:
                    print(f"ERROR: pattern not found {data}")
                    return

                error = moderation_img_distance(
                    player, data["drawing"], int(data["pattern"])
                )

                new_drawing = Drawing.create(
                    player=player,
                    attempt=get_latest_drawing(player, Drawing)[0] + 1,
                    similarity=error,
                    pattern=int(data["pattern"]),
                    drawing=data["drawing"],
                )  # save drawing in question

                if error > C.ERROR_THRESHOLD:
                    new_drawing.status = "wait"
                    moderation_submit(
                        player,
                        new_drawing,
                        get_pattern_image(player, int(data["pattern"])),
                        C,
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
                            "event": "init_con1",
                            "drawing": latest_drawing.drawing,
                            "pattern": latest_drawing.pattern,
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
                        message = {"event": "init_con1"}
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
                        return print(f"live_method ping UNKNOWN STATUS {default}")

        print(f"live_method ERROR: no event case matching: {data}")
        return

    @staticmethod
    def vars_for_template(player):
        # assign a rock-surface to draw on
        if not player.field_maybe_none("surface"):
            used_surfaces = [p.surface for p in player.in_previous_rounds()]
            available_surfaces = [
                s
                for s in range(1, len(C.SURFACE_OPTIONS) + 1)
                if s not in used_surfaces
            ]
            player.surface = choice(available_surfaces)

        # pull up the previous drawings
        history = [p.drawing for p in player.in_previous_rounds()]
        if len(history) >= C.NUM_STIM:
            history = history[C.NUM_STIM :]

        patternlist = pattern_choices(player)
        shuffle(patternlist)
        return {
            "instructions_hidden": "",
            "history": [
                {
                    "round": i + 1,
                    "value": v,
                    "image": v,
                    "usedsurface": get_surface_image(player, i),
                }
                for i, v in enumerate(history)
            ],
            "patterns": [
                {"value": v, "image": get_pattern_image(player, v)} for v in patternlist
            ],
            "surface": C.SURFACE_OPTIONS[player.surface - 1],
        }

    @staticmethod
    def before_next_page(player, timeout_happened):
        # print(f"before_next_page {player}")
        player.drawing = Drawing.filter(player=player)[-1].drawing


class Summary(Page):
    @staticmethod
    def is_displayed(player):
        return actively_playing(player) and player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player):
        # pull up all the previous drawings, but reorder them to match patterns
        history = player.in_all_rounds()
        hist1 = history[: C.NUM_ROUNDS // 2]
        pattern_order = [p.pattern for p in hist1]
        pattern_order_key = {x: i for i, x in enumerate(pattern_order)}
        hist2 = history[C.NUM_ROUNDS // 2 :]
        hist2.sort(key=lambda x: pattern_order_key[x.pattern])

        drawing1 = [(p.round_number - 1, p.drawing) for p in hist1]
        drawing2 = [(p.round_number - 1, p.drawing) for p in hist2]

        # history = list(enumerate([d for d in [p.field_maybe_none('drawing') for p in player.in_all_rounds()] if d]))

        return {
            "history": [
                {
                    "image1": v1,
                    "usedsurface1": get_surface_image_direct(player, i1),
                    "round1": i1 + 1,
                    "image2": v2,
                    "usedsurface2": get_surface_image_direct(player, i2),
                    "round2": i2 + 1,
                }
                for (i1, v1), (i2, v2) in zip(drawing1, drawing2)
            ],
            # for (i1,v1), (i2, v2) in zip(history[:C.NUM_ROUNDS//2], history[C.NUM_ROUNDS//2:])],
        }

    @staticmethod
    def before_next_page(player, timeout_happened):
        # save a csv of images for next session
        subchain_order = {
            calc_subchain(p, C): p.drawing for p in player.in_rounds(5, 8)
        }

        player.session.vars["new_drawings_db"].loc[player.id_in_group] = pd.Series(
            {
                "session": player.session.code,
                "prev_session": player.session.config["continue_session"],
                "chain": player.chain,
                "generation": player.generation,
                "drawing1": subchain_order[1],
                "drawing2": subchain_order[2],
                "drawing3": subchain_order[3],
                "drawing4": subchain_order[4],
            }
        )

        player.session.vars["new_drawings_db"].to_csv(
            C.DRAWINGS_DB_LOCATION.format(session=player.session.code), index=False
        )


def vars_for_admin_report(subsession):
    custom_export_save(subsession)
    return {}


# subsession.session.vars['drawings_db'] = pd.DataFrame(
#          columns = ["session", "chain", "generation", "drawing1", "drawing2", "drawing3", "drawing4"],
#          index = range(1, num_players+1))


page_sequence = [Introduction, Decorate, Summary]
