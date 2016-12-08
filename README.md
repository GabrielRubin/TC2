# TC2 - PyCatron

PyCatron is a Python 2.7 program capable of playing Settlers of Catan that is currently under development by Gabriel Rubin and Bruno Paz for their final course assignment in Coumputer Science at PUCRS. This program uses JSettlers as game server and plays the game with it's own Python 2.7 based agent.

### Usage

PyCatron requires [Python 2.7](https://www.python.org/) and [Java](https://www.java.com/) to run.

To run the program, you have to run the file `TC2Main.py` on a python editor ( like [PyCharm](https://www.jetbrains.com/pycharm/) ) or through command line ( you must have Python 2.7 in your SYSPATH ), like this:

```sh
$ cd Client
$ python TC2Main.py
```

And for more options and help:

```sh
$ python TC2Main.py -h
```
Running this script automatically starts the JSettlers server under the localhost ( other options in the near future ), opens a JSettlers Client window, start some JSettlers robots and starts the PyCatron agent.

### GamePlay

PyCatron is under development and can play Settlers of Catan with 3 different agents implementations:

- A Simple Agent: Capable of making simple decisions and play almost-randomly
- A MCTS Agent: A Monte Carlo Tree Search agent
- A UCT Agent: Similar to the MCTS agent, but using the Upper Confidence Bounds for Trees algorithm

We plan to make our implementation of Catan faster and create other agents in the future.

To see PyCatron agent playing a game, you just need to type a nickname on the JSettlers Client window and join the game called "TestGame" that is automatically created by our agent.
