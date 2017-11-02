import logging
import sys

from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode

# Register your models here.
from django.contrib.admin.models import LogEntry, CHANGE, ADDITION

traceback_template = '''Traceback (most recent call last):
  File "%(filename)s", line %(lineno)s, in %(name)s
%(type)s: %(message)s
'''  # Skipping the "actual line" item
traceback_with_message_template = '''Traceback (most recent call last):
  File "%(filename)s", line %(lineno)s, in %(name)s
%(type)s: %(message)s
%(custom_message)s
'''  # Skipping the "actual line" item

logger = logging.getLogger('django')


def get_traceback_details(message=None):
    exc_type, exc_value, exc_traceback = sys.exc_info()  # most recent (if any) by default
    message = str(message)
    return {
        'filename': exc_traceback.tb_frame.f_code.co_filename,
        'lineno': exc_traceback.tb_lineno,
        'name': exc_traceback.tb_frame.f_code.co_name,
        'type': exc_type.__name__,
        'message': exc_value.message,  # or see traceback._some_str()
        'custom_message': message
    }


def get_traceback(message, has_exception):
    if not has_exception:
        return message
    traceback_details = get_traceback_details(message)
    if message:
        return traceback_with_message_template % traceback_details
    else:
        return traceback_template % traceback_details


def critical(message=None, has_exception=True):
    logger.critical(get_traceback(message, has_exception))


def error(e, message=None, has_exception=True):
    if e is not None:
        logging.exception(e)
    logger.error(get_traceback(message, has_exception))


def info(message=None, has_exception=False):
    logger.info(get_traceback(message, has_exception))


def debug(message=None, has_exception=False):
    logger.debug(get_traceback(message, has_exception))


def warning(message=None, has_exception=False):
    logger.warning(get_traceback(message, has_exception))


def log(level, message=None, has_exception=False):
    logger.log(get_traceback(message, has_exception))


def log_change_for_admin(user, target_object, message, creation=False):
    LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=ContentType.objects.get_for_model(target_object).pk,
        object_id=target_object.pk,
        object_repr=force_unicode(target_object),
        action_flag=ADDITION if creation else CHANGE,
        change_message=message
    )
