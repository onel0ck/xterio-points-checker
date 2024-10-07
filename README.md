# XTERIO Points Checker

This project automates the process of checking XTERIO points for multiple wallets.

**Disclaimer:** This project is for educational purposes only. Use it responsibly and in accordance with XTERIO's terms of service.

## Features

- Multi-threaded points checking
- Proxy support for enhanced privacy
- Detailed logging with color-coded output
- Results saved to a file for easy analysis

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/onel0ck/xterio-points-checker.git
   cd xterio-points-checker
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Prepare the data files:
   - `proxies.txt`: Contains proxy addresses in the format `http://login:password@ip:port`
   - `wallets.txt`: Contains private keys of the wallets to check, one per line

## Usage

Run the script:
```
python main.py
```

## Results

- Results will be saved in `result.txt`
- Logs will be saved in `xterio_checker.log`
- Console output will show real-time progress

## Configuration

You can modify the following parameters in the `main.py` file:
- Number of worker threads
- Delay between requests
- Log format and levels

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This tool is for educational purposes only. The developers are not responsible for any misuse or damage caused by this program. Users should comply with XTERIO's terms of service and use this tool at their own risk.
