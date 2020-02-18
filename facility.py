import base64
import io
import json
import mimetypes
import os
import random
import string
import time
import uuid
import zipfile
from datetime import datetime

import requests
import xmltodict
import typing
from astropy.coordinates import SkyCoord
import astropy.units as u
from django import forms
from tom_observations.facility import GenericObservationForm, GenericObservationFacility
from tom_targets.models import Target

from mastertom import settings
from saltofi.xml import Block


class SaltFacilityBaseForm(GenericObservationForm):
    """Base form for all SALT observations."""
    exposure_time = forms.IntegerField(initial=1500)

    def __init__(self, *args, **kwargs):
        GenericObservationForm.__init__(self, *args, **kwargs)

        # get template path
        self.tpl_path = os.path.join(os.path.dirname(__file__), 'templates')

    @staticmethod
    def _set_current_semester(block: Block):
        """Updated the given block with the current semester.

        Args:
            block: The block to update.
        """

        # get today
        now = datetime.today()

        # decide on year and semester
        if 5 <= now.month <= 10:
            semester = 1
            year = now.year
        else:
            semester = 2
            year = now.year if now.month > 10 else now.year - 1

        # set it
        block.year = year
        block.semester = semester


class SaltFacilityGrbForm(SaltFacilityBaseForm):
    """Form for following up GRBs, based on template grb.xml"""

    def observation_payload(self):
        """This method is called to extract the data from the form into a dictionary that can be used by the rest
        of the module, which also contains the created XML for the block.
        """

        # get target
        target = Target.objects.get(pk=self.cleaned_data['target_id'])

        # load block template
        block = Block(os.path.join(self.tpl_path, 'grb.xml'))

        # set code and comment
        block.code = str(uuid.uuid4())
        block.comment = target.name

        # update semester
        self._set_current_semester(block)

        # set target
        block.targets[0].name = target.name
        block.targets[0].code = str(uuid.uuid4())
        block.targets[0].coordinates = SkyCoord(ra=target.ra * u.deg, dec=target.dec * u.deg, frame='icrs')
        block.targets[0].mag_filter = 'V'
        # block.targets[0].mag_min = event.magnitude
        # block.targets[0].mag_max = event.magnitude
        block.targets[0].finding_charts = ['auto-generated']

        # return dictionary
        return {
            'target_id': target.id,
            'block_code': block.code,
            'xml': block.to_string()
        }


class SaltFacility(GenericObservationFacility):
    """Observing facility interface for SALT"""
    name = 'SALT'
    observation_types = [('GRB', 'GRB Follow-Up')]

    SITES = {
        'SALT': {
            'latitude': -32.376006,
            'longitude': 20.810678,
            'elevation': 1783
        }
    }

    def data_products(self, observation_id, product_id=None):
        """Using an observation_id, retrieve a list of the data products that belong to this observation."""
        return []

    def get_form(self, observation_type):
        if observation_type == 'GRB':
            # GRB follow-ups
            return SaltFacilityGrbForm
        else:
            # by default, always show the GRB form
            return SaltFacilityGrbForm

    def get_observation_status(self, observation_id):
        return ['IN_PROGRESS']

    def get_observation_url(self, observation_id):
        return ''

    def get_observing_sites(self):
        return SaltFacility.SITES

    def get_terminal_observing_states(self):
        return ['IN_PROGRESS', 'COMPLETED']

    def submit_observation(self, observation_payload: dict):
        """Submit an observation to SALT.

        Args:
            observation_payload: Payload from form.

        Returns:
            Block code for submitted block.
        """

        # get XML
        xml = observation_payload['xml']

        # create proposal ZIP from block
        zip_file = self._create_zip_from_xml(xml)

        # send proposal
        self._submit_block(zip_file)

        # return code
        return [observation_payload['block_code']]

    @staticmethod
    def _create_zip_from_xml(xml: str) -> bytes:
        """Create a ZIP file in memory containing the given block XML.

        Args:
            xml: The XML for the block.

        Returns:
            The ZIP file as bytes array.
        """

        # create zip file in memory
        with io.BytesIO() as bio:
            # new ZIP file
            with zipfile.ZipFile(bio, mode='w') as zip:
                # write block XML
                zip.writestr('Block.xml', xml)

            # return ZIP file in memory
            return bio.getvalue()

    def validate_observation(self, observation_payload):
        pass

    def _submit_block(self, zip_file: bytes):
        """Submit a block to the SALT server.

        Args:
            zip_file: Bytes array containing ZIP file with proposal.
        """

        # get config
        cfg = settings.FACILITIES['SALT']

        # define parameters
        params = {
            'username': base64.b64encode(bytes(cfg['username'], 'utf-8')).decode('utf-8'),
            'password': base64.b64encode(bytes(cfg['password'], 'utf-8')).decode('utf-8'),
            'method': 'sendProposal',
            'asyncCode': '',
            'proposalCode': cfg['proposal_code'],
            'emails': 'false',
            'retainProposalStatus': 'false',
            'semester': '2017-2',
            'noValidation': 'false',
            'blocksOnly': 'true'
        }

        # encode body manually, since for whatever reason I cannot get requests
        # to encode the body in the correct form...
        content_type, body = self._encode_multipart_formdata(params, [zip_file])
        headers = {"Content-Type": content_type, 'content-length': str(len(body))}

        # do actual request
        response = requests.post(cfg['portal_url'], data=body, headers=headers)

        # parse response and check for error
        res = xmltodict.parse(response.content)
        if 'Error' in res:
            raise ValueError(res['Error'])

    @staticmethod
    def _encode_multipart_formdata(fields: typing.Dict[str, str], files: list) -> typing.Tuple[str, bytes]:
        """Manually creates a Multipart Formdata.

        Args:
            fields: HTTP headers.
            files: Files to add.

        Returns:
            Content type and actual body.
        """

        # define some strings
        boundary = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        crlf = '\r\n'
        body = b''

        # add parameters
        for key, value in fields.items():
            if isinstance(value, bool):
                value = 'true' if value else 'false'
            body += bytes('--' + boundary + crlf +
                          'Content-Disposition: form-data; name="%s"' % key + crlf +
                          'Content-Type: text/plain; charset=US-ASCII' + crlf +
                          'Content-Transfer-Encoding: 8bit' + crlf +
                          crlf +
                          str(value) + crlf, 'ascii')

        # add files
        for i, file_obj in enumerate(files):
            # add part header for file
            key = 'file_' + str(int(time.time())) + '_' + str(i)
            header = '--' + boundary + crlf + \
                     'Content-Disposition: form-data; name="%s"; filename="%s"' % (key, file_obj) + crlf + \
                     'Content-Type: application/zip' + crlf + \
                     'Content-Transfer-Encoding: binary' + crlf + crlf
            body += bytes(header, 'ascii')

            # add file itself, filename or file-like object?
            if isinstance(file_obj, io.IOBase):
                # file-like, read from it
                file_obj.seek(0)
                body += file_obj.read() + bytes(crlf, 'ascii')
            elif isinstance(file_obj, str):
                # filename, open and read
                with open(file_obj, 'rb') as f:
                    body += f.read() + bytes(crlf, 'ascii')
            elif isinstance(file_obj, bytes):
                # just bytes, write them
                body += file_obj + bytes(crlf, 'ascii')
            else:
                raise ValueError('Unknown file type.')

        # final boundary
        body += bytes('--' + boundary + '--', 'ascii')

        # return it
        content_type = 'multipart/form-data; boundary=%s' % boundary
        return content_type, body


__all__ = ['SaltFacility', 'SaltFacilityBaseForm', 'SaltFacilityGrbForm']
