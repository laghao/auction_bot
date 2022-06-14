# auction_bot

# Run on MacOS:

## Install launchd 
´´´
cp de.bencap.run.defi.table.plist ~/Library/LaunchAgents 
sudo launchctl bootstrap gui/${UID} de.bencap.run.defi.table.plist
sudo launchctl kickstart -k gui/${UID}/de.bencap.run.defi.table
´´´

## Remove launchd 
´´´
sudo launchctl bootout gui/${UID} de.bencap.run.defi.table.plist
rm -rf auto_table_*
´´´