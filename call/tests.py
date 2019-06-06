from django.core.exceptions import ValidationError, MultipleObjectsReturned
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from call.models import Call, Bill
from call.config import Constants


class CallModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(CallModelTests, cls).setUpClass()
        cls.call_1 = Call.objects.create(
            type=Constants.START,
            timestamp='2016-02-29T12:00:00Z',
            call_id=70,
            source='99988526423',
            destination='9993468278'
        )
        cls.call_2 = Call.objects.create(
            type=Constants.END,
            timestamp='2016-02-29T14:00:00Z',
            call_id=70
        )

    @classmethod
    def tearDownClass(cls):
        cls.call_1.delete()
        super(CallModelTests, cls).tearDownClass()

    def test_duplicate_start_call(self):
        """ validate that two call with the same call_id and the same type.
        """
        call = Call(
            type=Constants.START,
            timestamp='2016-02-29T12:10:00Z',
            call_id=70,
            source='99988526423',
            destination='9993468278'
        )
        with self.assertRaises(ValidationError):
            call.full_clean()

    def test_duplicate_end_call(self):
        """ validate that two call with the same call_id forbidden and the same type.
        """
        call = Call(
            type=Constants.END,
            timestamp='2016-02-29T14:10:00Z',
            call_id=70
        )
        with self.assertRaises(ValidationError):
            call.full_clean()


class CallEndPointTestCase(TestCase):
    CALL_URL = '/api/v1/call/'

    fixtures = ['initial_data.json']

    @classmethod
    def setUpClass(cls):
        super(CallEndPointTestCase, cls).setUpClass()
        cls.api_client = APIClient()

    def setUp(self):
        super(CallEndPointTestCase, self).setUp()
        self.post_data_start = {
            "call_id": 78,
            "destination": "9993468278",
            "source": "99988526423",
            "timestamp": "2018-07-07 15:07:13+00:00",
            "type": Constants.START
        }
        self.post_data_end = {
            "call_id": 78,
            "timestamp": "2018-07-07 15:14:56+00:00",
            "type": Constants.END
        }

    def create_call(self, type):
        """Make a post to create a call
        Arguments:
            **type (int):** the call type (1: Start, 2: End)
        Return:
            **response object:** the response of creation
        """
        if type == Constants.START:
            data = self.post_data_start
        else:
            data = self.post_data_end
        return self.api_client.post(self.CALL_URL, format='json', data=data)

    def test_create_call(self):
        """Test the API for create a new call
        Should return 201 CREATED
        """
        response = self.create_call(Constants.START)
        self.assertEquals(201, response.status_code)

        response = self.create_call(Constants.END)
        self.assertEquals(201, response.status_code)

    def test_get_calls(self):
        """Test the API for get all the calls
        Should return 200 OK and a list of calls
        """
        response = self.api_client.get(self.CALL_URL, format='json')
        calls = response.json()
        self.assertEquals(200, response.status_code)
        self.assertTrue(len(calls) > 0)

    def test_get_call_detail(self):
        """ Test the API for get a specific call
            Should return 200 OK
        """
        response = self.create_call(Constants.START)
        created_call = response.json()
        response = self.api_client.get(self.CALL_URL + "{}/".format(created_call['id']), format='json')
        self.assertEquals(200, response.status_code)

    def test_update_call(self):
        """Test the API for update a specific call
        Should return 405 METHOD NOT ALLOWED
        """
        response = self.create_call(Constants.START)
        created_call = response.json()
        response = self.api_client.put(
            self.CALL_URL + "{}/".format(created_call['id']),
            format='json',
            data={'timestamp': '2018-07-07 15:07:13'}
        )
        self.assertEquals(405, response.status_code)

    def test_delete_call(self):
        """Test the API for delete a specific call
        Should return 405 METHOD NOT ALLOWED
        """
        response = self.create_call(Constants.START)
        created_call = response.json()
        response = self.api_client.delete(self.CALL_URL + "{}/".format(created_call['id']), format='json')
        self.assertEquals(405, response.status_code)

    def test_no_data_call(self):
        """Test the API for create a new call with no data
        """
        response = self.api_client.post(self.CALL_URL, format='json', data={})
        self.assertEquals(400, response.status_code)
        self.assertEquals(
            {'call_id': ['This field is required.'],
             'timestamp': ['This field is required.'],
             'type': ['This field is required.']},
            response.json()
        )

    def test_no_type_call(self):
        """Test the API for create a new call with no type
        """
        del self.post_data_start['type']
        response = self.create_call(Constants.START)
        self.assertEquals(400, response.status_code)
        self.assertEquals(
            {'type': ['This field is required.']},
            response.json()
        )

    def teste_invalid_timestamp_call(self):
        """Test the API for create a new call with an invalid timestamp
        """
        self.post_data_start['timestamp'] = "2018-99-99 00:00:00"
        response = self.create_call(Constants.START)
        self.assertEquals(400, response.status_code)
        self.assertEquals(
            {'timestamp': (
                ["Datetime has wrong format. Use one of these formats instead: "
                 "YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]."]
            )},
            response.json()
        )

    def test_invalid_call_end_call_id(self):
        """Test the API for create a new end call with invalid call_id
        """
        self.post_data_end['call_id'] = 999
        self.create_call(Constants.START)
        response = self.create_call(Constants.END)
        self.assertEquals(400, response.status_code)
        self.assertEquals(
            {'non_field_errors': ['Does not exist a call start entry with this call id: 999']},
            response.json()
        )

    def test_invalid_call_end_timestamp(self):
        """Test the API for create a new end call with invalid timestamp
        """
        self.post_data_end['timestamp'] = "2018-07-06 15:07:13"
        self.create_call(Constants.START)
        response = self.create_call(Constants.END)
        self.assertEquals(400, response.status_code)
        self.assertEquals(
            {'non_field_errors': ["Invalid timestamp. Must be grater then {}".format(self.post_data_start['timestamp'])]},
            response.json()
        )


class BillsTests(TestCase):
    CALL_URL = '/api/v1/call/'
    BILL_URL = '/api/v1/bill/'

    @classmethod
    def setUpClass(cls):
        super(BillsTests, cls).setUpClass()
        cls.client = APIClient()

    def test_bill_creation(self):
        response = self.client.post(self.CALL_URL, {
            "type": Constants.START,
            "timestamp": "2016-02-19T21:57:13Z",
            "call_id": 70,
            "source": "99988526423",
            "destination": "9993468278"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Call.objects.count(), 1)
        self.assertEqual(Bill.objects.count(), 0)
        # to create a bill it' necessary to create the end call request
        response = self.client.post(self.CALL_URL, {
            "type": Constants.END,
            "timestamp": "2016-02-19T22:10:56Z",
            "call_id": 70,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Call.objects.count(), 2)
        self.assertEqual(Bill.objects.count(), 1)

        response = self.client.get(self.BILL_URL + '99988526423/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        bills = response.json()
        self.assertEqual(len(bills), 0)

        response = self.client.get(self.BILL_URL + '99988526423/2016/02/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        bills = response.json()
        self.assertEqual(len(bills), 1)
        self.assertEqual(bills[0]['price'], 'R$ 0,54')
