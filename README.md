ThermalBench

ThermalBench is a lightweight Linux CLI utility for CPU stress testing, temperature monitoring and thermal performance comparison.

It allows you to measure CPU temperatures before and after replacing thermal paste, changing a cooling system or modifying your cooling configuration.

The utility uses the native Linux "stress" and "lm-sensors" tools to perform CPU stress tests and collect temperature readings.

Features

- Before / After testing — save separate temperature snapshots before and after hardware modifications.
- Automatic CPU stress testing — use all available logical CPU threads.
- Manual stress testing — select the number of CPU workers.
- Configurable test duration — choose between recommended and custom durations.
- Temperature monitoring — display CPU temperatures during stress testing.
- Temperature safety limit — optionally stop testing when a configured temperature threshold is reached.
- Sensor snapshots — save the complete "sensors" output to separate text files.
- Temperature comparison — compare recorded CPU temperatures in the terminal.

Requirements

Operating system

- Linux
- Python 3.10 or newer
- "stress"
- "lm-sensors"

Python dependencies

No external Python packages are required.

The project uses Python standard library modules:

- "curses" — terminal interface
- "subprocess" — system command execution
- "multiprocessing" — CPU worker management (not required in versions using external "stress")
- "pathlib" — file management
- "re" — temperature parsing
- "time" — test timing

Installation

Ubuntu / Debian

Install the required system packages:

sudo apt update
sudo apt install python3 stress lm-sensors

Configure and verify hardware sensors:

sudo sensors-detect
sensors

Clone the repository:

git clone https://github.com/YOUR_USERNAME/thermalbench.git
cd thermalbench

Run ThermalBench:

python3 cputest.py

Configuration

ThermalBench supports basic configuration directly in the source code.

Example:

TEMP_LIMIT = None
DEFAULT_DURATION = 300
MAX_DURATION = 3600

Variable| Description
"TEMP_LIMIT"| Maximum allowed CPU temperature. "None" disables the limit.
"DEFAULT_DURATION"| Recommended test duration in seconds.
"MAX_DURATION"| Maximum manually configured test duration.

Usage

Launch the application:

python3 cputest.py

Select one of the available options:

1. Before thermal paste replacement — perform a stress test and save "before.txt".
2. After thermal paste replacement — perform a stress test and save "after.txt".
3. Temperature comparison — compare previously saved measurements.

Both test modes support automatic and manual CPU worker selection.

Output files

ThermalBench stores sensor snapshots in the application directory.

thermalbench/
├── cputest.py
├── before.txt
└── after.txt

- "before.txt" — sensor readings before hardware modifications.
- "after.txt" — sensor readings after hardware modifications.

The files contain the complete output of the Linux "sensors" command.

How it works

ThermalBench uses the following workflow:

1. Select a testing profile.
2. Configure CPU stress workers.
3. Select the test duration.
4. Start CPU stress using "stress".
5. Monitor CPU temperatures.
6. Capture sensor readings while the stress test is still running.
7. Stop the stress process after saving the snapshot.

Notes

For reliable comparisons, keep the following conditions identical:

- CPU stress worker count.
- Test duration.
- CPU frequency and power settings.
- Fan speeds.
- Ambient temperature.
- Cooling configuration.

Temperature results may vary depending on the motherboard, CPU sensors, cooling system and environmental conditions.

Warning: CPU stress testing generates sustained high temperatures and power consumption. Monitor your hardware and use an appropriate temperature limit when necessary.

License

MIT License (see "LICENSE" (LICENSE)).

---

ThermalBench — Measure the difference. Not just the temperature.
