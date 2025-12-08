class BooleanTransformer:
    def __init__(self, true_val):
        self._true_val = true_val

    def transform(self, value):
        if value == self._true_val:
            return value, 1
        return value, 0
    
class EnumTransformer:
    def __init__(self, states_to_values):
        self._states_to_values = states_to_values

    def transform(self, value):
        if value in self._states_to_values:
            return value, self._states_to_values[value]
        return value, -1


_ATTR_CONVERSIONS = {
    "switch": BooleanTransformer("on"),
    "water": BooleanTransformer("dry"),
    "power": BooleanTransformer("on"),
}


_DEVICE_SPECIFIC_CONVERSIONS = {
    "google_nest_thermostat": {
        "thermostatoperatingstate": EnumTransformer({
            "heating": 1,
            "pending cool": 0,
            "pending heat": 0,
            "vent economizer": 0,
            "idle": 0,
            "cooling": -1,
            "fan only": 1,
        })
    },
}

class AttributeTransformer:
    def __init__(self, device_type, attribute_name) -> None:
        self._device_type = device_type.lower() if device_type else ""
        self._attribute_name = attribute_name.lower() if attribute_name else ""

    def transform(self, value):
        # If it's a switch, then change from text to binary values
        if self._attribute_name in _ATTR_CONVERSIONS:
            # device_state, value
            return _ATTR_CONVERSIONS[self._attribute_name].transform(value)
        if self._device_type in _DEVICE_SPECIFIC_CONVERSIONS and self._attribute_name in _DEVICE_SPECIFIC_CONVERSIONS[self._device_type]:
            # device_state (enum), value
            return _DEVICE_SPECIFIC_CONVERSIONS[self._device_type][self._attribute_name].transform(value)

        return "", value
