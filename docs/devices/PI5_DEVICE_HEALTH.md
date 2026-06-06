# Pi5 Device Health Baseline

Status: sanitized device-health note only.

This note records the last known read-only Pi5 health snapshot so AI_OS can compare future checks against a retrievable baseline. It is not a repair packet, Pi service, SSH automation, GPIO workflow, or motor-control instruction.

## Device Identity

- Hostname: `aios-pi5`
- Last known IP: `192.168.1.167`
- OS: Debian 13 trixie
- Kernel: `6.18.33+rpt-rpi-2712`
- Uptime at check: `4h49m`

## Storage Baseline

- NVMe: Fanxiang S500Pro 256GB
- Root disk: `/dev/nvme0n1p2`
- Root filesystem: ext4 mounted at `/`
- Disk use at check: `7.7G used / 217G free / 4%`

## Power And Thermal Baseline

- Power throttling: `throttled=0x0`
- Temperature: `40.6 C`

## Corruption Scan Result

- Serious ext4/NVMe corruption scan: no matching serious error lines returned.
- Earlier orphan cleanup suggests a prior unclean shutdown.
- Current read-only checks did not prove active corruption.

## Interpretation

The Pi5 was online at the last check, the NVMe root filesystem was mounted, disk usage was low, power throttling was clear, and temperature was normal for a light-load Pi5. The prior orphan cleanup is evidence of an earlier unclean shutdown, but the sanitized read-only results do not currently prove active NVMe or ext4 corruption.

Treat this as a baseline for comparison only. Future evidence of I/O errors, ext4 errors, read-only remounts, boot failures, SMART failures, or unexplained data loss should reopen the device-health lane before any repair action is considered.

## Safe Next Read-Only Checks

Anthony can run these later on the Pi5 console when a fresh health comparison is needed:

```bash
hostname
hostname -I
uptime
lsblk -o NAME,MODEL,SIZE,TYPE,FSTYPE,MOUNTPOINTS
findmnt -no SOURCE,FSTYPE,OPTIONS /
df -hT /
vcgencmd get_throttled
vcgencmd measure_temp
journalctl -k -b --no-pager | grep -Ei 'nvme|ext4|i/o error|corrupt|reset|timeout|read-only' | tail -80
dmesg -T | grep -Ei 'nvme|ext4|i/o error|corrupt|reset|timeout|read-only' | tail -80
```

Optional privileged read-only storage inventory, only when Anthony explicitly approves it:

```bash
sudo smartctl -a /dev/nvme0n1
```

## Commands Not To Run Unless Explicitly Approved

Do not run repair, destructive, mount-state, or hardware-control commands from repo guidance alone. These require separate explicit approval and the correct safe device state:

```bash
fsck -y
e2fsck -y
mount
umount
mkfs
format
rm -rf
dd
gpio
raspi-gpio
```
