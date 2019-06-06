from rest_framework import serializers

from call.config import Constants
from call.models import Call, Bill
from call.util import CalculateBill


class CallSerializer(serializers.ModelSerializer):
    """ Serializer for Call model
    """

    class Meta:
        model = Call
        fields = ('id', 'type', 'timestamp', 'call_id', 'source', 'destination')
        read_only_fields = ('id',)

    def validate(self, attrs):
        source = attrs.get('source', None)
        destination = attrs.get('destination', None)
        type = attrs.get('type')
        call_id = attrs.get('call_id')
        timestamp = attrs.get('timestamp')
        if source:
            if not source.isdigit():
                raise serializers.ValidationError('The origin number field must be only numbers.')
            if len(source) < 8:
                raise serializers.ValidationError('The size of origin number field should be '
                                                  'between 8 and 11 characters.')
        if destination:
            if not destination.isdigit():
                raise serializers.ValidationError('The destination number field must be only numbers.')
            if len(destination) < 8:
                raise serializers.ValidationError('The size of destination number field should be '
                                                  'between 8 and 11 characters.')
        if type == Constants.END:
            call = Call.objects.filter(type=Constants.START, call_id=call_id)
            if call:
                if timestamp < call[0].timestamp:
                    raise serializers.ValidationError(
                        'Invalid timestamp. Must be grater then {}'.format(call[0].timestamp)
                    )
            else:
                raise serializers.ValidationError(
                    'Does not exist a call start entry with this call id: {}'.format(call_id)
                )
        return attrs

    def create(self, validated_data):
        instance = super(CallSerializer, self).create(validated_data)
        call = None

        # verify if the type of call is 'end'
        if validated_data['type'] == Constants.END:
            call = Call.objects.filter(type=Constants.START, call_id=validated_data['call_id'])
        if validated_data['type'] == Constants.START:
            call = Call.objects.filter(type=Constants.END, call_id=validated_data['call_id'])
            # the bill only will be created if start and end calls exists
        if call:
            calc_bill = CalculateBill(validated_data['call_id'])
            # verify if the created call has the type 'start'.
            # it' necessary to do the correct relationship in destination field
            if instance.type == Constants.START:
                month = call[0].timestamp.month
                year = call[0].timestamp.year
                call = instance
            else:
                call = call[0]
                month = instance.timestamp.month
                year = instance.timestamp.year
            Bill.objects.create(
                destination=call,
                start_date=call.timestamp.date(),
                start_time=call.timestamp.time(),
                duration=calc_bill.get_call_duration(),
                month=month,
                year=year,
                price=calc_bill.get_call_price()
            )
        return instance


class BillSerializer(serializers.ModelSerializer):
    """ Serializer for Bill model
    """
    destination = serializers.StringRelatedField(many=False)

    class Meta:
        model = Bill
        fields = ('destination', 'start_date', 'start_time', 'duration', 'price')
