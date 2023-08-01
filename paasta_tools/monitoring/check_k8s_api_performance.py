#!/usr/bin/env python
# Copyright 2015-2016 Yelp Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse
import time

from kubernetes import client

from paasta_tools.kubernetes_tools import KUBE_CONFIG_USER_PATH
from paasta_tools.kubernetes_tools import KubeClient


NAMESPACE = "paasta"
LABEL_SELECTOR = None


def parse_k8s_api_performance_options() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--kube-config-path",
        "-k",
        dest="kube_config_path",
        default=KUBE_CONFIG_USER_PATH,
        help="Specify the path to the kubeconfig file",
    )

    parser.add_argument(
        "--context",
        "-c",
        dest="context",
        default=None,
        help="Pass the cluster you want to connect to",
    )

    parser.add_argument(
        "--namespace",
        "-n",
        dest="namespace",
        default=NAMESPACE,
        help="Pass the namespace you want to query",
    )

    parser.add_argument(
        "--label-selector",
        "-l",
        dest="label_selector",
        default=LABEL_SELECTOR,
        help="Pass the label selector you want to select",
    )

    # Add additional filtering options
    parser.add_argument(
        "--pod-status",
        dest="pod_status",
        default=None,
        help="Filter pods by their status (e.g., Running, Pending, Succeeded, etc.)",
    )

    parser.add_argument(
        "--container-name",
        dest="container_name",
        default=None,
        help="Filter pods by their container name",
    )

    options = parser.parse_args()
    return options


def get_pods_from_namespace_selector(
    kube_client: KubeClient, namespace: str, label_selector: str, pod_status: str, container_name: str
) -> client.models.v1_pod_list.V1PodList:

    field_selector = []
    if pod_status:
        field_selector.append(f"status.phase={pod_status}")

    # Construct field selector for container name
    if container_name:
        field_selector.append(f"spec.containers[*].name={container_name}")

    if field_selector:
        field_selector_str = ",".join(field_selector)
    else:
        field_selector_str = None

    # list all the running pods with filters
    ret = kube_client.core.list_namespaced_pod(
        namespace, watch=False, label_selector=label_selector, field_selector=field_selector_str
    )
    return ret


if __name__ == "__main__":
    options = parse_k8s_api_performance_options()
    kube_client = KubeClient(
        config_file=options.kube_config_path, context=options.context
    )

    # measure the performance of this function
    start = time.time()
    ret = get_pods_from_namespace_selector(
        kube_client, options.namespace, options.label_selector, options.pod_status, options.container_name
    )
    end = time.time()

    print("time it took to run this function: ", end - start)

    # pods are stored here
    pods = ret.items
    pods_names = [pod.metadata.name for pod in pods]
    pods_status = [pod.status.phase for pod in pods]

    print(list(zip(pods_names, pods_status)))
