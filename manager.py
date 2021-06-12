from distributed import Client, as_completed
import traceback
from yaml_input import MultipleYamlInput
from deploy import DaskDeployer
import importlib
import os
import json

# class to manage running, waiting on, and saving experiments
class Manager:

    def __init__(self, session_name, input_filenames, scheduler_address, no_scheduler=False):
        self.session_name = session_name
        self.input_filenames = input_filenames
        self.scheduler_address = scheduler_address
        self.yaml_input = MultipleYamlInput(input_filenames)
        self.dask_deployer = DaskDeployer(self.session_name, self.yaml_input.workers, 
                                            self.scheduler_address, no_scheduler)
        self.dask_deployer()
        self.client = Client(address=self.scheduler_address)
        self.client.upload_file("yaml_input.py")
        self.client.upload_file("base_experiment.py")
        for fname in self.yaml_input.required_uploads:
            self.client.upload_file(fname)
        self.client.upload_file("deploy.py")
        self.client.upload_file("manager.py")
        self.pool = []
        self.futures = []
    
    def run_all(self):
        futures = []
        for yi in self.yaml_input:
            module = self.dynamic_import(yi['experiment_module'])
            exp = module(**yi['parameters'])
            future = self.client.submit(exp.run)
            futures.append(future)
        self.futures = futures

    def save_as_completed(self):
        for future, result in as_completed(self.futures, with_results=True):
            try:
                self.save_result(result)
                print(result)
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                print("=====================")

    def save_result(self, result):
        os.makedirs(result['input']['result_directory'], exist_ok=True)
        path = result['input']['result_directory'] + "/results.json"
        if not os.path.exists(path):
            open(path, 'a').close()
        curr = []
        with open(path, 'r') as fp:
            data = fp.read()
            if data:
                curr = json.loads(data)
        curr.append(result)
        with open(path, 'w') as fp:
            fp.write(json.dumps(curr))

    def dynamic_import(self, mod):
        mod = importlib.import_module(mod)
        return mod.Experiment

def build_argparser():
    import argparse
    parser = argparse.ArgumentParser(description="setup experiment manager input")
    parser.add_argument('-s', type=str, default="dask-exp", help="dask tmux session name")
    parser.add_argument('-p', type=str, default="python-exp", help="python tmux session name")
    parser.add_argument('-i', type=str, nargs="+", help="input filenames")
    parser.add_argument('-a', type=str, default="192.168.1.37:8786", help="dask scheduler address")
    parser.add_argument('--no-scheduler', type=int, default=0, help="[0|1] turn on new dask scheduler")
    return parser

if __name__ == "__main__":
    args = build_argparser().parse_args()

    manager = Manager(args.s, args.i, args.a, bool(args.no_scheduler))
    manager.run_all()
    manager.save_as_completed()
    