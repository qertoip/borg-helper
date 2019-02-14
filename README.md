# borg-helper
[Borg Backup](https://www.borgbackup.org/) is a proven open source archiver with encryption, deduplication, compression, snapshotting and auto-prunning.

[Borg Helper](https://github.com/qertoip/borg-helper) preconfigures Borg Backup for complete, secure, and efficient backups. Backups are ran and verified periodically. Configuration targets desktop Linux and employs status notifications.

This project accompanies ["Pragmatic Cypherpunk's Personal Backup"](https://medium.com/@qertoip/pragmatic-cypherpunks-personal-backup-d47425453a06) piece I wrote.

## Features

* Systemd timer to run backups daily
* Systemd timer to independently verify recent backup does exist
* Desktop notifications on successful, erronous or missing backup
* Opinionated and preconfigured for:
  * remote backups to any cloud supporting Borg (like [rsync.net](https://www.rsync.net/products/attic.html))
  * local encryption
  * modern compression (zstd)
  * full disk `/` excluding devices, mount points, caches, downloads, trash, etc
  * auto prunning (the older the sparser)
  * comprehensive reporting
* Convenience wrappers for `borg`:
  * `borg-init` - initialize remote repository (done once)
  * `borg-backup` - create incremental backup (snapshot)
  * `borg-list` - list incremental backups (snapshots)
  * `borg-mount` - mount remote repository as a local filesystem (can take many seconds or minutes); only used for file recovery
  * `borg-umonut` - unmount remote repository
* Trivially auditable - composed of very simple and well commented Bash and Python scripts

## Intended usage

The intention is that you modify the scripts in-place to suit your needs. Treat borg-helper as a starting point to your custom configuration.

## Instructions

Install and understand [Borg Backup](https://www.borgbackup.org/).

Buy a cloud storage with explicit Borg support (like [rsync.net](https://www.rsync.net/products/attic.html)).

Clone this repository and `cd` into it.

Configure `BORG_REPO` in `borg-helper.conf` in place. No need to copy the file anywhere. Also, review `exclude` file and maybe add your own exclusions.

`sudo ./install` to install borg-helper on your system. Review `install` file to understand what installing entails. It is just a couple of lines.

Run `sudo borg-init` to initialize the remote repository. No need to specify params. This will use the `BORG_REPO`0 you configured. This is a one-time action. Encryption key will be generated during this step. **Skip the passphrase with enter** to facilitate automated backups. Safeguard the encryption key. If lost, you won't be able to use your backups.

Test the remote repository with `sudo borg-list`. It should show an empty output (b/c we have no snapshosts).

Normally backups will be triggered daily by `borg-backup.timer`. However, the first time better do it manually by running `sudo borg-backup`. **It will likely take lots of time**. Thanks to deduplication the process can be interrupted and then resumed (technically a new snapshot will capitalize on the previous incomplete one).

Test the remote repository again with `sudo borg-list`. It should now show some snapshots.

Start the timers to allow periodic execution:

    sudo systemctl start borg-warn-if-no-recent-backup.timer
    sudo systemctl start borg-backup.timer

## Debugging

    # Run backup script directly
    sudo borg-backup

    # Run backup service manually (the above script wrapped with systemd service)
    sudo systemctl start borg-backup.service

    # Run the verification service manually
    sudo systemctl start borg-warn-if-no-recent-backup.service

    sudo systemctl status borg-backup.service   # status of the last backup run
    sudo systemctl status borg-backup.timer     # status of the timer to periodically call backup

    sudo systemctl stauts borg-warn-if-no-recent-backup.service  # status of the last check for recent backup
    sudo systemctl stauts borg-warn-if-no-recent-backup.timer    # status of the timer to call the checking

    cat /var/log/borg.log
    cat /var/log/borg-verify.log

## Notes

The backup and verification cannot run at the same time because borg repository has a lock. Only one repository client can connect at the time.
