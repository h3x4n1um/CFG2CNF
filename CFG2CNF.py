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

    def get_rule(self, var):
        return self.P.get(var, set())

    def set_rule(self, var, rule_set):
        self.P[var] = set()
        for rule in rule_set:
            self.add_rule(var, rule)

    def union_rule(self, var, rule_set):
        for rule in rule_set:
            self.add_rule(var, rule)

    # add rule key -> value
    def add_rule(self, var, rule):
        self.V.add(var)

        tmp = rule.split(',')
        for c in tmp:
            if c not in self.T and c != self.epsilon:
                self.V.add(c)

        if var not in self.P:
            self.P[var] = set([rule])
        else:
            self.P[var].add(rule)

    # remove rule key -> value
    def remove_rule(self, var, rule):
        self.P.get(var, set()).discard(rule)

    # Eliminate the start symbol from right-hand sides
    def START(self):
        self.add_rule('S0', 'S')
        self.S = 'S0'

    # Eliminate rules with nonsolitary terminals
    def TERM(self):
        sub = dict()
        for c in self.T:
            sub[c] = 'C'+c

        for key in self.V.copy():
            for rule in self.get_rule(key).copy():
                self.remove_rule(key, rule)
                rule = rule.split(self.delimiter)

                if len(rule) > 1:
                    for i in range(len(rule)):
                        c = rule[i]
                        if c in self.T:
                            self.add_rule(sub[c], c)
                            c = sub[c]
                            #print("key: {}\trule:{}\t{}".format(key, rule, c))
                        rule[i] = c

                rule = self.delimiter.join(rule)
                self.add_rule(key, rule)

    # Eliminate right-hand sides with more than 2 nonterminals
    def BIN(self):
        cnt = 1
        for key in self.V.copy():
            for rule in self.get_rule(key).copy():
                rule = rule.split(self.delimiter)

                if len(rule) > 2 and set(rule).issubset(self.V):
                    self.remove_rule(key, self.delimiter.join(rule))
                    tmp = rule

                    v = 'C'+str(cnt)
                    cnt = cnt+1
                    self.add_rule(key, tmp.pop(0)+','+v)

                    while len(tmp) > 2:
                        pre_v = v
                        v = "C"+str(cnt)
                        cnt = cnt+1
                        self.add_rule(pre_v, pre_v+','+tmp.pop(0))
                    self.add_rule(v, self.delimiter.join(tmp))
                else:
                    self.add_rule(key, self.delimiter.join(rule))

    # Eliminate ε-rules
    def epsilon_ommit(self, nullable, rule):
        #print("epsilon_ommit rule: {}".format(rule))
        if len(rule) == 1:
            return set([self.delimiter.join(rule)])

        res = set([self.delimiter.join(rule)])
        for i in range(len(rule)):
            c = rule[i]
            if c in nullable:
                tmp = rule.copy()
                tmp.remove(c)
                res_tmp = self.epsilon_ommit(nullable, tmp)
                #print("epsion_ommit recur: {}".format(res_tmp))
                res = res.union(res_tmp)
        return res

    def DEL(self):
        nullable = set()
        stop = False

        while stop == False:
            stop = True

            for key in self.V.copy():
                if key not in nullable and key != self.S:
                    for rule in self.get_rule(key):
                        rule = rule.split(self.delimiter)

                        if len(rule) == 1 and self.delimiter.join(rule) == self.epsilon:
                            nullable.add(key)
                            stop = False
                        elif set(rule).issubset(self.V) and set(rule).issubset(nullable):
                            nullable.add(key)
                            stop = False

        #print("nullable:{}".format(nullable))
        if len(nullable) > 0:
            # remove x -> epsilon
            for key in nullable:
                self.remove_rule(key, self.epsilon)

            for key in self.V.copy():
                for rule in self.get_rule(key).copy():
                    rule = rule.split(self.delimiter)
                    for c in nullable:
                        if c in rule:
                            #print("key: {}\trule: {}".format(key, rule))
                            ommited = self.epsilon_ommit(nullable, rule)
                            #print(ommited)
                            self.union_rule(key, ommited)

    # Eliminate unit rules
    def UNIT(self):
        for var in self.V.copy():
            for rule in self.get_rule(var).copy():
                rule = rule.split(',')
                if len(rule) == 1:
                    tmp = self.delimiter.join(rule)
                    if tmp in self.V:
                        self.union_rule(var, self.get_rule(tmp))
                        self.remove_rule(var, tmp)

    def to_CNF(self):
        self.START()
        self.TERM()
        self.BIN()
        self.DEL()
        self.UNIT()

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
                "\n\t\t{}\t->\t{}".format(key, " | ".join(list(value)))

        return "\nG(V, T, P, S):\n\tV={}\n\tT={}\n\tP={}\n\tS={}".format(
            self.V,
            self.T,
            P_str,
            self.S
        )


def main():
    cfg = CFG(
        V={'S', 'A', 'B'},
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
                'b,b'
            }
        },
        S='S'
    )
    print(cfg)
    cfg.to_CNF()
    print(cfg)


if __name__ == "__main__":
    main()
