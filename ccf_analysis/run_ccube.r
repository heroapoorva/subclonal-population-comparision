library(dplyr)
library(ccube)
library(foreach)

sample_purity = SAMPLE_PURITY
numOfClusterPool = NUMOFCLUSTERPOOL
maxSnv = MAXSNV

ssm = read.table(file = 'ccube_input.tsv', sep = '\t', header = TRUE)

RunCcubePipeline(sampleName = NULL,
                 dataFolder = NULL,
                 resultFolder = NULL,
                 runAnalysis = T,
                 runQC = T,
                 runAnalysisSnap = T,
                 purity = sample_purity,
                 numOfClusterPool = numOfClusterPool,
                 numOfRepeat = NULL,
                 maxSnv=maxSnv,
                 multiCore = F,
                 writeOutput = T,
                 basicFormats = T,
                 ccubeInputRDataFile = NULL)
