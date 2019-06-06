from datetime import timedelta, time
from string import Template

from call.config import Constants
from call.models import Call


class CalculateBill:
    """ class to calculate telephone bills
    """

    def __init__(self, call_id):
        self.call_id = call_id

    def get_call_duration(self):

        call_start = Call.objects.get(type=Constants.START, call_id=self.call_id).timestamp
        call_end = Call.objects.get(type=Constants.END, call_id=self.call_id).timestamp

        delta = call_end - call_start
        result_dict = {}
        time_dict = {'H': 3600, 'M': 60, 'S': 1}
        rem = int(delta.total_seconds())

        for k in ('H', 'M', 'S'):
            result_dict[k], rem = divmod(rem, time_dict[k])

        t = Template("${H}h${M}m${S}s")
        return t.substitute(**result_dict)

    def get_call_price(self):

        call_start = Call.objects.get(type=Constants.START, call_id=self.call_id).timestamp
        call_end = Call.objects.get(type=Constants.END, call_id=self.call_id).timestamp

        minutes = 0

        while call_start < call_end:
            call_start = call_start + timedelta(minutes=1)
            if call_start < call_end and time(6, 0, 0) < call_start.time() < time(22, 0, 0):
                minutes += 1

        subtotal = minutes * Constants.CHARGE_MINUTE

        total = round(Constants.FIXED_CHARGE + subtotal, 2)
        total_str = str(total).replace('.', ',')
        return 'R$ {}'.format(total_str)
