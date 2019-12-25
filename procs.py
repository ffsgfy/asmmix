import random
import itertools
import collections

try:
    import prefs
except ImportError:
    from . import prefs


class Action:
    class Output:
        def __init__(self, buffer):
            self.buffer = buffer

        def act(self, *, buffer, **kwargs):
            buffer.extend(self.buffer)

    class StackPop:
        def __init__(self, stop=1):
            self.stop = 1  # can be an int or one or more Mode types

        def act(self, *, stack, **kwargs):
            try:
                if isinstance(self.stop, int):
                    for _ in range(self.stop):
                        stack.pop()
                else:
                    while not isinstance(stack[-1], self.stop):
                        stack.pop()
            except IndexError:
                pass

    class StackPush:
        def __init__(self, item):
            self.item = item

        def act(self, *, stack, **kwargs):
            stack.append(self.item)

    class Reprocess:
        def __init__(self, item):
            self.item = item

        def act(self, *, buffer, stack, **kwargs):
            if stack:
                for action in stack[-1].process(self.item):
                    action.act(buffer=buffer, stack=stack)


class Mode:
    class WaitFunctionComment:
        PATTERN = "# -- Begin function "

        def process(self, line):
            actions = [Action.Output((line,))]

            pattern = line.find(self.PATTERN)
            if pattern != -1:
                function = line[pattern + len(self.PATTERN):]
                if prefs.should_process(function):
                    actions.append(Action.StackPush(Mode.WaitFunctionLabel(function)))

            return actions

    class WaitFunctionLabel:
        def __init__(self, function):
            self.function = function

        def process(self, line):
            actions = [Action.Output((line,))]

            if line.startswith(f"{self.function}:") or line.startswith(f"\"{self.function}\":"):
                actions.append(Action.StackPop())
                actions.append(Action.StackPush(Mode.SkipFunctionPrologue()))

            return actions

    class SkipFunctionPrologue:
        def process(self, line):
            if line[0].isspace():  # skip all lines that don't begin with a space/tab
                return [Action.StackPop(), Action.StackPush(Mode.ProcessFunction()), Action.Reprocess(line)]
            return [Action.Output((line,))]

    class ProcessFunction:
        LABEL_COUNT = itertools.count()

        def __init__(self):
            self.buffers = [collections.deque()]
            self.labels = [""]  # first label will never be used

        def label(self):
            return prefs.LABEL_TEMPLATE.format(next(self.LABEL_COUNT))

        def process_buffers(self):
            self.buffers = list(filter(lambda x: len(x) > 0, self.buffers))

            if len(self.buffers) > 3:
                for i, buffer in enumerate(self.buffers[:-1]):
                    buffer.append(f"\tjmp {self.labels[i + 1]}")

                buffers = self.buffers[1:-1]
                random.shuffle(buffers)
                self.buffers[1:-1] = buffers

        def process(self, line):
            if line.endswith("# -- End function"):
                self.process_buffers()
                buffer = []
                buffer.extend(itertools.chain(*self.buffers))
                buffer.append(line)
                return [Action.Output(buffer), Action.StackPop()]
            else:
                if random.random() < prefs.P_INSERT_PLAIN:
                    self.buffers[-1].extend(prefs.insert_plain())

                if random.random() < prefs.P_INSERT_JUMP:
                    label = self.label()
                    self.buffers[-1].append(f"\tjmp {label}")
                    self.buffers[-1].extend(prefs.insert_jump())
                    self.buffers[-1].append(f"{label}:")

                if line[0] == "." and line[-1] == ":":
                    if random.random() < prefs.P_SPLIT:
                        self.buffers.append(collections.deque())
                        self.labels.append(line[:-1])

                self.buffers[-1].append(line)
                return []


def process_lines(lines_in):
    lines_out = []
    mode_stack = [Mode.WaitFunctionComment()]

    for line in lines_in:
        line = line.rstrip()
        for action in mode_stack[-1].process(line):
            action.act(buffer=lines_out, stack=mode_stack)

    return lines_out


def process_file(path_in, path_out=None):
    with open(path_in, "r") as file:
        lines_in = file.readlines()

    lines_out = process_lines(lines_in)
    path_out = path_out or path_in

    with open(f"{path_out}", "w") as file:
        file.write("\n".join(lines_out))

    return path_out
