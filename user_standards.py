import csv
import math
from scipy.stats import kendalltau
import numpy as np


def calculate_weighted_average(raw_log, standard_states, standard_weights, standards):
    """
    Calculate the weighted average Kendall Tau correlation coefficient.
    """
    weighted_average = 0
    count_nonexistent_keys = 0

    for state, weight, standard in zip(standard_states, standard_weights, standards):
        real_log = []
        for standard_key in state:
            if standard_key in raw_log:
                index = raw_log.index(standard_key)
                real_log.append(index)
            else:
                real_log.append(30)  # Default value for missing keys
                count_nonexistent_keys += 1

        correlation, _ = kendalltau(standard, real_log)
        correlation = correlation if not math.isnan(correlation) else 0
        weighted_average += correlation * weight

    weighted_average /= sum(standard_weights)
    return weighted_average, count_nonexistent_keys


def process_phase_kendall(input_file, output_file):
    """
    Process the input file to calculate Kendall Tau coefficients and write the results to the output file.
    """
    tag_counts = {
        'Basic': 255219, 'logging': 17006, 'Build Tools': 128152, 'Exception Handeling': 23114,
        'Collection': 38300, 'Design Patterns': 46017, 'SQL': 135332, 'algorithm': 35034,
        'Memory Management': 20403, 'DevOps': 86122, 'Security': 25300, 'Scala': 47012,
        'Struts': 8445, 'Spring': 161218, 'Web Programming': 141706
    }

    standard_states = [
        {'Basic': 1, 'logging': 2, 'Build Tools': 2, 'Exception Handeling': 2, 'Design Patterns': 4},
        {'Basic': 1, 'logging': 2, 'Build Tools': 2, 'Exception Handeling': 2, 'Collection': 3, 'Memory Management': 5, 'DevOps': 6, 'Security': 6, 'Scala': 7, 'Struts': 7, 'Spring': 7, 'Web Programming': 7},
        {'Basic': 1, 'logging': 2, 'Build Tools': 2, 'Exception Handeling': 2, 'Collection': 3, 'algorithm': 5},
        {'Basic': 1, 'logging': 2, 'Build Tools': 2, 'Exception Handeling': 2, 'Collection': 3, 'SQL': 5}
    ]

    standard_weights = [469508, 1051997, 496825, 597123]
    standards = [list(state.values()) for state in standard_states]

    with open(input_file, encoding='utf-8') as tsvfile:
        reader = csv.reader(tsvfile, delimiter=',')
        next(reader)  # Skip header

        user = None
        raw_log = []
        report = "user,weighted_average,count_nonexistent_keys\n"

        for line in reader:
            current_user = line[0]

            if user is None:
                user = current_user

            if user != current_user:
                weighted_avg, nonexist_keys = calculate_weighted_average(raw_log, standard_states, standard_weights, standards)
                report += f"{user},{round(weighted_avg, 2)},{nonexist_keys}\n"

                user = current_user
                raw_log.clear()

            raw_log.append(line[1])

        with open(output_file, "w") as result_file:
            result_file.write(report)


def process_phase_rw(input_file):
    """
    Process the input file to calculate and print aggregated metrics.
    """
    with open(input_file, encoding='utf-8') as tsvfile:
        reader = csv.reader(tsvfile, delimiter=',')
        next(reader)  # Skip header

        total_report = 0
        count_positive, count_negative = 0, 0
        sum_positive, sum_negative = 0, 0

        for line in reader:
            score = float(line[1])
            rep = float(line[3]) if line[3] != 'None' else 0

            total_report += score * rep

            if score > 0:
                count_positive += 1
                sum_positive += score * rep
            elif score < 0:
                count_negative += 1
                sum_negative += score * rep

        print(
            f"Overall: {total_report / (count_positive + count_negative)}\n"
            f"Positive: {sum_positive} ({count_positive})\n"
            f"Negative: {sum_negative} ({count_negative})"
        )


if __name__ == "__main__":
    process_phase_kendall("java_topic_question.csv", "userstandards5.csv")
    print("Phase Kendall completed.")

    process_phase_rw("userstandards6.csv")
    print("Phase RW completed.")
