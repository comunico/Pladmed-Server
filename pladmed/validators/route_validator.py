from pladmed.validators.operations_validator import TRACEROUTE_PARAMS, PING_PARAMS, DNS_PARAMS
from pladmed.validators.command_validator import InvalidParam
from flanker.addresslib import address
from croniter import croniter
import numbers
import datetime


def validate_params(data, valid_params):
    print("Se validan los parametros")
    try:
        for param in data:
            print("Se valida el parametro: ", param)
            if param in valid_params:
                print("El parametro es dentro de los parametros validos: ", param)
                validator = valid_params[param]
                validator.validate(data[param])
        return True
    except InvalidParam:
        return False


def validate_probes(data):
    return len(data) > 0


def validate_destinations(data):
    print("Se validan los destinos")
    if "fqdns" not in data and "ips" not in data:
        return False
    total_destinations = 0
    if "fqdns" in data:
        total_destinations += len(data["fqdns"])
    if "ips" in data:
        total_destinations += len(data["ips"])

    print("Total de destinos: ", total_destinations)
    return total_destinations != 0


def validate_timing_params(data):
    print("Se validan los parametros de tiempo")
    if "cron" not in data:
        print("Falta el parametro cron")
        return False
    if not croniter.is_valid(data["cron"]):
        print("La expresion de cron es invalida")
        return False

    if "stop_time" not in data:
        print("Falta el parametro stop_time")
        return False
    try:
        datetime.datetime.strptime(data["stop_time"], '%d/%m/%Y %H:%M')
    except ValueError:
        return False

    if "times_per_minute" not in data:
        print("Falta el parametro times_per_minute")
        return False
    return isinstance(data["times_per_minute"], numbers.Number)


def validate_traceroute(data):
    return validate_operation(data, TRACEROUTE_PARAMS)


def validate_ping(data):
    return validate_operation(data, PING_PARAMS)


def validate_dns(data):
    return validate_operation(data, DNS_PARAMS)


def validate_operation(data, valid_params):
    print("Se comprueba si hay probes en la data")
    if "probes" not in data or "params" not in data:
        return False
        
    valido1 = validate_probes(data["probes"])
    valido2 = validate_params(data["params"], valid_params)
    valido3 = validate_destinations(data["params"])
    valido4 = validate_timing_params(data["params"])

    print("Resultado de las validacopnes = ", valido1, valido2, valido3, valido4)
    return valido1 and valido2 and valido3 and valido4
#    return validate_probes(data["probes"]) and validate_params(data["params"], valid_params) and validate_destinations(
#        data["params"]) and validate_timing_params(data["params"])


def validate_user_data_present(data):
    if "email" not in data or data["email"] == "":
        return "Missing email field"
    if "password" not in data or data["password"] == "":
        return "Missing password field"
    return ""


def validate_user_data(data):
    validation_error = validate_user_data_present(data)
    if validation_error != "":
        return validation_error

    addr = address.validate_address(data["email"], skip_remote_checks=True)
    if addr == None:
        return "Email address has invalid format, or MX domain does not exist"

    password = data["password"]
    special_characters = '!"@#$%^&*()-+?_=,/'
    rules = [lambda s: any(x.isupper() for x in s),  # must have at least one uppercase
             # must have at least one lowercase
             lambda s: any(x.islower() for x in s),
             lambda s: any(x.isdigit()
                           for x in s),  # must have at least one digit
             # must be at least 8 characters
             lambda s: len(s) >= 8,
             lambda s: any(x in special_characters for x in s),
             ]

    if not all(rule(password) for rule in rules):
        return "Password must have at least 8 characters, 1 uppercase character, 1 lowercase, 1 digit and 1 special character"

    return ""


def validate_credits(data):
    return "id" in data and data["id"] != "" and "credits" in data and data["credits"] > 0


def validate_location(data):
    if not "location" in data or data["location"] == None:
        return ""
    location = data["location"]

    if not "longitude" in location or location["longitude"] == None or not isinstance(location["longitude"], numbers.Number):
        return "location.longitude is not a number"

    if not "latitude" in location or location["latitude"] == None or not isinstance(location["latitude"], numbers.Number):
        return "location.latitude is not a number"
    return ""
