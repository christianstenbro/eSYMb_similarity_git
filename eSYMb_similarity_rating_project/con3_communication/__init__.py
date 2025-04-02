import sys

sys.path.insert(
    0, sys.path[0] + "/con1_aestetics"
)  # ugly hack to import the shared stuff
from con1_aesthetics.esymblib import *  # type: ignore [import]

from otree.api import models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer, Page, WaitPage  # type: ignore [import]
from otree.export import sanitize_for_csv
from random import shuffle, choice
import itertools
from json import dumps as json_dumps, loads as json_loads
import csv

"""
questions:
- what happens if a sender decides to ignore the pattern and try to draw the concept? is the transmission chain ruined?
- what happens if a sender picks a different pattern the second time s/he is communicating a concept?
"""


class C(BaseConstants):
    NAME_IN_URL = "study3"
    RECEIVER_ROLE = "RECEIVER"
    SENDER_ROLE = "SENDER"
    NUM_STIM = 4
    NUM_REPETITIONS = 2
    NUM_TRANSMISSIONS_PER_CHAIN = 9  # session.config['transmissions']
    PLAYERS_PER_GROUP = None  # NUM_TRANSMISSIONS_PER_CHAIN + 1
    # TOTAL_PARTICIPANTS = PLAYERS_PER_GROUP
    ROUNDS = NUM_STIM * NUM_REPETITIONS
    NUM_GROUPS_PER_SESSION = 2
    NUM_ROUNDS = (
        NUM_STIM * NUM_REPETITIONS * NUM_GROUPS_PER_SESSION * 9
    )  # NUM_TRANSMISSIONS_PER_CHAIN
    INSTRUCTIONS_TEMPLATE_SENDER = "con3_communication/InstructionsSend.html"
    INSTRUCTIONS_TEMPLATE_RECEIVER = "con3_communication/InstructionsReceive.html"
    PATTERN_SEED = [
        "/static/esymb_transmission/seeds/seed_1.png",
        "/static/esymb_transmission/seeds/seed_2.png",
        "/static/esymb_transmission/seeds/seed_3.png",
        "/static/esymb_transmission/seeds/seed_4.png",
    ]
    CONCEPT_OPTIONS = [
        f"/static/esymb_transmission/objects_communication/{obj}.png"
        for obj in ["Cloud", "Eye", "Fire", "Fish"]
    ]
    SURFACE_OPTIONS = [
        f"/static/esymb_transmission/objects_decoration/Object trace {i}.png"
        for i in range(1, 8 + 1)
    ]
    IMG_DIM = 155
    IMG_DIM_SMALL = 100
    GRID_DIM = 312
    # The icon to show correct or wrong answers
    CORRECT_ICON = '<img src="/static/esymb_transmission/icons/check-circle-fill.svg" class="green">'
    WRONG_ICON = (
        '<img src="/static/esymb_transmission/icons/x-circle-fill.svg" class="red">'
    )
    ERROR_THRESHOLD = 35


class Subsession(BaseSubsession):
    pass


def creating_session(subsession):
    num_players = (subsession.session.config["transmissions"] + 1) * 2
    if not "order3" in subsession.session.vars:
        # num_players = (18 // C.PLAYERS_PER_GROUP) * C.PLAYERS_PER_GROUP
        chainsize = subsession.session.config["transmissions"] + 1
        blocksize = 3
        subsession.session.vars["order3"] = list(range(1, num_players + 1))
        subsession.session.vars["order3"] = shuffled_blocks(
            subsession.session.vars["order3"], blocksize * 2
        )

        # subsession.session.vars['order3'] = subsession.session.vars['order3'][0:3] + subsession.session.vars['order3'][6:9] + subsession.session.vars['order3'][3:6] + subsession.session.vars['order3'][9:12]
        subsession.session.vars["order3"] = (
            subsession.session.vars["order3"][0:blocksize]
            + subsession.session.vars["order3"][blocksize * 2 : blocksize * 3]
            + subsession.session.vars["order3"][blocksize * 4 : blocksize * 5]
            + subsession.session.vars["order3"][blocksize * 6 : blocksize * 6 + 1]
            + subsession.session.vars["order3"][blocksize : blocksize * 2]
            + subsession.session.vars["order3"][blocksize * 3 : blocksize * 4]
            + subsession.session.vars["order3"][blocksize * 5 : blocksize * 6]
            + subsession.session.vars["order3"][blocksize * 6 + 1 : blocksize * 6 + 2]
        )

        # subsession.session.vars['order3'][blocksize  :blocksize*2] + subsession.session.vars['order3'][chainsize+blocksize  :chainsize+blocksize*2] +\
        # subsession.session.vars['order3'][blocksize*2:blocksize*3] + subsession.session.vars['order3'][chainsize+blocksize*2:chainsize+blocksize*3] +\
        # subsession.session.vars['order3'][blocksize*3:chainsize  ] + subsession.session.vars['order3'][chainsize+blocksize*3:chainsize*2          ]

        assert len(subsession.session.vars["order3"]) == 2 * chainsize

        # shuffle(subsession.session.vars['order3'])
        for i, p in enumerate(subsession.session.vars["order3"]):
            player = get_player_by_subsession_id(subsession, p)
            player.chain = (i // (1 + subsession.session.config["transmissions"])) + 1
            player.generation = (
                i % (1 + subsession.session.config["transmissions"])
            ) + 1

            # save it for other apps
            player.participant.vars["con3_generation"] = player.generation
    else:
        # fetch generation and chain from round 1
        for player in subsession.get_players():
            player.generation = player.in_round(1).generation
            player.chain = player.in_round(1).chain
    # The first set of participants do round 1-8. The next (overlapping) do 9-16 etc.
    # The active participants in a given round is in the first group, the inactives (waiting for their turn) in the 2nd

    pair = (subsession.round_number - 1) // (C.NUM_STIM * C.NUM_REPETITIONS) + 1
    if subsession.round_number > (
        C.ROUNDS * subsession.session.config["transmissions"]
    ):
        """
        skip one to avoid g1p9 playing with g2p1
        12 23 34 45 56 67 78 89 () 1011 1112 ...
        """
        pair += 1

    active = [pair + 1, pair]
    active = [subsession.session.vars["order3"][i - 1] for i in active]
    inactive = [i for i in range(1, num_players + 1) if i not in active]
    subsession.set_group_matrix([active, inactive])


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    drawing = models.LongStringField()
    pattern = models.IntegerField(widget=widgets.RadioSelect)
    concept = models.IntegerField()
    guess = models.IntegerField(
        choices=list(range(1, len(C.CONCEPT_OPTIONS) + 1)), widget=widgets.RadioSelect
    )
    # correct = models.BooleanField()
    chain = models.IntegerField()  # chain 1 or 2
    generation = models.IntegerField()  # generation 1-9
    linecount = models.IntegerField()
    surface = models.IntegerField()


class Drawing(ExtraModel):
    player = models.Link(Player)
    attempt = models.IntegerField()
    pattern = models.IntegerField()
    drawing = models.LongStringField()
    similarity = models.FloatField()
    status = models.StringField()


def custom_export_save(subsession):
    rows = custom_export_iter()
    str_rows = ([sanitize_for_csv(ele) for ele in row] for row in rows)
    with open(
        f"/opt/otree/data/esymbtransmission_export_con3_{subsession.session.code}.csv",
        "w",
    ) as f:
        writer = csv.writer(f)
        writer.writerows(str_rows)
    print("Wrote con3 export data to disk")


def custom_export_iter():
    session = DBSession()
    yield [
        "session",
        "participant_sender",
        "participant_receiver",
        "time_started_utc",
        "chain",
        "subchain",
        "generation",
        "round",
        "pattern",
        "surface",
        "concept",
        "guess",
        "correct",
        "attempt",
        "status",
        "drawing",
    ]
    print("Exporting con3 data")
    for drawing in session.query(Drawing).outerjoin(Player):
        p = drawing.player
        try:
            if p.role == C.RECEIVER_ROLE:
                continue
            if not actively_playing(p):
                continue

            participant = p.participant
            next_participant = get_player_by_chain_generation(
                p, p.chain, p.generation + 1
            )
            round_n = ((p.round_number - 1) % (C.NUM_STIM * C.NUM_REPETITIONS)) + 1
            correct = p.concept == next_participant.guess

            yield [
                p.session.code,
                participant.code,
                next_participant.participant.code,
                participant.time_started_utc,
                p.chain,
                calc_subchain(p, C),
                p.generation,
                round_n,
                p.pattern,
                p.surface,
                p.concept,
                next_participant.guess,
                correct,
                drawing.attempt,
                drawing.status,
                drawing.drawing,
            ]
        except Exception as e:
            print(e)


# FUNCTIONS


def get_my_partner(player: Player) -> Player:
    if player.role == C.SENDER_ROLE:
        # get the receiver
        return get_player_by_chain_generation(
            player, player.chain, player.generation + 1
        )
    else:
        # get the sender
        return get_player_by_chain_generation(
            player, player.chain, player.generation - 1
        )


def get_pattern_image(player, pattern):
    if player.generation == 1:
        return C.PATTERN_SEED[pattern - 1]
    else:
        # end_of_previous_round = ((player.round_number-1) // (C.NUM_STIM * C.NUM_REPETITIONS)) * (player.session.config['transmissions']+1)*2 # 0, 8, 16 etc
        end_of_previous_round = (player.generation - 1) * 8
        return get_prev_gen_drawing(get_previous_partner(player), pattern)


#        return get_previous_partner(player).in_round(end_of_previous_round - C.NUM_STIM + pattern).drawing


def get_prev_gen_drawing(player, pattern):
    possibilities = range(C.NUM_STIM, player.round_number, C.ROUNDS)
    for r in possibilities:
        p = player.in_round(r + pattern)
        if actively_playing(p) and p.role == C.SENDER_ROLE:
            return p.drawing
    raise KeyError(
        f"Previous drawing not found for player {player.id_in_subsession}, pattern {pattern}"
    )


def pattern_choices(player):
    return gen_pattern_choices(player, C)


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


def feedback_table(
    player: Player, skip_current_rounds=1, prev_guesses=None, prev_truth=None
):
    if not (prev_guesses and prev_truth):
        start_of_round = find_start_of_play(player)
        # start_of_round = 1 + (sender.round_number-1) // (C.NUM_STIM * C.NUM_REPETITIONS) * (player.session.config['transmissions']+1)*2 # 0, 8, 16 etc

    if not prev_guesses:
        receiver = player.group.get_player_by_role(C.RECEIVER_ROLE)
        prev_guesses = [
            p.field_maybe_none("guess")
            for p in receiver.in_rounds(
                start_of_round, receiver.round_number - skip_current_rounds
            )
        ]
        prev_guesses = remove_none(prev_guesses)

    if not prev_truth:
        sender = player.group.get_player_by_role(C.SENDER_ROLE)
        prev_truth = [
            p.field_maybe_none("concept")
            for p in sender.in_rounds(
                start_of_round, sender.round_number - skip_current_rounds
            )
        ]
        prev_truth = remove_none(prev_truth)

    prev_correct = [
        guess == correct for guess, correct in zip(prev_guesses, prev_truth)
    ]
    return prev_correct


def feedback_table_summary(player: Player, prev_truth=None, prev_guesses=None):
    return feedback_table(
        player, skip_current_rounds=0, prev_truth=prev_truth, prev_guesses=prev_guesses
    )


def actively_playing(player: Player):
    return player.group.id_in_subsession == 1


def get_concept_img(which):
    return C.CONCEPT_OPTIONS[which - 1]


def find_start_of_play(player):
    # example: we're in round 13, 5 rounds in, and the start of play was at 9.
    #      13                  - 5                    + 1 = 9
    return player.round_number - player_round(player, C) + 1


# def first_active_round(player):
#     # TODO
#     if player.role == C.SENDER_ROLE:
#         return 1 + (player.chain-1) * player.generation * C.NUM_STIM * C.NUM_REPETITIONS
#     else:
#         return 1 + (player.chain-1) * (player.generation-1) * C.NUM_STIM * C.NUM_REPETITIONS

# PAGES


class WaitStart(WaitPage):
    template_name = "con3_communication/WaitStart.html"

    @staticmethod
    def is_displayed(player: Player):
        return actively_playing(player) and player_round(player, C) == 1


class Introduction(Page):
    def is_displayed(player):
        return actively_playing(player) and player_round(player, C) == 1

    @staticmethod
    def vars_for_template(player):
        return {
            "instructions_hidden": ".show",
            "round": player_round(player, C),
            "correct_icon": C.CORRECT_ICON,
        }

    @staticmethod
    def js_vars(player):
        return dict(showmodal=player_round(player, C) == 1, timeout=4000)


class Send(Page):
    form_model = "player"
    form_fields = ["pattern", "drawing", "linecount"]

    @staticmethod
    def is_displayed(player):
        return actively_playing(player) and player.role == C.SENDER_ROLE

    @staticmethod
    def vars_for_template(player):
        start_of_round = find_start_of_play(player)
        if not player.field_maybe_none("surface"):
            used_surfaces = [
                p.surface
                for p in player.in_rounds(start_of_round, player.round_number - 1)
            ]
            available_surfaces = [
                s
                for s in range(1, len(C.SURFACE_OPTIONS) + 1)
                if s not in used_surfaces
            ]
            player.surface = choice(available_surfaces)

        used_concepts = [
            p.concept for p in player.in_rounds(start_of_round, player.round_number - 1)
        ]
        if len(used_concepts) >= C.NUM_STIM:
            used_concepts = used_concepts[C.NUM_STIM :]
        available_concepts = [
            s for s in range(1, len(C.CONCEPT_OPTIONS) + 1) if s not in used_concepts
        ]
        # available_concepts = [s for s in C.CONCEPT_OPTIONS if s not in used_concepts]
        if not player.field_maybe_none("concept"):
            player.concept = choice(available_concepts)

        conceptlist = list(range(1, len(C.CONCEPT_OPTIONS) + 1))
        shuffle(conceptlist)

        patternlist = pattern_choices(player)
        shuffle(patternlist)

        # print(start_of_round, player.round_number-1)
        prev_concepts = [
            p.concept for p in player.in_rounds(start_of_round, player.round_number - 1)
        ]
        prev_drawings = [
            p.drawing for p in player.in_rounds(start_of_round, player.round_number - 1)
        ]
        prev_correct = feedback_table(player, prev_truth=prev_concepts)
        return {
            "instructions_hidden": "",
            "round": player_round(player, C),
            "conceptlist": [
                {
                    "concept": get_concept_img(c),
                    "checked": "checked" if c == player.concept else "",
                }
                for c in conceptlist
            ],
            "patterns": [
                {"value": v, "image": get_pattern_image(player, v)} for v in patternlist
            ],
            "feedback_table": [
                {
                    "drawing": x,
                    "concept": get_concept_img(y),
                    "correct": correct_icon(z),
                    "round": i + 1,
                }
                for i, (x, y, z) in enumerate(
                    zip(prev_drawings, prev_concepts, prev_correct)
                )
            ],
            "surface": C.SURFACE_OPTIONS[player.surface - 1],
            "correct_icon": modal_correct(prev_correct),
            "correct_status": prev_correct[-1] if prev_correct else None,
        }

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
                            "event": "init_con3",
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
                        message = {"event": "init_con3"}
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
    def before_next_page(player, timeout_happened):
        # print(f"before_next_page {player}")
        player.drawing = Drawing.filter(player=player)[-1].drawing

    @staticmethod
    def js_vars(player):
        return dict(showmodal=player_round(player, C) != 1)


class Receive(Page):
    form_model = "player"
    form_fields = ["guess"]

    @staticmethod
    def is_displayed(player):
        return actively_playing(player) and player.role == C.RECEIVER_ROLE

    @staticmethod
    def vars_for_template(player):
        partner = get_my_partner(
            player
        )  # player.group.get_player_by_role(C.SENDER_ROLE)
        guesslist = list(range(1, len(C.CONCEPT_OPTIONS) + 1))
        shuffle(guesslist)

        # drawing = partner.drawing
        start_of_round = find_start_of_play(player)
        # start_of_round = 1 + (player.round_number-1) // (C.NUM_STIM * C.NUM_REPETITIONS) * (player.session.config['transmissions']+1)*2
        prev_guesses = [
            p.guess for p in player.in_rounds(start_of_round, player.round_number - 1)
        ]
        prev_drawings = [
            p.drawing
            for p in partner.in_rounds(start_of_round, player.round_number - 1)
        ]
        prev_correct = feedback_table(player, prev_guesses=prev_guesses)
        return {
            "instructions_hidden": "",
            "guesslist": [{"value": g, "img": get_concept_img(g)} for g in guesslist],
            "round": player_round(player, C),
            "drawing": partner.drawing,
            "feedback_table": [
                {
                    "guess": get_concept_img(g),
                    "drawing": d,
                    "correct": correct_icon(c),
                    "round": i + 1,
                }
                for i, (g, d, c) in enumerate(
                    zip(prev_guesses, prev_drawings, prev_correct)
                )
            ],
        }


class WaitSend(WaitPage):
    template_name = "con3_communication/WaitSend.html"

    @staticmethod
    def is_displayed(player: Player):
        return actively_playing(player)

    @staticmethod
    def vars_for_template(player):
        if player.role == C.SENDER_ROLE:
            return
        partner = get_my_partner(player)
        start_of_round = find_start_of_play(player)
        prev_guesses = [
            p.field_maybe_none("guess")
            for p in player.in_rounds(start_of_round, player.round_number - 1)
        ]
        prev_drawings = [
            p.field_maybe_none("drawing")
            for p in partner.in_rounds(start_of_round, player.round_number - 1)
        ]
        prev_guesses = remove_none(prev_guesses)
        prev_drawings = remove_none(prev_drawings)
        prev_correct = feedback_table(player, prev_guesses=prev_guesses)
        return {
            "feedback_table": [
                {
                    "guess": get_concept_img(g),
                    "drawing": d,
                    "correct": correct_icon(c),
                    "round": i + 1,
                }
                for i, (g, d, c) in enumerate(
                    zip(prev_guesses, prev_drawings, prev_correct)
                )
            ],
            "correct_icon": modal_correct(prev_correct),
            "correct_status": prev_correct[-1] if prev_correct else None,
        }

    @staticmethod
    def js_vars(player):
        return dict(showmodal=player_round(player, C) != 1)


class WaitReceive(WaitPage):
    template_name = "con3_communication/WaitReceive.html"

    @staticmethod
    def is_displayed(player: Player):
        return actively_playing(player)

    @staticmethod
    def after_all_players_arrive(group):
        # todo: save 'correct' instead of calculating on the fly in feedback_table
        for p in group.get_players():
            if p.role == C.RECEIVER_ROLE:
                pass

    @staticmethod
    def vars_for_template(player):
        if player.role == C.RECEIVER_ROLE:
            return

        # partner = player.group.get_player_by_role(C.SENDER_ROLE)

        start_of_round = find_start_of_play(player)
        # start_of_round = 1 + (player.round_number-1) // (C.NUM_STIM * C.NUM_REPETITIONS) * (player.session.config['transmissions']+1)*2
        prev_concepts = [
            p.concept for p in player.in_rounds(start_of_round, player.round_number)
        ]
        prev_drawings = [
            p.drawing for p in player.in_rounds(start_of_round, player.round_number)
        ]
        prev_correct = feedback_table(player, prev_truth=prev_concepts)
        return {
            "feedback_table": [
                {
                    "drawing": x,
                    "concept": get_concept_img(y),
                    "correct": correct_icon(z),
                    "round": i + 1,
                }
                for i, (x, y, z) in enumerate(
                    zip(
                        prev_drawings,
                        prev_concepts,
                        itertools.chain(prev_correct, [""]),
                    )
                )
            ],
        }


def vars_for_admin_report(subsession):
    custom_export_save(subsession)
    active_players = [s.get_group_matrix()[0] for s in subsession.in_all_rounds()]
    active_players = [
        active_players[i]
        for i in range(0, len(active_players), C.NUM_STIM * C.NUM_REPETITIONS)
    ]
    active_players_1 = active_players[: len(active_players) // 2]
    active_players_2 = active_players[len(active_players) // 2 :]
    return {
        "order1": [
            {"all": x, "new": x[0], "old": active_players_1[i - 1][1] if i > 0 else ""}
            for i, x in enumerate(active_players_1)
        ],
        "order2": [
            {"all": x, "new": x[0], "old": active_players_2[i - 1][1] if i > 0 else ""}
            for i, x in enumerate(active_players_2)
        ],
        "lastround": subsession.round_number == C.NUM_ROUNDS,
    }


class SummarySend(Page):
    @staticmethod
    def is_displayed(player):
        return (
            actively_playing(player)
            and player.role == C.SENDER_ROLE
            and player_round(player, C) == C.ROUNDS
        )

    @staticmethod
    def vars_for_template(player):
        start_of_round = find_start_of_play(player)
        prev_concepts = [
            p.concept for p in player.in_rounds(start_of_round, player.round_number)
        ]
        prev_drawings = [
            p.drawing for p in player.in_rounds(start_of_round, player.round_number)
        ]

        prev_correct = feedback_table_summary(player, prev_truth=prev_concepts)

        return {
            "round": player_round(player, C),
            "feedback_table": [
                {
                    "drawing": x,
                    "concept": get_concept_img(y),
                    "correct": correct_icon(z),
                    "round": i + 1,
                }
                for i, (x, y, z) in enumerate(
                    zip(prev_drawings, prev_concepts, prev_correct)
                )
            ],
            "correct_icon": modal_correct(prev_correct),
            "correct_status": prev_correct[-1] if prev_correct else None,
        }

    @staticmethod
    def js_vars(player):
        return dict(showmodal=player_round(player, C) != 1)


class SummaryReceive(Page):
    @staticmethod
    def is_displayed(player):
        return (
            actively_playing(player)
            and player.role == C.RECEIVER_ROLE
            and player_round(player, C) == 8
        )

    @staticmethod
    def vars_for_template(player):
        start_of_round = find_start_of_play(player)
        partner = get_my_partner(player)
        prev_guesses = [
            p.guess for p in player.in_rounds(start_of_round, player.round_number)
        ]
        prev_drawings = [
            p.drawing for p in partner.in_rounds(start_of_round, player.round_number)
        ]
        prev_correct = feedback_table_summary(player, prev_guesses=prev_guesses)
        return {
            "feedback_table": [
                {
                    "guess": get_concept_img(g),
                    "drawing": d,
                    "correct": correct_icon(c),
                    "round": i + 1,
                }
                for i, (g, d, c) in enumerate(
                    zip(prev_guesses, prev_drawings, prev_correct)
                )
            ],
            "correct_icon": modal_correct(prev_correct),
            "correct_status": prev_correct[-1] if prev_correct else None,
        }

    @staticmethod
    def js_vars(player):
        return dict(showmodal=player_round(player, C) != 1)


page_sequence = [
    WaitStart,
    Introduction,
    Send,
    WaitSend,
    Receive,
    WaitReceive,
    SummarySend,
    SummaryReceive,
]
