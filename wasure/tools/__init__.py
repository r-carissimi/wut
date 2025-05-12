from . import benchmarks, check, export, plot, run, runtimes

commands: dict = {
    "benchmarks": benchmarks,
    "run": run,
    "runtimes": runtimes,
    "plot": plot,
    "export": export,
    "check": check,
}
