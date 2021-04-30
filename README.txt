*********************************************
Static Configuration Generation Flow SJA1105x
*********************************************


This package contains the python tools to generate
the static configuration sequence in binary loader format
aka HEX file.

Installation
============
In order to run the files a Python 3 installation is required.
Python can be obtained from the python.org website.
It is recommended to put the python binary in the Window's PATH environment.

Additionally, the following Python packages are needed and can be installed
using pip install:
* PrettyTable v2.0.0
* IntelHex v2.3.0

This package does not need to be installed and can be be extracted to a
custom directory. The scripts are executed through the windows command line
(cmd.exe). 

For Windows:

#. Open cmd.exe

#. Navigate to the target directory 
   cd C:\your_directory

#. Execute the scripts to create the hex files, e.g.:
   python.exe sja1105QS.py

#. The script will generate a hex file (sja1105QS.hex).
   This can now be uploaded to the SHA1105Q/S using, e.g., the EVB Host Tools

Files
=====
  
sja1105_decode.py
    A diassmbler to peek into hex files and decode them.

sja1105_converter.py
    Script to generate a configstream for C.

examples_SJA1105x/sja1105_simple.py
  A simple example with reasonable defaults for the SJA1105(T).
  
examples_SJA1105x/sja1105T.py
  Same as simple.py, but with additional settings for 
  time-triggered ethernet tables only available on SJA1105T:
  TAS schedules and stream-based policing
  
examples_SJA1105x/sja1105PR_simple.py
  A simple example with reasonable defaults for SJA1105P/R.

examples_SJA1105x/sja1105QS_simple.py
  A simple example with reasonable defaults for SJA1105Q/S.

examples_SJA1105x/sja1105PR.py
  A more realistic, sophisticated example with policing and 
  credit based shaper control for for SJA1105P/R.

examples_SJA1105x/sja1105QS.py
  A more realistic, sophisticated example with policing and 
  credit based shaper control for for SJA1105Q/S.

examples_SJA1105x/sja1105QS_TSN.py
  Same as sja1105QS.py, but with the additional settings for 
  time-triggered ethernet available on SJA1105Q/S

examples_SJA1105x/sja1105SMBEVM_*
  Different examples for the SJA1105SMBEVM board


Changelog
=========

* Revision 0.1, 2.3.2017
    Initial release
* Revision 0.2 18.4.2017
    Fixed wrong symbol in L2 Forwarding Table from VLAN_BC to BC_DOMAIN.
* Revision 0.3 03.07.2017
    Moved to new branch of generation scripts
    Support for SJA1105/T and SJA1105/P/Q/R/S
    Added examples for Qbv (time aware shaper) and Qci (stream based policing)
* Revision 1.0 11.12.2017
    Added missing broadcast policiers to simple.py and simplePQRS.py
* Revision 1.1 17.02.2021
    - Reworked some settings in the examples
    - Changes for configuration class and SJA1105 tables to fix error in decoding of hex
    - Python 3