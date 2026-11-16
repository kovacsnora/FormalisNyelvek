from project.problem import Problem

import argparse
import re

class RegexProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            '--rgx',
            type=int,
            choices=[1, 2, 3, 4, 5],
            help='regex feladat szama'
        )

    def is_chosen_problem(self, args):
        return args.rgx is not None

    def run(self, args):
        input_file = args.input
        output_file = args.output

        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # a logcat sorok feldolgozasahoz hasznalt regex
        pattern = (
            r'^([0-9]{2}-[0-9]{2}) '
            r'([0-9]{2}:[0-9]{2}:[0-9]{2})\.[0-9]+'
            r'\s+([0-9]+)\s+([0-9]+)'
            r'\s+([IDVEFAW])\s+(.+?):\s*(.*)$'
        )

        results = []

        # 1. feladat - sorok megszamlalasa
        if args.rgx == 1:

            patterns = [
                r'^10-15\s',
                r'^10-15 10:18:51\.',
                r'^[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:51\.',
                r'^[0-9]{2}-[0-9]{2} .*?\s+lowmemorykiller:',
                r'^10-15 10:18:51\.\d+\s+221\s+\d+\s+',
                r'^[0-9]{2}-[0-9]{2} .*?\s+E\s+[^:]+:',
                r'^[0-9]{2}-[0-9]{2} .*?\s+W\s+PackageManager:',
                r'^[0-9]{2}-[0-9]{2} .*?\s+D\s+[^:]*ExoPlayer[^:]*:',                r'^[0-9]{2}-[0-9]{2} .*?\s+[EW]\s+[^:]+:.*\.java:',
                r'^[0-9]{2}-[0-9]{2} .*?\s+[IDVEFAW]\s+[^:]+:.*\bThread\b'            ]

            for regex in patterns:
                count = 0

                for line in lines:
                    if re.search(regex, line):
                        count += 1

                results.append(str(count))

        # 2. feladat - java fajlnevek a hibasorokbol
        elif args.rgx == 2:

            for line in lines:
                match = re.match(pattern, line)

                if match and match.group(5) == 'E':
                    message = match.group(7)

                    java_files = re.findall(
                        r'([A-Za-z0-9_$-]+\.java):[0-9]+',
                        message
                    )

                    for java_file in java_files:
                        results.append(java_file)

        # 3. feladat - kulonbozo process id-k
        elif args.rgx == 3:

            process_ids = set()

            for line in lines:
                match = re.match(pattern, line)

                if match:
                    pid = match.group(3)

                    if pid not in process_ids:
                        process_ids.add(pid)
                        results.append(pid)

        # 4. feladat - legtobb hibaval rendelkezo process
        elif args.rgx == 4:

            error_counts = {}

            for line in lines:
                match = re.match(pattern, line)

                if match and match.group(5) == 'E':
                    pid = match.group(3)

                    if pid not in error_counts:
                        error_counts[pid] = 0

                    error_counts[pid] += 1

            max_pid = None
            max_errors = 0

            for pid in error_counts:
                if error_counts[pid] > max_errors:
                    max_errors = error_counts[pid]
                    max_pid = pid

            if max_pid is not None:
                results.append(
                    f"PID={max_pid} ({max_errors} errors)"
                )

        # 5. feladat - foszalon tortent hibak szama
        elif args.rgx == 5:

            count = 0

            for line in lines:
                match = re.match(pattern, line)

                if match:
                    pid = match.group(3)
                    tid = match.group(4)
                    level = match.group(5)

                    if level == 'E' and pid == tid:
                        count += 1

            results.append(str(count))

        # eredmeny kiirasa
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(result + '\n')
