import json
import yaml
import re

PEERPEM = "crypto-config/peerOrganizations/org%d.example.com/tlsca/tlsca.org%d.example.com-cert.pem"
CAPEM="crypto-config/peerOrganizations/org%d.example.com/ca/ca.org%d.example.com-cert.pem"


class JSONObject:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class CertificateAuthorities(JSONObject):
    def __init__(self, org_id):
        self.url = "https://localhost:%d" % (19000 + org_id)
        self.caName = "ca-org%d" % org_id
        self.tlsCACerts = {"pem": CAPEM % (org_id, org_id)}
        self.httpOptions = {"verify": False}


class Peers(JSONObject):
    def __init__(self, org_id, peer_id, tlsCACerts):
        self.url = "grpcs://localhost:%d" % (20000+org_id*1000+peer_id)
        self.tlsCACerts = {"pem": tlsCACerts}
        self.grpcOptions = {"ssl-target-name-override": "peer%d.org%d.example.com" % (peer_id, org_id),
                            "hostnameOverride": "peer%d.org%d.example.com" % (peer_id, org_id)}


class OrgConfig(JSONObject):
    def __init__(self, org_id, peer_num):
        self.mspid = "Org%dMSP" % org_id
        self.peers = []
        for i in range(peer_num):
            self.peers.append("peer%d.org%d.example.com" % (i, org_id))
        self.certificateAuthorities = ["ca.org%d.example.com" % org_id]


class Client(JSONObject):
    def __init__(self, org_id):
        self.organization = "Org%d" % org_id
        self.connection = {"timeout": {"peer": {"endorser": 300}}}


class Ccp(JSONObject):
    def __init__(self, org_id, peer_num):
        self.name = "first-network-org%d" % org_id
        self.version = "1.0.0"
        self.client = Client(org_id)
        self.organizations = OrgConfig(org_id, peer_num)
        self.peers = {}
        for i in range(peer_num):
            self.peers["peer%d.org%d.example.com" % (i, org_id)] = Peers(org_id, i, PEERPEM % (org_id, org_id))
        self.certificateAuthorities = {"ca.org%d.example.com" % org_id: CertificateAuthorities(org_id)}


if __name__ == "__main__":
    for i in range(1,7):
        ccp_class = Ccp(i, 3)
        jsonOutput = open("../out/my-connection-org%d.json"%i,"w")
        jsonOutput.write(ccp_class.toJSON())
        yamlOutput = open("../out/my-connection-org%d.yaml"%i,"w")
        yamlOutput.write(re.sub("!!.*\n", "\n", yaml.dump(ccp_class)))
