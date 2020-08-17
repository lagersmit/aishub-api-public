"""
=======================================================================
aishub.api.py
Template version: 1.0
Created by ferdi.stoeltie at 14-8-2020
Company information:
Company name: Lagersmit
Company Address: Nieuwland Parc 306, 2952 DD Alblasserdam

  _                                         _ _
 | |                                       (_) |
 | |     __ _  __ _  ___ _ __ ___ _ __ ___  _| |_
 | |    / _` |/ _` |/ _ \ '__/ __| '_ ` _ \| | __|
 | |___| (_| | (_| |  __/ |  \__ \ | | | | | | |_
 |______\__,_|\__, |\___|_|  |___/_| |_| |_|_|\__|
               __/ |
              |___/
This file retrieves AIS records using the AISHub API
For more information about the API calls see: http://www.AISHub.net/api

Software licensed under: GNU GPLv3
=======================================================================
"""

import requests
import logging
import json
import xml.etree.ElementTree as ET
import pandas as pd
from io import StringIO
import zipfile
import io
import gzip
import bz2
from dataclasses import dataclass
from enum import Enum


class Format(Enum):
    AIS = 0
    HUMAN_READABLE = 1


class Output(Enum):
    JSON = 'json'
    XML = 'xml'
    CSV = 'csv'


class Compress(Enum):
    OFF = 0
    ZIP = 1
    GZIP = 2
    BZIP2 = 3


@dataclass
class AISHubApiConfig:
    """
    This dataclass is used to build a correct configuration to make requests
    to the AISHub api. All api settings are supported.

    Attributes
    ------------
    username : str
        Username as received by AISHub
    format : Format
        Format of the received data (AIS or Human-readable)
    output : Output
        Output format for the received data (xml, json, csv)
    compress : Compress
        Compression to receive the data in (no compression, zip, gzip, bzip2)

    Methods
    ------------
    dict()
        Returns a dictionary containing the configuration settings
    """
    username: str
    format: Format
    output: Output
    compress: Compress

    def __init__(self, username: str,
                 format: Format = Format.HUMAN_READABLE,
                 output: Output = Output.JSON,
                 compress: Compress = Compress.OFF) -> None:
        """
        Parameters
        ----------
        username : str
            Username as received by AISHub
        format : Format
            Format of the received data (AIS or Human-readable)
        output : Output
            Output format for the received data (xml, json, csv)
        compress : Compress
            Compression to receive the data in (no compression, zip, gzip, bzip2)
        """

        self.username = username
        self.format = format
        self.output = output
        self.compress = compress

    def dict(self) -> dict:
        """
        Method to return a dictionary of the configuration fields.
        :return:
            Returns a dictionary containing the configuration settings.
        """
        return {'username': self.username,
                'format': self.format.value,
                'output': self.output.value,
                'compress': self.compress.value}


def api_request(p) -> str:
    """
    Attempts to make an API request to AISHub. It returns a decompressed
    string.
    :param p:
        The configuration parameters used in the HTTP get request
    :return:
        A decompressed string or an empty string if the function failed.
    """
    ws_url = "http://data.AISHub.net/ws.php"

    try:
        r = requests.get(ws_url, params=p)
        return response_parser(p['compress'],
                               r.content)
    except requests.URLRequired as ur:
        logging.getLogger(__name__).error(ur)
        return ''
    except requests.ConnectionError as ce:
        logging.getLogger(__name__).error(ce)


def response_parser(compress: int, buffer: bytes) -> str:
    """
    Attempts to decompress the buffer using the specified Compress method.
    If the buffer uses a different compression an exception will be raised.
    :param compress:
        Compression type of the buffer (none, zip, gzip, bzip2)
    :param buffer:
        The buffer containing data received from AISHub when making an api
        request.
    :return:
        Returns a decompressed and decoded message as a string. The string
        can contain csv, xml or json data depending on the what type was
        requested.
    """

    def decompress_zip(x):
        z = zipfile.ZipFile(io.BytesIO(x))
        return z.read(z.infolist()[0])

    compress_type = {
        0: lambda x: x,
        1: lambda x: decompress_zip(x),
        2: lambda x: gzip.decompress(x).decode('utf-8'),
        3: lambda x: bz2.decompress(x).decode('utf-8')
    }

    logging.getLogger(__name__).debug('Decompressing response: {}.'.format(
        buffer))

    return compress_type.get(compress)(buffer)


def retrieve_vessel_record(cfg: AISHubApiConfig, mmsi=None, imo=None) -> \
        str:
    """
    Makes a request through the AISHub API for a single vessel.
    :param cfg:
        AISHub API Configuration to be used when making the api request.
    :param mmsi:
        MMSI of the vessel that is requested (either MMSI or IMO required).
    :param imo:
        IMO of the vessel that is requsted (either IMO or MMSI required).
    :return:
        Returns a string in the desired output type (xml, json or
        csv) and format (AIS or human-readable). If the request failed,
        an empty string is returned instead.
    """
    try:
        ship_id = {'mmsi': mmsi} if mmsi is not None else {'imo': imo}
        if ship_id is None:
            raise TypeError(
                'Ship id is invalid (None). mmsi or imo should be set.')
        return api_request({**cfg.dict(), **ship_id})
    except TypeError as te:
        logging.getLogger(__name__).error(te)
        return ''


def retrieve_vessels_in_area(cfg, latmin=-90, latmax=90, lonmin=-180,
                             lonmax=180) -> str:
    """
    Retrieves vessels in a specified area.
    :param cfg:
        AISHub API Configuration to be used when making the api request.
    :param latmin:
        >=-90
    :param latmax:
        <=90
    :param lonmin:
        >=-180
    :param lonmax:
        <=180
    :return:
        Returns a string in the desired output type (xml, json or
        csv) and format (AIS or human-readable). If the request failed,
        an empty string is returned instead.
    """
    try:
        if latmin < -90 or latmax > 90 or lonmin < -180 or lonmax > 180:
            raise ValueError(
                'Please set latitude and longitude parameters in valid range '
                '(>=-90, <=90, >=-180, <=180)')
        vs_area = {
            'latmin': latmin,
            'latmax': latmax,
            'lonmin': lonmin,
            'lonmax': lonmax
        }
        return api_request({**cfg.dict(), **vs_area})
    except ValueError as ve:
        logging.getLogger(__name__).error(ve)
        return ''


def retrieve_vessel_records(cfg):
    """
    Makes a request through the AISHub API for all vessels.
    :param cfg:
        AISHub API Configuration to be used when making the api request.
    :return:
        Returns a string in the desired output type (xml, json or
        csv) and format (AIS or human-readable). If the request failed,
        an empty string is returned instead.
    """
    return api_request(cfg.dict())


@dataclass
class ApiResponseHeader:
    """
    The AISHub API Response header. Note that if output type is csv,
    no response header is returned.
    """
    ERROR: bool
    USERNAME: str
    FORMAT: str
    RECORDS: int
    ERROR_MESSAGE: str

    def __init__(self, ERROR: bool, USERNAME: str, FORMAT: str, RECORDS:
    int, ERROR_MESSAGE: str = '') -> None:
        """
        
        :param ERROR: 
            False if there was no error. True if there was
        :param USERNAME: 
            Returned username as passed when the AISHub API request was made.
        :param FORMAT: 
            Format of the retrieved data (can be AIS or human-readable).
        :param RECORDS: 
            The amount of vessel records that are contained 
            in the retrieved message. Not available when ERROR is true.
        """
        self.ERROR = ERROR
        self.USERNAME = USERNAME
        self.FORMAT = FORMAT
        self.RECORDS = RECORDS
        self.ERROR_MESSAGE = ERROR_MESSAGE


@dataclass
class AISHubMessage:
    """
    Container for an AISHub Message that has been parsed. Contains a header
    and content section.
    """
    header: ApiResponseHeader
    content: pd.DataFrame

    def __init__(self, header: ApiResponseHeader,
                 content: pd.DataFrame) -> None:
        """
        Constructor for a parsed AISHubMessage
        :param header:
            The ApiResponseHeader.
        :param content:
            The content that was returned in the response as a pandas
            DataFrame. Empty DataFrame if no vessel records are in the
            response.
        """
        self.header = header
        self.content = content


def parse_message(message: str, output: Output=Output.JSON) -> AISHubMessage:
    """
    This function can parse the received message as returned by one of the
    api call functions. It supports multiple vessels and all output formats.
    It returns a pandas dataframe where the rows are vessels.
    valid api response message as the message parameter. If the returned
    dataframe is empty, it is recommended to check the header fields for a
    possible error.
    :param output:
        Output format that the message was received in (xml, csv or json)
    :param message:
        The message as returned by one of the three api calls.
    :return:
        Returns a pandas dataframe containing 1..n rows of vessels where
        columns are defined by the AISHub API. Values can be AIS or
        Human-readable based on the message. If there are no vessels in the
        message an empty dataframe is returned.
    """

    logging.getLogger(__name__).debug('decompressed message to parse:{}'
                                      .format(message))

    def parse_json(m):
        m = json.loads(m)
        error = m[0]['ERROR']
        username = m[0]['USERNAME']
        msg_format = m[0]['FORMAT']
        records = m[0]['RECORDS'] if 'RECORDS' in m[0] else 0
        error_message = m[0]['ERROR_MESSAGE'] if m[0]['ERROR'] is True else ''
        arh = ApiResponseHeader(error, username, msg_format, records,
                                error_message)
        frame = pd.DataFrame(m[1] if len(m) > 1 else None)
        return AISHubMessage(arh, frame)

    def parse_xml(m):

        def iter_vessels(vessels):
            for v in vessels.iter('vessel'):
                vessel_dict = v.attrib.copy()
                yield vessel_dict

        m = ET.fromstring(m)
        error = True if m.attrib['ERROR'] == 'true' else False
        username = m.attrib['USERNAME']
        msg_format = m.attrib['FORMAT']
        records = m.attrib['RECORDS'] if 'RECORDS' in m.attrib else 0
        error_message = m[0].text if m.attrib['ERROR'] == 'true' else ''
        arh = ApiResponseHeader(error, username, msg_format, records,
                                error_message)
        if error is False:
            return AISHubMessage(arh, pd.DataFrame(list(iter_vessels(m))))
        else:
            return AISHubMessage(arh, pd.DataFrame())

    def parse_csv(m):
        pd_read = pd.read_csv(StringIO(m), sep=',')
        if len(pd_read.index) == 1:
            return AISHubMessage(ApiResponseHeader(True, '', '', 0, m),
                                 pd.DataFrame())
        return AISHubMessage(ApiResponseHeader(False, '', '',
                                               len(pd_read.index), ''),
                             pd_read)

    output_type = {
        Output.JSON: parse_json,
        Output.XML: parse_xml,
        Output.CSV: parse_csv
    }
    return output_type.get(output)(message)