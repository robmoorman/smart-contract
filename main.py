from boa.interop.Neo.Action import RegisterAction
from boa.interop.Neo.Header import GetConsensusData
from boa.interop.Neo.Blockchain import GetHeight, GetHeader
from boa.interop.Neo.TriggerType import Verification, Application
from boa.interop.Neo.Runtime import Log, Notify, CheckWitness, GetTrigger, GetTime
from boa.builtins import concat, list, range, has_key
from boa.interop.Neo.Storage import Get, Put, GetContext, Delete

# -- Lottery Global variables
TICKET = 'ticket'
RESULT = 'result'
FLAG = 'flag'
POOL = 'pool'
CURRENT_GAME_NO = 'current_game_no'
LAST_TICKET_NO = "last_ticket_no"
LAST_VERIFIED_TICKET_NO = "last_verified_ticket_no"
LAST_DRAWING_AT = 'last_drawing_at'
LAST_DRAWING_TICKET = 'last_drawing_ticket'
DRAWING_SCHEDULE = 86400
TICKET_PRICE = 1 * 100000000  # 1 FTW
DRAWING_COMMISSION = 1 * 10000000  # 0.1 FTW
INITIAL_POOL = 5000000 * 100000000  # 5m FTW


# -- NEP5 Global variables
TOKEN_NAME = 'FTW Token'
SYMBOL = 'FTW'
# OWNER = b'#\xba\'\x03\xc52c\xe8\xd6\xe5"\xdc2 39\xdc\xd8\xee\xe9' #privatenet
OWNER = b'\x99\xd6H\x1aQh\x8c\xd1j\x0bX\x02=\x17\xd4\xdd\x9b\rS6' #testnet
DECIMALS = 8
TOTAL_SUPPLY = 100000000 * 100000000  # 100m total supply * 10^8 (decimals)

# -------------------------------------------
# Events
# -------------------------------------------

DispatchTransferEvent = RegisterAction('transfer', 'from', 'to', 'amount')
DispatchApproveEvent = RegisterAction('approval', 'owner', 'spender', 'value')
DispatchBuyEvent = RegisterAction('buy', 'from')
DispatchDrawEvent = RegisterAction('draw', 'from')

def Main(operation, args):
    trigger = GetTrigger()

    if trigger == Verification():

        is_owner = CheckWitness(OWNER)

        if is_owner:
            return True

        return False

    elif trigger == Application():

        # -- NEP5 Standard
        if operation == 'name': return TOKEN_NAME

        elif operation == 'decimals': return DECIMALS

        elif operation == 'symbol': return SYMBOL

        elif operation == 'totalSupply': return TOTAL_SUPPLY

        elif operation == 'deploy': return deploy()

        elif operation == 'balanceOf':

            if len(args) == 1:

                account = args[0]

                return balanceOf(account)

            return notifyErrorAndReturnZero("Argument count must be 1 and they must not be null")

        elif operation == 'transfer':

            if len(args) == 3:

                t_from = args[0]

                t_to = args[1]

                t_amount = args[2]

                transfer = doTransfer(t_from, t_to, t_amount)

                return transfer

            else:

                return False

        elif operation == 'transferFrom':

            if len(args) == 3:
                t_from = args[0]

                t_to = args[1]

                t_amount = args[2]

                transfer = doTransferFrom(t_from, t_to, t_amount)

                return transfer

            return False

        elif operation == 'approve':

            if len(args) == 3:
                t_owner = args[0]

                t_spender = args[1]

                t_amount = args[2]

                approve = doApprove(t_owner, t_spender, t_amount)

                return approve

            return False

        elif operation == 'allowance':

            if len(args) == 2:
                t_owner = args[0]

                t_spender = args[1]

                amount = getAllowance(t_owner, t_spender)

                return amount

            return False

        # -- FTW

        elif operation == 'buy': return buy(args)

        elif operation == 'draw':

            if len(args) == 1:

                return draw(args[0])

            else:

                return notifyErrorAndReturnFalse("Argument count must be 1 and must be address")

        elif operation == 'get_pool': return get_pool()

        elif operation == 'get_current_game_no': return get_current_game_no()

        elif operation == 'get_ticket_info':

            if len(args) == 1:

                return get_ticket_info(args[0])

            else:

                return notifyErrorAndReturnFalse("Argument count must be 1 and must be address")

        elif operation == 'get_drawing_result':

            if len(args) == 1:

                game_no = args[0]

                return get_drawing_result(game_no)

            return notifyErrorAndReturnZero("Argument count must be 1 and they must not be null")

        elif operation == 'get_last_drawing_result': return get_last_drawing_result()

        elif operation == 'get_last_ticket_no':return get_last_ticket_no()

        elif operation == 'get_last_verified_ticket_no': return get_last_verified_ticket_no()

        elif operation == 'time_left': return timeLeft()

        else: return notifyErrorAndReturnFalse('unknown operation')


def buy(args):
    """

    Method to buy tickets.

    :param args[0]: Player address: bytes
    :param args[1:6]: Lottery numbers: int

    :return: success of the purchasing
    :rtype: ticket no

    """

    player = args[0]

    referral = 0

    if len(args) == 8:

        referral = args[7]

    if player == referral:

        return notifyErrorAndReturnFalse('Player and referral can not be the same')

    numbers = list(0)

    for i in range(1, 7):

        if args[i] < 50:

            numbers.append(args[i])

    if len(numbers) != 6:

        return notifyErrorAndReturnFalse('Invalid lottery numbers')

    is_operator = CheckWitness(player)

    if not is_operator:

        return notifyErrorAndReturnFalse("Authentication failed")

    is_transferred = doTransfer(player, POOL, TICKET_PRICE)

    if is_transferred:

        current_game_no = get_current_game_no()

        new_ticket = [
            current_game_no,
            player,
            serialize_array(numbers),
            referral
        ]

        last_ticket_no = get_last_ticket_no()

        new_ticket_no = last_ticket_no + 1

        new_ticket_key = concat(TICKET, new_ticket_no)

        context = GetContext()

        Put(context, new_ticket_key, serialize_array(new_ticket))

        Put(context, LAST_TICKET_NO, new_ticket_no)

        flag = concat(FLAG,current_game_no)

        user_key = concat(flag,player)

        check_user_participation = Get(context,user_key)

        if not check_user_participation:

            Put(context,user_key,1)

        return new_ticket_no


def draw(miner):
    """
    Method by miners can draw the game

    :param miner address

    :return: success of the drawing
    :rtype: bool

    """
    is_operator = CheckWitness(miner)

    if not is_operator:

        return notifyErrorAndReturnFalse("Authentication failed")

    context = GetContext()

    miner_balance = balanceOf(miner)

    last_sold_ticket = get_last_ticket_no()

    last_drawn_ticket = Get(context, LAST_DRAWING_TICKET)

    prize_pool = get_pool()

    time_left = timeLeft()

    if (time_left >= 0):

        total_entries = last_sold_ticket - last_drawn_ticket

        if total_entries <= 0:

            return notifyErrorAndReturnFalse("No entries in the current game")

        # Check if user is qualified to draw
        current_game_no = get_current_game_no()

        flag = concat(FLAG, current_game_no)

        flag = concat(flag, miner)

        is_user_played = Get(context, flag)

        if not is_user_played:

            return notifyErrorAndReturnFalse("You did not participate the current game")

        # Get winning numbers
        winning_numbers = getLucky()

        winning_numbers = serialize_array(winning_numbers)

        key = concat(RESULT, current_game_no)

        # Winning numbers
        Put(context, key, winning_numbers)

        # Update current game no
        Put(context, CURRENT_GAME_NO, current_game_no + 1)

        # Update last drawing timestamp
        Put(context, LAST_DRAWING_AT, GetTime())

        Put(context, LAST_DRAWING_TICKET, last_sold_ticket)

        # Pay commission
        commission = total_entries * DRAWING_COMMISSION

        Put(context,miner,miner_balance + commission)

        # Update pool size
        Put(context,POOL,prize_pool - commission)

        return commission

    else:

        last_verified_ticket_no = get_last_verified_ticket_no()

        ticket_to_verify = last_verified_ticket_no + 1

        # Check if verifying stays in the past range.
        if ticket_to_verify > last_drawn_ticket:

            return notifyErrorAndReturnFalse("There is no more tickets to verify")

        key = concat(TICKET, ticket_to_verify)

        # Get target ticket to be verified
        target = Get(context, key)

        # Deserialize the information
        target = deserialize_bytearray(target)

        game_no = target[0]
        player = target[1]
        numbers = deserialize_bytearray(target[2])
        # referral = target[3]

        # The drawing info
        drawing_result = get_drawing_result(game_no)

        # Winning numbers
        winning_numbers = deserialize_bytearray(drawing_result)

        # Match the numbers
        rank = match_rank(numbers, winning_numbers)

        Put(context, LAST_VERIFIED_TICKET_NO, ticket_to_verify)

        if rank is not 0:

            # -- Pay winners

            PRIZES = [
                0,
                1000000 * 100000000,
                50000 * 100000000,
                5000 * 100000000,
                250 * 100000000,
                25 * 100000000,
                10 * 100000000,
                5 * 100000000,
                3 * 100000000,
                1 * 100000000
            ]

            prize = PRIZES[rank]

            Notify(prize)

            player_balance = Get(context, player)

            Put(context, player, player_balance + prize)

            Put(context, miner, miner_balance + DRAWING_COMMISSION)

            Put(context, POOL, prize_pool - prize - DRAWING_COMMISSION)

        else:

            Put(context, miner, miner_balance + DRAWING_COMMISSION)

            Put(context, POOL, prize_pool - DRAWING_COMMISSION)

        return DRAWING_COMMISSION


def match_rank(six_numbers,winning_numbers):
    """
    Match winning numbers
    :param six_numbers: array
    :param winning_numbers: array
    :return rank: int
    """
    rank = 0

    number_matched = 0

    five_number_dict = {}

    bonus_number = six_numbers[5]

    winning_bonus_number = winning_numbers[5]

    for i in range(0,5):
        five_number_dict[six_numbers[i]] = "1"

    for i in range(0, 5):

       if has_key(five_number_dict,winning_numbers[i]):
           number_matched += 1

    if number_matched == 5:

        if bonus_number == winning_bonus_number:

            rank = 1

        else:

            rank = 2

    elif number_matched == 4:

        if bonus_number == winning_bonus_number:

            rank = 3

        else:
            rank = 4

    elif number_matched == 3:

        if bonus_number == winning_bonus_number:

            rank = 5

        else:

            rank = 6

    elif number_matched == 2:

        if bonus_number == winning_bonus_number:

            rank = 7

    elif number_matched == 1:

        if bonus_number == winning_bonus_number:

            rank = 8

    elif number_matched == 0:

        if bonus_number == winning_bonus_number:

            rank = 9

    return rank


def get_pool():

    context = GetContext()

    return Get(context, POOL)


def get_current_game_no():

    context = GetContext()

    current_game_no = Get(context, CURRENT_GAME_NO)

    if not current_game_no:

        return 1

    else: return current_game_no


def get_ticket_info(no):

    context = GetContext()

    key = concat(TICKET,no)

    ticket = Get(context, key)

    if not ticket:

        return notifyErrorAndReturnFalse('Can not find the ticket')

    else: return ticket


def get_drawing_result(game_no):

    context = GetContext()

    result_key = concat(RESULT,game_no)

    last_drawing_result = Get(context,result_key)

    if not last_drawing_result:

        return notifyErrorAndReturnFalse("No drawing result")

    else:

        return last_drawing_result


def get_last_drawing_result():

    context = GetContext()

    current_game_no = get_current_game_no()

    result_key = concat(RESULT,current_game_no - 1)

    last_drawing_result = Get(context,result_key)

    if not last_drawing_result:

        return notifyErrorAndReturnFalse("No drawing result")

    else:

        return last_drawing_result


def get_last_ticket_no():

    context = GetContext()

    no = Get(context,LAST_TICKET_NO)

    if not no:

        return notifyErrorAndReturnZero("Can not find the last ticket")

    else:

        return no


def get_last_verified_ticket_no():

    context = GetContext()

    no = Get(context,LAST_VERIFIED_TICKET_NO)

    if not no:

        return notifyErrorAndReturnZero("No result")

    else:

        return no


def timeLeft():

    context = GetContext()

    last_drawing_at = Get(context, LAST_DRAWING_AT)

    now = GetTime()

    time_left = now - (last_drawing_at + DRAWING_SCHEDULE)

    return time_left


# -- NEP5 calls

def doTransfer(t_from, t_to, amount):
    """
    Method to transfer NEP5 tokens of a specified amount from one account to another

    :param t_from: the address to transfer from
    :type t_from: bytearray
    :param t_to: the address to transfer to
    :type t_to: bytearray
    :param amount: the amount of NEP5 tokens to transfer
    :type amount: int

    :return: whether the transfer was successful
    :rtype: bool

    """

    if amount <= 0:
        Log("Cannot transfer negative amount")
        return False

    from_is_sender = CheckWitness(t_from)

    if not from_is_sender:
        Log("Not owner of funds to be transferred")
        return False

    if t_from == t_to:
        Log("Sending funds to self")
        return True

    context = GetContext()

    from_val = Get(context, t_from)

    if from_val < amount:
        Log("Insufficient funds to transfer")
        return False

    if from_val == amount:
        Delete(context, t_from)

    else:
        difference = from_val - amount
        Put(context, t_from, difference)

    to_value = Get(context, t_to)

    to_total = to_value + amount

    Put(context, t_to, to_total)

    DispatchTransferEvent(t_from, t_to, amount)

    return True


def doTransferFrom(t_from, t_to, amount):
    """
    Method to transfer NEP5 tokens of a specified amount from one account to another

    :param t_from: the address to transfer from
    :type t_from: bytearray
    :param t_to: the address to transfer to
    :type t_to: bytearray
    :param amount: the amount of NEP5 tokens to transfer
    :type amount: int

    :return: whether the transfer was successful
    :rtype: bool

    """
    if amount <= 0:
        return False

    context = GetContext()

    allowance_key = concat(t_from, t_to)

    available_to_to_addr = Get(context, allowance_key)

    if available_to_to_addr < amount:
        Log("Insufficient funds approved")
        return False

    from_balance = Get(context, t_from)

    if from_balance < amount:
        Log("Insufficient tokens in from balance")
        return False

    to_balance = Get(context, t_to)

    # calculate the new balances
    new_from_balance = from_balance - amount
    new_to_balance = to_balance + amount
    new_allowance = available_to_to_addr - amount

    # persist the new balances
    Put(context, allowance_key, new_allowance)
    Put(context, t_to, new_to_balance)
    Put(context, t_from, new_from_balance)

    Log("transfer complete")

    # dispatch transfer event
    DispatchTransferEvent(t_from, t_to, amount)

    return True


def doApprove(t_owner, t_spender, amount):
    """

    Method by which the owner of an address can approve another address
    ( the spender ) to spend an amount

    :param t_owner: Owner of tokens
    :type t_owner: bytearray
    :param t_spender: Requestor of tokens
    :type t_spender: bytearray
    :param amount: Amount requested to be spent by Requestor on behalf of owner
    :type amount: bytearray

    :return: success of the operation
    :rtype: bool

    """

    owner_is_sender = CheckWitness(t_owner)

    if not owner_is_sender:
        Log("Incorrect permission")
        return False

    context = GetContext()

    from_balance = Get(context, t_owner)

    # cannot approve an amount that is
    # currently greater than the from balance
    if from_balance >= amount:
        approval_key = concat(t_owner, t_spender)

        current_approved_balance = Get(context, approval_key)

        new_approved_balance = current_approved_balance + amount

        Put(context, approval_key, new_approved_balance)

        Log("Approved")

        DispatchApproveEvent(t_owner, t_spender, amount)

        return True

    return False


def getAllowance(t_owner, t_spender):
    """
    Gets the amount of tokens that a spender is allowed to spend
    from the owners' account.

    :param t_owner: Owner of tokens
    :type t_owner: bytearray
    :param t_spender: Requestor of tokens
    :type t_spender: bytearray

    :return: Amount allowed to be spent by Requestor on behalf of owner
    :rtype: int

    """

    context = GetContext()

    allowance_key = concat(t_owner, t_spender)

    amount = Get(context, allowance_key)

    return amount


def balanceOf(account):
    """
    Method to return the current balance of an address

    :param account: the account address to retrieve the balance for
    :type account: bytearray

    :return: the current balance of an address
    :rtype: int

    """

    context = GetContext()

    balance = Get(context, account)

    return balance


# -- Global calls

def deserialize_bytearray(data):
    # get length of length
    collection_length_length = data[0:1]

    # get length of collection
    collection_len = data[1:collection_length_length + 1]

    # create a new collection
    new_collection = list(length=collection_len)

    # trim the length data
    offset = 1 + collection_length_length

    for i in range(0, collection_len):
        # get the data length length
        itemlen_len = data[offset:offset + 1]

        # get the length of the data
        item_len = data[offset + 1:offset + 1 + itemlen_len]

        # get the data
        item = data[offset + 1 + itemlen_len: offset + 1 + itemlen_len + item_len]

        # store it in collection
        new_collection[i] = item

        offset = offset + item_len + itemlen_len + 1

    return new_collection


def serialize_array(items):
    # serialize the length of the list
    itemlength = serialize_var_length_item(items)

    output = itemlength

    # now go through and append all your stuff
    for item in items:
        # get the variable length of the item
        # to be serialized
        itemlen = serialize_var_length_item(item)

        # add that indicator
        output = concat(output, itemlen)

        # now add the item
        output = concat(output, item)

    # return the stuff
    return output


def serialize_var_length_item(item):
    # get the length of your stuff
    stuff_len = len(item)

    # now we need to know how many bytes the length of the array
    # will take to store

    # this is one byte
    if stuff_len <= 255:
        byte_len = b'\x01'
    # two byte
    elif stuff_len <= 65535:
        byte_len = b'\x02'
    # hopefully 4 byte
    else:
        byte_len = b'\x04'

    out = concat(byte_len, stuff_len)

    return out


def notifyErrorAndReturnFalse(msg):
    Notify(msg)

    return False


def notifyErrorAndReturnZero(msg):
    Notify(msg)

    return 0


def getLucky():
    """
    Method to generate random numbers using the latest block nounce
    :return: random numbers array

    """

    # Lottery numbers
    numbers = [
        1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49
    ]

    # Ready empty list
    winning_numbers = list(0)

    # Get random nonce number in the latest block
    currentHeight = GetHeight()
    currentHeader = GetHeader(currentHeight)
    randomNumber = GetConsensusData(currentHeader)

    for i in range(1, 6):

        percentage = (randomNumber * i) % (49 - i)

        winning_numbers.append(numbers[percentage])

        numbers.remove(percentage)

    bonusIndex = ((randomNumber * 6) % 9) + 1

    winning_numbers.append(bonusIndex)

    return winning_numbers


def sort(list):
    for index in range(1, len(list)):
        value = list[index]
        i = index - 1
        while i >= 0:
            if value < list[i]:
                list[i + 1] = list[i]
                list[i] = value
                i -= 1
            else:
                break

    return list


# --- initial smart contact

def deploy():
    """
    Initialize token and game.
    """

    context = GetContext()

    if not CheckWitness(OWNER): return notifyErrorAndReturnFalse("Must be owner to deploy")

    if not Get(context, 'initialized'):

        Put(context, 'initialized', 1)

        Put(context, OWNER, TOTAL_SUPPLY - INITIAL_POOL)

        Put(context, POOL, INITIAL_POOL)

        current_time = GetTime()

        # TODO::remove minus for the production!!
        Put(context, LAST_DRAWING_AT, current_time - DRAWING_SCHEDULE)

        Log("Token minted!")

        return True

    else:
        notifyErrorAndReturnFalse("Already deployed!")
