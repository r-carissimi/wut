from . import benchmarks, export, plot, run, runtimes

commands: dict = {
    "benchmarks": benchmarks,
    "run": run,
    "runtimes": runtimes,
    "plot": plot,
    "export": export,
}
