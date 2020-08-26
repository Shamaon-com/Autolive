import boto3
import time
import sys
from apscheduler.schedulers.background import BackgroundScheduler


class lifecycle_manager:
    """ state graph:
  
    NONE ------> STARTING ------> CREATED ------> RUNNING | IDLE
    |              |                |               |
    ---------- INPUT_ERROR <------ ROLLBACK         |
                                    |               |
                DELETED <------ DELETING <------ STOPPING
    
    """
    
    def __init__(self, channel):
        self.state = None
        self.stateDate = 0.0
        self.channel = channel
        self.streamKey = self.channel.input_stream_key
        self.scheduler = BackgroundScheduler()

        self.dynamodb = boto3.client('dynamodb', region_name='eu-west-1')
        self.tableName = 'notifications-dev'

        self.load_state()
    
    def load_state(self):
        """ always load last state, if there is none init state with None """

        response = self.dynamodb.query(
            TableName = self.tableName,
            KeyConditionExpression='streamKey = :streamKey',
            ExpressionAttributeValues={
                ':streamKey': {'S':self.streamKey}
            }
        )
        if response['Count'] == 0:
            self.state = "NONE"
        else:
            for item in response['Items']:
                if float(item['date']['S']) > self.stateDate:
                    self.stateDate = float(item['date']['S'])
                    self.state = item['state']['S']
        if self.state == "ROLLBACK":
            print("Channel is rolling back")
            sys.exit()
        self.load_medialive_state(self.state)
        print(self.state)

    def load_medialive_state(self, state):
        """ We will always override current state with actual medialive state """
        channelStatus = self.channel.check_status()
        if channelStatus == None:
            if state != "NONE":
                self.set_state("NONE", "state missmatch! Adopting medialive state: NONE")
        elif channelStatus == "IDLE":
                if not (state == "CREATED" or state == "STOPPED"):
                    self.set_state("CREATED", "state missmatch! Adopting medialive state: CREATED")
        elif channelStatus == "RUNNING" and not state == "RUNNING":
            self.set_state("RUNNING", "state missmatch! Adopting medialive state: RUNNING")

    def rollback(self, e):
        self.set_state("ROLLBACK", e)
        self.channel.delete_channel()
        self.set_state("NONE", "Rollback successfull")

    def evaluate_state_change(self, currentState, nextState):
        if nextState == "STARTING":
            return currentState == "NONE" and nextState
        elif nextState == "CREATED":
            return currentState == "STARTING" and nextState
        elif nextState == "RUNNING":
            return (currentState == "CREATED" or currentState == "STOPPED") and nextState
        elif nextState == "STOPPED":
            return currentState == "RUNNING" and nextState
        elif nextState == "DELETED":
            return (currentState == "STOPPED" or currentState == "CREATED") and nextState
        else:
            return False

    def set_state(self, state, message):
        print(state + " " + str(message))
        stateDate = time.time()
        response = self.dynamodb.put_item(
            TableName = self.tableName,
            Item = {
                'streamKey': {'S': self.streamKey},
                'date': {'S': str(stateDate)},
                'state': {'S': state},
                'message': {'S': message},
                'previousState': {'S': self.state}
            }
        )

        self.state = state
        self.stateDate = stateDate



"""
#TESTS
state = lifecycle_manager('test')
if state.evaluate_state_change(state.state, "DELETING"):
    state.set_state("DELETING", "Creating channel")

#state.set_state('IDLE', "channel is being created")
"""