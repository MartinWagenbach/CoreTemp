# CoreTemp

Monitor the Raspberry Pi cpu temperature and send an e-mail or shutdown in case it's too high.

---

## Installation

- Clone this repo to your Raspberry Pi using `https://github.com/MartinWagenbach/CoreTemp.git`.

- Go to your directory where you cloned the repo and install the requirements.

```shell
$ pip3 install -r requirements.txt
```

- Edit the CoreTemp.ini.

- Move the CoreTemp.ini to your config path.

```shell
$ cp CoreTemp.ini /etc/
```

## Setup as service (Optional)

- Let’s create a file called: `/etc/systemd/system/coretemp.service`

```service
[Unit]
Description=Monitor CPU temperatur with CoreTemp.py
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
Environment=HOME=/root/
Environment=PYTHONUNBUFFERED=1
ExecStart=/usr/local/share/CoreTemp/CoreTemp.py

[Install]
WantedBy=multi-user.target
```

- That’s it. We can now start the service:

```shell
$ systemctl start coretemp
```

- And automatically get it to start on boot:

```shell
$ systemctl enable coretemp
```

---

## Contributors

| <a href="https://github.com/MartinWagenbach" target="_blank">**MartinWagenbach**</a> | <a href="https://github.com/tikrass" target="_blank">**Tikrass**</a> |
| :---: |:---:|
| [![MartinWagenbach](https://avatars3.githubusercontent.com/u/65785896?v=3&s=200)](https://github.com/MartinWagenbach)    | [![Tikrass](https://avatars1.githubusercontent.com/u/641293?v=3&s=200)](https://github.com/tikrass)  |
| <a href="https://github.com/MartinWagenbach" target="_blank">`github.com/MartinWagenbach`</a> | <a href="https://github.com/tikrass" target="_blank">`github.com/tikrass`</a> |
