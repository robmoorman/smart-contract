<p>
  <img
    src="https://s3-us-west-2.amazonaws.com/ftwcoin.io/FTW_LOGO.png"
    width="125px;">
</p>

<h1>FTW Smart contact</h1>
<p>
    The first pure decentralized blockchain lottery based on NEO
</p>


FTW token hash: 11dbc2316f35ea031449387f615d9e4b0cbafe8b<br>
POOL address: AMGqV7HJFrvxnXxVCzUjEcw4Gv3mdGReiF

#### What is decentralized lottery?
Game rules are similar to traditional lotteries but the game is managed by people. There are no fees to any organizations or 3rd parties.

### How does it work?
People can participate to draw the lottery and verify tickets and earn commissions. Similar concept to POW.

#### 1. Tickets

By purchasing the lottery tickets, you guarantee that you are 18 years of age and/or you have reached the minimum age for legally participating in the lottery in your country of residence.

##### Rules
* 1 ticket = 1 FTW.
* Users pick 5 numbers from 1 to 39.

##### How to participate
* Send 1 FTW to FTW pool address (AMGqV7HJFrvxnXxVCzUjEcw4Gv3mdGReiF). Autopick only*
* Use FTW wallet.

##### Winning prizes and odds
* Matched 5 of 5 numbers: 60,000 FTW (1 in 575,757)
* Matched 4 of 5 numbers: 700 FTW (1 in 3,387)
* Matched 3 of 5 numbers: 30 FTW (1 in 103)
* Matched 2 of 5 numbers: 3 FTW (1 in 10)


#### 2. Drawing

##### Rules
* Every users can participate to draw the lottery.
* One drawer per game. First come first served.
* Every 12 hours.
* Free to participate.
* Participators must buy at least one ticket of the current game that is being drawn. If not, submission will be rejected by the smart contract.

##### Commission
Total ticket sales of the current game x 5% of ticket price.

##### How to participate
* Send 2 FTW to FTW pool address. 2 FTW will not be transferred to the pool.
* Use FTW wallet.

##### How does FTW smart contract make winning numbers?
When the smart contract is triggered by participators, it uses nonce of the current block to create winning numbers. You can check the source code for detail.

##### Example
Current lottery game #1 sold 1000 tickets<br/>
It passed 12 hours from the last drawing which was for game #0.<br/>
User A send 2 FTW to FTW pool address.<br/>
User B hits a drawing button in FTW wallet.<br/>
A triggered the smart contract faster than B<br/>
A gets 50 FTW for commission.

#### 3. Verifying

##### Rules
* Every users can participate to verify winning tickets.
* Participators must have 1000 FTW or more to be qualified. If not, submission will be rejected by the smart contract.

##### Commission
Verified a no winning ticket = 0.05 FTW
Verified a winning ticket = 5% of winning prize.

##### How to participate
* Send 3 FTW to FTW pool address. 3 FTW will not be transferred to the pool.
* Use FTW wallet.

##### Example
After A made drawing, <br/>
Users can start to verify each of 1000 tickets if it is a winning ticket or not.


## Methods

##### NEP5 standard

- name
- symbol
- decimal
- balanceOf
- totalSupply
- transfer


##### Lottery methods

buy(address,numbers...)

```
# -- Example

@param hash:string - hash of player address
@param int:number - five numbers from 1 to 39 

buy("AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y",1,2,3,4,5)
```

draw(address)

```
# -- Example

@param hash:string - hash of applicant address

draw("AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y")
```

verify(address)

```
# -- Example

@param address:string - hash of applicant address

draw("AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y")
```
get_pool()<br/>
get_current_game_no()<br/>
get_time_left()<br/>
get_last_ticket_no()<br/>
get_last_verified_ticket_no()<br/>
get_last_drawing_ticket_no()<br/>
get_last_drawing_at()<br/>
get_ticket_info(ticket_no)<br/>
get_drawing_result(no)<br/>
get_all_tickets_by_player(address)<br/>
get_all_operators_by_player(address)<br/>
get_all_verifiers_by_player(address)<br/>
get_all_tickets_()<br/>
get_all_drawings_()<br/>
get_all_verifying_()<br/>


## Trigger
You can trigger method using [NEO-CLI](https://github.com/neo-project/neo-cli), [NEO-GUI](https://github.com/neo-project/neo-gui) and other NEO wallet that supports NEP5 tokens.<br/>
[FTW wallet](https://wallet.ftwcoin.io) provides UI for the games.