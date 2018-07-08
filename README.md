# Python Pipeline

This documentation is for end users. Developer documentation can be found in [DEVELOPERS.md](DEVELOPERS.md). Due to the limitations of the dependencies, this pipeline will only run on *NIX systems (i.e. OSX or Linux)

This is a pipeline for running CCF analysis and signature extraction on a large tumour samples. Before beginning, it's recommend you either install all the dependencies as described in [DEPENDENCIES.md](DEPENDENCIES.md), or to simply run everything from Docker. Given the large amount of dependencies and the customization required, it's recommended you use Docker.

You can run all the commands described in `Quick Start` without installing PyClone/CCube/PhyloWGS. All you have to do is `pip install -r requirements.txt` to install the basic Python dependencies. This will save you a lot of time installing dependencies, but you will not be able to run the full pipeline until you install all the dependencies listed in [DEPENDENCIES.md](DEPENDENCIES.md). 

# Quick Start

Intermediate data from running all the CCF analysis algorithms should have been provided along with the assignment submission. You can use this intermediate data to quickly run the pipeline and skip CCF analysis, which can take days.

Before running the below commands, please make sure you have correctly configured the input and output directories in `yaml/pipeline_config.yml`

    - For CCube:
    python main.py --use-intermediate-data /path/to/Test_Data/Intermediate_Data/ccube_500_intermediate_data/
    
    
    - For PyClone:
    python main.py --use-intermediate-data /path/to/Test_Data/Intermediate_Data/pyclone_500_intermediate_data/
    
    
    - For PhyloWGS:
    python main.py --use-intermediate-data /path/to/Test_Data/Intermediate_Data/phylowgs_500_intermediate_data/
    
    
You can also run the error analysis which compares the error rate for all 3 CCF algorithms:

    python main.py --error-analysis /path/to/Test_Data/Intermediate_Data/ ccube_500_intermediate_data/ /path/to/Test_Data/Intermediate_Data/pyclone_500_intermediate_data/ /path/to/Test_Data/Intermediate_Data/phylowgs_500_intermediate_data/
    
Finally, you can run the GUI web interface by executing:

    python web_interface/app.py
    
You can then access the GUI by navigating to http://localhost:5000/ in your web browser.
    
# Overview

The pipeline is divided into five stages:

- Input identification and reading: The pipeline will detect what sort of input was given to it based on the folder structure of the input, and will attempt to read it.

- CCF analysis: The pipeline will use either CCube, PyClone, or PhyloWGS to perform a CCF analysis and estimate a CCF for every mutation in the input

- Classification: The pipeline will sort the mutations into 10 bands based on their CCF. The first band will house mutations with a CCF of 0.0 - 0.1, the second band will house mutations with a CCF of 0.1 - 0.2, etc ... the last band will house mutations with a CCF of 0.9 - 1.0.

- Error analysis: If truth data is available, error analysis can optionally be run to estimate the error in the CCF estimates. 

- Topic modeling / Signature extraction: non-negative matrix factorization and Latent Dirichlet allocation will be run on the classified data to attempt to extract signatures from it.

# Command Line Options and Configuration

	usage: main.py [-h] [-c CONFIG] [-i USE_INTERMEDIATE_DATA]
								 [-a USE_CLASSIFIED_DATA]
								 [-e [ERROR_ANALYSIS [ERROR_ANALYSIS ...]]]
	
	optional arguments:
		-h, --help            show this help message and exit
		-c CONFIG_FILE_PATH, --config CONFIG_FILE_PATH
													Path for pipeline config file. If not set, looks in ./yaml/pipeline_config.yml Documentation for config file options are provided inside the config file.
		-i INTERMEDIATE_DATA_PATH, --use-intermediate-data INTERMEDIATE_DATA_PATH
													Specifies folder of intermediate data files to use. Skips running CCF analysis. Only runs bin10 classification and topic modeling.
		-a CLASSIFIED_DATA_PATH, --use-classified-data CLASSIFIED_DATA_PATH
													Specifies TSV of classified data to use. Skips running CCF analysis and bin10 classification. Only runs topic modeling.
		-e CCUBE_INTERMEDIATE_DATA_PATH PYCLONE_INTERMEDIATE_DATA_PATH PHYLOWGS_INTERMEDIATE_DATA_PATH 
		--error-analysis CCUBE_INTERMEDIATE_DATA_PATH PYCLONE_INTERMEDIATE_DATA_PATH PHYLOWGS_INTERMEDIATE_DATA_PATH 
													Runs error analysis on given folders of intermediate data. 
													3 arguments must be passed in the following order: 
													- The path to the CCube Intermediate Data folder 
													- The path to the PyClone Intermediate Data folder. 
													- The path to the PhyloWGS Intermediate Data folder. 
													Please note that this option also requires that a valid input directory be specified in 'pipeline_config.yml'

To configure the pipeline, please see sample config file provided in `yaml/pipeline_config.yml`. Documentation for each parameter is provided in the config file.
    
# Output Description

The output of the pipeline is over a dozen different files. A description of each file's contents is given below.

- `classified_data.tsv` - This file contains the counts of the classified data. Every mutation in every sample is sorted into a band according to its CCF. Every column represents a sample, every row represent a band. A value in the table is the number of mutations in that band for that sample. 
    - Class0 describes a band containing mutations with a CCF in the range [0.0, 0.1) 
    - Class1 describes a band containing mutations with a CCF in the range [0.1 - 0.2)
    - ...
    - Class9 represents a band containing mutations with a CCF in the range [0.9 - 1.0). 
    
- `lda_signature_to_band_exposure.tsv` - A TSV file describing the exposure of each signature extracted by LDA to each band. Each column is a signature, each row is a band. Every value in the table is the strength of the band for the given signature.

- `lda_signature_to_band_exposure_barplot.png` - An image of a barplot describing the exposure of each LDA signature to each band of the classified data.

- `lda_signature_to_band_exposure_heatmap.png` - An image of a heatmap describing the exposure of each LDA signature to each band of the classified data.

- `lda_sample_to_signature_exposure.tsv` - A TSV file describing how strong each signature is in each sample. Each column is a sample, each row corresponds to a signature. Every value in the table is the strength of that signature in that particular sample.

- `lda_sample_to_signature_exposure_heatmap.png` - A huge heatmap image describing how strong each signature is for each sample. Each column is a sample, each row a signature. Each value is the strength of that signature in that particular sample. 

- `nmf_W.tsv` - A TSV file describing exposure of each signature to each band. This corresponds to the 'W' matrix described in the literature for NMF. Each column is a signature, each row is a band. Every value is the strength of that band in that signature. This file corresponds to `lda_signature_to_band_exposure.tsv` from LDA. 

- `nmf_W_barplot.png` - A barplot image describing the exposure of each signature to each band. 

- `nmf_W_heatmap.png` - A heatmap image describing the exposure of each signature to each band. Each column is a signature, each row a band, each value is the exposure of that signature to that band.

- `nmf_H.tsv` - A TSV file describing how strongly each signature is in each sample. This corresponds to the 'H' matrix described in the literature for NMF. Each column is a sample, each row is a signature. Every value is the strength of that signature in that sample. This file corresponds to `lda_sample_to_signature_exposure.tsv` for LDA. 

- `nmf_H_heatmap.png` -  A huge heatmap image describing how strong each signature is in each sample. Each column is a sample, each row a signature. Each value is the strength of that signature in that sample. 

- `CCF bins error.png` - A boxplot showing the mean error in each band for the CCF algorithm that was run.

- `CCF scatter plot.png` - A scatter plot showing the error for each sample processed by the CCF algorithm. The X-Axis is mean error, the Y-axis is the standard deviation of the error. The color for each sample is the cancer type.

- `Final comparison between CCFs analysis.png` - This file is only present if `--error-analysis` is run. It's a boxplot comparing the mean error for all samples in between PyClone, CCube, and PhyloWGS

# Input Description

The pipeline is capable of reading two different formats. The first is the data given to us by the supervisor called `Simulations_August`. The second format is the data given to us by the supervisor called `for_project_10`. The pipeline is capable of automatically detecting and reading the two import formats. It is important that the input data be in one of the described input formats, and that `pipeline_config.yml` be configured to have `input_dir` point to a directory housing the input data. 

# Simulations_August Input Format

This input format requires that `input_dir` have the following directories and files present:

- `Segments` - This directory must contain a TSV file describing the chromosome segments for each sample. Each TSV file name must be in the following format: `SAMPLE_NAME_segments.txt`.The TSV files must have the following columns, in the order given:
    - `chromosome` - integer number of chromosome number for this segment
    - `start` - integer number of start of segment
    - `end` - integer number of end of segment
    - `copy_number` - integer number average total copy number for the segment
    - `minor_cn` - integer number minor copy number for the segment
    - `major_cn` - integer number major copy number for the segment
    - `cellular_prevalence` - float in range [0.0, 1.0] describing cellular prevalence of the segment
    
- `Truth_Values` - This directory must contain TSV/text files describing the tumor purity for each sample. Each file name must be in the following format: `SAMPLE_NAME_purity_ploidy_table.txt`. Each file must be a TSV with the following columns:
    - `sample` - must be exact name of samply
    - `purity` - must be a float number in range [0.0, 1.0] describing tumor purity of the sample
    - `ploidy` - value is ignored. However, must be present.

- `VCFs` - This directory must contain a VCF file describing the mutations for each sample. The VCF file name must be in the following format: `SAMPLE_NAME*.vcf`. The * is a wildcard, meaning any text can be present in that part of the filename. However, the VCF file must begin with the sample name, and it must end with `.vcf`. The VCF format must be `pcawg_consensus`.

- `BB` - This directory must contain a Battenberg file describing the CNVs for each sample. The BB file name must be in the following format: `SAMPLE_NAME_BB_file.txt`. The Battenberg file format must be `battenberg`.

Please note that error analysis is not possible on inputs with the `Simulations_August` format.

# for_project_10 Input Format

This input format requires that `input_dir` have the following directories and files present:

- `data/Segments` - This directory must contain a TSV file describing the chromosome segments for each sample. Each TSV file name must be in the following format: `SAMPLE_NAME.segments.txt`.The TSV files must have the following columns, in the order given:
    - `chromosome` - integer number of chromosome number for this segment
    - `start` - integer number of start of segment
    - `end` - integer number of end of segment
    - `copy_number` - integer number average total copy number for the segment
    - `minor_cn` - integer number minor copy number for the segment
    - `major_cn` - integer number major copy number for the segment
    - `ccf` - float in range [0.0, 1.0] describing CCF of the segment

- `data/VCF` - This directory must contain a VCF file describing the mutations for each sample. The VCF file name must be in the following format: `SAMPLE_NAME*.vcf`. The * is a wildcard, meaning any text can be present in that part of the filename. However, the VCF file must begin with the sample name, and it must end with `.vcf`. The VCF format must be `pcawg_consensus`.

- `data/BB` - This directory must contain a Battenberg file describing the CNVs for each sample. The BB file name must be in the following format: `SAMPLE_NAME.BB_file.txt`. The Battenberg file format must be `battenberg`.

- `data/pp_table.txt` - This must be a TSV file describing the sample name, tumor purity, and tumor ploidy of each sample. The TSV file must have the following columns, and must describe every input sample:
    - `sample` - name of sample (string)
    - `purity` - float number in range [0.0, 1.0] which describes the tumor purity
    - `ploidy` - column is ignored
    
Furthermore, for error analysis to be possible, the following data must be present under `input_dir`:

- `truth/Mut_Assign` - must contain a TSV file for every input sample. The TSV files must have a name in the following format: `SAMPLE_NAME.mutation_assignments.txt`. The TSV file must have the following columns:
    - `chr` - Integer number of chromosome # that mutation is located in. 
    - `pos` - Integer number of the position of the mutation
    - `cluster` - Cluster that mutation belongs to. Is integer number.
    
- `truth/Subclonal_Structure` - must contain a TSV file for every input sample. The TSV files must have a name in the following format: `SAMPLE_NAME.subclonal_structure.txt`. The TSV files must have the following columns:
    - `cluster` - Cluster ID
    - `n_ssms` - number of mutations in cluster. Value is ignored.
    - `ccf` - float number of CCF of mutations in this cluster. Number must be in range [0.0, 1.0]

# Running the full pipeline

You can run the full pipeline, including CCF analysis, by simply executing `main.py` with no parameters:

    python main.py
    
The config will be read from `yaml/pipeline_config.yml`. When running the full pipeline, we recommend you use a powerful multicore server, and that you set `multicore` to 'True' in `pipeline_config.yml`. Otherwise, the pipeline can take weeks to run on a regular laptop or desktop machine. 

# Saving CCF analysis results for reuse

After running the full pipeline with a CCF analysis, the results of the CCF analysis will be saved in a special folder in the output directory called `intermediates`. You can save this folder somewhere, and then later rerun the pipeline on this intermediate data using:

    python main.py --use-intermediate-data <path/to/intermediate/data/folder>
    
This way you don't need to rerun the full pipeline every time you want to try out different parameters for classification, NMF, or LDA. It can save a lot of time, because depending on your computer and data, the pipeline can take days or weeks to run.

# Docker
A docker image is provided pre-built. In order to run this image use the following command:

`docker load -i <name of image file>`

`docker run -it -p 5000:5000 -v path/to/input/data:/data pipeline:latest`

This will start a command prompt within the docker container from which the pipeline can be run. **If using the GUI, the pipeline assumes any intermediate data, pre-classified data, and simulation data, as specified above, is included in the mounted data folder specified using the `-v` command above. If the data cannot be found using the GUI, check that the data is in this folder.**

To run the web interface from the Docker command prompt, execute the following command:

    python web_interface/app.py
