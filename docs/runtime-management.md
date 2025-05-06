# Runtime Management

All installed runtimes are listed in the `runtimes/runtimes.json` file. This file, along with the `runtimes/` folder, is automatically created when you install your first runtime. The folder also contains all files required for runtimes to operate. **Deleting the `runtimes/` directory will remove all installed runtimes.**

Each entry in the `runtimes.json` file describes an installed runtime and its properties. These entries are created by copying information from the corresponding installer file in the `installers/` directory.

### Editing Runtime Behavior

- To **modify the behavior of an installed runtime**, edit the corresponding entry in `runtimes/runtimes.json`.
- To **change the behavior for future installations**, edit the relevant installer file in the `installers/` directory.
- To **make persistent changes** to a runtime's configuration (i.e., changes that won’t be overwritten by reinstallation), update *both* the `runtimes.json` file and the corresponding installer.

## Manually adding a runtime

To manually add a runtime, modify the `runtimes/runtimes.json` file. The structure of the file is:

```json
{
	"runtimes": [
		{
			// Runtime
		},
		{
			// Another runtime
		}
	]
}
```

Add a new JSON object to the `runtimes` array. Each runtime object supports the following fields:

- name (**required**) → Display name of the runtime.

- desc (**required**) → Description shown when listing runtimes.

- version-command (**required**) → Command to retrieve the runtime version. The path can be relative to the `runtimes/` directory. Only the **first line** of output is shown.

- command (**required**) → Command used to run a WebAssembly workload. It can be relative to the `runtimes` folder. It will be formatted using the following placeholders:

  - `{payload}` (**required**) → Path to the payload. It will be a quoted absolute path to a `.wasm` file.
  - `{args}`  → Arguments to be passed to the payload, if the runtimes supports it.
  - `{entrypoint}` → Function that needs to be called, if specified by the benchmark.
  - `{entrypoint_flag}` → Runtime flag to set an entrypoint. It's substituted from  `entrypoint-flag` in the runtime object when an entrypoint is specified in the benchmark.
  - `{mount_dir}` → Path benchmark directory so that it can be mounted using WASI.

- aot-command → Command for ahead-of-time (AOT) compilation. The command can be relative to the `runtimes` folder. Specifying it triggers the AOT phase when running a benchmark. It will be formatted using the following placeholders:

  - `{input}` (**required**) → Quoted absolute path to the input `.wasm` file
  - `{output}` (**required**) → Quoted absolute path for the file that will store the compiled payload. It will be the input file with `.aot` added at the end of the name. This file is deleted automatically.

- install-dir  → Folder where the runtime is installed, relative to the `runtimes/` folder. It's used to delete the runtime.

- entrypoint-flag → Flag to be used to enable choosing an entrypoint. This will be substituted to `{entrypoint_flag}` in the command.

- update-command → Command to update the runtime, relative to the `runtimes` directory. You most probably will not want to spend time writing this if you just want to add a runtime you have installed on your system.

- stats-parser → Dictionary of regex patterns to extract runtime statistics. Sometimes runtimes print out some informations that we want to store. This is the case for some runtimes that print out the instructions count, for instance. We want to capture this information by using regexs. Each entry is a regex that matches a statistic that we want to capture. The regex needs to have a named capture group that matches the name of the regex itself. Refer to the [python documentation](https://docs.python.org/3/library/re.html) to know more about named capture groups and the regex parser.
  ```json
  "instructions_count": "Executed wasm instructions count:\\s*(?P<instructions_count>[0-9]+)"
  ```

- subruntimes → List of alternative configurations/backends for the runtime, represented by a list of subset of runtime objects. Each subruntime has the same fields that a runtime has, but does not support the following:

  - version-command, install-dir, update-command → These are related to the installation of the runtime and cannot change in a subruntime. The version of a specific configuration of a runtime is the same as the runtime without such configuration. If a runtime needs a specific build or version in order to enable a configuration, create a new runtime.
  - subruntimes → Subruntimes cannot be nested.

### Examples

Here's a minimal example with the fields that are required.

```json
{
	"name": "wasmtime",
	"desc": "Wasmtime is a standalone JIT-style runtime for WebAssembly",
	"version-command": "wasmtime -V",
	"command": "wasmtime {payload}",
}
```

Whereas this is an example of a runtime with all fields. You'll probably never have to create such a complete runtime.

```json
{
	"name": "wasmedge",
	"desc": "A CNCF extensible WebAssembly runtime.",
	"version-command": "wasmedge/bin/wasmedge --version",
	"command": "wasmedge/bin/wasmedge {entrypoint_flag} --enable-all --enable-all-statistics --dir {mount_dir} {payload} {entrypoint} {args}",
	"install-dir": "wasmedge",
	"entrypoint-flag": "--reactor",
	"update-command": "curl -sSf https://raw.githubusercontent.com/WasmEdge/WasmEdge/master/utils/install.sh | bash -s -- -p wasmedge",
	"stats-parser": {
		"execution_time_ns": "Total execution time:\\s*(?P<execution_time_ns>[0-9]+)\\s*ns",
		"wasm_time_ns": "Wasm instructions execution time:\\s*(?P<wasm_time_ns>[0-9]+)\\s*ns",
		"host_time_ns": "Host functions execution time:\\s*(?P<host_time_ns>[0-9]+)\\s*ns",
		"instructions_count": "Executed wasm instructions count:\\s*(?P<instructions_count>[0-9]+)"
	},
	"subruntimes": [
		{
			"name": "wasmedge-int",
			"command": "wasmedge/bin/wasmedge {entrypoint_flag} --enable-all --enable-all-statistics --force-interpreter --dir {mount_dir} {payload} {entrypoint} {args}",
			"desc": "WasmEdge with interpreter backend.",
			"entrypoint-flag": "--reactor",
			"stats-parser": {
				"execution_time_ns": "Total execution time:\\s*(?P<execution_time_ns>[0-9]+)\\s*ns",
				"wasm_time_ns": "Wasm instructions execution time:\\s*(?P<wasm_time_ns>[0-9]+)\\s*ns",
				"host_time_ns": "Host functions execution time:\\s*(?P<host_time_ns>[0-9]+)\\s*ns",
				"instructions_count": "Executed wasm instructions count:\\s*(?P<instructions_count>[0-9]+)"
			}
		},
		{
			"name": "wasmedge-jit",
			"command": "wasmedge/bin/wasmedge {entrypoint_flag} --enable-all --enable-all-statistics --enable-jit --dir {mount_dir} {payload} {entrypoint} {args}",
			"desc": "WasmEdge with JIT backend.",
			"entrypoint-flag": "--reactor",
			"stats-parser": {
				"compile_start_timestamp": "\\[(?P<compile_start_timestamp>[0-9\\-:.\\s]+)\\]\\s*\\[info\\]\\s*compile start",
				"verify_start_timestamp": "\\[(?P<verify_start_timestamp>[0-9\\-:.\\s]+)\\]\\s*\\[info\\]\\s*verify start",
				"optimize_start_timestamp": "\\[(?P<optimize_start_timestamp>[0-9\\-:.\\s]+)\\]\\s*\\[info\\]\\s*optimize start",
				"optimize_done_timestamp": "\\[(?P<optimize_done_timestamp>[0-9\\-:.\\s]+)\\]\\s*\\[info\\]\\s*optimize done",
				"execution_time_ns": "Total execution time:\\s*(?P<execution_time_ns>[0-9]+)\\s*ns",
				"wasm_time_ns": "Wasm instructions execution time:\\s*(?P<wasm_time_ns>[0-9]+)\\s*ns",
				"host_time_ns": "Host functions execution time:\\s*(?P<host_time_ns>[0-9]+)\\s*ns",
				"instructions_count": "Executed wasm instructions count:\\s*(?P<instructions_count>[0-9]+)"
			}
		},
		{
			"name": "wasmedge-aot",
			"command": "wasmedge/bin/wasmedge {entrypoint_flag} --enable-all --enable-all-statistics --dir {mount_dir} {payload} {entrypoint} {args}",
			"desc": "WasmEdge with AOT",
			"entrypoint-flag": "--reactor",
			"aot-command": "wasmedge/bin/wasmedge compile --enable-all {input} {output}",
			"stats-parser": {
				"execution_time_ns": "Total execution time:\\s*(?P<execution_time_ns>[0-9]+)\\s*ns",
				"wasm_time_ns": "Wasm instructions execution time:\\s*(?P<wasm_time_ns>[0-9]+)\\s*ns",
				"host_time_ns": "Host functions execution time:\\s*(?P<host_time_ns>[0-9]+)\\s*ns",
				"instructions_count": "Executed wasm instructions count:\\s*(?P<instructions_count>[0-9]+)"
			}
		}
	]
}
```



## Adding or editing a runtime installation's instructions

You'd probably have little to no reasons to do this if you don't plan adding instructions to automatically install a runtime that is not covered yet. Anyway, each installer is a json file in the `installers` folder. The file contains an object that is a superset of a runtime object as specified before. This means that it supports all the fields that a runtime has and adds the following:

- install-command (**required**) → Command to install the runtime, relative to the `runtimes` directory. Example:
  ```json
  "install-command": "curl -sSf https://raw.githubusercontent.com/WasmEdge/WasmEdge/master/utils/install.sh | bash -s -- -p wasmedge",
  ```

When a runtime is installed, the object gets copied over to the list in the runtimes file (`runtimes/runtimes.json`), leaving out the `install-command`. Check any file in the `installers/` directory for real-world examples.
