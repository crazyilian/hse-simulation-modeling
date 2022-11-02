import simpy
import random
from enum import Enum

EPSILON = 1e-9


class States(Enum):
    NOT_ENTERED_VIEW = 0
    MOVING = 1  # A1
    STANDING = 2  # A2
    MOVING_IN_LINE = 3  # A3
    STANDING_IN_LINE = 4  # A4
    LEFT_VIEW = 5


class Events(Enum):
    ENTER_VIEW = 0  # E1
    LEAVE_TO_SERVICE_ZONE = 1  # E2
    LEAVE_VIEW = 2  # E3

    GET_IN_MIDDLE_OF_LINE = 3  # E4
    GET_IN_END_OF_LINE = 4  # E5
    GET_OUT_OF_LINE = 5  # E6

    START_MOVING = 6  # E7
    STOP_MOVING = 7  # E8

    START_MOVING_IN_LINE = 8  # E9
    STOP_MOVING_IN_LINE = 9  # E10

    GET_IN_LINE_STANDING = 10  # E11
    GET_OUT_OF_LINE_STANDING = 11  # E12

    CONTINUE_STANDING = 12  # E01
    CONTINUE_MOVING = 13  # E02
    CONTINUE_STANDING_IN_LINE = 14  # E03
    CONTINUE_MOVING_IN_LINE = 15  # E04

    ALREADY_LEFT = 16


class Event:
    def __init__(self, probability, next_state):
        self.probability = probability
        self.next_state = next_state


def validate_state_event_graph(state_event_graph):
    for state_id, events in state_event_graph.items():
        total_probability = 0
        for event_id, event in events.items():
            total_probability += event.probability
            if event.probability < 0:
                raise Exception(f"Negative event probability: event {event_id}, state {state_id} ")
        if abs(total_probability - 1) > EPSILON:
            raise Exception(f"Total events probability isn't equal to 1: state {state_id}")


state_event_graph = {
    States.NOT_ENTERED_VIEW: {
        Events.ENTER_VIEW: Event(1, States.MOVING),
    },
    States.MOVING: {
        Events.CONTINUE_MOVING: Event(0.83, States.MOVING),
        Events.LEAVE_VIEW: Event(0.01, States.LEFT_VIEW),
        Events.GET_IN_END_OF_LINE: Event(0.1, States.MOVING_IN_LINE),
        Events.GET_IN_MIDDLE_OF_LINE: Event(0.01, States.MOVING_IN_LINE),
        Events.STOP_MOVING: Event(0.05, States.STANDING)
    },
    States.STANDING: {
        Events.CONTINUE_STANDING: Event(0.9, States.STANDING),
        Events.START_MOVING: Event(0.09, States.MOVING),
        Events.GET_IN_LINE_STANDING: Event(0.01, States.STANDING_IN_LINE),
    },
    States.MOVING_IN_LINE: {
        Events.CONTINUE_MOVING_IN_LINE: Event(0.49, States.MOVING_IN_LINE),
        Events.LEAVE_TO_SERVICE_ZONE: Event(0.01, States.LEFT_VIEW),
        Events.GET_OUT_OF_LINE: Event(0.01, States.MOVING),
        Events.STOP_MOVING_IN_LINE: Event(0.49, States.STANDING_IN_LINE)
    },
    States.STANDING_IN_LINE: {
        Events.CONTINUE_STANDING_IN_LINE: Event(0.89, States.STANDING_IN_LINE),
        Events.START_MOVING_IN_LINE: Event(0.1, States.MOVING),
        Events.GET_OUT_OF_LINE_STANDING: Event(0.01, States.STANDING)
    },
    States.LEFT_VIEW: {
        Events.ALREADY_LEFT: Event(1, States.LEFT_VIEW),
    }
}

validate_state_event_graph(state_event_graph)


class Person:
    def __init__(self, id, env, state_event_graph):
        self.id = id
        self.env = env
        self.state_event_graph = state_event_graph
        self.state = States.NOT_ENTERED_VIEW
        self.action = env.process(self.run())

    def run(self):
        while self.state != States.LEFT_VIEW:
            events = state_event_graph[self.state]
            event_id, event = random.choices(
                population=list(events.items()),
                weights=[event.probability for event in events.values()],
                k=1
            )[0]
            self.state = event.next_state
            print(f'Person {self.id}:\t\tEvent {event_id}\t\t\t\tNew state {self.state}')
            yield self.env.timeout(1)


env = simpy.Environment()
people = [Person(i, env, state_event_graph) for i in range(10)]
env.run(until=100)
