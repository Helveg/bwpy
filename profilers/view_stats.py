import pstats, os
from pstats import SortKey

p = pstats.Stats(os.path.join(os.path.dirname(__file__), "stats.p"))
p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(0.1)
