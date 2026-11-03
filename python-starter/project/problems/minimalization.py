from project.problem import Problem

import argparse

class MinimalizationProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            '--mini',
            action='store_true',
            help='minimize the automaton'
        )

    def is_chosen_problem(self, args):
        return args.mini

    def run(self, args):
        input_file = args.input
        output_file = args.output

        with open(input_file, 'r') as f:
            lines = f.readlines()

        states = lines[0].split()
        alphabet = lines[1].split()
        start_state = lines[2].strip()
        final_states = lines[3].split()

        # az atmeneteket egy dictionary-be tesszuk
        transitions = {}

        for line in lines[4:]:
            parts = line.split()

            if not parts:
                continue

            from_state = parts[0]
            symbol = parts[1]
            to_state = parts[2]

            # ellenorizzuk az allapotokat es a szimbolumot
            if from_state not in states or to_state not in states:
                raise ValueError("Hibas allapot az atmenetben")

            if symbol not in alphabet:
                raise ValueError("Hibas szimbolum az atmenetben")

            if (from_state, symbol) in transitions:
                if transitions[(from_state, symbol)] != to_state:
                    raise ValueError("Nem determinisztikus automata")

            transitions[(from_state, symbol)] = to_state

        if start_state not in states:
            raise ValueError("Hibas kezdoallapot")

        for state in final_states:
            if state not in states:
                raise ValueError("Hibas vegallapot")

        # az automata teljesse tetele
        # a hianyzo atmeneteket csapdaallapotba iranyitjuk
        trap_state = "__trap__"

        while trap_state in states:
            trap_state += "_"

        complete_states = states.copy()
        complete_transitions = transitions.copy()

        need_trap = False

        for state in states:
            for symbol in alphabet:
                if (state, symbol) not in complete_transitions:
                    complete_transitions[(state, symbol)] = trap_state
                    need_trap = True

        if need_trap:
            complete_states.append(trap_state)

            for symbol in alphabet:
                complete_transitions[(trap_state, symbol)] = trap_state

        # megkulonboztethetosegi tablazat
        # a parokat frozenset segitsegevel taroljuk
        marked = set()

        # eloszor megjeloljuk azokat a parokat,
        # ahol az egyik vegallapot, a masik nem
        for i in range(len(complete_states)):
            for j in range(i + 1, len(complete_states)):
                state1 = complete_states[i]
                state2 = complete_states[j]

                if ((state1 in final_states) !=
                        (state2 in final_states)):
                    marked.add(frozenset([state1, state2]))

        # tovabbi megkulonboztetheto parok keresese
        changed = True

        while changed:
            changed = False

            for i in range(len(complete_states)):
                for j in range(i + 1, len(complete_states)):
                    state1 = complete_states[i]
                    state2 = complete_states[j]

                    pair = frozenset([state1, state2])

                    if pair in marked:
                        continue

                    for symbol in alphabet:
                        next1 = complete_transitions[(state1, symbol)]
                        next2 = complete_transitions[(state2, symbol)]

                        if next1 == next2:
                            continue

                        next_pair = frozenset([next1, next2])

                        if next_pair in marked:
                            marked.add(pair)
                            changed = True
                            break

        # az ekvivalens allapotok osszevonasa
        groups = []

        for state in complete_states:
            found = False

            for group in groups:
                representative = group[0]

                pair = frozenset([state, representative])

                if pair not in marked:
                    group.append(state)
                    found = True
                    break

            if not found:
                groups.append([state])

        # minden eredeti allapothoz hozzarendeljuk az osszevont allapot nevet
        state_names = {}

        for group in groups:
            original_states = [
                state for state in group
                if state != trap_state
            ]

            if not original_states:
                continue

            # a legkisebb eredeti allapot neve marad meg
            smallest = min(
                original_states,
                key=lambda state: (
                    int(state[1:]) if state[1:].isdigit()
                    else float('inf'),
                    state
                )
            )

            new_name = "s" + smallest[1:]

            for state in group:
                state_names[state] = new_name

        # az uj allapotok meghatarozasa
        new_states = []

        for state in states:
            name = state_names[state]

            if name not in new_states:
                new_states.append(name)

        # az uj kezdoallapot
        new_start_state = state_names[start_state]

        # az uj vegallapotok
        new_final_states = []

        for state in final_states:
            name = state_names[state]

            if name not in new_final_states:
                new_final_states.append(name)

        # az uj atmenetek meghatarozasa
        new_transitions = set()

        for (from_state, symbol), to_state in transitions.items():
            new_from = state_names[from_state]
            new_to = state_names[to_state]

            new_transitions.add((new_from, symbol, new_to))

        # allapotok rendezese
        def state_key(state):
            if state[1:].isdigit():
                return (0, int(state[1:]))
            return (1, state)

        new_states.sort(key=state_key)
        new_final_states.sort(key=state_key)

        # atmenetek rendezese
        sorted_transitions = sorted(
            new_transitions,
            key=lambda t: (
                state_key(t[0]),
                t[1],
                state_key(t[2])
            )
        )

        # eredmeny kiirasa
        with open(output_file, 'w') as f:
            f.write(" ".join(new_states) + "\n")
            f.write(" ".join(sorted(alphabet)) + "\n")
            f.write(new_start_state + "\n")
            f.write(" ".join(new_final_states) + "\n")

            for from_state, symbol, to_state in sorted_transitions:
                f.write(
                    f"{from_state} {symbol} {to_state}\n"
                )
