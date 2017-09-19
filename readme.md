# Check packages
 
This Python script will try to find all virtual environments and checks if any package from a list of specified packages is installed.  

## Installation

No installation required, just grab the repo:

```
git clone http://username@gitlab/jaap.vandervelde/data-collection.git
```

## Execution

To run the script ([check_packages.py](check_packages.py)):

```
python check_packages.py
```

By default, the script will check all of C:-drive, looking for the packages mentioned in [this SK-CSIRT report](http://www.nbu.gov.sk/skcsirt-sa-20170909-pypi/).

Check command line options to search other drives, pass a different list of packages, modify the list, log more (or less) information and more:
  
```
python check_packages.py --help
```

For example:
  
```
python check_packages.py -pl package_list.txt -p !urllib -p shady -l 3 -d C -d D
```

Ideally, the script will run without errors (with no command line options provided):

```
No packages matching the criteria found.
All found virtual environments checked.
```
