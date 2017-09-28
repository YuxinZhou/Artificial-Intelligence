import random
import time

class Literal:
    def __init__(self, positive, guest, table):
        self.positive = positive
        self.guest = guest
        self.table = table

    def is_complementary(self, other):
        """
        :type other: Literal
        :param other: the other literal
        :return:
        """
        if self.positive != other.positive and self.guest == other.guest \
                and self.table == other.table:
            return True
        return False

    def complementary_literal(self):
        return Literal(not self.positive, self.guest, self.table)

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        """Define a non-equality test"""
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        """Override the default hash behavior (that returns the id or the object)"""
        return hash(tuple(sorted(self.__dict__.items())))


class Model:
    def __init__(self, M, N, clauseSet=set()):
        """
        :param M: n_guest
        :param N: n_table
        :param clauseSet: CNF
        """
        self.M = M
        self.N = N
        self.clauseSet = clauseSet
        # M row * N col 2-D array
        self.symbols = [[bool(random.getrandbits(1)) for i in range(N)] for j in range(M)]

    def clause_value(self, clause):
        clause_value = False
        for literal in clause:
            if literal.positive:
                literal_value = self.symbols[literal.guest - 1][literal.table - 1]
            else:
                literal_value = not (self.symbols[literal.guest - 1][literal.table - 1])
            clause_value = clause_value or literal_value
        return clause_value

    def encode_one_table(self):
        M = self.M
        N = self.N
        # for each guest a, a = 1, 2, ... , n_guest
        for a in range(1, M + 1):
            clause = []
            # Union X(a, i) for i = 1, 2, .., n_table
            for i in range(1, N + 1):
                literal = Literal(True, a, i)
                clause.append(literal)
            self.clauseSet.add(tuple(clause))
            # Union {not X(a, i) U not X(a,j)} for 1 <= i < j <= n_table
            for i in range(1, N + 1):
                for j in range(i + 1, N + 1):
                    clause = []
                    # not X(a, i) U not X(a,j)
                    literal = Literal(False, a, i)
                    clause.append(literal)
                    literal = Literal(False, a, j)
                    clause.append(literal)
                    self.clauseSet.add(tuple(clause))
        return

    def encode_friend(self, a, b):
        """
        :param a: guest 1
        :param b: guest 2
        """
        N = self.N
        # for i = 1, 2, .., n_table
        for i in range(1, N + 1):
            clause = []
            # not X(a, i) Union X(b, i)
            literal = Literal(False, a, i)
            clause.append(literal)
            literal = Literal(True, b, i)
            clause.append(literal)
            self.clauseSet.add(tuple(clause))
            # X(a, i) Union not X(b, i)
            clause = []
            literal = Literal(True, a, i)
            clause.append(literal)
            literal = Literal(False, b, i)
            clause.append(literal)
            self.clauseSet.add(tuple(clause))
        return

    def encode_enemy(self, a, b):
        """
        :param a: guest 1
        :param b: guest 2
        """
        N = self.N
        # for i = 1, 2, .., n_table
        for i in range(1, N + 1):
            clause = []
            # not X(a, i) U not X(b,j)
            literal = Literal(False, a, i)
            clause.append(literal)
            literal = Literal(False, b, i)
            clause.append(literal)
            self.clauseSet.add(tuple(clause))
        return


class PLResolution:
    def __init__(self):
        pass

    def pl_resolve(self, c1, c2):
        """
        :type c1: tuple(Literal)
        :type c2: tuple(Literal)
        :rtype: set(tuple(Literal))

        :param c1: clause1
        :param c2: clause2
        :return: a set of resolvents (clauses)
        """
        resolventSet = set()
        for literal in c1:
            resolvent = []
            if literal.complementary_literal() in c2:
                for i in c1:
                    if i != literal:
                        resolvent.append(i)
                for j in c2:
                    if j != literal.complementary_literal():
                        resolvent.append(j)
                resolventSet.add(tuple(resolvent))
        return resolventSet

    def pl_resolution(self, clauseSet):
        """
        :type clauseSet: set(tuple(literal))
        :rtype: bool

        :param clauseSet:
        :return: return true if the clauseSet is satisfiable,
        false if the sentence is unsatisfiable
        """
        newSet = set()
        while (True):
            clauseList = list(clauseSet)
            clen = len(clauseList)
            for i in range(clen):
                for j in range(i + 1, clen):
                    clause1 = clauseList[i]
                    clause2 = clauseList[j]
                    resolvents = self.pl_resolve(clause1, clause2)
                    for r in resolvents:
                        if len(r) == 0:
                            return False
                    newSet = newSet.union(resolvents)
            if newSet.issubset(clauseSet):
                return True
            clauseSet = clauseSet.union(newSet)


class WalkSAT:
    def __init__(self, model):
        self.model = model

    def walksat(self, p, max_flip):
        for i in range(max_flip):
            if self.is_satisfied():
                return self.model.symbols
            negClause = self.random_select_neg_clause()
            if random.random() < p:
                self.flip_symbol_random(negClause)
            else:
                self.flip_symbol_max(negClause)
        return None

    def deepcopy_2D_list(self, l):
        return [x[:] for x in l]

    def is_satisfied(self):
        model = self.model
        if len(model.clauseSet) == self.count_satisfied_clauses():
            return True
        else:
            return False

    def flip_symbol_random(self, clause):
        literalList = list(clause)
        # Return a random integer N such that a <= N <= b. r = random.randint
        r = random.randint(0, len(literalList) - 1)
        x = literalList[r].guest - 1
        y = literalList[r].table - 1
        self.flip_symbol(x, y)
        return

    def flip_symbol_max(self, clause):
        """
        flip symbol in clause to maximizes number of satisfied clauses
        :param clause:
        :type clause: tuple(Literal)
        :return:
        """
        model = self.model
        literalList = list(clause)
        m_x, m_y = -1, -1  # symbol in clause maximizes number satisfied clauses
        max_count = -1
        for i in range(len(literalList)):
            symbols_copy = self.deepcopy_2D_list(model.symbols)
            x = literalList[i].guest - 1
            y = literalList[i].table - 1
            self.flip_symbol(x, y)
            if self.count_satisfied_clauses() > max_count:
                max_count = self.count_satisfied_clauses()
                m_x, m_y = x, y
            model.symbols = self.deepcopy_2D_list(symbols_copy)
        self.flip_symbol(m_x, m_y)
        return

    def flip_symbol(self, x, y):
        flip = self.model.symbols[x][y]
        self.model.symbols[x][y] = not flip
        return

    def random_select_neg_clause(self):
        negClauseList = []
        for clause in self.model.clauseSet:
            clause_value = self.model.clause_value(clause)
            if not clause_value:
                negClauseList.append(clause)
        # Return a random integer N such that a <= N <= b. r = random.randint
        r = random.randint(0, len(negClauseList) - 1)
        return negClauseList[r]

    def count_satisfied_clauses(self):
        # clauses = []
        count = 0
        for clause in self.model.clauseSet:
            clause_value = self.model.clause_value(clause)
            if clause_value:
                count = count + 1
                # clauses.append(clause_value)
        return count


class DPLL:
    def __init__(self):
        pass

    def dpll(self, clauseSet):
        # print_clause_set(clauseSet)
        # every clause True
        if len(clauseSet) == 0:
            return True
        # some clause False
        for c in clauseSet:
            if len(c) == 0:
                return False
        # unit symbol
        unit = self.find_first_unit_symbol(clauseSet)
        if unit is not None:
            clauseSet = self.unit_symbol_rules(clauseSet, unit)
            return self.dpll(clauseSet)
        pure = self.find_pure_symbol(clauseSet)
        if len(pure) > 0:
            clauseSet = self.pure_symbol_rule(clauseSet, pure)
            return self.dpll(clauseSet)
        # pure symbol
        # try values for first symbol
        first_literal = self.first_literal(clauseSet)
        clauseSet1 = self.assign_true_value(clauseSet, first_literal)
        clauseSet2 = self.assign_false_value(clauseSet, first_literal)
        return self.dpll(clauseSet1) or self.dpll(clauseSet2)

    def find_pure_symbol(self, clauseSet):
        neg_literal = set()
        pos_literal = set()
        for clause in clauseSet:
            for literal in clause:
                if literal.positive:
                    pos_literal.add(literal)
                else:
                    neg_literal.add(literal)
        pos_literal_trans = set()
        neg_literal_trans = set()
        for literal in pos_literal:
            pos_literal_trans.add(literal.complementary_literal())
        for literal in neg_literal:
            neg_literal_trans.add(literal.complementary_literal())
        pos_literal = pos_literal.difference(pos_literal.intersection(neg_literal_trans))
        neg_literal = neg_literal.difference(neg_literal.intersection(pos_literal_trans))
        return pos_literal.union(neg_literal)

    def pure_symbol_rule(self, clauseSet, pure):
        """remove all clauses that contain a pure symbols"""
        return set([clause for clause in clauseSet if self.not_contained_in_list(clause, pure)])

    def not_contained_in_list(self, clause, list):
        """filter"""
        for literal in clause:
            if literal in list:
                return False
        return True

    def not_equal_literal(self, clause, l):
        for literal in clause:
            if literal == l:
                return False
        return True

    def find_first_unit_symbol(self, clauseSet):
        for clause in clauseSet:
            if len(clause) == 1:
                for literal in clause:
                    return literal
        return None

    def unit_symbol_rules(self, clauseSet, unit):
        """
        Remove any clause where the unit clause is a subset
        Remove the complement of the literal from all remaining clauses
        :type clauseSet: set
        """
        clauseSet = set([clause for clause in clauseSet if self.not_equal_literal(clause, unit)])
        clause_return = set()
        for clause in clauseSet:
            literal_list = []
            for literal in clause:
                if literal.complementary_literal() != unit:
                    literal_list.append(literal)
            clause_return.add(tuple(literal_list))
        return clause_return

    def first_literal(self, clauseSet):
        for clause in clauseSet:
            if len(clause) > 0:
                for literal in clause:
                    return literal

    def assign_true_value(self, clauseSet, first_literal):
        """ same as unit symbol rules"""
        return self.unit_symbol_rules(clauseSet, first_literal)

    def assign_false_value(self, clauseSet, first_literal):
        return self.assign_true_value(clauseSet, first_literal.complementary_literal())


def read_from_file(fname):
    f = open(fname, 'r')
    line = f.readline().split()
    guest = int(line[0])
    table = int(line[1])
    model = Model(guest, table)
    model.encode_one_table()
    for line in f.readlines():
        line = line.split()
        g1 = int(line[0])
        g2 = int(line[1])
        relationship = line[2]
        if relationship == 'F':
            model.encode_friend(g1, g2)
        elif relationship == 'E':
            model.encode_enemy(g1, g2)
    f.close()
    return model


def write_to_file(fname, has_answer, symbols=[]):
    f = open(fname, 'w')
    if has_answer:
        f.write('yes')
        f.write('\n')
        for i in range(len(symbols)):
            for j in range(len(symbols[i])):
                if symbols[i][j]:
                    f.write('{0} {1}'.format(i + 1, j + 1))
                    f.write('\n')
        return
    else:
        f.write('no')
        f.write('\n')
    f.close()


def main():
    start = time.time()
    model = read_from_file('input.txt')
    dpll = DPLL()
    if (dpll.dpll(model.clauseSet)):
        print 'yes'
        walk = WalkSAT(model)
        result = walk.walksat(0.5, 100000)
        if result is None:
            print 'error'

        # else:
        #     write_to_file('output.txt', True, result)
    else:
        print 'no'
        # write_to_file('output.txt', False)
    end = time.time()
    print end - start


def print_clause_set(clause_set):
    """for test"""
    for clause in clause_set:
        c = []
        for literal in clause:
            c.append('({0} {1} {2})'.format(literal.positive, literal.guest, literal.table))
        print ' '.join(c)
    print '---------------'
    return

if __name__ == '__main__':
    main()
