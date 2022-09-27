from hat.doit import common

DOIT_CONFIG = common.init(python_paths=['src_py'],
                          default_tasks=['dist'])

from src_doit import *  # NOQA
