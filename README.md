## ansible-cassandra

Ansible role to install an Apache Cassandra cluster supervised with systemd. Includes the following:

* Some OS tuning options such as installing jemalloc, setting max_map_count and tcp_keepalive, disabling swap.
* Bootstraps nodes using the IPs of the servers in the `cassandra_seed` (configurable) inventory group.
* Weekly scheduled repairs via cron jobs that are non-overlapping (see `cassandra_repair_slots`).
    * requires setting `cassandra_keyspaces` (default `[]` will have no effect)
* Incremental and full backup scripts as well as a restore script. (NOTE: needs better testing)
    * requires access to S3, optional, disabled by default
* prometheus-style metrics using jmx-exporter

**Status: beta**, see [TODOs](#todo)

[![Build Status](https://travis-ci.org/wireapp/ansible-cassandra.svg?branch=master)](https://travis-ci.org/wireapp/ansible-cassandra)

<!-- vim-markdown-toc GFM -->

* [Ansible Requirements](#ansible-requirements)
* [Role Variables](#role-variables)
* [Dependencies](#dependencies)
* [Platforms](#platforms)
* [Example Playbook](#example-playbook)
* [License](#license)
* [A note on openjdk vs oracle:](#a-note-on-openjdk-vs-oracle)
* [Development setup](#development-setup)
* [Credits](#credits)
* [TODO](#todo)

<!-- vim-markdown-toc -->

## Ansible Requirements

- ansible >= 2.4
- no additional requirements

## Role Variables

Give your cluster a better name:

```yaml
# set cassandra_cluster_name before running the playbook for the first time; never change it afterwards
cassandra_cluster_name: default
```

You should override the keyspaces to match keyspaces on which you wish to run weekly repairs:

```yaml
cassandra_keyspaces: []
```

You may wish to override the following defaults for backups:

```yaml
# backups
cassandra_backup_enabled: false # recommended to enable this
cassandra_backup_s3_bucket: # set a name here and ensure access rights to an S3 bucket
cassandra_env: dev # used in naming backups in case you have more than one environment (e.g. production, staging, ...)
```

For a list of all variables, see `defaults/main.yml`.

## Dependencies

The following should be installed before installing this role:

- java (openJDK or Oracle, see [A note on openjdk vs oracle:](#a-note-on-openjdk-vs-oracle))
- ntp

For the above dependencies, you can use the same roles as in `molecule/default/requirements.yml` - but you don't have to.

## Platforms

- Currently tested with ubuntu 16.04 only

## Example Playbook

Assuming an inventory with 5 nodes where you wish to install cassandra on, two of them seed nodes:

```ini
# hosts.ini
[all]
host01 ansible_host=<some IP>
host02 ansible_host=<some IP>
host03 ansible_host=<some IP>
host04 ansible_host=<some IP>
host05 ansible_host=<some IP>

[cassandra]
host01
host02
host03
host04
host05

# cassandra_seed group will be used to configure seed bootstrapping
# recommended is 2 seed nodes per datacenter
[cassandra_seed]
host01
host02
```

Then the following should work and start your cluster:

```yaml
# playbook.yml

- hosts: cassandra
  vars:
    # set cluster_name before running the playbook for the first time; never change it afterwards
    cassandra_cluster_name: my_cluster
    cassandra_keyspaces:
      - my_keyspace1
  roles:
    # ensure to install java ntp first, e.g. by running these roles (see Dependencies section):
    # - ansible-ntp
    # - ansible-java
    - ansible-cassandra
```

If you don't wish to configure cassandra seed nodes via a `cassandra_seed_groupname` (default: `cassandra_seed`) inventory group, you can configure them statically:

```yaml
  vars:
    cassandra_seed_resolution: static
    cassandra_seeds:
      - 1.2.3.4
      - ...
```

## License

AGPL. See [LICENSE](LICENSE)

## A note on openjdk vs oracle:

As of November 2018, the cassandra homepage lists both openJDK and Oracle Java as supported (and offers their download links).

But when using openJDK, cassandra itself logs:

> WARN: OpenJDK is not recommended. Please upgrade to the newest Oracle Java release

In the [official upgrade-to-DSE docs](https://docs.datastax.com/en/pdf/upgrade.pdf) one can find:

> Important:
> Although Oracle JRE/JDK 8 is supported, DataStax does more
> extensive testing on OpenJDK 8 starting with DSE 6.0.3. This change is due to the
> end of public updates for Oracle JRE/JDK 8.)

It seems OpenJDK is the more future-proof thing to use.

## Development setup

Install [molecule](https://github.com/ansible/molecule). E.g. ensure you have docker installed, then, using a virtualenv, `pip install molecule ansible docker`.

* `molecule converge` to run the playbook against docker containers
* `molecule lint` and `molecule syntax` to improve yaml.
* `molecule test` to destroy + converge + converge again for idempotence + destroy
* `make` to run molecule converge on each file save.

* troubleshooting: [this issue](https://github.com/ansible/ansible/issues/43884) has been observed with molecule, ansible 2.7 and docker. Workaround was to downgrade to ansible 2.5.

## Credits

This role has been inspired by

* internal role used at Wire initially targeting older OSes and older cassandra versions.
* [this cassandra role](https://github.com/andrewrothstein/ansible-cassandra-cluster) and its dependent roles (insufficient for our needs)

## TODO

* [ ] write ansible check at the end of playbook checking cassandra port is open
* [ ] WARN: JMX is not enabled to receive remote connections. Please see cassandra-env.sh for more info.
* [ ] test backups and restore
* [ ] document usage of prometheus .prom files and node-exporter
* [ ] check out if instead of cron jobs a repair alternative could be https://github.com/thelastpickle/cassandra-reaper
