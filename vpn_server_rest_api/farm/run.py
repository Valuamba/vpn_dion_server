import docker
import sys
print ('Number of arguments:', len(sys.argv), 'arguments.')
print ('Argument List:', str(sys.argv))

client = docker.from_env()

IMAGE_NAME="vpn-debian"
NUMBER_CONTAINERS=10
VPN_PREFIX="vpn_dion_server_"
LISTEN_PORT=34078

if sys.argv[1] == 'run':
    containers = []
    for i in range(NUMBER_CONTAINERS):
        containers.append({ "port": 33440 + i, "name": f"{VPN_PREFIX}{i}"})

    for c in containers:
        print (f'Run [{c["name"]} container on port [{c["port"]}]')
        client.containers.run(
            image=IMAGE_NAME,
            ports={
                5000: c["port"]
            },
            name=c["name"],
            tty=True,
            stdin_open=True,
            detach=True,
            # network_mode="host"
        )

elif sys.argv[1] == 'down':
    containers = client.containers.list(all=True)
    vpn_containers = [c for c in containers if c.name.startswith(VPN_PREFIX)]
    for c in vpn_containers:
        print (f"Remove container {c.name}")
        c.stop()
        c.remove()