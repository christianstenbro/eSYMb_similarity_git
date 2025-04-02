from otree.api import models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer, Page, WaitPage  # type: ignore [import]
from otree.export import sanitize_for_csv
from random import shuffle, choice
import itertools
from json import dumps as json_dumps, loads as json_loads
from con1_aesthetics.esymblib import *  # type: ignore [import]

#
import csv


class C(BaseConstants):
    NAME_IN_URL = "study2"
    PLAYERS_PER_GROUP = None  # (session.config['transmissions']+1)*2
    JUDGE_ROLE = "GUESSER"
    JUDGE2_ROLE = "GUESSER"
    DECORATOR_ROLE = "DRAWER"
    DECORATOR2_ROLE = "DRAWER"
    NUM_STIM = 4
    NUM_REPETITIONS = 2
    # NUM_TRANSMISSIONS_PER_CHAIN = session.config['transmissions']
    ROUNDS = (
        NUM_STIM * NUM_REPETITIONS
    )  # how many rounds of drawing will each participant do
    NUM_ROUNDS = (
        NUM_STIM * NUM_REPETITIONS * 9
    )  # NUM_TRANSMISSIONS_PER_CHAIN # how many transmissions in total
    INSTRUCTIONS_TEMPLATE_DECORATOR = "con2_style/InstructionsDecorate.html"
    INSTRUCTIONS_TEMPLATE_JUDGE = "con2_style/InstructionsJudge.html"
    PATTERN_SEED = [
        "/static/esymb_transmission/seeds/seed_1.png",
        "/static/esymb_transmission/seeds/seed_2.png",
        "/static/esymb_transmission/seeds/seed_3.png",
        "/static/esymb_transmission/seeds/seed_4.png",
    ]
    SURFACE_OPTIONS = [
        f"/static/esymb_transmission/objects_decoration/Object trace {i}.png"
        for i in range(1, 8 + 1)
    ]
    IMG_DIM = 155
    IMG_DIM_SMALL = 100
    GRID_DIM = 282
    # The icon to show correct or wrong answers
    CORRECT_ICON = '<img src="/static/esymb_transmission/icons/check-circle-fill.svg" class="green">'
    WRONG_ICON = (
        '<img src="/static/esymb_transmission/icons/x-circle-fill.svg" class="red">'
    )
    ERROR_THRESHOLD = 35


class Subsession(BaseSubsession):
    pass


def creating_session(subsession):
    if not "order2" in subsession.session.vars:
        chainsize = subsession.session.config["transmissions"] + 1
        blocksize = 3
        subsession.session.vars["order2"] = list(range(1, chainsize * 2 + 1))
        subsession.session.vars["order2"] = shuffled_blocks(
            subsession.session.vars["order2"], blocksize * 2
        )
        # shuffle(subsession.session.vars['order2'])

        subsession.session.vars["order2"] = (
            subsession.session.vars["order2"][0:blocksize]
            + subsession.session.vars["order2"][blocksize * 2 : blocksize * 3]
            + subsession.session.vars["order2"][blocksize * 4 : blocksize * 5]
            + subsession.session.vars["order2"][blocksize * 6 : blocksize * 6 + 1]
            + subsession.session.vars["order2"][blocksize : blocksize * 2]
            + subsession.session.vars["order2"][blocksize * 3 : blocksize * 4]
            + subsession.session.vars["order2"][blocksize * 5 : blocksize * 6]
            + subsession.session.vars["order2"][blocksize * 6 + 1 : blocksize * 6 + 2]
        )

        # subsession.session.vars['order2'] = \
        #     subsession.session.vars['order2'][0          :blocksize  ] + subsession.session.vars['order2'][chainsize            :chainsize+blocksize  ] +\
        #     subsession.session.vars['order2'][blocksize  :blocksize*2] + subsession.session.vars['order2'][chainsize+blocksize  :chainsize+blocksize*2] +\
        #     subsession.session.vars['order2'][blocksize*2:blocksize*3] + subsession.session.vars['order2'][chainsize+blocksize*2:chainsize+blocksize*3] +\
        #     subsession.session.vars['order2'][blocksize*3:chainsize  ] + subsession.session.vars['order2'][chainsize+blocksize*3:chainsize*2          ]

        assert len(subsession.session.vars["order2"]) == 2 * chainsize

        for i, p in enumerate(subsession.session.vars["order2"]):
            player = get_player_by_subsession_id(subsession, p)
            ### straightforward way
            player.chain = (i // (1 + subsession.session.config["transmissions"])) + 1
            player.generation = (
                i % (1 + subsession.session.config["transmissions"])
            ) + 1
            ### blocked way
            # whichblock = i // blocksize
            # halfblock = blocksize // 2

            # player.chain      = 1 + (i // halfblock) - (whichblock * 2)
            # player.generation = 1 + (i %  halfblock) + (whichblock * halfblock)

            # save it for other apps
            player.participant.vars["con2_generation"] = player.generation

    else:
        # fetch generation and chain from round 1
        for player in subsession.get_players():
            player.generation = player.in_round(1).generation
            player.chain = player.in_round(1).chain

    # if subsession.round_number == 1:
    #     print(f"Con2 order: {subsession.session.vars['order2']}")
    # The first set of participants do round 1-8. The next (overlapping) do 9-16 etc.
    # The active participants in a given round is in the first group, the inactives (waiting for their turn) in the 2nd
    pair = ((subsession.round_number - 1) // (C.NUM_STIM * C.NUM_REPETITIONS)) + 1
    # print("pair", pair)
    # 1,2,10,11 or rather 2, 10, 1, 11 for role assignment purposes
    offset = subsession.session.config["transmissions"] + 1  # 9
    active = [
        pair + 1,
        pair + offset + 1,
        pair,
        pair + offset,
    ]
    # print("active", active)
    active = [subsession.session.vars["order2"][i - 1] for i in active]
    inactive = [
        i
        for i in range(1, (subsession.session.config["transmissions"] + 1) * 2 + 1)
        if i not in active
    ]
    subsession.set_group_matrix([active, inactive])


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    drawing = models.LongStringField()
    pattern = models.IntegerField(widget=widgets.RadioSelect)
    judge = models.IntegerField(widget=widgets.RadioSelect, choices=[1, 2])
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


# def custom_export(players):
#     custom_export_save()


def custom_export_save(subsession):
    rows = custom_export_iter()
    str_rows = ([sanitize_for_csv(ele) for ele in row] for row in rows)
    with open(
        f"/opt/otree/data/esymbtransmission_export_con2_{subsession.session.code}.csv",
        "w",
    ) as f:
        writer = csv.writer(f)
        writer.writerows(str_rows)
    print("Wrote con2 export data to disk")


def custom_export_iter():
    ## define my own custom export function which doesn't consume players to avoid oom-crashing
    session = DBSession()
    yield [
        "session",
        "participant_sender",
        "participant_receiver_a",
        "participant_receiver_b",
        "time_started_utc",
        "chain",
        "subchain",
        "generation",
        "round",
        "pattern",
        "surface",
        "guess_a",
        "guess_b",
        "correct_a",
        "correct_b",
        "attempt",
        "status",
        "drawing",
    ]
    print("Exporting con2 data")

    for drawing in session.query(Drawing).outerjoin(Player):
        try:
            if drawing.player.role == C.JUDGE_ROLE:
                continue
            if not actively_playing(drawing.player):
                continue

            participant_a = get_player_by_chain_generation(
                drawing.player, drawing.player.chain, drawing.player.generation + 1
            )
            participant_b = get_player_by_chain_generation(
                drawing.player, 3 - drawing.player.chain, drawing.player.generation + 1
            )
            round_n = (
                (drawing.player.round_number - 1) % (C.NUM_STIM * C.NUM_REPETITIONS)
            ) + 1
            correct_a = drawing.player.chain == participant_a.judge
            correct_b = drawing.player.chain != participant_b.judge

            yield [
                drawing.player.session.code,
                drawing.player.participant.code,
                participant_a.participant.code,
                participant_b.participant.code,
                drawing.player.participant.time_started_utc,
                drawing.player.chain,
                calc_subchain(drawing.player, C),
                drawing.player.generation,
                round_n,
                drawing.player.pattern,
                drawing.player.surface,
                participant_a.judge,
                participant_b.judge,
                correct_a,
                correct_b,
                drawing.attempt,
                drawing.status,
                drawing.drawing,
            ]
            print(drawing.player.id_in_subsession, end=",")
            # del participant_a, participant_b, round_b, correct_a, correct_b
        except Exception as e:
            print(e)
    print()


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


# FUNCTIONS

# def get_my_partner(player: Player) -> Player:
#     if player.role == C.DECORATOR_ROLE:
#         # get the judge
#         return get_player_by_chain_generation(player, player.chain, player.generation + 1)
#     else:
#         # get the decorator
#         return get_player_by_chain_generation(player, player.chain, player.generation - 1)


def pattern_choices(player):
    return gen_pattern_choices(player, C)


def get_my_decorator(player: Player) -> Player:
    assert player.generation > 1
    return get_player_by_chain_generation(player, player.chain, player.generation - 1)


# def get_my_guesser(player: Player) -> Player:
#     # assert player.generation
#     return get_player_by_chain_generation(player, player.chain, player.generation + 1)


def get_other_decorator(player: Player) -> Player:
    assert player.generation > 1
    return get_player_by_chain_generation(
        player, 3 - player.chain, player.generation - 1
    )


def get_pattern_image(player, pattern):
    if player.generation == 1:
        return C.PATTERN_SEED[pattern - 1]
    else:
        return get_prev_gen_drawing(get_my_decorator(player), pattern)
        # return get_my_decorator(player).in_round(C.NUM_STIM + pattern).drawing


def get_prev_gen_drawing(player, pattern):
    possibilities = range(C.NUM_STIM, player.round_number, C.ROUNDS)
    for r in possibilities:
        p = player.in_round(r + pattern)
        if actively_playing(p) and p.role == C.DECORATOR_ROLE:
            return p.drawing
    raise KeyError(
        f"Previous drawing not found for player {player.id_in_subsession}, pattern {pattern}"
    )


def get_judge_image_history(player: Player, guess, round_n: int = 0) -> str:
    end_of_previous_round = (
        (player.round_number - 1)
        // (C.NUM_STIM * C.NUM_REPETITIONS)
        * player.session.config["transmissions"]
    )  # 0, 8, 16 etc
    if player.role == C.JUDGE_ROLE:
        assert player.generation > 1
        return (
            get_player_by_chain_generation(player, guess, player.generation - 1)
            .in_round(end_of_previous_round + round_n)
            .drawing
        )
    else:
        return (
            get_player_by_chain_generation(player, guess, player.generation)
            .in_round(end_of_previous_round + round_n)
            .drawing
        )


def get_judge_image(player: Player, chain: int):
    return get_player_by_chain_generation(player, chain, player.generation - 1).drawing


def feedback_table(decorator: Player, judge: Player, cut_rounds=1):
    start_of_round = find_start_of_play(decorator)
    prev_guesses = [
        p.field_maybe_none("judge")
        for p in judge.in_rounds(start_of_round, decorator.round_number - cut_rounds)
    ]

    # print(prev_guesses)
    prev_correct = [g == judge.chain for g in prev_guesses]

    # decorator_truth = get_my_partner(judge)
    # prev_truth =  [p.drawing for p in decorator_truth.in_rounds(start_of_round, decorator.round_number-1)]
    # print(prev_truth)
    # prev_correct = [guess == correct for guess, correct in zip(prev_guesses, prev_truth)]
    # print(prev_correct)
    return prev_correct


def correct_icon(b: bool):
    if b == "":
        return ""
    else:
        return C.CORRECT_ICON if b else C.WRONG_ICON


def actively_playing(player: Player):
    return player.group.id_in_subsession == 1


def find_start_of_play(player):
    # example: we're in round 13, 5 rounds in, and the start of play was at 9.
    #      13                  - 5                    + 1 = 9
    return player.round_number - player_round(player, C) + 1


# PAGES
class Introduction(Page):
    def is_displayed(player):
        return actively_playing(player) and player_round(player, C) == 1

    @staticmethod
    def vars_for_template(player):
        # if player.role == C.DECORATOR_ROLE:
        #     player_round = player.round_number - (C.ROUNDS * (player.generation-1))
        # else:
        #     player_round = player.round_number - (C.ROUNDS * (player.generation-2))
        return {
            "instructions_hidden": ".show",
            "round": player_round(player, C),
            "correct_icon": C.CORRECT_ICON,
        }

    @staticmethod
    def js_vars(player):
        return dict(showmodal=player_round(player, C) == 1, timeout=4000)


class Decorate(Page):
    form_model = "player"
    form_fields = ["drawing", "linecount"]

    @staticmethod
    def is_displayed(player):
        return actively_playing(player) and player.role == C.DECORATOR_ROLE

    @staticmethod
    def error_message(player, values):
        if "drawing" in values:
            del values["drawing"]
        m = dict()
        if "linecount" not in values or not values["linecount"] == 6:
            m["linecount"] = "Please draw 6 lines"
        return m

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

        patternlist = pattern_choices(player)
        shuffle(patternlist)
        decorators = [
            p for p in player.group.get_players() if p.role == C.DECORATOR_ROLE
        ]
        if not all([p.field_maybe_none("pattern") for p in decorators]):
            pattern = choice(patternlist)
            for p in decorators:
                p.pattern = pattern

        guessers = [p for p in player.get_others_in_group() if p.role == C.JUDGE_ROLE]
        if guessers[0].chain != player.chain:
            guessers.reverse()

        correct_a, correct_b = [feedback_table(player, p) for p in guessers]

        prev_drawings = [
            p.drawing for p in player.in_rounds(start_of_round, player.round_number - 1)
        ]
        return {
            "instructions_hidden": "",
            "round": player_round(
                player, C
            ),  # player.round_number - (C.ROUNDS * (player.generation-1)),
            "patterns": [
                {
                    "value": v,
                    "image": get_pattern_image(player, v),
                    "checked": "checked" if v == player.pattern else "unchecked",
                }
                for v in patternlist
            ],
            "feedback_table": [
                {
                    "drawing": x,
                    "correct_a": correct_icon(y),
                    "correct_b": correct_icon(z),
                    "round": i + 1,
                }
                for i, (x, y, z) in enumerate(zip(prev_drawings, correct_a, correct_b))
            ],
            "surface": C.SURFACE_OPTIONS[player.surface - 1],
            "correct_icon_a": modal_correct(correct_a),
            "correct_icon_b": modal_correct(correct_b),
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
                            "event": "init_con2",
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
                        message = {"event": "init_con2"}
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


class Judge(Page):
    form_model = "player"
    form_fields = ["judge"]

    @staticmethod
    def is_displayed(player):
        return actively_playing(player) and player.role == C.JUDGE_ROLE

    @staticmethod
    def vars_for_template(player):
        partner = get_my_decorator(player)
        judgelist = [1, 2]
        shuffle(judgelist)

        start_of_round = find_start_of_play(player)
        prev_correct = feedback_table(partner, player)

        # prev_guesses = [p.judge for p in player.in_rounds(start_of_round, player.round_number-1)]
        # prev_other = [get_judge_image(p, 3 - p.judge) for p in player.in_rounds(start_of_round, player.round_number-1)]

        owngroup = [
            p.drawing
            for p in partner.in_rounds(start_of_round, player.round_number - 1)
        ]
        othergroup = [
            p.drawing
            for p in get_other_decorator(player).in_rounds(
                start_of_round, player.round_number - 1
            )
        ]
        return {
            "instructions_hidden": "",
            "round": player_round(
                player, C
            ),  # .round_number - (C.ROUNDS * (player.generation-2)),
            "judgelist": [
                {"image": get_judge_image(player, j), "value": j} for j in judgelist
            ],
            "feedback_table": [
                {
                    "owngroup": g,
                    "correct": correct_icon(c),
                    "round": i + 1,
                    "othergroup": o,
                }
                for i, (g, c, o) in enumerate(zip(owngroup, prev_correct, othergroup))
            ],
        }


class WaitDecorate(WaitPage):
    template_name = "con2_style/WaitDecorate.html"

    @staticmethod
    def is_displayed(player: Player):
        return actively_playing(player)

    @staticmethod
    def vars_for_template(player):
        if player.role == C.DECORATOR_ROLE:
            return
        partner = get_my_decorator(player)
        # partner = get_player_by_subsession_id(player.subsession, player.id_in_subsession-1)
        start_of_round = find_start_of_play(player)
        # prev_guesses = [p.field_maybe_none('judge') for p in player.in_rounds(start_of_round, player.round_number-1)]
        # prev_guesses = remove_none(prev_guesses)
        prev_correct = feedback_table(partner, player)
        # prev_other = [get_judge_image(p, 3 - p.judge) for p in player.in_rounds(start_of_round, player.round_number-1)]

        owngroup = [
            p.drawing
            for p in partner.in_rounds(start_of_round, player.round_number - 1)
        ]
        othergroup = [
            p.drawing
            for p in get_other_decorator(player).in_rounds(
                start_of_round, player.round_number - 1
            )
        ]
        # print((start_of_round, player.round_number-1))
        # print(prev_guesses)
        # print(prev_correct)
        return {
            "feedback_table": [
                {
                    "owngroup": g,
                    "correct": correct_icon(c),
                    "round": i + 1,
                    "othergroup": o,
                }
                for i, (g, c, o) in enumerate(zip(owngroup, prev_correct, othergroup))
            ],
            "correct_icon": modal_correct(prev_correct),
            "correct_status": prev_correct[-1] if prev_correct else None,
        }

    @staticmethod
    def js_vars(player):
        return dict(showmodal=player_round(player, C) != 1)


class WaitJudge(WaitPage):
    template_name = "con2_style/WaitJudge.html"

    @staticmethod
    def is_displayed(player: Player):
        return actively_playing(player)

    @staticmethod
    def vars_for_template(player):
        if player.role == C.JUDGE_ROLE:
            return

        guessers = [p for p in player.get_others_in_group() if p.role == C.JUDGE_ROLE]
        if guessers[0].chain != player.chain:
            guessers.reverse()

        correct_a, correct_b = [feedback_table(player, p) for p in guessers]

        start_of_round = find_start_of_play(player)
        prev_drawings = [
            p.drawing for p in player.in_rounds(start_of_round, player.round_number)
        ]
        return {
            "feedback_table": [
                {
                    "drawing": x,
                    "correct_a": correct_icon(y),
                    "correct_b": correct_icon(z),
                    "round": i + 1,
                }
                for i, (x, y, z) in enumerate(
                    zip(
                        prev_drawings,
                        itertools.chain(correct_a, [""]),
                        itertools.chain(correct_b, [""]),
                    )
                )
            ],
        }


class WaitStart(WaitPage):
    template_name = "con2_style/WaitStart.html"

    @staticmethod
    def is_displayed(player: Player):
        return actively_playing(player) and player_round(player, C) == 1


def vars_for_admin_report(subsession):
    custom_export_save(
        subsession
    )  # TODO careful, this doesn't really belong here but its the only place I could think of
    active_players = [s.get_group_matrix()[0] for s in subsession.in_all_rounds()]
    active_players = [
        active_players[i]
        for i in range(0, len(active_players), C.NUM_STIM * C.NUM_REPETITIONS)
    ]
    return {
        "order": [
            {"all": x, "new": x[:2], "old": active_players[i - 1][2:] if i > 0 else ""}
            for i, x in enumerate(active_players)
        ],
        "lastround": subsession.round_number == C.NUM_ROUNDS,
    }


class SummaryDecorate(Page):
    @staticmethod
    def is_displayed(player):
        return (
            actively_playing(player)
            and player.role == C.DECORATOR_ROLE
            and player_round(player, C) == C.ROUNDS
        )
        # player.round_number == (C.ROUNDS * player.generation) # last round of decorating

    @staticmethod
    def vars_for_template(player):
        guessers = [p for p in player.get_others_in_group() if p.role == C.JUDGE_ROLE]
        if guessers[0].chain != player.chain:
            guessers.reverse()

        correct_a, correct_b = [
            feedback_table(player, p, cut_rounds=0) for p in guessers
        ]

        start_of_round = find_start_of_play(player)
        prev_drawings = [
            p.drawing for p in player.in_rounds(start_of_round, player.round_number)
        ]
        return {
            "feedback_table": [
                {
                    "drawing": x,
                    "correct_a": correct_icon(y),
                    "correct_b": correct_icon(z),
                    "round": i + 1,
                }
                for i, (x, y, z) in enumerate(zip(prev_drawings, correct_a, correct_b))
            ],
            "correct_icon_a": modal_correct(correct_a),
            "correct_icon_b": modal_correct(correct_b),
        }

    @staticmethod
    def js_vars(player):
        return dict(showmodal=player_round(player, C) != 1)


class SummaryJudge(Page):
    @staticmethod
    def is_displayed(player):
        return (
            actively_playing(player)
            and player.role == C.JUDGE_ROLE
            and player_round(player, C) == C.ROUNDS
        )
        # player.round_number == (C.ROUNDS * (player.generation-1)) # last round of judging

    @staticmethod
    def vars_for_template(player):
        partner = get_my_decorator(player)

        start_of_round = find_start_of_play(player)
        # prev_guesses = [p.judge for p in player.in_rounds(start_of_round, player.round_number)]
        prev_correct = feedback_table(partner, player, cut_rounds=0)

        owngroup = [
            p.drawing for p in partner.in_rounds(start_of_round, player.round_number)
        ]
        othergroup = [
            p.drawing
            for p in get_other_decorator(player).in_rounds(
                start_of_round, player.round_number
            )
        ]
        return {
            "feedback_table": [
                {
                    "owngroup": g,
                    "correct": correct_icon(c),
                    "round": i + 1,
                    "othergroup": o,
                }
                for i, (g, c, o) in enumerate(zip(owngroup, prev_correct, othergroup))
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
    Decorate,
    WaitDecorate,
    Judge,
    WaitJudge,
    SummaryDecorate,
    SummaryJudge,
]
