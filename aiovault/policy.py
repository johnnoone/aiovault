from collections.abc import MutableMapping


class Policy(MutableMapping):

    def __init__(self, *, name, rules=None):
        """
        Parameters:
            name (str): The policy name
            rules (obj): List of :ref:`Rule` or a dict.
        """
        self.name = name
        self.rules = {}
        if isinstance(rules, dict):
            self.rules.update(rules)
        elif isinstance(rules, (list, set)):
            for rule in rules:
                self.__setitem__(*rule)
        elif isinstance(rules, tuple):
            self.__setitem__(*rules)

    def __getitem__(self, path):
        return self.rules[path]

    def __setitem__(self, path, policy):
        if isinstance(policy, str):
            policy = {
                'policy': policy
            }
        self.rules[path] = policy

    def __delitem__(self, path):
        del self.rules[path]

    def __iter__(self):
        return iter(self.rules)

    def __len__(self):
        return len(self.rules)

    def __eq__(self, other):
        if isinstance(other, Policy):
            other == other.rules
        return self.rules == other

    def __repr__(self):
        return '<Policy(name=%r, rules=%r)>' % (self.name, self.rules)
