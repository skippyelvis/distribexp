import yaml
from sklearn.model_selection import ParameterGrid
from itertools import chain

# handle experiment input through YAML files
class YamlInput:

    def __init__(self, fname):
        assert isinstance(fname, str)
        self.fname = fname
        with open(self.fname, "r") as fp:
            self.content = yaml.load(fp, Loader=yaml.FullLoader)
        self._prepare_grid()

    def __iter__(self):
        for grid_entry in ParameterGrid(self.content['parameters']):
            yield self.to_dict(grid_entry)

    def _prepare_grid(self):
        params_as_list = self.content['parameters'].copy()
        for k, v in params_as_list.items():
            if isinstance(v, list):
                continue
            params_as_list[k] = [params_as_list[k]]
        self.content['parameters'] = params_as_list

    def __len__(self):
        return len(list(self.__iter__()))

    def __getitem__(self, item):
        return self.content[item]

    def to_dict(self, param, dkeys=['workers']):
        out = self.content.copy()
        out['parameters'] = param.copy()
        for dk in dkeys:
            del out[dk]
        return out

# wrapper to merge multiple YAML inputs into one
class MultipleYamlInput:

    def __init__(self, fnames):
        assert isinstance(fnames, list)
        self.fnames = fnames
        self.yis = [YamlInput(f) for f in self.fnames]

    @property
    def workers(self):
        w = 0
        for yi in self.yis:
            w += yi['workers']
        return w

    @property
    def required_uploads(self):
        def mod2fname(mod):
            return mod.replace('.', '/') + '.py'
        imp = set([mod2fname(yi['experiment_module']) for yi in self.yis])
        return list(imp)

    def __iter__(self):
        for grid_entry in chain(*self.yis):
            yield grid_entry 

    def __len__(self):
        return sum(len(yi) for yi in self.yis)