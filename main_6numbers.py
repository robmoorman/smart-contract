from boa.interop.Neo.Action import RegisterAction
from boa.interop.Neo.Header import GetConsensusData
from boa.interop.Neo.Blockchain import GetHeight, GetHeader, GetTransaction
from boa.interop.Neo.TriggerType import Verification, Application
from boa.interop.Neo.Runtime import Log, Notify, CheckWitness, GetTrigger, GetTime
from boa.builtins import concat, list, range, has_key, substr, sha1, hash160, take
from boa.interop.Neo.Storage import Get, Put, GetContext, Delete, Find
from boa.interop.System.ExecutionEngine import GetScriptContainer, GetCallingScriptHash, GetEntryScriptHash, GetExecutingScriptHash
from boa.interop.Neo.Iterator import IterNext, IterKey, IterValue, IterValues

# Check list
# -- Is Drawing schedule correct?
# -- Is Winning number correct?
# -- Is Owner and pool address correct?
# -- Is Testnet only methods are deleted?

# -- Lottery variables
PLAYER = 'player'
OPERATOR = 'operator'
VERIFIER = 'verifier'
TICKET = 'ticket'
RESULT = 'result'
FLAG = 'flag'
CURRENT_GAME_NO = 'current_game_no'
LAST_TICKET_NO = "last_ticket_no"
LAST_VERIFIED_TICKET_NO = "last_verified_ticket_no"
LAST_DRAWING_AT = 'last_drawing_at'
LAST_DRAWING_TICKET = 'last_drawing_ticket'
LAUNCHED_AT = "launched_at"
DRAWING_SCHEDULE = 1
# DRAWING_SCHEDULE = 86400
TICKET_PRICE = 1 * 100000000  # 1 FTW
DRAWING_COMMISSION = 5000000  # 5% of TICKET_PRICE
JACKPOT_PERCENTAGE = 60
INITIAL_POOL = 5000000 * 100000000  # 5m FTW


# -- NEP5 variables
TOKEN_NAME = 'FTW Token'
SYMBOL = 'FTW'
DECIMALS = 8
TOTAL_SUPPLY = 100000000 * 100000000  # 100m total supply * 10^8 (decimals)

# # -- MainNet
# OWNER = b'\xdc\xf3\xca\xef\xf9\xbb;\xf1\xf0?\xbb\x18\x81\x9cj\xba\x98r\xdc\xe4'  # AbvAMiWRib6GzGZKU1o8QxUntnzhCwjXdS
# POOL = b'<R\xe3\x1d\x07\nX\x174\x97\x17\xa6V*\x0c\xa2>\xa6\xe2\xeb'  # AMGqV7HJFrvxnXxVCzUjEcw4Gv3mdGReiF

# -- PrivateNet
OWNER = b'#\xba\'\x03\xc52c\xe8\xd6\xe5"\xdc2 39\xdc\xd8\xee\xe9'  # AK2nJJpJr6o664CWJKi1QRXjqeic2zRp8y
POOL = b'#\xc54\xb1\xa0\x94\x98\x84{8\xce5\x11mR\xc4a\x964\xf7'   # AK31YKAiDjS6wtTq8jtgLdmWPcCuzCSBNb

# # -- TestNet
# OWNER = b'\x99\xd6H\x1aQh\x8c\xd1j\x0bX\x02=\x17\xd4\xdd\x9b\rS6'
# # -- AK31YKAiDjS6wtTq8jtgLdmWPcCuzCSBNb
# POOL = b'#\xc54\xb1\xa0\x94\x98\x84{8\xce5\x11mR\xc4a\x964\xf7'


# -------------------------------------------
# Events NEP5
# -------------------------------------------

DispatchTransferEvent = RegisterAction('transfer', 'from', 'to', 'amount')

# -------------------------------------------
# Events FTW
# -------------------------------------------

# DispatchBuyEvent = RegisterAction('buy', 'from', 'no_1', 'no_2', 'no_3', 'no_4', 'no_5')
# DispatchDrawEvent = RegisterAction('draw', 'from')
# DispatchVerifyEvent = RegisterAction('verify', 'from')

def Main(operation, args):
    trigger = GetTrigger()

    if trigger == Verification():

        is_owner = CheckWitness(OWNER)

        if is_owner:
            return True

        return False

    elif trigger == Application():

        # -- NEP5 Standard
        if operation == 'name':

            return TOKEN_NAME

        elif operation == 'decimals':

            return DECIMALS

        elif operation == 'symbol':

            return SYMBOL

        elif operation == 'totalSupply':

            return TOTAL_SUPPLY

        elif operation == 'deploy':

            return deploy()

        elif operation == 'balanceOf':

            if len(args) == 1:

                account = args[0]

                ctx = GetContext()

                return balanceOf(ctx, account)

            return notifyErrorAndReturnZero("Argument count must be 1 and they must not be null")

        elif operation == 'transfer':

            if len(args) == 3:

                t_from = args[0]
                t_to = args[1]
                amount = args[2]

                if t_to == POOL:

                    if amount == 100000000:
                        Log("Autopick entry")
                        return autopick(t_from)

                return do_transfer(t_from, t_to, amount)

            else:

                return notifyErrorAndReturnFalse("Argument count must be 3 and they must not be null")

        # -- FTW

        elif operation == 'buy':

            player = args[0]

            if len(args) == 7:

                numbers = list(0)

                for i in range(1, 7):

                    if args[i] < 50:
                        numbers.append(args[i])

                if len(numbers) != 6:

                    return notifyErrorAndReturnFalse('Invalid lottery numbers')

                return buy(player,numbers)

            return False

        elif operation == 'draw':

            if len(args) == 1:

                return draw(args[0])

            else:

                return notifyErrorAndReturnFalse("Argument count must be 1 and must be address")

        elif operation == 'verify':

            if len(args) == 1:

                return verify(args[0])

            else:

                return notifyErrorAndReturnFalse("Argument count must be 1 and must be address")

        elif operation == 'get_pool':

            return get_pool()

        elif operation == 'get_current_game_no':

            return get_current_game_no()

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

        elif operation == 'get_last_ticket_no':

            return get_last_ticket_no()

        elif operation == 'get_last_verified_ticket_no':

            return get_last_verified_ticket_no()

        elif operation == 'get_last_drawing_ticket_no':

            return get_last_drawing_ticket_no()


        elif operation == 'get_all_tickets':

            return get_all_tickets()

        elif operation == 'get_all_drawing_results':

            return get_all_drawing_results()

        elif operation == 'get_all_operators':

            return get_all_operators()

        elif operation == 'get_all_verifiers':

            return get_all_verifiers()

        elif operation == 'get_all_tickets_by_player':

            if len(args) == 1:
                player = args[0]

                return get_all_tickets_by_player(player)

            return notifyErrorAndReturnZero("Argument count must be 1 and they must not be null")


        elif operation == 'get_all_operators_by_player':

            if len(args) == 1:
                account = args[0]

                return get_all_operators_by_player(account)

            return notifyErrorAndReturnZero("Argument count must be 1 and they must not be null")


        elif operation == 'get_all_verifiers_by_player':

            if len(args) == 1:

                account = args[0]

                return get_all_verifiers_by_player(account)

            return notifyErrorAndReturnZero("Argument count must be 1 and they must not be null")


        elif operation == 'has_user_participated':

            if len(args) == 1:

                account = args[0]

                return has_user_participated(account)

            return notifyErrorAndReturnFalse("Argument count must be 1 and they must not be null")


        elif operation == 'is_verifying_open':

            return is_verifying_open()


        elif operation == 'get_time_left':

            return get_time_left()

        # -- Testnet only TODO::remove for mainnet

        elif operation == 'bounty':

            if len(args) == 1:

                address = args[0]

                return bounty(address)

            return notifyErrorAndReturnZero("Argument count must be 1 and they must not be null")

        else:

            return notifyErrorAndReturnFalse('unknown operation')


def buy(player, numbers):

    is_transferred = do_transfer(player, POOL, TICKET_PRICE)

    if is_transferred:

        context = GetContext()

        current_game_no = get_current_game_no()

        last_ticket_no = get_last_ticket_no()

        new_ticket_no = last_ticket_no + 1

        new_ticket_key = concat(TICKET, new_ticket_no)

        # -- Store TICKET with a new ticket index in order to save details.
        new_ticket = [
            current_game_no,
            player,
            serialize_array(numbers),
            GetTime()
        ]

        Put(context, new_ticket_key, serialize_array(new_ticket))

        # -- Store LAST_TICKET_NO with a new ticket index in order to keep tracks of ticket index.
        Put(context, LAST_TICKET_NO, new_ticket_no)

        # -- Store PLAYER with a new ticket in order to fetch tickets by player address for users.
        player_key = concat(PLAYER, player)

        player_key = concat(player_key, current_game_no)

        if not has_user_participated(player):

            player_key = concat(player_key, "first")

        else:

            player_key = concat(player_key, new_ticket_no)

        Put(context, player_key, new_ticket_no)

        return True

    return False


def autopick(player):

    # Lottery numbers
    samples = [
        1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49
    ]

    # Ready empty list
    numbers = list(0)
    randomNumber = GetTime()

    for i in range(1, 6):

        percentage = (randomNumber * i) % (49 - i)

        numbers.append(samples[percentage])

        samples.remove(percentage)

    bonusIndex = ((randomNumber * 6) % 9) + 1

    numbers.append(bonusIndex)

    return buy(player,numbers)


def draw(miner):

    is_operator = CheckWitness(miner)

    if not is_operator:

        return notifyErrorAndReturnFalse("Authentication failed")

    context = GetContext()

    miner_balance = balanceOf(context, miner)

    prize_pool = get_pool()

    time_left = get_time_left()

    if (time_left > 0):

        last_sold_ticket = get_last_ticket_no()

        last_drawn_ticket = get_last_drawing_ticket_no()

        total_entries = last_sold_ticket - last_drawn_ticket

        if total_entries <= 0:

            return notifyErrorAndReturnFalse("No entries in the current game")

        commission = total_entries * DRAWING_COMMISSION

        # -- Get last drawing result

        current_game_no = get_current_game_no()

        flag_key = concat(PLAYER, miner)

        flag_key = concat(flag_key, current_game_no)

        flag_key = concat(flag_key, "first")

        flag = Get(context, flag_key)

        if not flag:

            return notifyErrorAndReturnFalse("You did not participate the current game")

        # -- Get winning numbers and Store
        winning_numbers = getLucky()

        result_key = concat(RESULT, current_game_no)
        Put(context, result_key, serialize_array(winning_numbers))

        # -- Miner info
        operator_key = concat(OPERATOR, miner)
        operator_key = concat(operator_key, current_game_no)
        Put(context, operator_key, total_entries)

        # -- Update LAST_DRAWING_AT with timestamp in order to schedule for the next drawing.
        Put(context, LAST_DRAWING_AT, GetTime())

        # -- Update LAST_DRAWING_TICKET with the last ticket number of the current game to help verification.
        Put(context, LAST_DRAWING_TICKET, last_sold_ticket)

        # -- Update CURRENT_GAME_NO with a new game no which is the next game no.
        Put(context, CURRENT_GAME_NO, current_game_no + 1)

        # -- Update miner balance with commission.
        Put(context, miner, miner_balance + commission)

        # -- Update current pool size.
        Put(context, POOL, prize_pool - commission)

        DispatchTransferEvent(POOL, miner, commission)

        return True

    else:

        return notifyErrorAndReturnFalse("Please wait until the next drawing schedule")


def verify(miner):

    is_operator = CheckWitness(miner)

    if not is_operator:

        return notifyErrorAndReturnFalse("Authentication failed")

    context = GetContext()

    miner_balance = balanceOf(context, miner)

    prize_pool = get_pool()

    last_verified_ticket_no = get_last_verified_ticket_no()

    ticket_to_verify = last_verified_ticket_no + 1

    last_drawing_ticket = get_last_drawing_ticket_no()

    # Check if verifying stays in the past range.
    if ticket_to_verify > last_drawing_ticket:
        return notifyErrorAndReturnFalse("There are no more tickets to verify")

    # -- Get deserialized ticket details.

    ticket = get_ticket_info(ticket_to_verify)

    target = deserialize_bytearray(ticket)

    game_no = target[0]

    player = target[1]

    numbers = deserialize_bytearray(target[2])

    # -- Get the drawing result by the game number of the ticket and match numbers.
    drawing_result = get_drawing_result(game_no)

    winning_numbers = deserialize_bytearray(drawing_result)

    rank = match_rank(numbers, winning_numbers)

    # -- Update LAST_VERIFIED_TICKET_NO with the current ticket no being verified.

    Put(context, LAST_VERIFIED_TICKET_NO, ticket_to_verify)

    # -- Update verifier
    verifier_key = concat(VERIFIER, miner)

    verifier_key = concat(verifier_key, ticket_to_verify)

    Put(context, verifier_key, GetTime())

    if rank is not 0:

        PRIZES = [
            0,
            (prize_pool * JACKPOT_PERCENTAGE) / 100,
            5000000000000,
            500000000000,
            25000000000,
            2500000000,
            1000000000,
            500000000,
            300000000,
            100000000
        ]

        prize = PRIZES[rank]

        total_amount = prize + DRAWING_COMMISSION

        if prize_pool >= total_amount:

            player_balance = Get(context, player)

            if player == miner:

                # -- Update player balance
                Put(context, player, player_balance + total_amount)

                # -- Update pool balance
                pool_balance = prize_pool - total_amount

                Put(context, POOL, pool_balance)

                DispatchTransferEvent(POOL,player,total_amount)

            else:

                # -- Update player balance
                Put(context, player, player_balance + prize)

                # -- Update miner balance
                Put(context, miner, miner_balance + DRAWING_COMMISSION)

                # -- Update pool balance
                Put(context, POOL, prize_pool - total_amount)

                DispatchTransferEvent(POOL, player, player_balance + prize)

                DispatchTransferEvent(POOL, miner, DRAWING_COMMISSION)

            return True

        else:

            return notifyErrorAndReturnFalse("Pool can not afford to pay the prize")

    else:

        # -- Update miner balance
        Put(context, miner, miner_balance + DRAWING_COMMISSION)

        # -- Update pool balance
        Put(context, POOL, prize_pool - DRAWING_COMMISSION)

        return True

# def verify1(miner):
#
#     is_operator = CheckWitness(miner)
#
#     if not is_operator:
#
#         return notifyErrorAndReturnFalse("Authentication failed")
#
#     # -- Get current balance of miner.
#     miner_balance = balanceOf(miner)
#
#     # -- Get last ticket number in the last drawing
#     last_drawn_ticket = get_last_drawing_ticket_no()
#
#     prize_pool = get_pool()
#
#     last_verified_ticket_no = get_last_verified_ticket_no()
#
#     ticket_to_verify = last_verified_ticket_no + 1
#
#     # Check if verifying stays in the past range.
#     if ticket_to_verify > last_drawn_ticket:
#
#         return notifyErrorAndReturnFalse("There is no more tickets to verify")
#
#     context = GetContext()
#
#     # -- Get deserialized ticket details.
#     target_key = concat(TICKET, ticket_to_verify)
#
#     target_key = Get(context, target_key)
#
#     target = deserialize_bytearray(target_key)
#
#     game_no = target[0]
#
#     player = target[1]
#
#     numbers = deserialize_bytearray(target[2])
#
#     # -- Get the drawing result by the game number of the ticket and match numbers.
#     drawing_result = get_drawing_result(game_no)
#
#     winning_numbers = deserialize_bytearray(drawing_result)
#
#     rank = match_rank(numbers, winning_numbers)
#
#     # -- Update LAST_VERIFIED_TICKET_NO with the current ticket no being verified.
#     Put(context, LAST_VERIFIED_TICKET_NO, ticket_to_verify)
#
#     # -- Update verifier
#     verifier_key = concat(VERIFIER, miner)
#
#     verifier_key = concat(verifier_key,ticket_to_verify)
#
#     Put(context, verifier_key, GetTime())
#
#     if rank is not 0:
#
#         PRIZES = [
#             0,
#             1000000 * 100000000,
#             50000 * 100000000,
#             5000 * 100000000,
#             250 * 100000000,
#             25 * 100000000,
#             10 * 100000000,
#             5 * 100000000,
#             3 * 100000000,
#             1 * 100000000
#         ]
#
#         prize = PRIZES[rank]
#
#         total_amount = prize + DRAWING_COMMISSION
#
#         if prize_pool >= total_amount:
#
#             player_balance = Get(context, player)
#
#             if player == miner:
#
#                 # -- Update player balance
#                 Put(context, player, player_balance + total_amount)
#
#                 # -- Update pool balance
#                 pool_balance = prize_pool - total_amount
#
#                 Put(context, POOL, pool_balance)
#
#                 DispatchTransferEvent(POOL,player,total_amount)
#
#             else:
#
#                 # -- Update player balance
#                 Put(context, player, player_balance + prize)
#
#                 # -- Update miner balance
#                 Put(context, miner, miner_balance + DRAWING_COMMISSION)
#
#                 # -- Update pool balance
#                 Put(context, POOL, prize_pool - total_amount)
#
#                 DispatchTransferEvent(POOL, player, player_balance + prize)
#
#                 DispatchTransferEvent(POOL, miner, DRAWING_COMMISSION)
#
#             return True
#
#         else:
#
#             return notifyErrorAndReturnFalse("Pool can not afford to pay the prize")
#
#     else:
#
#         # -- Update miner balance
#         Put(context, miner, miner_balance + DRAWING_COMMISSION)
#
#         # -- Update pool balance
#         Put(context, POOL, prize_pool - DRAWING_COMMISSION)
#
#         return True


def match_rank(six_numbers, winning_numbers):

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

    ctx = GetContext()

    current_game_no = Get(ctx, CURRENT_GAME_NO)

    if not current_game_no:

        return 1

    else:

        return current_game_no


def get_last_ticket_no():

    ctx = GetContext()

    no = Get(ctx, LAST_TICKET_NO)

    if not no:

        return notifyErrorAndReturnZero("Can not find the last ticket")

    else:

        return no


def get_ticket_info(ticket_no):

    context = GetContext()

    key = concat(TICKET, ticket_no)

    ticket = Get(context, key)

    if not ticket:

        return notifyErrorAndReturnFalse('Can not find the ticket')

    else:

        return ticket


def get_drawing_result(game_no):

    context = GetContext()

    key = concat(RESULT, game_no)

    result = Get(context, key)

    if not result:

        return notifyErrorAndReturnFalse("No drawing result")

    else:

        return result


def get_last_drawing_ticket_no():

    context = GetContext()

    no = Get(context, LAST_DRAWING_TICKET)

    if not no:

        return notifyErrorAndReturnZero("Can not find the last drawing ticket no")

    else:

        return no


def get_last_verified_ticket_no():

    context = GetContext()

    no = Get(context,LAST_VERIFIED_TICKET_NO)

    if not no:

        return notifyErrorAndReturnZero("No verified tickets yet")

    else:

        return no


def get_all_tickets():

    context = GetContext()

    result_iter = Find(context, TICKET)

    pre = len(TICKET)

    tickets = []

    while result_iter.IterNext():

        key = result_iter.IterKey()

        val = result_iter.IterValue()

        key_length = len(key)

        ticket = deserialize_bytearray(val)

        ticket_no = substr(key, pre, key_length)

        ticket.append(ticket_no)

        rank = get_rank(ticket_no)

        ticket.append(rank)

        tickets.append(serialize_array(ticket))

    return serialize_array(tickets)


def get_all_drawing_results():

    context = GetContext()

    result_iter = Find(context, RESULT)

    results = []

    while result_iter.IterNext():

        drawing = []

        key = result_iter.IterKey()

        winning_numbers = result_iter.IterValue()

        pre = len(RESULT)

        key_length = len(key)

        drawing_no = substr(key, pre, key_length)

        drawing.append(drawing_no)

        drawing.append(winning_numbers)

        results.append(serialize_array(drawing))

    data = serialize_array(results)

    return data


def get_all_operators():

    context = GetContext()

    result_iter = Find(context, OPERATOR)

    pre = len(OPERATOR)

    operators = []

    while result_iter.IterNext():

        operator = []

        key = result_iter.IterKey()

        total_entries = result_iter.IterValue()

        account = substr(key, pre, pre + 19)

        game_no = substr(key, pre + 20, len(key))

        operator.append(game_no)

        operator.append(account)

        operator.append(total_entries)

        operators.append(serialize_array(operator))

    data = serialize_array(operators)

    return data


def get_all_verifiers():
    """
      :return: bytes
      [
          ticket_no,
          account,
          created_at
      ]
      """

    context = GetContext()

    result_iter = Find(context, VERIFIER)

    pre = len(VERIFIER)

    verifiers = []

    while result_iter.IterNext():

        verifier = []

        key = result_iter.IterKey()

        created_at = result_iter.IterValue()

        account = substr(key, pre, pre + 19)

        ticket_no = substr(key, pre + 20, len(key))

        verifier.append(ticket_no)

        verifier.append(account)

        verifier.append(created_at)

        verifiers.append(serialize_array(verifier))

    data = serialize_array(verifiers)

    return data


def get_all_tickets_by_player(player):

    context = GetContext()

    query = concat(PLAYER, player)

    result_iter = Find(context, query)

    tickets = []

    while result_iter.IterNext():

        key = result_iter.IterKey()

        ticket_no = result_iter.IterValue()

        Notify(key)

        ticket = get_ticket_info(ticket_no)

        ticket = deserialize_bytearray(ticket)

        ticket.append(ticket_no)

        rank = get_rank(ticket_no)

        ticket.append(rank)

        tickets.append(serialize_array(ticket))

    tickets = serialize_array(tickets)

    return tickets


def get_all_operators_by_player(account):

    context = GetContext()

    iter_key = concat(OPERATOR, account)

    pre = len(iter_key)

    result_iter = Find(context, iter_key)

    operators = []

    while result_iter.IterNext():

        operator = []

        key = result_iter.IterKey()

        total_entries = result_iter.IterValue()

        key_length = len(key)

        game_no = substr(key, pre, key_length)

        operator.append(game_no)

        operator.append(total_entries)

        operators.append(serialize_array(operator))

    data = serialize_array(operators)

    return data


def get_all_verifiers_by_player(account):

    context = GetContext()

    iter_key = concat(VERIFIER, account)

    pre = len(iter_key)

    result_iter = Find(context, iter_key)

    verifiers = []

    while result_iter.IterNext():

        verifier = []

        key = result_iter.IterKey()

        created_at = result_iter.IterValue()

        key_length = len(key)

        ticket_no = substr(key, pre, key_length)

        verifier.append(ticket_no)

        verifier.append(created_at)

        verifiers.append(serialize_array(verifier))

    data = serialize_array(verifiers)

    return data


def get_rank(ticket_no):

    ticket = get_ticket_info(ticket_no)

    if not ticket:

        return 0

    else:

        ticket = deserialize_bytearray(ticket)

        game_no = ticket[0]

        numbers = deserialize_bytearray(ticket[2])

        # -- Get the drawing result by the game number of the ticket and match numbers.
        drawing_result = get_drawing_result(game_no)

        if not drawing_result:

            return 0

        else:

            winning_numbers = deserialize_bytearray(drawing_result)

            rank = match_rank(numbers, winning_numbers)

            return rank


def get_time_left():

    context = GetContext()

    last_drawing_at = Get(context, LAST_DRAWING_AT)

    now = GetTime()

    time_left = now - (last_drawing_at + DRAWING_SCHEDULE)

    return time_left


def has_user_participated(account):

    if len(account) != 20:
        return notifyErrorAndReturnFalse("Account should be 20-byte addresses")

    context = GetContext()

    current_game_no = get_current_game_no()

    flag = concat(PLAYER, account)

    flag = concat(flag, current_game_no)

    flag = concat(flag, "first")

    check_user_participation = Get(context, flag)

    if check_user_participation:
        return True

    return False


def is_verifying_open():

    # -- Get target ticket number.
    last_verified_ticket_no = get_last_verified_ticket_no()

    ticket_to_verify = last_verified_ticket_no + 1

    # -- Get last drawing result
    last_drawn_ticket = get_last_drawing_ticket_no()

    if last_drawn_ticket:

        if ticket_to_verify <= last_drawn_ticket:
            return True

    return False


# -- NEP5 calls

def do_transfer(t_from, t_to, amount):

    context = GetContext()

    if amount < 0:
        # raise Exception('Amount MUST be greater than or equal to 0')
        notifyErrorAndReturnFalse("Amount MUST be greater than or equal to 0")

    if len(t_from) != 20:
        # raise Exception('From should be 20-byte addresses')
        notifyErrorAndReturnFalse("From should be 20-byte addresses")

    if len(t_to) != 20:
        notifyErrorAndReturnFalse("From should be 20-byte addresses")

    if CheckWitness(t_from):

        if t_from == POOL:
            # raise Exception("Nobody can withdraw from the pool")
            notifyErrorAndReturnFalse("Nobody can withdraw from the pool")

        if t_from == t_to:
            Log("Transfer to self")
            return True

        from_val = Get(context, t_from)

        if from_val < amount:
            return notifyErrorAndReturnFalse("insufficient funds")

        if from_val == amount:
            Put(context, t_from, 0)

        else:
            difference = from_val - amount
            Put(context, t_from, difference)

        to_value = Get(context, t_to)

        to_total = to_value + amount

        Put(context, t_to, to_total)

        DispatchTransferEvent(t_from, t_to, amount)

        return True

    else:

        Log("from address is not the tx sender")

    return False


def balanceOf(ctx, account):

    if len(account) != 20:
        # raise Exception('Account should be 20-byte addresses')
        return notifyErrorAndReturnFalse("Account should be 20-byte addresses")

    balance = Get(ctx, account)

    if balance:

        return balance

    else:

        return 0


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

    Log(msg)
    return False


def notifyErrorAndReturnZero(msg):

    Log(msg)
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

    winning_numbers = [1,2,3,4,5,1]

    return winning_numbers

# def sort(list):
#     for index in range(1, len(list)):
#         value = list[index]
#         i = index - 1
#         while i >= 0:
#             if value < list[i]:
#                 list[i + 1] = list[i]
#                 list[i] = value
#                 i -= 1
#             else:
#                 break
#
#     return list


# --- initial smart contact


def deploy():

    context = GetContext()

    if not CheckWitness(OWNER):

        return notifyErrorAndReturnFalse("Must be owner to deploy")

    if not Get(context, LAUNCHED_AT):

        current_time = GetTime()

        Put(context, LAUNCHED_AT, current_time)

        Put(context, LAST_DRAWING_AT, current_time)

        # result = [
        #     serialize_array([1,2,3,4,5,6]),
        #     1,
        #     0,
        #     0,
        #     GetTime(),
        # ]
        #
        # key = concat(RESULT, 0)
        #
        # Put(context, key, serialize_array(result))

        Put(context, OWNER, TOTAL_SUPPLY)

        DispatchTransferEvent(None, OWNER, TOTAL_SUPPLY)

        return do_transfer(OWNER, POOL, INITIAL_POOL)

    else:
        notifyErrorAndReturnFalse("Already deployed!")


# --- Testnet only

AIRDROP = 'airdrop'

def bounty(address):

    context = GetContext()

    key = concat(AIRDROP,address)

    user = Get(context,key)

    if not user:

        user_balance = balanceOf(context, address)
        owner_balance = balanceOf(context, OWNER)

        # 100 FTW
        Put(context, address, user_balance + 10000000000)
        Put(context, OWNER, owner_balance - 10000000000)
        Put(context, key, "participated")

        return True

    else:

        return notifyErrorAndReturnFalse("Already participated")


