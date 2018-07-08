# python_pipeline
Python 2.7 pipeline for team project.

Run `python --help` to view options. Make sure you have all dependencies installed as described in [DEPENDENCIES.md](DEPENDENCIES.md)

Currently project assumes input to be the `for_project_10` folder that the professor sent us via email. By default, it will look for it in `../for_project_10`.

Before you start running or editing the code of the project, it is recommended you set up a virtualenv. A tutorial on virtualenv is available here:
http://docs.python-guide.org/en/latest/dev/virtualenvs/

If you are using virtualenv with PyCharm, you can see here for instructions on how to set it up:
http://exponential.io/blog/2015/02/10/configure-pycharm-to-use-virtualenv/

You can then install the dependencies of the project with the following command:
`pip install -r requirements.txt`
You MUST run the pip install command before running or editing the code, otherwise the dependencies will be unsatisfied.

NOTE: If you're on OSX, you need to run the following shell commands after `pip install` in order to fix a problem with matplotlib:
`touch ~/.matplotlib/matplotlibrc; echo "backend: TkAgg" >> ~/.matplotlib/matplotlibrc`

NOTE: CCF analysis takes a large amount of time to run (24 hours across 20 samples in PyClone's case). To skip running CCF analysis, you can set set `--use-intermediate-data` flag, and pass to it a path to a folder containing the intermediate data from the CCF analysis. 
- You can download the CCube intermediate data for the 500 samples from [here](https://github.com/markoglasgow/python_pipeline/files/1539713/ccube_500_intermediates.zip).  
- You can download the PyClone intermediate data for the 500 samples from [here](https://github.com/markoglasgow/python_pipeline/files/1553076/pyclone_500_intermediates.zip).  
- You can download the PhyloWGS intermediate data for the 500 samples from [here](https://github.com/markoglasgow/python_pipeline/files/1563180/phylowgs_500_intermediates.zip).  

The password for all zip files is `PythonPipelineIntermediateData2017!`. 

NOTE: If you only want to work on topic modeling, and you want to skip CCF analysis and classification, you can set the `--use-classified-data` flag, and pass to it a path to a TSV file containing the classified data. 
- You can download the CCube classified data for the 500 samples from [here](https://github.com/markoglasgow/python_pipeline/files/1539724/ccube_500_classified_data.tsv.zip).
- You can download the PyClone classified data for the 500 samples from [here](https://github.com/markoglasgow/python_pipeline/files/1553089/pyclone_500_classified_data.tsv.zip).
- You can download the PhyloWGS classified data for the 500 samples from [here](https://github.com/markoglasgow/python_pipeline/files/1563181/phylowgs_500_classified_data.tsv.zip).

Project is organized in the following way:

`main.py` - high level code parsing input arguments and then running pipeline.

`ccf_analysis` - Contains code to run CCF analysis with PyClone, CCube, and PhyloWGS, and to read their outputs. Also contains template R code to run CCube, and error analysis code to compare outputs of CCF analysis to Truth values, if Truth values are given

`classifiers` - Contains code to classify the mutation data by their CCF. Currently only has a simple bin10 classifier, which sorts the mutations into 10 bins based on their CCF.

`input_utils` - Contains code to identify and read inputs to pipeline. Also contains miscellaneous code for directory management and unzipping files.

`topic_modeling` - Contains code for topic modeling with LDA and NMF

`web_interface` - Contains code for a web interface written using [Flask](http://flask.pocoo.org/)

## Docker
Docker must be installed to build and run docker containers and images. See relevant info and downloads here; https://www.docker.com/

To build using docker, ensure docker is running, navigate to the top level dir of the app file (the level containing the `dockerfile`), and use the following command: `docker build -t pipeline:latest .` (with the fullstop!)

This will build the image. This step may take a while to complete given that OS and all dependencies are required to be installed. 

Once the image is built, create a folder with the simulation data and config_file. The `input_dir` value within the config should be `../data/<name_of_simulation_folder>` or similar as it related to the dir within the container itself. Then you can run the command: `docker run -it -v <path/to/data/folder>:/data pipeline:latest`.

This will return a command prompt within the docker container. Run the pipeline as normal, with 

`python main.py -c ../data/pipeline_config.yml` or similar.
