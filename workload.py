from __future__ import print_function

import collections
import os
import sys
import time
# Import Python wrapper for or-tools CP-SAT solver.
from multiprocessing.pool import Pool

from ortools.sat.python import cp_model


def MinimalJobshopSat(input_i):
    # Create the model.
    model = cp_model.CpModel()

    # Fetching input
    input_path = 'inputs/input_group' + str(input_i) + '.txt'
    with open(input_path, 'r') as input_file:
        n = list(map(int, input_file.readline().split()))
        jobs_data = []
        for _ in range(n[0]):
            inp = input_file.readline().split()
            delay = int(inp.pop(0))
            temp = []
            for index, value in enumerate(inp):
                temp.append((index, int(value), delay))
            jobs_data.append(temp)

    machines_count = 1 + max(task[0] for job in jobs_data for task in job)
    all_machines = range(machines_count)

    # Computes horizon dynamically as the sum of all durations.
    horizon = sum(task[1] for job in jobs_data for task in job)

    # Named tuple to store information about created variables.
    task_type = collections.namedtuple('task_type', 'start end interval')
    # Named tuple to manipulate solution information.
    assigned_task_type = collections.namedtuple('assigned_task_type',
                                                'start job index duration')

    # Creates job intervals and add to the corresponding machine lists.
    all_tasks = {}
    machine_to_intervals = collections.defaultdict(list)

    for job_id, job in enumerate(jobs_data):
        for task_id, task in enumerate(job):
            machine = task[0]
            duration = task[1]
            delay = task[2]
            suffix = '_%i_%i' % (job_id, task_id)
            start_var = model.NewIntVar(delay, horizon, 'start' + suffix)
            end_var = model.NewIntVar(0, horizon, 'end' + suffix)
            interval_var = model.NewIntervalVar(start_var, duration, end_var,
                                                'interval' + suffix)
            all_tasks[job_id, task_id] = task_type(
                start=start_var, end=end_var, interval=interval_var)
            machine_to_intervals[machine].append(interval_var)

    # Create and add disjunctive constraints.
    for machine in all_machines:
        model.AddNoOverlap(machine_to_intervals[machine])

    # Precedences inside a job.
    for job_id, job in enumerate(jobs_data):
        for task_id in range(len(job) - 1):
            model.Add(all_tasks[job_id, task_id +
                                1].start >= all_tasks[job_id, task_id].end)

    # Makespan objective.
    obj_var = model.NewIntVar(0, horizon, 'makespan')
    model.AddMaxEquality(obj_var, [
        all_tasks[job_id, len(job) - 1].end
        for job_id, job in enumerate(jobs_data)
    ])
    model.Minimize(obj_var)

    class KeepBestSolution(cp_model.CpSolverSolutionCallback):
        def __init__(self):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self.__solution_count = 0
            self.__start_time = time.time()
            self.__best_obj = sys.maxsize

        def on_solution_callback(self):
            current_time = time.time()
            obj = self.ObjectiveValue()
            print('Solution for %i %i, time = %0.2f s, objective = %i' %
                  (input_i, self.__solution_count, current_time - self.__start_time, obj))
            self.__solution_count += 1

            if obj < self.__best_obj:
                # Create one list of assigned tasks per machine.
                job_starts = [[0] * n[1] for i in range(n[0])]
                for job_id, job in enumerate(jobs_data):
                    for task_id, task in enumerate(job):
                        machine = task[0]
                        job_starts[job_id][machine] = self.Value(all_tasks[job_id, task_id].start)

                # Form the output.
                # for machine in all_machines:
                #     assigned_jobs[machine].sort()
                # output = []
                # final_result = []
                # for jobs in assigned_jobs.values():
                #     output.append(jobs)
                # for i in range(len(output[0])):
                #     temp = []
                #     for j in range(len(output)):
                #         temp.append(output[j][i].start)
                #     final_result.append(temp)

                # Finally print the solution found.
                out_path = 'verification_outputs' + os.sep + 'output_from_20_to_%i.txt' % input_i
                with open(out_path, 'w') as output_file:
                    output_file.write(str(int(self.ObjectiveValue())))
                    output_file.write("\n")
                    for job_starts in job_starts:
                        for i, job_machine_start in enumerate(job_starts):
                            output_file.write(str(job_machine_start))
                            if i != n[1] - 1:
                                output_file.write(" ")
                        output_file.write("\n")

    solver = cp_model.CpSolver()
    solution_callback = KeepBestSolution()
    status = solver.SolveWithSolutionCallback(model, solution_callback)


if __name__ == "__main__":
    # pashm = [20, 22, 25]
    # sangin = [21, 23, 24, 26, 27, 28, 29, 30, 34]
    with Pool(3) as pool:
        list(pool.imap_unordered(MinimalJobshopSat, [20,22,25]))
