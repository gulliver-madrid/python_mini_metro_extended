[![Demo](https://i.imgur.com/xpUow2f.png)](https://youtu.be/W5fCgqlECeI)

# python_mini_metro
This repo uses `pygame` to implement Mini Metro, a fun 2D strategic game where you try to optimize the max number of passengers your metro system can handle. Both human and program inputs are supported. One of the purposes of this implementation is to enable reinforcement learning agents to be trained on it.

# Installation
## Using `poetry`

`poetry install`

## Using `pip`

### On Windows
```
python -m venv myenv
myenv\Scripts\activate
```

### On Linux
```
python -m venv myenv
source myenv/bin/activate
```
### Install dependencies (both Windows and Linux)
`pip install -r requirements.txt`

# How to run
## Using `poetry`
* Run `poetry run python src/main.py`

## Using `pip`
* Run `python src/main.py`

# Testing
`python -m unittest -v`
