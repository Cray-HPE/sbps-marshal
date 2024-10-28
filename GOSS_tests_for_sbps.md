# Assumptions before running this test

Ansible scripts are run successfully which configures iSCSI on selected worker nodes and labels them with 'iscsi=sbps'. Goss tests use this label as identification of nodes on which this test has to run.

## SBPS GOSS Frame work

SBPS GOSS tests run some of the sanity tests for SBPS solution and these tests run on worker node(s) where iSCSI is configured and the SBPS Marshal agent is running. Bash script 'https://github.com/Cray-HPE/csm-testing/blob/release/1.6/goss-testing/scripts/iscsi_sbps_sanity.sh' does the below mentioned sanity checksfor SBPS:

- Verify SPBS Agent is running (systemd service)
- Verify LIO target is active
- Verify TCP service probes complete against all active portals (iSCSI)
- Verify DNS SRV and A records exist for the worker respective of the iSCSI portals
- Verify the mapping between DNS A records and host iscsi portals

The goss script which determines on which nodes the script 'iscsi_sbps_sanity.sh' has to run is determined by 'https://github.com/Cray-HPE/csm-testing/blob/release/1.6/goss-testing/tests/ncn/goss-validate-iscsi-sbps-config.yaml'. Once the 'csm-testing' package is installed, GOSS frame work takes care of placing these scripts in required directory location on test system(s), here it will be on worker nodes. Please ensure 'iscsi_sbps_sanity.sh' is placed under /opt/cray/tests/install/ncn/scripts/ directory and 'https://github.com/Cray-HPE/csm-testing/blob/release/1.6/goss-testing/tests/ncn/goss-validate-iscsi-sbps-config.yaml' is placed under /opt/cray/tests/install/ncn/tests/ directory. And also, ensure an entry for goss-validate-iscsi-sbps-config.yaml is present in /opt/cray/tests/install/ncn/suites/ncn-healthcheck-worker.yaml as this SBPS sanity test will be run during ncn-health checks.

## Steps to run

Ensure 'goss-servers' systemd service is running on all the nodes (master and worker):
If not, restart the goss-server on all the worker nodes configured with iSCSI.

    systemctl restart goss-servers.service
    systemctl status goss-servers.service

Expected output:

        goss-servers.service - goss-servers
         Loaded: loaded (/etc/systemd/system/goss-servers.service; disabled; vendor preset: disabled)
        Active: active (running) since Tue 2024-01-16 18:47:59 UTC; 1 day 18h ago
        Main PID: 1630316 (bash)
        Tasks: 682
        CGroup: /system.slice/goss-servers.service

**Note:** In CSM 1.6.0, it is required to restart 'goss-servers' service as the 'goss-servers' is not getting restarted after the upgrade.
Run below from master node to restart 'goss-servers' on all worker nodes:

     worker_nodes=$(grep -oP "(ncn-w\d+)" /etc/hosts | sort -u | tr -t '\n' ',')
     pdsh -S -b -w $worker_nodes 'systemctl restart goss-servers'

Two ways to run the goss tests:

Method #1: Run the below script from master/pit node

    /opt/cray/tests/install/ncn/automated/ncn-healthcheck-worker

This will run the test on all the corresponding worker nodes which are configured with iSCSI.

Method #2: Run on Individual node (worker):

Set the below GOSS environment variable

    export GOSS_BASE=/opt/cray/tests/install/ncn

Then run the below command:

    goss -g /opt/cray/tests/install/ncn/tests/goss-validate-iscsi-sbps-config.yaml validate

This command will run the test on the individual node on which this was run where iSCSI is confgured.

## Steps to view the test logs

When the test is run on master/pit node (method #1), logs would be available at the below location on the system(s):
On the master node, the high level tests results log will be available and on the individual worker node, we can see
the detailed test results log.

On the master node:

    /opt/cray/tests/install/logs/print_goss_json_results/

e.g.

    /opt/cray/tests/install/logs/print_goss_json_results/20241002_133551.159786-1959742-YNsI6heE/out

The above log will have collated high level test results of all the goss tests run on the system,
we should look for iscsi goss tests as below: 

```
Result: PASS
Source: http://ncn-w001.hmn:8997/ncn-healthcheck-worker
Test Name: iscsi boot content projection
Description: checks for iscsi portals and iscsi based boot content projection service is active and running.
Test Summary: Command: iscsi_cps_sanity: exit-status: matches expectation: [0]
Execution Time: 0.000012453 seconds
Node: ncn-w001
```

This high level test result would be available for all the worker nodes.

On the worker node:

The individual worker node will have detailed log of the test run at the below location:

    /opt/cray/tests/install/logs/iscsi_cps_sanity

e.g.

    /opt/cray/tests/install/logs/iscsi_cps_sanity/20241014_110514_223323798_211125.log

Note: When the test is run on the individual worker node (method #2), the test log would be available
only on the individual node at the above mentioned location i.e /opt/cray/tests/install/logs/iscsi_cps_sanity.
