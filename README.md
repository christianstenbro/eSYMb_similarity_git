# eSYMb_similarity_git

GitHub repository for the eSYMb Similarity Rating Experiment

## Comments on the rating experiment script (located in the eSYMb_similarity_rating_project folder)
Currently, the image files are not included in the repository (to make commits more swift). 

I have uploaded a single folder to the OneDrive containing all drawings from study 1, 2 and 3 (called 'all_drawings')
This folder should be placed inside the '/_static/similarity/images' folder.

To test the project: 

Navigate to the project folder:

    `cd eSYMb_similarity_rating_project`

Set up a new virtual environment inside this folder:

    in the terminal you could use: `python -m venv name_of_virtual_environment´

    then activate the environment: `source name_of_virtual_environment/bin/activate´

Once the environment is activated, install the packages in the requirements.txt:

    `pip install -r requirements.txt´

Test-run the project using:

    `otree devserver´

## Comments on the R-script
The 'generate-stimuli-lists' contains the script used to reproduce the current stimuli sets loaded by the otree project. 
Everything made by the script is already included in the otree project filetree, so it is only here for reference.

If needed, we can generate new random sets after piloting.
