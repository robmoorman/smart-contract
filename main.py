from boa.interop.Neo.Action import RegisterAction
from boa.interop.Neo.Header import GetConsensusData
from boa.interop.Neo.Blockchain import GetHeight, GetHeader
from boa.interop.Neo.TriggerType import Verification, Application
from boa.interop.Neo.Runtime import Log, CheckWitness, GetTrigger, GetTime
from boa.builtins import concat, list, range, has_key, substr
from boa.interop.Neo.Storage import Get, Put, GetContext, Delete, Find
from boa.interop.System.ExecutionEngine import GetScriptContainer, GetCallingScriptHash, GetEntryScriptHash, GetExecutingScriptHash
from boa.interop.Neo.Iterator import IterNext, IterKey, IterValue, IterValues

# -- Lottery variables
PLAYER = 'player'
OPERATOR = 'operator'
VERIFIER = 'verifier'
TICKET = 'ticket'
WINNING_NUMBERS = 'winning_numbers'
FLAG = 'flag'
CURRENT_GAME_NO = 'current_game_no'
LAST_TICKET_NO = "last_ticket_no"
LAST_VERIFIED_TICKET_NO = "last_verified_ticket_no"
LAST_DRAWING_AT = 'last_drawing_at'
LAST_DRAWING_TICKET = 'last_drawing_ticket_no'
DEPLOYED_AT = "deployed_at"
LAUNCHED_AT = "launched_at"
DRAWING_SCHEDULE = 43200
TICKET_PRICE = 100000000  # 1FTW
DRAWING_COMMISSION = 5000000  # 5% of TICKET_PRICE
INITIAL_POOL = 5000000 * 100000000  # 5m FTW

# -- NEP5 variables
TOKEN_NAME = 'For The Win'
SYMBOL = 'FTW'
DECIMALS = 8
TOTAL_SUPPLY = 100000000 * 100000000  # 100m total supply * 10^8 (decimals)

OWNER = b'\xdc\xf3\xca\xef\xf9\xbb;\xf1\xf0?\xbb\x18\x81\x9cj\xba\x98r\xdc\xe4'
POOL = b'<R\xe3\x1d\x07\nX\x174\x97\x17\xa6V*\x0c\xa2>\xa6\xe2\xeb'

# -------------------------------------------
# Events NEP5
# -------------------------------------------

DispatchTransferEvent = RegisterAction('transfer', 'from', 'to', 'amount')

# -------------------------------------------
# Events FTW
# -------------------------------------------

DispatchBuyEvent = RegisterAction('buy', 'from', 'ticket_no', 'no_1', 'no_2', 'no_3', 'no_4', 'no_5')
DispatchDrawEvent = RegisterAction('draw', 'from', 'game_no')
DispatchVerifyEvent = RegisterAction('verify', 'from', 'ticket_no')

def Main(operation, args):

    trigger = GetTrigger()

    if trigger == Verification():

        is_owner = CheckWitness(OWNER)

        if is_owner:

            return True

        return False

    elif trigger == Application():

        # -- NEP5 standard methods

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

                    if amount == 200000000:

                        Log("Drawing entry")

                        return draw(t_from)

                    if amount == 300000000:

                        Log("Verifying entry")

                        return verify(t_from)

                return do_transfer(t_from, t_to, amount)

            else:

                return notifyErrorAndReturnFalse("Argument count must be 3 and they must not be null")

        # -- Lottery methods

        elif operation == 'launch':

            return launch()

        elif operation == 'buy':

            player = args[0]

            if len(args) == 6:

                numbers = list(0)

                # -- A trick to verify lottery numbers. 5 numbers in 1 to 39.

                five_number_dict = {}

                for i in range(1, 6):

                    if has_key(five_number_dict, args[i]):

                        return notifyErrorAndReturnFalse('Invalid lottery numbers')

                    five_number_dict[args[i]] = "1"

                    if args[i] == 0:

                        return notifyErrorAndReturnFalse('Invalid lottery numbers')

                    if args[i] > 39:

                        return notifyErrorAndReturnFalse('Invalid lottery numbers')

                    numbers.append(args[i])

                if len(numbers) != 5:

                    return notifyErrorAndReturnFalse('Invalid lottery numbers')

                return buy(player, numbers)

            return False

        elif operation == 'draw':

            if len(args) == 1:

                account = args[0]

                return draw(account)

            else:

                return notifyErrorAndReturnFalse("Argument count must be 1 and must be address")

        elif operation == 'verify':

            if len(args) == 1:

                account = args[0]

                return verify(account)

            else:

                return notifyErrorAndReturnFalse("Argument count must be 1 and must be address")

        elif operation == 'get_pool':

            return get_pool()

        elif operation == 'get_current_game_no':

            return get_current_game_no()

        elif operation == 'get_ticket_info':

            if len(args) == 1:

                ticket_no = args[0]

                return get_ticket_info(ticket_no)

            else:

                return notifyErrorAndReturnFalse("Argument count must be 1 and must be address")

        elif operation == 'get_last_ticket_no':

            return get_last_ticket_no()

        elif operation == 'get_last_verified_ticket_no':

            return get_last_verified_ticket_no()

        elif operation == 'get_last_drawing_ticket_no':

            return get_last_drawing_ticket_no()

        elif operation == 'get_last_drawing_at':

            return get_last_drawing_at()

        elif operation == 'has_user_participated':

            if len(args) == 1:

                account = args[0]

                return has_user_participated(account)

            return notifyErrorAndReturnFalse("Argument count must be 1 and they must not be null")

        elif operation == 'is_verifying_open':

            return is_verifying_open()

        elif operation == 'is_drawing_open':

            if len(args) == 1:

                account = args[0]

                return is_drawing_open(account)

            return notifyErrorAndReturnFalse("Argument count must be 1 and they must not be null")

        elif operation == 'get_time_left':

            return get_time_left()

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

        elif operation == 'get_all_tickets':

            return get_all_tickets()

        elif operation == 'get_all_drawings':

            return get_all_drawings()

        elif operation == 'get_all_verifying':

            return get_all_verifying()

        else:

            return notifyErrorAndReturnFalse('unknown operation')


# -------------------------------------------
# A custom method to participate the lottery.
# player: hash
# numbers: [int]
# -------------------------------------------

def buy(player, numbers):

    context = GetContext()

    current_game_no = Get(context, CURRENT_GAME_NO)

    # Check if the lottery is launched.
    # A method called launch() needs to be triggered by this contract owner in order to begin the lottery.

    if not current_game_no:

        return notifyErrorAndReturnFalse("The game has not been launched yet")

    # Ticket price will be transferred to the POOL

    is_transferred = do_transfer(player, POOL, TICKET_PRICE)

    if is_transferred:

        last_ticket_no = Get(context, LAST_TICKET_NO)

        new_ticket_no = last_ticket_no + 1

        new_ticket_key = concat(TICKET, new_ticket_no)

        new_ticket = [
            current_game_no,
            player,
            serialize_array(numbers),
            GetTime()
        ]

        Put(context, new_ticket_key, serialize_array(new_ticket))

        Put(context, LAST_TICKET_NO, new_ticket_no)

        player_key = concat(PLAYER, player)

        player_key = concat(player_key, current_game_no)

        # It needs flags to fetch all tickets by addresses and in order to check if a user is qualified for drawing.

        if not has_user_participated(player):

            player_key = concat(player_key, "first")

        else:

            player_key = concat(player_key, new_ticket_no)

        Put(context, player_key, new_ticket_no)

        DispatchBuyEvent(player, new_ticket_no, numbers[0], numbers[1], numbers[2], numbers[3], numbers[4])

        return True

    return False

# -------------------------------------------
# A custom method to participate draws.
# miner: hash
# -------------------------------------------

def draw(miner):

    if len(miner) != 20:

        return notifyErrorAndReturnFalse("From should be 20-byte addresses")

    is_operator = CheckWitness(miner)

    if not is_operator:

        return notifyErrorAndReturnFalse("Authentication failed")

    context = GetContext()

    miner_balance = balanceOf(context, miner)

    prize_pool = Get(context, POOL)

    current_game_no = Get(context, CURRENT_GAME_NO)

    # The initial LAST_DRAWING_AT is concatenated with 0.

    if current_game_no == 1:

        key = LAST_DRAWING_AT

    else:

        key = concat(LAST_DRAWING_AT, current_game_no - 1)

    last_drawing_at = Get(context, key)

    now = GetTime()

    time_left = now - (last_drawing_at + DRAWING_SCHEDULE)

    # It must pass 12 hours from last drawing.

    if (time_left > 0):

        last_sold_ticket = Get(context, LAST_TICKET_NO)

        last_drawn_ticket_key = concat(LAST_DRAWING_TICKET, current_game_no - 1)

        last_drawn_ticket = Get(context, last_drawn_ticket_key)

        total_entries = last_sold_ticket - last_drawn_ticket

        # The current game has to have a minimum of 1 ticket sales.

        if total_entries <= 0:

            return notifyErrorAndReturnFalse("No entries in the current game")

        # Commission to trigger this method.

        commission = total_entries * DRAWING_COMMISSION

        flag_key = concat(PLAYER, miner)
        flag_key = concat(flag_key, current_game_no)
        flag_key = concat(flag_key, "first")
        flag = Get(context, flag_key)

        # Check if the user who is triggering this method participated the current game.

        if not flag:

            return notifyErrorAndReturnFalse("You did not participate the current game")

        # Get winning numbers and Store

        winning_numbers = getLucky()
        result_key = concat(WINNING_NUMBERS, current_game_no)
        Put(context, result_key, winning_numbers)

        # Store the info of user who is triggering.

        current_time = GetTime()
        operator_key = concat(OPERATOR, miner)
        operator_key = concat(operator_key, current_game_no)
        Put(context, operator_key, current_time)

        # Update LAST_DRAWING_AT with timestamp in order to schedule for the next drawing.

        drawing_timestamp_key = concat(LAST_DRAWING_AT, current_game_no)
        Put(context, drawing_timestamp_key, current_time)

        # Update LAST_DRAWING_TICKET with the last ticket number of the current game to help verification.

        last_drawing_ticket_no_key = concat(LAST_DRAWING_TICKET, current_game_no)
        Put(context, last_drawing_ticket_no_key, last_sold_ticket)

        # Update CURRENT_GAME_NO with a new game no which is the next game no.

        Put(context, CURRENT_GAME_NO, current_game_no + 1)

        # Check if prize pool has enough amount to pay the commission

        if prize_pool >= commission:

            # -- Update miner balance with commission.
            Put(context, miner, miner_balance + commission)

            # -- Update current pool size.
            Put(context, POOL, prize_pool - commission)

            DispatchTransferEvent(POOL, miner, commission)

            DispatchDrawEvent(miner, current_game_no)

        return True

    else:

        return notifyErrorAndReturnFalse("Please wait until the next drawing schedule")

# -------------------------------------------
# A custom method to participate ticket verification.
# miner: hash
# -------------------------------------------

def verify(miner):

    if len(miner) != 20:

        return notifyErrorAndReturnFalse("From should be 20-byte addresses")

    is_operator = CheckWitness(miner)

    if not is_operator:

        return notifyErrorAndReturnFalse("Authentication failed")

    context = GetContext()

    miner_balance = balanceOf(context, miner)

    # A verifier has to have 1000 FTW or more to trigger this method.

    if miner_balance < 100000000000:

        return notifyErrorAndReturnFalse("Verifier must have more than 1000FTW")

    prize_pool = Get(context, POOL)

    last_verified_ticket_no = Get(context, LAST_VERIFIED_TICKET_NO)

    ticket_to_verify = last_verified_ticket_no + 1

    last_drawing_ticket = get_last_drawing_ticket_no()

    # Check if there are available tickets to verify

    if ticket_to_verify > last_drawing_ticket:

        return notifyErrorAndReturnFalse("There are no more tickets to verify")

    ticket_key = concat(TICKET, ticket_to_verify)

    ticket = Get(context, ticket_key)

    target = deserialize_bytearray(ticket)

    game_no = target[0]

    player = target[1]

    numbers = deserialize_bytearray(target[2])

    drawing_result_key = concat(WINNING_NUMBERS, game_no)

    drawing_result = Get(context, drawing_result_key)

    # Get winning numbers from the ticket which is being verified.

    winning_numbers = deserialize_bytearray(drawing_result)

    # Match if the ticket is a winning ticket.

    rank = match_rank(numbers, winning_numbers)

    if rank is not 0:

        prize = 0
        reward = 0

        if rank == 1:
            prize = 6000000000000
            reward = 300000000000

        if rank == 2:
            prize = 70000000000
            reward = 3500000000

        if rank == 3:
            prize = 3000000000
            reward = 150000000

        if rank == 4:
            prize = 300000000
            reward = 15000000

        total_amount = prize + reward

        # Check if the prize pool can afford to pay the winning prize.

        if prize_pool >= prize:

            player_balance = Get(context, player)

            # The prize pool can afford to pay the winning prize and reward.

            if prize_pool >= total_amount:

                # Check if verifiers is verifying his own ticket.

                if player == miner:

                    Put(context, player, player_balance + total_amount)

                    Put(context, POOL, prize_pool - total_amount)

                    DispatchTransferEvent(POOL, player, total_amount)

                else:

                    Put(context, player, player_balance + prize)

                    Put(context, miner, miner_balance + reward)

                    Put(context, POOL, prize_pool - total_amount)

                    DispatchTransferEvent(POOL, player, player_balance + prize)

                    DispatchTransferEvent(POOL, miner, reward)

            # The prize pool can on only pay the winning prize.

            else:

                Put(context, player, player_balance + prize)

                Put(context, POOL, prize_pool - prize)

                DispatchTransferEvent(POOL, player, player_balance + prize)

            DispatchVerifyEvent(miner, ticket_to_verify)

        else:

            return notifyErrorAndReturnFalse("Pool can not afford to pay the prize")

    # Verifying no winning ticket.

    else:

        if prize_pool >= DRAWING_COMMISSION:

            # Pay the verifier

            Put(context, miner, miner_balance + DRAWING_COMMISSION)

            Put(context, POOL, prize_pool - DRAWING_COMMISSION)

            DispatchTransferEvent(POOL, miner, DRAWING_COMMISSION)

            DispatchVerifyEvent(miner, ticket_to_verify)

    # Update verified ticket number to able to track for the next one.

    Put(context, LAST_VERIFIED_TICKET_NO, ticket_to_verify)

    # Store verifier information with current time to fetch all verifiers by address.

    verifier_key = concat(VERIFIER, miner)

    verifier_key = concat(verifier_key, ticket_to_verify)

    Put(context, verifier_key, GetTime())

    return True


# -------------------------------------------
# A custom method to generate random lottery numbers and participate the lottery.
# player: hash
# -------------------------------------------

def autopick(player):
    samples = [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
        31, 32, 33, 34, 35, 36, 37, 38, 39
    ]

    numbers = []

    # Use current time in blockchain to in order to generate the numbers.

    randomNumber = GetTime()

    for i in range(1, 6):
        percentage = (randomNumber * i) % (39 - i)

        numbers.append(samples[percentage])

        samples.remove(percentage)

    return buy(player, numbers)


def match_rank(numbers, winning_numbers):

    rank = 0

    number_matched = 0

    five_number_dict = {}

    for i in range(0, 5):

        five_number_dict[numbers[i]] = "1"

    for i in range(0, 5):

       if has_key(five_number_dict, winning_numbers[i]):

           number_matched += 1

    if number_matched == 5:

        rank = 1

    elif number_matched == 4:

        rank = 2

    elif number_matched == 3:

        rank = 3

    elif number_matched == 2:

        rank = 4

    return rank


def getLucky():

    numbers = [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10 , 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39
    ]

    winning_numbers = []

    currentHeight = GetHeight()
    currentHeader = GetHeader(currentHeight)
    randomNumber = GetConsensusData(currentHeader)
    randomNumber = randomNumber * GetTime()

    for i in range(1, 6):

        percentage = (randomNumber * i) % (39 - i)

        winning_numbers.append(numbers[percentage])

        numbers.remove(percentage)

    return serialize_array(winning_numbers)


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


def get_winning_numbers(game_no):

    context = GetContext()

    key = concat(WINNING_NUMBERS, game_no)

    result = Get(context, key)

    if not result:

        return notifyErrorAndReturnFalse("No drawing result")

    else:

        return result


def get_last_drawing_ticket_no():

    context = GetContext()

    current_game_no = get_current_game_no()

    key = concat(LAST_DRAWING_TICKET, current_game_no - 1)

    no = Get(context, key)

    if not no:

        return notifyErrorAndReturnZero("Can not find the last drawing ticket no")

    else:

        return no


def get_last_drawing_at():

    context = GetContext()

    current_game_no = get_current_game_no()

    key = concat(LAST_DRAWING_AT, current_game_no - 1)

    time = Get(context, key)

    return time


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


def get_all_drawings():

    context = GetContext()

    result_iter = Find(context, OPERATOR)

    pre = len(OPERATOR)

    operators = []

    while result_iter.IterNext():

        operator = []

        key = result_iter.IterKey()

        created_at = result_iter.IterValue()

        account = substr(key, pre, 20)

        game_no = substr(key, pre + 20, len(key) - (pre + 20))

        # --- Get total entries of the game
        previous_ticket = concat(LAST_DRAWING_TICKET, game_no - 1)

        previous_ticket = Get(context, previous_ticket)

        last_ticket = concat(LAST_DRAWING_TICKET, game_no)

        last_ticket = Get(context, last_ticket)

        total_entries = last_ticket - previous_ticket

        # -- Get winning numbers

        winning_numbers_key = concat(WINNING_NUMBERS, game_no)
        winning_numbers = Get(context,winning_numbers_key)

        operator.append(game_no)

        operator.append(winning_numbers)

        operator.append(account)

        operator.append(total_entries)

        operator.append(created_at)

        operators.append(serialize_array(operator))

    data = serialize_array(operators)

    return data


def get_all_verifying():

    context = GetContext()

    result_iter = Find(context, VERIFIER)

    pre = len(VERIFIER)

    verifiers = []

    while result_iter.IterNext():

        verifier = []

        key = result_iter.IterKey()

        created_at = result_iter.IterValue()

        account = substr(key, pre, 20)

        ticket_no = substr(key, pre + 20, len(key) - (pre + 20))

        rank = get_rank(ticket_no)

        verifier.append(ticket_no)

        verifier.append(account)

        verifier.append(rank)

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

        ticket_no = result_iter.IterValue()

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

        created_at = result_iter.IterValue()

        key_length = len(key)

        game_no = substr(key, pre, key_length)

        previous_ticket = concat(LAST_DRAWING_TICKET, game_no - 1)

        previous_ticket = Get(context, previous_ticket)

        last_ticket = concat(LAST_DRAWING_TICKET, game_no)

        last_ticket = Get(context, last_ticket)

        operator.append(game_no)

        operator.append(last_ticket - previous_ticket)

        operator.append(created_at)

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

        rank = get_rank(ticket_no)

        verifier.append(ticket_no)

        verifier.append(rank)

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
        drawing_result = get_winning_numbers(game_no)

        if not drawing_result:

            return 0

        else:

            winning_numbers = deserialize_bytearray(drawing_result)

            rank = match_rank(numbers, winning_numbers)

            return rank


def get_time_left():

    context = GetContext()

    current_game_no = get_current_game_no()

    if current_game_no == 1:
        key = LAST_DRAWING_AT
    else:
        key = concat(LAST_DRAWING_AT, current_game_no - 1)

    last_drawing_at = Get(context, key)

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


def is_drawing_open(account):


    check = has_user_participated(account)

    if not check:
        return notifyErrorAndReturnFalse("No entries in the current game")

    time_left = get_time_left()

    if (time_left < 0):

        return notifyErrorAndReturnFalse("It is not time")

    last_sold_ticket = get_last_ticket_no()

    last_drawn_ticket = get_last_drawing_ticket_no()

    total_entries = last_sold_ticket - last_drawn_ticket

    if total_entries <= 0:

        return notifyErrorAndReturnFalse("No entries in the current game")

    return True


# -- NEP5 calls

def do_transfer(t_from, t_to, amount):

    context = GetContext()

    if amount < 0:
        # raise Exception('Amount MUST be greater than or equal to 0')
        notifyErrorAndReturnFalse("Amount MUST be greater than or equal to 0")

    if len(t_from) != 20:
        return notifyErrorAndReturnFalse("From should be 20-byte addresses")

    if len(t_to) != 20:
        return notifyErrorAndReturnFalse("From should be 20-byte addresses")

    if CheckWitness(t_from):

        if t_from == POOL:
            return notifyErrorAndReturnFalse("Nobody can withdraw from the pool")

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



# --- Init smart contact

def deploy():

    context = GetContext()

    if not CheckWitness(OWNER):

        return notifyErrorAndReturnFalse("Must be owner to deploy")

    if not Get(context, DEPLOYED_AT):

        current_time = GetTime()

        Put(context, DEPLOYED_AT, current_time)

        Put(context, OWNER, TOTAL_SUPPLY)

        DispatchTransferEvent(None, OWNER, TOTAL_SUPPLY)

    else:
        return notifyErrorAndReturnFalse("Already deployed!")


def launch():

    context = GetContext()

    if not CheckWitness(OWNER):

        return notifyErrorAndReturnFalse("Must be owner to launch")

    if not Get(context, LAUNCHED_AT):

        current_time = GetTime()

        Put(context, LAUNCHED_AT, current_time)

        Put(context, CURRENT_GAME_NO, 1)

        key = concat(LAST_DRAWING_AT, 0)

        Put(context, key, current_time)

        return do_transfer(OWNER, POOL, INITIAL_POOL)

    else:
        return notifyErrorAndReturnFalse("Already launched!")

