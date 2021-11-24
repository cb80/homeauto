# Restart a bobcat miner when it lost Wifi

This script is scheduled on my synology and performs the following:
* check the bobcat status and quit if it is reachable
* otherwise connect to the FRITZ!Box and switch off and on the power outlet
* it does that with proper wait times and retries

I may enhance it later with helium specific checks, e.g. triggering fast sync if needed.

Contributions are welcome! Just send me a pull request.
