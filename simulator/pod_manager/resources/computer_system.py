
from flask_restful import Resource

from simulator.pod_manager.resources import computer_systems
from simulator.pod_manager.resources import systems_members


class SystemCollection(Resource):
    def get(self):
        return {
            "@odata.context": "/redfish/v1/$metadata#ComputerSystemCollection.ComputerSystemCollection",
            "@odata.id": "/redfish/v1/Systems",
            "@odata.type": "#ComputerSystemCollection.ComputerSystemCollection",
            "Name": "Computer System Collection",
            "Members@odata.count": 48,
            "Members": systems_members
        }


class System(Resource):
    def get(self, system_id):
        system_url = '/redfish/v1/Systems/%s' % system_id
        return computer_systems[system_url]
