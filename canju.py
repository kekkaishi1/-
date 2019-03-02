#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
本程序用于破解斗地主残局
"""

__author__ = 'Lin Xin'

from multiprocessing import Pool
from itertools import combinations
from functools import reduce
import sys
from copy import deepcopy

sys.setrecursionlimit(10000)

WIN = 0
LOSE = 0


class CardType:
    """可出牌型为字符串组成的列表"""

    def __init__(self, card, name=None):
        self.card = card
        self.name = name

    def flow(self):
        """单顺子"""

        def find_max_flow(card, i):
            """找到以i开头的最长顺子"""

            if i > 14:
                return ''
            elif str(i) in card and i < 10:
                return str(i) + find_max_flow(card, i + 1)
            elif i == 10 and 'T' in card:
                return 'T' + find_max_flow(card, i + 1)
            elif i == 11 and 'J' in card:
                return 'J' + find_max_flow(card, i + 1)
            elif i == 12 and 'Q' in card:
                return 'Q' + find_max_flow(card, i + 1)
            elif i == 13 and 'K' in card:
                return 'K' + find_max_flow(card, i + 1)
            elif i == 14 and 'A' in card:
                return 'A' + find_max_flow(card, i + 1)
            else:
                return ''

        def find_max_flow_all():
            """找到所有最长顺子"""
            if len(find_max_flow(self.card, 3)) == 5:
                flows = [find_max_flow(self.card, 3)]
                if len(find_max_flow(self.card, 9)) >= 5:
                    flows.append(find_max_flow(self.card, 9))
                    return flows
                elif len(find_max_flow(self.card, 10)) == 5:
                    flows.append(find_max_flow(self.card, 10))
                    return flows

            if len(find_max_flow(self.card, 3)) == 6:
                flows = [find_max_flow(self.card, 3)]
                if len(find_max_flow(self.card, 10)) == 5:
                    flows.append(find_max_flow(self.card, 10))
                    return flows

            if len(find_max_flow(self.card, 4)) == 5:
                flows = [find_max_flow(self.card, 4)]
                if len(find_max_flow(self.card, 10)) == 5:
                    flows.append(find_max_flow(self.card, 10))
                    return flows

            for i in range(3, 11):
                if len(find_max_flow(self.card, i)) > 4:
                    return [find_max_flow(self.card, i)]
            return []

        def unpack_flow(long_flow, shortest_length):
            """切割长顺"""
            if len(flow) > shortest_length:
                short_flow = []
                for i in range(len(long_flow) - shortest_length + 1):
                    for k in range(shortest_length + i, len(long_flow) + 1):
                        short_flow.append(long_flow[i: k])
                short_flow.remove(long_flow)
                return short_flow
            return []

        single_flow = find_max_flow_all()
        for flow in find_max_flow_all():
            single_flow += unpack_flow(flow, 5)
        # single flow complete

        """连对"""
        all_pair = [pair[0:len(pair) // 2] for pair in self.pairs()]
        double_flow = []
        for i in range(3, 13):
            if len(find_max_flow(all_pair, i)) >= 3:
                double_flow.append(find_max_flow(all_pair, i))
        flow_temp = double_flow
        for flow in flow_temp:
            double_flow += unpack_flow(flow, 3)
        double_flow_final = [flow * 2 for flow in set(double_flow)]
        # double_pair complete

        """飞机"""
        tri_card = [i for i in self.single() if self.card.count(i) >= 3]
        plane = []
        for i in range(3, 14):
            if len(find_max_flow(tri_card, i)) >= 2:
                plane.append(find_max_flow(tri_card, i))
        flow_temp = plane
        for flow in flow_temp:
            plane += unpack_flow(flow, 2)
        plane = list(set(plane))
        plane_final = [i * 3 for i in plane]
        for i in plane:
            if len(self.single()) >= len(i):
                for single_card in combinations(CardType(self.card_out(i * 3)).single(), len(i)):
                    plane_final += [i * 3 + ''.join(single_card)]
            if len(self.pairs()) >= len(i):
                for pair_card in combinations(CardType(self.card_out(i * 3)).pairs(), len(i)):
                    plane_final += [i * 3 + ''.join(pair_card)]
        return [single_flow, double_flow_final, plane_final]

    def single(self):
        """单张"""
        single = list(set(self.card))
        return single

    def tri_four(self):
        """三带四带"""
        plane3 = [i * 3 for i in self.single() if self.card.count(i) >= 3]
        plane3_1, plane3_2 = [], []
        for plane_3 in plane3:
            plane3_1 += [i + plane_3 for i in self.card_out(plane_3)]
            plane3_2 += [i + plane_3 for i in CardType(self.card_out(plane_3)).pairs()]

        plane4 = [i * 4 for i in self.single() if self.card.count(i) == 4]
        plane4_1, plane4_2 = [], []
        for plane_4 in plane4:
            plane4_1 += [plane_4 + card1 + card2 for i, card1 in enumerate(self.card_out(plane_4)) for j, card2 in
                         enumerate(self.card_out(plane_4)) if i < j]
            plane4_2 += [plane_4 + card1 + card2 for i, card1 in enumerate(CardType(self.card_out(plane_4)).pairs()) for
                         j, card2 in
                         enumerate(CardType(self.card_out(plane_4)).pairs()) if i < j]
        return plane3 + plane3_1 + plane3_2 + plane4_1 + plane4_2

    def pairs(self):
        """对子"""
        pairs = [i * 2 for i in self.single() if self.card.count(i) > 1]
        return pairs

    def boom(self):
        """炸弹"""
        boom = [i * 4 for i in self.single() if self.card.count(i) == 4]
        if 'G' in self.card and 'g' in self.card:
            boom.append('Gg')
        return boom

    def card_type(self):
        """可以出的牌"""
        card_type = {'single_flow': self.flow()[0], 'double_flow': self.flow()[1], 'plane': self.flow()[2],
                     'single': self.single(), 'pairs': self.pairs(), 'boom': self.boom(), 'tri_four': self.tri_four(),
                     'pass': ['']}
        return card_type

    def card_type_list(self):
        """可以出的牌的列表"""
        card_type_list = reduce(lambda x, y: x + y, [i for i in self.card_type().values()])
        return card_type_list

    def update(self, _card_out):
        """更新牌型"""
        for c in _card_out:
            self.card.remove(c)

    def card_out(self, card_out):
        """返回出牌后剩下的牌，用于生成牌型"""
        card_current = [i for i in self.card]
        for card in card_out:
            card_current.remove(card)
        return card_current


class CardTypeOne:
    def __init__(self, data, types):
        self.data = data
        self.types = types

    def __eq__(self, other):
        return self.data == other.data

    def __gt__(self, other):
        return compare(self.data, other.data, self.types)

    def __lt__(self, other):
        return compare(other.data, self.data, self.types)

    def __ge__(self, other):
        return not compare(other.data, self.data, self.types)

    def __le__(self, other):
        return not compare(self.data, other.data, self.types)


def init():
    """初始化牌型"""
    # c1 = input('please input player1\'s card like this:3345678JKA2 JOKER with G and T for 10\n')
    # c2 = input('please input player2\'s card like this:3345678JKA2 JOKER with G and T for 10\n')
    c2 = '446TJKKA'
    c1 = '335779JJK2'
    # c1 = '3456722'
    # c2 = '8899K'
    cards1, cards2 = list(c1), list(c2)
    return cards1, cards2


def transform(card):
    if card == 'T':
        return 10
    if card == 'J':
        return 11
    if card == 'Q':
        return 12
    if card == 'K':
        return 13
    if card == 'A':
        return 14
    if card == '2':
        return 15
    if card == 'g':
        return 16
    if card == 'G':
        return 17
    return int(card)


def cards_power(cards):
    if cards == 'Gg' or cards.count(cards[0]) == 4:
        cards_p = 1
    else:
        cards_p = 0
    return cards_p


def compare(card, last_card, types):
    if cards_power(card) > cards_power(last_card):
        return True
    if cards_power(card) < cards_power(last_card):
        return False
    if cards_power(card) + cards_power(last_card) == 2:
        return transform(card[0]) > transform(last_card[0])
    if types in ('single', 'pairs', 'single_flow', 'double_flow'):
        return transform(card[0]) > transform(last_card[0])
    if types in ('tri_four', 'plane'):
        card_min = [transform(i) for i in card if card.count(i) >= 3][0]
        last_card_min = [transform(i) for i in last_card if last_card.count(i) >= 3][0]
        return card_min > last_card_min


def card_issame(card1, card2, cardtype):
    """
    用于判断牌型的对称性，以减少运算时间复杂度
    牌力：当前牌在对面牌下的权重
    eg： 3，4对于5而言都是小的，此情况下3，4牌力大小相同
    :param card1: player1 本牌型下所有牌
    :param card2: player2 本牌型下所有牌
    :return: 返回一个列表，包含不同牌力的牌
    """

    def paixu(card_1, card_2):
        """
        用于排序,从前向后依次为从1相加，相等的话加0.5
        eg:
            card_2=3 5 7
            card_1: 2: 1
                    3: 1.5
                    4: 2
                    5: 2.5
                    6: 3
                    7: 3.5
                    8: 4
        :param card_1:用于插入比较的牌
        :param card_2:用于比较的牌列表
        :return: card1 在card2中的位置
        """
        nonlocal cardtype
        card_1_temp = CardTypeOne(card_1, cardtype)
        l = 1
        for i in range(len(card_2)):
            if card_1_temp < CardTypeOne(card_2[i], cardtype):
                return l
            elif card_1_temp == CardTypeOne(card_2[i], cardtype):
                return 1 + 0.5
            l += 1
        else:
            return l

    card_chikara = {card: paixu(card, card2) for card in card1}
    card_chikara_t = {}
    for v in set(card_chikara.values()):
        card_chikara_t[v] = []
        for k in card_chikara.keys():
            if card_chikara[k] == v:
                card_chikara_t[v].append(k)
    return card_chikara_t  # {1:[3,4,5],2：J,3:k}


def card_out(player1, player2, last_card_type='pass', last_card=''):
    """
    :param player1: 本局出牌人牌型类实例
    :param player2: 本局非出牌人牌型类实例
    :param last_card_type: 上局所出牌型
    :param last_card: 上局出牌
    :return:
    """

    global WIN, LOSE
    if last_card_type == 'pass':
        """上局对面pass，随便出但不能PASS"""
        for cardtype in player1.card_type().keys():
            if cardtype == 'pass':
                continue
            player1_distinct = card_issame(player1.card_type()[cardtype], player2.card_type()[cardtype], cardtype)
            for card_li in player1_distinct:
                card = player1_distinct[card_li][0]
                if player1.name == 'player1' and len(player1.card) == player1_origin:
                    try:
                        print('{1}\n本手出{0}的获胜概率为：'.format(player1_distinct[card_li], WIN / (WIN + LOSE)), end='')
                        WIN = LOSE = 0
                    except ZeroDivisionError:
                        print('本手出{0}的获胜概率为：'.format(player1_distinct[card_li]), end='')
                player1_temp, player2_temp = deepcopy(player1), deepcopy(player2)
                player1_temp.update(card)
                if len(player1_temp.card) == 0:
                    if player1.name == 'player1':
                        WIN += 1
                    else:
                        LOSE += 1
                else:
                    card_out(player2_temp, player1_temp, cardtype, card)
    else:
        """
        上局对面不是PASS
        """
        # 能大上的牌
        card_big = [card for card in player1.card_type()[last_card_type] if compare(card, last_card, last_card_type)]
        for card in card_big:
            player1_temp, player2_temp = deepcopy(player1), deepcopy(player2)
            player1_temp.update(card)
            if len(player1_temp.card) == 0:
                if player1.name == 'player1':
                    WIN += 1
                else:
                    LOSE += 1
            else:
                card_out(player2_temp, player1_temp, last_card_type, card)
        player1_temp, player2_temp = deepcopy(player1), deepcopy(player2)
        card_out(player2_temp, player1_temp)


if __name__ == '__main__':
    player1, player2 = init()
    player1, player2 = CardType(player1, 'player1'), CardType(player2, 'player2')
    player1_origin = len(player1.card)
    card_out(player1, player2)
    print(WIN / (WIN + LOSE))
