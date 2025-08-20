# This file is part of Octopus Sensing <https://octopus-sensing.nastaran-saffar.me/>
# Copyright © Nastaran Saffaryazdi 2020
#
# Octopus Sensing is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
#  either version 3 of the License, or (at your option) any later version.
#
# Octopus Sensing is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Octopus Sensing.
# If not, see <https://www.gnu.org/licenses/>.

import threading
import csv
import sys
import os
from typing import List, Optional, Any, Dict
import socket
import json
import time

from octopus_sensing.common.message_creators import MessageType
from octopus_sensing.devices.realtime_data_device import RealtimeDataDevice
from octopus_sensing.devices.common import SavingModeEnum


class MuseAthenaStreaming(RealtimeDataDevice):
    '''
    Get and Record data from a Muse s Athena headband stream.
    It needs the custom muse android app to be running on the phone and
    streaming data to the specified port.
    It uses the socket to connect to the app and receive data.

    Attributes
    ----------

    Parameters
    ----------
    
    name: str
          device name
          This name will be used in the output path to identify each device's data

    port: int
            The port number to listen for incoming data.
    
    host: str
            The host IP address to listen for incoming data.
            default value is 0.0.0.0
    sampling_rate: int
            The sampling rate of the data stream.
    
    output_path: str, optional
            The path for recording files.
            Recorded file/files will be in folder {output_path}/{name}
    
    saving_mode: SavingModeEnum, optional
            The saving mode for the recorded data.
            It can be either `SavingModeEnum.CONTINIOUS_SAVING_MODE` or `SavingModeEnum.SEPARATED_SAVING_MODE`.
    channels: Optional[list], optional
            A list of channels to record. If None, all channels will be recorded.

    Example
    -------
    Creating an instance of socket streaming recorder and adding it to the device coordinator.
    Device coordinator is responsible for triggerng the device to start or stop recording

    >>> muse = MuseAthenaStreaming("muse",
                                   5500, 
                                   250,
    ...                            output_path="output")
    >>> device_coordinator.add_device(muse)

    See Also
    -----------
    :class:`octopus_sensing.device_coordinator`
    :class:`octopus_sensing.devices.device`

    '''

    def __init__(self,
                 name: str,
                 port: int,
                 sampling_rate: int,
                 host: str = "0.0.0.0",
                 output_path: str = "output",
                 saving_mode: int=SavingModeEnum.CONTINIOUS_SAVING_MODE,
                 channels: Optional[list] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self._name = name
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen(1)
        self.conn, addr = sock.accept()
        print(f"Client connected: {addr}")

        self._stream_data: List[Dict[str, Any]] = []
        
        self._terminate = False
        self._state = ""
        self._experiment_id = None
        self.sampling_rate = sampling_rate
        self.channels = channels
        self._trigger = None
        self._saving_mode = saving_mode

        self.output_path = os.path.join(output_path, self._name)
        os.makedirs(self.output_path, exist_ok=True)

    def _run(self):
        '''
        Listening to the message queue and manage messages
        '''
        print("in muse athena streaming _run")
        self._loop_thread = threading.Thread(target=self._stream_loop)
        self._loop_thread.start()


        while True:
            message = self.message_queue.get()
            if message is None:
                continue

            if message.type == MessageType.START:
                if self._state == "START":
                    print(f"Muse Device: '{self.name}' has already started.")
                else:
                    print(f"Muse Device: '{self.name}' started.")
                    self._experiment_id = message.experiment_id
                    self.__set_trigger(message)
                    self._state = "START"

            elif message.type == MessageType.STOP:
                if self._state == "STOP":
                    print(f"Muse Device '{self.name}' has already stopped.")
                else:
                    print(f"Muse Device '{self.name}' stopped.")
                    if self._saving_mode == SavingModeEnum.SEPARATED_SAVING_MODE:
                        self._experiment_id = message.experiment_id
                        file_name = \
                            "{0}/{1}-{2}-{3}.csv".format(self.output_path,
                                                        self.name,
                                                        self._experiment_id,
                                                        message.stimulus_id)
                        self._save_to_file(file_name)
                        self._stream_data = []
                    else:
                        self._experiment_id = message.experiment_id
                        self.__set_trigger(message)
                    self._state = "STOP"              
            elif message.type == MessageType.SAVE:
                if self._saving_mode == SavingModeEnum.CONTINIOUS_SAVING_MODE:
                    self._experiment_id = message.experiment_id
                    file_name = \
                        "{0}/{1}-{2}.jsonl".format(self.output_path,
                                                 self.name,
                                                 self._experiment_id)
                    self._save_to_file(file_name)
                    self._stream_data = []
            elif message.type == MessageType.TERMINATE:
                self._terminate = True
                if self._saving_mode == SavingModeEnum.CONTINIOUS_SAVING_MODE:
                    file_name = \
                        "{0}/{1}-{2}.jsonl".format(self.output_path,
                                                 self.name,
                                                 self._experiment_id)
                    self._save_to_file(file_name)
                break

        self._loop_thread.join()

    def _stream_loop(self):
        buffer = b''
        while True:
            if self._terminate is True:
                print("connection closed")
                self.conn.close()
                break
                    
            data = self.conn.recv(1)
            if not data:
                break

            buffer += data
            # Split messages by newline (assuming each JSON object ends with '\n')
            if buffer.endswith(b'\n'):
                json_data = json.loads(buffer[:-1])
                print(json_data)
                buffer = b''
                # Add timestamp to the JSON data
                json_data['timestamp'] = (time.time() * 1000)

                self._stream_data.append(json_data)
                if self._trigger is not None:
                    trigger = {"marker": self._trigger}
                    self._stream_data.append(trigger)
                    self._trigger = None

    def __set_trigger(self, message):
        '''
        Takes a message and set the trigger using its data

        Parameters
        ----------
        message: Message
            a message object
        '''
        # Add the trigger to the data
        self._trigger = \
            f"{message.type}-{message.experiment_id}-{str(message.stimulus_id).zfill(2)}"

    def _save_to_file(self, file_name):
        print(f"Saving {self._name} to file {file_name} ...")
        with open(file_name, "a") as f:
            for obj in self._stream_data:
                f.write(json.dumps(obj) + "\n")
        print(f"Saving {self._name} to file {file_name} is done." )

    def _get_realtime_data(self, duration: int) -> Dict[str, Any]:
            '''
            Returns n seconds (duration) of latest collected data for monitoring/visualizing or
            realtime processing purposes.

            Parameters
            ----------
            duration: int
                A time duration in seconds for getting the latest recorded data in realtime

            Returns
            -------
            data: Dict[str, Any]
                The keys are `data` and `metadata`.
                `data` is a list of records, or empty list if there's nothing.
                `metadata` is a dictionary of device metadata including `sampling_rate` and `channels` and `type`

            '''
            # Last seconds of data

            raise NotImplementedError("Realtime data retrieval is not implemented for MuseAthenaStreaming.")
