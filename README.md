## DistribExp 
##### jack wolf

### What this does
simplifies process of running experiments in parallel
- `yaml` input to experiments for ease-of-input
    - no more writing long CLI lines or modifying source
    files each time you want to change the learning rate
- `dask` handles running and waiting on each job
    - resilient and powerful
    - helpful dashboard to visualize stats
    - easy to use API so you can parallelize more in your code
- `tmux` hides everything behind the scenes
    - don't have to click through a bunch of terminal windows

### Why I made this
`dask` and `distributed` are great for distributed computing and I wanted to
put a wrapper around the related code I rewrite for my projects. My goal was
to make this very general so you could use it for any type of distributed job

### How to use it
- Setup your experiment in some `my_experiment.py` file according to 

```
from base_experiment import BaseExperiment

# follow the filename.Experiment pattern
class MyExperiment(BaseExperiment):

    def __init__(self, result_directory, x=1):
        self.x = x
        self.resolved_parameters = self.resolve_parameters()  # gathers all parameters

    # follow the `filename.Experiment.run` pattern 
    def run(self):
        print(f"doing something with {self.x}")
        # result = do something with x...
        return self.create_record(self.resolved_parameters, result)
```

- Prepare an input `yaml` file 

```
# point to python file with MyExperiment class extending BaseExperiment
experiment_filename: path/to/my_experiment.py

# number of dask workers to spin up
workers: 2

# parameter grid for experiment
parameters:
  result_directory: path/to/results/my_experiment_results
  x: [1, 2, 3, 4]
```

- Find the address of your `dask-scheduler`
    - Activate your environment and run `dask-scheduler` in a terminal window
    - Look for the line that says `distributed.scheduler - INFO -   Scheduler at:   tcp://192.ABC.XY.37:8786`
- Run the `entry.py` file with the right arguments 

```
(env) user@os:~/py/distibexp$ p3 entry.py -h
usage: entry.py [-h] [-s S] [-p P] [-i I [I ...]] [-a A] [--no-scheduler NO_SCHEDULER]

setup experiment manager input

optional arguments:
  -h, --help            show this help message and exit
  -s S                  dask tmux session name
  -p P                  python tmux session name
  -i I [I ...]          input filenames
  -a A                  dask scheduler address
  --no-scheduler NO_SCHEDULER
                        [0*|1] turn on new dask scheduler
```
- For example, to run the `add_experiment.py` example with the two sample input files, the command would be
   
   ```(env) user@os:~/py/distibexp$ p3 entry.py -a 192.ABC.XY.37:8786 -i inputs/add1.yaml inputs/add2.yaml```
 - This will spin up two `tmux` sessions, one running the `dask` cluster and the other your jobs
 - By default the session names are `dask-exp` and `python-exp` and you can run `tmux ls` to see them
``` 
(env) user@os:~/py/distibexp$ tmux ls
dask-exp: 3 windows (created Fri Jun 11 19:05:06 2021)
python-exp: 1 windows (created Fri Jun 11 19:05:05 2021)
(env) user@os:~/py/distibexp$ 
```
- You're done! check on the jobs with a little bit of tmux by `$ tmux attach -t python-exp`

