#!/usr/bin/env python3

from sympy import *
from sympy.solvers import solve
init_printing(use_unicode=True)

# symbols for symbolic execution
# s: bet size
# b: probability that I bluffs with queen. NOTE: This is NOT the bluffing frequency
# c: O's call frequency
s, b, c = symbols('s b c')

# Ivan's ev
i = c / 3 + b*(2 - 3*c)/3

def ev_from_strategies(bet=b, call=c, pot=2, bet_size=1, print_table=True):
    """Compute the expected value (for Ivan) after antes are paid for a given
    strategy. To simplify the interface I don't make the user specify values
    that are clearly optimal. To do this I make the following assumptions:

    1. Ivan always bets with an ace; Opal always calls with an ace
    2. Ivan always checks with a King
    3. Opal always folds to a bet when holding a queen.

    This leaves two unspecified values:

    1. Ivan's betting frequency _when he holds a Queen_.

       NOTE: this is conditional on him holding a queen and is not the GLOBAL
       betting frequency

    2. Opal's calling frequency _when she holds a King_.

       NOTE: this is conditioned on Opal holding a King, and is not the GLOBAL
       calling frequency
    """
    ivan=(1,0,bet)
    opal=(1,call,0)

    def compute_ivan_ev(i, o):
        """
        Compute ivan's EV given his strategy and both player's cards

        i: ivan's card
        o: opal's card
        """
        b = ivan[i]
        c = opal[o]
        ivan_is_winning = i < o
        if ivan_is_winning:
            ev_when_bet = pot + bet_size*c
            ev_when_check = pot
        else:
            ev_when_bet = -c*bet_size + (1-c) * pot
            ev_when_check = 0
        scenario_ev = b*ev_when_bet + (1 - b)*ev_when_check
        return scenario_ev

    ev = 0    # ev holds the _unweighted_ ev
    table = [[0,0,0] for _ in range(3)]
    for ivans_card in range(3):
        for opals_card in range(3):
            if ivans_card == opals_card: continue
            x = compute_ivan_ev(ivans_card, opals_card)
            table[ivans_card][opals_card] = x
            ev += x
    print_table and print_strategy_table(table)
    return ev/6    # By linearity of E we can divide by # of scenarios

def find_equilibrium(bet_size = 1, print_table=False):
    print("Raw EV Table: ", end='')
    ev = ev_from_strategies(bet_size=bet_size, print_table=print_table)
    print("Raw EV:", ev)
    dEdb = diff(ev, b)
    opt_c = solve(dEdb, c)[0]
    if opt_c < 0:
        opt_c = 0
    elif opt_c > 1:
        opt_c = 1

    dEdc = diff(ev, c)
    opt_b = solve(dEdc, b)[0]
    if opt_b < 0:
        opt_b = 0
    elif opt_b > 1:
        opt_b = 1

    ev = ev.subs(b, opt_b).subs(c, opt_c)
    print("Bet with Queen: ", opt_b)
    print("Call with King: ", opt_c)
    print("Ivan's EV:", ev)
    return ev

def print_strategy_table(table):
    """
    Helper function, printing a strategy's EV in a table
    """
    print()
    print("  {:^12}{:^12}{:^12}".format('A', 'K', 'Q'))
    for i,row in enumerate(table):
        xs = []
        cell_width = 5
        for cell in row:
            if isinstance(cell, float):
                xs.append("{:^5.1f}".format(cell))
            else:
                xs.append("{}".format(str(cell)))
        print("{}|{:^12}{:^12}{:^12}".format('AKQ'[i], *xs))
    print()
