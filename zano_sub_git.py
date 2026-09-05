#!/usr/bin/env python3
"""
zano-subaddress-sweeper
-----------------------
Copyright (C) 2026 acf-script

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see (https://gnu.org).

---------------------------
**Made for the Full Zano Wallet: v2.21.506**

Zano does not have a native sub-address feature. This script enables sub addresses without having to manually create new wallets. (It effictively creates the sub-address feature but not literally)
- The goal of this script is to provide another layer of anonymity,
- Keep in mind you will have to pay the Zano transaction fee twice.

------------------
How to use script?
------------------
**- First Change the MAIN_ADDRESS to your address**
- Double check that SIMPLEWALLET_BIN is pointed towards the correct path
**- Ensure Full Zano Wallet is open and synced**
Now start the script
- Open File containing the script in File Explorer
- Click the address bar (or path bar) 
- type cmd
- Run the script using the command: python zano_sub_git.py
    - If you changed the name of the file you'll need to adjust "zano_sub_git.py" accordingly
Now copy and paste the "New Deposit Address" and send crypto to that address. The script will handle the sweeping function to your MAIN_ADDRESS.

----------------
Code Explanation
----------------
Each cycle:
  1. Generates a brand new Zano wallet file.
  2. Prints its address and its password (save the password - this is the only
     time the password is shown).
  3. Waits for a deposit, it prints confirmation updates every 60 seconds
  4. Once confirmed, sweeps the funds to MAIN_ADDRESS.
  5. Waits 3 minutes
  6. Shuts down that wallet's RPC server
     and starts a new cycle with a brand new wallet.

It loops forever until you press Ctrl+C. When you do, it shuts down the current wallet's RPC server.

-------------
Prerequisites
-------------
- Must have full Zano Wallet open and synced. You can find that here (https://zano.org/wallets). I don't think this will work with the Lite wallet.
- You will need to ensure python is downloaded. (https://www.python.org/downloads/)
- You need to have pip downloaded
    - to download pip open a windows powershell and enter: pip install requests

------
Extras
------
- Wallet files are kept permanently in tmp_sub_address (you can change your directory in configurations)
- I'LL SAY IT AGAIN, wallet file password is printed when created you'll NEED this password in case you accidentally stop the script or your computer shuts down.

----------
Disclaimer
----------
There are risks to automated code handling sweeping functions. I've tried and tested this script and had no singular issue though it's still possible issues 
could arise. I am not responsible for lose of funds. 
To ensure you do not loss funds make sure your MAIN_ADDRESS is set to the correct address, ensure its in the correct format. Remember in the event your script crashes the only way to get into the wallet file is if you have your password saved.

I would not recommend editing the native_asset_id to other tokens such as FUSD.
It just wouldn't work. I plan to add support for tokens on Zano so that's why the config is there but it's not going to work right now.

--------
Donation
--------
If you found the script useful you can optionally donate
Zano Address - @therandomscripter (ZxDmHxbA8pNhg19PxaXkbodjYPrdbvXna53fvb8nZ6ZdBzAU9q45X8sh2KQVqzbt89Aar3JygaHi5edbAdLpJtny2jg61qiaJ)

"""

import datetime
import os
import re
import secrets
import socket
import subprocess
import time
import requests

# Configuration

SIMPLEWALLET_BIN = r"C:\Program Files\Zano\simplewallet.exe" # This is the path to your SIMPLE_WALLET its typically in program files but double check
DAEMON_ADDRESS = "127.0.0.1:11211"
MAIN_ADDRESS = "Wallet" # YOU NEED TO CHANGE THIS, If you don't the script will cancel itself
WALLET_DIR = "./tmp_sub_address" # This is the directory your wallet files will end up in you can change it to whatever you'd like
RPC_BIND_IP = "127.0.0.1" # This decides who can send commands to your RPC. It defaults to only listening to your own machine. If you bind it to 0.0.0.0 it means anybody can execute commands on your wallet
CONFIRMATIONS_REQUIRED = 10 # This is the default confirmations required by the Zano Blockchain if you set it below 10 the script will cancel itself
NATIVE_ASSET_ID = "d6329b5b1f7c0805b5c345f4957554002a2f557845f64d7645dae0e051a6498a"
WALLET_STARTUP_TIMEOUT = 120  # seconds to wait for RPC to come up


def atomic_to_display(amount):
    return amount / (10 ** 12)

def ts():
    return datetime.datetime.now().strftime("%H:%M:%S")


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((RPC_BIND_IP, 0))
        return s.getsockname()[1]

# Safety Checks

if MAIN_ADDRESS == "Wallet" or not MAIN_ADDRESS.startswith("Zx"):
    print("Error, Your Main Address is not formatted correctly please read the instructions in the github")
    exit(1)
if not RPC_BIND_IP == "127.0.0.1":
    print("You changed the RPC_BIND_IP, I would not recommend exposing your RPC to the public internet, be careful (will resume in 5 seconds)")
    time.sleep(5)
if not NATIVE_ASSET_ID == "d6329b5b1f7c0805b5c345f4957554002a2f557845f64d7645dae0e051a6498a":
    print("You changed the Asset ID, you're in uncharted waters I've never tested other assets (will resume in 5 seconds)")
    time.sleep(5)
if CONFIRMATIONS_REQUIRED <= 9:
    print("Huh that's odd it appears you set confirmations below 10, Zano requires 10 confirmations, change it back")
    exit(1)

# Generates a brand new wallet file (non-interactive)

def generate_wallet(path, password):
    result = subprocess.run(
        [
            SIMPLEWALLET_BIN,
            f"--generate-new-wallet={path}",
            f"--password={password}",
            f"--daemon-address={DAEMON_ADDRESS}",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = result.stdout + result.stderr
    match = re.search(r"Generated new\s+wallet:\s*(\S+)", output)
    if not match:
        raise RuntimeError(f"Could not parse new wallet address from output:\n{output}")
    return match.group(1)

# Starts it in RPC server mode as a background process

def start_wallet_rpc(path, password, port):
    log_path = path + ".rpc_log.txt"
    log_file = open(log_path, "w")
    proc = subprocess.Popen(
        [
            SIMPLEWALLET_BIN,
            f"--wallet-file={path}",
            f"--password={password}",
            f"--rpc-bind-ip={RPC_BIND_IP}",
            f"--rpc-bind-port={port}",
            f"--daemon-address={DAEMON_ADDRESS}",
            "--unsecure-no-auth",
        ],
        stdout=log_file,
        stderr=subprocess.STDOUT,
    )

    rpc_url = f"http://{RPC_BIND_IP}:{port}/json_rpc"
    deadline = time.time() + WALLET_STARTUP_TIMEOUT
    while time.time() < deadline:
        if proc.poll() is not None:
            log_file.close()
            with open(log_path) as f:
                output = f.read()
            raise RuntimeError(
                f"simplewallet process exited before RPC came up "
                f"(exit code {proc.returncode}). Log ({log_path}):\n{output}"
            )
        try:
            rpc_call(rpc_url, "getbalance")
            return proc, rpc_url
        except Exception:
            time.sleep(1)
    proc.terminate()
    log_file.close()
    with open(log_path) as f:
        output = f.read()
    raise RuntimeError(f"Timed out waiting for wallet RPC to come up. Log ({log_path}):\n{output}")

# RPC stuff

def rpc_call(rpc_url, method, params=None):
    payload = {"jsonrpc": "2.0", "id": "0", "method": method, "params": params or {}}
    resp = requests.post(rpc_url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"RPC error calling {method}: {data['error']}")
    return data["result"]

# Look for incoming deposit then track confirmations

def find_incoming_deposit(rpc_url):
    """
    Returns (amount_atomic, tx_hash, confirmations) for the first incoming
    native-coin transfer seen in this wallet's history, or None if nothing
    has shown up yet.
    """
    result = rpc_call(
        rpc_url,
        "get_recent_txs_and_info3",
        {
            "count": 50,
            "offset": 0,
            "order": "FROM_BEGIN_TO_END",
            "exclude_unconfirmed": False,
            "exclude_mining_txs": False,
            "update_provision_info": True,
        },
    )
    current_height = result["pi"]["curent_height"]

    for tx in result.get("transfers", []):
        height = tx.get("height", 0)
        confirmations = (current_height - height) if height > 0 else 0
        for group in tx.get("subtransfers_by_pid", []):
            for sub in group.get("subtransfers", []):
                if sub.get("is_income") and sub.get("asset_id") == NATIVE_ASSET_ID:
                    return sub["amount"], tx["tx_hash"], confirmations
    return None

# Sweep to main wallet

def sweep_to_main(rpc_url, amount_atomic):
    send_amount = amount_atomic - 10_000_000_000
    if send_amount <= 0:
        raise RuntimeError(
            f"Deposit of {atomic_to_display(amount_atomic)} ZANO is too small "
            f"to cover the network fee."
        )
    result = rpc_call(
        rpc_url,
        "transfer",
        {
            "destinations": [
                {"address": MAIN_ADDRESS, "amount": send_amount, "asset_id": NATIVE_ASSET_ID}
            ],
            "fee": 10_000_000_000,
        },
    )
    return result["tx_hash"]

# Shut down this wallet's RPC server (wallet file is still kept)

def stop_wallet_rpc(proc, rpc_url):
    try:
        rpc_call(rpc_url, "store")
    except Exception:
        pass

    proc.terminate()
    try:
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()

def run_one_cycle(cycle_num):
    os.makedirs(WALLET_DIR, exist_ok=True)

    run_id = secrets.token_hex(4)
    wallet_path = os.path.join(WALLET_DIR, f"deposit_{run_id}.zan")
    password = secrets.token_hex(16)
    port = find_free_port()

    print(f"\n=== Cycle {cycle_num} ===")
    print(f"Generating new wallet at {wallet_path} ...")
    address = generate_wallet(wallet_path, password)
    print(f"New deposit address:\n  {address}")
    print(f"Wallet password (save this!): {password}")

    print("Starting wallet RPC server and syncing with daemon...")
    proc, rpc_url = start_wallet_rpc(wallet_path, password, port)

    try:
        print(f"[{ts()}] Waiting for a deposit (needs {CONFIRMATIONS_REQUIRED} confirmations)...")

        deposit = None
        while deposit is None or deposit[2] < CONFIRMATIONS_REQUIRED:
            time.sleep(60)
            deposit = find_incoming_deposit(rpc_url)
            if deposit is None:
                print(f"[{ts()}] Still waiting for a deposit...")
            else:
                amount, tx_hash, confirmations = deposit
                remaining = max(0, CONFIRMATIONS_REQUIRED - confirmations)
                print(
                    f"[{ts()}] Deposit seen: {atomic_to_display(amount)} ZANO - "
                    f"{confirmations}/{CONFIRMATIONS_REQUIRED} confirmations "
                    f"({remaining} to go)"
                )

        amount, deposit_tx, _ = deposit
        print(f"[{ts()}] Deposit confirmed: {atomic_to_display(amount)} ZANO (tx {deposit_tx})")

        sweep_tx = sweep_to_main(rpc_url, amount)
        print(f"[{ts()}] Sweep transaction submitted: {sweep_tx}")

        remaining = 180
        print(f"[{ts()}] Cooling down for {180}s to let the sweep settle...")
        while remaining > 0:
            wait = min(60, remaining)
            time.sleep(wait)
            remaining -= wait
            print(f"[{ts()}] Cooldown: {remaining}s remaining before treating sweep as sent")

        print(f"[{ts()}] Cooldown complete - treating sweep as sent. Cycle {cycle_num} complete.")

    finally:
        print(f"[{ts()}] Shutting down wallet RPC (file kept at {wallet_path})...")
        stop_wallet_rpc(proc, rpc_url)

# Loop

def main():
    cycle_num = 0
    try:
        while True:
            cycle_num += 1
            run_one_cycle(cycle_num)
    except KeyboardInterrupt:
        print(f"\n[{ts()}] Ctrl+C received. Stopped after cycle {cycle_num}.")

if __name__ == "__main__":
    main()
