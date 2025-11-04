# -*- coding: utf-8 -*-

#$$strtCprt
#
# AI Simple Personal Trainer
# 
# Copyright (C) 2025 Thornton Green
# 
# This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program; if not, 
# see <http://www.gnu.org/licenses>.
# Additional permission under GNU GPL version 3 section 7
#
#
#$$endCprt


"""

Module implementing a simple AI Personal Trainer using Ollama invocations

Takes in three images of a person (front, side, and back), and generates, based on which areas need improvement, a set of exercises to be added to an existing workout plan

Do not start any exercise program without first consulting with a doctor.  AI-based systems can make mistakes.

Images should always be smaller than 1024 x 1024

Images for front, side, and back should be placed at: image_front.jpeg, image_side.jpeg, image_back.jpeg respectively

Ollama AI needs to be running locally during execution

Ollama AI needs to have the llava and gpt-oss:20b models loaded

Algorithm influenced generally by Agentic AI patterns

Uses some example code from:   https://markaicode.com/process-images-ollama-multimodal-ai/

"""


import requests
import json
import base64
import re


"""
Encodes an image so it can be sent to Ollama
"""
def encode_image(image_path):
    """Convert image to base64 encoding for Ollama API"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


"""
Sends an image and text prompt to Ollama with llava, and returns the text response from Ollama
"""
def analyze_image_internal(image_path, prompt="Describe this image in detail"):
    """Send image and prompt to Ollama for analysis"""
    
    # Encode the image
    base64_image = encode_image(image_path)
    
    # Prepare the request
    payload = {
        "model": "llava",
        "prompt": prompt,
        "images": [base64_image],
        "stream": False
    }
    
    # Send request to Ollama
    response = requests.post(
        "http://localhost:11434/api/generate",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        return result['response']
    else:
        return f"Error: {response.status_code}"



"""
Sends a text prompt to Ollama with llava, and returns the text response from Ollama
"""
def send_prompt(prompt="Describe this image in detail"):
    """Send prompt to Ollama for analysis"""
    
    # Prepare the request
    payload = {
        "model": "llava",
        "prompt": prompt,
        "stream": False
    }
    
    # Send request to Ollama
    response = requests.post(
        "http://localhost:11434/api/generate",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        return result['response']
    else:
        return f"Error: {response.status_code}"



"""
Sends a text prompt to Ollama with gpt-oss, and returns the text response from Ollama
"""
def send_prompt_gpt_oss(prompt="Describe this image in detail"):
    """Send prompt to Ollama for analysis"""
    
    # Prepare the request
    payload = {
        "model": "gpt-oss:20b",
        "prompt": prompt,
        "stream": False
    }
    
    # Send request to Ollama
    response = requests.post(
        "http://localhost:11434/api/generate",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        return result['response']
    else:
        return f"Error: {response.status_code}"




"""
Constant used to parse whether a response contains a set of digits
"""
_digits = re.compile('\d')




"""
Sends an image and text prompt to Ollama with llava, and returns the text response from Ollama

Looks for a numerical rating, and validates that the response contains a rating if possible
"""
def analyze_image_rating_internal(image_path, prompt="Describe this image in detail"):

    desc = analyze_image_internal(image_path, prompt)
    count = 0
    found = ( "inappropriate" in desc ) or (  "not appropriate" in desc ) or (  "not to judge" in desc )
    found = found or ( not ( bool( _digits.search( desc ) ) ) )
    while( found and ( count < 15 ) ) :
        desc = analyze_image_internal(image_path, prompt)
        found = ( "inappropriate" in desc ) or (  "not appropriate" in desc ) or (  "not to judge" in desc )
        found = found or ( not ( bool( _digits.search( desc ) ) ) )
        count = count + 1
    return desc




"""
Constant containing additional text to be added to Ollama prompts
"""
PROMPT_ENGINEERING_RATING = "  Where there is insufficient information or the task is impossible, always make a best guess number from the information provided.  Please always produce a number."



"""
Sends an image and text prompt to Ollama with llava, and returns the text response from Ollama

Looks for a numerical rating, and gathers multiple opinions for that rating before combining them into a final summary
"""
def analyze_image_rating(image_path, inPrompt="Describe this image in detail"):

    prompt = inPrompt + PROMPT_ENGINEERING_RATING

    quality_A = analyze_image_rating_internal( image_path, prompt )

    quality_B = analyze_image_rating_internal( image_path, prompt )

    quality_C = analyze_image_rating_internal( image_path, prompt )

    prompt2 = "integrate these descriptions to generate an overall number for the person.\n\nDescription A:\n\n" +  quality_A + "\n\nDescription B:\n\n" + quality_B + "\n\nDescription C:\n\n" + quality_C

    quality_overall = send_prompt( prompt2 )

    return quality_overall





"""
Constant indicating the name of the back-side image
"""
BACK_IMAGE = "image_back.jpeg"

"""
Constant indicating the name of the front-side image
"""
FRONT_IMAGE = "image_front.jpeg"

"""
Constant indicating the name of the side image
"""
SIDE_IMAGE = "image_side.jpeg"


"""
Global AI prompt string that is appended with successive intermediate conclusions before being
sent to Ollama for an overall comparison.
"""
overPrompt = ""



"""
Returns an analysis of the relative strengths and weaknesses of the athlete

Future expansion
"""
def analyzeStrengthsAndWeaknesses( ) : 
    
    prompt = "analyze the physique of the person in the photo and summarize his athletic strengths and weaknesses"

    print( "back:" )
    quality_back = analyze_image_internal( BACK_IMAGE, prompt )

    print( quality_back )

    print( "front:" )
    quality_front = analyze_image_internal( FRONT_IMAGE, prompt )

    print( quality_front )

    print( "side:" )
    quality_side = analyze_image_internal( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to generate an overall summary of athletic strengths and weaknesses for the person.\n\nBack Photo:\n\n" +  quality_back + "\n\nFront Photo:\n\n" + quality_front + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )



"""
Returns an estimate of the bodyfat percentage of the athlete

Future expansion
"""
def analyzeBodyfat( ) : 
    
    prompt = "estimate the bodyfat percentage for the person in the photo"

    print( "back:" )
    quality_back = analyze_image_rating( BACK_IMAGE, prompt )

    print( quality_back )

    print( "front:" )
    quality_front = analyze_image_rating( FRONT_IMAGE, prompt )

    print( quality_front )

    print( "side:" )
    quality_side = analyze_image_rating( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to estimate an overall bodyfat percentage for the person.\n\nBack Photo:\n\n" +  quality_back + "\n\nFront Photo:\n\n" + quality_front + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )




"""
Appends overPrompt with a numerical estimate of the cardiovascular conditioning of the athlete
"""
def analyzeCardiovascularConditioning( ) : 
    
    prompt = "estimate the cardiovascular conditioning number on a scale from 0 to 10 for the person in the photo"

    print( "back:" )
    quality_back = analyze_image_rating( BACK_IMAGE, prompt )

    print( quality_back )

    print( "front:" )
    quality_front = analyze_image_rating( FRONT_IMAGE, prompt )

    print( quality_front )

    print( "side:" )
    quality_side = analyze_image_rating( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to estimate an overall cardiovascular conditioning number on a scale from 0 to 10 for the person.\n\nBack Photo:\n\n" +  quality_back + "\n\nFront Photo:\n\n" + quality_front + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\ncardiovascular conditioning : \n\n" + quality_overall




"""
Appends overPrompt with a numerical estimate of the neck and trapezius development of the athlete
"""
def analyzeNeckAndTraps( ) : 
    
    prompt = "estimate the muscle quality number of the neck and trapezius on a scale from 0 to 10 for the person in the photo"

    promptFront = "estimate the muscle quality number of the neck on a scale from 0 to 10 for the person in the photo"

    print( "back:" )
    quality_back = analyze_image_rating( BACK_IMAGE, prompt )

    print( quality_back )

    print( "front:" )
    quality_front = analyze_image_rating( FRONT_IMAGE, promptFront )

    print( quality_front )

    print( "side:" )
    quality_side = analyze_image_rating( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to estimate an overall muscle quality number of the neck and trapezius on a scale from 0 to 10 for the person.\n\nBack Photo:\n\n" +  quality_back + "\n\nFront Photo:\n\n" + quality_front + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\nneck : \n\n" + quality_overall




"""
Appends overPrompt with a numerical estimate of the upper chest development of the athlete
"""
def analyzeUpperChest( ) : 
    
    prompt = "estimate the muscle quality number of the upper chest on a scale from 0 to 10 for the person in the photo"

    print( "front:" )
    quality_front = analyze_image_rating( FRONT_IMAGE, prompt )

    print( quality_front )

    print( "side:" )
    quality_side = analyze_image_rating( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to estimate an overall muscle quality number of the upper chest on a scale from 0 to 10 for the person.\n\nFront Photo:\n\n" + quality_front + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\nupper chest : \n\n" + quality_overall



"""
Appends overPrompt with a numerical estimate of the lower chest development of the athlete
"""
def analyzeLowerChest( ) : 
    
    prompt = "estimate the muscle quality number of the lower chest on a scale from 0 to 10 for the person in the photo"

    print( "front:" )
    quality_front = analyze_image_rating( FRONT_IMAGE, prompt )

    print( quality_front )

    print( "side:" )
    quality_side = analyze_image_rating( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to estimate an overall muscle quality number of the lower chest on a scale from 0 to 10 for the person.\n\nFront Photo:\n\n" + quality_front + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\nlower chest : \n\n" + quality_overall



"""
Appends overPrompt with a numerical estimate of the upper abdominal development of the athlete
"""
def analyzeUpperAbdominals( ) : 
    
    prompt = "estimate the muscle quality number of the upper abdominals on a scale from 0 to 10 for the person in the photo"

    print( "front:" )
    quality_front = analyze_image_rating( FRONT_IMAGE, prompt )

    print( quality_front )

    print( "side:" )
    quality_side = analyze_image_rating( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to estimate an overall muscle quality number of the upper abdominals on a scale from 0 to 10 for the person.\n\nFront Photo:\n\n" + quality_front + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\nupper abdominals : \n\n" + quality_overall



"""
Appends overPrompt with a numerical estimate of the lower abdominal development of the athlete
"""
def analyzeLowerAbdominals( ) : 
    
    prompt = "estimate the muscle quality number of the lower abdominals on a scale from 0 to 10 for the person in the photo"

    print( "front:" )
    quality_front = analyze_image_rating( FRONT_IMAGE, prompt )

    print( quality_front )

    print( "side:" )
    quality_side = analyze_image_rating( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to estimate an overall muscle quality number of the lower abdominals on a scale from 0 to 10 for the person.\n\nFront Photo:\n\n" + quality_front + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\nlower abdominals : \n\n" + quality_overall



"""
Appends overPrompt with a numerical estimate of the quadriceps development of the athlete
"""
def analyzeQuadriceps( ) : 
    
    prompt = "estimate the muscle quality number of the quadriceps on a scale from 0 to 10 for the person in the photo"

    print( "front:" )
    quality_front = analyze_image_rating( FRONT_IMAGE, prompt )

    print( quality_front )

    print( "side:" )
    quality_side = analyze_image_rating( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to estimate an overall muscle quality number of the quadriceps on a scale from 0 to 10 for the person.\n\nFront Photo:\n\n" + quality_front + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\nquadriceps : \n\n" + quality_overall



"""
Appends overPrompt with a numerical estimate of the calves development of the athlete
"""
def analyzeCalves( ) : 
    
    prompt = "estimate the muscle quality number of the calves on a scale from 0 to 10 for the person in the photo"

    print( "back:" )
    quality_back = analyze_image_rating( BACK_IMAGE, prompt )

    print( quality_back )

    print( "side:" )
    quality_side = analyze_image_rating( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to estimate an overall muscle quality number of the calves on a scale from 0 to 10 for the person.\n\nBack Photo:\n\n" +  quality_back + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\ncalves : \n\n" + quality_overall



"""
Appends overPrompt with a numerical estimate of the hamstrings development of the athlete
"""
def analyzeHamstrings( ) : 
    
    prompt = "estimate the muscle quality number of the hamstrings on a scale from 0 to 10 for the person in the photo"

    print( "back:" )
    quality_back = analyze_image_rating( BACK_IMAGE, prompt )

    print( quality_back )

    print( "side:" )
    quality_side = analyze_image_rating( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to estimate an overall muscle quality number of the hamstrings on a scale from 0 to 10 for the person.\n\nBack Photo:\n\n" +  quality_back + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\nhamstrings : \n\n" + quality_overall



"""
Appends overPrompt with a numerical estimate of the latitssimus development of the athlete
"""
def analyzeLatissimus( ) : 
    
    prompt = "estimate the muscle quality number of the latissimus on a scale from 0 to 10 for the person in the photo"

    print( "back:" )
    quality_back = analyze_image_rating( BACK_IMAGE, prompt )

    print( quality_back )

    print( "side:" )
    quality_side = analyze_image_rating( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to estimate an overall muscle quality number of the latissimus on a scale from 0 to 10 for the person.\n\nBack Photo:\n\n" +  quality_back + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\nlatissimus : \n\n" + quality_overall



"""
Appends overPrompt with a numerical estimate of the obliques development of the athlete
"""
def analyzeObliques( ) : 
    
    prompt = "estimate the muscle quality number of the obliques on a scale from 0 to 10 for the person in the photo"

    print( "back:" )
    quality_back = analyze_image_rating( BACK_IMAGE, prompt )

    print( quality_back )

    print( "front:" )
    quality_front = analyze_image_rating( FRONT_IMAGE, prompt )

    print( quality_front )

    print( "side:" )
    quality_side = analyze_image_rating( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to estimate an overall muscle quality number of the obliques on a scale from 0 to 10 for the person.\n\nBack Photo:\n\n" +  quality_back + "\n\nFront Photo:\n\n" + quality_front + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\nobliques : \n\n" + quality_overall




"""
Appends overPrompt with a numerical estimate of the kinetic chain of the athlete
"""
def analyzeKineticChain( ) : 
    
    prompt = "estimate the kinetic chain number on a scale from 0 to 10 for the person in the photo"

    print( "back:" )
    quality_back = analyze_image_rating( BACK_IMAGE, prompt )

    print( quality_back )

    print( "front:" )
    quality_front = analyze_image_rating( FRONT_IMAGE, prompt )

    print( quality_front )

    print( "side:" )
    quality_side = analyze_image_rating( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to estimate an overall kinetic chain number on a scale from 0 to 10 for the person.\n\nBack Photo:\n\n" +  quality_back + "\n\nFront Photo:\n\n" + quality_front + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\nkinetic chain : \n\n" + quality_overall



"""
Appends overPrompt with a numerical estimate of the triceps development of the athlete
"""
def analyzeTriceps( ) : 
    
    prompt = "estimate the muscle quality number of the triceps on a scale from 0 to 10 for the person in the photo"

    print( "back:" )
    quality_back = analyze_image_rating( BACK_IMAGE, prompt )

    print( quality_back )

    print( "side:" )
    quality_side = analyze_image_rating( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to estimate an overall muscle quality number of the triceps on a scale from 0 to 10 for the person.\n\nBack Photo:\n\n" +  quality_back + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\ntriceps : \n\n" + quality_overall



"""
Appends overPrompt with a numerical estimate of the biceps development of the athlete
"""
def analyzeBiceps( ) : 
    
    prompt = "estimate the muscle quality number of the biceps on a scale from 0 to 10 for the person in the photo"

    print( "front:" )
    quality_front = analyze_image_rating( FRONT_IMAGE, prompt )

    print( quality_front )

    print( "side:" )
    quality_side = analyze_image_rating( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to estimate an overall muscle quality number of the biceps on a scale from 0 to 10 for the person.\n\nFront Photo:\n\n" + quality_front + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\nbiceps : \n\n" + quality_overall



"""
Appends overPrompt with a numerical estimate of the front shoulder development of the athlete
"""
def analyzeFrontShoulders( ) : 
    
    prompt = "estimate the muscle quality number of the front shoulders on a scale from 0 to 10 for the person in the photo"

    print( "front:" )
    quality_front = analyze_image_rating( FRONT_IMAGE, prompt )

    print( quality_front )

    print( "side:" )
    quality_side = analyze_image_rating( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to estimate an overall muscle quality number of the front shoulders on a scale from 0 to 10 for the person.\n\nFront Photo:\n\n" + quality_front + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\nfront shoulders : \n\n" + quality_overall



"""
Appends overPrompt with a numerical estimate of the back shoulder development of the athlete
"""
def analyzeBackShoulders( ) : 
    
    prompt = "estimate the muscle quality number of the rear shoulders on a scale from 0 to 10 for the person in the photo"

    print( "back:" )
    quality_back = analyze_image_rating( BACK_IMAGE, prompt )

    print( quality_back )

    print( "side:" )
    quality_side = analyze_image_rating( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to estimate an overall muscle quality number of the rear shoulders on a scale from 0 to 10 for the person.\n\nBack Photo:\n\n" +  quality_back + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\nrear shoulders : \n\n" + quality_overall



"""
Appends overPrompt with a numerical estimate of the posture of the athlete
"""
def analyzePosture( ) : 
    
    prompt = "estimate a posture quality number on a scale from 0 to 10 for the person in the photo"

    print( "back:" )
    quality_back = analyze_image_rating( BACK_IMAGE, prompt )

    print( quality_back )

    print( "front:" )
    quality_front = analyze_image_rating( FRONT_IMAGE, prompt )

    print( quality_front )

    print( "side:" )
    quality_side = analyze_image_rating( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to estimate an overall posture quality number on a scale from 0 to 10 for the person.\n\nBack Photo:\n\n" +  quality_back + "\n\nFront Photo:\n\n" + quality_front + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\nposture : \n\n" + quality_overall



"""
Appends overPrompt with a numerical estimate of the outer chest development of the athlete
"""
def analyzeOuterChest( ) : 
    
    prompt = "estimate the muscle quality number of the outer chest on a scale from 0 to 10 for the person in the photo"

    print( "front:" )
    quality_front = analyze_image_rating( FRONT_IMAGE, prompt )

    print( quality_front )

    print( "side:" )
    quality_side = analyze_image_rating( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to estimate an overall muscle quality number of the outer chest on a scale from 0 to 10 for the person.\n\nFront Photo:\n\n" + quality_front + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\nouter chest : \n\n" + quality_overall



"""
Appends overPrompt with a numerical estimate of the upper/lower body symmetry of the athlete
"""
def analyzeUpperLowerSymmetry( ) : 
    
    prompt = "estimate a quality number for symmetry of upper body versus lower body development on a scale from 0 to 10 for the person in the photo"

    print( "back:" )
    quality_back = analyze_image_rating( BACK_IMAGE, prompt )

    print( quality_back )

    print( "front:" )
    quality_front = analyze_image_rating( FRONT_IMAGE, prompt )

    print( quality_front )

    print( "side:" )
    quality_side = analyze_image_rating( SIDE_IMAGE, prompt )

    print( quality_side )

    prompt2 = "integrate these descriptions to estimate an overall quality number for symmetry of upper body versus lower body development on a scale from 0 to 10 for the person.\n\nBack Photo:\n\n" +  quality_back + "\n\nFront Photo:\n\n" + quality_front + "\n\nSide Photo:\n\n" + quality_side

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\nupper body versus lower body symmetry : \n\n" + quality_overall



"""
Appends overPrompt with a numerical estimate of the left/right symmetry of the athlete
"""
def analyzeLeftRightSymmetry( ) : 
    
    prompt = "estimate a quality number for symmetry of left-side versus right-side body development on a scale from 0 to 10 for the person in the photo"

    print( "back:" )
    quality_back = analyze_image_rating( BACK_IMAGE, prompt )

    print( quality_back )

    print( "front:" )
    quality_front = analyze_image_rating( FRONT_IMAGE, prompt )

    print( quality_front )

    prompt2 = "integrate these descriptions to estimate an overall quality number for symmetry of left-side versus right-side body development on a scale from 0 to 10 for the person.\n\nBack Photo:\n\n" +  quality_back + "\n\nFront Photo:\n\n" + quality_front

    print( "\n\noverall:\n\n" )
    quality_overall = send_prompt( prompt2 )

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\nleft versus right body symmetry : \n\n" + quality_overall



"""
Appends overPrompt with a numerical estimate of the inner chest development of the athlete
"""
def analyzeInnerChest( ) : 
    
    prompt = "estimate the muscle quality number of the inner chest on a scale from 0 to 10 for the person in the photo"

    print( "front:" )
    quality_front = analyze_image_rating( FRONT_IMAGE, prompt )

    print( quality_front )

    quality_overall = quality_front

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\ninner chest : \n\n" + quality_overall



"""
Appends overPrompt with a numerical estimate of the upper back development of the athlete
"""
def analyzeUpperBack( ) : 
    
    prompt = "estimate the muscle quality number of the upper back on a scale from 0 to 10 for the person in the photo"

    print( "back:" )
    quality_back = analyze_image_rating( BACK_IMAGE, prompt )

    print( quality_back )

    quality_overall = quality_back

    print( quality_overall )

    global overPrompt
    overPrompt = overPrompt + "\n\nupper back : \n\n" + quality_overall





"""
Given input text in inWork, determines whether each exercise in inList is in inWork.

If the exercise is in inWork, then it is added to outList
"""
def srchExerciseEntries( inWork , inList , outList ) :

    found = False

    for item in inList : 

        prompt = "Is the following exercise already in the workout below: " + item + "?  Please answer yes or no.\n\n" + inWork

        yesNo = send_prompt( prompt )

        print( "YesNo" )
        print( yesNo )

        found = found or ( "Yes" in yesNo ) or ( "yes" in yesNo ) or ( "affirmative" in yesNo ) or ( "Affirmative" in yesNo )

    if found :
        for item in inList :
            outList.add( item )




"""
Given the contents of overPrompt, identifies weak areas and produces an overall workout plan to be added to existing workouts

Future expansion-- rewrites the plan if one or more of the exercises are already being performed and hence would not generate a positive effect
"""
def analyzeOverall( ) : 
    
    global overPrompt
    prompt = "summarize the four categories listed below with the lowest numerical ratings.  Where there is a tie and multiple categories have a low numerical rating, exercise judgement based on the surrounding descriptions to determine which four areas need the most work.  For each of the four lowest-rated areas, include information relevant to creating a customized workout to address the lagging area.\n\n" + overPrompt

    print( "\n\noverall areas:\n\n" )
    overall_areas = send_prompt( prompt )

    print( overall_areas )

    promptA = "you are the mindfulness coach for the athlete described below.  write a comprehensive list of affirmations to assert performing workouts to develop the following lagging areas and affirmations to assert peak development in the following lagging areas:\n\n" + overall_areas

    print( "\n\naffirmations:\n\n" )
    affirmations = send_prompt_gpt_oss( promptA )
    with open( "Affirmations.txt" , "w" , encoding="utf-8" ) as f :
        f.write( affirmations )

    prompt2 = "generate a set of customized workouts for an athlete to address the following lagging areas:\n\n" + overall_areas

    print( "\n\noverall work:\n\n" )
    overall_work = send_prompt_gpt_oss( prompt2 )

    print( overall_work )

    inSet =  set()
    outSet = set()

    inSet.add( "Hanging Leg Lifts" )

    inSet.add( "Hanging Toes-To_Bar Leg Lifts" )

    srchExerciseEntries( overall_work , inSet , outSet )

    inSet =  set()

    inSet.add( "Standard Push-Ups" )

    inSet.add( "One-Arm Push-Ups" )

    srchExerciseEntries( overall_work , inSet , outSet )

    inSet =  set()

    inSet.add( "Pull-Ups" )

    inSet.add( "Chin-Ups" )

    inSet.add( "Assisted One-Arm Pull-Ups" )

    srchExerciseEntries( overall_work , inSet , outSet )




    print( "\n\noutSet\n\n" )
    print( outSet )



    

    if len( outSet ) > 0 : 
        prompt3 = "The athelete is already doing the following exercises: "
        started = False

        for exer in outSet : 
            if started : 
                prompt3 = prompt3 + ", "
            started = True
            prompt3 = prompt3 + exer

        prompt3 = prompt3 + ".  Rewrite the workout below so that it doesn't contain any of the aforementioned exercises.  When an exercisde is removed. replace it with a more intense exercise in the same category that will challenge the athlete.  When an exercise is removed, try to replace it with a more advanced exercise in a similar progression.  For instance, if hanging leg raises are to be removed then some potential replacements might be ice-cream makers or some other exercise starting a calisthenic progression to a front lever.  Replace exercises in the following workout:\n\n" + overall_work

        print( "\n\nfinal work:\n\n" )
        final_work = send_prompt_gpt_oss( prompt3 )

        print( final_work )
        with open( "FinalWorkout.txt" , "w" , encoding="utf-8" ) as f :
            f.write( final_work )
    else : 
        print( "final work same as overall work" )
        with open( "FinalWorkout.txt" , "w" , encoding="utf-8" ) as f :
            f.write( overall_work )









"""
Runs the overall personal training AI algorithm sequence
"""
def overallRun() : 

    # analyzeStrengthsAndWeaknesses()
    # analyzeBodyfat()

    analyzeCardiovascularConditioning()
    analyzeNeckAndTraps()
    analyzeUpperChest()
    analyzeLowerChest()
    analyzeUpperAbdominals()
    analyzeLowerAbdominals()
    analyzeQuadriceps()
    analyzeCalves()
    analyzeHamstrings()
    analyzeLatissimus()
    analyzeObliques()
    analyzeKineticChain()
    analyzeTriceps()
    analyzeBiceps()
    analyzeFrontShoulders()
    analyzeBackShoulders()
    analyzePosture()
    analyzeOuterChest()
    analyzeUpperLowerSymmetry()
    analyzeLeftRightSymmetry()
    analyzeInnerChest()
    analyzeUpperBack()

    analyzeOverall()









"""
Runs external command line invocation of main
"""
if __name__ == "__main__":
    image_path = "sample_image.jpg"  # Replace with your image path


    

    # promptAA = "analyze the physique of the person in the photo from and summarize his athletic strengths and weaknesses"

    # promptAC = "estimate the bodyfat percentage of the person in the photo"

    # promptAD = "estimate the cardiovascular conditioning number on a scale from 0 to 10 for the person in the photo"


    overallRun()


    # description = analyze_image( image_path, promptAB2 )
    # print(description)




    