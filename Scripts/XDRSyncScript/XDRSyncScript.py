import demistomock as demisto
from CommonServerPython import *
from CommonServerUserPython import *
from dateutil import parser
import copy
from typing import Optional, Dict


# XDR_FIELDS
INCIDENT_ID_XDR_FIELD = "incident_id"
MANUAL_SEVERITY_XDR_FIELD = "manual_severity"
MANUAL_DESCRIPTION_XDR_FIELD = "manual_description"
ASSIGNED_USER_MAIL_XDR_FIELD = "assigned_user_mail"
HIGH_SEVERITY_ALERT_COUNT_XDR_FIELD = "high_severity_alert_count"
HOST_COUNT_XDR_FIELD = "host_count"
XDR_URL_XDR_FIELD = "xdr_url"
ASSIGNED_USER_PRETTY_NAME_XDR_FIELD = "assigned_user_pretty_name"
ALERT_COUNT_XDR_FIELD = "alert_count"
MED_SEVERITY_ALERT_COUNT_XDR_FIELD = "med_severity_alert_count"
USER_COUNT_XDR_FIELD = "user_count"
SEVERITY_XDR_FIELD = "severity"
LOW_SEVERITY_ALERT_COUNT_XDR_FIELD = "low_severity_alert_count"
STATUS_XDR_FIELD = "status"
DESCRIPTION_XDR_FIELD = "description"
RESOLVE_COMMENT_XDR_FIELD = "resolve_comment"
NOTES_XDR_FIELD = "notes"
CREATION_TIME_XDR_FIELD = "creation_time"
DETECTION_TIME_XDR_FIELD = "detection_time"
MODIFICATION_TIME_XDR_FIELD = "modification_time"

XDR_INCIDENT_FIELDS = [
    INCIDENT_ID_XDR_FIELD,
    MANUAL_SEVERITY_XDR_FIELD,
    MANUAL_DESCRIPTION_XDR_FIELD,
    ASSIGNED_USER_MAIL_XDR_FIELD,
    HIGH_SEVERITY_ALERT_COUNT_XDR_FIELD,
    HOST_COUNT_XDR_FIELD,
    XDR_URL_XDR_FIELD,
    ASSIGNED_USER_PRETTY_NAME_XDR_FIELD,
    ALERT_COUNT_XDR_FIELD,
    MED_SEVERITY_ALERT_COUNT_XDR_FIELD,
    USER_COUNT_XDR_FIELD,
    SEVERITY_XDR_FIELD,
    LOW_SEVERITY_ALERT_COUNT_XDR_FIELD,
    STATUS_XDR_FIELD,
    DESCRIPTION_XDR_FIELD,
    RESOLVE_COMMENT_XDR_FIELD,
    NOTES_XDR_FIELD,
    CREATION_TIME_XDR_FIELD,
    DETECTION_TIME_XDR_FIELD,
    MODIFICATION_TIME_XDR_FIELD
]


def compare_incident_in_demisto_vs_xdr_context(incident_in_demisto, xdr_incident_in_context, incident_id, fields_mapping):
    modified_in_demisto = parser.parse(incident_in_demisto.get("modified")).timestamp() * 1000
    modified_in_xdr_in_context = int(xdr_incident_in_context.get("modification_time"))

    incident_in_demisto_was_modified = False

    xdr_update_args: Dict[str, Optional[str]] = {}

    if modified_in_demisto > modified_in_xdr_in_context:
        if ASSIGNED_USER_MAIL_XDR_FIELD in fields_mapping:
            field_name_in_demisto = fields_mapping[ASSIGNED_USER_MAIL_XDR_FIELD]

            if field_name_in_demisto == "owner":
                # if the ASSIGNED USER MAIL mapped to Demisto base field owner
                assigned_user_mail_current = incident_in_demisto.get("owner")
            else:
                assigned_user_mail_current = incident_in_demisto.get("CustomFields").get(field_name_in_demisto)

            assigned_user_mail_previous = xdr_incident_in_context[ASSIGNED_USER_MAIL_XDR_FIELD]

            if not assigned_user_mail_current and not assigned_user_mail_previous:
                # do nothing
                pass

            elif not assigned_user_mail_current and assigned_user_mail_previous:
                incident_in_demisto_was_modified = True
                xdr_update_args[ASSIGNED_USER_MAIL_XDR_FIELD] = "none"

            elif assigned_user_mail_current != assigned_user_mail_previous:
                incident_in_demisto_was_modified = True
                xdr_update_args[ASSIGNED_USER_MAIL_XDR_FIELD] = assigned_user_mail_current

        if ASSIGNED_USER_PRETTY_NAME_XDR_FIELD in fields_mapping:
            field_name_in_demisto = fields_mapping[ASSIGNED_USER_PRETTY_NAME_XDR_FIELD]
            assigned_user_pretty_name_current = incident_in_demisto.get("CustomFields").get(field_name_in_demisto)
            assigned_user_pretty_name_previous = xdr_incident_in_context[ASSIGNED_USER_PRETTY_NAME_XDR_FIELD]

            if assigned_user_pretty_name_current != assigned_user_pretty_name_previous:
                incident_in_demisto_was_modified = True
                xdr_update_args[ASSIGNED_USER_PRETTY_NAME_XDR_FIELD] = assigned_user_pretty_name_current

        if STATUS_XDR_FIELD in fields_mapping:
            field_name_in_demisto = fields_mapping[STATUS_XDR_FIELD]
            status_current = incident_in_demisto.get("CustomFields").get(field_name_in_demisto)
            status_previous = xdr_incident_in_context[STATUS_XDR_FIELD]

            if status_current != status_previous:
                incident_in_demisto_was_modified = True
                xdr_update_args[STATUS_XDR_FIELD] = status_current

        if SEVERITY_XDR_FIELD in fields_mapping:
            field_name_in_demisto = fields_mapping[SEVERITY_XDR_FIELD]

            severity_previous = xdr_incident_in_context[SEVERITY_XDR_FIELD]

            if field_name_in_demisto == "severity":
                # if field mapped to original demisto severity field then we should get it directly from incident
                severity_current = incident_in_demisto.get(field_name_in_demisto)

                severity_mapping = {
                    1: "low",
                    2: "medium",
                    3: "high",
                    4: "high"
                }
                if severity_current != 0 and severity_mapping[severity_current] != severity_previous:
                    incident_in_demisto_was_modified = True
                    xdr_update_args[MANUAL_SEVERITY_XDR_FIELD] = severity_mapping[severity_current]

            else:
                severity_current = incident_in_demisto.get("CustomFields").get(field_name_in_demisto)

                if severity_current != severity_previous:
                    incident_in_demisto_was_modified = True

                    if severity_current is None or severity_current == '':
                        xdr_update_args[MANUAL_SEVERITY_XDR_FIELD] = "none"
                    else:
                        xdr_update_args[MANUAL_SEVERITY_XDR_FIELD] = severity_current

        if RESOLVE_COMMENT_XDR_FIELD in fields_mapping:
            field_name_in_demisto = fields_mapping[RESOLVE_COMMENT_XDR_FIELD]
            resolve_comment_current = incident_in_demisto.get("CustomFields").get(field_name_in_demisto)
            resolve_comment_previous = xdr_incident_in_context[RESOLVE_COMMENT_XDR_FIELD]

            if resolve_comment_current != resolve_comment_previous:
                incident_in_demisto_was_modified = True
                xdr_update_args[RESOLVE_COMMENT_XDR_FIELD] = resolve_comment_current

    if not xdr_update_args:
        return False, {}

    xdr_update_args["incident_id"] = incident_id
    return incident_in_demisto_was_modified, xdr_update_args


def compare_incident_in_xdr_vs_previous_xdr_in_context(incident_in_xdr, xdr_incident_in_context, fields_mapping):
    modified_in_xdr = int(incident_in_xdr.get("modification_time"))
    modified_in_xdr_in_context = int(xdr_incident_in_context.get("modification_time"))

    incident_in_xdr_was_modified = False

    demisto_update_args = {}
    if modified_in_xdr > modified_in_xdr_in_context:

        for field_in_xdr in XDR_INCIDENT_FIELDS:
            if field_in_xdr in fields_mapping:

                current_value = incident_in_xdr.get(field_in_xdr)
                previous_value = xdr_incident_in_context.get(field_in_xdr)

                if not current_value and not previous_value:
                    # both non existing values - ignore
                    pass
                if current_value != previous_value:
                    incident_in_xdr_was_modified = True
                    field_name_in_demisto = fields_mapping[field_in_xdr]

                    if current_value is None:
                        demisto_update_args[field_name_in_demisto] = ""
                    else:
                        demisto_update_args[field_name_in_demisto] = current_value

    return incident_in_xdr_was_modified, demisto_update_args


def args_to_str(demisto_args, latest_incident_in_xdr):
    args_to_str = ""
    args_copy = copy.deepcopy(demisto_args)

    args_copy["xdr_incident_from_previous_run"] = json.dumps(latest_incident_in_xdr)
    args_copy["first"] = "false"

    for arg_key in args_copy:
        arg_value = args_copy[arg_key]
        args_to_str += '{}=`{}` '.format(arg_key, arg_value)

    return args_to_str


def get_latest_incident_from_xdr(incident_id):
    # get the latest incident from xdr
    latest_incident_in_xdr_result = demisto.executeCommand("xdr-get-incident-extra-data", {"incident_id": incident_id})
    if is_error(latest_incident_in_xdr_result):
        raise ValueError("Failed to execute xdr-get-incident-extra-data command. Error: {}".format(
            get_error(latest_incident_in_xdr_result)))

    latest_incident_in_xdr = latest_incident_in_xdr_result[0]["Contents"].get("incident")
    # no need to pass the whole incident with extra data - it will be too big json to pass
    # just the basic incident details
    if 'alerts' in latest_incident_in_xdr:
        del latest_incident_in_xdr['alerts']
    if 'file_artifacts' in latest_incident_in_xdr:
        del latest_incident_in_xdr['file_artifacts']
    if 'network_artifacts' in latest_incident_in_xdr:
        del latest_incident_in_xdr['network_artifacts']

    latest_incident_in_xdr_markdown = latest_incident_in_xdr_result[0]["HumanReadable"]
    if not latest_incident_in_xdr:
        raise ValueError("Error - for some reason xdr-get-incident-extra-data didn't return any incident from xdr "
                         "with id={}".format(incident_id))

    return latest_incident_in_xdr_result, latest_incident_in_xdr, latest_incident_in_xdr_markdown


def xdr_incident_sync(incident_id, fields_mapping, xdr_incident_from_previous_run, first_run, xdr_alerts_field,
                      xdr_file_artifacts_field, xdr_network_artifacts_field, verbose=True):

    latest_incident_in_xdr_result, latest_incident_in_xdr, latest_incident_in_xdr_markdown = \
        get_latest_incident_from_xdr(incident_id)

    if first_run:
        xdr_incident_from_previous_run = latest_incident_in_xdr
    else:
        if xdr_incident_from_previous_run:
            xdr_incident_from_previous_run = json.loads(xdr_incident_from_previous_run)
        else:
            raise ValueError("xdr_incident_from_previous_run expected to contain incident JSON, but passed None")

    # get the incident from demisto
    incident_in_demisto = demisto.incidents()[0]
    if not incident_in_demisto:
        raise ValueError("Error - demisto.incidents()[0] expected to return current incident "
                         "from context but returned None")

    incident_in_demisto_was_modified, xdr_update_args = compare_incident_in_demisto_vs_xdr_context(
        incident_in_demisto,
        xdr_incident_from_previous_run,
        incident_id, fields_mapping)

    if incident_in_demisto_was_modified:
        # update xdr and finish the script
        demisto.debug("the incident in demisto was modified, updating the incident in xdr accordingly. ")
        demisto.debug("xdr_update_args: {}".format(json.dumps(xdr_update_args, indent=4)))
        res = demisto.executeCommand("xdr-update-incident", xdr_update_args)
        if is_error(res):
            raise ValueError(get_error(res))

        latest_incident_in_xdr_result, latest_incident_in_xdr, latest_incident_in_xdr_markdown = \
            get_latest_incident_from_xdr(incident_id)

        xdr_incident = latest_incident_in_xdr_result[0]['Contents']
        update_incident = dict()
        update_incident[xdr_alerts_field] = replace_in_keys(xdr_incident.get('alerts').get('data', []), '_', '')
        update_incident[xdr_file_artifacts_field] = replace_in_keys(xdr_incident.get('file_artifacts').get('data', []),
                                                                    '_', '')
        update_incident[xdr_network_artifacts_field] = replace_in_keys(xdr_incident.get('network_artifacts').get('data',
                                                                                                                 []),
                                                                       '_', '')

        res = demisto.executeCommand("setIncident", update_incident)
        if is_error(res):
            raise ValueError(get_error(res))

        # update the context with latest incident from xdr
        demisto.results(latest_incident_in_xdr_result)

        if verbose:
            return_outputs(
                "Incident in Demisto was modified, updating incident in XDR accordingly.\n\n{}".format(xdr_update_args),
                None)

        return latest_incident_in_xdr

    incident_in_xdr_was_modified, demisto_update_args = compare_incident_in_xdr_vs_previous_xdr_in_context(
        latest_incident_in_xdr,
        xdr_incident_from_previous_run,
        fields_mapping)

    if incident_in_xdr_was_modified:
        demisto.debug("the incident in xdr was modified, updating the incident in demisto")
        demisto.debug("demisto_update_args: {}".format(json.dumps(demisto_update_args, indent=4)))

        xdr_incident = latest_incident_in_xdr_result[0]['Contents']
        update_incident = dict()
        update_incident[xdr_alerts_field] = replace_in_keys(xdr_incident.get('alerts').get('data', []), '_', '')
        update_incident[xdr_file_artifacts_field] = replace_in_keys(xdr_incident.get('file_artifacts').get('data', []),
                                                                    '_', '')
        update_incident[xdr_network_artifacts_field] = replace_in_keys(xdr_incident.get('network_artifacts').get('data',
                                                                                                                 []),
                                                                       '_', '')

        res = demisto.executeCommand("setIncident", update_incident)
        if is_error(res):
            raise ValueError(get_error(res))

        demisto.results(latest_incident_in_xdr_result)
        if verbose:
            return_outputs(
                "Incident in XDR was modified, updating incident in Demisto accordingly.\n\n{}".format(demisto_update_args),
                None)

        # rerun the playbook the current playbook
        demisto.executeCommand("setPlaybook", {})
        return latest_incident_in_xdr

    if first_run:
        demisto.results(latest_incident_in_xdr_result)

        # set the incident markdown field
        xdr_incident = latest_incident_in_xdr_result[0]['Contents']
        update_incident = dict()
        update_incident[xdr_alerts_field] = replace_in_keys(xdr_incident.get('alerts').get('data', []), '_', '')
        update_incident[xdr_file_artifacts_field] = replace_in_keys(xdr_incident.get('file_artifacts').get('data', []),
                                                                    '_', '')
        update_incident[xdr_network_artifacts_field] = replace_in_keys(xdr_incident.get('network_artifacts').get('data',
                                                                                                                 []),
                                                                       '_', '')

        demisto.results(update_incident)
        res = demisto.executeCommand("setIncident", update_incident)
        if is_error(res):
            raise ValueError(get_error(res))

        if verbose:
            return_outputs("Nothing to sync.", None)

        return latest_incident_in_xdr


def main():
    fields_mapping = {}
    for xdr_field in XDR_INCIDENT_FIELDS:
        if xdr_field in demisto.args() and demisto.args().get(xdr_field) is not None:
            custom_field_in_demisto = demisto.args().get(xdr_field)
            fields_mapping[xdr_field] = custom_field_in_demisto

    incident_id = demisto.args().get('incident_id')
    first_run = demisto.args().get('first') == 'true'
    interval = int(demisto.args().get('interval'))
    xdr_incident_from_previous_run = demisto.args().get('xdr_incident_from_previous_run')
    xdr_alerts_field = demisto.args().get('xdr_alerts')
    xdr_file_artifacts_field = demisto.args().get('xdr_file_artifacts')
    xdr_network_artifacts_field = demisto.args().get('xdr_network_artifacts')
    verbose = demisto.args().get('verbose') == 'true'

    xdr_incident_markdown_field = demisto.args().get('xdr_incident_markdown_field')  # deprecated
    if xdr_incident_markdown_field:
        # deprecated field
        return_error('Deprecated xdr_incident_markdown_field argument, instead use xdr_alerts, xdr_file_artifacts, '
                     'xdr_network_artifacts. For more information follow Demisto documentation.', None)

    previous_scheduled_task_id = demisto.get(demisto.context(), 'XDRSyncScriptTaskID')
    if first_run and previous_scheduled_task_id:
        if verbose:
            demisto.debug('Stopping previous scheduled task with ID: {}'.format(previous_scheduled_task_id))

        demisto.executeCommand('StopScheduledTask', {'taskID': previous_scheduled_task_id})
        demisto.setContext('XDRSyncScriptTaskID', '')

    try:
        latest_incident_in_xdr = xdr_incident_sync(incident_id, fields_mapping, xdr_incident_from_previous_run,
                                                   first_run, xdr_alerts_field, xdr_file_artifacts_field,
                                                   xdr_network_artifacts_field, verbose)
    except Exception as ex:
        return_error(str(ex), ex)
    finally:
        # even if error occurred keep trigger sync
        if latest_incident_in_xdr is None:
            args = args_to_str(demisto.args(), xdr_incident_from_previous_run)
        else:
            args = args_to_str(demisto.args(), latest_incident_in_xdr)

        res = demisto.executeCommand("ScheduleCommand", {
            'command': '''!XDRSyncScript {}'''.format(args),
            'cron': '*/{} * * * *'.format(interval),
            'times': 1
        })

        if is_error(res):
            # return the error entries to warroom
            demisto.results(res)
            return

        scheduled_task_id = res[0]["Contents"].get("id")
        demisto.setContext("XDRSyncScriptTaskID", scheduled_task_id)

        if verbose:
            demisto.results("XDRSyncScriptTaskID: {}".format(scheduled_task_id))


if __name__ == 'builtins':
    main()
