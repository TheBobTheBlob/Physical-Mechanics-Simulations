# Physical Mechanics Simulations

<p align="center">
  <img src=".github/program.png" width="750" alt="Screenshot of program"/>
</p>

As my honours project for my physical mechanics class (Physics 3201) at Missouri S&T, I created a few simulations of problems from homework and class. There are four simulations:

- A damped pendulum
- Trajectory of an object thrown off of a sloped surface
- Scattering of two hard-surface spheres
- Movement of two objects of the same mass connected by two springs

THe icon for the program is the "volleyball" icon from [Lucide Icons](https://lucide.dev/).

## Running the program

The application requires the Python programming language.

First clone/download the repository, then install the required packages using `pyproject.toml` or `requirements.txt`

```bash
python -m pip install -r requirements.txt
```

After everything is installed, run the program with `main.py`

```bash
python main.py
```

The active simulation can be changed using the list of button on the left. The right contains editable parameters for the simulation, as well as live readings of positions and velocities of objects in the simulation.

## Building the program

To create an executable pyinstaller is used. `main.spec` contains its settings.

```bash
pyinstaller main.spec
```
