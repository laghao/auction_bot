from enum import Flag
from genericpath import exists
from time import sleep
import traceback
from bitcoinrpc.authproxy import AuthServiceProxy

RPC_USERNAME = ""
RPC_PASSWORD = ""
RPC_HOSTNAME = "127.0.0.1"
RPC_PORT = 8554
WALLET = ""
WALLET_PASSWORD = ""


url = f'http://{RPC_USERNAME}:{RPC_PASSWORD}@{RPC_HOSTNAME}:{RPC_PORT}'
rpc_conn = AuthServiceProxy(url)


#getfixedintervalprice = rpc_conn.getfixedintervalprice("DUSD/USD")
#activePrice = float(getfixedintervalprice["activePrice"])
unlock = rpc_conn.walletpassphrase(WALLET_PASSWORD, 60)

auctions = rpc_conn.listauctions()
blockcount = rpc_conn.getblockcount()

loantoken = "DUSD"
vaultdata = 0
blockdiff = 800
Windollarlist = []
bidingdict = []


while vaultdata < len(auctions):
    liquidationheight = auctions[vaultdata]["liquidationHeight"]
    rblocks = liquidationheight-blockcount
    if rblocks < blockdiff:
        batchCount=auctions[vaultdata]["batchCount"]
        indexbatch = 0
        while indexbatch < batchCount:
        # collateralValue = auctions[vaultdata]["batches"][indexbatch]["collaterals"]
            #print(collateralValue)
            indexCollateral = 0
            totalactivePrice = 0
            listamounts = [[0,0,0,0,0]]
            #print(((auctions[vaultdata]["batches"][indexbatch]["loan"]).split('@'))[1])
            while indexCollateral < len(auctions[vaultdata]["batches"][indexbatch]["collaterals"]):
                # Collateral Value
                collatsplit = (auctions[vaultdata]["batches"][indexbatch]["collaterals"][indexCollateral]).split('@')
                getfixedintervalprice = rpc_conn.getfixedintervalprice(f'{collatsplit[1]}/USD')
                activePrice = (float(getfixedintervalprice["activePrice"])) * float(collatsplit[0])
                totalactivePrice += activePrice

                indexCollateral += 1
            
            # Highest Bid Amount
            if (((auctions[vaultdata]["batches"][indexbatch]["loan"]).split('@'))[1]) == loantoken:
                ### print(auctions[vaultdata]["vaultId"])
                ### print(f'{indexbatch} Index')
                ### print(f'{round(totalactivePrice,2)} Collateral Value')

                if "highestBid" in (auctions[vaultdata]["batches"][indexbatch]):
                    highestBidAmount = ((auctions[vaultdata]["batches"][indexbatch]["highestBid"]["amount"]).split('@'))
                    getfixedintervalbid = rpc_conn.getfixedintervalprice(f'{highestBidAmount[1]}/USD')
                    highestBidAmountConverted = (float(getfixedintervalbid["activePrice"])) * float(highestBidAmount[0])
                    nextBid = ((highestBidAmountConverted * 1.01)*1.01)
                    ### print(f'{round(highestBidAmountConverted,2)} highest Bid price')
                else:
                    LoanAmount = (auctions[vaultdata]["batches"][indexbatch]["loan"]).split('@')
                    getfixedLoanAmount = rpc_conn.getfixedintervalprice(f'{LoanAmount[1]}/USD')
                    nextBid = (float(getfixedLoanAmount["activePrice"])) * float(LoanAmount[0]) * 1.05 + 1
                # Next Bid Amount
                
                ### print(f'{round(nextBid,2)} Next Bid price')

                # Loan Amount
                #LoanAmount = ((auctions[vaultdata]["batches"][indexbatch]["loan"]).split('@'))
                #print(LoanAmount)
                #getfixedLoanAmount = rpc_conn.getfixedintervalprice(f'{LoanAmount[1]}/USD')
                #loanprice = (float(getfixedLoanAmount["activePrice"])) * float(LoanAmount[0])
                #print(f'{round(loanprice,2)} Loan Amount')

                # Win in Dollar  Calculation
                winDollard = totalactivePrice - round(nextBid,2)
                ### print(f'{round(winDollard,2)} Win in Dollar')

                
                # Win in percentage  Calculation
                try:
                    winPercentage = round(nextBid,2) / totalactivePrice
                except ZeroDivisionError:
                    winPercentage = 0
                ### print(f'{round((1-winPercentage)*100,2)}% Win in percentage')


                # Number of blocks until end of Bid
                rblocks=liquidationheight-blockcount
                ### print(f'{liquidationheight-blockcount} Blocks until Liquidation')
                Windollarlist.append(winDollard)
                
                if "highestBid" in auctions[vaultdata]["batches"][indexbatch]:
                    if "owner" in auctions[vaultdata]["batches"][indexbatch]["highestBid"]:
                        owner = (auctions[vaultdata]["batches"][indexbatch]["highestBid"]["owner"])
                        if owner == WALLET:
                            owner= True
                        else:
                            owner= False
                    else:
                        owner= False
                else:
                    owner= False

                bidingdict.append([(auctions[vaultdata]["vaultId"]),indexbatch,round(winDollard,2),round(nextBid,2),totalactivePrice,owner])
            
            indexbatch += 1 
    
    
    vaultdata += 1  
try:
    print(f'{round(max(Windollarlist),2)} Max Win price')
except:
    print("Red: no auctions yet")
    exit(1)

value = round(max(Windollarlist),2)

def find_highbidvault(bidingdict, value):
    return [x for x in bidingdict if x[2] == value]

if value > 30:
    x = find_highbidvault(bidingdict,value)[0]
    vault = (x[0])
    index = (x[1])
    windusd = (x[2])
    bid=(f'{x[3]}@DUSD')
    if ((rpc_conn.gettokenbalances({},True,True)).get("DUSD"))>x[3]:
        if owner is False:
            print(f'Green = VaultId: {vault} Index: {index} windusd: {windusd} current bid: {bid}')
            auctionbid = rpc_conn.placeauctionbid(str(vault),int(index),str(WALLET),str(bid))
            print(auctionbid)
        else:
            print("Red: I am the owner")
    else:
        print("Red: Insufficient funds!")
else:
    print("Red: Win below 30 Dollar")
