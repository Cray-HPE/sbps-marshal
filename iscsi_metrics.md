# iSCSI based boot content projection metrics

# Assumptions
Ansible play books to personalize the worker node are run successfully where iSCSI is configured and the SBPS Marshal agent is running sucessfully.

## Description

iSCSI based boot content projection is replacing DVS/CPS and is a read-only projection. A few of the metrics related to projection are exported to the node exporter / promethus are:

    - read megabytes (read_mbytes)
    - Number read I/O's per second (IOPs)
    - Number of projected rootfs LUNs
    - Number of projected PE LUNs
    - Throughput statistics on LIO portal network endpoints

iSCSI metrics 'read_mbytes' and 'IOPs' are retrieved from sysfs:

Example:
```
ncn-w002:/sys/kernel/config/target/iscsi/iqn.2023-06.csm.iscsi:ncn-w002/tpgt_1/lun/lun_0/statistics/scsi_tgt_port # ls
dev  hs_in_cmds  in_cmds  indx  inst  name  port_index  read_mbytes  write_mbytes
ncn-w002:/sys/kernel/config/target/iscsi/iqn.2023-06.csm.iscsi:ncn-w002/tpgt_1/lun/lun_0/statistics/scsi_tgt_port # cat read_mbytes
137
```
The number of projected rootfs and PE LUNs is retrieved by querying /etc/target/saveconfig.json

## Retrieve iSCSI metrics

iSCSI metrics can be retrieved on an individual node in text or through web interface. The first
four commands list above can be retrieved via the methods below:

1. Retrieve text:

    #kubectl exec -n services cray-shared-kafka-kafka-0 -it sh
    #curl -G 'http://vmselect-vms.sysmgmt-health.svc.cluster.local:8481/select/0/prometheus/api/v1/query?query=iscsi_read_mbytes'

2. To use the web interface:

Go to the URL  `https://vmselect.cmn.<system_name>.hpc.amslabs.hpecorp.net/select/0/prometheus/vmui`

For example, if the system name is fanta, use:

    https://vmselect.cmn.fanta.hpc.amslabs.hpecorp.net/select/0/prometheus/vmui 

Then query for iscsi metrics.

Throughput statistics on LIO portal network endpoints can be viewed on prometheus/ Grafana dash boards.

As we are using HSN and/or NMN network interface, these metrics are available as part of prometheus/ Grafana dash boards and can be viwed at Grafana dash boards on any CSM cluster, under General metrics, Node Exporter Full. Please select Job as "node-exporter" and Host as any worker node (say ncn-w001). Under this we can monitor the following metrics:

`recv hsn0`, `trans hsn0`, `recv nmn0` and `trans nmn0`

These metrics can be monitored during iSCSI LUN projection from iSCSI targets to iSCSI initiators during compute/UAN node boot time.
