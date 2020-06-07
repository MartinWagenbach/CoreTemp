#!/usr/bin/python3
import sys
from configparser import ConfigParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP
import subprocess as sp
import time
from os.path import expanduser
from config_path import ConfigPath


cfg_path = ConfigPath("", "CoreTemp", "ini")
last_mail = None


def createConfig():
    cp = ConfigParser()

    cp["config"] = {
        "log_path": "stdout",
        "update_interval": 60,
        "mail_interval": 900,
        "warning_threshold": 70,
        "panic_threshold": 90
    }
    cp["mail_login"] = {
        "smtp_server": "smtp.srv.com:587",
        "e_mail": "user@mail.com",
        "password": "changeme",
        "receiver": "user@mail.com"
    }

    print("Config file not found.")
    print("Writing default config to {}".format(cfg_path.saveFilePath()))
    print("Change me pls. Beep Bop.")

    with open(cfg_path.saveFilePath(mkdir=True), "w") as configfile:
        cp.write(configfile)


def sendMail(cfg, body, subject):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = cfg["mail_login"]["e_mail"]
    message["To"] = cfg["mail_login"]["receiver"]

    message.attach(MIMEText(body, "plain"))
    server = SMTP(cfg["mail_login"]["smtp_server"])
    server.starttls()
    server.login(cfg["mail_login"]["e_mail"], cfg["mail_login"]["password"])
    server.sendmail(cfg["mail_login"]["e_mail"], cfg["mail_login"]["receiver"], message.as_string())
    server.quit()


def measureTemp(cfg):
    global last_mail
    temp = float(sp.check_output(["vcgencmd", "measure_temp"]).decode(encoding="utf-8").replace("temp=", "")
                 .replace("'C", ""))
    psAux = sp.check_output(["ps", "aux"]).decode(encoding="utf-8")

    if temp >= float(cfg["config"]["warning_threshold"]) and \
            (last_mail is None or (time.time() - last_mail) >= float(cfg["config"]["mail_interval"])):
        sendMail(cfg, psAux, "Raspberry Pi temperatur at {:3.2f} °C".format(temp))
        last_mail = time.time()

    if temp >= float(cfg["config"]["panic_threshold"]):
        sendMail(cfg, "", "Raspberry Pi overheating! Shutting down.")
        sp.run("poweroff")

    if config["config"]["log_path"] == "stdout":
        print("{} >> {: 3.2f} °C\n".format(time.strftime("%d.%m.%Y %H:%M:%S"), temp))
    else:
        file = open(expanduser(cfg["config"]["log_path"]), "a")
        file.write("{} >> {: 3.2f} °C\n".format(time.strftime("%d.%m.%Y %H:%M:%S"), temp))
        file.close()


if not cfg_path.readFilePath():
    createConfig()
    sys.exit()

config = ConfigParser()
config.read(cfg_path.readFilePath())

while True:
    measureTemp(config)
    time.sleep(int(config["config"]["update_interval"]))
