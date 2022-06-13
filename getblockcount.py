# bitcoinrpc importieren
from numbers import Rational
from time import sleep
import traceback
from bitcoinrpc.authproxy import AuthServiceProxy

# Variablen setzen mit Werten aus der defi.conf 
RPC_USERNAME = ""
RPC_PASSWORD = ""
RPC_HOSTNAME = "127.0.0.1"
RPC_PORT = 8554     # Port steht auch in der defi.conf
WALLET = "deine Walletadresse von der Desktopwallet"
WALLET_PASSWORD = "dein Passwort zum entsperren der Desktopwallet"

# Zugriff auf die Desktopwallet
url = f'http://{RPC_USERNAME}:{RPC_PASSWORD}@{RPC_HOSTNAME}:{RPC_PORT}'
rpc_conn = AuthServiceProxy(url)

# Die Variable blockcount wird durch den befehl getblockcount gesetzt. Das getblockcount ist ein API Befehl, der auf der Desktopwallet in der Konsole manuell ausgeführt werden kann.
# Das Skript mach dies, in dem rpc_conn gefolgt von einem Punkt vor dem Befehl geschrieben wird.
blockcount = rpc_conn.listauctions()

# Ausgabe des Blockcounts
print(blockcount)

# Zur Vollständigkeit hier noch der Teil, mit dem die Wallet entsperrt wird. Ist für dieses Beispiel nicht notwendig, daher auskommentiert.
# Durch diesen Befehl wird die Wallet für 60 Sekunden entsperrt.
# unlock = rpc_conn.walletpassphrase(WALLET_PASSWORD, 60)


def holefutureswapinfo():
    getblocks = 0
    while getblocks == 0:
        try:
            blockcount = rpc_conn.getblockcount()
            futureswapblock = rpc_conn.getfutureswapblock()
            futureswapcount = futureswapblock - blockcount
            getblocks = 1
        except:
            traceback.print_exc()
            sleep(10)
    maxratio = 0
    minratio = 2
    maxratiotoken = ""
    minratiotoken = ""
    pairdata = 0

    while pairdata < len(poolpairs["data"]):
        if poolpairs["data"][pairdata]["tokenB"]["symbol"] == "DUSD":
            getfixedintervalprice = rpc_conn.getfixedintervalprice(f'{poolpairs["data"][pairdata]["tokenA"]["symbol"]}/USD')
            dexprice = float(poolpairs["data"[pairdata]["priceRatio"]["ba"]])
            nextprice = float(getfixedintervalprice["nextPrice"])
            ratio = round(dexprice/nextprice,4)
            if maxratio < ratio:
                maxratio = ratio
                maxratiotoken = poolpairs["data"][pairdata]["tokenA"]["symbol"]
            if minratio > ratio:
                minratio = ratio
                minratiotoken = poolpairs["data"][pairdata]["tokenA"]["symbol"]
        pairdata += 1
    logeintrag(f'Still {futureswapcount} blocks until Futurswap - maxration {maxratiotoken} {maxratio} - minratio {minratiotoken} {minratio}')
    return(futureswapcount, maxratiotoken, maxratio, minratiotoken, minratio )


        


# Ratio DUSD USD
# https://dfi.terac.de/auctions