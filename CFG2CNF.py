# https://en.wikipedia.org/wiki/Chomsky_normal_form#Converting_a_grammar_to_Chomsky_normal_form
# START->TERM->BIN->DEL->UNIT


class CFG():
    def __init__(self, **kwargs):
        self.V = kwargs.get('V', set())
        self.T = kwargs.get('T', set())
        self.P = kwargs.get('P', dict())
        self.S = kwargs.get('S', str())
        self.delimiter = kwargs.get('delimiter', ',')
        self.epsilon = kwargs.get('epsilon', 'ε')

    def copy(self):
        res_P = dict()
        for key, value in self.P.items():
            res_P[key] = value.copy()

        res = CFG(
            V=self.V.copy(),
            T=self.T.copy(),
            P=res_P,
            S=self.S
        )
        return res

    def get_rule(self, var):
        return self.P.get(var, set())

    def union_rule(self, var, rule_set):
        for rule in rule_set:
            self.add_rule(var, rule)

    # add rule var -> value
    def add_rule(self, var, rule):
        self.V.add(var)

        for c in rule.split(self.delimiter):
            if c not in self.T and c != self.epsilon:
                self.V.add(c)

        if var not in self.P:
            self.P[var] = set()
        self.P[var].add(rule)

    # remove rule var -> value
    def remove_rule(self, var, rule):
        self.P.get(var, set()).discard(rule)
        # if it has no rule then hasta la vista
        tmp = rule.split(self.delimiter)
        tmp.append(var)
        for c in tmp:
            if c in self.V:
                if len(self.P.get(c, set())) == 0:
                    self.V.discard(c)
                    self.P.pop(c, None)

    # remove var from CFG
    def remove_var(self, var):
        for rule in self.get_rule(var).copy():
            self.remove_rule(var, rule)

        for tmp_var in self.V.copy():
            for rule in self.get_rule(tmp_var).copy():
                for c in rule.split(self.delimiter):
                    if c == var:
                        self.remove_rule(var, rule)

    # Eliminate symbol not produce from S
    def PURGE(self):
        res = self.copy()
        producible = set(res.S)
        stop = False
        while stop == False:
            stop = True
            for var in producible.copy():
                for rule in res.get_rule(var):
                    for c in rule.split(res.delimiter):
                        if c in res.V and c not in producible:
                            producible.add(c)
                            stop = False

        for var in res.V.copy():
            if var not in producible:
                res.remove_var(var)

        return res

    # Eliminate the start symbol from right-hand sides
    def START(self):
        res = self.copy()
        res.add_rule('S0', 'S')
        res.S = 'S0'
        return res

    # Eliminate rules with nonsolitary terminals
    def TERM(self):
        res = self.copy()
        sub = dict()
        for c in res.T:
            sub[c] = 'C'+c

        for var in res.V.copy():
            for rule in res.get_rule(var).copy():
                rule = rule.split(res.delimiter)

                if len(rule) > 1:
                    for i in range(len(rule)):
                        c = rule[i]
                        if c in res.T:
                            res.remove_rule(var, res.delimiter.join(rule))
                            res.add_rule(sub[c], c)
                            c = sub[c]
                            # print("var: {}\trule:{}\t{}".format(var, rule, c))
                        rule[i] = c
                    res.add_rule(var, res.delimiter.join(rule))
        return res

    # Eliminate right-hand sides with more than 2 nonterminals
    def BIN(self):
        res = self.copy()
        cnt = 1
        for var in res.V.copy():
            for rule in res.get_rule(var).copy():
                rule = rule.split(res.delimiter)

                if len(rule) > 2 and set(rule).issubset(res.V):
                    res.remove_rule(var, res.delimiter.join(rule))
                    tmp = rule

                    v = 'C'+str(cnt)
                    cnt = cnt+1
                    res.add_rule(var, tmp.pop(0)+res.delimiter+v)

                    while len(tmp) > 2:
                        pre_v = v
                        v = 'C'+str(cnt)
                        cnt = cnt+1
                        res.add_rule(pre_v, pre_v+res.delimiter+tmp.pop(0))
                    res.add_rule(v, res.delimiter.join(tmp))
        return res

    # Eliminate ε-rules
    def epsilon_ommit(self, nullable, rule):
        # print("epsilon_ommit rule: {}".format(rule))
        if len(self.delimiter.join(rule)) == 1:
            return set([rule])

        res = set([rule])
        for c in rule.split(self.delimiter):
            if c in nullable:
                tmp = rule.split(self.delimiter)
                tmp.remove(c)
                res_tmp = self.epsilon_ommit(
                    nullable, self.delimiter.join(tmp))
                # print("epsion_ommit recur: {}".format(res_tmp))
                res = res.union(res_tmp)
        return res

    def DEL(self):
        res = self.copy()
        nullable = set()
        stop = False

        while stop == False:
            stop = True

            for var in res.V:
                if var not in nullable and var != res.S:
                    for rule in res.get_rule(var):
                        rule = rule.split(res.delimiter)

                        if len(rule) == 1 and res.delimiter.join(rule) == res.epsilon:
                            nullable.add(var)
                            stop = False
                        elif set(rule).issubset(res.V) and set(rule).issubset(nullable):
                            nullable.add(var)
                            stop = False

        # print("nullable:{}".format(nullable))
        if len(nullable) > 0:
            # remove x -> epsilon
            for var in nullable:
                res.remove_rule(var, res.epsilon)

            for var in res.V.copy():
                for rule in res.get_rule(var).copy():
                    for c in nullable:
                        if c in rule.split(res.delimiter):
                            # print("var: {}\trule: {}".format(var, rule))
                            ommited = res.epsilon_ommit(nullable, rule)
                            # print(ommited)
                            res.union_rule(var, ommited)
        return res

    # Eliminate unit rules
    def UNIT(self):
        res = self.copy()
        stop = False
        while stop == False:
            stop = True

            for var in res.V.copy():
                for rule in res.get_rule(var).copy():
                    rule = rule.split(res.delimiter)

                    if len(rule) == 1:
                        tmp = res.delimiter.join(rule)

                        if tmp in res.V:
                            stop = False
                            res.union_rule(var, res.get_rule(tmp))
                            res.remove_rule(var, tmp)
                            res.remove_rule(var, var)
        return res

    def is_CNF(self):
        for var in self.V:
            for rule in self.get_rule(var):
                rule = rule.split(self.delimiter)
                if len(rule) > 2:
                    return False
                elif len(rule) == 2:
                    if not set(rule).issubset(self.V):
                        return False
                else:
                    if not set(rule).issubset(self.T):
                        return False
        return True

    def CNF(self):
        if self.is_CNF():
            return self
        return self.PURGE().START().TERM().BIN().DEL().UNIT()

    def __repr__(self):
        return "\n\tV={}\n\tT={}\n\tP={}\n\tS={}\n\tdelimiter={}\n\tepsilon={}".format(
            self.V,
            self.T,
            self.P,
            self.S,
            self.delimiter,
            self.epsilon
        )

    def __str__(self):
        P_str = ''
        for key, value in self.P.items():
            P_str = P_str + \
                "\n\t\t{}\t->\t{}".format(key, "\t| ".join(value))

        return "\nG(V, T, P, S):\n\tV={}\n\tT={}\n\tP={}\n\tS={}".format(
            self.V,
            self.T,
            P_str,
            self.S
        )


def main():
    cfg = CFG(
        V={'S', 'A', 'B', 'C', 'D', 'E'},
        T={'a', 'b'},
        P={
            'S': {
                'A,S,B',
            },
            'A': {
                'a,A,S',
                'a',
                'ε'
            },
            'B': {
                'S,b,S',
                'A',
                'b,b',
                'E'
            },
            'C': {
                'a,b',
                'D'
            },
            'D': {
                'C',
                'b,B'
            },
            'E': {
                'ε'
            }
        },
        S='S'
    )
    print(cfg)
    print(cfg.CNF())


if __name__ == "__main__":
    main()
