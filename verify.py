import os
import re


def verify(out_i, diagram):
    from_i, to_i = out_i
    out_path = file_name(out_i)
    durations = []
    starts = []
    with open('inputs/input_group%s.txt' % to_i, 'r') as input_file:
        n, m = map(int, input_file.readline().split())
        for i in range(n):
            w_in = list(map(int, input_file.readline().split()))
            starts.append(w_in[0])
            durations.append(w_in[1:])
    w_outs_list = []
    with open(out_path, 'r') as output_file:
        load_time = int(output_file.readline())
        for i in range(n):
            w_outs_list.append(list(map(int, output_file.readline().split())))
    machine_ranges = [[] for k in range(m)]
    machine_tasks = [[] for k in range(m)]
    for i in range(n):
        w_outs = w_outs_list[i]
        for w_out in w_outs:
            if w_out < starts[i]:
                return False
        w_ranges = []
        for j in range(m):
            w_out = w_outs[j]
            w_range = set(range(w_out, w_out + durations[i][j]))
            machine_ranges[j].append(w_range)
            machine_tasks[j].append((i, w_out, durations[i][j]))
            w_ranges.append(w_range)
        for w_range1_i, w_range1 in enumerate(w_ranges):
            for w_range2_i, w_range2 in enumerate(w_ranges):
                if w_range2 is not w_range1:
                    if w_range1.intersection(w_range2):
                        return False
    for machine in machine_ranges:
        for w_range1 in machine:
            for w_range2 in machine:
                if w_range2 is not w_range1:
                    if w_range1.intersection(w_range2):
                        return False
    all_task_time = []
    for machine in machine_ranges:
        [all_task_time.extend(w_range) for w_range in machine]
    if max(all_task_time) + 1 != load_time:
        return False

    if diagram:
        for machine_i in range(m):
            machine_tasks[machine_i].sort()
            print(f'\x1b[1;30;41m{str.center(f"machine {machine_i}", 20, " ")}:\x1b[0m', end='')
            for task in machine_tasks[machine_i]:
                print_task(task)
        # for machine_i in range(m):
        #     for i in range(n):
        #         s=w_outs_list[i][machine_i]
        #         dur=durations[i][machine_i]
        #         for j in range(s,s+dur)
        #         machine[machine_i]=
    return True


def file_name(out_i):
    return 'verification_outputs' + os.sep + "output_from_%s_to_%s.txt" % out_i


def print_task(machine_task):
    i, start, dur = machine_task
    c_s = f'\x1b[6;30;{41 + i}m'
    c_e = '\x1b[0m'
    task_str = c_s + str.center(f'{start}-{i}-{dur + start}', 12, " ") + c_e
    print(task_str, end='')


if __name__ == "__main__":
    outputs_path = 'verification_outputs'
    regex = r"output_from_(\d*)_to_(\d*)\.txt"
    out_indexes = [re.findall(regex, name)[0] for name in os.listdir(outputs_path)]
    for out_index in out_indexes:
        result = verify(out_index, True)
        print(file_name(out_index) + ': ' + str(result))
