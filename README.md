<p>
  <img
    src="https://s3-us-west-2.amazonaws.com/ftwcoin.io/FTW_LOGO.png"
    width="125px;">
</p>

<h1>FTW Smart contact</h1>
<p>
  The first pure decentralized blockchain lottery based on NEO
</p>

## Philosophy 

We believe the future of the lottery is blockchain that removes geographical limitations and brings full transparency to
the process, offering unprecedented trust and quality.


## How it works

Two different parties participate this smart contract.

##### Players

Players buy lottery tickets.

##### Miners

Miners draw the lottery, verify and distribute prizes to winners. Miners earn commissions.

## Game rules

By purchasing the lottery tickets, you guarantee that you are 18 years of age and/or you have reached the minimum age for legally participating in the lottery in your country of residence.

- Ticket price: 1 FTW
- Drawing timestamp: 86400 (1 day)
- 5 numbers from 1 to 49 and 1 bonus number from 1 to 10
- Prizes
    -  5 numbers + bonus number: 1000000 FTW
    -  5 numbers: 50000 FTW
    -  4 numbers + bonus number: 500 FTW
    -  4 numbers: 250 FTW
    -  3 numbers + bonus number: 10 FTW
    -  2 numbers + bonus number: 5 FTW
    -  1 numbers + bonus number: 3 FTW
    -  bonus number: 1 FTW
    
    
## Drawing & Verifying rules

People can participate to draw the lottery and distribute prizes. It is kinds of "Proof of work" system. Whoever triggers the smart contract with its method will earn reward if the trigger succeed. 

##### Drawing

Users can trigger the smart contract to draw the current game after it passes 1 day (timestamp: 86400) from the last drawing.

- Reward: 5% of total ticket sales of the game
- Must buy at least 1 ticket to be qualified to participate
- First come First served

##### Verifying

The trigger will verify tickets.

- Reward: 5% of a ticket.
- No requirement to participate

## Winning numbers

We use the nonce field of the latest block to generate winning numbers. Check details in the source code.


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

@param address:string - player address (required)
@param int:number - five numbers from 1 to 49 and one number from 1 to 10 (more than 6 numbers are required)

buy("AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y",1,2,3,4,5,10,1,2,3,4,5,10)
```

draw(address)

```
# -- Example

@param address:string - applicant address (required)

draw("AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y")
```

verify(address)

```
# -- Example

@param address:string - applicant address (required)

draw("AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y")
```
get_pool()<br/>
get_current_game_no()<br/>
time_left()<br/>
get_last_ticket_no()<br/>
get_last_verified_ticket_no()<br/>
get_last_drawing_result()<br/>
get_ticket_info(no)<br/>
get_drawing_result(no)<br/>
get_all_tickets_by_player(address)<br/>
get_all_drawing_results_()<br/>


## Play
You can trigger method using [NEO-CLI](https://github.com/neo-project/neo-cli), [NEO-GUI](https://github.com/neo-project/neo-gui) and other NEO wallet that supports NEP5 tokens.<br/>
[FTW wallet](https://wallet.ftwcoin.io) provides nice UI for this smart contract.