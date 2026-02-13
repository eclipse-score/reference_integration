AutoSD MCO LoLa Demo
====================

## Background and Basic Info

This demo build an AutoSD image using [Automotive-Image-Builder](https://gitlab.com/CentOS/automotive/src/automotive-image-builder).
This image comes pre-populated with the S-core's [communication](https://github.com/eclipse-score/communication) project packaged as RPM in a [COPR](https://copr.fedorainfracloud.org/coprs/pingou/score-playground/) repository as well as the [QM](https://github.com/containers/qm) project.

The image is pre-configured to allow the communication project to send and receive messages within the root partition but also between the root partition and the QM partition.


Some things to know about this demo:
- The RPM packaging, currently, doesn't rely on Bazel. This is something that is being fixed, but in the current stage it is not there yet.
- Baselibs and communication have had to get some patches, some of which have already been sent upstream:
  - Missing headers: https://github.com/eclipse-score/communication/pull/64
  - Missing headers: https://github.com/eclipse-score/baselibs/pull/19
  - Compilation issues on newer GCC + support for Linux ARM64: https://github.com/eclipse-score/baselibs/pull/22
  - Fix dangling references and compiler warnings for newer GCC: https://github.com/eclipse-score/communication/pull/68
  - Fix Google benchmark main function scope: https://github.com/eclipse-score/communication/pull/67
- Other changes have not yet been sent upstream:
  - Add the ability to configure the path where communication opens the shared memory segments: https://github.com/eclipse-score/communication/commit/127a64f07f48e1d69783dc20f217da813115dbe6 (not the final version of this change)

The goal of this last commit is to avoid having to mount the entire `/dev/shm` into the QM partition and instead mount just a subfolder: `/dev/shm/lola_qm`.


## Building It

A linux system is required to build this image but Ubuntu
and an OCI compliant container manager (docker, podman) should be enough.

Download the builder script:

```
$ curl -o auto-image-builder.sh \
  "https://gitlab.com/CentOS/automotive/src/automotive-image-builder/-/raw/main/auto-image-builder.sh"
$ chmod +x automotive-image-builder
```

Build a qemu image by running:

```
sudo ./auto-image-builder.sh build \
--define-file vars.yml \
--define-file vars-devel.yml \
--target qemu \
--export qcow2 \
--distro autosd10 lola-demo.aib.yml \
autosd10-lola-x86_64.qcow2
```

Change the image perms (if needed) since `sudo` was used:

```
sudo chown $(logname) autosd10-lola-x86_64.qcow2
```

## Running/Testing the Demo

You can run the qcow2 image with your qemu tool of choice and login into the image (either directly or over ssh)
with `root / password` (developer access defined by `vars-devel`).

The image contains Systemd service defintions for LoLa, in both host and QM environemnts:

- lola-ipc-sub.service
- lola-ipc-pub.service

They can be used in the same environment or between them, to exemplify its mixed critical orchestration integration.

For example, to run the publisher in the host environment while receiving messages in the QM one:


Start the subscriber in the QM partition:

```
# start the service
podman exec -it qm systemctl start lola-ipc-sub

# check status
podman exec -it qm systemctl status lola-ipc-sub

# get logs
podman exec -it qm journalctl -u lola-ipc-sub.service 
```


Start a publisher in the host environment:

```
systemctl start lola-ipc-pub
```

Check the QM process logs again with:

```
podman exec -it qm journalctl -u lola-ipc-sub.service
```
