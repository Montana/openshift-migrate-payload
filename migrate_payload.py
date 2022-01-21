from subprocess import check_output, CalledProcessError
import json
import yaml
import os

nightly = "registry.svc.ci.openshift.org/ocp/release:4.6.0-0.nightly-2020-07-21-004949"
ocp_build_data_path = "./ocp-build-data/images"
fetch = True
payload_image = set()


def fetch_from_payload():
    oc_output = ""
    try:
        oc_output = check_output([
            "oc",
            "adm",
            "release",
            "info",
            "--output=json",
            nightly,
        ])
    except CalledProcessError as e:
        print("command '{}' return with error (code {}): {}".format(
            e.cmd, e.returncode, e.output))

    payload_json = json.loads(oc_output)
    for x in payload_json["references"]["spec"]["tags"]:
        tmp = "ose-" + x["name"]
        payload_image.add(tmp)

    for y in payload_image:
        print(y)


if fetch:
    fetch_from_payload()

for filename in os.listdir(ocp_build_data_path):
    find = ""
    if filename.endswith(".yml"):
        curr_file = os.path.join(ocp_build_data_path, filename)
        with open(curr_file, "r") as stream:
            curr_yaml = yaml.safe_load(stream)
            if curr_yaml is not None:
                find = curr_yaml["name"].split("/")[1]
                if find in payload_image:

                    print("we should update file {} with 'for_payload: true'".
                          format(find))
                    curr_yaml["for_payload"] = "true"
                else:

                    print("we should update file {} with 'for_payload: false'".
                          format(find))
                    curr_yaml["for_payload"] = "false"

                with open(curr_file, "w") as yamlfile:
                    yaml.safe_dump(curr_yaml, yamlfile)
