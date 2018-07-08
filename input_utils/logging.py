class PipelineLog:

    total_sams = 0
    completed_sams = 0

    def __init__(self, sams): 
        self.total_sams = sams

    def setTotalSamples(self, sams):
        self.total_sams = sams

    def incrementSams(self):
        self.completed_sams += 1

    def progress(self):
        return("Completed %d of %d samples" % (self.completed_sams, self.total_sams))

    def completedCCF(self):
        return("CCF analysis complete.")

    def completedClass(self):
        return("Sample classification complete.")

    def completedTM(self):
        return("Topic modelling complete.")
