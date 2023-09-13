# Background
Nowadays, human-computer interaction technologies such as gesture recognition, speech recognition and EEG signal recognition have been widely used. These new technologies open up new possibilities for game development and allow gamers to participate in games in a more intuitive and immersive manner.
In our game, you can control the character with your hands and brain waves.
# Design Summary
## EEG Module
The design of the instrument system of this project is as follows. The device uses Flowtime, an EEG head ring of return technology, to collect bioelectrical signals through the electrodes in the head ring. The emotion cloud computing interface of return technology is integrated in the app, the collected bioelectric signal data is sent to the cloud, which calculates the concentration value we need through algorithm analysis and returns it to the app, which then sends the concentration data to the raspberry pie through the UDP protocol, we need to achieve the EEG signal control.
![image.png](https://pokemongle-images-1319763739.cos.ap-nanjing.myqcloud.com/sandox/img/202309132152632.png)
## Hand detect Module
The development of gesture recognition is integrated in hand. The OPENCV and mediapipe libraries are the main base of the opencv and mediapipe libraries. Before using this module, you need to type the following on the command line to install the dependent libraries.
![image.png](https://pokemongle-images-1319763739.cos.ap-nanjing.myqcloud.com/sandox/img/202309132154477.png)
## Game dev
We choose Python pygame library for game development.
Game scene switching, role movement, role and props interaction, role and monster interaction through the state machine, the use of Python object-oriented programming inheritance features, after you've written the Superclass, you can create subclasses with new features by changing only a few lines of code.
### Scenes finite state machine
![image.png](https://pokemongle-images-1319763739.cos.ap-nanjing.myqcloud.com/sandox/img/202309132157038.png)

### Character fsm
Movement:
![image.png](https://pokemongle-images-1319763739.cos.ap-nanjing.myqcloud.com/sandox/img/202309132159225.png)
Ability:
![image.png](https://pokemongle-images-1319763739.cos.ap-nanjing.myqcloud.com/sandox/img/202309132159208.png)

### Monster fsm(take Troopa as an example)
![image.png](https://pokemongle-images-1319763739.cos.ap-nanjing.myqcloud.com/sandox/img/202309132200066.png)

### Powerup fsm(take mushroom as an example)
![image.png](https://pokemongle-images-1319763739.cos.ap-nanjing.myqcloud.com/sandox/img/202309132200477.png)

# How to control character with player's biomedical signals?
R-right hand L-left hand

|   |   |   |
|---|---|---|
|hand signal|keyboard signal|command|
|Index finger of R leans to the right|keyboard’→’|speed up right|
|Index finger of R leans to the left|keyboard’←’|speed up left|
|Index finger of the R stands in the middle|nothing|speed down(until steady)|
|Make a fist with L|space key|jump|
|Index finger of the L stands in the middle|Right Shift|attack|
|gesture1(See the example below)|Enable EEG Control|Enable the brain to control whether the character is able to attack|
|gesture2(See the example below)|Disable EEG Control|Disable the brain to control whether the character is able to attack|

gesture1:
![image.png](https://pokemongle-images-1319763739.cos.ap-nanjing.myqcloud.com/sandox/img/202309132324762.png)

gesture2:
![image.png](https://pokemongle-images-1319763739.cos.ap-nanjing.myqcloud.com/sandox/img/202309132325059.png)

# Game demo
## example1(without EEG head circle)
The figure eats the mushroom, the blood strip is yellow. The player makes a gesture 1, allowing the EEG signal to control the character to fire a fireball. Since no EEG headband is worn, the EEG signal is set to the default 0, and an exclamation point appears after FOCUS to remind the player to FOCUS.
![image.png](https://pokemongle-images-1319763739.cos.ap-nanjing.myqcloud.com/sandox/img/202309132203686.png)
At this point, the player gestures 2, the prohibition of EEG control characters can launch fireball, focus 0 can not affect characters can launch fireball attack. The exclamation point after FOCUS disappears, and a fire sign appears in the upper left corner to alert the player that the character is now able to fire a fireball.
![image.png](https://pokemongle-images-1319763739.cos.ap-nanjing.myqcloud.com/sandox/img/202309132327774.png)

## example2(with EEG head circle on head)
The player makes a gesture 1 that allows the EEG to control whether the character is able to attack, and a light bulb sign appears in the upper left corner.
1. when the FOCUS is greater than the set threshold, FOCUS after the exclamation point disappeared, the upper left corner of the fire signs. Player left index finger extended, characters can attack.
	![image.png](https://pokemongle-images-1319763739.cos.ap-nanjing.myqcloud.com/sandox/img/202309132328696.png)
2. When the FOCUS is too low, the upper right corner of the FOCUS after an exclamation point to remind the player to FOCUS, the upper left corner of the flame logo disappeared, the character can not fire a fireball attack
	![image.png](https://pokemongle-images-1319763739.cos.ap-nanjing.myqcloud.com/sandox/img/202309132329151.png)
	In addition to focus, heart rate can control the maximum rate of movement of the character, (when the heart rate is greater than 80) , considering that the player's heart rate should not be static, so no heart rate control switch, instead, set the heart rate to at least how much to control the speed of the character's movement.
