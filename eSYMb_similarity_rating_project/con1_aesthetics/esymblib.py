from otree.api import models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer, Page  # type: ignore [import]
from typing import List
from random import sample
from collections.abc import Iterable
import pathlib
import io
import base64
import numpy as np
import skimage.io, skimage.transform, skimage.color

from otree.database import engine, DBSession
from typing import Optional
from sqlalchemy import select
from sqlalchemy import Column, Integer, String, Text, Float
from sqlalchemy.ext.declarative import declarative_base


from otree.api import ExtraModel

"""
Library of shared functions for running the esymb_transmission study
Malte Lau Petersen

"""


CORRECT_ICON = (
    '<img src="/static/esymb_transmission/icons/check-circle-fill.svg" class="green">'
)
WRONG_ICON = (
    '<img src="/static/esymb_transmission/icons/x-circle-fill.svg" class="red">'
)

MODERATION_JOB_QUEUE = "esymb_transmission_moderation_job"


def get_player_by_subsession_id(subsession: BaseSubsession, id: int) -> BasePlayer:
    """Why isn't this built in??"""
    for p in subsession.get_players():
        if p.id_in_subsession == id:
            return p
    raise KeyError(f"Player with subsession id {id} not found")


def get_player_by_chain_generation(
    player: BasePlayer, chain: int, generation: int
) -> BasePlayer:
    if chain is None or generation is None:
        print("DEBUG: Searching for player", chain, generation)
        return
    # print("Searching for player", chain, generation)
    for p in player.subsession.get_players():
        if p.chain == chain and p.generation == generation:
            # print("Accepting player", p.chain, p.generation)
            return p
        else:
            # print("Rejecting player", p.chain, type(p.chain), p.generation, type(p.generation))
            pass
    raise KeyError(f"Player with chain {chain}, generation {generation} not found")


def get_2ndhalf_rounds(player: BasePlayer, C: BaseConstants) -> List[BasePlayer]:
    # are we in round 1-4 or 5-8?
    starting_round = 1 + (C.NUM_STIM * ((player.round_number - 1) // C.NUM_STIM))
    return player.in_rounds(starting_round, player.round_number - 1)


def get_previous_partner(player):
    assert player.generation != 1
    return get_player_by_chain_generation(player, player.chain, player.generation - 1)


def gen_pattern_choices(player: BasePlayer, C: BaseConstants) -> List[int]:
    """Return the valid pattern options for this round"""

    pattern_options = list(range(1, C.NUM_STIM + 1))
    # which patterns did we already just use for decoration
    prev_picked = [p.pattern for p in get_2ndhalf_rounds(player, C)]
    return [x for x in pattern_options if x not in prev_picked]


def calc_subchain(player: BasePlayer, C: BaseConstants):
    # a player object in some round
    if player.field_maybe_none("pattern"):  # we picked a pattern this round
        if player.generation == 1:
            return player.pattern
        else:
            prev_sender = get_player_by_chain_generation(
                player, player.chain, player.generation - 1
            )
            end_of_previous_round = player.round_number - player_round(player, C)
            # end_of_previous_round = (player.round_number-1) // (C.NUM_STIM * C.NUM_REPETITIONS) * C.NUM_TRANSMISSIONS_PER_CHAIN # 0, 8, 16 etc
            return calc_subchain(
                prev_sender.in_round(
                    end_of_previous_round - C.NUM_STIM + player.pattern
                ),
                C,
            )
    else:
        print(f"Failed to find subchain for player {player.chain}.{player.generation}")
        return "NA"


def remove_none(thelist: list) -> list:
    return [x for x in thelist if x is not None]


def shuffled_blocks(thelist: list, blocksize: int) -> list:
    # [[j1, j2, j3], [ ... ]]
    # where each j is picked randomly within the block
    # then unnest
    if blocksize > len(thelist):
        blocksize = len(thelist)

    order = []
    for startpoint in range(0, len(thelist), blocksize):
        for j in sample(range(startpoint, startpoint + blocksize), k=blocksize):
            if j >= len(thelist):
                continue
            else:
                order.append(thelist[j])

    return order

    # return list(chain.from_iterable(
    #     [[l[j] # the jth element \
    #       for j in sample(range(i, i+blocksize), blocksize)] # sample within the block \
    #      for i in range(0, len(l), blocksize)])) # repeat to get the full list


def modal_correct(correctlist):
    if correctlist:
        return correct_icon(correctlist[-1])


def correct_icon(b: bool):
    if b == "":
        return ""
    else:
        return CORRECT_ICON if b else WRONG_ICON


def player_round(player: BasePlayer, C: BaseConstants) -> int:

    return ((player.round_number - 1) % C.ROUNDS) + 1


#####################
# moderation client #
#####################


Base = declarative_base()


class ModerationJob(Base):
    __tablename__ = MODERATION_JOB_QUEUE

    id = Column(Integer, primary_key=True)
    session = Column(String)
    app = Column(String)
    id_in_subsession = Column(Integer)
    round = Column(Integer)
    attempt = Column(Integer)
    prev_drawing = Column(Text)
    drawing = Column(Text)
    error = Column(Float)
    status = Column(String)

    def __repr__(self) -> str:
        return f"ModerationJob(id={self.id!r}, session={self.session!r}, app={self.app!r}, player={self.id_in_subsession!r}, round={self.round!r}, attempt={self.attempt!r}, status={self.status!r})"


# create table for ModerationJob
Base.metadata.create_all(engine)
session = DBSession()


def moderation_status(player: BasePlayer, C: BaseConstants) -> str:
    latest_drawing = (
        session.query(ModerationJob)
        .filter_by(
            session=player.session.code,
            app=player.participant._current_app_name,
            id_in_subsession=player.id_in_subsession,
            round=player_round(player, C),
        )
        .order_by(ModerationJob.attempt.desc())
        .first()
    )

    if latest_drawing:
        # print(f"moderation_status: {latest_drawing}")
        return latest_drawing.status
    else:
        return "not_found"


def moderation_init() -> Iterable:
    result = session.query(ModerationJob).filter_by(status="wait")
    # print(f"moderation_init: {result.count()} jobs in queue")
    result = [x.__dict__ for x in result]
    for r in result:
        del r["_sa_instance_state"]
    # print([[(k, v) for k, v in r.items() if k != "drawing"] for r in result])
    return result


def moderation_change_status(new_id: int, status: str, previous: str = "wait"):
    job = session.query(ModerationJob).filter(ModerationJob.id == new_id).first()
    # print(f"moderation_change: {job}")
    if job.status == previous:
        job.status = status
        session.commit()
        print(f"moderation_change_status: id={new_id!r}, status={status!r}")
    else:
        print(
            f"ERROR moderation_change_status: status was not as expected: {previous} {job.status}"
        )


def moderation_submit(
    player: BasePlayer, drawing: ExtraModel, prev_drawing: str, C: BaseConstants
):
    job = ModerationJob(
        session=player.session.code,
        app=player.participant._current_app_name,
        id_in_subsession=player.id_in_subsession,
        round=player_round(player, C),
        attempt=drawing.attempt,
        prev_drawing=prev_drawing,
        drawing=drawing.drawing,
        error=drawing.similarity,
        status="wait",
    )
    session.add(job)
    session.commit()
    print(f"moderation_submit: {job}")


def get_latest_drawing(player: BasePlayer, Drawing: ExtraModel):
    max_id = 0
    result = None
    for drawing in Drawing.filter(player=player):
        if drawing.attempt > max_id:
            max_id = drawing.attempt
            result = drawing
    return max_id, result


### functions for "img distance"
###
def load_img_b64(img: str) -> np.ndarray:
    return load_preprocess_img(io.BytesIO(base64.b64decode(img[22:])))


def load_img_filename(img: str) -> np.ndarray:
    path = pathlib.Path("_static") / pathlib.Path(*pathlib.PurePath(img).parts[2:])
    return load_preprocess_img(path)


def load_preprocess_img(filepath) -> np.ndarray:
    im = 1 - skimage.color.rgb2gray(
        skimage.color.rgba2rgb(skimage.io.imread(filepath, plugin="pil"))
    )
    return im


# https://learnopencv.com/shape-matching-using-hu-moments-c-python/
def calc_hu_moments(img: np.ndarray) -> np.ndarray:
    mu = skimage.measure.moments_central(img)
    nu = skimage.measure.moments_normalized(mu)
    return skimage.measure.moments_hu(nu)


def calc_hu_i1(h1, h2):
    return np.absolute((1 / h1) - (1 / h2)).sum()


def calc_hu_i2(h1, h2):
    return np.absolute(h1 - h2).sum()


def calc_hu_i3(h1, h2):
    return (np.absolute(h1 - h2) / np.absolute(h1)).sum()
