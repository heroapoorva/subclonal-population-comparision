class PhylowgsAnalysis:

    def __init__(self, args):
        self.args = args
        self.verify_args()
        return

    def run_analysis(self, sample):
        print('Running phylowgs...')