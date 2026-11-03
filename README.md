# ThermalBench

A lightweight Linux CLI utility for CPU stress testing, temperature monitoring, and before/after thermal performance comparison.

## Features

- CPU stress testing using `stress`
- Automatic CPU thread detection
- Manual worker configuration
- Real-time CPU temperature monitoring
- Configurable temperature limit
- Before/after temperature snapshots
- Temperature comparison
- Terminal interface using `curses`

## Requirements

- Linux
- Python 3.10+
- `stress`
- `lm-sensors`

## Installation

Install dependencies:

```bash
sudo apt update
sudo apt install python3 stress lm-sensors
sudo sensors-detect
```

Clone the repository:

```bash
git clone https://github.com/NUTIS-YT/thermalbench.git
cd thermalbench
```

Run:

```bash
python3 cputest.py
```

## Configuration

Edit the configuration variables in `cputest.py`:

```python
TEMP_LIMIT = None
DEFAULT_DURATION = 300
MAX_DURATION = 3600
```

| Variable | Description |
|---|---|
| `TEMP_LIMIT` | Maximum CPU temperature in °C. `None` disables the limit. |
| `DEFAULT_DURATION` | Default test duration in seconds. |
| `MAX_DURATION` | Maximum allowed test duration in seconds. |

## Usage

Launch ThermalBench:

```bash
python3 cputest.py
```

Available operations:

1. Record temperatures before thermal paste replacement.
2. Record temperatures after thermal paste replacement.
3. Compare recorded temperatures.
4. Exit.

## Output Files

- `before.txt` — temperature snapshot before replacement.
- `after.txt` — temperature snapshot after replacement.

These files contain sensor readings and should not be committed to the repository.

## Dependencies

ThermalBench uses Python standard library modules and external system utilities.

No additional Python packages are required.

## License

This project is licensed under the MIT License.
