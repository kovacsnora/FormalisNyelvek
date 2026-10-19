from project.problem import Problem

import argparse


class DFAProblem(Problem):
 
    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            '--check',
            help='check words with the DFA'
        )

    def is_chosen_problem(self, args):
        return args.check is not None

    def run(self, args):
        input_file = args.input
        output_file = args.output

        with open(input_file, 'r') as f:
            lines = f.readlines()

        states = lines[0].split() 
        alphabet = lines[1].split() 
        start_state = lines[2].strip()
        final_states = lines[3].split()

        #az atmeneteket egy dictionary-be tesszuk
        transitions = {}

        for line in lines[4:]:
            parts = line.split()

            from_state = parts[0]
            symbol = parts[1]
            to_state = parts[2]

            transitions[(from_state, symbol)] = to_state

        words = args.check.split(',')

        results = []

        for word in words:
            current_state = start_state
            accepted = True

            for symbol in word:

                if (current_state, symbol) not in transitions:
                    accepted = False
                    break

                current_state = transitions[(current_state, symbol)]

            if accepted and current_state in final_states:
                result = "IGEN"
            else:
                result = "NEM"

            results.append(result)

        with open(output_file, 'w') as f:
            f.write("\n".join(results))