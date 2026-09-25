# GENJRENG - Basic Guitar Chord Training

![GENJRENG](.\bloon_genjreng.jpg)

GENJRENG is a small Python/Pygame guitar-learning game built for beginners.

> "Press the strings. Make noise. Eventually call it music."

## What is GENJRENG?

**GENJRENG** stands for:

**G**uitar **E**ducation for **N**ovice **J**am, **R**hythm, **E**xercise, **N**otes & **G**roove

The project turns basic chord practice into a simple game instead of a boring tutorial.

## Features

- **LEARN MODE** - chord diagrams, finger positions, playable chord audio, and feedback.
- **PRACTICE MODE** - random four-chord progressions with score and combo tracking.
- **CHALLENGE MODE** - timed random-chord challenge with scoring.
- **STRUMMING MODE** - visual strumming patterns and interactive strumming.
- **Procedural audio** - synthesized plucked-string guitar sounds; no external audio files are required.
- **Progress tracking** - score, best score, accuracy, and mastered chords are stored locally.
- **BLOON MODE** - absurd feedback messages when the player keeps missing chords.
- **10 basic chords** - C, G, D, Em, Am, E, A, F, Dm, Bm.

## Requirements

- Python 3
- pygame-ce
- NumPy (recommended for procedural audio; the game can start without it, but audio is disabled)

## Run

~~~bash
python -m pip install -r requirements.txt
python main.py
~~~

## Controls

- Mouse: click buttons and chord choices
- ESC: return to the main menu
- SPACE: play / strum
- 1-9 and 0: select chords in the game modes

## Source Layout

The repository uses the self-contained `main.py` implementation as the canonical runnable version.

Local editor/dev artifacts and the persistent game state file are excluded by `.gitignore`.

## Blogger Demo

Playable article on Solitude Labs:

https://solitudelabs.blogspot.com/2026/09/genjreng-guitar-education-for-beginners.html

## License

See [LICENSE.md](LICENSE.md).
