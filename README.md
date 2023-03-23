# FaFi
## Overview

FaFi, a portmanteau of Face Finder, implements the YOLOv5 pre-trained model to detect any person objects in a live streaming video through the computer's camera. A Surveillance mode can be turned on and stores a snapshot of the video along with other information whenever people are detected inside the video, then an email notification will be sent to the email on file.

I designed an algorithm called objectDetection to detect the number of people in each frame captured by the live web camera. I also fine-tuned the model's inferences to achieve 6 frames per second processing rate.

## Team Members
  Team Leader- Matthew Kluska<br/>
  QA Leader- Brendan Truong<br/>
  Security Leader- Zengrui Luo<br/>
  Design and Implementation Leader- Aidan Chang<br/>
  Configuration Leader- Derric Syme<br/>
  Requirement Leader- Patounezambo Ouedraogo

## Environment Configuration
Pytorch recommended that you use Python 3.7 or greater. For the ease of creating libraries and frameworks on each device, we created a requirements.txt file that the developers can simply download. We also recommended that you create a Virtual Environment for the Fafi applicatoin.

## Setting up for Development
1. If you are using conda virtualenv
`conda install pytorch torchvision torchaudio -c pytorch`
   If you are not using virtualenv
`pip3 install torch torchvision torchaudio`
2. Install dependencies with `pip install -r requirements.txt`
3. Run `pre-commit install` to set up the git hooks.

## How to run web-app locally
1. Run `python init_db.py` to initialize the database.
2. Set environmental variable `FLASK_ENV=development`
3. Run `flask run`
4. On your browser, go to `http://127.0.0.1:5000/`

## Running unittests
1a. Run `pytest`
1b. Run `pytest --cov=.` for test coverage results.


## GitHub Repository
https://github.com/BUMETCS673/team-project-cs673olf22team5
