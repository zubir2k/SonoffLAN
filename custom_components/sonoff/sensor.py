import logging
from typing import Optional

from homeassistant.const import TEMP_CELSIUS, DEVICE_CLASS_HUMIDITY, \
    DEVICE_CLASS_TEMPERATURE, DEVICE_CLASS_ILLUMINANCE
from homeassistant.helpers.entity import Entity

from . import DOMAIN, EWeLinkDevice

_LOGGER = logging.getLogger(__name__)

ATTRS = {
    'temperature': [DEVICE_CLASS_TEMPERATURE, TEMP_CELSIUS, None],
    'humidity': [DEVICE_CLASS_HUMIDITY, '%', None],
    'dusty': [None, None, 'mdi:cloud'],
    'light': [DEVICE_CLASS_ILLUMINANCE, None, None],
    'noise': [None, None, 'mdi:bell-ring']
}


def setup_platform(hass, config, add_entities, discovery_info=None):
    if discovery_info is None:
        return

    deviceid = discovery_info['deviceid']
    device = hass.data[DOMAIN][deviceid]
    add_entities([EWeLinkSensor(device, k)
                  for k in ATTRS
                  if k in device.state])


class EWeLinkSensor(Entity):
    def __init__(self, device: EWeLinkDevice, attr: str):
        self.device = device
        self._attr = attr
        self._name = None
        self._state = None

        self._update(device, False)

        device.listen(self._update)

    async def async_added_to_hass(self) -> None:
        # Присваиваем имя устройства только на этом этапе, чтоб в `entity_id`
        # было "sonoff_{unique_id}". Если имя присвоить в конструкторе - в
        # `entity_id` попадёт имя в латинице.
        self._name = self.device.name

    def _update(self, device: EWeLinkDevice, schedule_update: bool = True):
        self._state = device.state.get(self._attr)

        if schedule_update:
            self.schedule_update_ha_state()

    @property
    def should_poll(self) -> bool:
        # Устройство само присылает обновление своего состояния по Multicast.
        return False

    @property
    def unique_id(self) -> Optional[str]:
        return f'{self.device.deviceid}_{self._attr}'

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def device_class(self):
        return ATTRS[self._attr][0]

    @property
    def unit_of_measurement(self):
        return ATTRS[self._attr][1]

    @property
    def icon(self):
        return ATTRS[self._attr][2]

    @property
    def state(self):
        return self._state
