<img src="assets/logo.png" width="200">

# WASURE - WebAssembly SUite for Runtime Evaluation

**⚠️ This is a work in progress!**

**WASURE** is a command-line toolkit that helps you **benchmark WebAssembly runtimes** with clarity. It lets you run benchmarks across multiple engines, manage runtime environments, and generate meaningful visualizations and exports for analysis.



## 🚀 Features

- Run and manage WebAssembly benchmarks across various runtimes
- Install, update, and manage runtimes with simple commands
- Export results to CSV for analysis or create plots for quick visualization
- Designed for clarity, reproducibility, and extensibility



## 🛠 Getting Started

1. **Clone the repository:**

   ```bash
   git clone https://github.com/r-carissimi/wasure.git
   cd wasure/wasure
   ```

2. **Install dependencies:**

   ```bash
   pip install -r ../requirements.txt
   ```



## 📖 How to Use WASURE

WASURE is structured as a command-line tool with modular subcommands to list, run, compare, and visualize WebAssembly benchmarks. Each subcommand has its own options, allowing you to start simple and scale up your experiments as needed.

```bash
python3 wasure.py [OPTIONS] COMMAND
```

Use `--log-level DEBUG` to troubleshoot issues and `--help` under any subcommand for more information.



### 🔍 Listing Available Benchmarks

See what benchmarks are available:

```bash
python3 wasure.py benchmarks list
```



### ⚙️ Managing Runtimes

Install, update, and manage supported runtimes:

```bash
# View available runtimes
python3 wasure.py runtimes available

# Install a runtime
python3 wasure.py runtimes install wasmtime

# Update or remove runtimes
python3 wasure.py runtimes update wasmtime
python3 wasure.py runtimes remove wasmtime

# List installed runtimes and their versions
python3 wasure.py runtimes list
python3 wasure.py runtimes version
```



### 🏃 Running Benchmarks

Run benchmarks with your chosen runtimes:

```bash
# Run a single benchmark on one runtime
python3 wasure.py run -b helloworld -r wasmtime

# Run multiple benchmarks on multiple runtimes
python3 wasure.py run -b pystone dummy dhrystone/dhrystone10M -r wasmtime wasmedge wasmer --repeat 3

# Run a raw WebAssembly file directly
python3 wasure.py run -b py2wasm/pystone/pystone.wasm -r wasmtime
```

#### Useful Flags

- `--repeat N`: Repeat each benchmark N times
- `--no-store-output`: Don’t save output, just timings
- `--results-folder <path>`: Define custom output directory



### 📊 Visualizing and Exporting Results

Plot or export results with:

```bash
# Plot benchmark output
python3 wasure.py plot results/2025-05-06_10-56-21.json

# Export results to CSV
python3 wasure.py export results/2025-05-06_10-56-21.json
```

### ✅ Checking Runtimes Support

The `check` command allows you to verify if specific benchmarks run successfully on selected runtimes. It is particularly useful when combined with the `wasm-features` or `wasi-proposals` benchmark groups. These groups enable you to track which runtime has implemented specific features or proposals.

```bash
# Check the wasm features support on all runtimes
python3 wasure.py check wasm-features

# Check the wasi proposals implementation on wasmtime and wasmedge
python3 wasure.py check wasi-proposals -r wasmtime wasmedge
```


### 💡 Run WASI benchmarks on runtimes that do not support WASI

Refer to the [Replay Merger project](https://github.com/r-carissimi/wasm-r3-replay-generator-docker) for instructions on how to run WASI benchmarks on runtimes that do not support WASI.

### ➕ Adding New Benchmarks

Refer to the [Benchmarks Management Documentation](docs/benchmarks-management.md) for detailed instructions on adding new benchmarks.

### ⚙️ Adding or Editing a Runtime

Refer to the [Runtimes Management Documentation](docs/runtimes-management.md) for detailed instructions on adding or editing runtimes.



## ⚠️ Known Limitations

- **Platform Support:** Linux and macOS are supported. Windows is currently **not** supported.
- **Path Restrictions:** Installers relying on `npm` (e.g., v8, jsc, spidermonkey) may fail if the runtimes path contains spaces.
- **Non-ASCII Characters:** JSC (JavaScriptCore) does not support payload paths with non-ASCII characters.



## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve the project. Please ensure your code follows the [PEP 8](https://peps.python.org/pep-0008/) style guide for Python to maintain consistency across the project.



## 📜 License

This project is licensed under the [GNU General Public License v3.0](LICENSE).
