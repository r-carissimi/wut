from . import benchmarks, export, plot, run, runtime

commands: dict = {
    "benchmarks": benchmarks,
    "run": run,
    "runtime": runtime,
    "plot": plot,
    "export": export,
}
