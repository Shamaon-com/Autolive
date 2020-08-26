import argparse
import boto3
import sys
import json

from .channel import Channel
from .ladder_generator import Ladder_generator
from .errors import MissingStreamError, WrongCodecError
from .lifecycle_manager import lifecycle_manager
from .cli_parser import parse_data




    
def main():

    MAIN_MESSAGE = "Cli utility to automate AWS Medialive channel creation deletion"

    parser = argparse.ArgumentParser(description=MAIN_MESSAGE)
    
    # Add arguments
    parser.add_argument('--action', action='store', type=str, required=True, choices=['Create', 'Delete', 'Start', 'Stop'])
    parser.add_argument('--key', type=str, required=True)
    parser.add_argument('--input', type=str, choices=['Pull', 'Push'])
    parser.add_argument('--debug', type=bool)
    parser.add_argument('--data', type=str, action='store', nargs=2)

    args = parser.parse_args()
    channel = Channel(args.key, args.debug)
    state = lifecycle_manager(channel)

    if args.action == "Create":
        if args.data == None:
            parser.error("Action \"Create\" needs --data flag. Check -h or --help for more info.")
        if args.input == None:
            args.input = "Pull"
        try:
            processedData = parse_data(args.data[0], args.data[1]).data
            if state.evaluate_state_change(state.state, "STARTING"):
                state.set_state("STARTING", "input was detected")
        except Exception as e:
            state.set_state("INPUT_ERROR", "there was an error while processing input:{e}".format(e=e))
            sys.exit()
        if state.evaluate_state_change(state.state, "CREATED"):
            try:
                channel.create_channel_input(args.input)
                channel.set_ladder(processedData)
                channel.create_channel()
                state.set_state("CREATED", "channel was created succesfully")
            except Exception as e:
                state.rollback(str(e))
                sys.exit()

        if state.evaluate_state_change(state.state, 'RUNNING'):
            try:
                channel.start_channel()
                state.set_state("RUNNING", "channel is running")
            except Exception as e:
                state.rollback(str(e))
                sys.exit()

    elif args.action == "Start":
        if state.evaluate_state_change(state.state, "RUNNING"):
            try:
                channel.start_channel()
                state.set_state("RUNNING", "channel is running")
            except Exception as e:
                state.rollback(str(e))
                sys.exit()

    elif args.action == "Stop":
        if state.evaluate_state_change(state.state, "STOPPED"):
            try:
                channel.stop_channel()
                state.set_state("STOPPED", "channel is stopped")
            except Exception as e:
                print(e)
                sys.exit()

    elif args.action == "Delete":
        if state.evaluate_state_change(state.state, "STOPPED"):
            channel.stop_channel()
            state.set_state("STOPPED", "channel is stopped")
        if state.evaluate_state_change(state.state, "DELETED"):
            channel.delete_channel()
            state.set_state("DELETED", "channel is deleted")
