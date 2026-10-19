
from project.problem import Problem

import argparse


class DeterminizationProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            '--det',
            action='store_true',
            help='determinize the automaton'
        )

    def is_chosen_problem(self, args):
        return args.det

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

            if (from_state, symbol) not in transitions:
                transitions[(from_state, symbol)] = set()

            transitions[(from_state, symbol)].add(to_state)

        # determinizalas
        new_states = [frozenset([start_state])]
        new_transitions = {}
        new_final_states = []

        i = 0

        while i < len(new_states):
            current_states = new_states[i]

            for symbol in sorted(alphabet):
                next_states = set()

                for state in current_states:
                    if (state, symbol) in transitions:
                        next_states.update(
                            transitions[(state, symbol)]
                        )

                if not next_states:
                    continue

                next_states = frozenset(next_states)

                if next_states not in new_states:
                    new_states.append(next_states)

                j = new_states.index(next_states)

                new_transitions[(f"s{i}", symbol)] = f"s{j}"

            i += 1

        # vegallapotok meghatarozasa
        for i in range(len(new_states)):
            for state in new_states[i]:
                if state in final_states:
                    new_final_states.append(f"s{i}")
                    break

        # eredmeny kiirasa
        with open(output_file, 'w') as f:
            f.write(" ".join(
                f"s{i}" for i in range(len(new_states))
            ) + "\n")

            f.write(" ".join(sorted(alphabet)) + "\n")
            f.write("s0\n")
            f.write(" ".join(new_final_states) + "\n")

            for i in range(len(new_states)):
                for symbol in sorted(alphabet):
                    if (f"s{i}", symbol) in new_transitions:
                        f.write(
                            f"s{i} {symbol} "
                            f"{new_transitions[(f's{i}', symbol)]}\n"
                        )
