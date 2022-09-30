# :brain: :video_game: Mind Games: natHacks-team-Meng :video_game: :brain:

### Introduction ###
Welcome to Mind Games, a free game you can play with your own Muse 2 or Muse 2 brain wave sensing device developed from the natHacks 2022 Hackathon. 

Mind Games is a simple platform jumping game- except instead of a standard keyboard input, you play with a brain sensing headband- just blink in order to trigger the character’s jump action!

natHacks is an annual hackathon hosted by the NeurAlbertaTech, an organization started by University of Alberta students to promote interest in neurotech by hosting hackathons, seminars, and networking events.
All of this code was developed from our team members: Nick Lor, Ken Weech, Shawn Lee, Tania So, and Ed Hale during the event weekend, July 29th, 2022 to August 31st, 2022.

### Why a Game? ###
Brain-Computer Interfaces (BCIs) are a direct pathway between your brain’s waves and a computer- with the intent of achieving some sort of action or collecting data.  They have shown potential in a variety of use cases- they can help disabled people communicate or control artificial limbs, detect your mood and help you meditate, and control simple video games. 

As fairly new beginners to programming and complete beginners to the neurotech domain, we wanted to dip our feet in the pond with a reasonable use case- a simple game. Additionally, there have been BCI games released in the past designed for disabled people as a form of entertainment.

### Development Process ###
We first prepared for the hackathon by learning a bit about neuroscience fundamentals through natHacks’ provided workshops and seminars. During the hackathon, we first worked to stream our Muse hardware headsets to a python program to grab some initial data using the MuseLSL python streaming package. The Muse 2 and Muse S headsets have four sensors each on them that detect Electroencephalogram (EEG) data. 

After an initial look at some sample brain wave data, we concluded the blink event would be the easiest method to trigger a jump action as beginners. We then developed the game using PyGame and interlinked the jump action.

### Result ###
We intended to make a 2 player game, but only had time to get one character working with the headset. Regardless, it was a fantastic experience that exposed us to the infinite possibilities in the neurotech world and was a great chance to improve our Python programming!

### Technical Overview ###
Mind games has a single control input, jump, which allows the brain sprite to avoid the enemy sprites.

The streaming LSL chosen was muselsl. Neurofeedback.py, located in the examples folder of the github repo, was adapted to produce eeg_boiler.py, which contains the functions setup_eeg() and run_eeg(). run_eeg() streams the raw channel data, with no fourier transforms. A simple jump_boolean is returned by run_eeg() which constantly analyzes the channel data and detects if the eeg data is over a certain threshold, which is turned to true when the user blinks. Before running game.py, a separate terminal window must be running first with the command stream muselsl, which provides the stream data utilised by setup_eeg() and run_eeg().

A server is used (MQTT broker) as the intermediate controller to communicate between the two scripts. The EEG_boiler script is responsible for publishing the output signal to the server in the channel named “JUMP”. The game.py script is responsible for subscribing to the same signal and using it to control the player movement. The server is used to handle the eeg data stream as a digestible signal that will not overwhelm the game refresh rate and cause lag.

game.py is the pygame script, creating a simple two player side-scrolling game with players fixed in the x-axis and the ability to dodge incoming enemies by jumping (or not jumping). The game begins with a Start Screen, where the player can initiate gameplay by sending a practice jump signal with the Muse device. The same jump signal is used during gameplay to avoid enemies with the run time displayed as the score. The game is ended when a player collides with an enemy, taking the users to the end screen where the score is displayed and the opportunity to start another round.

### Attribution ### 
To stream the muse data into our game, we utilized the muselsl package and adapted code found in the neurofeedback.py example. 
https://github.com/alexandrebarachant/muse-lsl
