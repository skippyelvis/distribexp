# base logic each Experiment will share
class BaseExperiment:

    def __init__(self, result_directory, experiment_filename):
        assert isinstance(result_directory, str)
        assert isinstance(experiment_filename, str)
        self.result_directory = result_directory
        self.experiment_filename = experiment_filename

    def run(self):
        pass

    # create a record of this experiment with input and output
    def create_record(self, resolved_parameters, result):
        record = {
            "input": resolved_parameters,
            "output": result
        }
        return record

    # take a snapshot of experiment parameters
    # call this after you have set all important instance variables
    # in your experiment class and before you have initialized instance
    # variables you do not want stored in the output
    #
    # this is helpful because some locals have to be resolved (ie missing
    # value, default initialization, etc) and may have a different value in 
    # or be missing from the raw yaml input, and then some you do not want
    # to recor
    def resolve_parameters(self):
        return self.__dict__.copy()


    