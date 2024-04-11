from datetime import date, datetime, timezone

import phonenumbers
from dateutil.parser import isoparse


class Int32(int):
    """
    A restricted int type for only 32bit range integer
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        sql_integer = int(v)
        if not (-0x1 << 31) <= sql_integer <= (0x1 << 31) - 1:
            raise ValueError('Lookup value too large to convert to SQL INTEGER')
        return sql_integer


class PhoneNumberStr(str):
    EXAMPLE_PHONE_NUMBER = '+8860912345678'

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            format='phone-number',
            description=f'Example : {cls.EXAMPLE_PHONE_NUMBER}',
        )

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        try:
            parsed_phone_number = phonenumbers.parse(v, None)
        except Exception:
            raise ValueError('invalid phone number')
        if not phonenumbers.is_possible_number(parsed_phone_number):
            raise ValueError('invalid phone number')
        return v


class ParameterInt(Int32):
    """
    Restricts path/query parameters (string) of the URL to pure digits (0 ~ 9).

    Underscores in Numeric Literals is prohibited.

    It inherits int so the type on the documents (OpenApi) would be integer.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        v = str(v)
        if not v.isdigit():
            raise ValueError('Unacceptable numeric literals in URL parameters')
        return super().validate(v)


class ParameterDate(date):
    """
        Restrict date format of query parameters to simply accept iso8601 calendar date format only
    (eg.'YYYY-MM-DD' or 'YYYYMMDD'), query parameters like date=20160101 should be recognized as date
    string format instead of timestamp.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if type(v) is not str:
            v = str(v)

        if v.isdigit():
            try:
                date_obj = datetime.strptime(v, '%Y%m%d')
            except ValueError:
                raise ValueError('Unprocessable date format in URL parameters')
        else:
            try:
                date_obj = datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Unprocessable date format in URL parameters')

        return date_obj


class ISO8601Datetime(datetime):
    """
    Restrict the input datetime format to ISO 8601 datetime format which contains
    timezone info.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if type(v) is not str:
            v = str(v)

        datetime_ = isoparse(v)
        if not datetime_.tzinfo:
            raise ValueError('datetime should contain timezone info')

        return datetime_.astimezone(timezone.utc)


class UTCDatetime(datetime):
    """
    Add timezone info of UTC and return an ISO 8601 datetime.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v) -> datetime:
        if type(v) is not str:
            v = str(v)
        return isoparse(v).replace(tzinfo=timezone.utc, microsecond=0)

    @classmethod
    def to_isoformat_str(cls, v: datetime) -> str:
        return cls.validate(v).isoformat()
