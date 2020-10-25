# covid-schools

Analyses for school reopening. The folder `first_analysis` includes the folders and analyses that were used for the initial paper submission:

    https://www.medrxiv.org/content/10.1101/2020.09.08.20190942v1

The remaining folders are in active use and development, especially `testing_in_schools`.


Requirements
============

Python >=3.6 (64-bit). (Note: Python 2 is not supported, and only Python >=3.8 has been tested.)

We also recommend, but do not require, using Python virtual environments.


Installation
============

Create a virtual environment, if desired:

```
conda create -n covaschool python=3.8
conda activate covaschool
```


Install Covasim:

```
pip install covasim --upgrade
```

Install SynthPops in a folder of your choice:

```
git clone https://github.com/InstituteforDiseaseModeling/synthpops
cd synthpops
python setup.py develop
```

Install CovasimSchools:

```
git clone https://github.com/amath-idm/covid-schools
cd covid-schools
python setup.py develop
```


Quick start
===========

Run the main test script:

```
cd tests
python test_schools.py
```

If it worked, it should bring up a plot.


Slower start
============

To run the main analysis scripts, first generate the synthetic populations:

```
cd testing_in_schools
python create_sp_pop.py
```

Then run either `run_scenarios.py` or `sensitivity_scenarios.py`. NB, these are intended to be run on HPCs and will likely not work (or take more than a day to complete) on a PC.


Fonts
=====

The font "Roboto Condensed" is used for generating the figures. To use with Python:

On Linux/Mac:

1. Copy the font files you want (e.g. in the `assets` folder) to `$HOME/.fonts` or `/usr/share/fonts/truetype/`
2. Run `sudo fc-cache -f -v`
3. Confirm they're installed: `fc-list`

On Windows:

1. Open the `assets` folder in Windows Explorer and do what you need to do.

Then on all systems:

1. Rebuild matplotlib font cache: `from matplotlib import font_manager as fm; fm._rebuild()`  -- this needs to be done for every user and/or virtual environment
2. Confirm they're available: `from matplotlib import font_manager as fm; fm.findSystemFonts()`
