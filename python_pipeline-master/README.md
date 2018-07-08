# python_pipeline
Python 2.7 pipeline for team project.

Run `python --help` to view options.

Currently project assumes input to be the `Simulations_August` folder that the professor sent us via email. If the location of this folder is not specified via the command line, it will look for it in `../Simulations_August`.

Project currently reads simulation names and tumor purities from `Truth_Values` folder. Next it reads the chromosome segments and copy numbers from the `Segments` folder. Next it reads mutation data from the `VCFs` folder, and then creates a TSV file that can be inputted into PyClone in a temporary directory.

Before you start running or editing the code of the project, it is recommended you set up a virtualenv. A tutorial on virtualenv is available here:
http://docs.python-guide.org/en/latest/dev/virtualenvs/

If you are using virtualenv with PyCharm, you can see here for instructions on how to set it up:
http://exponential.io/blog/2015/02/10/configure-pycharm-to-use-virtualenv/

You can then install the dependencies of the project with the following command:
`pip install -r requirements.txt`
You MUST run the pip install command before running or editing the code, otherwise the dependencies will be unsatisfied.

NOTE: If you're on OSX, you need to run the following shell commands after `pip install` in order to fix a problem with matplotlib:
`touch ~/.matplotlib/matplotlibrc; echo "backend: TkAgg" >> ~/.matplotlib/matplotlibrc`

NOTE: PyClone takes a large amount of time to run (24 hours across 20 samples). To skip running PyClone, you can set `DEBUG` to `True` in `pyclone_analysis.py`. After this, download the sample output from [here](https://github.com/markoglasgow/python_pipeline/releases/download/500ccube/sample_output.zip), and then unpack it into the directory where this file (README.md) is located. The password for the zip file is `PythonPipelineSampleOutput2017!`.  

Project is organized in the following way:

`main.py` - high level code parsing input arguments and then running pipeline.

`input_identifier.py` - based on the directories of the input, identifies correct class to parse the input and returns said parser class. From there, the parser class is used by the caller to read the input.

`simulation_input_reader.py` - the only input reader we currently have. Reads the input data the professor provided into 'CCFInputSample' objects. 

`ccf_input` - holds definition for 'CCFInputSample' objects and helper objects. These are objects which should hold all data (chromosome segments, copy numbers, ref/var counts etc...) necessary for any CCF script (such as PyClone or CCube) to run. This file might be split into multiple files later, because it currently holds multiple classes which are expected to grow.

`dir_manager` - hold code to help manage temporary and output directories

`utils` - small helper functions useful throughout the program

`pyclone_analysis` - contains code that will run a PyClone analysis on a given 'CCFInputSample', and then read the data outputted by PyClone.

`ccube_analysis` - contains code that will run a CCube analysis on a given 'CCFInputSample', and then read the data outputted by CCube. This code is in progress and is not yet done.

`bin10_classifier` - Code for a simple classifier which sorts mutations into 10 different bins depending on their CCF/cellular prevalence

TODO:
- Integrate PhyloWGS for CCF analysis
- Integrate Latent Dirichlet Allocation for topic modeling.
- Add options in YAML file for CCube
- Add options in YAML file for NMF
- Create a cache that will store CCF outputs cached by a hash across config and input file contents.
- When multiple cores are available, run the CCF analysis across multiple cores. Experiment with how hyperthreading affects performance on Intel CPUs.
- Write code run at init to check PATH for dependencies (such as PyClone) based on args.
- Detect when input is .zip, .tar.gz, or .bz2, and uncompress it in temporary directory.
- Add logging code which can print output of the pipeline as it's running. We will probably later use the logging code to show progress in a GUI.
- Experiment with using PyPy to speed up the execution of PyClone
- Run NMF and LDA at the same time.

- Compare CCF from real data to estimates given by PyClone/CCube/Phylowgs. Plot as boxplot of error CCube/PyClone/PhyloWGS.
- Break the boxplot down into a boxplot for every CCF bands, to show the PyClone/CCube/Phylowgs error in each band.
- Finally, have a scatter plot where Y axis is standard deviation, and X axis is mean error, and plot each sample's error rate onto there. Color the samples differently by cancer type.

- Heatmap of exposure of each sample to topic. Call it the exposure matrix.
- Make a barplot for each topic showing how strong the signal is for each band. This will be the signature in itself.
