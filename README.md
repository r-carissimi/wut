<img src="assets/logo.png" width="200">

# WUT - WUT Understands Timing

> A WebAssembly benchmarking toolkit for confused humans

**⚠️ This is a work in progress!**

WUT is a command-line toolkit designed to benchmark WebAssembly runtimes and analyze their performance. It provides tools to manage benchmarks, execute them across multiple runtimes, and visualize the results in an easy-to-understand format.

## Installation

1. Clone the repository

```bash
git clone https://github.com/your-repo/wut.git
cd wut
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

Here's some example commands you can use

* List available benchmarks

```bash
python3 wut.py benchmarks list
```

* List available runtimes

```bash
python3 wut.py runtime list
```

* Run benchmarks

```bash
python3 wut.py run -b dhrystone/dhrystone100M
```

* Plot results

```bash
python3 wut.py plot results/<results-file>.json
```

### Adding new benchmarks

1. Create a new folder under benchmarks/ for your benchmark group.
2. Add a benchmarks.json file describing the benchmarks in the group.
3. Include the WebAssembly files for the benchmarks in the same folder.

Example template for `benchmarks.json`

```json
{
    "benchmarks": [
        {
            "name": "<name-of-the-benchmark>",
            "path": "<name-of-the-wasm-file>.wasm",
            "score-parser": "<regex-to-parse-the-score-from-the-output>"
        }
    ]
}
```

### Adding a new runtime

1. Edit the `runtimes/runtime.json` file by adding an entry with the following format

```json
{
	"name": "<name-of-the-runtime>",
	"command": "<absolute-path-or-relative-to-the-runtime-folder>",
	"desc": "<description-of-the-runtime>"
}
```

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve the project. Please ensure that your code follows the [PEP 8](https://peps.python.org/pep-0008/) style guide for Python to maintain consistency across the project.


## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

