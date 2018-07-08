library(dplyr)
library(ccube)
library(foreach)

sample_purity = SAMPLE_PURITY
ssm = read.table(file = 'ccube_input.tsv', sep = '\t', header = TRUE)

RunCcubePipeline(sampleName = NULL,
                 dataFolder = NULL,
                 resultFolder = NULL,
                 runAnalysis = T,
                 runQC = T,
                 runAnalysisSnap = T,
                 purity = sample_purity,
                 numOfClusterPool = 1:10,
                 numOfRepeat = NULL,
                 maxSnv=1000000,
                 multiCore = F,
                 writeOutput = T,
                 basicFormats = T,
                 ccubeInputRDataFile = NULL)