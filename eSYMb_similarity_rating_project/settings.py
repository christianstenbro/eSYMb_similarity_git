from os import environ


ROOMS = [
    dict(
        name="TheLineDrawingExperiment",
        display_name="The Line Drawing Experiment",
        # participant_label_file="participants.txt",
        # use_secure_urls=True
    ),
    #dict(
    #    name="moderation", display_name="Moderation client for transmission chain study"
    #),
    # dict(
    #     name='dothraki',
    #     display_name='Learn and communicate in Dothraki',
    #     participant_label_file='participants_dothraki.txt',
    #     # use_secure_urls=True
    # ),
]

SESSION_CONFIGS = [
    # dict(
    #     name='SymbolicTransmission_PREpilot',
    #     app_sequence=['con0_practice', 'con1_aesthetics', 'con2_style', 'con3_communication'],
    #     num_demo_participants=4,
    #     transmissions=1,
    # ),
#     dict(
#         name="SymbolicTransmission",
#         app_sequence=[
#             "con0_practice",
#             "con1_aesthetics",
#             "con3_communication",
#             "con2_style",
#             "goodbye",
#         ],
#         num_demo_participants=20,
#         continue_session="",
#         doc="""
# Add the session code to continue_session if this is a continuation.
# - if blank, condition 1 starts from generation 1.
# - if filled in, condition 1 starts from where the previous session left off.
#         """,
#         transmissions=9,
#     ),
#     dict(
#         name="SymbolicTransmission_livepage_test",
#         app_sequence=["con3_communication"],
#         num_demo_participants=20,
#         transmissions=9,
#         continue_session="",
#     ),
#     dict(
#         name="Moderation",
#         app_sequence=["transmission_moderation"],
#         num_demo_participants=1,
#     ),
#     dict(
#         name="Memorability",
#         app_sequence=["memorability_practice", "memorability"],
#         num_demo_participants=1,
#     ),
    dict(
        name="SimilarityRatingExperiment",
        display_name="SimilarityRatingExperiment",
        app_sequence=[#"BTL_practice", 
            "SimilarityRatingExperiment"],
        num_demo_participants=10,
    ),
    # dict(
    #     name="dothraki",
    #     display_name="Dothraki",
    #     app_sequence=['learn_dothraki', 'use_dothraki'],
    #     num_demo_participants=6,
    # ),
    # dict(
    #     name='SymbolicTransmission_Practice',
    #     app_sequence=['con0_practice'],
    #     num_demo_participants=1,
    # ),
    # dict(
    #     name='SymbolicTransmission_Aesthetics',
    #     app_sequence=['con1_aesthetics'],
    #     num_demo_participants=4,
    #     transmissions=1
    # ),
    # dict(
    #     name='SymbolicTransmission_Style',
    #     app_sequence=['con2_style'],
    #     num_demo_participants=4,
    #     transmissions=1
    # ),
    # dict(
    #     name='SymbolicTransmission_Communication',
    #     app_sequence=['con3_communication'],
    #     num_demo_participants=4,
    #     transmissions=1
    # ),
    #    dict(
    #        name='matrix_task_test_integration',
    #        app_sequence=['matrix_task'],
    #        num_demo_participants=1
    #    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ["avatar", "treatment"]
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "en"

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = "DKK"
USE_POINTS = True

ADMIN_USERNAME = "admin"
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = environ.get("OTREE_SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = "osderhfo234hr98udfo23hr9pw8h309hp98h"
