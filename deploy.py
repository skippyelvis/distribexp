import libtmux

# base class for Deployers that holds tmux session
class Deployer:

    def __init__(self, session_name):
        assert isinstance(session_name, str)
        self.session_name = session_name
        self.server = libtmux.Server()
        self.session = self.server.new_session(
            self.session_name,
            kill_session=True
        )

    def setup_env(self, pane):
        pane.send_keys("conda activate dlenv")

# Deployer to set up dask environment
class DaskDeployer(Deployer):

    def __init__(self, session_name, workers, scheduler_address, no_scheduler=False):
        super().__init__(session_name)
        assert isinstance(workers, int)
        assert isinstance(scheduler_address, str)
        assert isinstance(no_scheduler, bool)
        self.workers = workers
        self.scheduler_address = scheduler_address
        self.scheduler_port = self.scheduler_address.split(":")[1]
        self.no_scheduler = no_scheduler

    def __call__(self):
        if self.no_scheduler == False:
            self.scheduler_pane()
        self.worker_pane()
        self.htop_pane()
    
    def setup_env(self, pane):
        super().setup_env(pane)
        envvars = [
            "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
            "VECLIB_MAXIMUM_THREADS", "OPENBLAS_NUM_THREADS"
        ]
        for ev in envvars:
            pane.send_keys(f"export {ev}=1")
        
    # create a pane to host dask scheduler
    def scheduler_pane(self):
        pane = self.session.attached_window.attached_pane
        self.setup_env(pane)
        pane.send_keys("conda activate dlenv")
        pane.send_keys(f"dask-scheduler --port={self.scheduler_port}")
        
    # create a pane to host dask workers
    def worker_pane(self):
        _, pane = self.new_pane_in_new_window("workers", False)
        self.setup_env(pane)
        cmd = f"dask-worker --nthreads 1 --nprocs {self.workers} {self.scheduler_address}"
        pane.send_keys(cmd)

    # create a pane to host htop
    def htop_pane(self):
        _, pane = self.new_pane_in_new_window("htop", False)
        self.setup_env(pane)
        pane.send_keys("htop")

    def new_pane_in_new_window(self, window_name, attach=False, **kw):
        window = self.session.new_window(window_name=window_name, attach=attach, **kw)
        pane = window.attached_pane
        return window, pane

# Deployer for python process running experiment
class PythonDeployer(Deployer):

    def __init__(self, session_name):
        super().__init__(session_name)
        self.setup_env(self.session.attached_window.attached_pane)

    def __call__(self, args):
        pane = self.session.attached_window.attached_pane
        pane.send_keys(f"python3 manager.py {args}")
        