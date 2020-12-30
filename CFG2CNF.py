# https://en.wikipedia.org/wiki/Chomsky_normal_form#Converting_a_grammar_to_Chomsky_normal_form
# START->TERM->BIN->DEL->UNIT

class CFG():
    def __init__(self, *agrs, **kwargs):
        self.V = kwargs.get('V', None)
        self.T = kwargs.get('T', None)
        self.P = kwargs.get('P', None)
        self.S = kwargs.get('S', None)

    # Eliminate the start symbol from right-hand sides
    def START(self):
        self.V.add('S0')
        tmp = self.P.get('S0', set())
        tmp.add('S')
        self.P['S0'] = tmp
        self.S = 'S0'

    # Eliminate rules with nonsolitary terminals
    def TERM(self):
        return None

    # Eliminate right-hand sides with more than 2 nonterminals
    def BIN(self):
        return None

    # Eliminate ε-rules
    def DEL(self):
        return None

    # Eliminate unit rules
    def UNIT(self):
        return None

    def toCNF(self):
        self.START()
        self.TERM()
        self.BIN()
        self.DEL()
        self.UNIT()

    def __str__(self):
        P_str=''
        for key, value in self.P.items():
            tmp = ''
            list_value = list(value)
            for i in range(len(list_value)):
                if list_value[i] == chr(0):
                    p = 'ε'
                else:
                    p = list_value[i]
                tmp = tmp+p
                if i+1 < len(list_value):
                    tmp = tmp+'|'
            P_str = P_str+"\n\t\t{}\t-> {}".format(key, tmp)

        res = "\nG(V, T, P, S):\n\tV={}\n\tT={}\n\tP={}\n\tS={}".format(
            self.V,
            self.T,
            P_str,
            self.S
        )

        return res


def main():
    cfg = CFG(
        V={'S'},
        T={'a', 'b'},
        P={
            'S': {"abS", 'a', chr(0)}
        },
        S='S'
    )
    print(cfg)
    cfg.START()
    print(cfg)


if __name__ == "__main__":
    main()
