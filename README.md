# zano-subaddress-sweeper
"""

**Zano-subaddress-sweeper**

**Made for the Full Zano Wallet: v2.21.506**

Zano does not have a native sub-address feature. This script enables sub addresses without having to manually create new wallets. (It effictively creates the sub-address feature but not literally)
The goal of this script is to provide another layer of anonymity,
Keep in mind you will have to pay the Zano transaction fee twice.

------------------
How to use script?
------------------

**- First Change the MAIN_ADDRESS to your address**

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
To ensure you do not loss funds make sure your Main_Address is set to the correct address, ensure its in the correct format. Remember in the event your script crashes the only way to get into the wallet file is if you have your password saved.

I would not recommend editing the native_asset_id to other tokens such as FUSD.
It just wouldn't work. I plan to add support for tokens on Zano so that's why the config is there but it's not going to work right now.

--------
Donation
--------
If you found the script useful you can optionally donate

Zano Address - @therandomscripter (ZxDmHxbA8pNhg19PxaXkbodjYPrdbvXna53fvb8nZ6ZdBzAU9q45X8sh2KQVqzbt89Aar3JygaHi5edbAdLpJtny2jg61qiaJ)

"""
