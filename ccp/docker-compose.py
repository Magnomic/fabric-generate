import yaml
import json
import re


class JSONObject:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class CLIConfig(JSONObject):

    def __init__(self, volumes):
        self.container_name = "cli"
        self.image = "hyperledger/fabric-tools:latest"
        self.tty = True
        self.stdin_open = True
        self.environment = ["SYS_CHANNEL=byfn-sys-channel",
                            "GOPATH=/opt/gopath",
                            "CORE_VM_ENDPOINT=unix:///host/var/run/docker.sock",
                            "FABRIC_LOGGING_SPEC=DEBUG",
                            "FABRIC_LOGGING_SPEC=INFO",
                            "CORE_PEER_ID=cli",
                            "CORE_PEER_ADDRESS=peer0.org1.example.com:21000",
                            "CORE_PEER_LOCALMSPID=Org1MSP",
                            "CORE_PEER_TLS_ENABLED=true",
                            "CORE_PEER_TLS_CERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/server.crt",
                            "CORE_PEER_TLS_KEY_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/server.key",
                            "CORE_PEER_TLS_ROOTCERT_FILE=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt",
                            "CORE_PEER_MSPCONFIGPATH=/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp"]
        self.working_dir = "/opt/gopath/src/github.com/hyperledger/fabric/peer"
        self.command = "/bin/bash"
        self.volumes = ["/var/run/:/host/var/run/",
                        "./../chaincode/:/opt/gopath/src/github.com/chaincode",
                        "./crypto-config:/opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/",
                        "./scripts:/opt/gopath/src/github.com/hyperledger/fabric/peer/scripts/",
                        "./channel-artifacts:/opt/gopath/src/github.com/hyperledger/fabric/peer/channel-artifacts"]
        self.depends_on = list(volumes)
        self.networks = ["byfn"]


class OrdererConfig(JSONObject):

    def __init__(self, orderer_id=""):
        self.container_name = "orderer%s.example.com" % orderer_id
        self.extends = {"file": "base/peer-base.yaml",
                        "service": "orderer-base"}

        self.volumes = ["./channel-artifacts/genesis.block:/var/hyperledger/orderer/orderer.genesis.block",
                        "./crypto-config/ordererOrganizations/example.com/orderers/orderer%s.example.com/msp:/var/hyperledger/orderer/msp" % orderer_id,
                        "./crypto-config/ordererOrganizations/example.com/orderers/orderer%s.example.com/tls/:/var/hyperledger/orderer/tls" % orderer_id,
                        "orderer%s.example.com:/var/hyperledger/production/orderer" % orderer_id]

        if orderer_id != "":
            self.ports = ["%d:%d" % (18000 + int(orderer_id), 7050)]
        else:
            self.ports = ["%d:%d" % (18000, 7050)]

        self.networks = ["byfn"]


class PeerConfig(JSONObject):
    def __init__(self, org_id, peer_id, total_peers):
        self.container_name = "peer%d.org%d.example.com" % (peer_id, org_id)
        self.extends = {"file": "base/peer-base.yaml",
                        "service": "peer-base"}
        bootstrap = ""
        for i in range(total_peers):
            if i != peer_id:
                bootstrap += "peer%d.org%d.example.com:%d " % (i, org_id, 20000 + org_id * 1000 + i)
        # if peer_id != total_peers - 1:
        #    bootstrap += "peer%d.org%d.example.com:%d" % (total_peers - 1, org_id, 20000 + org_id * 1000 + total_peers - 1)

        # bootstrap += "]"

        self.environment = ["CORE_PEER_ID=peer%d.org%d.example.com" % (peer_id, org_id),
                            "CORE_PEER_ADDRESS=peer%d.org%d.example.com:%d" % (
                                peer_id, org_id, 20000 + org_id * 1000 + peer_id),
                            "CORE_PEER_LISTENADDRESS=0.0.0.0:%d" % (20000 + org_id * 1000 + peer_id),
                            "CORE_PEER_CHAINCODEADDRESS=peer%d.org%d.example.com:%d" % (
                                peer_id, org_id, 18000 + org_id * 100 + peer_id),
                            "CORE_PEER_CHAINCODELISTENADDRESS=0.0.0.0:%d" % (18000 + org_id * 100 + peer_id),
                            "CORE_PEER_GOSSIP_BOOTSTRAP=" + bootstrap,
                            "CORE_PEER_GOSSIP_EXTERNALENDPOINT=peer%d.org%d.example.com:%d" % (
                                peer_id, org_id, 20000 + org_id * 1000 + peer_id),
                            "CORE_PEER_LOCALMSPID=Org%dMSP" % org_id]
        self.volumes = ["/var/run/:/host/var/run/",
                        "./crypto-config/peerOrganizations/org%d.example.com/peers/peer%d.org%d.example.com/msp:/etc/hyperledger/fabric/msp" % (
                            org_id, peer_id, org_id),
                        "./crypto-config/peerOrganizations/org%d.example.com/peers/peer%d.org%d.example.com/tls:/etc/hyperledger/fabric/tls" % (
                            org_id, peer_id, org_id),
                        "peer%d.org%d.example.com:/var/hyperledger/production" % (peer_id, org_id)]

        self.ports = ["%d:%d" % (20000 + org_id * 1000 + peer_id, 20000 + org_id * 1000 + peer_id)]
        self.networks = ["byfn"]


class CAConfig(JSONObject):
    def __init__(self, org_id):
        self.image = "hyperledger/fabric-ca:latest"
        self.environment = [
            "FABRIC_CA_HOME=/etc/hyperledger/fabric-ca-server",
            "FABRIC_CA_SERVER_CA_NAME=ca.org%d.example.com" % org_id,
            "FABRIC_CA_SERVER_TLS_ENABLED=true",
            "FABRIC_CA_SERVER_TLS_CERTFILE=/etc/hyperledger/fabric-ca-server-config/ca.org%d.example.com-cert.pem" % org_id,
            "FABRIC_CA_SERVER_TLS_KEYFILE=/etc/hyperledger/fabric-ca-server-config/CA%d_PRIVATE_KEY" % org_id]
        self.ports = ["%d:7054" % (19000 + org_id)]
        self.command = "sh -c 'fabric-ca-server start --ca.certfile /etc/hyperledger/fabric-ca-server-config/ca.org%d.example.com-cert.pem --ca.keyfile /etc/hyperledger/fabric-ca-server-config/CA%d_PRIVATE_KEY -b admin:adminpw -d'" % (
            org_id, org_id)
        self.volumes = [
            "./crypto-config/peerOrganizations/org%d.example.com/ca/:/etc/hyperledger/fabric-ca-server-config" % org_id]
        self.container_name = "ca.org%d.example.com" % org_id
        self.networks = ["byfn"]


class DockerComposeConfig(JSONObject):
    def __init__(self, peer_num, org_num, orderer_num):
        self.version = "2"
        self.volumes = {"orderer.example.com"}
        for i in range(2, orderer_num + 1):
            self.volumes.add("orderer%d.example.com" % i)
        for i in range(1, org_num + 1):
            for j in range(peer_num):
                self.volumes.add("peer%d.org%d.example.com" % (j, i))
        self.networks = {"byfn"}
        self.services = {}
        for i in range(1, org_num + 1):
            self.services["ca.org%d.example.com" % i] = CAConfig(i)
            self.volumes.add("ca.org%d.example.com" % i)
        self.services["orderer.example.com"] = OrdererConfig()

        self.services["cli"] = CLIConfig(self.volumes)

        for i in range(2, orderer_num + 1):
            self.services["orderer%d.example.com" % i] = OrdererConfig(i)
        for i in range(1, org_num + 1):
            for j in range(peer_num):
                self.services["peer%d.org%d.example.com" % (j, i)] = PeerConfig(i, j, peer_num)


if __name__ == '__main__':
    config = DockerComposeConfig(3, 6, 5)
    configStr = yaml.dump(config)
    f = open("../out/docker-compose-e2e.yaml", "w")
    f.write(re.sub("\'", "", re.sub("null", "", re.sub("!!.*\n", "\n", configStr))))
