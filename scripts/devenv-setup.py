import argparse
import os
import subprocess
import yaml

def setup_devenv(dev_instance_name, services):
    """
    This function sets up the development environment for the given services.
    It clones the necessary repositories, checks out the correct branch, and sets up the environment.
    It also generates a custom docker-compose file that includes only the necessary services.
    It then builds and starts the necessary containers and runs the necessary commands for the given services.
    """
    branch = "prep-release"

    print("Setting up new fullctl dev environment", dev_instance_name)
    print("Cloning repositories")

    # Clone fullctl repository
    if not os.path.isdir("fullctl"):
        subprocess.run(["git", "clone", "git@github.com:fullctl/fullctl"])
        os.chdir("fullctl")
        subprocess.run(["git", "checkout", branch])
        os.chdir("..")

    # copy Ctl/dev to Ctl/dev-instance-name
    os.chdir("fullctl")

    if not os.path.isdir(f"Ctl/{dev_instance_name}"):
        subprocess.run(["cp", "-r", "Ctl/dev", f"Ctl/{dev_instance_name}"])

    if not os.path.isfile(f"Ctl/{dev_instance_name}/.env"):
        print(f"Copying base env settings for fullctl")
        subprocess.run(["cp", f"Ctl/{dev_instance_name}/example.env", f"Ctl/{dev_instance_name}/.env"])
    os.chdir("..")

    # Clone necessary service repositories
    for service in services:
        if not os.path.isdir(service):
            subprocess.run(["git", "clone", f"git@github.com:fullctl/{service}"])
            os.chdir(service)
            subprocess.run(["git", "checkout", branch])
            os.chdir("..")

        # copy Ctl/dev to Ctl/dev-instance-name
        os.chdir(service)
        if not os.path.isdir(f"Ctl/{dev_instance_name}"):
            subprocess.run(["cp", "-r", "Ctl/dev", f"Ctl/{dev_instance_name}"])

        if not os.path.isfile(f"Ctl/{dev_instance_name}/.env"):
            print(f"Copying base env settings for {service}")
            subprocess.run(["cp", f"Ctl/{dev_instance_name}/example.env", f"Ctl/{dev_instance_name}/.env"])
        os.chdir("..")

    os.chdir("fullctl")

    # Generate custom docker-compose file
    with open("Ctl/dev/docker-compose.yml", 'r') as file:
        data = yaml.safe_load(file)
        services_dict = data['services']
        service_names = [f"{service}_web" for service in services]
        custom_services = {k: v for k, v in services_dict.items() if k in ['postgres'] + service_names}

        for svc_name, svc in custom_services.items():
            if "env_file" not in svc:
                continue
            svc["env_file"] = [path.replace("Ctl/dev", f"Ctl/{dev_instance_name}") for path in svc["env_file"]]

        data['services'] = custom_services
    with open(f"Ctl/{dev_instance_name}/docker-compose.yml", 'w') as file:
        yaml.dump(data, file)

    print("Building and starting database container")
    subprocess.run(["poetry", "run", f"Ctl/{dev_instance_name}/compose.sh", "up", "-d", "postgres"])

    print("Building containers")
    subprocess.run(["poetry", "run", f"Ctl/{dev_instance_name}/compose.sh", "build"])

    for service_name in service_names:
        subprocess.run(["poetry", "run", f"Ctl/{dev_instance_name}/run.sh", service_name, "migrate"])
        subprocess.run(["poetry", "run", f"Ctl/{dev_instance_name}/run.sh", service_name, "createcachetable"])
        if service_name == "aaactl_web":
            subprocess.run(["poetry", "run", f"Ctl/{dev_instance_name}/run.sh", service_name, "loaddata", "fixtures/fixture.full-perms.json"])
            print("Creating django admin account (ctrl+c if already exists)")
            subprocess.run(["poetry", "run", f"Ctl/{dev_instance_name}/run.sh", service_name, "createsuperuser"])
        if service_name == "pdbctl_web":
            subprocess.run(["poetry", "run", f"Ctl/{dev_instance_name}/run.sh", service_name, "fullctl_peeringdb_sync"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Setup development environment for a service.')

    parser.add_argument('--dev-instance-name', help='The name of the development instance.', default="dev-custom")

    parser.add_argument('--services', nargs='+', required=True, help='The services to setup the development environment for.')
    args = parser.parse_args()
    setup_devenv(args.dev_instance_name ,args.services)