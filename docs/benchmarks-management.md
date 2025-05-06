# Benchmarks management

> **‼️ Note:** You probably don't need to do this as `.wasm` files can be executed directly by the run command. Adding a benchmark is useful if:
>
> - your workload needs parameters
> - you want to parse the score
> - you want to validate the output
> - you need to specify the entrypoint function



Benchmarks are located in the `benchmarks/` directory and organized into *groups*. Each group is a subfolder of `benchmarks/` and contains a `benchmarks.json` file describing one or more benchmarks. The file has the following structure:

```json
{
	"benchmarks": [
		{
			// Benchmark
		},
		{
			// Another benchmark
		}
	]
}
```

Each benchmark is an object that supports the following fields:

- `name` (**required**) → Display name of the benchmark.

- `path` (**required**) → Path of the `.wasm` file, relative to the folder the `benchmarks.json` file is in.

- `entrypoint` → Entrypoint function of the benchmark.

- `args` → Arguments to pass to the benchmarks. Is a string separated by spaces. It will be formatted with the following placeholders, useful if a file needs to be loaded. Example: `"args": "4 4096"`

  - `{path}` → The path to the folder of the benchmark. This is useful when loading a file, since an absolute path is needed. Usually files are in the `assets` directory, placed in the benchmark folder. Example:

    ```json
    "args": "{path}/assets/small.pcm",
    ```

- `output-validator` → Regex that matches the output to check that it's valid. In the following example the regex looks for the string "Dhrystones per Second:" in the output. **Avoid using patters that check that a pattern is at the start or at the end of the output** as some runtimes output statistics or informations along with the output.

  ```json
  "output-validator": "Dhrystones per Second:"
  ```

- `score-parser` → Regex pattern to extract the score from the output of the benchmark. The regex needs to have a named capture group called `score` that matches the score to be captured. Refer to the [python documentation](https://docs.python.org/3/library/re.html) to know more about named capture groups and the regex parser. Example:

  ```json
  "score-parser": "Dhrystones per Second:\\s+(?P<score>\\d+)"
  ```



## Add a benchmark

To add a benchmark create a folder inside the `benchmarks/` directory and create a `benchmarks.json` file inside the folder. Place the `.wasm` payloads in the folder and the files that benchmarks need in a folder called `assets` in your newly-created benchmark group folder.

You can refer to existing benchmark groups in the `benchmarks/` directory for working examples.